# 007 - Collector-Architektur für externe Systeme

## Entscheidung
Für Systeme, die ihre Daten nicht selbst an CampusHub übertragen,
werden Collector-Komponenten eingesetzt.

## Begründung
- nicht auf jedem Netzwerkgerät kann eigene Software installiert werden
- unterschiedliche Geräte stellen unterschiedliche Schnittstellen bereit
- die gerätespezifische Kommunikation kann vom restlichen System getrennt werden
- neue Gerätetypen können später durch zusätzliche Collector-Implementierungen ergänzt werden

## Prinzip

CampusHub Collector
        |
        v
externes Gerät
        |
        v
erfasste Daten
        |
        v
CampusHub Backend

## Mögliche Schnittstellen
Abhängig vom jeweiligen Gerät können beispielsweise folgende Technologien
zum Einsatz kommen:

- SNMP
- SSH
- REST-APIs
- ICMP

Die konkrete Auswahl wird erst nach Analyse der verfügbaren Geräte getroffen.
