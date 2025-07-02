"""Flask application exposing the language learning utilities via a web UI."""

from pathlib import Path
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

from langdb.ingest import create_table as create_content_table, ingest_transcripts
from langdb.recommend import get_recommendation
from langdb.recommend_known import best_match, load_known_words
from langdb.manage_words import create_table as create_user_table, add_words

CONTENT_DB = Path("data/content.db")
USER_DB = Path("data/user_words.db")

app = Flask(__name__)


def init_dbs() -> None:
    """Create required databases if they do not already exist."""

    CONTENT_DB.parent.mkdir(exist_ok=True)
    USER_DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(CONTENT_DB) as conn_content, sqlite3.connect(
        USER_DB
    ) as conn_user:
        create_content_table(conn_content)
        create_user_table(conn_user)


@app.before_first_request
def setup() -> None:
    init_dbs()


def list_known_words() -> list[str]:
    """Return all stored known words."""

    with sqlite3.connect(USER_DB) as conn:
        rows = conn.execute("SELECT word FROM known_words ORDER BY word").fetchall()
        return [r[0] for r in rows]


@app.route("/")
def index():
    """Render the homepage."""
    words = list_known_words()
    return render_template("index.html", recommendation=None, known_words=words)


@app.route("/recommend", methods=["POST"])
def recommend_route():
    """Recommend content based on the level submitted by the user."""
    level = float(request.form.get("level", 0))
    with sqlite3.connect(CONTENT_DB) as conn:
        rec = get_recommendation(level, conn)
    words = list_known_words()
    return render_template("index.html", recommendation=rec, known_words=words)


@app.route("/recommend_known", methods=["POST"])
def recommend_known_route():
    """Recommend content using the user's known vocabulary."""
    with sqlite3.connect(CONTENT_DB) as conn_content, sqlite3.connect(
        USER_DB
    ) as conn_user:
        known = load_known_words(conn_user)
        if not known:
            rec = None
        else:
            rec = best_match(conn_content, known)
    words = list_known_words()
    if rec:
        title, transcript, score = rec
        rec = {
            "title": title,
            "transcript": transcript,
            "grade_level": None,
            "score": score,
        }
    return render_template("index.html", recommendation=rec, known_words=words)


@app.route("/add_words", methods=["POST"])
def add_words_route():
    """Add words entered on the form to the user's database."""
    text = request.form.get("words", "")
    words = [w.strip() for w in text.split() if w.strip()]
    if words:
        with sqlite3.connect(USER_DB) as conn:
            add_words(conn, words)
    words = list_known_words()
    return render_template("index.html", recommendation=None, known_words=words)


@app.route("/ingest", methods=["POST"])
def ingest_route():
    """Ingest all transcript files into the content database."""
    with sqlite3.connect(CONTENT_DB) as conn:
        ingest_transcripts(conn)
    words = list_known_words()
    return render_template("index.html", recommendation=None, known_words=words)


if __name__ == "__main__":
    app.run(debug=True)
