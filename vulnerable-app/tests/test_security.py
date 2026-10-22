"""Security regression tests: they FAIL on the vulnerable app and PASS once it is fixed."""
import importlib
import os
import sqlite3

import pytest

# TARGET=solutions.app_fixed runs the same tests against the reference fix
target = importlib.import_module(os.environ.get("TARGET", "app"))


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)                       # users.db is created in a temp dir
    con = sqlite3.connect("users.db")
    con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, pw TEXT, bio TEXT)")
    con.execute("CREATE TABLE grades (student_id INTEGER, course TEXT, grade TEXT)")
    for uid, name, pw in [(1, "alice", "correct horse"), (2, "bob", "battery staple")]:
        con.execute("INSERT INTO users VALUES (?, ?, ?, '')", (uid, name, target.hash_password(pw)))
    con.executemany("INSERT INTO grades VALUES (?, ?, ?)", [(1, "DAT250", "A"), (2, "DAT250", "F")])
    con.commit()
    return target.app.test_client()


def login(client, user, pw):
    return client.post("/login", data={"username": user, "password": pw})


# --- injection ---------------------------------------------------------------
def test_login_works_for_real_user(client):
    assert login(client, "alice", "correct horse").status_code == 200


@pytest.mark.parametrize("payload", ["alice' --", "' OR '1'='1' --"])
def test_sql_injection_is_rejected(client, payload):
    r = client.post("/login", data={"username": payload, "password": "wrong"})
    assert r.status_code == 401


def test_ping_does_not_run_extra_commands(client):
    r = client.get("/ping?host=127.0.0.1;echo INJECTED")
    assert b"INJECTED" not in r.data


# --- broken access control (IDOR) -------------------------------------------
def test_student_sees_own_grades(client):
    login(client, "alice", "correct horse")
    assert client.get("/grades/1").status_code == 200


def test_student_cannot_see_other_students_grades(client):
    login(client, "alice", "correct horse")
    assert client.get("/grades/2").status_code == 403


# --- cross-site scripting ----------------------------------------------------
def test_bio_is_escaped(client):
    login(client, "alice", "correct horse")
    client.post("/bio", data={"bio": "<script>alert(document.cookie)</script>"})
    r = client.get("/profile/1")
    assert b"<script>" not in r.data
    assert b"&lt;script&gt;" in r.data
