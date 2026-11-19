# CampusHub – Backend

Das Python-Backend des abgeschlossenen [CampusHub-Schulprojekts](../README.md) basiert auf **FastAPI**, **Pydantic**, **psycopg** und **PostgreSQL**.

Es bietet lesende Endpunkte für Health, Geräte und Events. Der `SnmpIngestService` verarbeitet Snapshots aus dem separat gestarteten Fake-SNMP-Collector, und `EventService` sowie `SeverityClassifier` erkennen und bewerten Änderungen.

## Lokaler Backend-Start

Nach Einrichtung der lokalen PostgreSQL-Datenbank und `backend/.env`:

```bash
cd backend
uv sync
uv run uvicorn campushub.__main__:app --reload
```

API-Dokumentation direkt am Backend: <http://127.0.0.1:8000/docs>.

Der Backend-Server startet den Collector **nicht** automatisch. Für Beispiel-Daten aus einem zweiten Terminal (aus `backend/`):

```bash
uv run python scripts/collectors/fake_snmp_collector.py --seed-only
uv run python scripts/collectors/fake_snmp_collector.py --cycles 20 --interval 15
```

## API

| Methode | Direkter FastAPI-Pfad | Über Nginx |
| --- | --- | --- |
| GET | `/health` | `/api/health` |
| GET | `/devices` | `/api/devices` |
| GET | `/devices/{device_id}` | `/api/devices/{device_id}` |
| GET | `/events` | `/api/events` |
| GET | `/devices/{device_id}/events` | `/api/devices/{device_id}/events` |

## Struktur

- `src/campushub/api/`: FastAPI-Routen
- `src/campushub/models/` und `schemas/`: Pydantic-Modelle und API-Ausgaben
- `src/campushub/services/`: Snapshot-Verarbeitung, Zustandsvergleich und Event-Klassifizierung
- `src/campushub/repositories/` und `database/`: SQL und Datenbankverbindung
- `scripts/schema.sql`: zur Einrichtung verwendete Schema-Datei
- `scripts/collectors/fake_snmp_collector.py`: Simulationsskript
- `tests/integration/database/test_connection.py`: verbliebener Datenbank-Test (`uv run pytest`)

**Hinweis:** Das Datenbankschema, die Event-Severity-Constraint und einige Frontend-URLs enthalten im abgeschlossenen Stand bekannte Abweichungen. Einzelheiten und vollständige Setup-Schritte stehen in der [Projekt-README](../README.md) und [Einrichtungsanleitung](../docs/development/setup.md). Ein echter SNMP-Poller ist nicht implementiert.
