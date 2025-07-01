import sqlite3
import re
from pathlib import Path

CONTENT_DB = Path('data/content.db')
USER_DB = Path('data/user_words.db')


def load_known_words(conn):
    rows = conn.execute('SELECT word FROM known_words').fetchall()
    return {row[0] for row in rows}


def coverage_score(transcript, known_words):
    words = re.findall(r'\b\w+\b', transcript.lower())
    if not words:
        return 0
    known_count = sum(1 for w in words if w in known_words)
    return known_count / len(words)


def best_match(conn_content, known_words):
    rows = conn_content.execute('SELECT title, transcript FROM content').fetchall()
    best = None
    best_score = -1
    for title, transcript in rows:
        score = coverage_score(transcript, known_words)
        if score > best_score:
            best = (title, transcript, score)
            best_score = score
    return best


def main():
    conn_content = sqlite3.connect(CONTENT_DB)
    conn_user = sqlite3.connect(USER_DB)
    try:
        known_words = load_known_words(conn_user)
        if not known_words:
            print('No known words stored. Add words using scripts/manage_words.py.')
            return
        match = best_match(conn_content, known_words)
    finally:
        conn_content.close()
        conn_user.close()

    if match:
        title, transcript, score = match
        print(f'Recommended content: {title}')
        print(f'Known word coverage: {score*100:.1f}%')
        print('--- Transcript ---')
        print(transcript)
    else:
        print('No content available')


if __name__ == '__main__':
    main()
