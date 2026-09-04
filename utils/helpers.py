from __future__ import annotations

import json
import re
from typing import Any

DIFFICULTIES = ("Easy", "Medium", "Hard")
##helper funtcions git checking

def extract_json(content: str) -> dict[str, Any]:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.I)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object returned")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("JSON response is not an object")
    return value


def score_value(value: Any, default: float = 0.0) -> float:
    try:
        return round(max(0.0, min(10.0, float(value))), 1)
    except (ValueError, TypeError):
        return default


def listify(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [value.strip()] if isinstance(value, str) and value.strip() else []


def text_value(value: Any, default: str = "") -> str:
    return str(value).strip() if value is not None and str(value).strip() else default


def normalize_difficulty(value: Any) -> str:
    value = str(value or "").title()
    return value if value in DIFFICULTIES else "Medium"


def adaptive_difficulty(current: str, scores: list[float]) -> str:
    if len(scores) < 2:
        return current
    position = list(DIFFICULTIES).index(current) if current in DIFFICULTIES else 1
    recent = sum(scores[-2:]) / 2
    if recent >= 8:
        position = min(2, position + 1)
    elif recent <= 4.5:
        position = max(0, position - 1)
    return DIFFICULTIES[position]


def normalize_evaluation(raw: dict[str, Any], coding: bool = False) -> dict[str, Any]:
    result = {key: score_value(raw.get(key)) for key in ("score", "technical_accuracy", "relevance", "completeness", "clarity")}
    score = result.get("score", 0.0)
    if score >= 7.0:
        verdict = "Correct"
    elif score >= 4.0:
        verdict = "Partially correct"
    else:
        verdict = "Incorrect"
    result.update({"strengths": listify(raw.get("strengths")), "missing_points": listify(raw.get("missing_points")), "areas_to_improve": listify(raw.get("areas_to_improve")), "feedback": text_value(raw.get("feedback"), "No detailed feedback returned."), "better_answer": text_value(raw.get("better_answer"), "No ideal answer returned."), "difficulty_recommendation": normalize_difficulty(raw.get("difficulty_recommendation")), "follow_up_question": text_value(raw.get("follow_up_question")), "verdict": verdict})
    if coding:
        review = raw.get("code_review") if isinstance(raw.get("code_review"), dict) else {}
        result["code_review"] = {key: text_value(review.get(key), "Not assessed.") for key in ("correctness", "code_quality", "efficiency", "time_complexity", "space_complexity", "python_best_practices")}
    return result
