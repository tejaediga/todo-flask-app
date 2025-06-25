import sqlite3

conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    category TEXT,
    date_updated TEXT
)
""")

conn.commit()
conn.close()
