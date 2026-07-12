# -*- coding: utf-8 -*-
{
    "name": "Jimmy Van Sales",
    "summary": "Crea 3 bodegas de vehiculo para venta en ruta",
    "description": """
Configura la venta en ruta (van sales):
crea 3 almacenes (uno por vehiculo) con reabastecimiento
desde el almacen principal. Renombra los vehiculos en
Inventario > Configuracion > Almacenes.
""",
    "author": "Jimmy",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "license": "LGPL-3",
    "depends": ["sale_management", "stock"],
    "data": [
        "data/warehouse_data.xml",
    ],
    "installable": True,
    "application": False,
}
