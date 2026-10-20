import random, sqlite3
from pathlib import Path
from io import BytesIO
from gtts import gTTS
import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Polyglot Language Lab", page_icon="🌍", layout="wide")
DB=Path(__file__).with_name("language_progress.db")
LANG_TEXT="""Abkhaz|ab;Afrikaans|af;Albanian|sq;Amharic|am;Arabic|ar;Armenian|hy;Assamese|as;Aymara|ay;Azerbaijani|az;Bambara|bm;Basque|eu;Belarusian|be;Bengali|bn;Bosnian|bs;Bulgarian|bg;Burmese|my;Catalan|ca;Cebuano|ceb;Chinese (Simplified)|zh-CN;Chinese (Traditional)|zh-TW;Corsican|co;Croatian|hr;Czech|cs;Danish|da;Dhivehi|dv;Dogri|doi;Dutch|nl;English|en;Esperanto|eo;Estonian|et;Filipino|tl;Finnish|fi;French|fr;Frisian|fy;Galician|gl;Georgian|ka;German|de;Greek|el;Gujarati|gu;Haitian Creole|ht;Hausa|ha;Hawaiian|haw;Hebrew|iw;Hindi|hi;Hmong|hmn;Hungarian|hu;Icelandic|is;Igbo|ig;Indonesian|id;Irish|ga;Italian|it;Japanese|ja;Javanese|jw;Kannada|kn;Kazakh|kk;Khmer|km;Kinyarwanda|rw;Korean|ko;Kurdish (Kurmanji)|ku;Kyrgyz|ky;Lao|lo;Latin|la;Latvian|lv;Lithuanian|lt;Luxembourgish|lb;Macedonian|mk;Maithili|mai;Malagasy|mg;Malay|ms;Malayalam|ml;Maltese|mt;Maori|mi;Marathi|mr;Mongolian|mn;Nepali|ne;Norwegian|no;Odia (Oriya)|or;Oromo|om;Pashto|ps;Persian|fa;Polish|pl;Portuguese|pt;Punjabi|pa;Romanian|ro;Russian|ru;Samoan|sm;Sanskrit|sa;Scots Gaelic|gd;Serbian|sr;Sesotho|st;Shona|sn;Sindhi|sd;Sinhala|si;Slovak|sk;Slovenian|sl;Somali|so;Spanish|es;Sundanese|su;Swahili|sw;Swedish|sv;Tajik|tg;Tamil|ta;Tatar|tt;Telugu|te;Thai|th;Turkish|tr;Turkmen|tk;Ukrainian|uk;Urdu|ur;Uyghur|ug;Uzbek|uz;Vietnamese|vi;Welsh|cy;Xhosa|xh;Yiddish|yi;Yoruba|yo;Zulu|zu;Acehnese|ace;Balinese|ban;Bashkir|ba;Bhojpuri|bho;Chichewa|ny;Ewe|ee;Guarani|gn;Ilocano|ilo;Konkani|gom;Krio|kri;Lingala|ln;Luganda|lg;Meiteilon (Manipuri)|mni-Mtei;Mizo|lus;Quechua|qu;Sepedi|nso;Tigrinya|ti;Tsonga|ts;Twi|ak"""
LANGUAGES=dict(item.split("|",1) for item in LANG_TEXT.split(";"))
PHRASES=[("Vocabulary","Book"),("Vocabulary","Water"),("Vocabulary","Friend"),("Vocabulary","School"),("Vocabulary","Time"),("Vocabulary","Language"),("Grammar","I am learning this language."),("Grammar","Do you speak English?"),("Grammar","I went there yesterday."),("Grammar","I will study tomorrow."),("Grammar","Could you help me, please?"),("Greetings","Hello"),("Greetings","Good morning"),("Greetings","How are you?"),("Greetings","Nice to meet you."),("Everyday","Please"),("Everyday","Thank you"),("Everyday","You're welcome"),("Everyday","I don't understand."),("Everyday","Could you repeat that, please?"),("Everyday","My name is…"),("Travel","Where is the station?"),("Travel","How much does this cost?"),("Travel","Where is the bathroom?"),("Travel","I need help."),("Food","Water, please."),("Food","The food is delicious."),("Food","I am vegetarian."),("Study","What does this word mean?"),("Study","Can you explain this?"),("Study","I am learning this language.")]
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:linear-gradient(140deg,#f7f8ff,#f1fbfa 70%,#f8f6ff)}.block-container{max-width:1200px;padding-top:2rem}
.hero{background:linear-gradient(120deg,#172554,#3730a3 58%,#7c3aed);color:white;border-radius:24px;padding:1.5rem 1.8rem;margin-bottom:1.25rem}.hero h1{font-family:Manrope,sans-serif;color:white;margin:0}.hero p{color:#e0e7ff;margin:.35rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #e4e7f2;border-radius:16px;padding:1rem}.study-card{background:white;border:1px solid #e4e7f2;border-radius:20px;padding:1.5rem;box-shadow:0 10px 30px #202b5010}
div.stButton>button{border-radius:12px;min-height:2.8rem;font-weight:700;border:1px solid #dce1ee}div.stButton>button[kind="primary"]{background:#4f46e5;color:white;border:0}
</style>""",unsafe_allow_html=True)
def db(): return sqlite3.connect(DB)
with db() as c:
 c.execute("CREATE TABLE IF NOT EXISTS translations(lang TEXT, phrase TEXT, translated TEXT, PRIMARY KEY(lang,phrase))")
 c.execute("CREATE TABLE IF NOT EXISTS progress(lang TEXT, phrase TEXT, correct INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0, PRIMARY KEY(lang,phrase))")
def translate(text,target):
 with db() as c: row=c.execute("SELECT translated FROM translations WHERE lang=? AND phrase=?",(target,text)).fetchone()
 if row:return row[0]
 value=GoogleTranslator(source="auto",target=target).translate(text)
 if not value: raise ValueError("No translation returned")
 with db() as c:c.execute("INSERT OR REPLACE INTO translations VALUES(?,?,?)",(target,text,value))
 return value
def record(lang,phrase,ok):
 with db() as c:c.execute("INSERT INTO progress VALUES(?,?,?,1) ON CONFLICT(lang,phrase) DO UPDATE SET correct=correct+excluded.correct,attempts=attempts+1",(lang,phrase,int(ok)))
st.markdown('<div class="hero"><h1>🌍 Polyglot Language Lab</h1><p>Learn practical phrases, translate your own text, and track your quiz progress.</p></div>',unsafe_allow_html=True)
left,right=st.columns([2,1])
with left: lang_name=st.selectbox("Choose a learning language",list(LANGUAGES),index=list(LANGUAGES).index("Spanish"))
with right: st.metric("Languages available",len(LANGUAGES))
target=LANGUAGES[lang_name]
st.caption("Translations are fetched on demand and cached. An internet connection is required for a phrase's first translation; availability can vary by language.")
learn_tab,custom_tab,quiz_tab,progress_tab=st.tabs(["📚 Phrasebook","✍️ Translate text","🧠 Quiz","📈 Progress"])
with learn_tab:
 categories=["All categories"]+sorted({x[0] for x in PHRASES})
 category=st.selectbox("Category",categories)
 rows=[x for x in PHRASES if category=="All categories" or x[0]==category]
 if "phrase_idx" not in st.session_state:st.session_state.phrase_idx=0
 idx=st.session_state.phrase_idx%len(rows); cat,phrase=rows[idx]
 st.markdown(f'<div class="study-card"><small>PHRASE {idx+1} OF {len(rows)} · {cat.upper()}</small><h2 style="color:#252552">{phrase}</h2><p style="color:#6b7280">Read it first, then reveal the translation.</p></div>',unsafe_allow_html=True)
 a,b,c=st.columns([1,1.5,1])
 with a:
  if st.button("← Previous",disabled=len(rows)<2,use_container_width=True):st.session_state.phrase_idx=(idx-1)%len(rows);st.rerun()
 with b:
  if st.button("Translate phrase",type="primary",use_container_width=True):
   with st.spinner("Translating…"):
    try:st.session_state["tr_"+target+"_"+phrase]=translate(phrase,target)
    except Exception:st.error("Translation failed. Check your connection and try again.")
 with c:
  if st.button("Next →",disabled=len(rows)<2,use_container_width=True):st.session_state.phrase_idx=(idx+1)%len(rows);st.rerun()
 tr=st.session_state.get("tr_"+target+"_"+phrase)
 if tr:
  st.success(f"{lang_name}: {tr}")
  if st.button("🔊 Hear pronunciation",key=f"audio_{target}_{phrase}"):
   try:
    audio=BytesIO(); gTTS(text=tr,lang=target).write_to_fp(audio); st.audio(audio.getvalue(),format="audio/mp3")
   except Exception: st.info("Audio pronunciation is not available for this language right now.")
 st.markdown("#### Translate your own phrase")
 custom=st.text_input("Word, phrase, or sentence",placeholder="Type anything you want to learn")
 if st.button("Translate my phrase",type="primary"):
  if not custom.strip():st.warning("Enter some text first.")
  else:
   with st.spinner("Translating…"):
    try:st.session_state.custom_src=custom.strip();st.session_state.custom_tr=translate(custom.strip(),target)
    except Exception:st.error("Translation service is unavailable. Check your internet and try again.")
 if st.session_state.get("custom_tr"):st.markdown(f"**Original:** {st.session_state.custom_src}\n\n**{lang_name}:** {st.session_state.custom_tr}")
with custom_tab:
 st.subheader("Translate any text")
 text_in=st.text_area("Text to translate",height=150,placeholder="Enter a word, phrase, sentence, or short paragraph")
 if st.button("Translate text",type="primary",use_container_width=True):
  if not text_in.strip():st.warning("Enter text first.")
  else:
   with st.spinner(f"Translating to {lang_name}…"):
    try:st.session_state.long_src=text_in.strip();st.session_state.long_tr=translate(text_in.strip(),target)
    except Exception:st.error("Translation failed. Check your internet connection and try again.")
 if st.session_state.get("long_tr"):
  st.text_area(f"Translation · {lang_name}",value=st.session_state.long_tr,height=150)
  st.caption("Machine translation can miss context. Check important wording with a fluent speaker.")
with quiz_tab:
 st.subheader(f"Phrase quiz · {lang_name}")
 if st.session_state.get("quiz_target")!=target or "quiz_options" not in st.session_state:
  st.info("Prepare a quiz when you're ready. Translations load only after you click the button.")
  if st.button("Prepare quiz",type="primary",use_container_width=True):
   q=st.session_state.get("quiz_phrase",random.choice(PHRASES)[1])
   with st.spinner("Preparing translation choices…"):
    try:
     distractors=random.sample([p[1] for p in PHRASES if p[1]!=q],3)
     choices=[translate(x,target) for x in distractors]+[translate(q,target)]
     random.shuffle(choices)
     st.session_state.quiz_phrase=q
     st.session_state.quiz_options=choices
     st.session_state.quiz_answer=translate(q,target)
     st.session_state.quiz_target=target
     st.session_state.quiz_feedback=""
     st.rerun()
    except Exception:
     st.error("Could not load quiz translations. Check your internet connection and retry.")
 else:
  q=st.session_state.quiz_phrase
  st.markdown(f'<div class="study-card"><small>WHAT DOES THIS MEAN?</small><h2 style="color:#252552">{q}</h2></div>',unsafe_allow_html=True)
  choice=st.radio("Choose the correct translation",st.session_state.quiz_options,key=f"quiz_choice_{target}_{q}")
  if st.button("Check answer",type="primary",use_container_width=True):
   ok=choice==st.session_state.quiz_answer
   record(target,q,ok)
   st.session_state.quiz_feedback="Correct! Nice work." if ok else "Not quite. Correct translation: "+st.session_state.quiz_answer
  if st.session_state.get("quiz_feedback"): st.info(st.session_state.quiz_feedback)
  if st.button("Next question",use_container_width=True):
   st.session_state.quiz_phrase=random.choice([p[1] for p in PHRASES if p[1]!=q])
   for k in ["quiz_options","quiz_answer","quiz_target","quiz_feedback"]: st.session_state.pop(k,None)
   st.rerun()
with progress_tab:
 with db() as con:
  totals=con.execute("SELECT COALESCE(SUM(correct),0),COALESCE(SUM(attempts),0) FROM progress WHERE lang=?",(target,)).fetchone()
  rows=con.execute("SELECT phrase,correct,attempts FROM progress WHERE lang=? ORDER BY attempts DESC",(target,)).fetchall()
 correct,attempts=totals
 a,b,c=st.columns(3);a.metric("Questions answered",attempts);b.metric("Correct answers",correct);c.metric("Accuracy",f"{round(correct/attempts*100)}%" if attempts else "—")
 if rows:st.dataframe([{"English phrase":r[0],"Correct":r[1],"Attempts":r[2],"Accuracy":f"{round(r[1]/r[2]*100)}%"} for r in rows],use_container_width=True,hide_index=True)
 else:st.info("Complete quiz questions to start tracking progress.")
st.caption("Translations and learning progress are cached in SQLite. First-time translations need internet; machine translation support varies by language.")
