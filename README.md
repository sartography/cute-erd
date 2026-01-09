# ERD Mini-Diagram Builder

A lightweight tool to create focused Mermaid ERD diagrams from PostgreSQL databases.

## Quick Start

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Start server
uv run python manage.py runserver 0.0.0.0:8000
```

Or use the startup script with a preset connection:

```bash
./start-server.sh "postgresql://user:pass@host:5432/dbname"
```

Then open `http://localhost:8000`

## Features

- Select tables and columns from **all schemas** in your PostgreSQL database
- Auto-selects primary keys, foreign keys, and unique keys
- Search/filter tables by name
- Generates Mermaid ERD syntax
- Export as `.mmd` file

## Environment Variable (Optional)

Set preset connections:

```bash
POSTGRES_CONNECTIONS="name1=postgresql://...,name2=postgresql://..." uv run python manage.py runserver 0.0.0.0:8000
```
