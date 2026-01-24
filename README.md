# 🚀 LEARNER: AI-Driven STEM Career Architect

An adaptive learning platform that uses **Multi-Agent AI Systems** to bridge the gap between STEM curiosity and career mastery.

## 🧠 Core Features
- **Adaptive Testing:** Real-time Skill Vector tracking (Math, Science, Tech) based on quiz performance.
- **Multi-Agent Orchestration:** Powered by **CrewAI**, utilizing specialized agents:
  - *Career Pathfinder:* Analyzes skill vectors to identify optimal industry roles.
  - *Curriculum Architect:* Designs a personalized, step-by-step learning roadmap.
- **Secure Authentication:** Integrated login system with BCrypt password hashing.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Orchestration:** CrewAI
- **LLM:** Groq (Llama 3)
- **Security:** Streamlit-Authenticator & YAML Configuration

---

## 💻 Getting Started (For Team Members)

Follow these steps exactly to set up the project on your local machine:

### STEPS:
1. Clone the Repository
```bash
git clone [https://github.com/imanghosh2006-netizen/STEM-Quest-Platform.git](https://github.com/imanghosh2006-netizen/STEM-Quest-Platform.git)
cd STEM-Quest-Platform
```

2. Set Up a Virtual Environment (venv)
This creates an isolated space for the project so it doesn't mess up your global Python settings.


Bash
python -m venv venv
```


3. Activate the Virtual Environment
You must do this every time you open a new terminal to work on the project.

On Windows:

Bash
.\venv\Scripts\activate
On Mac/Linux:

Bash
source venv/bin/activate


4. Install Dependencies
Once your environment is active (you should see (venv) in your terminal), run:

Bash
pip install -r requirements.txt


5. Setup Secrets (CRITICAL)
The .streamlit/secrets.toml file is NOT on GitHub. You must create it manually:

In your project folder, create a new folder named .streamlit.

Inside that folder, create a file named secrets.toml.

Paste the following into the file (ask the team lead for the API Key):

Ini, TOML
GROQ_API_KEY = "PASTE_YOUR_GROQ_KEY_HERE"


6. Run the App
Bash
streamlit run app.py


📈 Demo Instructions
Login with your credentials (e.g., imanghosh2006-netizen / 123).

Complete challenges in the Training Center to build your Skill Vector.

Navigate to AI Roadmap to have the agents architect your personalized career path.