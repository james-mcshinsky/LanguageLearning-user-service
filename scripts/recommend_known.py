"""Recommendation utilities using the learner's known vocabulary."""

import re
import sqlite3
from pathlib import Path

CONTENT_DB = Path("data/content.db")
USER_DB = Path("data/user_words.db")


def load_known_words(conn: sqlite3.Connection) -> set[str]:
    """Return the set of words stored in ``conn``."""

    rows = conn.execute("SELECT word FROM known_words").fetchall()
    return {row[0] for row in rows}


def coverage_score(transcript: str, known_words: set[str]) -> float:
    """Return the proportion of *transcript* contained in *known_words*."""

    words = re.findall(r"\b\w+\b", transcript.lower())
    if not words:
        return 0
    known_count = sum(1 for w in words if w in known_words)
    return known_count / len(words)


def best_match(conn_content: sqlite3.Connection, known_words: set[str]):
    """Return the transcript with the highest known-word coverage."""

    rows = conn_content.execute("SELECT title, transcript FROM content").fetchall()
    best = None
    best_score = -1.0
    for title, transcript in rows:
        score = coverage_score(transcript, known_words)
        if score > best_score:
            best = (title, transcript, score)
            best_score = score
    return best


def main() -> None:
    """CLI entry point for recommending content by known vocabulary."""

    with sqlite3.connect(CONTENT_DB) as conn_content, sqlite3.connect(
        USER_DB
    ) as conn_user:
        known_words = load_known_words(conn_user)
        if not known_words:
            print("No known words stored. Add words using scripts/manage_words.py.")
            return
        match = best_match(conn_content, known_words)

    if match:
        title, transcript, score = match
        print(f"Recommended content: {title}")
        print(f"Known word coverage: {score*100:.1f}%")
        print("--- Transcript ---")
        print(transcript)
    else:
        print("No content available")


if __name__ == "__main__":
    main()
