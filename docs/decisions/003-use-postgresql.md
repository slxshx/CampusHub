# 003 - PostgreSQL als Datenbanksystem

## Entscheidung
CampusHub verwendet PostgreSQL als relationales Datenbanksystem.

## Begründung
- geeignet für strukturierte und relationale Infrastrukturdaten
- unterstützt Beziehungen, Constraints und Transaktionen
- gute Unterstützung durch Python
- für den späteren Betrieb auf Linux geeignet
- ermöglicht eine saubere Trennung zwischen Anwendung und Datenhaltung

## Hinweis
Die Datenbank wird nicht direkt von Netzwerkgeräten oder Benutzern angesprochen.
Der Zugriff erfolgt über das Backend von CampusHub.
