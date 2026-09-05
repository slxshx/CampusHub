#!/usr/bin/env bash

set -e

echo "======================================"
echo "        CampusHub Dev Stop macOS"
echo "======================================"
echo

echo "[1/2] Stoppe Nginx..."

if brew services list | grep -q "^nginx.*started"; then
    brew services stop nginx
    echo "✓ Nginx gestoppt"
else
    echo "✓ Nginx läuft bereits nicht"
fi

echo

echo "[2/2] Stoppe PostgreSQL..."

if brew services list | grep -q "^postgresql@17.*started"; then
    brew services stop postgresql@17
    echo "✓ PostgreSQL gestoppt"
else
    echo "✓ PostgreSQL läuft bereits nicht"
fi

echo
echo "======================================"
echo "       CampusHub wurde gestoppt"
echo "======================================"
