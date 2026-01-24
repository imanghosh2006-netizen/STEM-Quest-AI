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
        temperature=0.3 
    )

def generate_roadmap(user_scores):
    """
    Expects user_scores as: {'math': X, 'science': Y, 'tech': Z}
    """
    try:
        llm = get_llm()
        
        # --- AGENTS ---
        counselor = Agent(
            role='STEM Career Matchmaker',
            goal='Identify a high-growth STEM career based on: Math {math}, Science {science}, Tech {tech}.',
            backstory=(
                'You are a world-class career strategist. You look at technical proficiency '
                'scores to suggest the perfect career path for a student.'
            ),
            llm=llm,
            verbose=True
        )
        
        specialist = Agent(
            role='Curriculum Designer',
            goal='Create a 4-week learning roadmap based on the suggested career.',
            backstory=(
                'You specialize in accelerated learning. You design paths that '
                'focus on exactly what a student needs to reach a job-ready level.'
            ),
            llm=llm,
            verbose=True
        )

        # --- TASKS ---
        # Note: We use the keys math, science, and tech to match your app logic
        task1 = Task(
            description=(
                "Analyze these proficiency scores: Math: {math}/1.0, Science: {science}/1.0, Tech: {tech}/1.0. "
                "Suggest 1 high-growth STEM career and give a 2-sentence 'Why' based on these specific strengths."
            ),
            expected_output="A career title and a brief justification.",
            agent=counselor
        )

        task2 = Task(
            description=(
                "Based on the career from Task 1 and the skill levels (M:{math}, S:{science}, T:{tech}), "
                "design a 4-week roadmap. Adjust difficulty: if a score is below 0.4, include more basics. "
                "If above 0.8, make Week 1 a masterclass."
            ),
            expected_output=(
                "A Markdown formatted 4-week roadmap. Each week needs: "
                "1. Focus Title | 2. 3 Specific Objectives | 3. A Success Pro-Tip."
            ),
            agent=specialist,
            context=[task1]
        )

        # --- THE CREW ---
        crew = Crew(
            agents=[counselor, specialist],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=True
        ) 

        # Kickoff with the dictionary passed from app.py
        result = crew.kickoff(inputs=user_scores)
        return result.raw

    except Exception as e:
        return f"### ⚠️ AI Error\nAn error occurred while generating your roadmap: {str(e)}"