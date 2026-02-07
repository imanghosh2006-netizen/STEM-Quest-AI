import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="AI Health Check", page_icon="🚀")

st.title("🤖 AI System Diagnostic")
st.write("Checking connection between Streamlit and Groq...")

# 1. Check if the key exists in st.secrets
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ ERROR: 'GROQ_API_KEY' not found in secrets.toml")
    st.info("Check if you named the key something else by mistake! ")
    st.stop() # Stops the app here so it doesn't crash later

try:
    # 2. Initialize the Groq Client
    # We pull the key directly from the secret vault
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    st.success("✅ secrets.toml loaded successfully!")

    # 3. Test the actual AI response
    with st.spinner("Requesting response from Llama 3..."):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a system diagnostic tool."},
                {"role": "user", "content": "Status check: Say 'All systems functional'"}
            ],
            temperature=0.5
        )
    
    # 4. Show result
    ai_response = completion.choices[0].message.content
    st.balloons() # Fun effect for the demo!
    st.success(f"🤖 AI Response: {ai_response}")
    
    st.info("Your AI integration is officially READY for the hackathon.")

except Exception as e:
    st.error(f"⚠️ Connection Failed: {e}")
    st.warning("Tip: Make sure your internet is stable and your API key is active.")