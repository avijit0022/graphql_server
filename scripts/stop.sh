#!/bin/bash
# GraphQL Server - Stop Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Stopping GraphQL Server"
echo "========================"

# Load environment for port reference
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

if [ -f "graphql_server.pid" ]; then
    PID=$(cat graphql_server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping server (PID: $PID)"
        kill $PID 2>/dev/null || true
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID 2>/dev/null || true
        fi
    else
        echo "PID $PID is stale (process not running)"
    fi
    rm -f graphql_server.pid
else
    echo "No PID file found"
fi

# Fallback: kill any leftover process on the port
if [ -n "$GRAPHQL_SERVER_PORT" ]; then
    LEFTOVER=$(lsof -ti :$GRAPHQL_SERVER_PORT 2>/dev/null)
    if [ -n "$LEFTOVER" ]; then
        echo "Killing leftover process on port $GRAPHQL_SERVER_PORT (PID: $LEFTOVER)"
        kill -9 $LEFTOVER 2>/dev/null || true
    fi
fi

echo "Server stopped"
