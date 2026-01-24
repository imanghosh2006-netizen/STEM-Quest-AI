import streamlit as st
import streamlit_authenticator as stauth
import json
import time
import yaml
from yaml.loader import SafeLoader
from agents import generate_roadmap 

# --- 1. LOGIN CONFIGURATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Newest version login call
authenticator.login(location='main')

# Safely get status from session state
authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')

if authentication_status:
    # --- 2. MAIN APP STARTS HERE ---
    
    # Initialization
    if 'xp' not in st.session_state: st.session_state.xp = 0
    if 'skill_vector' not in st.session_state: st.session_state.skill_vector = [0.0, 0.0, 0.0]
    if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
    if 'first_visit' not in st.session_state: st.session_state.first_visit = True

    # Custom CSS Style
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

    # Splash Screen (First time only)
    if st.session_state.first_visit:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown('<div class="welcome-container"><h1 style="font-size: 50px;">WELCOME TO</h1><h1 style="font-size: 60px; color: #d4a017;">LEARNER</h1></div>', unsafe_allow_html=True)
            st.info(f"Welcome back, {name}! Loading your STEM Dashboard...")
            time.sleep(3)
        placeholder.empty()
        st.session_state.first_visit = False

    # Side Bar Dashboard
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
        # LOGOUT BUTTON PLACEMENT
        authenticator.logout('Logout', 'sidebar')

    # --- 3. TRAINING CENTER (QUIZ) ---
    if mode == "Training Center":
        st.header("🚀 Daily Subject Challenge")
        
        def load_quiz_data():
            with open('quiz_data.json', 'r') as f: return json.load(f)

        cat = st.selectbox("Select Subject", ["Math", "Science", "Tech"])
        data = load_quiz_data()
        questions = data.get(cat, [])

        if st.session_state.q_idx < len(questions):
            current_q = questions[st.session_state.q_idx]
            with st.form(key=f"q_form_{st.session_state.q_idx}"):
                st.write(f"### {current_q['question']}")
                choice = st.radio("Options:", current_q['options'])
                if st.form_submit_button("Submit"):
                    if choice == current_q['answer']:
                        st.session_state.xp += current_q['xp']
                        idx = {"Math": 0, "Science": 1, "Tech": 2}.get(cat)
                        st.session_state.skill_vector[idx] += 0.2
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect! It was {current_q['answer']}")
                    st.session_state.q_idx += 1
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("Category complete!")
            if st.button("Restart Category"):
                st.session_state.q_idx = 0
                st.rerun()

    # --- 4. AI ROADMAP ---
    else:
        st.header("📍 Your Personalized Path")
        if st.session_state.xp == 0:
            st.warning("Please earn some XP in the Training Center first!")
        else:
            if st.button("Generate Roadmap"):
                # Use current values from the skill_vector
                cur_m, cur_s, cur_t = st.session_state.skill_vector
                user_data = {"math": cur_m, "science": cur_s, "tech": cur_t}
                with st.spinner("AI Agents are architecting your future..."):
                    try:
                        roadmap = generate_roadmap(user_data)
                        st.markdown(roadmap)
                    except Exception as e:
                        st.error(f"Error connecting to AI agents: {e}")

# --- 5. AUTHENTICATION ERRORS ---
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')