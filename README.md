# JIMMY-1 — Gestor de Rutas

Aplicación web sencilla para crear y administrar rutas de viaje (origen, destino y distancia). Construida con Node.js puro, sin dependencias externas.

## Requisitos

- Node.js 18 o superior

## Cómo ejecutar

```bash
node server.js
```

Luego abre http://localhost:3000 en tu navegador.

El puerto se puede cambiar con la variable de entorno `PORT`:

```bash
PORT=8080 node server.js
```

## API REST

| Método | Ruta              | Descripción                  |
| ------ | ----------------- | ---------------------------- |
| GET    | `/api/rutas`      | Lista todas las rutas        |
| GET    | `/api/rutas/:id`  | Obtiene una ruta por su id   |
| POST   | `/api/rutas`      | Crea una nueva ruta          |
| PUT    | `/api/rutas/:id`  | Actualiza una ruta existente |
| DELETE | `/api/rutas/:id`  | Elimina una ruta             |

### Ejemplo: crear una ruta

```bash
curl -X POST http://localhost:3000/api/rutas \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bogotá - Medellín", "origen": "Bogotá", "destino": "Medellín", "distanciaKm": 415}'
```

Los campos `nombre`, `origen` y `destino` son obligatorios; `distanciaKm` es opcional.

## Persistencia

Las rutas se guardan en `data/rutas.json` (se crea automáticamente al agregar la primera ruta).

## Estructura del proyecto

```
├── server.js          # Servidor HTTP y API REST
├── public/
│   └── index.html     # Interfaz web
└── data/
    └── rutas.json     # Datos persistidos (generado en tiempo de ejecución)
```
