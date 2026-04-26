import streamlit as st
import os
import tempfile
from parser import parse_resume, parse_jd
from agent import extract_skills, assess_skill, score_skill
from planner import generate_learning_plan

st.set_page_config(page_title="Catalyst — Skill Assessment Agent", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background: #0f1117; }
    
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 48px 40px;
        margin-bottom: 32px;
        text-align: center;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 0;
    }
    .hero .accent { color: #6366f1; }

    .card {
        background: #1e2330;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .card h3 {
        color: #e2e8f0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 16px 0;
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .stat-card {
        background: #1e2330;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-card .number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #6366f1;
        line-height: 1;
        margin-bottom: 6px;
    }
    .stat-card .label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .skill-tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
    }
    .skill-match {
        background: #064e3b;
        color: #6ee7b7;
        border: 1px solid #065f46;
    }
    .skill-missing {
        background: #450a0a;
        color: #fca5a5;
        border: 1px solid #7f1d1d;
    }

    .score-bar-wrap { margin-bottom: 12px; }
    .score-bar-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        color: #cbd5e1;
        font-size: 0.9rem;
    }
    .score-bar-bg {
        background: #2d3748;
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 10px;
        border-radius: 8px;
        transition: width 0.6s ease;
    }

    .plan-card {
        background: #1e2330;
        border-left: 4px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .plan-card.high { border-left-color: #ef4444; }
    .plan-card.medium { border-left-color: #f59e0b; }
    .plan-card.low { border-left-color: #22c55e; }
    .plan-card h4 { color: #e2e8f0; margin: 0 0 8px 0; font-size: 1.1rem; }
    .plan-card .meta { color: #64748b; font-size: 0.85rem; margin-bottom: 12px; }
    .plan-card .gap { color: #94a3b8; font-size: 0.9rem; margin-bottom: 12px; }
    .resource-link {
        display: inline-block;
        background: #0f1724;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 4px 4px 4px 0;
        color: #6366f1;
        font-size: 0.82rem;
        text-decoration: none;
    }

    .chat-q {
        background: #1e2330;
        border: 1px solid #2d3748;
        border-radius: 12px 12px 12px 0;
        padding: 16px 20px;
        color: #e2e8f0;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .chat-a {
        background: #1a2744;
        border: 1px solid #2d4a8a;
        border-radius: 12px 12px 0 12px;
        padding: 16px 20px;
        color: #bfdbfe;
        margin-bottom: 16px;
        font-size: 0.95rem;
        text-align: right;
    }

    .progress-wrap {
        background: #1e2330;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    }
    .progress-label {
        display: flex;
        justify-content: space-between;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    .progress-bg {
        background: #2d3748;
        border-radius: 8px;
        height: 8px;
    }
    .progress-fill {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        height: 8px;
        border-radius: 8px;
    }

    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: opacity 0.2s !important;
    }
    div[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

    div[data-testid="stTextArea"] textarea {
        background: #1e2330 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stFileUploader"] {
        background: #1e2330 !important;
        border: 2px dashed #2d3748 !important;
        border-radius: 10px !important;
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-high { background: #450a0a; color: #fca5a5; }
    .badge-medium { background: #451a03; color: #fed7aa; }
    .badge-low { background: #052e16; color: #86efac; }
    .badge-beginner { background: #450a0a; color: #fca5a5; }
    .badge-intermediate { background: #451a03; color: #fed7aa; }
    .badge-advanced { background: #052e16; color: #86efac; }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

for key, default in {
    "stage": "upload",
    "resume_text": "",
    "jd_text": "",
    "jd_skills": [],
    "resume_skills": [],
    "current_skill_index": 0,
    "conversation_history": {},
    "scores": [],
    "learning_plan": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── STAGE 1: Upload ──
if st.session_state.stage == "upload":
    st.markdown("""
    <div class="hero">
        <h1>Skill Assessment <span class="accent">Agent</span></h1>
        <p>Upload your resume + job description. Get assessed. Receive a personalised learning plan.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><h3>Resume (PDF)</h3>', unsafe_allow_html=True)
        resume_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>Job Description</h3>', unsafe_allow_html=True)
        jd_input = st.text_area("", height=180, placeholder="Paste the full job description here...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Start Assessment", use_container_width=True):
        if not resume_file or not jd_input.strip():
            st.error("Please upload a resume and paste a job description.")
        else:
            with st.spinner("Analysing resume and extracting skills..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(resume_file.read())
                    tmp_path = tmp.name
                resume_text = parse_resume(tmp_path)
                os.unlink(tmp_path)
                jd_text = parse_jd(jd_input)
                skills = extract_skills(resume_text, jd_text)
                st.session_state.resume_text = resume_text
                st.session_state.jd_text = jd_text
                st.session_state.jd_skills = skills["jd_skills"]
                st.session_state.resume_skills = skills["resume_skills"]
                st.session_state.stage = "gap_summary"
                st.rerun()

# ── STAGE 1.5: Gap Summary ──
elif st.session_state.stage == "gap_summary":
    resume_skills_lower = set(s.lower() for s in st.session_state.resume_skills)
    matched = [s for s in st.session_state.jd_skills if s.lower() in resume_skills_lower]
    missing = [s for s in st.session_state.jd_skills if s.lower() not in resume_skills_lower]
    match_pct = int(len(matched) / len(st.session_state.jd_skills) * 100) if st.session_state.jd_skills else 0

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card"><div class="number">{len(st.session_state.jd_skills)}</div><div class="label">Required Skills</div></div>
        <div class="stat-card"><div class="number">{len(matched)}</div><div class="label">Matched on Resume</div></div>
        <div class="stat-card"><div class="number">{match_pct}%</div><div class="label">Resume Match Rate</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><h3>Skills You Claim</h3>', unsafe_allow_html=True)
        if matched:
            tags = "".join(f'<span class="skill-tag skill-match">{s}</span>' for s in matched)
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b">No direct matches found</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h3>Skills You Are Missing</h3>', unsafe_allow_html=True)
        if missing:
            tags = "".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in missing)
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b">You claim all required skills!</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="color:#64748b; font-size:0.85rem; margin-bottom:16px">Resume claims will now be verified through a real conversational assessment.</p>', unsafe_allow_html=True)

    if st.button("Begin Assessment", use_container_width=True):
        st.session_state.stage = "assess"
        st.rerun()

# ── STAGE 2: Assessment ──
elif st.session_state.stage == "assess":
    skills = st.session_state.jd_skills
    idx = st.session_state.current_skill_index
    QUESTIONS_PER_SKILL = 2

    if idx >= len(skills):
        with st.spinner("Scoring all skills..."):
            scores = []
            for skill in skills:
                history = st.session_state.conversation_history.get(skill, [])
                if history:
                    score = score_skill(skill, history)
                    scores.append(score)
            st.session_state.scores = scores
            st.session_state.stage = "plan"
            st.rerun()
    else:
        current_skill = skills[idx]
        pct = int(idx / len(skills) * 100)

        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-label">
                <span>Assessing: <strong style="color:#e2e8f0">{current_skill}</strong></span>
                <span>{idx+1} of {len(skills)}</span>
            </div>
            <div class="progress-bg"><div class="progress-fill" style="width:{pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        history = st.session_state.conversation_history.get(current_skill, [])
        q_count = len(history)

        for turn in history:
            st.markdown(f'<div class="chat-q">{turn["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-a">{turn["answer"]}</div>', unsafe_allow_html=True)

        if q_count < QUESTIONS_PER_SKILL:
            if "pending_question" not in st.session_state or st.session_state.get("pending_skill") != current_skill:
                with st.spinner("Generating question..."):
                    question = assess_skill(current_skill, st.session_state.resume_text, history)
                    st.session_state.pending_question = question
                    st.session_state.pending_skill = current_skill

            st.markdown(f'<div class="chat-q">{st.session_state.pending_question}</div>', unsafe_allow_html=True)
            answer = st.text_area("Your answer", key=f"answer_{idx}_{q_count}", height=120, placeholder="Type your answer here...", label_visibility="collapsed")

            if st.button("Submit Answer", use_container_width=True):
                if not answer.strip():
                    st.error("Please type an answer before submitting.")
                else:
                    history.append({"question": st.session_state.pending_question, "answer": answer.strip()})
                    st.session_state.conversation_history[current_skill] = history
                    del st.session_state["pending_question"]
                    del st.session_state["pending_skill"]
                    st.rerun()
        else:
            st.success(f"Assessment complete for {current_skill}")
            if st.button("Next Skill", use_container_width=True):
                st.session_state.current_skill_index += 1
                if "pending_question" in st.session_state:
                    del st.session_state["pending_question"]
                    del st.session_state["pending_skill"]
                st.rerun()

# ── STAGE 3: Results ──
elif st.session_state.stage == "plan":
    assessed_match = sum(1 for s in st.session_state.scores if s["score"] >= 7)
    total = len(st.session_state.scores)
    match_pct = int(assessed_match / total * 100) if total else 0

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card"><div class="number">{total}</div><div class="label">Skills Assessed</div></div>
        <div class="stat-card"><div class="number">{assessed_match}</div><div class="label">Proficient (7+)</div></div>
        <div class="stat-card"><div class="number">{match_pct}%</div><div class="label">Verified Match Rate</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Score bars
    st.markdown('<div class="card"><h3>Proficiency Scores</h3>', unsafe_allow_html=True)
    for s in st.session_state.scores:
        pct = s["score"] * 10
        color = "#22c55e" if s["score"] >= 7 else "#f59e0b" if s["score"] >= 4 else "#ef4444"
        level = s["level"]
        badge_class = f"badge-{level.lower()}"
        st.markdown(f"""
        <div class="score-bar-wrap">
            <div class="score-bar-label">
                <span>{s['skill']} &nbsp;<span class="badge {badge_class}">{level}</span></span>
                <span style="color:{color}; font-weight:600">{s['score']}/10</span>
            </div>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%; background:{color}"></div></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Learning plan
    if st.session_state.learning_plan is None:
        with st.spinner("Generating personalised learning plan..."):
            plan = generate_learning_plan(
                st.session_state.resume_text,
                st.session_state.jd_skills,
                st.session_state.scores
            )
            st.session_state.learning_plan = plan

    st.markdown('<h3 style="color:#e2e8f0; margin: 24px 0 16px">Personalised Learning Plan</h3>', unsafe_allow_html=True)

    download_text = "PERSONALISED LEARNING PLAN\n" + "="*40 + "\n\n"

    for item in st.session_state.learning_plan:
        p = item["priority"].lower()
        resources_html = "".join(
            f'<a class="resource-link" href="{r["url"]}" target="_blank">{r["title"]} ({r["type"]})</a>'
            for r in item["resources"]
        )
        st.markdown(f"""
        <div class="plan-card {p}">
            <h4>{item['skill']}</h4>
            <div class="meta">Priority: <strong>{item['priority']}</strong> &nbsp;|&nbsp; Time to proficiency: <strong>{item['time_estimate']}</strong></div>
            <div class="gap">{item['gap_explanation']}</div>
            <div>{resources_html}</div>
        </div>
        """, unsafe_allow_html=True)

        download_text += f"SKILL: {item['skill']}\nPriority: {item['priority']}\nGap: {item['gap_explanation']}\nTime: {item['time_estimate']}\nResources:\n"
        for r in item["resources"]:
            download_text += f"  - {r['title']} ({r['type']}): {r['url']}\n"
        download_text += "\n"

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("Download Learning Plan", data=download_text, file_name="learning_plan.txt", mime="text/plain", use_container_width=True)

    if st.button("Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()