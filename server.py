import os
import random
import sqlite3
import secrets
import string
from datetime import datetime, timedelta

from flask import Flask, request, render_template, g, redirect, url_for, abort

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stash.db")
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB)

EXPIRY_DAYS = 7
MAX_CONTENT_BYTES = 1_000_000  # 1MB cap; raise if needed
CLEANUP_PROBABILITY = 0.05  # run cleanup on ~1 in 20 requests

app = Flask(__name__)

def get_db():
    if "db" not in g:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir:
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError:
                pass

        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    with open("schema.sql") as f:
        db.executescript(f.read())
    db.commit()

def cleanup_expired():
    cutoff = datetime.utcnow() - timedelta(days=EXPIRY_DAYS)
    db = get_db()
    db.execute("DELETE FROM stash WHERE created_at < ?", (cutoff,))
    db.commit()

def maybe_cleanup():
    # Probabilistic cleanup: avoids a DELETE query on every request.
    # At 5% probability, expired rows are cleared roughly every 20 requests.
    if random.random() < CLEANUP_PROBABILITY:
        cleanup_expired()

def gen_id(length=8):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

@app.route("/")
def index():
    maybe_cleanup()
    return render_template("index.html")

@app.route("/stash", methods=["POST"])
def create_stash():
    content = request.form.get("content", "").strip()
    if not content:
        return redirect(url_for("index"))

    # Enforce content size cap to prevent DB bloat
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        abort(413)

    stash_id = gen_id()
    db = get_db()
    db.execute(
        "INSERT INTO stash (id, content, created_at) VALUES (?, ?, ?)",
        (stash_id, content, datetime.utcnow()),
    )
    db.commit()

    return redirect(url_for("view_stash", stash_id=stash_id))

@app.route("/s/<stash_id>")
def view_stash(stash_id):
    maybe_cleanup()
    db = get_db()
    row = db.execute(
        "SELECT content, created_at FROM stash WHERE id = ?",
        (stash_id,),
    ).fetchone()

    if not row:
        abort(404)

    return render_template(
        "view.html",
        content=row["content"],
        stash_id=stash_id,
    )

@app.route("/r/<stash_id>")
def raw_stash(stash_id):
    maybe_cleanup()
    db = get_db()
    row = db.execute(
        "SELECT content FROM stash WHERE id = ?",
        (stash_id,),
    ).fetchone()

    if not row:
        abort(404)

    return row["content"], 200, {"Content-Type": "text/plain; charset=utf-8"}

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
