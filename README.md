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

### 3️⃣ init.json (Tabllendaten) hochladen
```bash
curl -X 'POST' \
  'http://localhost:8000/api/init' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@init.json;type=application/json'
```
Hier müssen ggf die Pfade angepast werden.


### 4️⃣ fertig
Seite öffnen ``http://localhost:8000``
