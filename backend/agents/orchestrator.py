"""
Orchestrator for BerkeleyBites Multi-Agent System

A coordinating agent that calls specialized sub-agents as tools
to provide personalized food recommendations.

Now integrates HybridRetriever for deterministic scoring before LLM calls.
"""

import os
import re
import logging
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

# Import all agent tools
from .mood_agent import get_user_mood, set_user_mood
from .food_availability_agent import get_available_dishes, get_menu_summary, set_menu_data
from .taste_preferences_agent import get_taste_preferences, get_similar_liked_dishes, set_feedback_data

# Import hybrid retriever components
from .hybrid_retriever import HybridRetriever, get_retriever, RetrieverConfig
from .scoring import UserContext, DishScore

logger = logging.getLogger(__name__)

# Global state
_user_profile: Optional[dict] = None
_user_id: Optional[str] = None
_message_stores: dict[str, InMemoryChatMessageHistory] = {}

# Hybrid retriever config
_use_hybrid_retriever: bool = True  # Feature flag

# LLM instance (lazy loaded)
_llm = None


def get_llm():
    """Get or create the LLM instance."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="sonar",
            temperature=0.7,
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai",
        )
    return _llm


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create message history for a session."""
    if session_id not in _message_stores:
        _message_stores[session_id] = InMemoryChatMessageHistory()
    return _message_stores[session_id]


def set_orchestrator_context(
    menu_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    user_profile: dict,
    user_id: str,
    user_mood: str = "happy"
) -> None:
    """
    Set the context for all agents.

    Args:
        menu_df: Today's menu DataFrame (already filtered by dietary restrictions)
        feedback_df: User feedback history DataFrame
        user_profile: User's dietary profile dictionary
        user_id: User's session ID
        user_mood: User's current mood
    """
    global _user_profile, _user_id
    _user_profile = user_profile
    _user_id = user_id

    # Set context for each agent
    set_menu_data(menu_df)
    set_feedback_data(feedback_df, user_id, menu_df)
    set_user_mood(user_mood)


def get_user_profile_str() -> str:
    """Get the user's dietary restrictions as a string."""
    if _user_profile is None:
        return "No dietary restrictions"

    profile = _user_profile
    restrictions = []

    if profile.get("is_vegan"):
        restrictions.append("VEGAN")
    elif profile.get("is_vegetarian"):
        restrictions.append("VEGETARIAN")
    elif profile.get("is_pescatarian"):
        restrictions.append("PESCATARIAN")

    if profile.get("is_halal"):
        restrictions.append("HALAL")
    if profile.get("is_kosher"):
        restrictions.append("KOSHER")

    allergens = []
    if profile.get("avoid_milk"):
        allergens.append("dairy")
    if profile.get("avoid_eggs"):
        allergens.append("eggs")
    if profile.get("avoid_gluten"):
        allergens.append("gluten")
    if profile.get("avoid_nuts"):
        allergens.append("nuts")
    if profile.get("avoid_soy"):
        allergens.append("soy")

    if allergens:
        restrictions.append(f"Avoids: {', '.join(allergens)}")

    return ", ".join(restrictions) if restrictions else "No dietary restrictions"


def gather_agent_context(meal: str = "") -> dict:
    """
    Call all sub-agents to gather context for recommendations.

    Returns:
        Dictionary with context from each agent.
    """
    context = {}

    # 1. Get user mood
    try:
        context["mood"] = get_user_mood.invoke({})
    except Exception as e:
        context["mood"] = f"Error getting mood: {e}"

    # 2. Get taste preferences
    try:
        context["preferences"] = get_taste_preferences.invoke({})
    except Exception as e:
        context["preferences"] = f"Error getting preferences: {e}"

    # 3. Get available dishes
    try:
        context["dishes"] = get_available_dishes.invoke({
            "meal_period": meal,
            "limit": 20
        })
    except Exception as e:
        context["dishes"] = f"Error getting dishes: {e}"

    return context


