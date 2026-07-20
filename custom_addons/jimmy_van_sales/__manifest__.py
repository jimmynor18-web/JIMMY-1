# -*- coding: utf-8 -*-
{
    "name": "Jimmy Van Sales",
    "summary": "Bodegas por vehiculo, diarios de efectivo y plazos de pago para venta en ruta",
    "description": """
Configura la venta en ruta (van sales):
- 3 almacenes (uno por vehiculo) con reabastecimiento desde el almacen principal
- 3 diarios de efectivo (uno por vehiculo) para cuadre de caja por vendedor
- Plazos de pago: Contado y Credito 15 dias
Renombra los vehiculos en Inventario > Configuracion > Almacenes.
""",
    "author": "Jimmy",
    "version": "18.0.1.4.0",
    "category": "Inventory",
    "license": "LGPL-3",
    "depends": ["sale_management", "sale_stock", "stock", "account", "mrp", "purchase"],
    "data": [
        "data/warehouse_data.xml",
        "data/account_data.xml",
        "data/users_data.xml",
    ],
    "installable": True,
    "application": False,
}
