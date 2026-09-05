#!/usr/bin/env bash

set -e

echo "======================================"
echo "        CampusHub macOS Setup"
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


# --------------------------------------------------
# Homebrew
# --------------------------------------------------

echo "[1/7] Prüfe Homebrew..."

if ! command -v brew >/dev/null 2>&1; then
    echo "FEHLER: Homebrew wurde nicht gefunden."
    echo
    echo "Installiere Homebrew zuerst:"
    echo "https://brew.sh"
    exit 1
fi

echo "✓ Homebrew gefunden"
echo


# --------------------------------------------------
# Python
# --------------------------------------------------

echo "[2/7] Prüfe Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "FEHLER: Python 3 wurde nicht gefunden."
    echo
    echo "Installiere Python mit:"
    echo "brew install python@3.12"
    exit 1
fi

echo "✓ Python gefunden: $(python3 --version)"
echo


# --------------------------------------------------
# uv
# --------------------------------------------------

echo "[3/7] Prüfe uv..."

if ! command -v uv >/dev/null 2>&1; then
    echo "uv wurde nicht gefunden."
    echo "Installiere uv..."

    brew install uv
fi

echo "✓ uv gefunden"
echo


# --------------------------------------------------
# PostgreSQL
# --------------------------------------------------

echo "[4/7] Prüfe PostgreSQL..."

if ! command -v psql >/dev/null 2>&1; then
    echo "PostgreSQL wurde nicht gefunden."
    echo "Installiere PostgreSQL 17..."

    brew install postgresql@17
fi

echo "✓ PostgreSQL gefunden"
echo


# --------------------------------------------------
# Backend / .env
# --------------------------------------------------

echo "[5/7] Bereite Backend vor..."

if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "FEHLER: backend/.env.example fehlt."
        exit 1
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"

    echo "✓ backend/.env wurde aus .env.example erstellt"
    echo
    echo "======================================"
    echo "  Einmalige Konfiguration erforderlich"
    echo "======================================"
    echo
    echo "Öffne:"
    echo "  backend/.env"
    echo
    echo "und ersetze:"
    echo "  DB_PASSWORD=CHANGE_ME"
    echo
    echo "durch ein lokales Passwort."
    echo
    echo "Danach dieses Setup-Script erneut starten."
    exit 0
fi

echo "✓ backend/.env existiert bereits"
echo

echo "Installiere Python-Abhängigkeiten..."

cd "$BACKEND_DIR"
uv sync

echo "✓ Backend-Abhängigkeiten installiert"
echo


# --------------------------------------------------
# .env Werte lesen
# --------------------------------------------------

DB_VALUES="$(
    python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path

values = {}

for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#"):
        continue

    if "=" not in line:
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
        raise SystemExit(
            f"FEHLER: {key} fehlt in backend/.env"
        )

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
    echo "FEHLER: DB_PASSWORD in backend/.env ist noch nicht gesetzt."
    exit 1
fi


# --------------------------------------------------
# Datenbank-Setup
# --------------------------------------------------

echo "[6/7] Bereite PostgreSQL-Datenbanken vor..."

brew services start postgresql@17 >/dev/null 2>&1 || true

echo "✓ PostgreSQL läuft"


# Rolle anlegen
if psql postgres -tAc \
    "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" \
    | grep -q 1; then

    echo "✓ PostgreSQL-Rolle '$DB_USER' existiert bereits"

else
    echo "Erstelle PostgreSQL-Rolle '$DB_USER'..."

    psql postgres \
        -v db_user="$DB_USER" \
        -v db_password="$DB_PASSWORD" <<'SQL'
CREATE ROLE :"db_user"
WITH LOGIN PASSWORD :'db_password';
SQL

    echo "✓ PostgreSQL-Rolle '$DB_USER' erstellt"
fi


# Dev-DB anlegen
if psql postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" \
    | grep -q 1; then

    echo "✓ Datenbank '$DB_NAME' existiert bereits"

else
    echo "Erstelle Datenbank '$DB_NAME'..."

    createdb \
        --owner="$DB_USER" \
        "$DB_NAME"

    echo "✓ Datenbank '$DB_NAME' erstellt"
fi


# Test-DB anlegen
if psql postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='$TEST_DB_NAME'" \
    | grep -q 1; then

    echo "✓ Datenbank '$TEST_DB_NAME' existiert bereits"

