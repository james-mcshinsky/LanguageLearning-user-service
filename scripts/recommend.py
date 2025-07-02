"""Utilities for selecting appropriate content based on a learner's level."""

import argparse
from pathlib import Path
import sqlite3

DB_PATH = Path("data/content.db")


def get_recommendation(level: float, conn: sqlite3.Connection):
    """Return the record nearest to ``level + 1`` in readability."""

    target = level + 1
    cur = conn.execute(
        "SELECT title, transcript, grade_level, ABS(grade_level - ?) as diff FROM content ORDER BY diff ASC LIMIT 1",
        (target,),
    )
    return cur.fetchone()


def main() -> None:
    """CLI entry point for recommending content by level."""

    parser = argparse.ArgumentParser(description="Recommend transcript by level")
    parser.add_argument(
        "--level", type=float, required=True, help="User language level"
    )
    args = parser.parse_args()

    with sqlite3.connect(DB_PATH) as conn:
        rec = get_recommendation(args.level, conn)

    if rec:
        title, transcript, grade_level, _ = rec
        print(f"Recommended content: {title}")
        print(f"Grade level: {grade_level:.2f}")
        print("--- Transcript ---")
        print(transcript)
    else:
        print("No content available")


if __name__ == "__main__":
    main()
