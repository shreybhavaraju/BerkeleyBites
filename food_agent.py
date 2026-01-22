"""
BerkeleyBites Food Recommendation Agent

An LLM-powered assistant using Perplexity for personalized food recommendations.
Uses a simple prompt-based approach (no tool calling required).
"""

import os
import pandas as pd
from datetime import date
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

# ============================================
# GLOBAL STATE (set by Streamlit app)
# ============================================

_menu_df: Optional[pd.DataFrame] = None
_feedback_df: Optional[pd.DataFrame] = None
_user_profile: Optional[dict] = None
_user_id: Optional[str] = None
_session_preferences: dict = {}

# Memory store for conversation history
_message_stores: dict[str, InMemoryChatMessageHistory] = {}

# Minimum feedback count before we rely on historical data
MIN_FEEDBACK_FOR_RAG = 5

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


def set_context(menu_df: pd.DataFrame, feedback_df: pd.DataFrame,
                user_profile: dict, user_id: str):
    """Set the global context for the assistant."""
    global _menu_df, _feedback_df, _user_profile, _user_id
    _menu_df = menu_df
    _feedback_df = feedback_df
    _user_profile = user_profile
    _user_id = user_id


# ============================================
# CONTEXT GATHERING FUNCTIONS
# ============================================

def get_feedback_stats() -> str:
    """Get statistics about the user's feedback history."""
    if _feedback_df is None or _feedback_df.empty or _user_id is None:
        return "NEW USER: 0 ratings"

    user_feedback = _feedback_df[_feedback_df['user_id'] == _user_id]
    count = len(user_feedback)

    if count < MIN_FEEDBACK_FOR_RAG:
        return f"NEW USER: {count} ratings (need {MIN_FEEDBACK_FOR_RAG} for personalized recs)"
    else:
        liked = user_feedback['liked'].sum()
        disliked = count - liked
        return f"ESTABLISHED USER: {count} ratings ({liked} likes, {disliked} dislikes)"


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

    if not profile.get("is_vegetarian") and not profile.get("is_vegan"):
        avoided = []
        if not profile.get("eats_chicken", True):
            avoided.append("chicken")
        if not profile.get("eats_beef", True):
            avoided.append("beef")
        if not profile.get("eats_pork", True):
            avoided.append("pork")
        if not profile.get("eats_fish", True):
            avoided.append("fish")
        if avoided:
            restrictions.append(f"Avoids: {', '.join(avoided)}")

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
        restrictions.append(f"Allergens: {', '.join(allergens)}")

    return ", ".join(restrictions) if restrictions else "No dietary restrictions"


def get_feedback_history_str(limit: int = 10) -> str:
    """Get the user's food ratings history."""
    if _feedback_df is None or _feedback_df.empty or _user_id is None:
        return "No feedback history"

    user_feedback = _feedback_df[_feedback_df['user_id'] == _user_id].copy()

    if user_feedback.empty or len(user_feedback) < MIN_FEEDBACK_FOR_RAG:
        return "Not enough feedback history"

    user_feedback = user_feedback.sort_values('timestamp', ascending=False).head(limit)

    liked = user_feedback[user_feedback['liked'] == 1]['dish_name'].tolist()
    disliked = user_feedback[user_feedback['liked'] == 0]['dish_name'].tolist()

    result = []
    if liked:
        result.append(f"Liked: {', '.join(liked)}")
    if disliked:
        result.append(f"Disliked: {', '.join(disliked)}")

    return "; ".join(result) if result else "No feedback history"


