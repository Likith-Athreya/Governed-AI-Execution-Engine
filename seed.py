import sqlite3
import os

DB_PATH = os.path.join("db", "app.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    ssn TEXT,
    salary INTEGER
)
""")

cursor.execute("DELETE FROM customers")

cursor.executemany(
    "INSERT INTO customers (id, name, email, ssn, salary) VALUES (?, ?, ?, ?, ?)",
    [
        (1, "Alice", "alice@example.com", "XXX-XX-1111", 70000),
        (2, "Bob", "bob@example.com", "XXX-XX-2222", 80000),
        (3, "Charlie", "charlie@example.com", "XXX-XX-3333", 90000),
    ]
)

conn.commit()
conn.close()

print("app.db seeded successfully")
