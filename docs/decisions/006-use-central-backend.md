# 006 - Zentrales Backend als Zugriffsschicht

## Entscheidung
Alle Zugriffe auf die Datenbank erfolgen über das Backend von CampusHub.

## Begründung
- Netzwerkgeräte benötigen keinen direkten Datenbankzugriff
- Datenvalidierung erfolgt zentral
- Geschäftslogik befindet sich an einer definierten Stelle
- Zugriffsrechte können zentral kontrolliert werden
- Änderungen am Datenbankschema wirken sich nicht direkt auf externe Systeme aus

## Architektur

Geräte / Collector / Weboberfläche
                |
                v
             Backend
                |
                v
            PostgreSQL
