"""
BerkeleyBites FastAPI Backend

Provides REST API endpoints for the React frontend, wrapping existing agents.
"""

import os
import sys
from datetime import date, datetime
from typing import Optional
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for agent imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import (
    UserProfile, MoodUpdate, Dish, MenuSummary,
    FeedbackSubmit, FeedbackStats,
    ChatMessage, ChatResponse, RecommendationResponse, AgentSummary,
    WeatherResponse, QuestionResponse, QuestionOption
)

# Import existing modules from parent directory
from scraper import is_data_fresh, scrape_and_transform
from food_agent import set_context, process_command
from agents import set_orchestrator_context, get_recommendation
from agents.temperature_agent import fetch_weather_from_open_meteo, get_temperature_guidance
from agents.mood_agent import MOOD_GUIDANCE
from agents.question_agent import (
    get_next_question,
    all_questions_answered,
    format_context_for_recommendation
)


# ===========================================
# Global State
# ===========================================

# In-memory user profiles (keyed by user_id)
_user_profiles: dict[str, UserProfile] = {}
_user_moods: dict[str, str] = {}
_menu_df: Optional[pd.DataFrame] = None

# Pending recommendations (keyed by session_id)
# Stores: {"meal": str, "answered": dict[str, str]}
_pending_recommendations: dict[str, dict] = {}


def get_base_path() -> str:
    """Get the base path for data files."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_menu_data() -> pd.DataFrame:
    """Load menu data, scraping if necessary."""
    global _menu_df

    base_path = get_base_path()
    csv_path = os.path.join(base_path, 'dining_data_clean.csv')

    if not is_data_fresh():
        # Need to scrape fresh data
        df = scrape_and_transform()
        _menu_df = df
        return df

    if _menu_df is None:
        _menu_df = pd.read_csv(csv_path)

    return _menu_df


def load_feedback() -> pd.DataFrame:
    """Load existing feedback from CSV."""
    base_path = get_base_path()
    csv_path = os.path.join(base_path, 'feedback.csv')

    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=['user_id', 'dish_id', 'dish_name', 'liked', 'timestamp', 'date'])


def save_feedback_to_csv(feedback_df: pd.DataFrame) -> None:
    """Save feedback DataFrame to CSV."""
    base_path = get_base_path()
    csv_path = os.path.join(base_path, 'feedback.csv')
    feedback_df.to_csv(csv_path, index=False)


def get_user_profile(user_id: str) -> UserProfile:
    """Get or create user profile."""
    if user_id not in _user_profiles:
        _user_profiles[user_id] = UserProfile()
    return _user_profiles[user_id]


def get_user_mood(user_id: str) -> str:
    """Get user mood, defaulting to happy."""
    return _user_moods.get(user_id, "happy")


def filter_by_profile(df: pd.DataFrame, profile: UserProfile) -> pd.DataFrame:
    """Filter dishes based on user profile."""
    filtered = df.copy()

    if profile.is_vegan:
        filtered = filtered[filtered['is_vegan'] == True]
        return filtered

    if profile.is_vegetarian:
        filtered = filtered[filtered['is_vegetarian'] == True]

    if profile.is_pescatarian:
        filtered = filtered[
            (filtered['is_vegetarian'] == True) |
            (filtered['has_fish'] == True)
        ]

    if profile.is_halal:
        filtered = filtered[filtered['is_halal'] == True]

    if profile.is_kosher:
        filtered = filtered[filtered['is_kosher'] == True]

    if profile.avoid_milk:
        filtered = filtered[filtered['has_milk'] == False]

    if profile.avoid_eggs:
        filtered = filtered[filtered['has_egg'] == False]

    if profile.avoid_gluten:
        filtered = filtered[filtered['has_gluten'] == False]

    if profile.avoid_nuts:
        filtered = filtered[filtered['has_tree_nuts'] == False]

    if profile.avoid_soy:
        filtered = filtered[filtered['has_soybeans'] == False]

    return filtered


def update_agent_context(user_id: str) -> pd.DataFrame:
    """Update the agent context and return filtered menu."""
    menu_df = load_menu_data()
    feedback_df = load_feedback()
    profile = get_user_profile(user_id)
    mood = get_user_mood(user_id)

    # Filter menu by profile
    filtered_df = filter_by_profile(menu_df, profile)

    # Update legacy food_agent context
    set_context(
        menu_df=filtered_df,
        feedback_df=feedback_df,
        user_profile=profile.model_dump(),
        user_id=user_id
    )

    # Update orchestrator context
    set_orchestrator_context(
        menu_df=filtered_df,
        feedback_df=feedback_df,
        user_profile=profile.model_dump(),
        user_id=user_id,
        user_mood=mood
    )

    return filtered_df


# ===========================================
# Lifespan Handler
# ===========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data on startup."""
    # Load menu data on startup
    load_menu_data()
    yield


