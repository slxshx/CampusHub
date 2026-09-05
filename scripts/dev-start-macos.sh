#!/usr/bin/env bash

set -e

echo "======================================"
echo "       CampusHub Dev Start macOS"
echo "======================================"
echo

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "[1/3] Starte PostgreSQL..."

brew services start postgresql@17 >/dev/null 2>&1 || true

echo "✓ PostgreSQL läuft"
echo


echo "[2/3] Starte / lade Nginx..."

if brew services list | grep -q "^nginx.*started"; then
    nginx -t
    nginx -s reload

    echo "✓ Nginx neu geladen"
else
    nginx -t
    brew services start nginx

    echo "✓ Nginx gestartet"
fi

echo


echo "[3/3] Starte FastAPI..."
echo
echo "CampusHub:"
echo "  http://localhost:8081"
echo
echo "Swagger:"
echo "  http://localhost:8081/api/docs"
echo
echo "Backend wird mit Ctrl+C beendet."
echo

cd "$BACKEND_DIR"

uv run uvicorn campushub.__main__:app --reload
