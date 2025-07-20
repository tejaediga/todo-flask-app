from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime, date  # ✅ Fix: imported both datetime and date

app = Flask(__name__)

# ----------------------- Home Route -----------------------
@app.route("/")
def home():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # ✅ Create table if it doesn't exist
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

    # ✅ Daily reset logic
    cursor.execute("UPDATE tasks SET completed = 0 WHERE date_updated < ?", (today,))
    conn.commit()

    category_filter = request.args.get("category", "All")
    status_filter = request.args.get("filter", "all")

    query = "SELECT id, content, completed, category FROM tasks WHERE 1=1"
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

    return render_template("index.html",
                           tasks=tasks,
                           current_date=date.today().strftime('%A, %d %B %Y'),
                           selected_category=category_filter,
                           selected_filter=status_filter,
                           categories=categories,
                           today=today)

# ----------------------- Add Task -----------------------
@app.route("/add", methods=["POST"])
def add():
    content = request.form["task"]
    category = request.form.get("category", "General")
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (content, category, date_updated) VALUES (?, ?, ?)",
                   (content, category, date.today().isoformat()))
    conn.commit()
    conn.close()
    return redirect("/")

# ----------------------- Mark Complete/Incomplete -----------------------
@app.route("/complete/<int:task_id>")
def complete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = NOT completed, date_updated = ? WHERE id = ?",
                   (date.today().isoformat(), task_id))
    conn.commit()
    conn.close()
    return redirect("/")

# ----------------------- Delete Task -----------------------
@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ----------------------- Edit Task -----------------------
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    if request.method == "POST":
        content = request.form["content"]
        category = request.form.get("category", "General")
        completed = 1 if request.form.get("completed") == "on" else 0
        date_updated = datetime.now().date()
        cursor.execute("UPDATE tasks SET content = ?, category = ?, completed = ?, date_updated = ? WHERE id = ?",
                       (content, category, completed, date_updated, task_id))
        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template("edit.html", task=task)

# ----------------------- Run App -----------------------
if __name__ == "__main__":
    app.run(debug=True)
