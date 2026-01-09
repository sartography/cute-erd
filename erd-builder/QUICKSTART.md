# Quick Start Guide

Get up and running with the ERD Mini-Diagram Builder in 5 minutes!

## 1. Install Dependencies

```bash
uv sync
```

## 2. Run Migrations

```bash
uv run python manage.py migrate
```

## 3. (Optional) Set Up Test Database

If you want to try the tool with a sample database:

```bash
# Create a PostgreSQL database
createdb erd_test

# Run the example schema
psql erd_test < example_schema.sql
```

## 4. (Optional) Configure Database Connections

You can configure preset connections via environment variable:

```bash
export POSTGRES_CONNECTIONS="test=postgres://localhost:5432/erd_test"
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your connections
```

## 5. Start the Server

```bash
uv run python manage.py runserver
```

## 6. Use the Tool

1. Open http://localhost:8000 in your browser
2. Enter your PostgreSQL connection string or select a preset
3. Click "Load Schema"
4. Select tables by clicking their checkboxes
5. Toggle additional columns if needed
6. Click "Generate Diagram"
7. Copy or download your Mermaid ERD!

## Example Connection String

```
postgres://username:password@localhost:5432/database_name
```

For the test database (assuming default PostgreSQL setup):
```
postgres://localhost:5432/erd_test
```

## Troubleshooting

### Can't connect to database?

Make sure:
- PostgreSQL is running
- The connection string is correct
- The user has permission to access the database
- The database exists

### No tables showing up?

The tool looks for tables in the `public` schema by default. Make sure your tables are in the public schema.

### htmx not working?

Make sure you have a stable internet connection, as htmx and Alpine.js are loaded from CDN.

## Next Steps

- Read the full [README.md](README.md) for more details
- Check out [example_schema.sql](example_schema.sql) for a sample database
- Try creating diagrams with your own databases!

## Tips

- **Focus on relationships**: Select 4-5 related tables for the most useful diagrams
- **Key columns**: Primary keys, foreign keys, and unique keys are auto-selected for a reason!
- **Iterate quickly**: The htmx interface updates in real-time, so you can experiment rapidly
- **Export options**: Use "Copy to Clipboard" for quick sharing, or "Download" to save for later

Enjoy building your ERD diagrams!
