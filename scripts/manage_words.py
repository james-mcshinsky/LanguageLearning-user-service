import sqlite3
import argparse
from pathlib import Path

USER_DB = Path('data/user_words.db')


def create_table(conn):
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS known_words (
            word TEXT PRIMARY KEY
        )
        '''
    )
    conn.commit()


def add_words(conn, words):
    for w in words:
        conn.execute('INSERT OR IGNORE INTO known_words (word) VALUES (?)', (w.lower(),))
    conn.commit()


def list_words(conn):
    rows = conn.execute('SELECT word FROM known_words ORDER BY word').fetchall()
    for row in rows:
        print(row[0])


def main():
    parser = argparse.ArgumentParser(description='Manage words known by the user')
    subparsers = parser.add_subparsers(dest='command', required=True)

    add_p = subparsers.add_parser('add', help='Add known words')
    add_p.add_argument('words', nargs='+', help='Words to add')

    subparsers.add_parser('list', help='List known words')

    args = parser.parse_args()

    USER_DB.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(USER_DB)
    try:
        create_table(conn)
        if args.command == 'add':
            add_words(conn, args.words)
        elif args.command == 'list':
            list_words(conn)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
