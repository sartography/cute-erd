"""Views for the ERD diagram builder."""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json

from .utils import parse_connections, get_database_schema, generate_mermaid


def index(request):
    """Main page with database connection selection."""
    connections = parse_connections()
    last_connection = request.session.get('connection_string', '')
    return render(request, 'diagram/index.html', {
        'connections': connections,
        'last_connection': last_connection
    })


@require_http_methods(["POST"])
def load_schema(request):
    """Load schema from selected database connection."""
    connection_string = request.POST.get('connection_string')

    if not connection_string:
        return HttpResponse("No connection string provided", status=400)

    try:
        schema = get_database_schema(connection_string)
        # Store schema in session for later use
        request.session['schema'] = schema
        request.session['connection_string'] = connection_string
        # Clear any previously selected tables when loading new schema
        request.session['selected_tables'] = {}

        return render(request, 'diagram/table_list.html', {
            'tables': schema['tables']
        })
    except Exception as e:
        return HttpResponse(f"Error loading schema: {str(e)}", status=500)


@require_http_methods(["POST"])
def toggle_table(request):
    """Toggle table selection and return updated column list + diagram."""
    table_name = request.POST.get('table_name')
    is_selected = request.POST.get('selected') == 'true'

    schema = request.session.get('schema', {})
    table_info = schema.get('tables', {}).get(table_name, {})

    # Get currently selected tables from session
    selected_tables = request.session.get('selected_tables', {})

    if is_selected:
        # Auto-select primary keys, foreign keys, and unique keys
        auto_select = []
        auto_select.extend(table_info.get('primary_keys', []))
        auto_select.extend([fk['column'] for fk in table_info.get('foreign_keys', [])])
        auto_select.extend(table_info.get('unique_keys', []))

        # Remove duplicates while preserving order
        auto_select = list(dict.fromkeys(auto_select))

        selected_tables[table_name] = auto_select
    else:
        # Remove table from selection
        if table_name in selected_tables:
            del selected_tables[table_name]

    request.session['selected_tables'] = selected_tables
    request.session.modified = True

    # Generate diagram output
    mermaid_code = ""
    if selected_tables:
        try:
            mermaid_code = generate_mermaid(selected_tables, schema)
        except:
            pass

    # Return column list + OOB diagram update
    if is_selected:
        return render(request, 'diagram/toggle_response.html', {
            'table_name': table_name,
            'table_info': table_info,
            'selected_columns': selected_tables.get(table_name, []),
            'mermaid_code': mermaid_code,
            'has_selection': bool(selected_tables)
        })
    else:
        # Just return the diagram update
        return render(request, 'diagram/diagram_only.html', {
            'mermaid_code': mermaid_code,
            'has_selection': bool(selected_tables)
        })


@require_http_methods(["POST"])
def toggle_column(request):
    """Toggle column selection."""
    table_name = request.POST.get('table_name')
    column_name = request.POST.get('column_name')
    is_selected = request.POST.get('selected') == 'true'

    selected_tables = request.session.get('selected_tables', {})

    if table_name not in selected_tables:
        selected_tables[table_name] = []

    if is_selected:
        if column_name not in selected_tables[table_name]:
            selected_tables[table_name].append(column_name)
    else:
        if column_name in selected_tables[table_name]:
            selected_tables[table_name].remove(column_name)

    request.session['selected_tables'] = selected_tables
    request.session.modified = True

    return HttpResponse("")


@require_http_methods(["POST"])
def generate_diagram(request):
    """Generate Mermaid diagram from selected tables and columns."""
    schema = request.session.get('schema', {})
    selected_tables = request.session.get('selected_tables', {})

    if not selected_tables:
        return HttpResponse("No tables selected", status=400)

    try:
        mermaid_code = generate_mermaid(selected_tables, schema)
        return render(request, 'diagram/mermaid_output.html', {
            'mermaid_code': mermaid_code
        })
    except Exception as e:
        return HttpResponse(f"Error generating diagram: {str(e)}", status=500)


@require_http_methods(["GET"])
def download_diagram(request):
    """Download Mermaid diagram as .mmd file."""
    schema = request.session.get('schema', {})
    selected_tables = request.session.get('selected_tables', {})

    if not selected_tables:
        return HttpResponse("No tables selected", status=400)

    try:
        mermaid_code = generate_mermaid(selected_tables, schema)

        response = HttpResponse(mermaid_code, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="erd_diagram.mmd"'
        return response
    except Exception as e:
        return HttpResponse(f"Error generating diagram: {str(e)}", status=500)
