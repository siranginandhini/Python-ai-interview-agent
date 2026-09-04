from __future__ import annotations
from typing import Any
from utils.helpers import extract_json, listify, score_value
from utils.prompts import REPORT_PROMPT
SKILLS = ["Python Fundamentals","OOP","Advanced Python","DSA","SQL","Backend","Problem Solving"]
class ReportAgent:
 def __init__(self, client: Any | None = None, model: str = "llama-3.3-70b-versatile"):
  self.client, self.model = client, model
 def create_report(self, records: list[dict[str, Any]]) -> dict[str, Any]:
  average = sum(float(x["score"]) for x in records) / len(records) if records else 0
  raw: dict[str, Any] = {}
  if self.client:
   try:
    reply = self.client.chat.completions.create(model=self.model,messages=[{"role":"user","content":REPORT_PROMPT.format(records=records)}],temperature=.3,response_format={"type":"json_object"})
    raw = extract_json(reply.choices[0].message.content or "")
   except Exception: pass
  levels = [(8.5,"Excellent"),(7,"Very Good"),(5.5,"Good"),(4,"Average"),(0,"Needs Improvement")]
  performance = next(name for limit,name in levels if average >= limit)
  data = raw.get("skill_breakdown",{}) if isinstance(raw.get("skill_breakdown"),dict) else {}
  return {"overall_performance":raw.get("overall_performance",performance),"readiness_score":round(max(0,min(100,score_value(raw.get("readiness_score"),average*10))),1),"strengths":listify(raw.get("strengths")) or ["Completed a structured interview."],"weaknesses":listify(raw.get("weaknesses")) or ["Configure Groq for personal AI insights."],"recommended_practice":listify(raw.get("recommended_practice")) or ["Practice Python fundamentals, edge cases, and complexity."],"skill_breakdown":{s:score_value(data.get(s),0) for s in SKILLS},"summary":str(raw.get("summary") or "Report based on your recorded answers.")}
