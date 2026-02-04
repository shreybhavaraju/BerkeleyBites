"""
Mood Agent for BerkeleyBites

A deterministic agent that reads user mood from session state
and provides food guidance based on mood.
"""

from langchain_core.tools import tool

# Mood to food guidance mapping
MOOD_GUIDANCE = {
    "happy": {
        "description": "Feeling happy and content",
        "food_suggestion": "You're in a great mood! Try something adventurous or celebratory - maybe a new dish you haven't tried before, or your favorite comfort food to maintain that good feeling.",
        "prefer_categories": ["entrees", "chef's special", "grill"],
        "avoid_categories": [],
    },
    "grumpy": {
        "description": "Feeling irritable or annoyed",
        "food_suggestion": "Comfort food can help lift your spirits. Look for hearty, satisfying dishes - warm soups, pasta, or familiar favorites that feel like a warm hug.",
        "prefer_categories": ["soups", "comfort food", "pasta", "bakery"],
        "avoid_categories": [],
    },
    "stressed": {
        "description": "Feeling anxious or overwhelmed",
        "food_suggestion": "Go for foods that are easy to eat and won't add to your stress. Avoid heavy, greasy foods. Light, nutritious options with complex carbs can help stabilize your mood.",
        "prefer_categories": ["salads", "grain bowls", "soups", "vegetarian"],
        "avoid_categories": ["fried foods", "heavy entrees"],
    },
    "tired": {
        "description": "Feeling low on energy",
        "food_suggestion": "You need an energy boost! Look for protein-rich foods and complex carbohydrates. Avoid heavy, sleep-inducing foods. Something with good nutrition to power through your day.",
        "prefer_categories": ["protein", "grain bowls", "breakfast", "smoothies"],
        "avoid_categories": ["heavy pasta", "large portions"],
    },
    "adventurous": {
        "description": "Feeling curious and open to new experiences",
        "food_suggestion": "Perfect time to try something new! Look for unique dishes, international cuisine, or items you've never had before. The chef's specials might have something exciting.",
        "prefer_categories": ["chef's special", "international", "new items"],
        "avoid_categories": [],
    },
}


# Session state reference (set by orchestrator)
_user_mood: str = "happy"


def set_user_mood(mood: str) -> None:
    """Set the current user mood (called by orchestrator)."""
    global _user_mood
    if mood in MOOD_GUIDANCE:
        _user_mood = mood


@tool
def get_user_mood() -> str:
    """
    Get the user's current mood and food guidance.

    Returns a description of the user's mood and suggestions for what
    types of food might suit their current emotional state.

    Returns:
        A string with mood description and food suggestions.
    """
    mood = _user_mood
    guidance = MOOD_GUIDANCE.get(mood, MOOD_GUIDANCE["happy"])

    return f"""Current Mood: {mood.upper()}

{guidance['description']}

Food Guidance: {guidance['food_suggestion']}

Preferred food categories: {', '.join(guidance['prefer_categories']) if guidance['prefer_categories'] else 'No specific preference'}
Categories to potentially avoid: {', '.join(guidance['avoid_categories']) if guidance['avoid_categories'] else 'None'}"""
