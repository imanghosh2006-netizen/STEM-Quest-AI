import streamlit as st
import json

def run_quiz():
    st.subheader("🚀 STEM Personality Quiz")
    
    # Load questions
    with open('quiz_data.json', 'r') as f:
        data = json.load(f)
    
    # Use a form so the page doesn't refresh on every click
    with st.form("quiz_form"):
        user_responses = []
        for q in data['questions']:
            choice = st.radio(q['question'], q['options'], key=f"q_{q['id']}")
            # Map choice back to the skill
            skill_index = q['options'].index(choice)
            user_responses.append(q['skills'][skill_index])
        
        submitted = st.form_submit_button("Submit Results")
        
        if submitted:
            # Save the identified skills
            skills_string = ", ".join(list(set(user_responses)))
            st.session_state['detected_skills'] = skills_string
            
            # Add this line so your AI agents have the 'user_interests' they need!
            st.session_state['user_interests'] = "High-tech STEM careers and hands-on projects"
            
            st.success(f"Target Skills Identified: {skills_string}")
            st.balloons()