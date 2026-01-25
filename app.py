import streamlit as st
import streamlit_authenticator as stauth
import json
import time
import yaml
import random
from yaml.loader import SafeLoader
from agents import generate_roadmap 
from groq import Groq

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- AI GENERATORS ---
def generate_ai_question(category):
    sub_topics = {
        "Math": ["Linear Algebra", "Calculus", "Statistics"],
        "Science": ["Astrophysics", "Chemistry", "Biology"],
        "Tech": ["Cybersecurity", "AI", "Cloud Computing"]
    }
    selected_sub = random.choice(sub_topics.get(category, ["General"]))
    seed = random.randint(1, 10000)
    prompt = f"Generate ONE unique multiple-choice question for {category} ({selected_sub}). Return ONLY JSON: {{'question': '...', 'options': ['...'], 'answer': '...', 'xp': 15}}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9 
    )
    return json.loads(response.choices[0].message.content)

def generate_word_scramble():
    """Generates a STEM word and a clue for the scramble game."""
    prompt = "Pick a common STEM word (7-10 letters). Return JSON: {'word': 'BIOLOGY', 'clue': 'The study of living organisms', 'xp': 20}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    word = data['word'].upper()
    scrambled = "".join(random.sample(word, len(word)))
    return {"scrambled": scrambled, "original": word, "clue": data['clue'], "xp": data['xp']}

# --- LOGIN ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days'])
authenticator.login(location='main')

if st.session_state.get('authentication_status'):
    # Initialization
    if 'xp' not in st.session_state: st.session_state.xp = 0
    if 'skill_vector' not in st.session_state: st.session_state.skill_vector = [0.0, 0.0, 0.0]
    
    # Rank Logic
    def get_rank_info(xp):
        if xp < 50: return "🌱 Novice", "#808080"
        if xp < 150: return "⚔️ Apprentice", "#4CAF50"
        if xp < 300: return "🎓 Scholar", "#2196F3"
        return "🏆 Grandmaster", "#FFD700"

    rank_name, rank_col = get_rank_info(st.session_state.xp)

    # Styling
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #f8f9fa; }}
        .stat-card {{
            background-color: {rank_col};
            padding: 20px; border-radius: 15px; color: white;
            text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .game-box {{
            background: white; padding: 25px; border-radius: 15px;
            border-left: 5px solid {rank_col}; margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown(f'<div class="stat-card"><h3>{rank_name}</h3></div>', unsafe_allow_html=True)
        st.metric("Your Total XP", st.session_state.xp)
        st.divider()
        mode = st.radio("Quest Map", ["Quiz Arena", "Word Scramble", "AI Roadmap"])
        authenticator.logout('Logout', 'sidebar')

    # --- MODE 1: QUIZ ARENA ---
    if mode == "Quiz Arena":
        st.header("🎯 Quiz Arena")
        cat = st.selectbox("Choose Subject", ["Math", "Science", "Tech"])
        
        if st.button("Generate New Challenge") or 'current_ai_q' not in st.session_state:
            st.session_state.current_ai_q = generate_ai_question(cat)
            st.session_state.answered = False

        q = st.session_state.current_ai_q
        with st.container():
            st.markdown('<div class="game-box">', unsafe_allow_html=True)
            st.write(f"### {q['question']}")
            ans = st.radio("Options:", q['options'], key=f"q_{hash(q['question'])}")
            if st.button("Submit Answer") and not st.session_state.answered:
                if ans == q['answer']:
                    st.balloons()
                    st.session_state.xp += q['xp']
                    st.success(f"Correct! +{q['xp']} XP")
                else:
                    st.error(f"Wrong! Answer was {q['answer']}")
                st.session_state.answered = True
            st.markdown('</div>', unsafe_allow_html=True)

    # --- MODE 2: WORD SCRAMBLE ---
    elif mode == "Word Scramble":
        st.header("🧩 STEM Word Scramble")
        if st.button("New Scramble") or 'scramble' not in st.session_state:
            st.session_state.scramble = generate_word_scramble()
            st.session_state.s_ans = False

        s = st.session_state.scramble
        st.markdown(f'<div class="game-box"><h3>Scrambled: <span style="color:blue;">{s["scrambled"]}</span></h3>', unsafe_allow_html=True)
        st.write(f"**Clue:** {s['clue']}")
        guess = st.text_input("Unscramble the word:").upper()
        if st.button("Check Word") and not st.session_state.s_ans:
            if guess == s['original']:
                st.snow()
                st.session_state.xp += s['xp']
                st.success(f"Brilliant! {s['original']} is correct! +{s['xp']} XP")
            else:
                st.error("Not quite! Try again.")
            st.session_state.s_ans = True
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MODE 3: AI ROADMAP ---
    else:
        st.header("📍 Master Roadmap")
        if st.session_state.xp < 50:
            st.warning("⚠️ Reach **50 XP** (Apprentice Rank) to unlock the AI Career Roadmap!")
        else:
            if st.button("Generate My Path"):
                with st.spinner("Analyzing your performance..."):
                    m, s, t = st.session_state.skill_vector
                    roadmap = generate_roadmap({"math": m, "science": s, "tech": t})
                    st.markdown(roadmap)

elif st.session_state.get('authentication_status') == False:
    st.error('Username/password is incorrect')