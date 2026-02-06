"""
BerkeleyBites Recommendation Orchestrator

Coordinates the recommendation flow:
1. Collects user preferences via questions (mood, craving, spice, time)
2. Passes to HybridRetriever for 4-stage scoring pipeline
3. Returns personalized recommendations with explanations

The HybridRetriever handles all the heavy lifting:
- Stage 1: SQL filters (dietary safety)
- Stage 2: Vector search (semantic matching)
- Stage 3: Multi-factor scoring (mood, taste, craving weights)
- Stage 4: LLM picks top 3-4 with explanations
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_core.chat_history import InMemoryChatMessageHistory

from .hybrid_retriever import get_retriever
from .scoring import UserContext, DishScore

logger = logging.getLogger(__name__)

# Global state
_user_profile: Optional[dict] = None
_user_id: Optional[str] = None
_message_stores: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create message history for a session."""
    if session_id not in _message_stores:
        _message_stores[session_id] = InMemoryChatMessageHistory()
    return _message_stores[session_id]


def set_orchestrator_context(
    user_profile: dict,
    user_id: str,
    **kwargs  # Accept but ignore legacy parameters (menu_df, feedback_df, user_mood)
) -> None:
    """
    Set the user context for recommendations.

    Args:
        user_profile: User's dietary profile dictionary
        user_id: User's session ID
        **kwargs: Ignored (for backwards compatibility with main.py)
    """
    global _user_profile, _user_id
    _user_profile = user_profile
    _user_id = user_id