def get_agent_summaries(context: dict, meal: str = "", question_context: Optional[dict] = None) -> dict:
    """
    Extract medium-detail summaries from each agent's output.

    Args:
        context: Dictionary from gather_agent_context()
        meal: Optional meal period filter
        question_context: Optional context from user's question answers

    Returns:
        Dictionary with structured summaries for each agent.
    """
    summaries = {}
    qc = question_context or {}

    # Mood Summary - use question answer if available
    mood_value = qc.get("mood", "")
    mood_text = context.get("mood", "")

    mood_points = []
    mood_to_check = mood_value.lower() if mood_value else mood_text.lower()

    if "happy" in mood_to_check:
        mood_points = ["You're feeling happy today", "Great time to try something new!"]
    elif "grumpy" in mood_to_check:
        mood_points = ["You're feeling a bit grumpy", "Comfort food might help lift your spirits"]
    elif "stressed" in mood_to_check:
        mood_points = ["You're feeling stressed", "Something warm and soothing could help"]
    elif "tired" in mood_to_check:
        mood_points = ["You're feeling tired", "Energy-boosting foods recommended"]
    elif "adventurous" in mood_to_check:
        mood_points = ["You're feeling adventurous!", "Perfect day to explore new cuisines"]
    else:
        mood_points = [mood_text[:100] if mood_text else "Mood not detected"]

    summaries["mood"] = {
        "icon": "😊",
        "title": "Mood Analysis",
        "points": mood_points
    }

    # Craving Summary - from question answers
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

    # Spice Summary - from question answers
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

    # Time Summary - from question answers
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

    # Preferences Summary - Parse the taste preferences output for specific data
    pref_text = context.get("preferences", "")
    pref_points = []

    # Check for new user or limited history
    if "no feedback history" in pref_text.lower() or "new user" in pref_text.lower():
        pref_points = ["New user - no taste history yet", "Rate dishes to personalize recommendations!"]
    elif "limited feedback" in pref_text.lower():
        pref_points = ["Building taste profile", "Rate more dishes for better recommendations"]
    else:
        # Extract specific data from preferences
        # Look for rating count
        rating_match = re.search(r'based on (\d+) ratings', pref_text.lower())
        if rating_match:
            rating_count = rating_match.group(1)
            pref_points.append(f"Analyzed {rating_count} of your past ratings")

        # Look for liked count
        liked_match = re.search(r'liked dishes \((\d+)\)', pref_text.lower())
        if liked_match:
            liked_count = liked_match.group(1)
            pref_points.append(f"You've liked {liked_count} dishes")

        # Look for preferred categories
        cat_match = re.search(r'preferred categories.*?:\s*\n(.*?)(?:\n\n|$)', pref_text, re.IGNORECASE | re.DOTALL)
        if cat_match:
            cat_text = cat_match.group(1).strip()
            # Extract first category
            first_cat = re.search(r'-\s*([^:]+):', cat_text)
            if first_cat:
                pref_points.append(f"Favorite: {first_cat.group(1).strip()}")

        # Look for like ratio
        ratio_match = re.search(r'like rate:\s*(\d+)%', pref_text.lower())
        if ratio_match:
            ratio = int(ratio_match.group(1))
            if ratio > 70:
                pref_points.append("Generally positive about dining food")
            elif ratio < 30:
                pref_points.append("Selective eater - prioritizing top picks")

    if not pref_points:
        # Fallback: extract liked dishes/categories
        lines = pref_text.split('\n')
        for line in lines[:3]:
            if line.strip():
                pref_points.append(line.strip()[:60])
    elif "no history" in pref_text.lower() or "no feedback" in pref_text.lower():
        pref_points = ["No taste history yet", "Rate dishes to get personalized recommendations"]
    else:
        pref_points = [pref_text[:80] if pref_text else "Building your taste profile"]

    if not pref_points:
        pref_points = ["Analyzing your preferences", "Rate dishes to improve recommendations"]

    summaries["preferences"] = {
        "icon": "📊",
        "title": "Your Preferences",
        "points": pref_points[:3]
    }

    # Menu Summary
    dishes_text = context.get("dishes", "")
    menu_points = []
    if "dishes available" in dishes_text.lower() or "found" in dishes_text.lower():
        # Count dishes and halls
        count_match = re.search(r'(\d+)\s*dishes', dishes_text.lower())
        dish_count = count_match.group(1) if count_match else "Multiple"

        # Extract dining halls
        halls = []
        for hall in ["Crossroads", "Cafe 3", "Clark Kerr", "Foothill"]:
            if hall.lower() in dishes_text.lower():
                halls.append(hall)

        menu_points.append(f"Found {dish_count} dishes matching your profile")
        if halls:
            menu_points.append(f"Available at: {', '.join(halls[:3])}")
        if meal:
            menu_points.append(f"Filtered for {meal}")
    else:
        menu_points = [dishes_text[:80] if dishes_text else "Scanning today's menu"]

    if not menu_points:
        menu_points = ["Scanning available options"]

    summaries["menu"] = {
        "icon": "📋",
        "title": "Menu Scan",
        "points": menu_points[:3]
    }

    return summaries


