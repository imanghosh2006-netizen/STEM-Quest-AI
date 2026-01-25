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

# --- AI & GAME GENERATORS ---
def generate_word_scramble():
    try:
        prompt = "Pick a common STEM word (7-10 letters). Return JSON: {'word': 'ALGORITHM', 'clue': 'A set of steps to solve a problem', 'xp': 20}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        word = data['word'].upper()
        scrambled = "".join(random.sample(word, len(word)))
        return {"scrambled": scrambled, "original": word, "clue": data['clue'], "xp": 20}
    except:
        return {"scrambled": "NURON", "original": "NEURON", "clue": "A specialized cell transmitting nerve impulses", "xp": 20}

def get_logic_gate():
    gate = random.choice(["AND", "OR", "XOR", "NAND"])
    a, b = random.randint(0, 1), random.randint(0, 1)
    if gate == "AND": ans = a & b
    elif gate == "OR": ans = a | b
    elif gate == "XOR": ans = a ^ b
    else: ans = 1 if not (a & b) else 0 
    return {"gate": gate, "a": a, "b": b, "ans": ans}

def get_math_duel():
    num1 = random.randint(10, 50)
    num2 = random.randint(10, 50)
    ops = ["+", "-", "*"]
    op = random.choice(ops)
    if op == "+": ans = num1 + num2
    elif op == "-": ans = num1 - num2
    else: ans = num1 * random.randint(2, 9)
    return {"q": f"{num1} {op} {num2 if op != '*' else ans//num1}", "ans": ans}

def get_tech_binary():
    num = random.randint(1, 15)
    binary = bin(num)[2:].zfill(4)
    return {"binary": binary, "decimal": num}

def get_chem_challenge():
    challenges = [
        {"q": "H₂ + O₂ → ?", "options": ["H₂O", "2H₂O", "HO₂"], "ans": "2H₂O", "note": "Balanced: 2H₂ + O₂ → 2H₂O"},
        {"q": "N₂ + H₂ → ?", "options": ["NH₃", "2NH₃", "N₂H"], "ans": "2NH₃", "note": "Balanced: N₂ + 3H₂ → 2NH₃"},
        {"q": "Na + Cl₂ → ?", "options": ["NaCl", "2NaCl", "Na₂Cl"], "ans": "2NaCl", "note": "Balanced: 2Na + Cl₂ → 2NaCl"}
    ]
    return random.choice(challenges)

# --- LOGIN ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days'])
authenticator.login(location='main')

