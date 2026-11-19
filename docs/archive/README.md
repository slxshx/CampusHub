# CampusHub – Archiv

Diese Dateien stammen aus früheren Planungs- und Entwicklungsphasen. Sie wurden **unverändert archiviert** (mit Ausnahme einer Korrektur des irreführenden Dateinamens der Quality-Session). Sie dokumentieren Ideen und Zwischenstände, nicht den zuletzt implementierten Funktionsumfang.

## Inhalte

- [`database-v1/`](database-v1/) – erster Datenbankentwurf: ER-Diagramm (draw.io und PNG), Schemaausgabe, Designnotizen und damaliger initialer SQL-Dump. Enthält teilweise Tabellen wie `devices`, `interfaces`, `metrics` und `device_assignments`, die nicht Teil des aktuellen Schemas sind.
- [`planning/`](planning/) – historische Session-Pläne sowie der Netzplan für das Schulprojekt. Die frühere Datei `2026-01-09.md` wurde nach der im Dokument angegebenen Session auf `2026-09-01.md` umbenannt.
- [`screenshots/`](screenshots/) – Screenshot aus der frühen Projekteinitialisierung.

## Maßgeblicher Stand

- Aktuelle Struktur: [`../../backend/scripts/schema.sql`](../../backend/scripts/schema.sql)
- Aktuelle Architektur: [`../architecture/snmp-data-flow.md`](../architecture/snmp-data-flow.md)
- Einrichtung: [`../development/setup.md`](../development/setup.md)

Der Datenbank-Snapshot `backend/scripts/campushub_backup.sql` bleibt unverändert an seinem bisherigen Ort. Er enthält Beispiel-Datensätze und ist keine Anweisung für das Neuaufsetzen des Schemas.
