"""
BerkeleyBites FastAPI Backend

Provides REST API endpoints for the React frontend, wrapping existing agents.
Data is stored in Supabase (PostgreSQL).
"""

import logging
import os
from datetime import date, datetime
from typing import Optional
from contextlib import asynccontextmanager

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .models import (
    UserProfile, MoodUpdate, Dish, MenuSummary,
    FeedbackSubmit, FeedbackStats,
    ChatMessage, ChatResponse, RecommendationResponse, AgentSummary,
    QuestionResponse, QuestionOption
)

# Import from sibling modules
from scraper import is_data_fresh, scrape_and_transform
from .agents import set_orchestrator_context, get_recommendation
from .agents.question_agent import (
    get_next_question,
    all_questions_answered,
    format_context_for_recommendation
)

# Import database layer
from . import database as db


# ===========================================
# Constants
# ===========================================

# Mood to food guidance mapping (used by /api/profile/mood endpoint)
# Note: Actual mood scoring for recommendations is in backend/agents/scoring.py
MOOD_GUIDANCE = {
    "happy": {
        "description": "Feeling happy and content",
        "food_suggestion": "You're in a great mood! Try something adventurous or celebratory.",
    },
    "grumpy": {
        "description": "Feeling irritable or annoyed",
        "food_suggestion": "Comfort food can help lift your spirits. Look for hearty, satisfying dishes.",
    },
    "stressed": {
        "description": "Feeling anxious or overwhelmed",
        "food_suggestion": "Go for foods that are easy to eat. Light, nutritious options can help stabilize your mood.",
    },
    "tired": {
        "description": "Feeling low on energy",
        "food_suggestion": "You need an energy boost! Look for protein-rich foods and complex carbohydrates.",
    },
    "adventurous": {
        "description": "Feeling curious and open to new experiences",
        "food_suggestion": "Perfect time to try something new! Look for unique dishes or international cuisine.",
    },
}


# ===========================================
# Time-Based Meal Detection
# ===========================================

def get_current_meal_period() -> str:
    """
    Determine the current meal period based on time of day.

    Uses Pacific time (Berkeley's timezone) for accurate detection.
    Falls back to system local time if timezone conversion fails.

    Meal periods (based on Berkeley dining hours):
    - Breakfast: until 10:30 AM
    - Lunch: 10:30 AM - 3:00 PM
    - Dinner: 3:00 PM - 9:00 PM
    - After 9 PM: defaults to Dinner (late night)

    Returns:
        Meal period string (e.g., "Lunch", "Dinner")
    """
    try:
        # Try to get Pacific time
        from zoneinfo import ZoneInfo
        pacific = ZoneInfo("America/Los_Angeles")
        now = datetime.now(pacific)
    except Exception:
        # Fallback to local time
        now = datetime.now()

    hour = now.hour
    minute = now.minute
    time_decimal = hour + minute / 60.0

    if time_decimal < 10.5:
        # Before 10:30 AM - Breakfast
        return "Breakfast"
    elif time_decimal < 15.0:
        # 10:30 AM - 3:00 PM - Lunch
        return "Lunch"
    elif time_decimal < 21.0:
        # 3:00 PM - 9:00 PM - Dinner
        return "Dinner"
    else:
        # After 9 PM - Late night, show Dinner
        return "Dinner"


# ===========================================
# Global State
# ===========================================

# In-memory cache for menu data
_menu_df: Optional[pd.DataFrame] = None

# Pending recommendations (in-memory, ephemeral by design)
# Stores: {"meal": str, "answered": dict[str, str]}
_pending_recommendations: dict[str, dict] = {}


def load_menu_data() -> pd.DataFrame:
    """Load menu data from Supabase, scraping if necessary."""
    global _menu_df

    if not is_data_fresh():
        # Need to scrape fresh data
        df = scrape_and_transform()
        _menu_df = df
        return df

    # Load from Supabase
    dishes = db.get_dishes()
    if dishes:
        _menu_df = pd.DataFrame(dishes)
        return _menu_df

    return pd.DataFrame()


