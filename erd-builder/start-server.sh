#!/bin/bash

# ERD Builder Server Startup Script
# Usage: ./start-server.sh [connection_string]
#
# If connection_string is provided, it will be set as a preset connection named "default"
# Example: ./start-server.sh "postgresql://civi:civi@127.0.0.1:5432/civitos_api"

if [ -n "$1" ]; then
    export POSTGRES_CONNECTIONS="default=$1"
    echo "Starting server with preset connection: default"
fi

# Start the Django development server
uv run python manage.py runserver 0.0.0.0:8000
