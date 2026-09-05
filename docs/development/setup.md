# CampusHub – Lokale Entwicklungsumgebung

Diese Anleitung beschreibt die einmalige Einrichtung und den täglichen Start
von CampusHub.

CampusHub besteht lokal aus drei Teilen:

- Nginx stellt das Frontend bereit.
- FastAPI stellt die API bereit.
- PostgreSQL speichert die Daten.

Der Browser kommuniziert ausschließlich mit Nginx.

```text
Browser
   |
   v
Nginx :8081
   |
   +---- / --------> Frontend
   |
   +---- /api/ ----> FastAPI :8000
                         |
                         v
                     PostgreSQL
```
## Windows

### 1. PowerShell im CampusHub-Ordner öffnen

Öffne den `CampusHub`-Ordner im Windows Explorer.

Dann entweder:

- oben in die Adressleiste klicken
- `powershell` eingeben
- Enter drücken

oder:

- Rechtsklick in den Ordner
- `Im Terminal öffnen`

Prüfe anschließend mit:

```powershell
pwd
