# Representative of what assistants often return for prompt.txt (kept verbatim-style for the demo).
import os
import sqlite3

import jwt
from flask import Flask, request, send_file

app = Flask(__name__)
SECRET = "supersecretkey123"            # "replace in production"
UPLOADS = "uploads"


@app.route("/download")
def download():
    name = request.args.get("name")
    return send_file(os.path.join(UPLOADS, name))          # path traversal: ../../etc/passwd


@app.route("/order")
def order():
    token = request.headers.get("Authorization", "")
    jwt.decode(token, SECRET, algorithms=["HS256"], options={"verify_signature": False})
    oid = request.args.get("id")
    conn = sqlite3.connect("shop.db")
    row = conn.execute(f"SELECT * FROM orders WHERE id = {oid}").fetchone()
    return {"order": row}


if __name__ == "__main__":
    app.run(debug=True)
