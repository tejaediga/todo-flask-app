from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date
import os
from init_db import init_db

# Create the DB if it doesn't exist (for fresh deployment)
if not os.path.exists("todo.db"):
    init_db()

app = Flask(__name__)

# Home Page Route
@app.route("/")
def home():
    category_filter = request.args.get("category", "All")
    status_filter = request.args.get("filter", "all")

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # Reset completed tasks if date is older than today
    today = date.today().isoformat()
    cursor.execute("UPDATE tasks SET completed = 0 WHERE date_updated < ?", (today,))
    conn.commit()

    # Build filter conditions
    query = "SELECT id, content, completed, category FROM tasks"
    conditions = []
    params = []

    if category_filter != "All":
        conditions.append("category = ?")
        params.append(category_filter)

    if status_filter == "pending":
        conditions.append("completed = 0")
    elif status_filter == "completed":
        conditions.append("completed = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return render_template(
    "index.html",
    tasks=tasks,
    selected_category=category_filter,
    selected_filter=status_filter,
    today=date.today().strftime('%A, %d %B %Y')  #This passes the date
)



# Add a Task
@app.route("/add", methods=["POST"])
def add():
    task_content = request.form.get("task")
    category = request.form.get("category")
    today = date.today().isoformat()

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (content, category, completed, date_updated) VALUES (?, ?, ?, ?)",
        (task_content, category, 0, today)
    )
    conn.commit()
    conn.close()
    return redirect("/")


# Mark Complete / Undo Complete
@app.route("/complete/<int:task_id>")
def mark_complete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    current = cursor.fetchone()
    if current:
        new_status = 0 if current[0] == 1 else 1
        cursor.execute("UPDATE tasks SET completed = ?, date_updated = ? WHERE id = ?", (new_status, today, task_id))

    conn.commit()
    conn.close()
    return redirect("/")


# Delete a Task
@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


# Edit a Task
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    if request.method == "POST":
        new_content = request.form.get("task")
        new_category = request.form.get("category")
        today = date.today().isoformat()
        cursor.execute(
            "UPDATE tasks SET content = ?, category = ?, date_updated = ? WHERE id = ?",
            (new_content, new_category, today, task_id)
        )
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        cursor.execute("SELECT id, content, category FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()
        return render_template("edit.html", task=task)

#  Run the app
if __name__ == "__main__":
    app.run(debug=True)
