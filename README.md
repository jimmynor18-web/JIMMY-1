# JIMMY-1 — Odoo Development Environment

A ready-to-run Odoo 18 development setup using Docker, with a sample custom
addon (`jimmy_tasks`) that shows the standard structure of an Odoo module.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose

## Quick start

```bash
docker compose up -d
```

Then open http://localhost:8069 in your browser.

1. On the first visit, Odoo asks you to create a database. Choose a database
   name, set the master password to `admin` (from `config/odoo.conf`), and
   create your admin user.
2. Go to **Apps**, remove the *Apps* filter if needed, click
   **Update Apps List** (developer mode must be enabled: *Settings →
   General Settings → Developer Tools → Activate the developer mode*),
   then search for **Jimmy Tasks** and install it.
3. A new **Jimmy Tasks** menu appears with a simple task manager.

To stop everything:

```bash
docker compose down
```

Add `-v` to also delete the database volumes and start fresh.

## Project layout

```
├── docker-compose.yml        # Odoo 18 + PostgreSQL 16
├── config/
│   └── odoo.conf             # Odoo server configuration
└── custom_addons/            # Your custom modules (mounted into the container)
    └── jimmy_tasks/          # Sample module: simple task manager
        ├── __manifest__.py   # Module metadata and data files
        ├── models/task.py    # jimmy.task model (fields, compute, actions)
        ├── security/ir.model.access.csv  # Access rights
        └── views/task_views.xml          # List/form/search views + menus
```

## Developing your own module

1. Create a new folder under `custom_addons/` (use `jimmy_tasks` as a
   template).
2. Restart Odoo so it picks up the new module:

   ```bash
   docker compose restart odoo
   ```

3. Update the apps list in Odoo and install your module.

After changing Python code, restart the `odoo` service. After changing XML
data/views, upgrade the module (**Apps → your module → Upgrade**) or restart
with `-u`:

```bash
docker compose exec odoo odoo -d <your-db> -u jimmy_tasks --stop-after-init
docker compose restart odoo
```

## Default credentials

| What                | Value   |
|---------------------|---------|
| Odoo URL            | http://localhost:8069 |
| Master password     | `admin` |
| PostgreSQL user     | `odoo`  |
| PostgreSQL password | `odoo`  |

> These are development defaults — change them before deploying anywhere
> public.
