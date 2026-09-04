from agents.evaluation_agent import EvaluationAgent
from agents.interview_agent import InterviewAgent


def test_interview_agent_prefers_type_relevant_fallback_question():
    question = InterviewAgent().generate_question("3-5 Years", "Advanced Python", "Medium", [])
    assert "decorator" in question["question"].lower()


def test_evaluation_agent_feedback_is_specific_to_question():
    theory = EvaluationAgent().evaluate(
        {"question": "Explain the difference between a Python list and tuple. When would you choose each?", "question_type": "theory", "category": "Python Fundamentals"},
        "A list is mutable and a tuple is immutable; use a list when you need to change values.",
    )
    coding = EvaluationAgent().evaluate(
        {"question": "Write a function that finds the length of the longest substring without repeated characters.", "question_type": "coding", "category": "DSA"},
        "Use a sliding window and a hash set to track seen characters.",
    )

    assert "list" in theory["feedback"].lower() or "tuple" in theory["feedback"].lower()
    assert "sliding" in coding["feedback"].lower() or "substring" in coding["feedback"].lower()
