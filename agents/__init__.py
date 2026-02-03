"""
BerkeleyBites Multi-Agent System

This package provides specialized agents for food recommendation:
- MoodAgent: Reads user mood and provides food guidance
- TemperatureAgent: Gets Berkeley weather for temperature-based suggestions
- FoodAvailabilityAgent: Queries menu data
- TastePreferencesAgent: Analyzes user feedback history
- Orchestrator: Coordinates all agents for recommendations
"""

from .mood_agent import get_user_mood
from .temperature_agent import get_current_temperature
from .food_availability_agent import get_available_dishes, get_menu_summary
from .taste_preferences_agent import get_taste_preferences, get_similar_liked_dishes
from .orchestrator import get_recommendation, set_orchestrator_context

__all__ = [
    "get_user_mood",
    "get_current_temperature",
    "get_available_dishes",
    "get_menu_summary",
    "get_taste_preferences",
    "get_similar_liked_dishes",
    "get_recommendation",
    "set_orchestrator_context",
]