def build_recommendation_prompt(context: dict, meal: str = "", question_context: Optional[dict] = None) -> str:
    """Build a comprehensive prompt with all agent context."""
    qc = question_context or {}

    # Build additional context from questions
    extra_context = ""
    if qc:
        extra_lines = []
        if qc.get("mood"):
            extra_lines.append(f"- Current mood: {qc['mood']}")
        if qc.get("craving"):
            craving_desc = {
                "comfort": "comfort food (warm, hearty dishes)",
                "healthy": "something healthy (fresh, nutritious)",
                "quick": "a quick bite (fast, convenient)",
                "filling": "a big filling meal (substantial portions)",
            }
            extra_lines.append(f"- Craving: {craving_desc.get(qc['craving'], qc['craving'])}")
        if qc.get("spice_level"):
            spice_desc = {
                "mild": "mild (no spice)",
                "medium": "medium (some kick)",
                "spicy": "spicy (bring the heat)",
            }
            extra_lines.append(f"- Spice preference: {spice_desc.get(qc['spice_level'], qc['spice_level'])}")
        if qc.get("time_constraint"):
            time_desc = {
                "rush": "in a rush (need quick options)",
                "normal": "normal mealtime",
                "leisurely": "taking their time (can sit down)",
            }
            extra_lines.append(f"- Time available: {time_desc.get(qc['time_constraint'], qc['time_constraint'])}")

        if extra_lines:
            extra_context = "\n## User's Current Preferences (from questions)\n" + "\n".join(extra_lines)

    prompt = f"""You are BerkeleyBites AI, a personalized food recommendation assistant for UC Berkeley dining halls.

CRITICAL RULES:
- ONLY recommend dishes from the "Available Dishes" list below
- NEVER search the web or use external information
- NEVER include dates, times, or timestamps in your response
- NEVER mention dishes that aren't in the provided list
- If a dish isn't in the list, it's not available - don't recommend it

I've gathered the following information to help you make personalized recommendations:

## User's Dietary Profile
{get_user_profile_str()}

## User's Current Mood
{context.get('mood', 'Unknown')}
{extra_context}

## User's Taste Preferences & History
{context.get('preferences', 'No history available')}

## Available Dishes{f' for {meal}' if meal else ''}
{context.get('dishes', 'No dishes available')}

## Your Task
Based on ALL the information above, recommend 2-4 specific dishes that would be perfect for this user right now. Consider:
1. Their mood and what foods suit that emotional state
2. Their specific cravings and food preferences they just told you
3. Their past preferences and ratings history
4. Their dietary restrictions (these are already filtered in the dish list)
5. Their time constraints (if in a rush, prioritize quick options)

For each recommendation:
- Name the specific dish
- Explain briefly why it's a good match (mood, craving, taste, or combination)
- Mention where to find it (dining hall and meal)

Be concise, friendly, and helpful. Use markdown formatting."""

    return prompt


