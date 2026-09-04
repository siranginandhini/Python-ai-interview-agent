from __future__ import annotations
from typing import Any
from utils.helpers import extract_json, normalize_difficulty
from utils.prompts import QUESTION_PROMPT

FALLBACK = [
 {"question":"Explain the difference between a Python list and tuple. When would you choose each?","category":"Python Fundamentals","difficulty":"Easy","question_type":"theory","starter_code":""},
 {"question":"What is the difference between shallow copy and deep copy in Python? When would each be useful?","category":"Python Fundamentals","difficulty":"Easy","question_type":"theory","starter_code":""},
 {"question":"Write a function that returns the first non-repeating character in a string, or None.","category":"DSA","difficulty":"Medium","question_type":"coding","starter_code":"def first_non_repeating(text: str) -> str | None:\n    pass"},
 {"question":"What is a decorator in Python? Explain a practical use case and functools.wraps.","category":"Advanced Python","difficulty":"Medium","question_type":"theory","starter_code":""},
 {"question":"Write a function that finds the length of the longest substring without repeated characters.","category":"DSA","difficulty":"Hard","question_type":"coding","starter_code":"def longest_unique_substring_length(text: str) -> int:\n    pass"},
 {"question":"How would you handle errors and transactions in a Python REST API database write?","category":"Backend","difficulty":"Medium","question_type":"theory","starter_code":""},
 {"question":"Describe Python's garbage collection and when you would use weakref or context managers.","category":"Advanced Python","difficulty":"Hard","question_type":"theory","starter_code":""},
 {"question":"How would you optimize a query that joins two large tables and filters on a non-indexed column?","category":"SQL","difficulty":"Medium","question_type":"theory","starter_code":""},
 {"question":"Write a function to detect if a string is a palindrome ignoring spaces and punctuation.","category":"DSA","difficulty":"Easy","question_type":"coding","starter_code":"def is_palindrome_ignoring_punctuation(text: str) -> bool:\n    pass"},
 {"question":"Explain Python's MRO and when method resolution order matters in multiple inheritance.","category":"OOP","difficulty":"Hard","question_type":"theory","starter_code":""},
 {"question":"How do you structure a Python backend service to keep API requests idempotent and safe under retries?","category":"Backend","difficulty":"Hard","question_type":"theory","starter_code":""},
 {"question":"Write a function to merge two sorted lists into one sorted list without using built-in sort.","category":"DSA","difficulty":"Medium","question_type":"coding","starter_code":"def merge_sorted(a: list[int], b: list[int]) -> list[int]:\n    pass"},
]

class InterviewAgent:
 def __init__(self, client: Any | None = None, model: str = "llama-3.3-70b-versatile"):
  self.client, self.model = client, model
 def generate_question(self, experience_level: str, interview_type: str, difficulty: str, previous: list[str]) -> dict[str, Any]:
  if self.client:
   try:
    prompt = QUESTION_PROMPT.format(experience_level=experience_level, interview_type=interview_type, difficulty=difficulty, previous_questions=" | ".join(previous[-8:]) or "None")
    response = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=.7, response_format={"type":"json_object"})
    item = extract_json(response.choices[0].message.content or "")
    if item.get("question"):
     item.update({"difficulty": normalize_difficulty(item.get("difficulty", difficulty)), "question_type": "coding" if item.get("question_type") == "coding" else "theory"})
     item.setdefault("category", "Python Fundamentals"); item.setdefault("starter_code", "")
     return item
   except Exception: pass
  fallback = [q for q in FALLBACK if q["question"] not in previous]
  interview_type_l = (interview_type or "").lower()
  relevant = []
  if "dsa" in interview_type_l:
   relevant.extend(q for q in fallback if "DSA" in q["category"] or "substring" in q["question"].lower() or "palindrome" in q["question"].lower())
  if "sql" in interview_type_l:
   relevant.extend(q for q in fallback if "SQL" in q["category"])
  if "backend" in interview_type_l or "full stack" in interview_type_l:
   relevant.extend(q for q in fallback if "Backend" in q["category"] or "SQL" in q["category"])
  if "advanced" in interview_type_l:
   relevant.extend(q for q in fallback if "Advanced" in q["category"] or "OOP" in q["category"] or "decorator" in q["question"].lower())
  if "fundamental" in interview_type_l or "python" in interview_type_l:
   relevant.extend(q for q in fallback if "Python Fundamentals" in q["category"] or "OOP" in q["category"])
  candidates = (relevant or fallback)
  same = [q for q in candidates if q["difficulty"] == difficulty]
  return (same or candidates or FALLBACK)[0].copy()
