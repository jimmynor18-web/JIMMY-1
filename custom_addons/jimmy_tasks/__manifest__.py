# -*- coding: utf-8 -*-
{
    "name": "Jimmy Tasks",
    "summary": "Simple task manager - sample custom Odoo module",
    "description": """
Sample custom addon that demonstrates the basic structure of an Odoo module:
a model, list/form views, menus and access rights.
""",
    "author": "Jimmy",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/task_views.xml",
    ],
    "application": True,
    "installable": True,
}