def get_recommendation(
    query: str,
    meal: str = "",
    session_id: str = "default",
    question_context: Optional[dict] = None
) -> dict:
    """
    Get a food recommendation using the hybrid retrieval pipeline.

    Flow:
    1. Build user context from question answers
    2. Call HybridRetriever.retrieve_recommendations()
    3. Format results with UI summaries

    Args:
        query: The user's request (e.g., "recommend lunch")
        meal: Meal period filter (auto-detected if empty)
        session_id: Session ID for conversation history
        question_context: Context from user's question answers
            (mood, craving, spice_level, time_constraint)

    Returns:
        Dictionary with agent_summaries and recommendation.
    """
    history = get_session_history(session_id)

    try:
        result = _get_recommendation(meal, question_context)

        if result:
            history.add_user_message(query)
            history.add_ai_message(result["recommendation"])
            return result

        # No results found
        return {
            "agent_summaries": _build_summaries(question_context or {}, meal),
            "recommendation": "I couldn't find dishes matching your preferences right now. The dining halls may be between meals or the menu hasn't been updated yet."
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Recommendation failed: {error_msg}")

        if "rate limit" in error_msg.lower():
            error_response = "The AI service is currently busy. Please try again in a moment."
        else:
            error_response = f"Error generating recommendation: {error_msg}"

        return {
            "agent_summaries": {},
            "recommendation": error_response
        }


def _get_recommendation(
    meal: str,
    question_context: Optional[dict]
) -> Optional[dict]:
    """
    Get recommendation using hybrid retriever.

    Returns:
        Dict with agent_summaries and recommendation, or None if no results
    """
    global _user_id, _user_profile

    if not _user_id:
        return None

    qc = question_context or {}

    # Build UI summaries from question answers
    summaries = _build_summaries(qc, meal)

    # Build user context for scoring
    user_context = UserContext(
        user_id=_user_id,
        mood=qc.get("mood"),
        craving=qc.get("craving"),
        spice_level=qc.get("spice_level"),
        time_constraint=qc.get("time_constraint"),
        meal_period=meal if meal else None
    )

    # Get recommendations from hybrid retriever
    retriever = get_retriever()
    result = retriever.retrieve_recommendations(
        user_id=_user_id,
        user_context=user_context,
        meal_period=meal if meal else None,
        user_profile=_user_profile
    )

    recommendations = result.get("recommendations", [])
    top_scores = result.get("top_scores", [])
    stats = result.get("stage_stats", {})

    if not recommendations:
        return None

    # Format recommendations as markdown
    recommendation_text = _format_recommendations(recommendations, user_context)

    # Add retrieval stats to summaries
    if stats:
        summaries["retrieval"] = {
            "icon": "⚡",
            "title": "Smart Matching",
            "points": [
                f"Analyzed {stats.get('stage1_count', 0)} dishes",
                "Personalization scoring applied",
                f"Retrieved in {stats.get('total_ms', 0):.0f}ms"
            ]
        }

    return {
        "agent_summaries": summaries,
        "recommendation": recommendation_text,
        "top_scores": [_score_to_dict(s) for s in top_scores[:5]],
        "stats": stats
    }


def _build_summaries(question_context: dict, meal: str = "") -> dict:
    """
    Build UI summaries from question answers.

    These are displayed as cards in the frontend to show the user
    what factors influenced their recommendations.
    """
    qc = question_context or {}
    summaries = {}

    # Mood Summary
    mood_value = qc.get("mood", "")
    mood_map = {
        "happy": ["You're feeling happy today", "Great time to try something new!"],
        "grumpy": ["You're feeling a bit grumpy", "Comfort food might help lift your spirits"],
        "stressed": ["You're feeling stressed", "Something warm and soothing could help"],
        "tired": ["You're feeling tired", "Energy-boosting foods recommended"],
        "adventurous": ["You're feeling adventurous!", "Perfect day to explore new cuisines"],
    }
    summaries["mood"] = {
        "icon": "😊",
        "title": "Mood Analysis",
        "points": mood_map.get(mood_value.lower(), ["Ready for a great meal"]) if mood_value else ["Ready for a great meal"]
    }

    # Craving Summary
    if qc.get("craving"):
        craving = qc["craving"]
        craving_map = {
            "comfort": ["Looking for comfort food", "Warm, hearty dishes preferred"],
            "healthy": ["Craving something healthy", "Fresh, nutritious options in mind"],
            "quick": ["Want a quick bite", "Fast, convenient options prioritized"],
            "filling": ["Hungry for a big meal", "Substantial portions needed"],
        }
        summaries["craving"] = {
            "icon": "🍽️",
            "title": "Food Craving",
            "points": craving_map.get(craving, [f"Craving: {craving}"])
        }

    # Spice Summary
    if qc.get("spice_level"):
        spice = qc["spice_level"]
        spice_map = {
            "mild": ["Keeping it mild today", "Gentle flavors preferred"],
            "medium": ["Open to some kick", "Moderate spice welcome"],
            "spicy": ["Bringing the heat!", "Spicy dishes preferred"],
        }
        summaries["spice"] = {
            "icon": "🌶️",
            "title": "Spice Level",
            "points": spice_map.get(spice, [f"Spice preference: {spice}"])
        }

    # Time Summary
    if qc.get("time_constraint"):
        time_val = qc["time_constraint"]
        time_map = {
            "rush": ["In a hurry", "Quick service spots prioritized"],
            "normal": ["Normal mealtime", "Standard dining options"],
            "leisurely": ["Taking your time", "Sit-down options work well"],
        }
        summaries["time"] = {
            "icon": "⏰",
            "title": "Time Available",
            "points": time_map.get(time_val, [f"Time: {time_val}"])
        }

    return summaries


def _format_recommendations(recommendations: list[dict], user_context: UserContext) -> str:
    """Format recommendations as markdown for display."""
    if not recommendations:
        return "I couldn't find dishes matching your preferences right now."

    lines = ["Here are my top picks for you:\n"]

    for i, rec in enumerate(recommendations, 1):
        dish_name = rec.get("dish_name", "Unknown")
        dining_hall = rec.get("dining_hall", "")
        explanation = rec.get("explanation", "")

        lines.append(f"### {i}. {dish_name}")
        lines.append(f"📍 **{dining_hall}**")
        if explanation:
            lines.append(f"\n{explanation}")
        lines.append("")

    # Add context-aware closing
    closing = _generate_closing(user_context)
    if closing:
        lines.append(closing)

    return "\n".join(lines)


def _generate_closing(user_context: UserContext) -> str:
    """Generate context-aware closing message."""
    parts = []

    if user_context.mood:
        mood_closings = {
            "happy": "Enjoy your meal! 🎉",
            "stressed": "Take a moment to enjoy your food and relax.",
            "tired": "Hope this gives you the energy boost you need!",
            "grumpy": "Hope this brightens your day!",
            "adventurous": "Have fun trying something new!"
        }
        if user_context.mood.lower() in mood_closings:
            parts.append(mood_closings[user_context.mood.lower()])

    if user_context.time_constraint == "rush":
        parts.append("These should be quick options for you!")

    return " ".join(parts) if parts else ""


def _score_to_dict(score: DishScore) -> dict:
    """Convert DishScore to dict for JSON serialization."""
    return {
        "dish_id": score.dish_id,
        "dish_name": score.dish_name,
        "dining_hall": score.dining_hall,
        "category": score.category,
        "total_score": score.total_score,
        "taste_score": score.taste_score,
        "craving_score": score.craving_score,
        "mood_score": score.mood_score,
        "is_liked": score.is_liked,
        "is_new": score.is_new
    }


def clear_orchestrator_history(session_id: str) -> None:
    """Clear the conversation history for a session."""
    if session_id in _message_stores:
        _message_stores[session_id].clear()
