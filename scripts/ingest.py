import sqlite3
from pathlib import Path
import re

DB_PATH = Path('data/content.db')
TRANSCRIPT_DIR = Path('transcripts')


def count_syllables(word: str) -> int:
    word = word.lower()
    vowels = 'aeiouy'
    count = 0
    prev = False
    for char in word:
        if char in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith('e') and count > 1:
        count -= 1
    return count or 1


def flesch_kincaid_grade(text: str) -> float:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', text.lower())
    syllables = sum(count_syllables(w) for w in words)
    num_words = len(words)
    num_sentences = len(sentences) or 1
    return 0.39 * num_words / num_sentences + 11.8 * syllables / num_words - 15.59

def create_table(conn):
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            transcript TEXT,
            grade_level REAL
        )
        '''
    )
    conn.commit()


def ingest_transcripts(conn):
    for txt_file in TRANSCRIPT_DIR.glob('*.txt'):
        text = txt_file.read_text()
        grade = flesch_kincaid_grade(text)
        conn.execute(
            'INSERT INTO content (title, transcript, grade_level) VALUES (?, ?, ?)',
            (txt_file.stem, text, grade)
        )
    conn.commit()


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        create_table(conn)
        ingest_transcripts(conn)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
