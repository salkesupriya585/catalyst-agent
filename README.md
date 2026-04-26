# 🎯 Catalyst — AI-Powered Skill Assessment Agent

An AI agent that takes a Job Description and a candidate's resume, conversationally assesses real proficiency on each required skill, identifies gaps, and generates a personalised learning plan.

Built for **Catalyst Hackathon by Deccan AI**.

## 🚀 Live Demo
[https://catalyst-agent-deccan.streamlit.app](https://catalyst-agent.streamlit.app)

## 🧠 What it does
1. Upload a resume (PDF) + paste a Job Description
2. AI agent asks scenario-based questions for each required skill
3. Scores proficiency: Beginner / Intermediate / Advanced
4. Generates a personalised learning plan with resources + time estimates

## 🏗️ Architecture
Resume (PDF) + JD (text)
↓
[Parser] — extracts clean text
↓
[Skill Extractor] — Groq LLM identifies required vs claimed skills
↓
[Assessment Agent] — asks 2 scenario-based questions per skill
↓
[Scorer] — rates each skill 1–10, assigns level
↓
[Learning Plan Generator] — curated resources + time estimates

## ⚙️ Tech Stack
- **LLM**: Groq (llama-3.3-70b-versatile) — free tier
- **Frontend**: Streamlit
- **Resume Parsing**: pdfplumber
- **Language**: Python 3.10+

## 🛠️ Run Locally

1. Clone the repo
```bash
git clone https://github.com/salkesupriya585/catalyst-agent.git
cd catalyst-agent
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Add your API key — create a `.env` file:

4. Run the app
```bash
streamlit run main.py
```

## 📁 Project Structure
catalyst-agent/
├── main.py        # Streamlit UI + app flow
├── agent.py       # LLM calls — skill extraction, assessment, scoring
├── parser.py      # Resume PDF parser + JD cleaner
├── planner.py     # Learning plan generator
└── requirements.txt

## 👩‍💻 Built by
Supriya Santosh Salke  
[LinkedIn](https://www.linkedin.com/in/supriya-salke-0910b12b5) | [GitHub](https://github.com/salkesupriya585)
