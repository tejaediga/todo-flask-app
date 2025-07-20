 # init_db.py
import sqlite3

conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT,
        completed INTEGER DEFAULT 0,
        date_created TEXT DEFAULT CURRENT_TIMESTAMP,
        date_updated TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
