from pathlib import Path
import sqlite3, json
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"patient_data"/"mediscan.db"
DB.parent.mkdir(exist_ok=True)

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    c=conn();
    c.execute("""CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,report_date TEXT,report_type TEXT,model_label TEXT,confidence REAL,summary TEXT,parameters_json TEXT,FOREIGN KEY(patient_id) REFERENCES patients(id))""")
    c.commit(); c.close()

def save_report(name, report_type, label, confidence, summary, parameters):
    init_db(); c=conn(); now=datetime.now().isoformat(timespec="seconds")
    c.execute("INSERT OR IGNORE INTO patients(name,created_at) VALUES(?,?)",(name,now))
    pid=c.execute("SELECT id FROM patients WHERE name=?",(name,)).fetchone()[0]
    c.execute("INSERT INTO reports(patient_id,report_date,report_type,model_label,confidence,summary,parameters_json) VALUES(?,?,?,?,?,?,?)",(pid,now,report_type,label,confidence,summary,json.dumps(parameters)))
    c.commit(); c.close()

def history(name):
    init_db(); c=conn(); rows=c.execute("SELECT r.* FROM reports r JOIN patients p ON p.id=r.patient_id WHERE p.name=? ORDER BY r.report_date",(name,)).fetchall(); c.close()
    return [dict(r) for r in rows]
