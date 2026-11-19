# CampusHub – Dokumentation

Diese Übersicht trennt die **geltende technische Beschreibung** von historischen Entwürfen.

## Technische Dokumentation

- [Lokale Einrichtung und Nutzung](development/setup.md) – Voraussetzungen, Setup-Skripte, Start/Stop, Simulator und API
- [SNMP-Datenfluss und Backend-Pipeline](architecture/snmp-data-flow.md) – implementierte Models, Services, Speicherung und Event-Verarbeitung
- [Aktuelles SQL-Schema](../backend/scripts/schema.sql) – Schema-Datei, die die Setup-Skripte importieren
- [Projektübersicht](../README.md) – Einstiegspunkt für Anwender

## Architekturentscheidungen

Die Dateien unter [`decisions/`](decisions/) dokumentieren Entscheidungen zum Zeitpunkt ihrer Entstehung. Manche beschreiben frühe Pläne oder Alternativen (beispielsweise SQLAlchemy) und sind **keine** vollständige Liste tatsächlich eingesetzter Funktionen.

## Historische Unterlagen

[Archiv](archive/README.md) – frühere Datenbankentwürfe, Planungs-Sessions, Netzplan und Screenshots. Diese Dokumente dienen der Nachvollziehbarkeit des Projektverlaufs; für Installation und Verwendung sind die oben genannten aktuellen Dateien maßgeblich.

**Projektumfang:** CampusHub verwendet einen Fake-SNMP-Collector. Ein echter SNMP-Collector, Syslog-Receiver und vollständige Benutzerverwaltung sind nicht implementiert. Der Dateiname oder ein früherer Projektplan begründet keine implementierte Funktion.
