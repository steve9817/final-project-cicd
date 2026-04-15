"""
⚠️  INTENTIONALLY VULNERABLE APPLICATION - FOR SECURITY TESTING ONLY ⚠️
This app is designed to trigger Trivy vulnerability findings.
DO NOT USE IN PRODUCTION.
"""

import os
import sqlite3
import subprocess
import pickle
import yaml
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ── Hardcoded secrets (CWE-798) ────────────────────────────────────────────
SECRET_KEY        = "super_secret_hardcoded_key_12345"
DB_PASSWORD       = "admin123"
AWS_ACCESS_KEY    = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY    = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
JWT_SECRET        = "jwt_secret_do_not_share"

app.config["SECRET_KEY"] = SECRET_KEY


# ── SQL Injection (CWE-89) ─────────────────────────────────────────────────
@app.route("/user")
def get_user():
    username = request.args.get("username", "")
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'password123')")
    conn.commit()

    # ❌ Raw string interpolation → SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


# ── Command Injection (CWE-78) ─────────────────────────────────────────────
@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    # ❌ shell=True with user input → RCE
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return jsonify({"output": result.stdout, "error": result.stderr})


# ── Insecure Deserialization (CWE-502) ─────────────────────────────────────
@app.route("/load", methods=["POST"])
def load_object():
    data = request.get_data()
    # ❌ pickle.loads on untrusted data → RCE
    obj = pickle.loads(data)
    return jsonify({"result": str(obj)})


# ── YAML Arbitrary Code Execution (CWE-502) ────────────────────────────────
@app.route("/parse-yaml", methods=["POST"])
def parse_yaml():
    raw = request.get_data(as_text=True)
    # ❌ yaml.load without Loader → arbitrary Python execution
    parsed = yaml.load(raw)
    return jsonify(parsed)


# ── Path Traversal (CWE-22) ────────────────────────────────────────────────
@app.route("/read-file")
def read_file():
    filename = request.args.get("file", "readme.txt")
    # ❌ No sanitisation → directory traversal (../../etc/passwd)
    with open(f"/app/data/{filename}", "r") as f:
        content = f.read()
    return content


# ── XSS via render_template_string (CWE-79) ───────────────────────────────
@app.route("/greet")
def greet():
    name = request.args.get("name", "World")
    # ❌ User input interpolated directly into template → SSTI / XSS
    template = f"<h1>Hello, {name}!</h1>"
    return render_template_string(template)


# ── Sensitive data in response (CWE-200) ──────────────────────────────────
@app.route("/debug")
def debug():
    # ❌ Exposes environment variables and internal secrets
    return jsonify({
        "env":        dict(os.environ),
        "db_pass":    DB_PASSWORD,
        "aws_key":    AWS_ACCESS_KEY,
        "jwt_secret": JWT_SECRET,
    })


# ── Running as root with debug mode ───────────────────────────────────────
if __name__ == "__main__":
    # ❌ debug=True exposes interactive debugger
    app.run(host="0.0.0.0", port=5000, debug=True)
