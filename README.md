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

## Recommend by level

Run `recommend.py` with the user's current level:

```bash
python scripts/recommend.py --level 2
```

The script outputs the transcript whose grade level is nearest to `level + 1`.

## Track known words

Use `manage_words.py` to store the words a learner already knows. This creates
`data/user_words.db` if it does not exist.

Add words:

```bash
python scripts/manage_words.py add hello world
```

List stored words:

```bash
python scripts/manage_words.py list
```

## Recommend by known words

Run `recommend_known.py` to select the transcript that contains the highest
proportion of words already stored in `user_words.db`:

```bash
python scripts/recommend_known.py
```

## Web interface

A simple Flask app exposes the scripts through a browser. Start it with:

```bash
python webapp/app.py
```

The homepage lets you ingest transcripts, add known words, and get video recommendations using either your level or stored words.

## Hosting on GitHub Pages

To make the static site in `docs/` available online:
1. Push this repository to GitHub.
2. Open the repository **Settings** on GitHub and choose **Pages** from the side bar.
3. Under **Source** select **Deploy from a branch**, then pick the `main` branch and the `/docs` folder.
4. Save the changes. After a minute GitHub will publish the site at `https://<your-username>.github.io/<repository>`.
