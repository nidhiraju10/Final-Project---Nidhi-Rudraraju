import sqlite3
from pathlib import Path

DB_PATH = Path("trips.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_place TEXT NOT NULL,
            end_place TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            description TEXT
        );
    """)

    conn.commit()
    conn.close()
