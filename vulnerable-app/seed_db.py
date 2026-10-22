"""Create users.db with two students for the IDOR and XSS demos."""
import sqlite3
import sys

import importlib, os
target = importlib.import_module(os.environ.get("TARGET", "app"))

con = sqlite3.connect("users.db")
con.executescript("DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS grades;"
                  "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, pw TEXT, bio TEXT);"
                  "CREATE TABLE grades (student_id INTEGER, course TEXT, grade TEXT);")
for uid, name, pw in [(1, "alice", "correct horse"), (2, "bob", "battery staple")]:
    con.execute("INSERT INTO users VALUES (?, ?, ?, '')", (uid, name, target.hash_password(pw)))
con.executemany("INSERT INTO grades VALUES (?, ?, ?)",
                [(1, "DAT250", "A"), (1, "DAT110", "B"), (2, "DAT250", "F")])
con.commit()
print("users.db ready: alice / correct horse, bob / battery staple")
