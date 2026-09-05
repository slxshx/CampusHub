#!/usr/bin/env bash

set -e

echo "======================================"
echo "        CampusHub Linux Setup"
echo "======================================"
echo

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
NGINX_DIR="$PROJECT_ROOT/nginx"

ENV_FILE="$BACKEND_DIR/.env"
ENV_EXAMPLE="$BACKEND_DIR/.env.example"
SCHEMA_FILE="$BACKEND_DIR/scripts/schema.sql"

NGINX_TEMPLATE="$NGINX_DIR/campushub.conf.template"
NGINX_LOCAL="$NGINX_DIR/campushub.local.conf"

echo "Projektverzeichnis:"
echo "$PROJECT_ROOT"
echo

if ! command -v apt >/dev/null 2>&1; then
    echo "FEHLER: Dieses Script unterstützt aktuell Debian/Ubuntu."
    exit 1
fi

echo "[1/7] Prüfe Python..."

if ! command -v python3 >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y python3 python3-venv
fi

echo "✓ Python gefunden: $(python3 --version)"
echo

echo "[2/7] Prüfe curl..."

if ! command -v curl >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y curl
fi

echo "✓ curl gefunden"
echo

echo "[3/7] Prüfe uv..."

if ! command -v uv >/dev/null 2>&1; then
    echo "Installiere uv..."

    curl -LsSf https://astral.sh/uv/install.sh | sh

    export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "FEHLER: uv wurde installiert, aber noch nicht im PATH gefunden."
    echo "Öffne ein neues Terminal und starte das Setup erneut."
    exit 1
fi

echo "✓ uv gefunden"
echo

echo "[4/7] Prüfe PostgreSQL..."

if ! command -v psql >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y postgresql postgresql-client
fi

sudo systemctl enable --now postgresql

echo "✓ PostgreSQL gefunden und gestartet"
echo

echo "[5/7] Bereite Backend vor..."

if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "FEHLER: backend/.env.example fehlt."
        exit 1
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"

    echo "✓ backend/.env wurde erstellt"
    echo
    echo "Öffne jetzt backend/.env und setze DB_PASSWORD."
    echo "Danach dieses Script erneut starten."
    exit 0
fi

cd "$BACKEND_DIR"
uv sync

echo "✓ Backend-Abhängigkeiten installiert"
echo

DB_VALUES="$(
    python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path

values = {}

for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#") or "=" not in line:
        continue

    key, value = line.split("=", 1)
    values[key.strip()] = value.strip()

required = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

for key in required:
    if key not in values:
        raise SystemExit(f"FEHLER: {key} fehlt in backend/.env")

print(values["DB_HOST"])
print(values["DB_PORT"])
print(values["DB_NAME"])
print(values["DB_USER"])
print(values["DB_PASSWORD"])
PY
)"

DB_HOST="$(echo "$DB_VALUES" | sed -n '1p')"
DB_PORT="$(echo "$DB_VALUES" | sed -n '2p')"
DB_NAME="$(echo "$DB_VALUES" | sed -n '3p')"
DB_USER="$(echo "$DB_VALUES" | sed -n '4p')"
DB_PASSWORD="$(echo "$DB_VALUES" | sed -n '5p')"

TEST_DB_NAME="${DB_NAME}_test"

if [ "$DB_PASSWORD" = "CHANGE_ME" ] || [ -z "$DB_PASSWORD" ]; then
    echo "FEHLER: DB_PASSWORD in backend/.env muss gesetzt werden."
    exit 1
fi

echo "[6/7] Bereite Datenbanken vor..."

if sudo -u postgres psql -tAc \
    "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" \
    | grep -q 1; then

    echo "✓ Rolle '$DB_USER' existiert bereits"
else
    sudo -u postgres psql \
        -v db_user="$DB_USER" \
        -v db_password="$DB_PASSWORD" <<'SQL'
CREATE ROLE :"db_user"
WITH LOGIN PASSWORD :'db_password';
SQL

    echo "✓ Rolle '$DB_USER' erstellt"
fi

if sudo -u postgres psql -tAc \
    "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" \
    | grep -q 1; then

    echo "✓ Datenbank '$DB_NAME' existiert bereits"
else
    sudo -u postgres createdb \
        --owner="$DB_USER" \
        "$DB_NAME"

    echo "✓ Datenbank '$DB_NAME' erstellt"
fi

if sudo -u postgres psql -tAc \
    "SELECT 1 FROM pg_database WHERE datname='$TEST_DB_NAME'" \
    | grep -q 1; then

    echo "✓ Datenbank '$TEST_DB_NAME' existiert bereits"
else
    sudo -u postgres createdb \
        --owner="$DB_USER" \
        "$TEST_DB_NAME"

    echo "✓ Datenbank '$TEST_DB_NAME' erstellt"
fi

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "FEHLER: backend/scripts/schema.sql fehlt."
    exit 1
fi

for DATABASE in "$DB_NAME" "$TEST_DB_NAME"; do
    if PGPASSWORD="$DB_PASSWORD" psql \
        -U "$DB_USER" \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -d "$DATABASE" \
        -tAc "SELECT to_regclass('public.devices');" \
        | grep -q devices; then

        echo "✓ Schema in '$DATABASE' bereits vorhanden"
    else
        echo "Importiere Schema nach '$DATABASE'..."

        PGPASSWORD="$DB_PASSWORD" psql \
            -U "$DB_USER" \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -d "$DATABASE" \
            -f "$SCHEMA_FILE"

        echo "✓ Schema in '$DATABASE' importiert"
    fi
done

echo
echo "[7/7] Bereite Nginx vor..."

if ! command -v nginx >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y nginx
fi

python3 - "$NGINX_TEMPLATE" "$NGINX_LOCAL" "$PROJECT_ROOT" <<'PY'
import sys
from pathlib import Path

template = Path(sys.argv[1]).read_text()
output = Path(sys.argv[2])
project_root = sys.argv[3]

output.write_text(
    template.replace("__CAMPUSHUB_ROOT__", project_root)
)
PY

sudo ln -sf \
    "$NGINX_LOCAL" \
    /etc/nginx/sites-enabled/campushub.conf

sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx

echo
echo "======================================"
echo "       CampusHub Setup beendet"
echo "======================================"
echo
echo "Frontend:"
echo "  http://localhost:8081"
echo
echo "Backend:"
echo "  cd backend"
echo "  uv run uvicorn campushub.__main__:app --reload"
echo
echo "Swagger:"
echo "  http://localhost:8081/api/docs"
echo
