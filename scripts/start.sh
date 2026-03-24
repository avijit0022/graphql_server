#!/bin/bash
# GraphQL Server - Start Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_NAME="venv"

echo "Starting GraphQL Server"
echo "========================"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment from .env"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "WARNING: No .env file found"
fi

# Check venv
if [ ! -d "$VENV_NAME" ]; then
    echo "ERROR: Virtual environment not found. Run scripts/setup.sh first."
    exit 1
fi

source "$VENV_NAME/bin/activate"

# Require .env values
if [ -z "$GRAPHQL_SERVER_HOST" ] || [ -z "$GRAPHQL_SERVER_PORT" ]; then
    echo "ERROR: GRAPHQL_SERVER_HOST and GRAPHQL_SERVER_PORT must be set in .env"
    exit 1
fi

# Start server
echo "Starting server on $GRAPHQL_SERVER_HOST:$GRAPHQL_SERVER_PORT..."
nohup python server.py > graphql_server.log 2>&1 &
PID=$!
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo $PID > graphql_server.pid
    echo ""
    echo "Server started!"
    echo "  - GraphQL endpoint: http://$GRAPHQL_SERVER_HOST:$GRAPHQL_SERVER_PORT"
    echo "  - Logs: graphql_server.log"
else
    echo "ERROR: Server failed to start. Check graphql_server.log"
    exit 1
fi
