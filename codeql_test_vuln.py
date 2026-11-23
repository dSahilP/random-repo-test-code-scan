import os
import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)


@app.route("/user")
def get_user():
    # CWE-89: SQL Injection — untrusted query parameter concatenated into SQL
    username = request.args.get("username", "")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT id, username FROM users WHERE username = '{username}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return {"rows": rows}


@app.route("/ping")
def ping_host():
    # CWE-78: OS Command Injection — untrusted input passed to shell command
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)
    return {"output": output}


@app.route("/file")
def read_file():
    # CWE-22: Path Traversal — untrusted filename joined directly with base directory
    filename = request.args.get("name", "readme.txt")
    filepath = os.path.join("/var/data/reports", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