def get_menu_str(meal: str = "") -> str:
    """Get today's menu as a string."""
    if _menu_df is None or _menu_df.empty:
        return "No menu available"

    df = _menu_df.copy()

    if meal:
        df = df[df['meal_period'].str.lower().str.contains(meal.lower())]

    if df.empty:
        return f"No dishes found for {meal}"

    result = []
    for hall in df['dining_hall'].unique():
        hall_df = df[df['dining_hall'] == hall]
        dishes = []
        for _, dish in hall_df.head(10).iterrows():
            tags = []
            if dish.get('is_vegan'):
                tags.append("vegan")
            elif dish.get('is_vegetarian'):
                tags.append("vegetarian")
            tag_str = f" ({', '.join(tags)})" if tags else ""
            dishes.append(f"{dish['dish_name']}{tag_str}")
        result.append(f"{hall}: {', '.join(dishes)}")

    return "\n".join(result)


def get_session_prefs_str() -> str:
    """Get session preferences as a string."""
    if not _session_preferences:
        return "None"
    prefs = []
    for k, v in _session_preferences.items():
        prefs.append(f"{k.replace('_', ' ')}: {v}")
    return ", ".join(prefs)


# ============================================
# SESSION MANAGEMENT
# ============================================

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create message history for a session."""
    if session_id not in _message_stores:
        _message_stores[session_id] = InMemoryChatMessageHistory()
    return _message_stores[session_id]


def clear_session_history(session_id: str) -> None:
    """Clear the message history for a session."""
    global _session_preferences
    if session_id in _message_stores:
        _message_stores[session_id].clear()
    _session_preferences = {}


def save_preference(pref_type: str, value: str):
    """Save a session preference."""
    global _session_preferences
    _session_preferences[pref_type] = value


# ============================================
# MAIN PROCESSING
# ============================================

def build_system_prompt(command_type: str, meal: str = "") -> str:
    """Build a context-rich system prompt."""

    # Gather all context
    feedback_stats = get_feedback_stats()
    user_profile = get_user_profile_str()
    session_prefs = get_session_prefs_str()
    is_new_user = "NEW USER" in feedback_stats

    base_prompt = f"""You are BerkeleyBites AI, a food recommendation assistant for UC Berkeley dining halls.

## Current User Context
- Dietary Profile: {user_profile}
- Feedback Status: {feedback_stats}
- Session Preferences: {session_prefs}
"""

    if command_type == "recommend":
        menu = get_menu_str(meal)
        feedback_history = get_feedback_history_str() if not is_new_user else "N/A"

        base_prompt += f"""
## Today's Menu
{menu}

## User's Past Ratings
{feedback_history}

## Your Task
"""
        if is_new_user and session_prefs == "None":
            base_prompt += """This is a new user with no preferences set. Before recommending food:
1. Ask ONE quick question about their preference (spicy vs mild, OR light vs hearty, OR cuisine type)
2. Keep it brief and friendly
3. Do NOT recommend food yet - wait for their answer first"""
        else:
            base_prompt += """Make personalized food recommendations:
1. Recommend 2-3 specific dishes from the menu
2. Respect their dietary restrictions
3. Consider their preferences and past ratings
4. Briefly explain why each dish is a good match
5. Format as a numbered list"""

    elif command_type == "why":
        menu = get_menu_str()
        base_prompt += f"""
## Today's Menu
{menu}

## Your Task
Explain whether the requested dish is a good choice for this user based on their dietary profile and preferences. Be specific about ingredients and restrictions."""

    elif command_type == "search":
        base_prompt += """
## Your Task
Use your knowledge to answer the user's food-related question. Perplexity has built-in web search, so you can provide current information about nutrition, recipes, etc."""

    elif command_type == "similar":
        menu = get_menu_str()
        base_prompt += f"""
## Today's Menu
{menu}

## Your Task
Find dishes on today's menu that are similar to what the user asked about. Consider flavor profiles, ingredients, and cooking style."""

    else:  # general/chat
        base_prompt += """
## Your Task
Respond helpfully to the user. If they're answering a preference question you asked, acknowledge their answer warmly, save that preference mentally, and then either ask another question or provide recommendations based on what you know."""

    base_prompt += """

## Response Style
- Be concise and friendly
- Use markdown formatting
- Keep responses focused and helpful"""

    return base_prompt


