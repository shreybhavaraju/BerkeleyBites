"""
Orchestrator for BerkeleyBites Multi-Agent System

A coordinating agent that calls specialized sub-agents as tools
to provide personalized food recommendations.
"""

import os
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

# Import all agent tools
from .mood_agent import get_user_mood, set_user_mood
from .temperature_agent import get_current_temperature
from .food_availability_agent import get_available_dishes, get_menu_summary, set_menu_data
from .taste_preferences_agent import get_taste_preferences, get_similar_liked_dishes, set_feedback_data

# Global state
_user_profile: Optional[dict] = None
_message_stores: dict[str, InMemoryChatMessageHistory] = {}

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
    global _user_profile
    _user_profile = user_profile

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

    # 2. Get current temperature/weather
    try:
        context["temperature"] = get_current_temperature.invoke({})
    except Exception as e:
        context["temperature"] = f"Error getting temperature: {e}"

    # 3. Get taste preferences
    try:
        context["preferences"] = get_taste_preferences.invoke({})
    except Exception as e:
        context["preferences"] = f"Error getting preferences: {e}"

    # 4. Get available dishes
    try:
        context["dishes"] = get_available_dishes.invoke({
            "meal_period": meal,
            "limit": 20
        })
    except Exception as e:
        context["dishes"] = f"Error getting dishes: {e}"

    return context


def build_recommendation_prompt(context: dict, meal: str = "") -> str:
    """Build a comprehensive prompt with all agent context."""

    prompt = f"""You are BerkeleyBites AI, a personalized food recommendation assistant for UC Berkeley dining halls.

I've gathered the following information to help you make personalized recommendations:

## User's Dietary Profile
{get_user_profile_str()}

## User's Current Mood
{context.get('mood', 'Unknown')}

## Current Weather
{context.get('temperature', 'Unknown')}

## User's Taste Preferences & History
{context.get('preferences', 'No history available')}

## Available Dishes{f' for {meal}' if meal else ''}
{context.get('dishes', 'No dishes available')}

## Your Task
Based on ALL the information above, recommend 2-4 specific dishes that would be perfect for this user right now. Consider:
1. Their mood and what foods suit that emotional state
2. The weather and temperature-appropriate food choices
3. Their past preferences and ratings history
4. Their dietary restrictions (these are already filtered in the dish list)

For each recommendation:
- Name the specific dish
- Explain briefly why it's a good match (mood, weather, taste, or combination)
- Mention where to find it (dining hall and meal)

Be concise, friendly, and helpful. Use markdown formatting."""

    return prompt


def get_recommendation(
    query: str,
    meal: str = "",
    session_id: str = "default"
) -> str:
    """
    Get a food recommendation using the multi-agent system.

    This orchestrator:
    1. Calls the mood agent to understand emotional state
    2. Calls the temperature agent to check weather
    3. Calls the preferences agent to understand taste history
    4. Calls the food availability agent to get menu options
    5. Combines all context and asks the LLM to make recommendations

    Args:
        query: The user's request (e.g., "recommend lunch")
        meal: Optional meal period filter
        session_id: Session ID for conversation history

    Returns:
        The recommendation response string.
    """
    history = get_session_history(session_id)
    llm = get_llm()

    try:
        # Gather context from all sub-agents
        context = gather_agent_context(meal)

        # Build the comprehensive prompt
        system_prompt = build_recommendation_prompt(context, meal)

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

        return response_text

    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            return "The AI service is currently busy. Please try again in a moment."
        return f"Error generating recommendation: {error_msg}"


def clear_orchestrator_history(session_id: str) -> None:
    """Clear the conversation history for a session."""
    if session_id in _message_stores:
        _message_stores[session_id].clear()
