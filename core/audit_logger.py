import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "audit_logs.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS audit_logs (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        policy TEXT,
        invoice TEXT,
        decision TEXT,
        explanation TEXT
    )
                   """)
    conn.commit()
    conn.close()

def log_decision(policy, invoice, decision, explanation):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_logs (timestamp, policy, invoice, decision, explanation)
        VALUES (?, ?, ?, ?, ?)
    """,(
        datetime.utcnow().isoformat(),
        json.dumps(policy),
        json.dumps(invoice),
        decision,
        json.dumps(explanation)
         ))
    
    conn.commit()
    conn.close()