def process_command(command: str, session_id: str = "default") -> str:
    """
    Process a user command and return the response.

    Args:
        command: The user's command (e.g., "/recommend lunch")
        session_id: Session ID for conversation history

    Returns:
        The assistant's response string.
    """
    global _session_preferences

    history = get_session_history(session_id)
    command = command.strip()

    # Handle /help command locally
    if command.lower() == "/help":
        return """**BerkeleyBites AI Commands:**

`/recommend` - Get personalized meal recommendations
`/recommend [meal]` - Recommendations for specific meal (breakfast/lunch/dinner)
`/why [dish]` - Explain why a dish is or isn't good for you
`/search [query]` - Search for nutrition info or food facts
`/similar [dish]` - Find similar dishes on today's menu
`/preferences` - Show your current session preferences
`/clear` - Clear conversation and start fresh
`/help` - Show this help message

**Tip:** The more dishes you rate (👍/👎), the better my recommendations become!"""

    if command.lower() == "/preferences":
        if not _session_preferences:
            return "No preferences set this session. Use `/recommend` and I'll ask you some questions!"
        prefs = []
        for k, v in _session_preferences.items():
            prefs.append(f"- {k.replace('_', ' ').title()}: {v}")
        return "**Your session preferences:**\n" + "\n".join(prefs)

    if command.lower() == "/clear":
        clear_session_history(session_id)
        return "Conversation cleared! Let's start fresh."

    # Determine command type and build appropriate prompt
    if command.lower().startswith("/recommend"):
        parts = command.split(maxsplit=1)
        meal = parts[1] if len(parts) > 1 else ""
        command_type = "recommend"
        user_message = f"I want food recommendations{' for ' + meal if meal else ''}."

    elif command.lower().startswith("/why"):
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: `/why [dish name]` - e.g., `/why Pizza`"
        command_type = "why"
        user_message = f"Is '{parts[1]}' a good choice for me? Why or why not?"

    elif command.lower().startswith("/search"):
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: `/search [query]` - e.g., `/search tofu protein content`"
        command_type = "search"
        user_message = parts[1]

    elif command.lower().startswith("/similar"):
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "Usage: `/similar [dish name]` - e.g., `/similar Pasta`"
        command_type = "similar"
        user_message = f"Find dishes similar to '{parts[1]}' on today's menu."

    else:
        # Natural language - likely answering a preference question
        command_type = "chat"
        user_message = command

        # Try to detect and save preferences from user's answer
        lower_cmd = command.lower()
        if any(word in lower_cmd for word in ['spicy', 'hot', 'mild', 'medium']):
            if 'spicy' in lower_cmd or 'hot' in lower_cmd:
                save_preference('spicy_preference', 'spicy')
            elif 'mild' in lower_cmd:
                save_preference('spicy_preference', 'mild')
            elif 'medium' in lower_cmd:
                save_preference('spicy_preference', 'medium')

        if any(word in lower_cmd for word in ['light', 'hearty', 'heavy', 'filling']):
            if 'light' in lower_cmd:
                save_preference('portion_preference', 'light')
            elif any(word in lower_cmd for word in ['hearty', 'heavy', 'filling']):
                save_preference('portion_preference', 'hearty')

    try:
        llm = get_llm()

        # Build system prompt with context
        meal = ""
        if command_type == "recommend":
            parts = command.split(maxsplit=1)
            meal = parts[1] if len(parts) > 1 else ""

        system_prompt = build_system_prompt(command_type, meal)

        # Build messages
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (last 6 messages max)
        for msg in history.messages[-6:]:
            messages.append(msg)

        # Add current message
        messages.append(HumanMessage(content=user_message))

        # Get response
        response = llm.invoke(messages)
        response_text = response.content

        # Update history
        history.add_user_message(command)
        history.add_ai_message(response_text)

        return response_text

    except Exception as e:
        return f"Error: {str(e)}"
