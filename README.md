# Python Developer AI Interview Agent

Practice Python developer interviews with an AI interviewer and improve technical skills. The app runs structured theory and coding interviews, evaluates each response, adapts difficulty, stores results in SQLite, and creates a final readiness report.

## Features

- Candidate setup with experience, interview type, difficulty, and question count
- Three focused modules: `InterviewAgent` generates non-repeated questions; `EvaluationAgent` scores explanations and statically reviews code; `ReportAgent` summarizes performance
- Groq API integration, with JSON validation and safe offline fallbacks
- Coding editor; candidate code is **never executed** on the host
- Adaptive difficulty based on the most recent two scores
- SQLite-backed interview history and dashboard trends

## Architecture

`app.py` coordinates Streamlit state and navigation. `agents/` owns AI prompts and responses, `database/` persists candidates/interviews/questions/answers, and `utils/` validates structured model JSON.

## Setup and run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set a fresh key:

```text
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Run the app:

```bash
streamlit run app.py
```

The key is intentionally excluded by `.gitignore`. If no key is configured, the full interview flow remains usable with clearly marked offline fallback feedback.

## Project structure

```text
app.py                 Streamlit UI and interview flow
agents/                Question, evaluation, and report agents
database/database.py   SQLite schema and queries
utils/                 Prompts and safe response helpers
```

## Database

SQLite is created automatically at `database/interviews.db` with `candidates`, `interviews`, `questions`, and `answers` tables. The database is ignored by Git.

## Git and GitHub workflow

Use `main` for stable releases, `develop` for integration, and short-lived `feature/...` branches. Before every commit, check `git status` and confirm `.env` is absent. After creating a GitHub repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/python-ai-interview-agent.git
git push -u origin main
git push -u origin develop
```

Suggested next enhancements: authentication, question rubrics curated by role, guarded container-based code execution, and exported PDF reports.
