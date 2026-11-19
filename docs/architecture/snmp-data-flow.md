# CampusHub – SNMP-Datenfluss und Backend-Pipeline

## Ziel

CampusHub verarbeitet strukturierte SNMP-Gerätesnapshots, speichert sie in PostgreSQL und stellt die Daten über eine REST-API für das Frontend bereit. Im abgeschlossenen Schulprojekt stammen die Snapshots aus einem SNMP-Simulator; ein Collector, der reale Geräte per SNMP abfragt, ist nicht implementiert.

Die zentrale Idee ist:

```text
Fake SNMP Collector
        ↓
SnmpDeviceSnapshot
        ↓
SnmpIngestService
        ↓
Repositories
        ↓
PostgreSQL
        ↓
DeviceReadService
        ↓
Response Schemas
        ↓
FastAPI
        ↓
Frontend
```

Der Collector kennt dabei keine SQL-Logik und die API kennt keine SNMP-OIDs. Jede Schicht hat eine klar getrennte Aufgabe.

## 1. Managed Devices

Geräte, die von CampusHub überwacht werden sollen, werden zuerst als `ManagedDevice` angelegt.

Ein Managed Device enthält nur Verwaltungsdaten:

- `id`
- `management_ip`
- `device_type`
- `enabled`
- `snmp_port`
- `snmp_version`

Der eigentliche Hostname, die Beschreibung, der Standort oder die Interfaces werden nicht manuell im Managed Device gepflegt, sondern später aus SNMP-Daten übernommen.

Unterstützte Gerätetypen sind aktuell Router, Switch, Server und Client.

## 2. SNMP-Modelle

Die SNMP-Daten wurden entsprechend der tatsächlichen Struktur der SNMP-Abfragen modelliert.

### SnmpSystem

Enthält allgemeine Systeminformationen:

- `device_id`
- `description`
- `object_id`
- `uptime`
- `name`
- `location`

Diese Werte entsprechen unter anderem `sysDescr`, `sysObjectID`, `sysUpTime`, `sysName` und `sysLocation`.

### SnmpInterface

Enthält Informationen über ein einzelnes Interface:

- `device_id`
- `if_index`
- `description`
- `interface_type`
- `mtu`
- `speed`
- `mac_address`
- `admin_status`
- `oper_status`

Der `if_index` ist nur innerhalb eines Geräts eindeutig. Deshalb wird in der Datenbank die Kombination aus `device_id` und `if_index` verwendet.

### SnmpIpAddress

IP-Adressen werden separat gespeichert, da SNMP sie ebenfalls separat liefert:

- `device_id`
- `interface_index`
- `address`
- `subnet_mask`

Über `interface_index` wird eine IP-Adresse später wieder einem Interface zugeordnet.

### SnmpRoute

Routinginformationen enthalten:

- `device_id`
- `interface_index`
- `destination`
- `subnet_mask`
- `next_hop`
- `route_type`
- `protocol`
- `age`

## 3. SnmpDeviceSnapshot

Der `SnmpDeviceSnapshot` ist kein eigener Datenbank-Datensatz. Er dient als Transportobjekt zwischen Collector und Service und enthält:

```text
SnmpDeviceSnapshot
├── system
├── interfaces[]
├── ip_addresses[]
└── routes[]
```

Der implementierte FakeSnmpCollector erzeugt dieses Objekt. Durch die Trennung der Schichten wäre eine andere Datenquelle möglich, ist aber kein Bestandteil der abgeschlossenen Implementierung.

## 4. Datenbankstruktur

Die aktuelle SNMP-Basisstruktur besteht aus:

```text
managed_devices
snmp_system
snmp_interfaces
snmp_ip_addresses
snmp_routes
events
users
```

### Beziehungen

```text
managed_devices
    │
    ├── 1:1 snmp_system
    │
    ├── 1:n snmp_interfaces
    │       │
    │       └── 1:n snmp_ip_addresses
    │
    ├── 1:n snmp_routes
    └── 1:n events
```

