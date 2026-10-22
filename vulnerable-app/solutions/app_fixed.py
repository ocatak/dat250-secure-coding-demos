"""Reference fix for login, grades, profile and ping (other endpoints: exercise)."""
import ipaddress
import os
import sqlite3
import subprocess

from argon2 import PasswordHasher          # pip install argon2-cffi
from flask import Flask, abort, render_template_string, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]   # from the environment, not the code
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
ph = PasswordHasher()


def hash_password(pw):
    return ph.hash(pw)                                  # Argon2id, salted


def db():
    return sqlite3.connect("users.db")


@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'"   # blocks inline scripts
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.route("/login", methods=["POST"])
def login():
    row = db().execute("SELECT id, pw FROM users WHERE username = ?",   # parameterized
                       (request.form["username"],)).fetchone()
    try:
        ok = row is not None and ph.verify(row[1], request.form["password"])
    except Exception:
        ok = False
    if not ok:
        return "denied", 401
    session.clear()                                     # new session on login (no fixation)
    session["user_id"] = row[0]
    return "welcome"


@app.route("/grades/<int:student_id>")
def grades(student_id):
    if "user_id" not in session:
        abort(401)
    if session["user_id"] != student_id:                # ownership check: fixes the IDOR
        abort(403)
    rows = db().execute("SELECT course, grade FROM grades WHERE student_id = ?",
                        (student_id,)).fetchall()
    return {"student": student_id, "grades": rows}


PROFILE = "<h1>{{ name }}</h1><div class='bio'>{{ bio }}</div>"   # autoescaped


@app.route("/bio", methods=["POST"])
def save_bio():
    if "user_id" not in session:
        abort(401)
    con = db()
    con.execute("UPDATE users SET bio = ? WHERE id = ?", (request.form["bio"], session["user_id"]))
    con.commit()
    return "saved"


@app.route("/profile/<int:user_id>")
def profile(user_id):
    row = db().execute("SELECT username, bio FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        abort(404)
    return render_template_string(PROFILE, name=row[0], bio=row[1])


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


@app.route("/ping")
def ping():
    try:
        host = str(ipaddress.ip_address(request.args.get("host", "")))  # validate: IPs only
    except ValueError:
        abort(400)
    out = subprocess.run(["ping", "-c", "1", host],                     # no shell, arg list
                         capture_output=True, timeout=5)
    return out.stdout
