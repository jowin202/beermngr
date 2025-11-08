# 🍺 Beermngr – Bierverwaltungs-App

Willkommen beim **Beermngr**!  
Verwalte Getränkekonten, verarbeite Ein-/Auszahlungen und generiere PDF-Reports – alles mit einer modernen UI.

---

## 🚀 Schnellstart mit Docker

> Voraussetzung:  
> 🐳 Docker & Docker Compose installiert

### 1️⃣ Repository klonen

```bash
git clone git@github.com:jowin202/beermngr.git
```

### 2️⃣ Container starten
```bash
cd beermngr
docker compose up
```

### 3️⃣ init.json (Tabllendaten) anpassen
Passe Namen und Mail Adressen aller Teilnehmer an. Reihenfolge wird in Tabelle übernommen 
```json[
[
  {"name": "Max Mustermann", "email": "max.mustermann@example.com"},
  {"name": "Erika Musterfrau", "email": "erika.musterfrau@example.com"},
  {"name": "Lukas Schneider", "email": "lukas.schneider@example.com"},
  {"name": "Anna Becker", "email": "anna.becker@example.com"},
  {"name": "Jonas Fischer", "email": "jonas.fischer@example.com"},
  {"name": "Lea Wagner", "email": "lea.wagner@example.com"},
]
```

### 4️⃣ init.json (Tabllendaten) hochladen
```bash
curl -X 'POST' \
  'http://localhost:8000/api/init' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@init.json;type=application/json'
```
Hier müssen ggf die Pfade angepast werden.


### 5️⃣ fertig
Seite öffnen ``http://localhost:8000``
