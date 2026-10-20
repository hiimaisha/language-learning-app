import random
import sqlite3
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Language Learning Buddy", page_icon="🌍", layout="wide")
DB_PATH = Path(__file__).with_name("language_progress.db")
WORDS = [
    {"category":"Greetings","word":"Hello","translation":"Hola","pronunciation":"OH-lah","example":"Hola, ¿cómo estás? — Hello, how are you?","language":"Spanish"},
    {"category":"Greetings","word":"Good morning","translation":"Buenos días","pronunciation":"BWEH-nos DEE-as","example":"Buenos días, profesora. — Good morning, teacher.","language":"Spanish"},
    {"category":"Greetings","word":"Thank you","translation":"Gracias","pronunciation":"GRAH-syahs","example":"Muchas gracias. — Thank you very much.","language":"Spanish"},
    {"category":"Travel","word":"Where is the station?","translation":"¿Dónde está la estación?","pronunciation":"DON-deh es-TAH lah es-tah-SYON","example":"Ask this when looking for a station.","language":"Spanish"},
    {"category":"Travel","word":"How much does it cost?","translation":"¿Cuánto cuesta?","pronunciation":"KWAN-toh KWES-tah","example":"Use this while shopping.","language":"Spanish"},
    {"category":"Food","word":"Water","translation":"Agua","pronunciation":"AH-gwah","example":"Quiero agua, por favor. — Water, please.","language":"Spanish"},
    {"category":"Food","word":"Delicious","translation":"Delicioso / deliciosa","pronunciation":"deh-lee-SYOH-soh / sah","example":"¡Está delicioso! — It is delicious!","language":"Spanish"},
    {"category":"Everyday","word":"Please","translation":"Por favor","pronunciation":"por fah-VOR","example":"A polite way to make a request.","language":"Spanish"},
    {"category":"Everyday","word":"Yes / No","translation":"Sí / No","pronunciation":"see / noh","example":"Simple answers: yes and no.","language":"Spanish"},
    {"category":"Everyday","word":"I don't understand","translation":"No entiendo","pronunciation":"noh en-TYEN-doh","example":"Use this when you need someone to repeat.","language":"Spanish"},
]
def db():
    return sqlite3.connect(DB_PATH)
def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS progress (
            item TEXT PRIMARY KEY,
            correct INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0
        )""")
init_db()
def get_progress(item):
    with db() as con:
        row = con.execute("SELECT correct, attempts FROM progress WHERE item=?", (item,)).fetchone()
    return row or (0, 0)
def record(item, correct):
    with db() as con:
        con.execute("""INSERT INTO progress(item, correct, attempts) VALUES (?, ?, 1)
            ON CONFLICT(item) DO UPDATE SET correct=correct+excluded.correct, attempts=attempts+1""",
            (item, int(correct)))
st.title("🌍 Language Learning Buddy")
st.caption("Learn practical Spanish vocabulary and phrases, then quiz yourself.")
language = st.selectbox("Learning language", ["Spanish"], help="The starter vocabulary currently contains Spanish phrases.")
categories = ["All"] + sorted({w["category"] for w in WORDS})
category = st.selectbox("Choose a category", categories)
filtered = [w for w in WORDS if category == "All" or w["category"] == category]
tab_learn, tab_quiz, tab_progress = st.tabs(["📚 Learn", "🧠 Quiz", "📈 My progress"])

with tab_learn:
    st.write(f"**{len(filtered)} words and phrases**")
    for i, item in enumerate(filtered):
        with st.expander(f"{item['word']}  ·  {item['category']}", expanded=(i == 0)):
            st.markdown(f"**Translation:** {item['translation']}")
            st.markdown(f"**Pronunciation guide:** {item['pronunciation']}")
            st.write(item["example"])
            correct, attempts = get_progress(item["word"])
            st.caption(f"Quiz accuracy: {correct}/{attempts} correct")
with tab_quiz:
    if "quiz_item" not in st.session_state or st.session_state.get("quiz_category") != category:
        st.session_state.quiz_item = random.choice(filtered)
        st.session_state.quiz_category = category
        st.session_state.quiz_feedback = ""
    item = st.session_state.quiz_item
    st.progress(0.5, text="Quick practice")
    st.subheader(f"What does “{item['word']}” mean in Spanish?")
    options = list({item["translation"]} | {w["translation"] for w in WORDS if w["translation"] != item["translation"]})
    random.shuffle(options)
    # Keep options stable while the user answers.
    if st.session_state.get("options_item") != item["word"]:
        st.session_state.quiz_options = random.sample(options, min(4, len(options)))
        st.session_state.options_item = item["word"]
    choice = st.radio("Choose the correct translation", st.session_state.quiz_options, key=f"answer_{item['word']}")
    if st.button("Check answer", type="primary"):
        is_correct = choice == item["translation"]
        record(item["word"], is_correct)
        st.session_state.quiz_feedback = "✅ Correct! Great job." if is_correct else f"Not quite. The answer is **{item['translation']}**."
    if st.session_state.get("quiz_feedback"):
        st.info(st.session_state.quiz_feedback)
    if st.button("Next question"):
        st.session_state.quiz_item = random.choice(filtered)
        st.session_state.quiz_feedback = ""
        st.rerun()
with tab_progress:
    with db() as con:
        rows = con.execute("SELECT item, correct, attempts FROM progress ORDER BY attempts DESC, item").fetchall()
    if not rows:
        st.info("Your progress will appear here after you answer a quiz question.")
    else:
        attempts = sum(r[2] for r in rows)
        correct = sum(r[1] for r in rows)
        c1, c2, c3 = st.columns(3)
        c1.metric("Questions answered", attempts)
        c2.metric("Correct answers", correct)
        c3.metric("Overall accuracy", f"{round(correct/attempts*100)}%" if attempts else "0%")
        st.dataframe([{"Word / phrase":r[0],"Correct":r[1],"Attempts":r[2],"Accuracy":f"{round(r[1]/r[2]*100)}%" if r[2] else "—"} for r in rows],
                     use_container_width=True, hide_index=True)
st.divider()
st.caption("Progress is saved in a local SQLite database. Pronunciation spellings are approximate guides, not formal phonetic notation.")
