# CampusHub

CampusHub ist ein schulisches Monitoring- und Logging-System für Netzwerk- und Server-Infrastruktur.

## Architektur

CampusHub besteht aus:

- Nginx als zentralem Einstiegspunkt
- einem statischen HTML/CSS/JS-Frontend
- einem FastAPI-Backend
- PostgreSQL als Datenbank

Ablauf:

Browser → Nginx → Frontend oder `/api/...` → FastAPI → PostgreSQL

Das Frontend verwendet ausschließlich relative API-Pfade wie:

`/api/devices`

Dadurch bleibt das Routing lokal und später im Deployment gleich.

## Projektstruktur

- `backend/` – FastAPI, Models, Repositories, Services, Collector, Tests
- `frontend/` – HTML, CSS, JavaScript
- `nginx/` – Nginx-Konfiguration
- `scripts/` – Setup-, Start- und Stop-Scripts
- `docs/` – technische Dokumentation

## Lokales Setup

Die vollständige Anleitung befindet sich unter:

`docs/development/setup.md`

Einmalige Einrichtung:

macOS:
`./scripts/setup-macos.sh`

Linux:
`./scripts/setup-linux.sh`

Windows:
`.\scripts\setup-windows.ps1`

## Entwicklung starten

macOS:
`./scripts/dev-start-macos.sh`

Linux:
`./scripts/dev-start-linux.sh`

Windows:
`.\scripts\dev-start-windows.ps1`

Danach:

- CampusHub: `http://localhost:8081`
- Health Check: `http://localhost:8081/api/health`
- Swagger: `http://localhost:8081/api/docs`

## Entwicklung stoppen

macOS:
`./scripts/dev-stop-macos.sh`

Linux:
`./scripts/dev-stop-linux.sh`

Windows:
`.\scripts\dev-stop-windows.ps1`

## Tests

Die Tests befinden sich unter `backend/tests/`.

Ausführen:

`cd backend`
`uv run pytest`

Für Integrationstests wird die separate Datenbank `campushub_test` verwendet.

## Wichtige Regeln

- Frontend greift niemals direkt auf PostgreSQL zu.
- Frontend verwendet nur `/api/...`.
- Datenbankzugriffe laufen über Repositories.
- Business-Logik gehört in Services.
- Collector sollen keine SQL-Logik enthalten.
- `.env` und andere lokale Geheimnisse werden nicht committed.
