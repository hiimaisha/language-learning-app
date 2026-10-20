# Language Learning Buddy

A beginner-friendly Streamlit app for learning practical Spanish words and phrases.

## Features
- Vocabulary grouped by greetings, travel, food, and everyday phrases
- English-to-Spanish translations, examples, and pronunciation guides
- Multiple-choice quiz with immediate feedback
- Quiz progress and accuracy saved in SQLite
- No API key required; works offline after dependencies are installed

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app creates `language_progress.db` beside `app.py` automatically. The pronunciation text is an approximate learner aid.
