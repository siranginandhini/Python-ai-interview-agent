from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import Any
DB_PATH = Path(__file__).resolve().parent / "interviews.db"
def connection() -> sqlite3.Connection:
 conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; conn.execute("PRAGMA foreign_keys=ON"); return conn
def initialize_database() -> None:
 with connection() as conn: conn.executescript('''CREATE TABLE IF NOT EXISTS candidates(id INTEGER PRIMARY KEY,name TEXT NOT NULL,experience_level TEXT NOT NULL); CREATE TABLE IF NOT EXISTS interviews(id INTEGER PRIMARY KEY,candidate_id INTEGER NOT NULL,interview_type TEXT NOT NULL,difficulty TEXT NOT NULL,total_questions INTEGER NOT NULL,average_score REAL,readiness_score REAL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(candidate_id) REFERENCES candidates(id)); CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY,interview_id INTEGER NOT NULL,question TEXT NOT NULL,category TEXT NOT NULL,difficulty TEXT NOT NULL,question_type TEXT NOT NULL DEFAULT 'theory',FOREIGN KEY(interview_id) REFERENCES interviews(id)); CREATE TABLE IF NOT EXISTS answers(id INTEGER PRIMARY KEY,question_id INTEGER NOT NULL,answer TEXT NOT NULL,score REAL NOT NULL,feedback TEXT,better_answer TEXT,evaluation_json TEXT,FOREIGN KEY(question_id) REFERENCES questions(id));''')
def create_candidate(name: str, level: str) -> int:
 with connection() as conn: return conn.execute("INSERT INTO candidates(name,experience_level) VALUES(?,?)",(name,level)).lastrowid
def create_interview(candidate_id: int, kind: str, difficulty: str, total: int) -> int:
 with connection() as conn: return conn.execute("INSERT INTO interviews(candidate_id,interview_type,difficulty,total_questions) VALUES(?,?,?,?)",(candidate_id,kind,difficulty,total)).lastrowid
def save_question(interview_id: int, q: dict[str,Any]) -> int:
 with connection() as conn: return conn.execute("INSERT INTO questions(interview_id,question,category,difficulty,question_type) VALUES(?,?,?,?,?)",(interview_id,q["question"],q.get("category","Python Fundamentals"),q.get("difficulty","Medium"),q.get("question_type","theory"))).lastrowid
def save_answer(question_id: int, answer: str, evaluation: dict[str,Any]) -> None:
 with connection() as conn: conn.execute("INSERT INTO answers(question_id,answer,score,feedback,better_answer,evaluation_json) VALUES(?,?,?,?,?,?)",(question_id,answer,evaluation["score"],evaluation["feedback"],evaluation["better_answer"],json.dumps(evaluation)))
def finalize_interview(interview_id: int, average: float, readiness: float) -> None:
 with connection() as conn: conn.execute("UPDATE interviews SET average_score=?,readiness_score=? WHERE id=?",(average,readiness,interview_id))
def interview_history() -> list[dict[str,Any]]:
 with connection() as conn: rows=conn.execute("SELECT i.id,i.created_at,c.name,c.experience_level,i.interview_type,i.total_questions,i.average_score,i.readiness_score FROM interviews i JOIN candidates c ON c.id=i.candidate_id ORDER BY i.created_at DESC").fetchall()
 return [dict(x) for x in rows]
def dashboard_metrics() -> dict[str,Any]:
 items=[x for x in interview_history() if x["average_score"] is not None]; scores=[float(x["average_score"]) for x in items]; trend="No completed interviews yet"
 if len(scores)>1: trend="Improving" if scores[0]-scores[1]>.3 else "Declining" if scores[0]-scores[1]<-.3 else "Stable"
 return {"total":len(items),"average":sum(scores)/len(scores) if scores else 0,"best":max(scores) if scores else 0,"latest":scores[0] if scores else 0,"readiness":float(items[0]["readiness_score"] or 0) if items else 0,"trend":trend}
