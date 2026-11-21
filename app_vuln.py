import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route("/run")
def run_cmd():
    # Triggers CodeQL command-injection query: unsanitized input passed to shell
    cmd = request.args.get("cmd", "ls")
    return os.popen(cmd).read()

@app.route("/search")
def search_user():
    # Triggers CodeQL SQL-injection query: string concatenation in SQL query
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE name = '" + name + "'")
    rows = cur.fetchall()
    conn.close()
    return str(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
