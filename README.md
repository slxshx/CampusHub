# CampusHub

**CampusHub** ist ein im Rahmen eines Schulprojekts entwickelter Prototyp für die zentrale Erfassung, Speicherung und Darstellung von Netzwerk- und Infrastrukturinformationen. Im Repository befinden sich ein FastAPI-Backend, PostgreSQL-Datenhaltung, ein einfacher Webauftritt sowie ein **Fake-SNMP-Collector**, der reproduzierbare Beispieldaten und Zustandsänderungen erzeugt.

> **Projektstatus:** Abgeschlossener Schulprojekt-Prototyp. Das Repository dokumentiert den implementierten Stand, nicht einen produktionsfertigen Monitoring-Dienst. Der Collector simuliert Netzwerkgeräte; ein echter SNMP-Poller wurde nicht implementiert. Bekannte Einschränkungen sind [unten](#bekannte-einschränkungen) aufgelistet.

## Was ist implementiert?

| Bereich | Implementierter Umfang |
| --- | --- |
| **Geräteverwaltung (Backend)** | Speicherung und Repository-Operationen für verwaltete Router, Switches, Server und Clients |
| **SNMP-Datenmodell** | Systeminformationen, Interfaces, IP-Adressen und Routing-Einträge als Pydantic-Modelle |
| **Datenerfassung (Demo)** | Separater Fake-SNMP-Collector mit vier simulierten Gerätetypen, wiederholten Snapshots und Szenarien |
| **Datenverarbeitung** | `SnmpIngestService` zum Verarbeiten von Snapshots und Persistieren in PostgreSQL |
| **Event-Erkennung** | Vergleich aufeinanderfolgender Snapshots für Interface-Status, hinzugefügte/entfernte IPs und Routen |
| **Klassifizierung** | Schweregrad-Berechnung mit Basiswerten und Kontextregeln für Ereignisse |
| **REST-API** | Read-Endpunkte für Health, Geräteübersicht, Gerätedetails und Events |
| **Frontend** | Statische HTML-/CSS-/JS-Seiten für Übersicht und Campus-Ansichten, teilweise mit API-Anbindung |
| **Lokale Entwicklungsumgebung** | Setup- sowie Start-/Stop-Skripte für macOS, Debian/Ubuntu und Windows |

**Nicht implementiert:** ein echter SNMP-Collector, automatische Abfrage realer Geräte, vollständige Authentifizierung/Benutzerverwaltung, Syslog- oder SNMP-Trap-Empfänger und eine produktionsfertige Bereitstellung. Die vorhandenen Enums und Tabellen für einige dieser Bereiche stellen keine fertigen Funktionen dar.

## Architektur

```text
       FakeSnmpCollector (separater Prozess)
                       |
                       v
              SnmpDeviceSnapshot
                       |
                       v
              SnmpIngestService
                 |         |
                 |         +--> EventService
                 |                |
                 |                v
                 |        SeverityClassifier
                 |                |
                 v                v
               Repositories (psycopg)
                       |
                       v
                   PostgreSQL
                       ^
                       |
                 Read-Services
                       ^
                       |
                 FastAPI :8000
                       ^
                       |
           Nginx :8081 (Reverse Proxy)
                       ^
                       |
            HTML/CSS/JavaScript-Frontend
```

Die Erfassung läuft **nicht automatisch** beim Start des Webservers. Der Fake-Collector ist ein separates Skript; das Backend liest gespeicherte Informationen aus der Datenbank.

Der Aufbau trennt Verantwortlichkeiten:

- **Models/Schemas**: Validierung und Darstellung von Geräte-, SNMP- und Event-Daten
- **Services**: Datenverarbeitung, Zustandsvergleich, Klassifizierung und Zusammenstellung von API-Antworten
- **Repositories**: Datenbankzugriffe mit psycopg
- **FastAPI**: ausschließlich lesende HTTP-Endpunkte
- **Nginx**: Auslieferung des Frontends und Weiterleitung von `/api/` an FastAPI

Details: [SNMP-Datenfluss und Backend-Pipeline](docs/architecture/snmp-data-flow.md).

## Technologien

- Python **3.12+**, [uv](https://docs.astral.sh/uv/)
- FastAPI und Uvicorn
- Pydantic / pydantic-settings
- PostgreSQL mit psycopg 3
- Nginx
- HTML, CSS und JavaScript
- pytest (verbliebener Datenbank-Verbindungstest)

`pysnmp` ist als Projekt-Abhängigkeit deklariert. Das allein bedeutet nicht, dass ein echter SNMP-Poller enthalten ist.

## Schnellstart (lokal)

### 1. Voraussetzungen

Benötigt werden **Git, Python 3.12+, uv, PostgreSQL und Nginx**. Die vorhandenen Setup-Skripte können abhängig vom Betriebssystem einzelne Werkzeuge installieren beziehungsweise einrichten. Unterstützte Setup-Umgebungen sind macOS mit Homebrew, Debian/Ubuntu mit apt und Windows mit PowerShell und WinGet.

```bash
git clone https://github.com/slxshx/CampusHub.git
cd CampusHub
```

### 2. Einmaliges Setup

Passendes Skript im Projekt-Hauptverzeichnis ausführen:

| Betriebssystem | Befehl |
| --- | --- |
| macOS | `./scripts/setup-macos.sh` |
| Debian / Ubuntu | `./scripts/setup-linux.sh` |
| Windows (PowerShell) | `.\scripts\setup-windows.ps1` |

Beim ersten Durchlauf wird `backend/.env` aus der Vorlage erstellt. Trage dort die Datenbankverbindung ein; die Beispielwerte in der Vorlage sind **Platzhalter**. Beispielsweise:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushub
DB_USER=campushub_app
DB_PASSWORD=ein-eigenes-lokales-passwort
```

Anschließend das Setup-Skript **erneut** ausführen. Es richtet die benötigte PostgreSQL-Rolle und die Datenbanken ein, synchronisiert die Backend-Abhängigkeiten mit `uv`, importiert `backend/scripts/schema.sql` und konfiguriert Nginx.

**Wichtig:** Das wiederholte Schema-Setup besitzt eine bekannte Inkonsistenz (Prüfung auf die alte Tabelle `devices`). Das initiale oder wiederholte Setup ist deshalb nicht für alle Umgebungen als erfolgreich verifiziert. Siehe [bekannte Einschränkungen](#bekannte-einschränkungen).

Die ausführlichere, betriebssystemspezifische Anleitung steht unter [docs/development/setup.md](docs/development/setup.md).

### 3. CampusHub starten

| Betriebssystem | Start | Stop |
| --- | --- | --- |
| macOS | `./scripts/dev-start-macos.sh` | `./scripts/dev-stop-macos.sh` |
| Debian / Ubuntu | `./scripts/dev-start-linux.sh` | `./scripts/dev-stop-linux.sh` |
| Windows (PowerShell) | `.\scripts\dev-start-windows.ps1` | `.\scripts\dev-stop-windows.ps1` |

Die Startskripte starten PostgreSQL und Nginx und führen FastAPI/Uvicorn im Vordergrund aus. Uvicorn kann aus `backend/` auch einzeln gestartet werden:

```bash
cd backend
uv run uvicorn campushub.__main__:app --reload
```

Vorgesehene lokale Adressen:

| Dienst | URL |
| --- | --- |
| Frontend | <http://localhost:8081/> |
| API-Health über Nginx | <http://localhost:8081/api/health> |
| Swagger über Nginx | <http://localhost:8081/api/docs> |
| Swagger direkt am Backend | <http://127.0.0.1:8000/docs> |

### 4. Demo-Daten erzeugen

Der Webserver erzeugt **keine** Beispieldaten. Starte den Fake-Collector in einem **zweiten Terminal** und mit eingerichteter Datenbank:

```bash
cd backend
uv run python scripts/collectors/fake_snmp_collector.py --seed-only
```

Damit wird eine gesunde Ausgangslage für vier simulierte Geräte ohne Event-Erkennung angelegt. Für eine endliche Demo mit Zustandsänderungen:

```bash
uv run python scripts/collectors/fake_snmp_collector.py --cycles 20 --interval 15
```

Der Collector simuliert Änderungen an Interfaces, IP-Adressen und Routen. Daraus können Events erzeugt und klassifiziert werden. Die Parameter `--interval` (Sekunden) und `--cycles` (Durchläufe) steuern den Ablauf; ohne `--cycles` läuft er bis zum manuellen Abbruch mit `Ctrl+C`.

## REST-API

Die folgende Tabelle zeigt die **über Nginx** vorgesehenen Endpunkte auf `localhost:8081`. FastAPI definiert die Routen intern ohne das `/api`-Präfix.

| Methode | Endpunkt | Zweck |
| --- | --- | --- |
| GET | `/api/health` | Einfacher Status-Endpunkt (`{"health":"Online"}`) |
| GET | `/api/devices` | Alle verwalteten Geräte als Übersicht |
| GET | `/api/devices/{device_id}` | Details zu einem Gerät einschließlich System, Interfaces, IPs und Routen; bei unbekannter ID: HTTP 404 |
| GET | `/api/events` | Neueste 50 Events, absteigend sortiert |
| GET | `/api/devices/{device_id}/events` | Neueste 50 Events eines Geräts |

Beispiel eines API-Aufrufs:

```bash
curl http://localhost:8081/api/health
curl http://localhost:8081/api/devices
curl http://localhost:8081/api/events
```

Die API liefert aktuell ausschließlich **GET-Endpunkte**; die Create-/Update-/Delete-Methoden der Repository-Schicht sind nicht automatisch als HTTP-Endpunkte verfügbar.

## Event-Erkennung und Severity

Der `EventService` vergleicht beim Ingest einen neuen SNMP-Snapshot mit dem gespeicherten Zustand und erkennt:

- operative und administrative Interface-Statuswechsel
- hinzugefügte oder entfernte IP-Adressen
- hinzugefügte oder entfernte Routen

Der `SeverityClassifier` vergibt Ausgangswerte und berücksichtigt Kontext, beispielsweise eine administrative Abschaltung, den Verlust einer Standardroute oder einen Routenverlust bei gleichzeitig ausgefallenem Interface. Die Python-Modelle kennen `info`, `low`, `warning`, `high` und `critical`.

**Achtung:** Das aktuelle SQL-Schema lässt davon nicht alle Werte zu; dies ist eine bekannte Einschränkung, siehe unten. Das Repository enthält damit die Implementierung der Klassifizierungslogik, aber keine Garantie, dass jeder klassifizierte Event in der unveränderten Beispieldatenbank gespeichert werden kann.

## Repository-Struktur

```text
CampusHub/
├── backend/
│   ├── src/campushub/
│   │   ├── api/             # FastAPI-Routen
│   │   ├── config/          # Umgebungsbasierte Einstellungen
│   │   ├── database/        # PostgreSQL-Verbindung
│   │   ├── models/          # Interne Pydantic-Modelle
│   │   ├── repositories/    # Datenbankzugriff
│   │   ├── schemas/         # API-Response-Schemas
│   │   └── services/        # Verarbeitung und Klassifizierung
│   ├── scripts/
│   │   ├── collectors/      # Fake-SNMP-Collector
│   │   └── schema.sql       # Aktuelles SQL-Schema
│   └── tests/               # Verbliebener DB-Verbindungstest
├── frontend/                # Statische Webseiten
├── nginx/                   # Reverse-Proxy-Vorlage
├── scripts/                 # Setup-, Start- und Stop-Skripte
└── docs/
    ├── architecture/        # Technische Architektur
    ├── development/         # Einrichtung
    ├── decisions/           # Frühere Architekturentscheidungen
    └── archive/             # Historische Entwürfe und Projektplanung
```

## Tests

Die früheren, nicht mehr zur aktuellen Datenstruktur passenden Modell- und Repository-Tests wurden beim Abschluss-Cleanup entfernt. Der im Repository verbliebene Test ist:

`backend/tests/integration/database/test_connection.py`

Er benötigt eine laufende PostgreSQL-Instanz und die Testdatenbank `campushub_test`. Aus dem Backend-Verzeichnis:

```bash
cd backend
uv run pytest
```

Der Datenbank-Test wurde für die abschließende Dokumentationsüberarbeitung **nicht erneut ausgeführt**. Eine umfangreiche automatisierte Test-Suite oder CI-Pipeline ist im aktuellen Repository nicht enthalten.

## Bekannte Einschränkungen

Diese Punkte werden hier **dokumentiert, nicht behoben**, da CampusHub als Schulprojekt abgeschlossen ist:

1. **Abweichendes SQL-Schema:** Das Modell und `SnmpSystemRepository` verwenden `cpu`, `gpu` und `ram`; die mitgelieferte `backend/scripts/schema.sql` enthält diese Spalten in `snmp_system` nicht. Die Snapshot-Verarbeitung kann dadurch in einer frisch aus dieser Datei angelegten Datenbank scheitern.
2. **Event-Severity:** Python klassifiziert Events in fünf Stufen (`info`, `low`, `warning`, `high`, `critical`); die SQL-CHECK-Constraint erlaubt nur `info`, `warning`, `error`, `critical`. `low` und `high` können deshalb beim Speichern fehlschlagen.
3. **Setup-Erkennung:** Die Setup-Skripte prüfen teilweise auf `public.devices` statt `public.managed_devices`; eine erneute Initialisierung kann zu SQL-Fehlern führen.
4. **Frontend-API-Pfade:** Einige HTML-/JS-Dateien verwenden `http://localhost:8000/api/devices`, obwohl die API über Nginx unter `http://localhost:8081/api/devices` vorgesehen ist und die direkten FastAPI-Routen keinen `/api`-Präfix besitzen.
5. **Frontend-Demo:** Teile der Campus-Seiten zeigen fest eingetragene Infrastruktur- und Statusinformationen. Diese stellen keine Live-Messungen dar. Weitere Frontend-Seiten sind unvollständig, und eine Campus-Ansicht referenziert eine nicht vorhandene JavaScript-Datei.
6. **Keine reale SNMP-Erfassung:** Der Fake-Collector arbeitet mit simulierten Daten. Eine echte Geräteanbindung, produktiver Hintergrunddienst oder vollständige Betriebsüberwachung sind nicht enthalten.
7. **Begrenzte Tests:** Die Integration wurde für diese README nicht Ende-zu-Ende verifiziert. Der einzige verbliebene Test prüft die Datenbankverbindung.

Die genannten Probleme sollten bei einem eigenständigen Nachbau oder einer Weiterentwicklung berücksichtigt werden. **Diese README beschreibt bewusst den Repository-Stand und beansprucht keine uneingeschränkt funktionsfähige Neuinstallation.**

## Weitere Dokumentation

- [Dokumentationsübersicht](docs/README.md)
- [Lokale Einrichtung und Nutzung](docs/development/setup.md)
- [SNMP-Datenfluss und Backend-Architektur](docs/architecture/snmp-data-flow.md)
- [Historische Entscheidungen](docs/decisions/)
- [Projektarchiv und ursprüngliche Planungsunterlagen](docs/archive/README.md)

## Hintergrund

CampusHub entstand als Schulprojekt zur praktischen Auseinandersetzung mit Monitoring, Logging, REST-APIs, relationaler Datenhaltung und modularer Backend-Architektur. Im Vordergrund standen die Trennung von Verantwortlichkeiten und die Nachvollziehbarkeit des Datenflusses. Das Projekt ist in seinem schulischen Umfang abgeschlossen.
