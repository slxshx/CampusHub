# 008 - Kein Docker in der ersten Projektumsetzung

## Entscheidung
CampusHub wird zunächst ohne Docker entwickelt und betrieben.

Für die Python-Umgebung und Abhängigkeiten wird uv verwendet.

## Begründung
- zusätzlicher Docker-Aufwand soll während des begrenzten Projektzeitraums vermieden werden
- Fokus liegt auf Softwarearchitektur, Datenbank und Schnittstellen
- die Anwendung soll zunächst direkt auf einer Linux-Umgebung betrieben werden
- Python-Abhängigkeiten können über uv reproduzierbar installiert werden

## Deployment

Entwicklung:
macOS + uv

Späterer Betrieb:
Linux + uv + virtuelle Python-Umgebung

## Ausblick
Eine Containerisierung kann später als Erweiterung durchgeführt werden,
ist jedoch nicht Bestandteil der ersten Umsetzung.
