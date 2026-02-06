"""
Question Agent for BerkeleyBites

Handles the multi-turn questioning flow before generating recommendations.
Questions are asked fresh each time (no memory between recommendations).
"""

from typing import Optional

QUESTIONS = [
    {
        "id": "mood",
        "question_text": "How are you feeling right now?",
        "options": [
            {"value": "happy", "label": "Happy", "emoji": "😊"},
            {"value": "stressed", "label": "Stressed", "emoji": "😤"},
            {"value": "tired", "label": "Tired", "emoji": "😴"},
            {"value": "adventurous", "label": "Adventurous", "emoji": "🤠"},
            {"value": "grumpy", "label": "Grumpy", "emoji": "😠"},
        ]
    },
    {
        "id": "craving",
        "question_text": "What kind of food sounds good?",
        "options": [
            {"value": "comfort", "label": "Comfort Food", "emoji": "🍲"},
            {"value": "healthy", "label": "Something Healthy", "emoji": "🥗"},
            {"value": "quick", "label": "Quick Bite", "emoji": "🥪"},
            {"value": "filling", "label": "Big Filling Meal", "emoji": "🍛"},
        ]
    },
    {
        "id": "spice",
        "question_text": "How adventurous with spice today?",
        "options": [
            {"value": "mild", "label": "Keep it Mild", "emoji": "😌"},
            {"value": "medium", "label": "Some Kick", "emoji": "🌶️"},
            {"value": "spicy", "label": "Bring the Heat", "emoji": "🔥"},
        ]
    },
    {
        "id": "time",
        "question_text": "How much time do you have?",
        "options": [
            {"value": "rush", "label": "In a Rush", "emoji": "⚡"},
            {"value": "normal", "label": "Normal Meal", "emoji": "🍽️"},
            {"value": "leisurely", "label": "Taking My Time", "emoji": "☕"},
        ]
    },
]

QUESTION_ORDER = ["mood", "craving", "spice", "time"]


def get_next_question(answered: dict) -> Optional[dict]:
    """
    Get the next unanswered question, or None if all answered.

    Args:
        answered: Dictionary of question_id -> answer_value

    Returns:
        The next question dict, or None if all questions answered.
    """
    for q_id in QUESTION_ORDER:
        if q_id not in answered:
            return next(q for q in QUESTIONS if q["id"] == q_id)
    return None


def all_questions_answered(answered: dict) -> bool:
    """
    Check if all questions have been answered.

    Args:
        answered: Dictionary of question_id -> answer_value

    Returns:
        True if all questions in QUESTION_ORDER have answers.
    """
    return all(q_id in answered for q_id in QUESTION_ORDER)


def format_context_for_recommendation(answered: dict) -> dict:
    """
    Format the answered questions into context for the orchestrator.

    Args:
        answered: Dictionary of question_id -> answer_value

    Returns:
        Dictionary with formatted context for each category.
    """
    context = {}

    # Map mood answer to mood context
    if "mood" in answered:
        context["mood"] = answered["mood"]

    # Map craving answer to food type preference
    if "craving" in answered:
        context["craving"] = answered["craving"]

    # Map spice preference
    if "spice" in answered:
        context["spice_level"] = answered["spice"]

    # Map time constraint
    if "time" in answered:
        context["time_constraint"] = answered["time"]

    return context
