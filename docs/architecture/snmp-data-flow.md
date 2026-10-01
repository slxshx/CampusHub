# CampusHub – SNMP-Datenfluss und Backend-Pipeline

## Ziel

Das Backend von CampusHub wurde so aufgebaut, dass Gerätedaten zentral über SNMP eingesammelt, in PostgreSQL gespeichert und anschließend über eine einfache REST-API für das Frontend bereitgestellt werden.

Die zentrale Idee ist:

```text
SNMP Collector / Simulator
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

Ein späterer echter SNMP-Collector soll genau dieses Objekt erzeugen. Dadurch ist dem restlichen Backend egal, ob die Daten aus einem echten Gerät oder aktuell aus einem Simulator stammen.

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

Foreign Keys verwenden `ON DELETE CASCADE`, damit abhängige SNMP-Daten automatisch entfernt werden, wenn ein Managed Device gelöscht wird.

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

Events werden separat gespeichert und später unter anderem nach Gerät und Kritikalität abrufbar sein.

## 6. SnmpIngestService

Der `SnmpIngestService` verarbeitet einen fertigen `SnmpDeviceSnapshot`.

Er erzeugt selbst keine SNMP-Daten und schreibt kein SQL.

Sein Ablauf ist:

```text
process_snapshot(snapshot)

1. Systemdaten upserten
2. Interfaces ersetzen
3. IP-Adressen ersetzen
4. Routes ersetzen
```

Die Reihenfolge ist wichtig, da IP-Adressen und Routes auf Interfaces verweisen.

Der Service ist damit die Orchestrierungs-Schicht zwischen Collector und Repository.

## 7. FakeSnmpCollector

Da zum aktuellen Entwicklungsstand noch keine echten Geräte dauerhaft angebunden werden können, wurde ein temporärer SNMP-Simulator gebaut.

Der Simulator:

- erzeugt mehrere Managed Devices
- simuliert Router, Switch, Server und Client
- erzeugt alle 15 Sekunden neue Snapshots
- erhöht die Uptime
- verändert teilweise Interface-Zustände
- variiert Routing-Werte
- ruft anschließend den `SnmpIngestService` auf

Damit kann die komplette Backend-Pipeline getestet werden, ohne von realer Hardware abhängig zu sein.

Später wird nur der Simulator durch einen echten SNMP-Collector ersetzt. Der restliche Flow kann unverändert bleiben:

```text
FakeSnmpCollector
        ↓ später ersetzt durch
RealSnmpCollector
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

Aktuell werden zwei zentrale Device-Endpunkte bereitgestellt.

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

## 11. Events

Die Event-Struktur ist bereits vorbereitet.

Ein Event enthält:

- `id`
- `device_id`
- optional `interface_index`
- `timestamp`
- `severity`
- `event_type`
- `source`
- `message`

Severity:

- `info`
- `warning`
- `error`
- `critical`

Event-Quellen:

- `snmp_poll`
- `snmp_trap`
- `syslog`
- `system`

Geplant ist, später beim Einlesen eines neuen Snapshots Zustandsänderungen zu erkennen.

Beispiel:

```text
vorher:
Interface oper_status = 1

neuer Poll:
Interface oper_status = 2

→ Event:
event_type = interface_down
severity = warning / critical
```

Events sollen später unter anderem über die API nach Kritikalität gefiltert werden können.

## Aktueller Stand

Die vollständige Test-Pipeline funktioniert bereits:

```text
Fake SNMP Daten
→ Snapshot
→ Ingest Service
→ Repository
→ PostgreSQL
→ Read Service
→ Response Schema
→ FastAPI
→ Swagger / Frontend
```

Der nächste geplante Schritt ist die Event-Erkennung anhand von Zustandsänderungen zwischen zwei SNMP-Polls.

