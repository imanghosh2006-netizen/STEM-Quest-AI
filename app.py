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

def generate_ai_question(category):
    """Generates a truly random STEM question using sub-topics and high temperature."""
    
    # Sub-topics force the AI to move away from the same 'default' questions
    sub_topics = {
        "Math": ["Linear Algebra", "Discrete Math", "Statistics", "Trigonometry", "Number Theory", "Calculus"],
        "Science": ["Astrophysics", "Organic Chemistry", "Molecular Biology", "Thermodynamics", "Geology", "Quantum Mechanics"],
        "Tech": ["Data Structures", "Cybersecurity", "Cloud Computing", "Machine Learning", "Networking", "Software Architecture"]
    }
    
    selected_sub = random.choice(sub_topics.get(category, ["General"]))
    # A random seed in the prompt breaks the AI's tendency to repeat
    seed = random.randint(1, 10000)

    prompt = f"""
    Generate ONE unique multiple-choice question for {category}, specifically focusing on {selected_sub}.
    Difficulty: Challenging.
    Random Seed: {seed}.
    
    Return ONLY a JSON object with this exact structure:
    {{
        "question": "the question text",
        "options": ["option 1", "option 2", "option 3", "option 4"],
        "answer": "the exact string of the correct option",
        "xp": 15
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9 # High temperature = more randomness
    )
    
    return json.loads(response.choices[0].message.content)

# --- 1. LOGIN CONFIGURATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='main')

authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')

if authentication_status:
    # --- 2. MAIN APP STARTS HERE ---
    if 'xp' not in st.session_state: st.session_state.xp = 0
    if 'skill_vector' not in st.session_state: st.session_state.skill_vector = [0.0, 0.0, 0.0]
    if 'first_visit' not in st.session_state: st.session_state.first_visit = True

    st.markdown("""
        <style>
        .stApp { background-color: #f4f4f4; }
        .welcome-container {
            border-right: 25px solid #f5c600;
            padding: 40px; background-color: #ffffff;
            border-radius: 10px; text-align: center; margin-bottom: 30px;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.session_state.first_visit:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown('<div class="welcome-container"><h1 style="font-size: 50px;">WELCOME TO</h1><h1 style="font-size: 60px; color: #d4a017;">LEARNER</h1></div>', unsafe_allow_html=True)
            st.info(f"Welcome back, {name}! Loading your STEM Dashboard...")
            time.sleep(3)
        placeholder.empty()
        st.session_state.first_visit = False

    with st.sidebar:
        st.title(f"Hi, {name}!")
        st.metric("Total XP", st.session_state.xp)
        st.write("**Proficiency Levels:**")
        m, s, t = st.session_state.skill_vector
        st.progress(min(m, 1.0), text=f"Math: {m:.1f}")
        st.progress(min(s, 1.0), text=f"Science: {s:.1f}")
        st.progress(min(t, 1.0), text=f"Tech: {t:.1f}")
        st.divider()
        mode = st.radio("Navigation", ["Training Center", "AI Roadmap"])
        st.divider()
        authenticator.logout('Logout', 'sidebar')

    # --- 3. TRAINING CENTER (QUIZ) ---
    if mode == "Training Center":
        st.header("🚀 AI-Generated STEM Challenge")
        cat = st.selectbox("Select Subject", ["Math", "Science", "Tech"])

        def refresh_question():
            with st.spinner("AI is thinking of a challenge..."):
                try:
                    st.session_state.current_ai_q = generate_ai_question(cat)
                    st.session_state.answered = False
                except Exception as e:
                    st.error(f"AI had a glitch: {e}")

        # Trigger refresh on button click or category change
        if st.button(f"Generate New {cat} Question"):
            refresh_question()
        elif 'current_ai_q' not in st.session_state:
            refresh_question()
        elif 'last_cat' in st.session_state and st.session_state.last_cat != cat:
            st.session_state.last_cat = cat
            refresh_question()
            st.rerun()

        st.session_state.last_cat = cat

        if 'current_ai_q' in st.session_state:
            q = st.session_state.current_ai_q
            # Unique key prevents form "stickiness"
            with st.form(key=f"ai_q_{cat}_{hash(q['question'])}"):
                st.write(f"### {q['question']}")
                choice = st.radio("Pick your answer:", q['options'])
                submitted = st.form_submit_button("Submit Answer")
                
                if submitted and not st.session_state.get('answered', False):
                    if choice == q['answer']:
                        st.session_state.xp += q['xp']
                        idx = {"Math": 0, "Science": 1, "Tech": 2}.get(cat)
                        st.session_state.skill_vector[idx] += 0.2
                        st.success(f"✅ Correct! +{q['xp']} XP")
                    else:
                        st.error(f"❌ Incorrect! The right answer was: {q['answer']}")
                    st.session_state.answered = True

    # --- 4. AI ROADMAP ---
    else:
        st.header("📍 Your Personalized Path")
        if st.session_state.xp == 0:
            st.warning("Please earn some XP in the Training Center first!")
        else:
            if st.button("Generate Roadmap"):
                cur_m, cur_s, cur_t = st.session_state.skill_vector
                user_data = {"math": cur_m, "science": cur_s, "tech": cur_t}
                with st.spinner("AI Agents are architecting your future..."):
                    try:
                        roadmap = generate_roadmap(user_data)
                        st.markdown(roadmap)
                    except Exception as e:
                        st.error(f"Error connecting to AI agents: {e}")

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')