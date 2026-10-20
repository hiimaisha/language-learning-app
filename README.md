# Polyglot Language Lab

A multilingual Streamlit learning app with a broad language selector and on-demand machine translation.

## Features
- 100+ language options across major regional and global languages
- Phrasebook categories: greetings, everyday, travel, food, and study
- Translate custom words, phrases, and sentences
- Multiple-choice translation quiz with feedback
- Progress tracking and translation caching in SQLite

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
An internet connection is required for first-time translations. Machine translation availability can vary by language and service availability. Progress and translation cache are stored in local SQLite files.
