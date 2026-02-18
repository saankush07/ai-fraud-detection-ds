import os
import sqlite3
from urllib.parse import urlparse

try:
    import psycopg2
except ImportError:
    psycopg2 = None

SQLITE_DB = "fraud_app.db"


def _get_db_url():
    # Streamlit Cloud secrets => os.environ
    return os.getenv("DATABASE_URL", "").strip()


def init_db():
    db_url = _get_db_url()

    if db_url:
        # PostgreSQL (Supabase/Neon/etc.)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                risk_level TEXT NOT NULL,
                fraud_probability DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    else:
        # SQLite fallback (local)
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_level TEXT NOT NULL,
                fraud_probability REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()


def insert_prediction(risk_level: str, probability: float):
    db_url = _get_db_url()

    if db_url:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (risk_level, fraud_probability) VALUES (%s, %s)",
            (risk_level, probability)
        )
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO predictions (risk_level, fraud_probability) VALUES (?, ?)",
            (risk_level, probability)
        )
        conn.commit()
        conn.close()


def get_stats():
    db_url = _get_db_url()

    if db_url:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM predictions")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='HIGH'")
        high_risk = cur.fetchone()[0]
        cur.close()
        conn.close()
        return int(total), int(high_risk)
    else:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM predictions")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='HIGH'")
        high_risk = c.fetchone()[0]
        conn.close()
        return int(total), int(high_risk)
