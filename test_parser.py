from parser import parse_resume, parse_jd
from agent import extract_skills
from planner import generate_learning_plan

resume_text = parse_resume("test_resume.pdf")
sample_jd = """
We are looking for a Python Developer with experience in REST APIs, 
SQL databases, and basic machine learning. The candidate should know 
Git, FastAPI, and have good problem solving skills.
"""
jd_text = parse_jd(sample_jd)
skills = extract_skills(resume_text, jd_text)

# Simulate scores (pretend assessment already happened)
mock_scores = [
    {"skill": "Python", "score": 2, "level": "Beginner", "feedback": "No Python experience shown"},
    {"skill": "FastAPI", "score": 1, "level": "Beginner", "feedback": "Never used FastAPI"},
    {"skill": "machine learning", "score": 3, "level": "Beginner", "feedback": "Limited ML exposure"},
    {"skill": "SQL databases", "score": 7, "level": "Intermediate", "feedback": "Good SQL knowledge"},
]

plan = generate_learning_plan(resume_text, skills["jd_skills"], mock_scores)

for item in plan:
    print("\n===", item["skill"], "===")
    print("Priority:", item["priority"])
    print("Gap:", item["gap_explanation"])
    print("Time:", item["time_estimate"])
    for r in item["resources"]:
        print(" -", r["title"], "->", r["url"])