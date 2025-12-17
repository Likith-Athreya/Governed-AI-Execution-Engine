import sqlite3
import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "db", "audit.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_input TEXT,
        sql TEXT,
        decision TEXT,
        reason TEXT,
        simulation TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_audit(user_input, sql, decision, reason, simulation):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs
        (timestamp, user_input, sql, decision, reason, simulation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        user_input,
        sql,
        decision,
        reason,
        json.dumps(simulation)
    ))
    conn.commit()
    conn.close()
