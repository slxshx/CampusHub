# 005 - REST-API als Anwendungsschnittstelle

## Entscheidung
CampusHub stellt eine REST-API zur Kommunikation mit der Anwendung bereit.

## Begründung
- klare Trennung zwischen Frontend und Backend
- standardisierte Kommunikation über HTTP
- andere Systeme können Daten bereitstellen oder abrufen
- erleichtert spätere Erweiterungen
- unabhängig von der konkreten Benutzeroberfläche

## Verwendung
Die REST-API kann unter anderem verwendet werden für:

- Abruf von Geräteinformationen
- Abruf von Monitoringdaten
- Übertragung von Daten durch externe Systeme oder Agents
- Kommunikation zwischen Weboberfläche und Backend
