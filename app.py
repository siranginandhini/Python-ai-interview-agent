"""Chatbot-style Python Developer AI Interview Agent."""
from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from agents.evaluation_agent import EvaluationAgent
from agents.interview_agent import InterviewAgent
from agents.report_agent import ReportAgent
from database.database import create_candidate, create_interview, dashboard_metrics, finalize_interview, initialize_database, interview_history, save_answer, save_question
from utils.helpers import adaptive_difficulty

load_dotenv(); initialize_database()
st.set_page_config(page_title="Python Interview Chatbot", page_icon="Python", layout="wide")
#adding some comments to test the git commit and push functionality
def groq_client():
    key = os.getenv("GROQ_API_KEY") or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None)
    if not key: return None
    try:
        from groq import Groq
        return Groq(api_key=key)
    except Exception: return None

def initialize_state():
    for key, value in {"stage":"setup", "messages":[], "records":[], "index":0, "current":None}.items():
        st.session_state.setdefault(key, value)

def bullets(items):
    return "\n".join(f"- {item}" for item in items) or "- None noted"

def question_message(question):
    text = f"**Question {st.session_state['index'] + 1} of {st.session_state['total']}**  \n*{question['category']} · {question['difficulty']}*  \n\n{question['question']}"
    if question.get("question_type") == "coding":
        text += "\n\nPaste your Python code in the chat. I will statically review it; candidate code is never executed."
        if question.get("starter_code"): text += f"\n\n```python\n{question['starter_code']}\n```"
    return text

