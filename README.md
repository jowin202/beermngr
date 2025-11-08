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
cd beermngr
docker compose up 
curl -X 'POST' \
  'http://localhost:8000/api/init' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@init.json;type=application/json'
```


  open ``http://localhost:8000``
