import os
import time
import psycopg2
from flask import Flask, request, redirect, render_template_string, jsonify

app = Flask(__name__)

DB = dict(
    host=os.getenv("DB_HOST", "db"),
    dbname=os.getenv("DB_NAME", "notesdb"),
    user=os.getenv("DB_USER", "notes"),
    password=os.getenv("DB_PASSWORD", "notes_pass"),
)

PAGE = """
<!doctype html>
<title>Notes App</title>
<style>
  body{font-family:Arial,sans-serif;max-width:640px;margin:40px auto;padding:0 16px}
  input[type=text]{width:70%;padding:8px} button{padding:8px 14px}
  li{margin:6px 0}
</style>
<h1>Notes App</h1>
<p>Student: <b>Sakina Abbas</b> | FA23-BDS-055 | Environment: <b>{{ env }}</b></p>
<form method="post" action="/add">
  <input type="text" name="content" placeholder="Write a note" required>
  <button type="submit">Add</button>
</form>
<h3>Saved notes ({{ notes|length }})</h3>
<ul>{% for n in notes %}<li>{{ n[1] }} <small>({{ n[2] }})</small></li>{% endfor %}</ul>
"""


def get_conn(retries=30):
    for _ in range(retries):
        try:
            return psycopg2.connect(**DB)
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("database not reachable")


def init_db():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id SERIAL PRIMARY KEY, content TEXT NOT NULL, "
            "created_at TIMESTAMP DEFAULT NOW())"
        )
    conn.close()


@app.route("/")
def index():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, content, to_char(created_at,'YYYY-MM-DD HH24:MI') "
                    "FROM notes ORDER BY id DESC")
        notes = cur.fetchall()
    conn.close()
    return render_template_string(PAGE, notes=notes, env=os.getenv("APP_ENV", "Part I"))


@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content", "").strip()
    if content:
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        conn.close()
    return redirect("/")


@app.route("/health")
def health():
    conn = get_conn(retries=3)
    with conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM notes")
        count = cur.fetchone()[0]
    conn.close()
    return jsonify({"status": "ok", "database": "connected", "notes": count})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # trigger test