def ask_next_question():
    state = st.session_state
    difficulty = state["current_difficulty"] if state["difficulty"] == "Adaptive" else state["difficulty"]
    question = InterviewAgent(groq_client(), os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")).generate_question(state["experience"], state["interview_type"], difficulty, [r["question"]["question"] for r in state["records"]])
    state["current"], state["question_id"] = question, save_question(state["interview_id"], question)
    state["messages"].append({"role":"assistant", "content":question_message(question)})

def begin_interview(name, experience, interview_type, difficulty, total):
    state = st.session_state
    candidate_id = create_candidate(name, experience)
    state.update({"name":name, "experience":experience, "interview_type":interview_type, "difficulty":difficulty, "current_difficulty":"Easy" if difficulty == "Adaptive" else difficulty, "total":total, "interview_id":create_interview(candidate_id, interview_type, difficulty, total), "records":[], "messages":[{"role":"assistant", "content":f"Hi **{name}**! I’m your Python interview coach. I’ll ask {total} questions and provide feedback after each answer. Let’s begin."}], "index":0, "stage":"chat"})
    ask_next_question()

def setup_page():
    st.title("Python Developer AI Interview Chatbot")
    st.write("Practice Python interviews with an AI interviewer and improve your technical skills.")
    if not os.getenv("GROQ_API_KEY"): st.warning("No GROQ_API_KEY configured. The chat works in offline fallback mode, but detailed AI feedback needs a key.")
    with st.form("candidate_setup"):
        name = st.text_input("What is your name?")
        experience = st.selectbox("Experience level", ["Fresher", "0–1 Years", "1–3 Years", "3–5 Years", "5+ Years"])
        interview_type = st.selectbox("Interview type", ["Python Fundamentals", "Advanced Python", "Python + DSA", "Python + SQL", "Python Backend", "Python Full Stack", "Mixed Python Interview"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Adaptive"])
        total = st.selectbox("Number of questions", [5, 10, 15, 20])
        started = st.form_submit_button("Start Chat Interview", type="primary")
    if started:
        if not name.strip(): st.error("Please enter your name to start.")
        else: begin_interview(name.strip(), experience, interview_type, difficulty, total); st.rerun()

def feedback_message(evaluation):
    improvements = evaluation["areas_to_improve"] or evaluation["missing_points"]
    verdict = evaluation.get("verdict", "Incorrect" if evaluation["score"] < 4 else "Partially correct")
    if verdict == "Correct":
        text = f"Your answer is correct. {evaluation['feedback']}"
    elif verdict == "Partially correct":
        text = f"Your answer is partially correct. {evaluation['feedback']}"
    else:
        text = f"Your answer is incorrect. {evaluation['feedback']}"
    if evaluation.get("better_answer"):
        text += f"\n\nCorrect answer: {evaluation['better_answer']}"
    if improvements:
        text += f"\n\nTo make it even stronger, try to:\n{bullets(improvements)}"
    if evaluation.get("follow_up_question"):
        text += f"\n\nBefore we continue, think about this: {evaluation['follow_up_question']}"
    return text

def complete_interview():
    state = st.session_state
    report = ReportAgent(groq_client(), os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")).create_report(state["records"])
    average = sum(r["score"] for r in state["records"]) / len(state["records"])
    finalize_interview(state["interview_id"], average, report["readiness_score"])
    state["report"], state["stage"] = report, "report"

def chat_page():
    state = st.session_state
    st.title("Python Interview Chat")
    st.caption(f"{state['name']} · {state['interview_type']} · {state['index'] + 1}/{state['total']}")
    st.progress(state["index"] / state["total"])
    for message in state["messages"]:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    answer = st.chat_input("Type your answer, explanation, or Python code…")
    if not answer: return
    question = state["current"]
    state["messages"].append({"role":"user", "content":answer})
    with st.chat_message("user"): st.markdown(answer)
    with st.chat_message("assistant"):
        with st.spinner("Reviewing your answer…"):
            evaluation = EvaluationAgent(groq_client(), os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")).evaluate(question, answer)
        response = feedback_message(evaluation); st.markdown(response)
    state["messages"].append({"role":"assistant", "content":response})
    save_answer(state["question_id"], answer, evaluation)
    state["records"].append({"question":question, "answer":answer, "score":evaluation["score"], "category":question["category"], "evaluation":evaluation})
    state["index"] += 1
    if state["index"] >= state["total"]: complete_interview(); st.rerun()
    if state["difficulty"] == "Adaptive": state["current_difficulty"] = adaptive_difficulty(state["current_difficulty"], [r["score"] for r in state["records"]])
    ask_next_question(); st.rerun()

def report_page():
    state, report = st.session_state, st.session_state["report"]
    st.title("Interview Completed"); st.write(f"**{state['name']}** · {state['experience']} · {state['interview_type']}")
    st.metric("Questions completed", len(state["records"]))
    st.subheader("Your interview summary")
    st.write(report["summary"]); st.subheader("Python Skill Breakdown"); st.bar_chart(report["skill_breakdown"])
    left, right = st.columns(2)
    with left: st.markdown("**Strengths**"); st.markdown(bullets(report["strengths"]))
    with right: st.markdown("**Weaknesses**"); st.markdown(bullets(report["weaknesses"]))
    st.markdown("**Recommended practice**"); st.markdown(bullets(report["recommended_practice"]))
    if st.button("Start a New Chat Interview", type="primary"): st.session_state.clear(); st.rerun()

def dashboard_page():
    st.title("Dashboard"); metrics = dashboard_metrics()
    labels = ["Total Interviews", "Average Score", "Best Score", "Latest Score", "Interview Readiness"]
    values = [metrics["total"], f"{metrics['average']:.1f}/10", f"{metrics['best']:.1f}/10", f"{metrics['latest']:.1f}/10", f"{metrics['readiness']:.1f}%"]
    for column, label, value in zip(st.columns(5), labels, values): column.metric(label, value)
    st.info(f"Performance trend: {metrics['trend']}")

def history_page():
    st.title("Interview History"); history = interview_history()
    if history: st.dataframe(history, use_container_width=True, hide_index=True)
    else: st.info("No completed interviews yet.")

initialize_state()
page = st.sidebar.radio("Navigate", ["Interview Chat", "Dashboard", "Interview History"])
if page == "Dashboard": dashboard_page()
elif page == "Interview History": history_page()
elif st.session_state["stage"] == "setup": setup_page()
elif st.session_state["stage"] == "chat": chat_page()
else: report_page()