# ===========================================
# FastAPI App
# ===========================================

app = FastAPI(
    title="BerkeleyBites API",
    description="Backend API for BerkeleyBites food recommendation app",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Menu Endpoints
# ===========================================

@app.get("/api/menu", response_model=list[Dish])
async def get_menu(
    hall: Optional[str] = Query(None, description="Filter by dining hall"),
    meal: Optional[str] = Query(None, description="Filter by meal period"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: str = Query("default", description="User ID for profile filtering")
):
    """Get menu dishes with optional filters."""
    filtered_df = update_agent_context(user_id)

    if filtered_df.empty:
        return []

    # Apply additional filters
    if hall:
        filtered_df = filtered_df[filtered_df['dining_hall'].str.lower() == hall.lower()]

    if meal:
        filtered_df = filtered_df[filtered_df['meal_period'].str.lower() == meal.lower()]

    if category:
        filtered_df = filtered_df[filtered_df['category'].str.lower() == category.lower()]

    # Convert to list of Dish models
    dishes = []
    for _, row in filtered_df.iterrows():
        dishes.append(Dish(**row.to_dict()))

    return dishes


@app.get("/api/menu/summary", response_model=MenuSummary)
async def get_menu_summary(
    user_id: str = Query("default", description="User ID for profile filtering")
):
    """Get summary of available menu options."""
    filtered_df = update_agent_context(user_id)

    if filtered_df.empty:
        return MenuSummary(
            total_dishes=0,
            dining_halls=[],
            meal_periods=[],
            categories=[],
            vegan_count=0,
            vegetarian_count=0,
            halal_count=0
        )

    return MenuSummary(
        total_dishes=len(filtered_df),
        dining_halls=filtered_df['dining_hall'].unique().tolist(),
        meal_periods=filtered_df['meal_period'].unique().tolist(),
        categories=filtered_df['category'].unique().tolist(),
        vegan_count=int(filtered_df['is_vegan'].sum()),
        vegetarian_count=int(filtered_df['is_vegetarian'].sum()),
        halal_count=int(filtered_df['is_halal'].sum())
    )


@app.post("/api/menu/refresh")
async def refresh_menu():
    """Trigger menu scraper to get fresh data."""
    global _menu_df

    try:
        df = scrape_and_transform()
        _menu_df = df
        return {
            "success": True,
            "message": f"Scraped {len(df)} dishes",
            "date": str(date.today())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


# ===========================================
# Profile Endpoints
# ===========================================

@app.get("/api/profile", response_model=UserProfile)
async def get_profile(
    user_id: str = Query("default", description="User ID")
):
    """Get user dietary profile."""
    return get_user_profile(user_id)


@app.put("/api/profile", response_model=UserProfile)
async def update_profile(
    profile: UserProfile,
    user_id: str = Query("default", description="User ID")
):
    """Update user dietary profile."""
    _user_profiles[user_id] = profile
    return profile


@app.put("/api/profile/mood")
async def update_mood(
    mood_update: MoodUpdate,
    user_id: str = Query("default", description="User ID")
):
    """Update user mood."""
    mood = mood_update.mood.lower()

    if mood not in MOOD_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Valid options: {list(MOOD_GUIDANCE.keys())}"
        )

    _user_moods[user_id] = mood
    guidance = MOOD_GUIDANCE[mood]

    return {
        "mood": mood,
        "description": guidance["description"],
        "food_suggestion": guidance["food_suggestion"]
    }


@app.get("/api/profile/mood")
async def get_mood(
    user_id: str = Query("default", description="User ID")
):
    """Get current user mood and available options."""
    current_mood = get_user_mood(user_id)

    return {
        "current_mood": current_mood,
        "available_moods": [
            {"value": k, "label": k.capitalize(), "description": v["description"]}
            for k, v in MOOD_GUIDANCE.items()
        ]
    }


# ===========================================
# Feedback Endpoints
# ===========================================

@app.post("/api/feedback")
async def submit_feedback(
    feedback: FeedbackSubmit,
    user_id: str = Query("default", description="User ID")
):
    """Submit dish rating feedback."""
    feedback_df = load_feedback()

    # Check for existing feedback today
    today = str(date.today())
    existing = feedback_df[
        (feedback_df['user_id'] == user_id) &
        (feedback_df['dish_id'] == feedback.dish_id) &
        (feedback_df['date'] == today)
    ]

    if not existing.empty:
        # Update existing feedback
        feedback_df.loc[existing.index, 'liked'] = 1 if feedback.liked else 0
        feedback_df.loc[existing.index, 'timestamp'] = datetime.now().isoformat()
    else:
        # Add new feedback
        new_entry = {
            'user_id': user_id,
            'dish_id': feedback.dish_id,
            'dish_name': feedback.dish_name,
            'liked': 1 if feedback.liked else 0,
            'timestamp': datetime.now().isoformat(),
            'date': today
        }
        feedback_df = pd.concat([feedback_df, pd.DataFrame([new_entry])], ignore_index=True)

    save_feedback_to_csv(feedback_df)

    return {
        "success": True,
        "dish_id": feedback.dish_id,
        "liked": feedback.liked
    }


@app.get("/api/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    user_id: str = Query("default", description="User ID")
):
    """Get user feedback statistics."""
    feedback_df = load_feedback()

    if feedback_df.empty:
        return FeedbackStats(
            total_ratings=0,
            liked_count=0,
            disliked_count=0,
            today_ratings=0
        )

    user_feedback = feedback_df[feedback_df['user_id'] == user_id]

    if user_feedback.empty:
        return FeedbackStats(
            total_ratings=0,
            liked_count=0,
            disliked_count=0,
            today_ratings=0
        )

    today = str(date.today())
    today_feedback = user_feedback[user_feedback['date'] == today]
    liked_count = int(user_feedback['liked'].sum())

    return FeedbackStats(
        total_ratings=len(user_feedback),
        liked_count=liked_count,
        disliked_count=len(user_feedback) - liked_count,
        today_ratings=len(today_feedback)
    )


@app.get("/api/feedback/{dish_id}")
async def get_dish_feedback(
    dish_id: int,
    user_id: str = Query("default", description="User ID")
):
    """Get user's feedback for a specific dish today."""
    feedback_df = load_feedback()

    if feedback_df.empty:
        return {"feedback": None}

    today = str(date.today())
    existing = feedback_df[
        (feedback_df['user_id'] == user_id) &
        (feedback_df['dish_id'] == dish_id) &
        (feedback_df['date'] == today)
    ]

    if existing.empty:
        return {"feedback": None}

    return {"feedback": bool(existing.iloc[0]['liked'])}


# ===========================================
# Chat Endpoints
# ===========================================

@app.post("/api/chat")
async def chat(
    message: ChatMessage,
    user_id: str = Query("default", description="User ID")
):
    """Send a command to the AI assistant."""
    session_id = message.session_id or user_id

    # Update context before processing
    update_agent_context(user_id)

    command = message.message.strip()

    # Check if this is an answer to a pending question
    if command.startswith("answer:"):
        return await handle_question_answer(command, session_id, user_id)

    # Route /recommend to start the questioning flow
    if command.lower().startswith("/recommend"):
        parts = command.split(maxsplit=1)
        meal = parts[1] if len(parts) > 1 else ""

        # Initialize pending recommendation with empty answers
        _pending_recommendations[session_id] = {
            "meal": meal,
            "answered": {}
        }

        # Get the first question
        next_question = get_next_question({})
        if next_question:
            return QuestionResponse(
                response_type="question",
                question_id=next_question["id"],
                question_text=next_question["question_text"],
                options=[
                    QuestionOption(
                        value=opt["value"],
                        label=opt["label"],
                        emoji=opt.get("emoji", "")
                    )
                    for opt in next_question["options"]
                ],
                session_id=session_id
            )

        # If no questions (shouldn't happen), proceed directly to recommendation
        return await generate_recommendation(session_id, user_id, meal, {})

    # Other commands go to food_agent
    response = process_command(command, session_id=session_id)
    return ChatResponse(
        response=response,
        session_id=session_id
    )


async def handle_question_answer(command: str, session_id: str, user_id: str):
    """Handle an answer to a pending question."""
    # Parse answer: format is "answer:question_id:value"
    parts = command.split(":", 2)
    if len(parts) != 3:
        return ChatResponse(
            response="Invalid answer format",
            session_id=session_id
        )

    _, question_id, value = parts

    # Get pending recommendation
    pending = _pending_recommendations.get(session_id)
    if not pending:
        return ChatResponse(
            response="No pending recommendation. Use /recommend to start.",
            session_id=session_id
        )

    # Record the answer
    pending["answered"][question_id] = value

    # Check if all questions are answered
    if all_questions_answered(pending["answered"]):
        # Generate the recommendation
        meal = pending["meal"]
        answered = pending["answered"]

        # Clear pending state
        del _pending_recommendations[session_id]

        return await generate_recommendation(session_id, user_id, meal, answered)

    # Get the next question
    next_question = get_next_question(pending["answered"])
    if next_question:
        return QuestionResponse(
            response_type="question",
            question_id=next_question["id"],
            question_text=next_question["question_text"],
            options=[
                QuestionOption(
                    value=opt["value"],
                    label=opt["label"],
                    emoji=opt.get("emoji", "")
                )
                for opt in next_question["options"]
            ],
            session_id=session_id
        )

    # Fallback: generate recommendation if no more questions
    meal = pending["meal"]
    answered = pending["answered"]
    del _pending_recommendations[session_id]
    return await generate_recommendation(session_id, user_id, meal, answered)


async def generate_recommendation(
    session_id: str,
    user_id: str,
    meal: str,
    answered: dict
):
    """Generate a recommendation using the multi-agent system."""
    # Get context from answers
    question_context = format_context_for_recommendation(answered)

    # Update the mood based on the answer (for orchestrator compatibility)
    if "mood" in question_context:
        _user_moods[user_id] = question_context["mood"]
        # Re-update agent context with new mood
        update_agent_context(user_id)

    # Get recommendation with additional context
    result = get_recommendation(
        query=f"/recommend {meal}",
        meal=meal,
        session_id=session_id,
        question_context=question_context
    )

    # Convert dict summaries to AgentSummary models
    agent_summaries = {}
    for key, summary in result.get("agent_summaries", {}).items():
        agent_summaries[key] = AgentSummary(
            icon=summary["icon"],
            title=summary["title"],
            points=summary["points"]
        )

    return RecommendationResponse(
        agent_summaries=agent_summaries,
        recommendation=result["recommendation"],
        session_id=session_id
    )


# ===========================================
# Weather Endpoint
# ===========================================

@app.get("/api/weather", response_model=WeatherResponse)
async def get_weather():
    """Get current Berkeley weather and food suggestions."""
    weather = fetch_weather_from_open_meteo()
    temp_f = weather["temperature_f"]
    conditions = weather["conditions"]
    guidance = get_temperature_guidance(temp_f)

    return WeatherResponse(
        temperature_f=temp_f,
        conditions=conditions,
        food_suggestion=guidance["food_suggestion"]
    )


# ===========================================
# Health Check
# ===========================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    menu_df = load_menu_data()
    return {
        "status": "healthy",
        "date": str(date.today()),
        "menu_loaded": not menu_df.empty,
        "dish_count": len(menu_df)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
