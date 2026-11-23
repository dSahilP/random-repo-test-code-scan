import hashlib
import os
import pickle
import sqlite3
import subprocess
import tempfile
import yaml
from flask import Flask, make_response, render_template_string, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "hardcoded-dev-secret-key-12345"  # Hardcoded secret / weak key pattern


@app.route("/cmd1")
def cmd_os_system():
    target = request.args.get("target", "127.0.0.1")
    os.system(f"ping -c 1 {target}")  # Command injection (CWE-78)
    return "ok"


@app.route("/cmd2")
def cmd_subprocess_shell():
    arg = request.args.get("arg", "")
    subprocess.Popen(f"echo {arg}", shell=True)  # Shell command injection (CWE-78)
    return "ok"


@app.route("/cmd3")
def cmd_popen():
    raw = request.args.get("cmd", "whoami")
    return os.popen(raw).read()  # Command injection via os.popen (CWE-78)


@app.route("/sql1")
def sql_concat():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = " + user_id)  # SQL injection (CWE-89)
    return str(cur.fetchall())


@app.route("/sql2")
def sql_fstring():
    role = request.args.get("role", "user")
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    cur.execute(f"SELECT username FROM users WHERE role = '{role}'")  # SQL injection (CWE-89)
    return str(cur.fetchall())


@app.route("/sql3")
def sql_percent():
    email = request.args.get("email", "")
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = '%s'" % email)  # SQL injection (CWE-89)
    return str(cur.fetchall())


@app.route("/file1")
def path_read():
    filename = request.args.get("file", "readme.txt")
    with open(os.path.join("/tmp/uploads", filename), "r", encoding="utf-8") as f:  # Path injection (CWE-22)
        return f.read()


@app.route("/file2")
def path_write():
    path = request.args.get("path", "/tmp/out.txt")
    with open(path, "w", encoding="utf-8") as f:  # Uncontrolled path write (CWE-22)
        f.write(request.args.get("content", ""))
    return "written"


@app.route("/deserialize1")
def unsafe_pickle():
    payload = request.args.get("data", "")
    obj = pickle.loads(bytes.fromhex(payload))  # Unsafe deserialization (CWE-502)
    return str(obj)


@app.route("/deserialize2")
def unsafe_yaml():
    doc = request.args.get("yaml", "a: 1")
    loaded = yaml.unsafe_load(doc)  # Unsafe YAML load (CWE-502)
    return str(loaded)


@app.route("/xss")
def reflected_ssti_xss():
    name = request.args.get("name", "guest")
    return render_template_string(f"<h1>Hello {name}</h1>")  # Template / XSS issue (CWE-79 / CWE-1336)


@app.route("/cookie")
def set_bad_cookie():
    val = request.args.get("val", "test")
    resp = make_response("cookie set")
    resp.set_cookie("session_tag", val)  # Cookie injection / insecure cookie flags
    return resp


def weak_crypto_and_temp(password: str):
    md5_digest = hashlib.md5(password.encode()).hexdigest()  # Weak hash (CWE-327)
    sha1_digest = hashlib.sha1(password.encode()).hexdigest()  # Weak hash (CWE-327)
    tmp_path = tempfile.mktemp()  # Insecure temporary file (CWE-377)
    print("Debug password:", password)  # Clear-text logging of sensitive info (CWE-532)
    return md5_digest, sha1_digest, tmp_path


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Debug mode / all interfaces
