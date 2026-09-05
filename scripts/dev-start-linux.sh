#!/usr/bin/env bash

set -e

echo "======================================"
echo "       CampusHub Dev Start Linux"
echo "======================================"
echo

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "[1/3] Starte PostgreSQL..."

sudo systemctl start postgresql

echo "✓ PostgreSQL läuft"
echo


echo "[2/3] Starte / lade Nginx..."

sudo nginx -t

if systemctl is-active --quiet nginx; then
    sudo systemctl reload nginx

    echo "✓ Nginx neu geladen"
else
    sudo systemctl start nginx

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
