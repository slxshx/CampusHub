#!/usr/bin/env bash

set -e

echo "======================================"
echo "        CampusHub Dev Stop Linux"
echo "======================================"
echo

echo "[1/2] Stoppe Nginx..."

if systemctl is-active --quiet nginx; then
    sudo systemctl stop nginx
    echo "✓ Nginx gestoppt"
else
    echo "✓ Nginx läuft bereits nicht"
fi

echo

echo "[2/2] Stoppe PostgreSQL..."

if systemctl is-active --quiet postgresql; then
    sudo systemctl stop postgresql
    echo "✓ PostgreSQL gestoppt"
else
    echo "✓ PostgreSQL läuft bereits nicht"
fi

echo
echo "======================================"
echo "       CampusHub wurde gestoppt"
echo "======================================"
