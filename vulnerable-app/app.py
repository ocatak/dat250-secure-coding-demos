"""DAT250 demo app - INTENTIONALLY VULNERABLE. Never deploy. Binds to localhost only."""
import hashlib
import pickle
import sqlite3
import subprocess

import yaml
from flask import Flask, render_template_string, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-do-not-use"          # hardcoded secret


def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()            # weak hash


def db():
    return sqlite3.connect("users.db")


@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    pw = request.form["password"]
    pw_hash = hash_password(pw)
    query = f"SELECT * FROM users WHERE username = '{user}' AND pw = '{pw_hash}'"
    row = db().execute(query).fetchone()                     # SQL injection
    if not row:
        return "denied", 401
    session["user_id"] = row[0]
    return "welcome"


@app.route("/grades/<int:student_id>")
def grades(student_id):
    if "user_id" not in session:
        return "login required", 401
    rows = db().execute("SELECT course, grade FROM grades WHERE student_id = ?",
                        (student_id,)).fetchall()            # IDOR: whose grades are these?
    return {"student": student_id, "grades": rows}


PROFILE = "<h1>{{ name }}</h1><div class='bio'>{{ bio|safe }}</div>"


@app.route("/bio", methods=["POST"])
def save_bio():
    con = db()
    con.execute("UPDATE users SET bio = ? WHERE id = ?", (request.form["bio"], session["user_id"]))
    con.commit()
    return "saved"


@app.route("/profile/<int:user_id>")
def profile(user_id):
    name, bio = db().execute("SELECT username, bio FROM users WHERE id = ?", (user_id,)).fetchone()
    return render_template_string(PROFILE, name=name, bio=bio)   # |safe: stored XSS


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    out = subprocess.check_output("ping -c 1 " + host, shell=True)   # command injection
    return out


@app.route("/import", methods=["POST"])
def import_settings():
    return str(yaml.load(request.data, Loader=yaml.Loader))  # unsafe YAML


@app.route("/restore", methods=["POST"])
def restore():
    return str(pickle.loads(request.data))                   # insecure deserialization


@app.route("/")
def index():
    # A plain map of the demo endpoints, so GET / doesn't 404. No user input here.
    return (
        "<h1>DAT250 vulnerable app</h1>"
        "<p>Intentionally insecure. Endpoints:</p><ul>"
        "<li>POST /login  (username, password)</li>"
        "<li>GET  /grades/&lt;id&gt;</li>"
        "<li>POST /bio  (bio)</li>"
        "<li>GET  /profile/&lt;id&gt;</li>"
        "<li>GET  /ping?host=127.0.0.1</li>"
        "<li>POST /import   POST /restore</li></ul>"
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)         # debug mode on
