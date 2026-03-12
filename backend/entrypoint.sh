#!/bin/sh
# entrypoint.sh — Wait for PostgreSQL before starting the backend

set -e

HOST="${POSTGRES_SERVER:-localhost}"
PORT="${POSTGRES_PORT:-5432}"

echo "⏳ Waiting for PostgreSQL at ${HOST}:${PORT}..."

MAX_RETRIES=30
RETRY_COUNT=0

while ! python -c "
import socket, sys
try:
    s = socket.create_connection(('$HOST', $PORT), timeout=2)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "❌ PostgreSQL not available after $MAX_RETRIES attempts. Exiting."
        exit 1
    fi
    echo "  Attempt ${RETRY_COUNT}/${MAX_RETRIES} — waiting 2s..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"
echo "🚀 Starting Geopolitical Intelligence Platform..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
