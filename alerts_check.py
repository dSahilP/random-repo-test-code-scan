import os
import pickle
import sqlite3
import subprocess
import urllib.request
from flask import Flask, request
from jinja2 import Template
import yaml

app = Flask(__name__)


@app.route("/exec-cmd")
def exec_cmd():
    # Direct command injection (py/command-line-injection)
    cmd = request.args["cmd"]
    os.system(cmd)
    return "ran"


@app.route("/shell-cmd")
def shell_cmd():
    # Direct shell command injection
    arg = request.args["arg"]
    subprocess.Popen(arg, shell=True)
    return "ok"


@app.route("/query-user")
def query_user():
    # Direct SQL injection (py/sql-injection)
    name = request.args["name"]
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = '" + name + "'")
    return str(cur.fetchall())


@app.route("/fetch-url")
def fetch_url():
    # Server-Side Request Forgery (py/ssrf)
    target = request.args["url"]
    with urllib.request.urlopen(target) as resp:
        return resp.read().decode("utf-8", errors="ignore")


@app.route("/read-file")
def read_file():
    # Path injection (py/path-injection)
    path = request.args["path"]
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


@app.route("/render-tpl")
def render_tpl():
    # Template injection / XSS (py/code-injection or py/reflective-xss)
    tpl = request.args["tpl"]
    return Template(tpl).render()


@app.route("/load-pickle", methods=["POST"])
def load_pickle():
    # Unsafe deserialization (py/unsafe-deserialization)
    raw = request.get_data()
    return str(pickle.loads(raw))


@app.route("/load-yaml", methods=["POST"])
def load_yaml():
    # Unsafe YAML deserialization
    data = request.get_data(as_text=True)
    return str(yaml.load(data, Loader=yaml.Loader))
