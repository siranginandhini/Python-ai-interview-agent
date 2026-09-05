def generate_feedback(scores):
    """
    scores example:
    {
        "technical": 8,
        "communication": 7,
        "problem_solving": 6
    }
    """

    total = sum(scores.values())
    maximum = len(scores) * 10
    percentage = (total / maximum) * 100

    strengths = []
    improvements = []

    for skill, score in scores.items():
        if score >= 8:
            strengths.append(skill)
        elif score <= 6:
            improvements.append(skill)

    feedback = {
        "total_score": total,
        "percentage": round(percentage, 2),
        "strengths": strengths,
        "areas_to_improve": improvements
    }

    return feedback