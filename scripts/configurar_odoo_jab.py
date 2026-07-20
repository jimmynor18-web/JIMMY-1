#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configura el Odoo Online de JAB Factory SAS via XML-RPC.

Crea (si no existen) las bodegas de los 3 camiones, las cajas de
efectivo, los plazos de pago y activa las ubicaciones de
almacenamiento. Es idempotente: se puede ejecutar varias veces sin
duplicar nada. Al final imprime una auditoria de la configuracion.

Uso:
    ODOO_URL=https://jab-factory-sas.odoo.com \
    ODOO_DB=jab-factory-sas \
    ODOO_USER=correo@ejemplo.com \
    ODOO_API_KEY=xxxx \
    python3 scripts/configurar_odoo_jab.py

O por argumentos:
    python3 scripts/configurar_odoo_jab.py --url ... --db ... --user ... --key ...
"""
import argparse
import os
import sys
import xmlrpc.client

BODEGAS = [
    ("Camión Cesar Gomez", "VEH1"),
    ("Camión Luis Melo", "VEH2"),
    ("Camión Andres Gutierrez", "VEH3"),
]

CAJAS = [
    ("Efectivo Cesar Gomez", "EFCG"),
    ("Efectivo Luis Melo", "EFLM"),
    ("Efectivo Andres Gutierrez", "EFAG"),
    ("Efectivo repartos", "EFREP"),
    ("Caja principal", "CAJAP"),
]

PLAZOS = [
    ("Contado", 0),
    ("Crédito 15 días", 15),
]

# Vendedor -> codigo de su bodega predeterminada
VENDEDOR_BODEGA = {
    "Cesar Gomez": "VEH1",
    "Luis Melo": "VEH2",
    "Andres Gutierrez": "VEH3",
}


def conectar(url, db, user, key):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    version = common.version()
    print(f"✔ Conectado a {url} — Odoo {version.get('server_version')}")
    uid = common.authenticate(db, user, key, {})
    if not uid:
        sys.exit("✘ Autenticación fallida: revisa correo, base de datos y clave API")
    print(f"✔ Autenticado como {user} (uid {uid})")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def call(model, method, *args, **kwargs):
        return models.execute_kw(db, uid, key, model, method, list(args), kwargs)

    return call


def activar_ubicaciones(call):
    grupo = call("res.groups", "search", [("category_id.name", "in", ["Technical", "Técnico"]),
                                          ("name", "in", ["Manage Multiple Stock Locations",
                                                          "Gestionar múltiples ubicaciones de inventario"])])
    vals_id = call("res.config.settings", "create", {"group_stock_multi_locations": True})
    call("res.config.settings", "execute", [vals_id])
    print("✔ Ubicaciones de almacenamiento: activadas")


def crear_bodegas(call):
    for nombre, codigo in BODEGAS:
        existe = call("stock.warehouse", "search", [("code", "=", codigo)])
        if existe:
            print(f"• Bodega {codigo} ya existe ({nombre})")
            continue
        call("stock.warehouse", "create", {"name": nombre, "code": codigo})
        print(f"✔ Bodega creada: {nombre} ({codigo})")


def crear_cajas(call):
    for nombre, codigo in CAJAS:
        existe = call("account.journal", "search", ["|", ("code", "=", codigo),
                                                    ("name", "=", nombre)])
        if existe:
            print(f"• Caja '{nombre}' ya existe")
            continue
        call("account.journal", "create", {"name": nombre, "code": codigo, "type": "cash"})
        print(f"✔ Caja creada: {nombre} ({codigo})")


def crear_plazos(call):
    for nombre, dias in PLAZOS:
        existe = call("account.payment.term", "search", [("name", "=", nombre)])
        if existe:
            print(f"• Plazo '{nombre}' ya existe")
            continue
        call("account.payment.term", "create", {
            "name": nombre,
            "line_ids": [(0, 0, {"value": "percent", "value_amount": 100.0,
                                  "nb_days": dias, "delay_type": "days_after"})],
        })
        print(f"✔ Plazo de pago creado: {nombre}")


def asignar_bodegas_vendedores(call):
    for nombre, codigo in VENDEDOR_BODEGA.items():
        usuarios = call("res.users", "search", [("name", "ilike", nombre)])
        bodegas = call("stock.warehouse", "search", [("code", "=", codigo)])
        if not usuarios:
            print(f"• Usuario '{nombre}' no existe aún — crear en Ajustes → Usuarios y re-ejecutar")
            continue
        if not bodegas:
            continue
        try:
            call("res.users", "write", usuarios, {"property_warehouse_id": bodegas[0]})
            print(f"✔ {nombre}: bodega predeterminada {codigo}")
        except Exception as e:
            print(f"• {nombre}: no se pudo asignar bodega ({e})")


def auditoria(call):
    print("\n===== AUDITORÍA DE CONFIGURACIÓN =====")
    for modelo, titulo, campos in [
        ("stock.warehouse", "Bodegas", ["name", "code"]),
        ("account.journal", "Diarios", ["name", "type"]),
        ("account.payment.term", "Plazos de pago", ["name"]),
        ("res.users", "Usuarios activos", ["name", "login"]),
    ]:
        registros = call(modelo, "search_read", [], fields=campos, limit=50)
        print(f"\n{titulo} ({len(registros)}):")
        for r in registros:
            print("  -", " | ".join(str(r.get(c, "")) for c in campos))
    productos = call("product.template", "search_count", [])
    clientes = call("res.partner", "search_count", [("customer_rank", ">", 0)])
    print(f"\nProductos: {productos} | Clientes: {clientes}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=os.environ.get("ODOO_URL", "https://jab-factory-sas.odoo.com"))
    p.add_argument("--db", default=os.environ.get("ODOO_DB", "jab-factory-sas"))
    p.add_argument("--user", default=os.environ.get("ODOO_USER"))
    p.add_argument("--key", default=os.environ.get("ODOO_API_KEY"))
    p.add_argument("--solo-auditoria", action="store_true",
                   help="No crea nada: solo imprime el estado actual")
    args = p.parse_args()
    if not args.user or not args.key:
        sys.exit("Faltan credenciales: --user y --key (o variables ODOO_USER / ODOO_API_KEY)")

    call = conectar(args.url, args.db, args.user, args.key)
    if not args.solo_auditoria:
        try:
            activar_ubicaciones(call)
        except Exception as e:
            print(f"• No se pudo activar ubicaciones automáticamente ({e}) — activarla en Ajustes")
        crear_bodegas(call)
        crear_cajas(call)
        crear_plazos(call)
        asignar_bodegas_vendedores(call)
    auditoria(call)
    print("\n✔ Terminado")


if __name__ == "__main__":
    main()