Die meisten SNMP-Fremdschlüssel verwenden `ON DELETE CASCADE`, damit zugehörige Daten beim Löschen eines Managed Device entfernt werden. Die Tabelle `users` ist noch im aktuellen SQL-Schema vorhanden, wird jedoch von keinem aktiven Benutzer-Workflow verwendet.

## 5. Repository-Schicht

Repositories kapseln den Datenbankzugriff.

### ManagedDeviceRepository

Verwendet das vorhandene `BaseRepository` und stellt klassische CRUD-Operationen bereit:

- Geräte auflisten
- Gerät per ID laden
- Gerät anlegen
- Gerät aktualisieren
- Gerät löschen

### SnmpSystemRepository

Wichtige Operationen:

- `get_by_device(...)`
- `upsert(...)`

Da pro Gerät nur ein aktueller Systemdatensatz existiert, wird dieser angelegt oder aktualisiert.

### SnmpInterfaceRepository

Wichtige Operationen:

- `get_by_device(...)`
- `replace_for_device(...)`

Der aktuelle Interface-Zustand eines Geräts wird bei einem neuen Poll vollständig ersetzt.

### SnmpIpAddressRepository

Wichtige Operationen:

- `get_by_device(...)`
- `replace_for_device(...)`

### SnmpRouteRepository

Wichtige Operationen:

- `get_by_device(...)`
- `replace_for_device(...)`

### EventRepository

Events werden separat gespeichert. Die API liefert die 50 neuesten Events insgesamt oder die 50 neuesten Events eines Geräts; eine Filterung nach Kritikalität ist nicht implementiert.

## 6. SnmpIngestService

Der `SnmpIngestService` verarbeitet einen fertigen `SnmpDeviceSnapshot`.

Er erzeugt selbst keine SNMP-Daten und schreibt kein SQL.

Sein Ablauf ist:

```text
process_snapshot(snapshot, detect_events=True)

1. Sofern aktiviert: alten und neuen Zustand vergleichen, Events klassifizieren und speichern
2. Systemdaten upserten
3. Interfaces ersetzen
4. IP-Adressen ersetzen
5. Routes ersetzen
```

Die Reihenfolge ist wichtig, da IP-Adressen und Routes auf Interfaces verweisen.

Der Service ist damit die Orchestrierungs-Schicht zwischen Collector und Repository.

## 7. FakeSnmpCollector

Für die Demonstration der abgeschlossenen Anwendung wurde ein Fake-SNMP-Collector implementiert. Ein realer SNMP-Poller ist in diesem Repository nicht vorhanden.

Der Simulator:

- erzeugt mehrere Managed Devices
- simuliert Router, Switch, Server und Client
- erzeugt alle 15 Sekunden neue Snapshots
- erhöht die Uptime
- verändert teilweise Interface-Zustände
- variiert Routing-Werte
- ruft anschließend den `SnmpIngestService` auf

Damit kann die komplette Backend-Pipeline getestet werden, ohne von realer Hardware abhängig zu sein.

Die Architektur trennt die Datenerfassung von der Verarbeitung. Ein echter Collector wäre eine denkbare Erweiterung, gehört aber nicht zum abgeschlossenen Umfang:

```text
FakeSnmpCollector (implementiert)
        ↓
SnmpDeviceSnapshot
        ↓
SnmpIngestService
```

## 8. API-Response-Schemas

Die internen Datenbank-/SNMP-Models werden nicht direkt an das Frontend ausgegeben.

Stattdessen wurden eigene Response-Schemas erstellt. Grund: Die Datenbank speichert Informationen so, wie sie technisch sinnvoll sind. Das Frontend soll sie dagegen so erhalten, wie sie bequem verarbeitet werden können.

Beispiel: Intern werden Interfaces und IP-Adressen getrennt gespeichert. Die API liefert die IP-Adressen direkt innerhalb des passenden Interfaces.

Verwendete Schemas:

- `DeviceSummary`
- `DeviceDetail`
- `SystemDetail`
- `InterfaceDetail`
- `IpAddressDetail`
- `RouteDetail`

## 9. DeviceReadService

Der `DeviceReadService` liest die getrennten Daten über die Repositories und setzt sie für die API zusammen.

### Geräteübersicht

Für die Übersicht werden Managed Device und SNMP-Systemdaten kombiniert:

