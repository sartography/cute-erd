# ERD Mini-Diagram Builder

Create focused Mermaid ERD diagrams from PostgreSQL databases. Select tables/columns, auto-selects keys, exports `.mmd` files.

## Quick Start

```bash
uv sync && uv run python manage.py migrate && uv run python manage.py runserver
# Open http://localhost:8000, enter postgres://user:pass@host:5432/dbname, select tables, generate diagram
```

Set preset connections: `POSTGRES_CONNECTIONS="name=postgresql://..." uv run python manage.py runserver`
