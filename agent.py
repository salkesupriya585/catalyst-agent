import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"
def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()

def ask(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_skills(resume_text, jd_text):
    prompt = (
        "You are a technical recruiter AI.\n\n"
        "Given the Job Description and Resume below, extract:\n"
        "1. jd_skills: list of specific technical skills required by the JD\n"
        "2. resume_skills: list of specific technical skills the candidate claims\n\n"
        "Return ONLY a JSON object in this exact format, no explanation:\n"
        '{"jd_skills": ["skill1", "skill2"], "resume_skills": ["skill1", "skill2"]}\n\n'
        "JOB DESCRIPTION:\n" + jd_text + "\n\n"
        "RESUME:\n" + resume_text
    )
    return json.loads(clean_json(ask(prompt)))

def assess_skill(skill, resume_text, conversation_history):
    history_str = ""
    for turn in conversation_history:
        history_str += "Q: " + turn["question"] + "\nA: " + turn["answer"] + "\n"

    prompt = (
        "You are a strict but fair technical interviewer assessing proficiency in: " + skill + "\n\n"
        "Candidate resume context:\n" + resume_text[:1000] + "\n\n"
        "Previous Q&A:\n" + (history_str if history_str else "None yet.") + "\n\n"
        "Ask ONE concise scenario-based question to assess real understanding of " + skill + ".\n"
        "Do NOT repeat previous questions. Do NOT ask yes/no questions.\n"
        "Return only the question, nothing else."
    )
    return ask(prompt).strip()

def score_skill(skill, conversation_history):
    history_str = ""
    for turn in conversation_history:
        history_str += "Q: " + turn["question"] + "\nA: " + turn["answer"] + "\n"

    prompt = (
        "You are evaluating a candidate's proficiency in: " + skill + "\n\n"
        "Based on these Q&A exchanges:\n" + history_str + "\n"
        "Return ONLY this JSON, no explanation:\n"
        '{"skill": "' + skill + '", "score": <1-10>, "level": "<Beginner|Intermediate|Advanced>", "feedback": "<one sentence>"}'
    )
    return json.loads(clean_json(ask(prompt)))