"""Utilities for parsing database connections and extracting schema information."""
import psycopg2
from typing import Dict, List, Tuple
from django.conf import settings


def parse_connections() -> Dict[str, str]:
    """Parse POSTGRES_CONNECTIONS environment variable.

    Format: "name1=postgres://...,name2=postgres://..."
    Returns: {"name1": "postgres://...", "name2": "postgres://..."}
    """
    connections = {}
    if not settings.POSTGRES_CONNECTIONS:
        return connections

    for conn_str in settings.POSTGRES_CONNECTIONS.split(','):
        if '=' in conn_str:
            name, url = conn_str.split('=', 1)
            connections[name.strip()] = url.strip()

    return connections


def get_database_schema(connection_string: str) -> Dict:
    """Extract schema information from a PostgreSQL database.

    Returns a dictionary with tables, columns, and relationships.
    Optimized to use batch queries instead of per-table queries.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    schema = {
        'tables': {},
        'relationships': []
    }

    # Get all tables from all schemas (excluding system schemas)
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        AND table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name
    """)

    # Initialize all tables
    tables = [(row[0], row[1]) for row in cursor.fetchall()]
    for table_schema, table_name in tables:
        qualified_name = f"{table_schema}.{table_name}"
        schema['tables'][qualified_name] = {
            'columns': [],
            'primary_keys': [],
            'foreign_keys': [],
            'unique_keys': []
        }

    # Batch query: Get all columns for all tables at once
    cursor.execute("""
        SELECT table_schema, table_name, column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position
    """)

    for table_schema, table_name, col_name, data_type, max_length in cursor.fetchall():
        qualified_name = f"{table_schema}.{table_name}"
        if qualified_name in schema['tables']:
            type_str = data_type
            if max_length:
                type_str = f"{data_type}({max_length})"

            schema['tables'][qualified_name]['columns'].append({
                'name': col_name,
                'type': type_str
            })

    # Batch query: Get all primary keys at once
    cursor.execute("""
        SELECT tc.table_schema, tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    """)

    for table_schema, table_name, col_name in cursor.fetchall():
        qualified_name = f"{table_schema}.{table_name}"
        if qualified_name in schema['tables']:
            schema['tables'][qualified_name]['primary_keys'].append(col_name)

    # Batch query: Get all foreign keys at once
    cursor.execute("""
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    """)

    for table_schema, table_name, col_name, foreign_schema, foreign_table, foreign_column in cursor.fetchall():
        qualified_name = f"{table_schema}.{table_name}"
        foreign_qualified = f"{foreign_schema}.{foreign_table}"

        if qualified_name in schema['tables']:
            schema['tables'][qualified_name]['foreign_keys'].append({
                'column': col_name,
                'foreign_table': foreign_qualified,
                'foreign_column': foreign_column
            })

            # Add to relationships
            schema['relationships'].append({
                'from_table': qualified_name,
                'from_column': col_name,
                'to_table': foreign_qualified,
                'to_column': foreign_column
            })

    # Batch query: Get all unique constraints at once
    cursor.execute("""
        SELECT tc.table_schema, tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'UNIQUE'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    """)

    for table_schema, table_name, col_name in cursor.fetchall():
        qualified_name = f"{table_schema}.{table_name}"
        if qualified_name in schema['tables']:
            schema['tables'][qualified_name]['unique_keys'].append(col_name)

    cursor.close()
    conn.close()

    return schema


def generate_mermaid(selected_tables: Dict[str, List[str]], schema: Dict) -> str:
    """Generate Mermaid ERD syntax from selected tables and columns.

    Args:
        selected_tables: Dict mapping table names to lists of column names
        schema: Full schema dictionary from get_database_schema

    Returns:
        Mermaid ERD syntax string
    """
    lines = ["erDiagram"]

    # Helper function to convert schema.table to valid Mermaid identifier
    def mermaid_name(table_name: str) -> str:
        """Replace dots with underscores for Mermaid compatibility."""
        return table_name.replace('.', '_')

    # Generate table definitions
    for table_name, columns in selected_tables.items():
        if not columns:
            continue

        table_info = schema['tables'].get(table_name, {})
        primary_keys = table_info.get('primary_keys', [])
        foreign_keys = [fk['column'] for fk in table_info.get('foreign_keys', [])]
        unique_keys = table_info.get('unique_keys', [])

        mermaid_table_name = mermaid_name(table_name)
        lines.append(f"    {mermaid_table_name} {{")

        for col in columns:
            # Find column type
            col_type = "string"
            for col_info in table_info.get('columns', []):
                if col_info['name'] == col:
                    col_type = col_info['type']
                    break

            # Determine column markers
            markers = []
            if col in primary_keys:
                markers.append("PK")
            if col in foreign_keys:
                markers.append("FK")
            if col in unique_keys and col not in primary_keys:
                markers.append("UK")

            marker_str = " ".join(markers)
            if marker_str:
                lines.append(f"        {col_type} {col} {marker_str}")
            else:
                lines.append(f"        {col_type} {col}")

        lines.append("    }")

    # Generate relationships
    for rel in schema.get('relationships', []):
        from_table = rel['from_table']
        to_table = rel['to_table']

        # Only include relationships where both tables are selected
        if from_table in selected_tables and to_table in selected_tables:
            # Convert to Mermaid-compatible names
            mermaid_from = mermaid_name(from_table)
            mermaid_to = mermaid_name(to_table)
            # Determine cardinality (simplified: one-to-many)
            lines.append(f'    {mermaid_to} ||--o{{ {mermaid_from} : "has"')

    return "\n".join(lines)
