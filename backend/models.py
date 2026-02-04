"""
Pydantic models for BerkeleyBites FastAPI backend.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date


# ===========================================
# User Profile Models
# ===========================================

class UserProfile(BaseModel):
    """User dietary profile with preferences and restrictions."""
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_pescatarian: bool = False
    is_halal: bool = False
    is_kosher: bool = False
    avoid_milk: bool = False
    avoid_eggs: bool = False
    avoid_gluten: bool = False
    avoid_nuts: bool = False
    avoid_soy: bool = False
    prefer_low_carbon: bool = False


class MoodUpdate(BaseModel):
    """Request to update user mood."""
    mood: str  # happy, grumpy, stressed, tired, adventurous


# ===========================================
# Menu Models
# ===========================================

class Dish(BaseModel):
    """A single dish from the dining hall menu."""
    dish_id: int
    dish_name: str
    dining_hall: str
    dining_hall_status: str
    meal_period: str
    category: str
    has_milk: bool = False
    has_egg: bool = False
    has_fish: bool = False
    has_shellfish: bool = False
    has_tree_nuts: bool = False
    has_wheat: bool = False
    has_peanuts: bool = False
    has_soybeans: bool = False
    has_sesame: bool = False
    has_gluten: bool = False
    is_vegan: bool = False
    is_vegetarian: bool = False
    is_halal: bool = False
    is_kosher: bool = False
    has_pork: bool = False
    has_alcohol: bool = False
    scrape_date: str


class MenuSummary(BaseModel):
    """Summary of available menu options."""
    total_dishes: int
    dining_halls: list[str]
    meal_periods: list[str]
    categories: list[str]
    vegan_count: int
    vegetarian_count: int
    halal_count: int


class MenuQuery(BaseModel):
    """Query parameters for filtering menu."""
    hall: Optional[str] = None
    meal: Optional[str] = None
    category: Optional[str] = None
    vegetarian_only: bool = False
    vegan_only: bool = False


# ===========================================
# Feedback Models
# ===========================================

class FeedbackSubmit(BaseModel):
    """Request to submit dish feedback."""
    dish_id: int
    dish_name: str
    liked: bool  # True for like, False for dislike


class FeedbackStats(BaseModel):
    """User feedback statistics."""
    total_ratings: int
    liked_count: int
    disliked_count: int
    today_ratings: int


class FeedbackEntry(BaseModel):
    """A single feedback entry."""
    user_id: str
    dish_id: int
    dish_name: str
    liked: int
    timestamp: str
    date: str


# ===========================================
# Chat Models
# ===========================================

class ChatMessage(BaseModel):
    """A chat message request."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the AI chat."""
    response: str
    session_id: str


class QuestionOption(BaseModel):
    """A single option for a question."""
    value: str
    label: str
    emoji: str = ""


class QuestionResponse(BaseModel):
    """Response that asks user a question with options."""
    response_type: str = "question"
    question_id: str
    question_text: str
    options: list[QuestionOption]
    session_id: str


class AgentSummary(BaseModel):
    """Summary from a single agent."""
    icon: str
    title: str
    points: list[str]


class RecommendationResponse(BaseModel):
    """Response from the AI recommendation with agent summaries."""
    agent_summaries: dict[str, AgentSummary]
    recommendation: str
    session_id: str