else
    echo "Erstelle Datenbank '$TEST_DB_NAME'..."

    createdb \
        --owner="$DB_USER" \
        "$TEST_DB_NAME"

    echo "✓ Datenbank '$TEST_DB_NAME' erstellt"
fi


# Schema-Datei prüfen
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "FEHLER: backend/scripts/schema.sql wurde nicht gefunden."
    exit 1
fi


# Schema Dev-DB
if PGPASSWORD="$DB_PASSWORD" psql \
    -U "$DB_USER" \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -d "$DB_NAME" \
    -tAc "SELECT to_regclass('public.devices');" \
    | grep -q devices; then

    echo "✓ Schema in '$DB_NAME' bereits vorhanden"

else
    echo "Importiere Schema nach '$DB_NAME'..."

    PGPASSWORD="$DB_PASSWORD" psql \
        -U "$DB_USER" \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -d "$DB_NAME" \
        -f "$SCHEMA_FILE"

    echo "✓ Schema in '$DB_NAME' importiert"
fi


# Schema Test-DB
if PGPASSWORD="$DB_PASSWORD" psql \
    -U "$DB_USER" \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -d "$TEST_DB_NAME" \
    -tAc "SELECT to_regclass('public.devices');" \
    | grep -q devices; then

    echo "✓ Schema in '$TEST_DB_NAME' bereits vorhanden"

else
    echo "Importiere Schema nach '$TEST_DB_NAME'..."

    PGPASSWORD="$DB_PASSWORD" psql \
        -U "$DB_USER" \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -d "$TEST_DB_NAME" \
        -f "$SCHEMA_FILE"

    echo "✓ Schema in '$TEST_DB_NAME' importiert"
fi

echo


# --------------------------------------------------
# Nginx
# --------------------------------------------------

echo "[7/7] Bereite Nginx vor..."

if ! command -v nginx >/dev/null 2>&1; then
    echo "Nginx wurde nicht gefunden."
    echo "Installiere Nginx..."

    brew install nginx
fi

echo "✓ Nginx gefunden"


if [ ! -f "$NGINX_TEMPLATE" ]; then
    echo "FEHLER: nginx/campushub.conf.template fehlt."
    exit 1
fi


echo "Generiere lokale CampusHub-Nginx-Konfiguration..."

python3 - "$NGINX_TEMPLATE" "$NGINX_LOCAL" "$PROJECT_ROOT" <<'PY'
import sys
from pathlib import Path

template_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
project_root = sys.argv[3]

template = template_path.read_text()

config = template.replace(
    "__CAMPUSHUB_ROOT__",
    project_root,
)

output_path.write_text(config)
PY

echo "✓ nginx/campushub.local.conf erzeugt"


NGINX_SERVERS_DIR="$(brew --prefix)/etc/nginx/servers"
NGINX_LINK="$NGINX_SERVERS_DIR/campushub.conf"

mkdir -p "$NGINX_SERVERS_DIR"

if [ -L "$NGINX_LINK" ]; then
    rm "$NGINX_LINK"

elif [ -e "$NGINX_LINK" ]; then
    echo
    echo "FEHLER:"
    echo "$NGINX_LINK existiert bereits und ist kein Symlink."
    echo "Die Datei wird nicht automatisch überschrieben."
    exit 1
fi


ln -s "$NGINX_LOCAL" "$NGINX_LINK"

echo "✓ Nginx-Konfiguration verlinkt"

echo
echo "Prüfe Nginx-Konfiguration..."

nginx -t

echo
echo "Starte Nginx..."

if brew services list | grep -q "^nginx.*started"; then
    nginx -s reload
    echo "✓ Nginx neu geladen"
else
    brew services start nginx
    echo "✓ Nginx gestartet"
fi


# --------------------------------------------------
# Fertig
# --------------------------------------------------

echo
echo "======================================"
echo "       CampusHub Setup beendet"
echo "======================================"
echo

echo "Datenbanken:"
echo "  $DB_NAME"
echo "  $TEST_DB_NAME"
echo

echo "Frontend:"
echo "  http://localhost:8081"
echo

echo "Backend starten:"
echo "  cd backend"
echo "  uv run uvicorn campushub.__main__:app --reload"
echo

echo "Backend Health:"
echo "  http://127.0.0.1:8000/health"
echo

echo "Swagger:"
echo "  http://127.0.0.1:8000/docs"
echo

echo "Tests:"
echo "  cd backend"
echo "  uv run pytest"
echo
