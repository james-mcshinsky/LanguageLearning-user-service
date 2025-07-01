# Language Learning Content Database

This project stores short video transcripts and provides simple scripts to ingest them into a SQLite database and recommend content for language learners. The recommendation uses a basic L+1 formula: it searches for transcripts with a grade level closest to the user's level plus one.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ingest transcripts from the `transcripts/` folder:
   ```bash
   python scripts/ingest.py
   ```
   This creates `data/content.db` with the transcripts and their readability scores.

## Recommend content

Run `recommend.py` with the user's current level:

```bash
python scripts/recommend.py --level 2
```

The script outputs the transcript whose grade level is nearest to `level + 1`.
