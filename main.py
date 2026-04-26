import streamlit as st
import os
import tempfile
from parser import parse_resume, parse_jd
from agent import extract_skills, assess_skill, score_skill
from planner import generate_learning_plan

st.set_page_config(page_title="Catalyst — Skill Assessment Agent", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered Skill Assessment Agent")
st.caption("Upload a resume + job description → get assessed → receive a personalised learning plan")

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
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Upload Resume (PDF)")
        resume_file = st.file_uploader("Choose resume PDF", type=["pdf"])
    with col2:
        st.subheader("📋 Paste Job Description")
        jd_input = st.text_area("Paste the full JD here", height=300)

    if st.button("🚀 Start Assessment", use_container_width=True):
        if not resume_file or not jd_input.strip():
            st.error("Please upload a resume and paste a job description.")
        else:
            with st.spinner("Parsing resume and extracting skills..."):
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
    jd_skills = set(s.lower() for s in st.session_state.jd_skills)
    resume_skills = set(s.lower() for s in st.session_state.resume_skills)
    matched = [s for s in st.session_state.jd_skills if s.lower() in resume_skills]
    missing = [s for s in st.session_state.jd_skills if s.lower() not in resume_skills]
    match_pct = int(len(matched) / len(st.session_state.jd_skills) * 100) if st.session_state.jd_skills else 0

    st.subheader("📊 Skill Gap Summary")
    st.caption("Before the assessment — based on what your resume claims vs what the JD requires.")

    col1, col2, col3 = st.columns(3)
    col1.metric("JD Required Skills", len(st.session_state.jd_skills))
    col2.metric("Matched on Resume", len(matched))
    col3.metric("Resume Match Rate", f"{match_pct}%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Skills You Claim")
        for s in matched:
            st.success(s)
        if not matched:
            st.info("No direct matches found")

    with col2:
        st.markdown("### ❌ Skills You're Missing")
        for s in missing:
            st.error(s)
        if not missing:
            st.info("You claim all required skills!")

    st.divider()
    st.info("⚠️ Note: Resume claims will now be verified through a real conversational assessment.")

    if st.button("▶️ Start Skill Assessment", use_container_width=True):
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
        progress = idx / len(skills)
        st.progress(progress, text=f"Assessing skill {idx+1} of {len(skills)}: **{current_skill}**")
        st.subheader(f"🧠 Assessing: `{current_skill}`")

        history = st.session_state.conversation_history.get(current_skill, [])
        q_count = len(history)

        for turn in history:
            with st.chat_message("assistant"):
                st.write(turn["question"])
            with st.chat_message("user"):
                st.write(turn["answer"])

        if q_count < QUESTIONS_PER_SKILL:
            if "pending_question" not in st.session_state or st.session_state.get("pending_skill") != current_skill:
                with st.spinner("Generating question..."):
                    question = assess_skill(current_skill, st.session_state.resume_text, history)
                    st.session_state.pending_question = question
                    st.session_state.pending_skill = current_skill

            with st.chat_message("assistant"):
                st.write(st.session_state.pending_question)

            answer = st.text_area("Your answer:", key=f"answer_{idx}_{q_count}", height=100)

            if st.button("Submit Answer ➡️", use_container_width=True):
                if not answer.strip():
                    st.error("Please type an answer before submitting.")
                else:
                    history.append({"question": st.session_state.pending_question, "answer": answer.strip()})
                    st.session_state.conversation_history[current_skill] = history
                    del st.session_state["pending_question"]
                    del st.session_state["pending_skill"]
                    st.rerun()
        else:
            st.success(f"✅ Done assessing {current_skill}!")
            if st.button("Next Skill ➡️", use_container_width=True):
                st.session_state.current_skill_index += 1
                if "pending_question" in st.session_state:
                    del st.session_state["pending_question"]
                    del st.session_state["pending_skill"]
                st.rerun()

# ── STAGE 3: Results + Learning Plan ──
elif st.session_state.stage == "plan":
    st.subheader("📊 Assessment Results")

    # Score cards
    cols = st.columns(len(st.session_state.scores))
    for i, s in enumerate(st.session_state.scores):
        with cols[i]:
            color = "🟢" if s["score"] >= 7 else "🟡" if s["score"] >= 4 else "🔴"
            st.metric(label=s["skill"], value=f"{color} {s['level']}", delta=f"Score: {s['score']}/10")

    # Bar chart
    st.divider()
    st.subheader("📈 Proficiency Overview")
    chart_data = {s["skill"]: s["score"] for s in st.session_state.scores}
    st.bar_chart(chart_data, use_container_width=True)

    # JD match rate after assessment
    assessed_match = sum(1 for s in st.session_state.scores if s["score"] >= 7)
    total = len(st.session_state.scores)
    match_pct = int(assessed_match / total * 100) if total else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Skills Assessed", total)
    col2.metric("Skills Proficient (≥7)", assessed_match)
    col3.metric("Assessed Match Rate", f"{match_pct}%")

    st.divider()

    # Learning plan
    if st.session_state.learning_plan is None:
        with st.spinner("Generating your personalised learning plan..."):
            plan = generate_learning_plan(
                st.session_state.resume_text,
                st.session_state.jd_skills,
                st.session_state.scores
            )
            st.session_state.learning_plan = plan

    st.subheader("🗺️ Your Personalised Learning Plan")

    # Build downloadable text
    download_text = "PERSONALISED LEARNING PLAN\n"
    download_text += "=" * 40 + "\n\n"

    for item in st.session_state.learning_plan:
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(item["priority"], "⚪")
        with st.expander(f"{priority_color} {item['skill']} — {item['time_estimate']}", expanded=True):
            st.write("**Gap:**", item["gap_explanation"])
            st.write("**Priority:**", item["priority"])
            st.write("**Time to proficiency:**", item["time_estimate"])
            st.write("**Resources:**")
            for r in item["resources"]:
                st.markdown(f"- [{r['title']}]({r['url']}) `{r['type']}`")

        download_text += f"SKILL: {item['skill']}\n"
        download_text += f"Priority: {item['priority']}\n"
        download_text += f"Gap: {item['gap_explanation']}\n"
        download_text += f"Time: {item['time_estimate']}\n"
        download_text += "Resources:\n"
        for r in item["resources"]:
            download_text += f"  - {r['title']} ({r['type']}): {r['url']}\n"
        download_text += "\n"

    st.divider()

    # Download button
    st.download_button(
        label="⬇️ Download Learning Plan",
        data=download_text,
        file_name="learning_plan.txt",
        mime="text/plain",
        use_container_width=True
    )

    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()