if st.session_state.get('authentication_status'):
    if 'xp' not in st.session_state: st.session_state.xp = 0
    if 'skill_vector' not in st.session_state: st.session_state.skill_vector = [0.0, 0.0, 0.0]
    
    rank_name, rank_col = ("🌱 Novice", "#808080") if st.session_state.xp < 50 else ("⚔️ Apprentice", "#4CAF50")
    if st.session_state.xp >= 150: rank_name, rank_col = "🎓 Scholar", "#2196F3"
    if st.session_state.xp >= 300: rank_name, rank_col = "🏆 Grandmaster", "#FFD700"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #0e1117; color: white; }}
        div.stButton > button {{
            background-color: transparent !important;
            color: #00FFA3 !important;
            border: 2px solid #00FFA3 !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            transition: 0.3s all ease !important;
        }}
        div.stButton > button:hover {{
            background-color: #00FFA3 !important;
            color: #0e1117 !important;
            box-shadow: 0 0 15px #00FFA3 !important;
        }}
        .game-box {{
            background: #161b22; padding: 25px; border-radius: 15px;
            border: 2px solid #00FFA3; margin-bottom: 20px;
        }}
        .display-text {{
            font-family: 'Courier New', monospace; text-align: center;
            font-size: 32px; color: #00FFA3; margin: 20px 0;
        }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f'<div style="background:{rank_col}; padding:15px; border-radius:10px; text-align:center;"><h3>{rank_name}</h3></div>', unsafe_allow_html=True)
        st.metric("Total Credits", st.session_state.xp)
        st.divider()
        mode = st.radio("Missions", ["Logic Lab", "Math Duel", "Binary Tech", "Chem Reactor", "Word Scramble", "AI Roadmap"])
        authenticator.logout('Logout', 'sidebar')

    # --- LOGIC LAB ---
    if mode == "Logic Lab":
        st.header("🔌 Logic Gate Simulator")
        
        if st.button("New Circuit"): st.session_state.logic_data = get_logic_gate()
        if 'logic_data' not in st.session_state: st.session_state.logic_data = get_logic_gate()
        
        l = st.session_state.logic_data
        st.markdown(f'<div class="game-box"><div class="display-text">{l["a"]} [{l["gate"]}] {l["b"]} = ?</div></div>', unsafe_allow_html=True)
        user_out = st.radio("Result:", [0, 1], horizontal=True, index=None)
        
        if st.button("Submit Signal"):
            if user_out is not None:
                if user_out == l['ans']:
                    st.balloons(); st.session_state.xp += 15
                    st.session_state.skill_vector[2] += 0.1
                    st.success("STABLE!")
                else: st.error("FAILED!")
            else: st.warning("Please select an output first!")

    # --- MATH DUEL ---
    elif mode == "Math Duel":
        st.header("🔢 Mental Math Duel")
        if st.button("Next Problem"): st.session_state.math_data = get_math_duel()
        if 'math_data' not in st.session_state: st.session_state.math_data = get_math_duel()
        
        m = st.session_state.math_data
        st.markdown(f'<div class="game-box"><div class="display-text">{m["q"]} = ?</div></div>', unsafe_allow_html=True)
        guess = st.number_input("Answer:", step=1, value=None, placeholder="Type your result...")
        
        if st.button("Check Result"):
            if guess is not None:
                if guess == m['ans']:
                    st.balloons(); st.session_state.xp += 10
                    st.session_state.skill_vector[0] += 0.1
                    st.success("Correct!")
                else: st.error(f"Wrong! Answer was {m['ans']}")
            else: st.warning("Type an answer first!")

    # --- BINARY TECH ---
    elif mode == "Binary Tech":
        st.header("💻 Binary Decoder")
        
        if st.button("New Data"): st.session_state.bin_data = get_tech_binary()
        if 'bin_data' not in st.session_state: st.session_state.bin_data = get_tech_binary()
        
        b = st.session_state.bin_data
        st.markdown(f'<div class="game-box"><div class="display-text">Binary: {b["binary"]}</div></div>', unsafe_allow_html=True)
        guess = st.number_input("Decimal Value:", step=1, value=None, placeholder="Decode...")
        
        if st.button("Decode"):
            if guess is not None:
                if guess == b['decimal']:
                    st.balloons(); st.session_state.xp += 20
                    st.session_state.skill_vector[2] += 0.1
                    st.success("Access Granted!")
                else: st.error("Access Denied!")
            else: st.warning("Enter a decimal value!")

    # --- CHEM REACTOR ---
    elif mode == "Chem Reactor":
        st.header("🧪 Chemical Reactor")
        if st.button("New Reaction"): st.session_state.chem_data = get_chem_challenge()
        if 'chem_data' not in st.session_state: st.session_state.chem_data = get_chem_challenge()
        c = st.session_state.chem_data
        st.markdown(f'<div class="game-box"><h2 style="text-align:center;">{c["q"]}</h2></div>', unsafe_allow_html=True)
        ans = st.selectbox("Product:", c['options'], index=None, placeholder="Choose product...")
        
        if st.button("Stabilize"):
            if ans:
                if ans == c['ans']:
                    st.snow(); st.session_state.xp += 20
                    st.session_state.skill_vector[1] += 0.1
                    st.success("Stable!")
                else: st.error("Boom! Reaction unstable.")
            else: st.warning("Select a product first!")

    # --- WORD SCRAMBLE ---
    elif mode == "Word Scramble":
        st.header("🧩 STEM Scramble")
        if st.button("New Word"): st.session_state.scramble = generate_word_scramble()
        if 'scramble' not in st.session_state: st.session_state.scramble = generate_word_scramble()
        s = st.session_state.scramble
        st.markdown(f'<div class="game-box"><h3>{s["scrambled"]}</h3><p>{s["clue"]}</p></div>', unsafe_allow_html=True)
        guess = st.text_input("Unscramble:", placeholder="Type word here...").upper()
        
        if st.button("Check"):
            if guess:
                if guess == s['original']:
                    st.snow(); st.session_state.xp += 20
                    st.success("Correct!")
                else: st.error("Wrong! Try again.")
            else: st.warning("Please type a word!")

    # --- AI ROADMAP ---
    else:
        st.header("📍 Career Roadmap")
        if st.session_state.xp < 50: st.warning("Earn 50 XP to unlock!")
        elif st.button("Generate Path"):
            with st.spinner("Analyzing performance..."):
                roadmap = generate_roadmap({"math": st.session_state.skill_vector[0], "science": st.session_state.skill_vector[1], "tech": st.session_state.skill_vector[2]})
                st.markdown(roadmap)

elif st.session_state.get('authentication_status') == False:
    st.error('Login incorrect')