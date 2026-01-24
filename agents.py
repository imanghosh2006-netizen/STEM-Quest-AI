import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM

# Senior Dev Tip: Dummy key to keep CrewAI's internal logic happy
os.environ["OPENAI_API_KEY"] = "NA"

def get_llm():
    """Returns the Groq-powered brain for our agents."""
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.7
    )

def generate_roadmap(user_skills):
    """The main engine for STEM Quest. Called by the UI team."""
    
    # --- OPTION 2: DATA VALIDATION ---
    try:
        # Ensures all inputs are integers to prevent AI confusion
        validated_skills = {k: int(v) for k, v in user_skills.items()}
    except (ValueError, TypeError):
        return "### ❌ Input Error\nPlease ensure all quiz scores are valid numbers before generating the roadmap."

    llm = get_llm()
    
    # --- OPTION 3: PREMIUM PROMPTS (AGENT BACKSTORIES) ---
    
    # Define Agent 1: The STEM Guru
    counselor = Agent(
        role='STEM Career Matchmaker',
        goal=f'Based on these scores: {validated_skills}, suggest 1 high-growth STEM career.',
        backstory=(
            'You are a world-class career strategist with 20 years of experience. '
            'You don’t just find jobs; you identify callings by looking for the unique '
            'intersection of a student’s technical spikes and market trends.'
        ),
        llm=llm,
        verbose=True
    )
    
    # Define Agent 2: The Roadmap Architect
    specialist = Agent(
        role='Academic Path Architect',
        goal='Create a weekly learning roadmap in Markdown format.',
        backstory=(
            'You are an expert curriculum designer specializing in accelerated learning. '
            'You find the fastest, most effective way for beginners to gain job-ready skills '
            'using high-quality free online resources.'
        ),
        llm=llm,
        verbose=True
    )

    # Define the Tasks
    task1 = Task(
        description=f"Analyze scores: {validated_skills} and recommend one STEM path.",
        expected_output="A career title and a 2-sentence explanation of why it fits these specific scores.",
        agent=counselor
    )

    task2 = Task(
        description=(
            "Write a detailed 4-week roadmap for this career in Markdown. "
            "Use clean bullet points and professional headers. Do not use extra indentation."
        ),
        expected_output=(
            "A professional 4-week roadmap. Each week must include: "
            "1. A catchy 'Focus Title'. "
            "2. 3-4 specific learning objectives. "
            "3. A 'Pro-Tip' for success. "
            "End with a short motivational closing statement."
        ),
        agent=specialist,
        context=[task1]
    )

    # The Crew
    crew = Crew(
        agents=[counselor, specialist],
        tasks=[task1, task2],
        process=Process.sequential,
        memory=False,  
        cache=False,   
        verbose=True
    ) 

    # Kickoff and return clean raw text
    result = crew.kickoff()
    return result.raw