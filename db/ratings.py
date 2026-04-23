import sqlite3
from pathlib import Path

DB_PATH = "ratings.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            title TEST NOT NULL,
            rating INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ) 
    """)  

    conn.commit()
    conn.close()  

def save_rating(book_id: str, title: str, rating: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ratings (book_id, title, rating)
        VALUES (?, ?, ?)
    """, (book_id, title, rating))

    conn.commit()
    conn.close()

def get_ratings() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT book_id, title, rating FROM ratings")
    rows = cursor.fetchall()
    conn.close()

    return [
        {"book_id": row[0], "title": row[1], "rating": row[2]}
        for row in rows
    ]