def load_feedback(user_id: str) -> pd.DataFrame:
    """Load existing feedback from Supabase for a specific user.

    Args:
        user_id: Required user ID to load feedback for.
                 Never loads all users' feedback for security.
    """
    feedback = db.get_user_feedback(user_id)

    if feedback:
        df = pd.DataFrame(feedback)
        # Rename columns for compatibility
        if 'rating_date' in df.columns:
            df['date'] = df['rating_date']
        return df

    return pd.DataFrame(columns=['user_id', 'dish_id', 'dish_name', 'liked', 'created_at', 'date'])


def save_feedback(user_id: str, dish_id: int, dish_name: str, liked: bool) -> None:
    """Save feedback to Supabase."""
    db.submit_feedback(user_id, dish_id, dish_name, liked)


def get_user_profile(user_id: str) -> UserProfile:
    """Get or create user profile from Supabase."""
    profile_data = db.get_user_profile(user_id)
    if profile_data:
        return UserProfile(**profile_data)
    return UserProfile()


def save_user_profile(user_id: str, profile: UserProfile) -> None:
    """Save user profile to Supabase."""
    db.upsert_user_profile(user_id, profile.model_dump())


def get_user_mood(user_id: str) -> str:
    """Get user mood from Supabase, defaulting to happy."""
    return db.get_user_mood(user_id)


def save_user_mood(user_id: str, mood: str) -> None:
    """Save user mood to Supabase."""
    db.set_user_mood(user_id, mood)


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
    feedback_df = load_feedback(user_id)
    profile = get_user_profile(user_id)
    mood = get_user_mood(user_id)

    # Filter menu by profile
    filtered_df = filter_by_profile(menu_df, profile)

    # Update orchestrator context (handles /recommend with multi-agent system)
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

    # Warm caches for faster recommendations
    await warm_caches()

    yield


async def warm_caches():
    """Warm caches on startup for faster recommendations."""
    from datetime import date as date_type

    logging.info("Warming caches...")

    try:
        # Import cache functions
        from .agents.cache import (
            set_cached_dishes,
            set_cached_dish_embeddings
        )

        today = str(date_type.today())

        # Cache today's dishes
        dishes = db.get_dishes(scrape_date=today)
        if dishes:
            set_cached_dishes(dishes, today)
            logging.info(f"Cached {len(dishes)} dishes")

        # Cache embeddings
        try:
            embeddings = db.get_dish_embeddings(today)
            if embeddings:
                set_cached_dish_embeddings(embeddings, today)
                logging.info(f"Cached {len(embeddings)} embeddings")
        except Exception as e:
            logging.warning(f"Could not cache embeddings: {e}")

    except Exception as e:
        logging.warning(f"Cache warmup failed: {e}")


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
        # Use contains match to handle "Spring - Lunch" format from scraper
        filtered_df = filtered_df[filtered_df['meal_period'].str.lower().str.contains(meal.lower())]

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
async def refresh_menu(
    generate_embeddings: bool = Query(False, description="Also generate embeddings")
):
    """Trigger menu scraper to get fresh data."""
    global _menu_df

    try:
        df = scrape_and_transform()
        _menu_df = df

        result = {
            "success": True,
            "message": f"Scraped {len(df)} dishes",
            "date": str(date.today()),
            "embeddings_generated": 0
        }

        # Generate embeddings if requested
        if generate_embeddings:
            try:
                from scraper import generate_embeddings_for_new_dishes
                count = generate_embeddings_for_new_dishes()
                result["embeddings_generated"] = count
                result["message"] += f", generated {count} embeddings"
            except Exception as e:
                result["embedding_error"] = str(e)

        # Re-warm caches
        await warm_caches()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.post("/api/embeddings/generate")