```text
ManagedDevice
+
SnmpSystem
↓
DeviceSummary
```

Dadurch erhält das Frontend unter anderem direkt ID, Name, Management-IP, Gerätetyp, Standort und Aktiv-Status.

### Gerätedetails

Für ein einzelnes Gerät werden kombiniert:

```text
ManagedDevice
+
SnmpSystem
+
SnmpInterfaces
+
SnmpIpAddresses
+
SnmpRoutes
↓
DeviceDetail
```

IP-Adressen werden dabei anhand von

```text
SnmpIpAddress.interface_index
==
SnmpInterface.if_index
```

dem richtigen Interface zugeordnet.

## 10. API-Endpunkte

Für Geräte und Events sind folgende Read-Endpunkte im FastAPI-Backend implementiert.

### GET `/api/devices`

Liefert eine kompakte Übersicht aller überwachten Geräte.

Beispiel:

```json
{
  "id": 1,
  "name": "CampusHub-Router-01",
  "management_ip": "192.168.10.1",
  "device_type": "router",
  "location": "Serverraum",
  "enabled": true
}
```

### GET `/api/devices/{id}`

Liefert die vollständigen aktuellen Informationen zu einem Gerät:

- Managed-Device-Daten
- Systeminformationen
- Interfaces
- zugeordnete IP-Adressen
- Routingtabelle

Das Frontend muss dadurch nicht mehrere Requests durchführen oder Daten selbst zusammensetzen.

## 11. Events und Zustandsänderungen

Bei `SnmpIngestService.process_snapshot(..., detect_events=True)` vergleicht der `EventService` den bisherigen Datenbankzustand mit dem neuen Snapshot. Erkennt er Änderungen, entstehen `EventCandidate`-Objekte für:

- Interface operativ UP/DOWN und administrativ UP/DOWN
- hinzugefügte oder entfernte IP-Adressen
- hinzugefügte oder entfernte Routen

`SeverityClassifier` bewertet Kandidaten mit Ausgangswerten und Kontextregeln. Dazu zählen administrative Abschaltungen, entfernte Standardrouten und Routenverluste zusammen mit ausgefallenen Interfaces. Das Ergebnis wird als `EventCreate` im `EventRepository` gespeichert.

Der Python-Code kennt die Schweregrade `info`, `low`, `warning`, `high` und `critical`. **Bekannte Abweichung:** Die CHECK-Constraint der mitgelieferten `schema.sql` erlaubt dagegen `info`, `warning`, `error` und `critical`. Diese Dokumentation beschreibt den Stand, behebt die Abweichung aber nicht.

Die Event-Quelle im implementierten Simulator ist `snmp_poll`. In den Modellen sind außerdem `snmp_trap`, `syslog` und `system` als mögliche Quellen angelegt; eigenständige Trap- oder Syslog-Empfänger gehören nicht zur Implementierung.

### Event-API

- `GET /api/events` – die neuesten 50 Events, absteigend nach Zeit sortiert
- `GET /api/devices/{device_id}/events` – die neuesten 50 Events für ein Gerät

### Weitere Endpunkte

- `GET /api/health` – einfacher API-Health-Endpunkt
- `GET /api/devices` – Geräteübersicht
- `GET /api/devices/{device_id}` – Details zu einem Gerät, bei fehlender ID mit HTTP 404

Die angegebenen `/api/...`-Pfade gelten für den Zugriff über Nginx auf Port 8081. Die definierten FastAPI-Routen selbst lauten `/health`, `/devices` und `/events` usw.

## Abschlussstand

Der umgesetzte Datenweg ist:

```text
FakeSnmpCollector
  → SnmpDeviceSnapshot
  → SnmpIngestService
  → EventService / SeverityClassifier (bei aktivierter Event-Erkennung)
  → Repositories
  → PostgreSQL
  → Read-Services
  → FastAPI-Responses
  → Nginx / Frontend
```

Der Collector wird als separates Python-Skript gestartet und nicht automatisch mit dem FastAPI-Server hochgefahren. Diese Beschreibung stellt den implementierten Stand dar, keine Roadmap.
