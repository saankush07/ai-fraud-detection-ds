import os
import sqlite3

try:
    import psycopg2
except ImportError:
    psycopg2 = None

SQLITE_DB = "fraud_app.db"


def _get_db_url():
    return os.getenv("DATABASE_URL", "").strip()


def _use_postgres():
    db_url = _get_db_url()
    return bool(db_url) and (psycopg2 is not None)


def init_db():
    if _use_postgres():
        conn = psycopg2.connect(_get_db_url())
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
        return

    # SQLite fallback
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
    if _use_postgres():
        conn = psycopg2.connect(_get_db_url())
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (risk_level, fraud_probability) VALUES (%s, %s)",
            (risk_level, probability)
        )
        conn.commit()
        cur.close()
        conn.close()
        return

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO predictions (risk_level, fraud_probability) VALUES (?, ?)",
        (risk_level, probability)
    )
    conn.commit()
    conn.close()


def get_stats():
    if _use_postgres():
        conn = psycopg2.connect(_get_db_url())
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM predictions")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='HIGH'")
        high_risk = cur.fetchone()[0]
        cur.close()
        conn.close()
        return int(total), int(high_risk)

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='HIGH'")
    high_risk = c.fetchone()[0]
    conn.close()
    return int(total), int(high_risk)
