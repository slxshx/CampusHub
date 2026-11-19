# CampusHub – Lokale Einrichtung und Nutzung

Diese Anleitung dokumentiert die bereits vorhandenen Setup- und Startskripte des abgeschlossenen Schulprojekts. Sie ergänzt die [Haupt-README](../../README.md); sie verändert keine Anwendungskomponenten.

## Aufbau

```text
Browser → Nginx (localhost:8081)
             ├── /        → statisches Frontend
             └── /api/... → FastAPI (localhost:8000) → PostgreSQL
```

Der Fake-SNMP-Collector läuft separat und schreibt Gerätesnapshots über die Services und Repositories in PostgreSQL.

## Voraussetzungen

- Git zum Klonen des Repositories
- Python 3.12 oder neuer (laut `backend/pyproject.toml`)
- `uv` für Python-Abhängigkeiten
- PostgreSQL für die Datenhaltung
- Nginx als Einstiegspunkt

Die mitgelieferten Setup-Skripte unterstützen **macOS (Homebrew)**, **Debian/Ubuntu (apt, sudo)** und **Windows (PowerShell, WinGet)**. Je nach System installieren sie fehlende Werkzeuge oder erwarten bereits vorhandene Software. Die Skripte wurden für diese Dokumentationsbereinigung nicht neu ausgeführt.

## Repository holen

```bash
git clone https://github.com/slxshx/CampusHub.git
cd CampusHub
```

## Einmaliges Setup

Im Repository-Hauptverzeichnis das passende Skript ausführen:

**macOS**

```bash
./scripts/setup-macos.sh
```

**Debian / Ubuntu**

```bash
./scripts/setup-linux.sh
```

**Windows / PowerShell**

```powershell
.\scripts\setup-windows.ps1
```

Die Skripte erzeugen zunächst `backend/.env` aus `backend/.env.example` und beenden sich, damit die Datenbankzugangsdaten eingetragen werden können. Die Vorlage enthält Platzhalter – insbesondere ist `DB_PORT` noch **keine gültige Zahl**.

Beispielwerte für eine lokale Installation:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushub
DB_USER=campushub_app
DB_PASSWORD=hier-ein-eigenes-passwort-eintragen
```

Danach dasselbe Setup-Skript erneut ausführen. Die Skripte legen die benötigten PostgreSQL-Rollen und Datenbanken an, synchronisieren die Python-Abhängigkeiten und generieren die lokale Nginx-Konfiguration. Sie importieren das Schema aus `backend/scripts/schema.sql`.

**Hinweis zum aktuellen Stand:** Die Setup-Skripte prüfen zur Erkennung eines bereits vorhandenen Schemas noch auf `public.devices`; das aktuelle Schema verwendet jedoch `public.managed_devices`. Ein erneuter Import in eine bereits initialisierte Datenbank kann deshalb scheitern. Dies ist eine bekannte Inkonsistenz der vorhandenen Skripte, keine zusätzliche Setup-Anforderung.

## Anwendung starten

Im Repository-Hauptverzeichnis:

| System | Start | Stop |
| --- | --- | --- |
| macOS | `./scripts/dev-start-macos.sh` | `./scripts/dev-stop-macos.sh` |
| Debian/Ubuntu | `./scripts/dev-start-linux.sh` | `./scripts/dev-stop-linux.sh` |
| Windows (PowerShell) | `.\scripts\dev-start-windows.ps1` | `.\scripts\dev-stop-windows.ps1` |

Der Start startet die lokalen Dienste und führt Uvicorn im Vordergrund aus. Alternativ lässt sich das Backend aus `backend/` starten:

```bash
uv run uvicorn campushub.__main__:app --reload
```

Anschließend sind lokal vorgesehen:

- Frontend: <http://localhost:8081/>
- API-Health: <http://localhost:8081/api/health>
- Swagger: <http://localhost:8081/api/docs>
- FastAPI direkt: <http://127.0.0.1:8000/docs>

Einige Frontend-Dateien verwenden derzeit fest eingetragene `localhost:8000`-URLs statt relativer Pfade. Die gezeigte Konfiguration ist deshalb als **lokale Demonstrationsumgebung** zu verstehen, nicht als fertiges Remote-Deployment.

## Beispieldaten erzeugen

Der mitgelieferte **FakeSnmpCollector** simuliert Router, Switch, Server und Client. Es ist kein Collector für reale SNMP-Geräte implementiert. Der Simulator startet **nicht automatisch** mit dem Webserver.

In einem zweiten Terminal:

```bash
cd backend
uv run python scripts/collectors/fake_snmp_collector.py --seed-only
```

Damit werden die Ausgangsdaten ohne Event-Erkennung gespeichert. Für eine Demo mit Zustandsänderungen:

```bash
uv run python scripts/collectors/fake_snmp_collector.py --cycles 20 --interval 15
```

Der Collector erzeugt eine neue Ausgangslage und durchläuft die simulierten Änderungen. Mit `Ctrl+C` kann er gestoppt werden.

## API und Tests

Über den Nginx-Einstiegspunkt stehen die Read-Endpunkte `/api/health`, `/api/devices`, `/api/devices/{device_id}`, `/api/events` und `/api/devices/{device_id}/events` zur Verfügung.

Nach Entfernung der veralteten Test-Suite ist derzeit nur noch der Datenbank-Verbindungstest unter `backend/tests/integration/database/test_connection.py` enthalten. Er erwartet eine erreichbare Datenbank `campushub_test`. Zum Aufruf aus `backend/`:

```bash
uv run pytest
```

Die `backend/.env` enthält lokale Zugangsdaten und gehört nicht ins Repository. Die ältere Datei `backend/scripts/campushub_backup.sql` enthält einen Datenbank-Snapshot mit Beispieldaten und ist **nicht** das Schema, das das Setup verwendet.
