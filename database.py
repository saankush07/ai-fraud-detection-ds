import sqlite3

DB_NAME = "fraud_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO predictions (risk_level, fraud_probability) VALUES (?, ?)",
        (risk_level, probability)
    )

    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM predictions")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='HIGH'")
    high_risk = c.fetchone()[0]

    conn.close()
    return total, high_risk
