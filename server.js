const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data', 'rutas.json');

// --- Persistencia simple en archivo JSON ---

function cargarRutas() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function guardarRutas(rutas) {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  fs.writeFileSync(DATA_FILE, JSON.stringify(rutas, null, 2));
}

let rutas = cargarRutas();
let siguienteId = rutas.reduce((max, r) => Math.max(max, r.id), 0) + 1;

// --- Utilidades HTTP ---

function enviarJSON(res, codigo, datos) {
  res.writeHead(codigo, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(datos));
}

function leerCuerpo(req) {
  return new Promise((resolve, reject) => {
    let cuerpo = '';
    req.on('data', (chunk) => {
      cuerpo += chunk;
      if (cuerpo.length > 1e6) {
        reject(new Error('Cuerpo demasiado grande'));
        req.destroy();
      }
    });
    req.on('end', () => {
      try {
        resolve(cuerpo ? JSON.parse(cuerpo) : {});
      } catch {
        reject(new Error('JSON inválido'));
      }
    });
    req.on('error', reject);
  });
}

function validarRuta(datos) {
  const errores = [];
  if (!datos.nombre || typeof datos.nombre !== 'string' || !datos.nombre.trim()) {
    errores.push('El campo "nombre" es obligatorio');
  }
  if (!datos.origen || typeof datos.origen !== 'string' || !datos.origen.trim()) {
    errores.push('El campo "origen" es obligatorio');
  }
  if (!datos.destino || typeof datos.destino !== 'string' || !datos.destino.trim()) {
    errores.push('El campo "destino" es obligatorio');
  }
  if (datos.distanciaKm != null && (typeof datos.distanciaKm !== 'number' || datos.distanciaKm < 0)) {
    errores.push('El campo "distanciaKm" debe ser un número positivo');
  }
  return errores;
}

// --- Archivos estáticos ---

const TIPOS_MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

function servirEstatico(res, rutaArchivo) {
  const rutaAbsoluta = path.join(__dirname, 'public', path.normalize(rutaArchivo).replace(/^(\.\.[/\\])+/, ''));
  fs.readFile(rutaAbsoluta, (err, contenido) => {
    if (err) {
      enviarJSON(res, 404, { error: 'No encontrado' });
      return;
    }
    const ext = path.extname(rutaAbsoluta).toLowerCase();
    res.writeHead(200, { 'Content-Type': TIPOS_MIME[ext] || 'application/octet-stream' });
    res.end(contenido);
  });
}

// --- Servidor y enrutamiento ---

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const partes = url.pathname.split('/').filter(Boolean);

  // API: /api/rutas y /api/rutas/:id
  if (partes[0] === 'api' && partes[1] === 'rutas') {
    const id = partes[2] ? Number(partes[2]) : null;

    try {
      if (req.method === 'GET' && id === null) {
        enviarJSON(res, 200, rutas);
      } else if (req.method === 'GET') {
        const ruta = rutas.find((r) => r.id === id);
        if (!ruta) return enviarJSON(res, 404, { error: `Ruta ${id} no encontrada` });
        enviarJSON(res, 200, ruta);
      } else if (req.method === 'POST' && id === null) {
        const datos = await leerCuerpo(req);
        const errores = validarRuta(datos);
        if (errores.length) return enviarJSON(res, 400, { errores });
        const ruta = {
          id: siguienteId++,
          nombre: datos.nombre.trim(),
          origen: datos.origen.trim(),
          destino: datos.destino.trim(),
          distanciaKm: datos.distanciaKm ?? null,
          creadaEn: new Date().toISOString(),
        };
        rutas.push(ruta);
        guardarRutas(rutas);
        enviarJSON(res, 201, ruta);
      } else if (req.method === 'PUT' && id !== null) {
        const indice = rutas.findIndex((r) => r.id === id);
        if (indice === -1) return enviarJSON(res, 404, { error: `Ruta ${id} no encontrada` });
        const datos = await leerCuerpo(req);
        const errores = validarRuta(datos);
        if (errores.length) return enviarJSON(res, 400, { errores });
        rutas[indice] = {
          ...rutas[indice],
          nombre: datos.nombre.trim(),
          origen: datos.origen.trim(),
          destino: datos.destino.trim(),
          distanciaKm: datos.distanciaKm ?? null,
        };
        guardarRutas(rutas);
        enviarJSON(res, 200, rutas[indice]);
      } else if (req.method === 'DELETE' && id !== null) {
        const indice = rutas.findIndex((r) => r.id === id);
        if (indice === -1) return enviarJSON(res, 404, { error: `Ruta ${id} no encontrada` });
        const [eliminada] = rutas.splice(indice, 1);
        guardarRutas(rutas);
        enviarJSON(res, 200, eliminada);
      } else {
        enviarJSON(res, 405, { error: 'Método no permitido' });
      }
    } catch (err) {
      enviarJSON(res, 400, { error: err.message });
    }
    return;
  }

  // Frontend estático
  if (req.method === 'GET') {
    servirEstatico(res, url.pathname === '/' ? 'index.html' : url.pathname);
    return;
  }

  enviarJSON(res, 404, { error: 'No encontrado' });
});

servidor.listen(PORT, () => {
  console.log(`Servidor de rutas escuchando en http://localhost:${PORT}`);
});

module.exports = servidor;
