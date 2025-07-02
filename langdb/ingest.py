"""Utilities for ingesting transcript files into the content database."""

from pathlib import Path
import re
import sqlite3

DB_PATH = Path("data/content.db")
TRANSCRIPT_DIR = Path("transcripts")


def count_syllables(word: str) -> int:
    """Naive syllable counter used for Flesch–Kincaid calculations."""

    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev = False
    for char in word:
        if char in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith("e") and count > 1:
        count -= 1
    return count or 1


def flesch_kincaid_grade(text: str) -> float:
    """Return the approximate grade level for *text* using Flesch–Kincaid."""

    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"\b\w+\b", text.lower())
    syllables = sum(count_syllables(w) for w in words)
    num_words = len(words)
    num_sentences = len(sentences) or 1
    return 0.39 * num_words / num_sentences + 11.8 * syllables / num_words - 15.59


def create_table(conn: sqlite3.Connection) -> None:
    """Create the ``content`` table if it does not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            transcript TEXT,
            grade_level REAL
        )
        """
    )
    conn.commit()


def ingest_transcripts(conn: sqlite3.Connection) -> None:
    """Insert all ``.txt`` files in :data:`TRANSCRIPT_DIR` into ``conn``."""
    for txt_file in TRANSCRIPT_DIR.glob("*.txt"):
        text = txt_file.read_text()
        grade = flesch_kincaid_grade(text)
        conn.execute(
            "INSERT INTO content (title, transcript, grade_level) VALUES (?, ?, ?)",
            (txt_file.stem, text, grade),
        )
    conn.commit()


def main() -> None:
    """Populate the content database from transcript files."""

    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        create_table(conn)
        ingest_transcripts(conn)


if __name__ == "__main__":
    main()
