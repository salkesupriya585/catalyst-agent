import json
from agent import ask, clean_json

def generate_learning_plan(resume_text, jd_skills, scores):
    """
    Given JD skills and assessment scores, generate a personalised learning plan.
    scores = [{"skill": "Python", "score": 3, "level": "Beginner", "feedback": "..."}, ...]
    """

    scores_str = ""
    for s in scores:
        scores_str += (
            "- " + s["skill"] +
            ": " + s["level"] +
            " (score " + str(s["score"]) + "/10) — " +
            s["feedback"] + "\n"
        )

    prompt = (
        "You are a personalised learning coach.\n\n"
        "A candidate has been assessed on the following skills required by a job description.\n"
        "Here are their assessment results:\n\n"
        + scores_str +
        "\nBased on these results, generate a personalised learning plan.\n"
        "For each skill where score is below 7, include:\n"
        "1. A short explanation of the gap\n"
        "2. 2-3 specific free resources (with URLs if possible)\n"
        "3. Realistic time estimate to reach proficiency\n"
        "4. Priority: High / Medium / Low based on how critical the skill gap is\n\n"
        "Return ONLY a JSON array like this, no explanation:\n"
        '[\n'
        '  {\n'
        '    "skill": "skill name",\n'
        '    "gap_explanation": "why this is a gap",\n'
        '    "priority": "High|Medium|Low",\n'
        '    "time_estimate": "e.g. 2-3 weeks",\n'
        '    "resources": [\n'
        '      {"title": "Resource Name", "url": "https://...", "type": "Course|Video|Docs|Article"}\n'
        '    ]\n'
        '  }\n'
        ']\n'
    )

    response = ask(prompt)
    return json.loads(clean_json(response)) 
