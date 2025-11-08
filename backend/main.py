from fastapi import FastAPI, UploadFile, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from datetime import datetime, date
import sqlite3, json, io, os
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
from datetime import datetime, date, datetime as dt

# ---------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.getenv("DB_FILE", os.path.join(DATA_DIR, "finance.db"))

app = FastAPI(title="Finance Tracker API")

# ---------------------------------------------------------------------
# Datenbank Setup
# ---------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            balance REAL DEFAULT 0,
            last_change TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            amount REAL,
            description TEXT,
            date TEXT,
            FOREIGN KEY(person_id) REFERENCES people(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------
class TransactionInput(BaseModel):
    person_id: int
    amount: float
    description: str | None = None

# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@app.post("/api/init")
async def initialize_database(file: UploadFile):
    """Initialisiert DB mit JSON-Datei (Namen + E-Mail)"""
    try:
        data = json.load(io.BytesIO(await file.read()))
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for entry in data:
            c.execute(
                "INSERT OR IGNORE INTO people (name, email, balance, last_change) VALUES (?, ?, 0, ?)",
                (entry["name"], entry["email"], datetime.now().isoformat())
            )
        conn.commit()
        conn.close()
        return {"status": "ok", "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/people")
def list_people():
    """Alle Personen mit ID, Name, E-Mail, Saldo, letzte Änderung"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, email, balance, last_change FROM people ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "email": r[2], "balance": r[3], "last_change": r[4]}
        for r in rows
    ]

@app.post("/api/transaction")
def add_transaction(t: TransactionInput):
    """Einzahlung (+) oder Auszahlung (-) über ID"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT balance FROM people WHERE id = ?", (t.person_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Person nicht gefunden")

    balance = row[0]
    new_balance = balance + t.amount
    now = datetime.now().isoformat()

    c.execute("INSERT INTO transactions (person_id, amount, description, date) VALUES (?, ?, ?, ?)",
              (t.person_id, t.amount, t.description, now))
    c.execute("UPDATE people SET balance = ?, last_change = ? WHERE id = ?", (new_balance, now, t.person_id))

    conn.commit()
    conn.close()

    return {"person_id": t.person_id, "new_balance": new_balance}








# ---------------------------------------------------------------------
# REPORT: Einzelperson
# ---------------------------------------------------------------------
@app.get("/api/report/person")
def report_person(
    person_id: int,
    start: dt | None = Query(None),
    end: dt | None = Query(None),
    day: date | None = Query(None)
):
    """PDF-Bericht für eine Person inkl. Datum + Uhrzeit"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, email FROM people WHERE id = ?", (person_id,))
    person = c.fetchone()
    if not person:
        conn.close()
        raise HTTPException(status_code=404, detail="Person nicht gefunden")
    name, email = person

    query = "SELECT amount, description, date FROM transactions WHERE person_id = ?"
    params = [person_id]

    if day:
        query += " AND date LIKE ?"
        params.append(f"{day.isoformat()}%")
    elif start and end:
        query += " AND date BETWEEN ? AND ?"
        params += [start.isoformat(sep=" "), end.isoformat(sep=" ")]
    elif start:
        query += " AND date >= ?"
        params.append(start.isoformat(sep=" "))
    elif end:
        query += " AND date <= ?"
        params.append(end.isoformat(sep=" "))

    query += " ORDER BY date ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Bericht für {name} (ID: {person_id})", ln=True)
    pdf.set_font("Arial", "", 12)

    if day:
        pdf.cell(200, 10, f"Tag: {day}", ln=True)
    elif start or end:
        start_str = start.strftime("%d.%m.%Y %H:%M") if start else "---"
        end_str = end.strftime("%d.%m.%Y %H:%M") if end else "---"
        pdf.cell(200, 10, f"Zeitraum: {start_str} bis {end_str}", ln=True)
    else:
        pdf.cell(200, 10, "Zeitraum: Alle Transaktionen", ln=True)
    pdf.ln(10)

    total = 0
    for amount, desc, d in rows:
        total += amount
        dt_obj = datetime.fromisoformat(d)
        formatted_date = dt_obj.strftime("%d.%m.%Y %H:%M")
        pdf.cell(0, 10, f"{formatted_date} | {amount:+.2f} EUR | {desc or ''}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Summe im Zeitraum: {total:+.2f} EUR", ln=True)

    label = f"day_{day}" if day else f"period_{start or 'all'}_{end or 'all'}"
    filename = os.path.join(DATA_DIR, f"report_{person_id}_{label}.pdf")
    pdf.output(filename)

    return FileResponse(filename, media_type="application/pdf", filename=os.path.basename(filename))


# ---------------------------------------------------------------------
# REPORT: Tages- oder Zeitraumbericht für alle Personen
# ---------------------------------------------------------------------
@app.get("/api/report/daily")
def report_daily(
    day: date | None = Query(None),
    start: dt | None = Query(None),
    end: dt | None = Query(None)
):
    """PDF-Bericht aller Personen inkl. Datum + Uhrzeit"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = """
        SELECT p.id, p.name, t.amount, t.description, t.date
        FROM transactions t
        JOIN people p ON t.person_id = p.id
        WHERE 1=1
    """
    params = []

    if day:
        query += " AND t.date LIKE ?"
        params.append(f"{day.isoformat()}%")
    elif start and end:
        query += " AND t.date BETWEEN ? AND ?"
        params += [start.isoformat(sep=" "), end.isoformat(sep=" ")]
    elif start:
        query += " AND t.date >= ?"
        params.append(start.isoformat(sep=" "))
    elif end:
        query += " AND t.date <= ?"
        params.append(end.isoformat(sep=" "))

    query += " ORDER BY t.date ASC, p.id ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    if day:
        pdf.cell(200, 10, f"Tagesbericht {day}", ln=True)
    elif start or end:
        start_str = start.strftime("%d.%m.%Y %H:%M") if start else "---"
        end_str = end.strftime("%d.%m.%Y %H:%M") if end else "---"
        pdf.cell(200, 10, f"Zeitraumbericht: {start_str} bis {end_str}", ln=True)
    else:
        pdf.cell(200, 10, "Gesamtbericht aller Transaktionen", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    total_sum = 0
    for pid, name, amount, desc, d in rows:
        total_sum += amount
        dt_obj = datetime.fromisoformat(d)
        formatted_date = dt_obj.strftime("%d.%m.%Y %H:%M")
        pdf.cell(0, 10, f"[{formatted_date}] {name} (ID {pid}): {amount:+.2f} EUR - {desc or ''}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Gesamtsumme: {total_sum:+.2f} EUR", ln=True)

    label = f"day_{day}" if day else f"period_{start or 'all'}_{end or 'all'}"
    filename = os.path.join(DATA_DIR, f"daily_report_{label}.pdf")
    pdf.output(filename)

    return FileResponse(filename, media_type="application/pdf", filename=os.path.basename(filename))




app.mount("/", StaticFiles(directory="static", html=True), name="static-root")

@app.middleware("http")
async def spa_fallback(request: Request, call_next):

    # Paths that should NOT fall back to index.html
    passthrough_prefixes = (
        "/api", "/activate", "/docs", "/redoc", "/openapi.json"
    )
    if (
        request.url.path.startswith(passthrough_prefixes)
        or os.path.isfile(f"static{request.url.path}")
    ):
        return await call_next(request)

    # For anything else, serve index.html
    with open("static/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