async def generate_embeddings():
    """Generate embeddings for dishes without them."""
    try:
        from scraper import generate_embeddings_for_new_dishes
        count = generate_embeddings_for_new_dishes()

        # Update embedding cache
        from .agents.cache import set_cached_dish_embeddings
        embeddings = db.get_dish_embeddings()
        if embeddings:
            set_cached_dish_embeddings(embeddings, str(date.today()))

        return {
            "success": True,
            "embeddings_generated": count,
            "total_embeddings": len(embeddings) if embeddings else 0
        }
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service unavailable: {str(e)}. Install sentence-transformers."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")


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
    save_user_profile(user_id, profile)
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

    save_user_mood(user_id, mood)
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
async def submit_feedback_endpoint(
    feedback: FeedbackSubmit,
    user_id: str = Query("default", description="User ID")
):
    """Submit dish rating feedback."""
    save_feedback(user_id, feedback.dish_id, feedback.dish_name, feedback.liked)

    return {
        "success": True,
        "dish_id": feedback.dish_id,
        "liked": feedback.liked
    }


@app.get("/api/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats_endpoint(
    user_id: str = Query("default", description="User ID")
):
    """Get user feedback statistics."""
    stats = db.get_feedback_stats(user_id)
    return FeedbackStats(**stats)


@app.get("/api/feedback/{dish_id}")
async def get_dish_feedback_endpoint(
    dish_id: int,
    user_id: str = Query("default", description="User ID")
):
    """Get user's feedback for a specific dish today."""
    liked = db.get_dish_feedback(user_id, dish_id)
    return {"feedback": liked}


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

        # Auto-detect meal period if not specified
        if not meal:
            meal = get_current_meal_period()
            logging.info(f"Auto-detected meal period: {meal}")

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

    # For unrecognized commands, return a helpful message
    return ChatResponse(
        response="Please use `/recommend [meal]` to get personalized recommendations. Example: `/recommend lunch`",
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

    # Save mood for future sessions (no need to re-update agent context
    # since the orchestrator gets mood directly from question_context)
    if "mood" in question_context:
        save_user_mood(user_id, question_context["mood"])

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
# Health Check
# ===========================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    menu_df = load_menu_data()

    result = {
        "status": "healthy",
        "date": str(date.today()),
        "menu_loaded": not menu_df.empty,
        "dish_count": len(menu_df),
        "storage_backend": "supabase"
    }

    # Add Supabase health
    try:
        db_health = db.health_check()
        result["database"] = db_health
    except Exception as e:
        result["database"] = {"status": "error", "error": str(e)}

    # Add cache stats
    try:
        from .agents.cache import get_cache
        cache = get_cache()
        result["cache"] = cache.get_stats()
    except Exception as e:
        result["cache"] = {"status": "error", "error": str(e)}

    # Add embedding stats
    try:
        embeddings = db.get_dish_embeddings()
        result["embeddings"] = {
            "count": len(embeddings) if embeddings else 0,
            "coverage": f"{len(embeddings) / len(menu_df) * 100:.1f}%" if menu_df is not None and len(menu_df) > 0 and embeddings else "0%"
        }
    except Exception as e:
        result["embeddings"] = {"status": "unavailable", "error": str(e)}

    return result


@app.get("/api/rag/stats")
async def get_rag_stats(
    user_id: str = Query("default", description="User ID")
):
    """Get RAG system statistics and performance metrics."""
    try:
        from .agents.cache import get_cache
        from .agents.hybrid_retriever import get_retriever

        cache = get_cache()
        retriever = get_retriever()

        # Get embedding coverage
        today = str(date.today())
        dishes = db.get_dishes(scrape_date=today)
        embeddings = db.get_dish_embeddings(today)

        embedding_coverage = 0
        if dishes and embeddings:
            embedding_coverage = len(embeddings) / len(dishes) * 100

        return {
            "status": "healthy",
            "cache_stats": cache.get_stats(),
            "dishes_today": len(dishes) if dishes else 0,
            "embeddings_count": len(embeddings) if embeddings else 0,
            "embedding_coverage_percent": round(embedding_coverage, 1),
            "retriever_config": {
                "vector_candidates": retriever.config.vector_candidates,
                "top_k_for_llm": retriever.config.top_k_for_llm,
                "final_selection": retriever.config.final_selection,
                "use_llm": retriever.config.use_llm,
                "use_cache": retriever.config.use_cache
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
