from __future__ import annotations
from typing import Any
from utils.helpers import extract_json, normalize_evaluation
from utils.prompts import EVALUATION_PROMPT

class EvaluationAgent:
 def __init__(self, client: Any | None = None, model: str = "llama-3.3-70b-versatile"):
  self.client, self.model = client, model

 def _build_fallback_feedback(self, question: dict[str, Any], answer: str) -> dict[str, Any]:
  question_text = (question.get("question") or "").lower()
  answer_text = answer.lower()
  coding = question.get("question_type") == "coding"

  if "list" in question_text and "tuple" in question_text:
   score = 7 if ("mutable" in answer_text and "immutable" in answer_text) or ("list" in answer_text and "tuple" in answer_text) else 5
   raw = {"score": score, "technical_accuracy": score, "relevance": score, "completeness": max(0, score - 1), "clarity": score, "strengths": ["You identified the key trade-off between mutability and immutability."], "missing_points": ["Mention a concrete case where mutability matters, such as appending values or storing fixed configuration."], "areas_to_improve": ["Compare list operations like append and tuple use cases like fixed records.", "Explain performance or safety trade-offs.", "Mention how the choice affects API contracts and data integrity."], "feedback": "Good start. You captured the main distinction: lists are mutable and tuples are immutable, which affects when each is appropriate.", "better_answer": "A strong answer explains that lists are used when data changes, while tuples are better for fixed data and safe, hashable values.", "difficulty_recommendation": "easy", "follow_up_question": "When would you prefer a tuple for a configuration object or fixed record?"}
  elif "substring" in question_text or ("longest" in question_text and "repeated" in question_text):
   score = 7 if "sliding" in answer_text or "set" in answer_text or "window" in answer_text else 5
   raw = {"score": score, "technical_accuracy": score, "relevance": score, "completeness": max(0, score - 1), "clarity": score, "strengths": ["The core idea is the correct pattern for longest-unique-substring problems."], "missing_points": ["State the invariant for the window and how the left pointer moves."], "areas_to_improve": ["Explain why the window tracks unique characters.", "Describe the time and space complexity clearly.", "Call out edge cases like empty strings and repeated characters."], "feedback": "You are pointing in the right direction: the standard solution uses a sliding window and a set or map to track characters.", "better_answer": "A strong answer describes maintaining a window of unique characters, moving the left pointer when duplicates appear, and states O(n) time and O(k) space.", "difficulty_recommendation": "hard", "follow_up_question": "How would your approach behave on a string like 'abba' or an empty string?"}
  elif "decorator" in question_text:
   score = 7 if "wrapper" in answer_text or "functools" in answer_text or "@" in answer_text else 5
   raw = {"score": score, "technical_accuracy": score, "relevance": score, "completeness": max(0, score - 1), "clarity": score, "strengths": ["You recognized that decorators wrap functions and add behavior."], "missing_points": ["Explain how a decorator preserves metadata with functools.wraps and why that matters."], "areas_to_improve": ["Explain the execution flow around the wrapper function.", "Discuss a practical example such as logging or access control.", "Mention why functools.wraps is important for introspection."], "feedback": "Good explanation: decorators wrap functions to add behavior without changing their call sites.", "better_answer": "A strong answer explains a decorator as a higher-order function, shows a logging example, and mentions that functools.wraps preserves the wrapped function name and docstring.", "difficulty_recommendation": "medium", "follow_up_question": "What would happen if you did not use functools.wraps in a decorated API endpoint?"}
  elif "transaction" in question_text or "database" in question_text:
   score = 7 if ("commit" in answer_text and ("rollback" in answer_text or "try" in answer_text)) or "transaction" in answer_text else 5
   raw = {"score": score, "technical_accuracy": score, "relevance": score, "completeness": max(0, score - 1), "clarity": score, "strengths": ["You identified the need for safe write behavior in a backend API."], "missing_points": ["Explain transaction boundaries, rollback behavior, and retry-safe idempotency considerations."], "areas_to_improve": ["Discuss commit and rollback flow in a try/except block.", "Explain validation and duplicate request handling.", "Mention logging or dead-letter handling for failed writes."], "feedback": "Your answer is on the right track: safe writes need validation, transaction control, and error handling around the database action.", "better_answer": "A strong answer covers validation, database transaction boundaries, rollback on failure, and idempotent retries to avoid duplicate writes.", "difficulty_recommendation": "medium", "follow_up_question": "What would you do if the request reaches the database but the client times out?"}
  else:
   score = 6 if len(answer.strip()) >= 80 else 3
   raw = {"score": score, "technical_accuracy": score, "relevance": score, "completeness": max(0, score - 1), "clarity": score, "strengths": ["You attempted the question and gave a relevant explanation."], "missing_points": ["Add a concrete example or clarify the exact trade-offs in the concept you are explaining."], "areas_to_improve": ["Explain your assumptions and mention an edge case you would handle.", "Use a short example to make the answer concrete.", "State the trade-offs or constraints clearly."], "feedback": "Thanks for giving that a try. Your answer is relevant, and a stronger version would add a concrete example and the main trade-offs.", "better_answer": "A strong answer defines the concept, gives an example, discusses trade-offs, and covers edge cases.", "difficulty_recommendation": "medium", "follow_up_question": "What edge case would you test first?"}

  if coding:
   raw["code_review"] = {"correctness": "Check the core logic and edge cases before finalizing.", "code_quality": "Use clear names, keep functions small, and prefer readable logic.", "efficiency": "Explain the complexity and avoid unnecessary nested loops.", "time_complexity": "State your intended time complexity explicitly.", "space_complexity": "State your intended extra space usage explicitly.", "python_best_practices": "Use descriptive variable names, type hints, and a few focused tests."}
  return raw

 def evaluate(self, question: dict[str, Any], answer: str) -> dict[str, Any]:
  coding = question.get("question_type") == "coding"
  if self.client:
   try:
    prompt = EVALUATION_PROMPT.format(question=question["question"], category=question.get("category","Python"), question_type=question.get("question_type","theory"), answer=answer)
    response = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=.2, response_format={"type":"json_object"})
    return normalize_evaluation(extract_json(response.choices[0].message.content or ""), coding)
   except Exception: pass
  return normalize_evaluation(self._build_fallback_feedback(question, answer), coding)
