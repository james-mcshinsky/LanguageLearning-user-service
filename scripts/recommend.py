import sqlite3
import argparse
from pathlib import Path

DB_PATH = Path('data/content.db')

def get_recommendation(level: float, conn):
    target = level + 1
    rows = conn.execute(
        'SELECT title, transcript, grade_level, ABS(grade_level - ?) as diff FROM content ORDER BY diff ASC LIMIT 1',
        (target,)
    ).fetchall()
    return rows[0] if rows else None

def main():
    parser = argparse.ArgumentParser(description='Recommend transcript by level')
    parser.add_argument('--level', type=float, required=True, help='User language level')
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    try:
        rec = get_recommendation(args.level, conn)
    finally:
        conn.close()

    if rec:
        title, transcript, grade_level, _ = rec
        print(f'Recommended content: {title}')
        print(f'Grade level: {grade_level:.2f}')
        print('--- Transcript ---')
        print(transcript)
    else:
        print('No content available')

if __name__ == '__main__':
    main()