def get_recommendation(
    query: str,
    meal: str = "",
    session_id: str = "default",
    question_context: Optional[dict] = None
) -> dict:
    """
    Get a food recommendation using the multi-agent system.

    This orchestrator:
    1. Calls the mood agent to understand emotional state
    2. Calls the preferences agent to understand taste history
    3. Calls the food availability agent to get menu options
    4. Combines all context and asks the LLM to make recommendations

    With hybrid retriever enabled:
    1. Uses HybridRetriever for deterministic pre-scoring
    2. Passes top-scored dishes to LLM for final selection
    3. Returns scored recommendations with explanations

    Args:
        query: The user's request (e.g., "recommend lunch")
        meal: Optional meal period filter
        session_id: Session ID for conversation history
        question_context: Optional context from user's question answers
            (mood, craving, spice_level, time_constraint)

    Returns:
        Dictionary with agent_summaries and recommendation.
    """
    history = get_session_history(session_id)
    llm = get_llm()

    try:
        # Gather context from all sub-agents (for summaries)
        context = gather_agent_context(meal)

        # Extract summaries for UI display
        summaries = get_agent_summaries(context, meal, question_context)

        # Try hybrid retriever first (if enabled)
        if _use_hybrid_retriever:
            try:
                result = _get_hybrid_recommendation(
                    meal=meal,
                    question_context=question_context,
                    context=context,
                    summaries=summaries
                )
                if result:
                    # Update history
                    history.add_user_message(query)
                    history.add_ai_message(result["recommendation"])
                    return result
            except Exception as e:
                logger.warning(f"Hybrid retriever failed, falling back to legacy: {e}")

        # Fallback: Legacy LLM-only approach
        return _get_legacy_recommendation(
            query=query,
            meal=meal,
            context=context,
            summaries=summaries,
            question_context=question_context,
            history=history,
            llm=llm
        )

    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            error_response = "The AI service is currently busy. Please try again in a moment."
        else:
            error_response = f"Error generating recommendation: {error_msg}"

        # Return error with empty summaries
        return {
            "agent_summaries": {},
            "recommendation": error_response
        }


def _get_hybrid_recommendation(
    meal: str,
    question_context: Optional[dict],
    context: dict,
    summaries: dict
) -> Optional[dict]:
    """
    Get recommendation using hybrid retriever.

    Returns:
        Dict with agent_summaries and recommendation, or None if failed
    """
    global _user_id, _user_profile

    if not _user_id:
        return None

    qc = question_context or {}

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
    recommendation_text = _format_hybrid_recommendations(
        recommendations=recommendations,
        user_context=user_context,
        stats=stats
    )

    # Add retrieval stats to summaries
    if stats:
        summaries["retrieval"] = {
            "icon": "⚡",
            "title": "Smart Matching",
            "points": [
                f"Analyzed {stats.get('stage1_count', 0)} dishes",
                f"Personalization scoring applied",
                f"Retrieved in {stats.get('total_ms', 0):.0f}ms"
            ]
        }

    return {
        "agent_summaries": summaries,
        "recommendation": recommendation_text,
        "top_scores": [_score_to_dict(s) for s in top_scores[:5]],
        "stats": stats
    }


def _format_hybrid_recommendations(
    recommendations: list[dict],
    user_context: UserContext,
    stats: dict
) -> str:
    """Format hybrid recommendations as markdown."""
    if not recommendations:
        return "I couldn't find dishes matching your preferences right now. Try adjusting your criteria."

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


def _get_legacy_recommendation(
    query: str,
    meal: str,
    context: dict,
    summaries: dict,
    question_context: Optional[dict],
    history,
    llm
) -> dict:
    """
    Legacy LLM-only recommendation (fallback).
    """
    # Build the comprehensive prompt with question context
    system_prompt = build_recommendation_prompt(context, meal, question_context)

    # Build messages
    messages = [SystemMessage(content=system_prompt)]

    # Add conversation history (last 4 messages max)
    for msg in history.messages[-4:]:
        messages.append(msg)

    # Add current request
    if meal:
        user_message = f"Please recommend food for {meal}."
    else:
        user_message = "Please recommend food for whatever meal is currently available."
    messages.append(HumanMessage(content=user_message))

    # Get response from LLM
    response = llm.invoke(messages)
    response_text = response.content

    # Update history
    history.add_user_message(query)
    history.add_ai_message(response_text)

    return {
        "agent_summaries": summaries,
        "recommendation": response_text
    }


def clear_orchestrator_history(session_id: str) -> None:
    """Clear the conversation history for a session."""
    if session_id in _message_stores:
        _message_stores[session_id].clear()
