# (Member 1) The Main Website Entry Point
import streamlit as st
import yaml
from yaml.loader import SafeLoader
try:
    from agents import generate_roadmap_ui
    from game_logic import run_quiz
except ImportError:
    st.error("Error:agents.py or game_logic.py not found in this folder.")

st.set_page_config(page_title="STEM Quest",page_icon="🚀",layout="wide")

