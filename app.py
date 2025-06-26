from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date
import os

app = Flask(__name__)

# --- Database initialization ---
def init_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            completed INTEGER DEFAULT 0,
            date_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Create the table if not exists

# --- Homepage ---
@app.route('/')
def home():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    
     # 🔧 Auto-create tasks table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            category TEXT DEFAULT 'General',
            date_updated TEXT DEFAULT CURRENT_DATE
        )
    """)
    conn.commit()
    today = date.today().isoformat()
    cursor.execute("UPDATE tasks SET completed = 0 WHERE date_updated < ?", (today,))
    conn.commit()


    # Reset completed tasks if the day has changed
    cursor.execute("UPDATE tasks SET completed = 0 WHERE date_updated < ?", (today,))
    conn.commit()

    category_filter = request.args.get('category', 'All')
    status_filter = request.args.get('filter', 'all')

    query = "SELECT id, title, category, completed FROM tasks WHERE 1=1"
    values = []

    if category_filter != "All":
        query += " AND category = ?"
        values.append(category_filter)

    if status_filter == "completed":
        query += " AND completed = 1"
    elif status_filter == "pending":
        query += " AND completed = 0"

    cursor.execute(query, values)
    tasks = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM tasks")
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return render_template("index.html", tasks=tasks, categories=categories, selected_category=category_filter, selected_filter=status_filter)

# --- Add Task ---
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    category = request.form.get('category')
    today = date.today().isoformat()

    if title:
        conn = sqlite3.connect("todo.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, category, completed, date_updated) VALUES (?, ?, 0, ?)", (title, category, today))
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

# --- Mark Task Complete/Incomplete ---
@app.route('/complete/<int:task_id>')
def complete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    status = cursor.fetchone()
    if status:
        new_status = 0 if status[0] == 1 else 1
        today = date.today().isoformat()
        cursor.execute("UPDATE tasks SET completed = ?, date_updated = ? WHERE id = ?", (new_status, today, task_id))
        conn.commit()

    conn.close()
    return redirect(url_for('home'))

# --- Delete Task ---
@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# --- Edit Task ---
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_category = request.form.get('category')
        today = date.today().isoformat()

        cursor.execute("UPDATE tasks SET title = ?, category = ?, date_updated = ? WHERE id = ?", (new_title, new_category, today, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    else:
        cursor.execute("SELECT title, category FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        cursor.execute("SELECT DISTINCT category FROM tasks")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template("edit.html", task_id=task_id, task=task, categories=categories)

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
