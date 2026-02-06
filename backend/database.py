"""
BerkeleyBites Database Layer

Provides Supabase (PostgreSQL) access for all data operations.
"""

import os
from datetime import date
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ===========================================
# Supabase Client Singleton
# ===========================================

_client: Optional[Client] = None


def get_client() -> Client:
    """
    Get or create the Supabase client singleton.

    Returns:
        Supabase client instance.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY not set.
    """
    global _client

    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "Run 'supabase start' and copy the values from 'supabase status'."
            )

        _client = create_client(url, key)

    return _client


# ===========================================
# Dishes Functions
# ===========================================

def get_dishes(
    meal_period: Optional[str] = None,
    dining_hall: Optional[str] = None,
    scrape_date: Optional[str] = None
) -> list[dict]:
    """
    Get dishes from the database with optional filters.

    Args:
        meal_period: Filter by meal period (e.g., "Breakfast", "Lunch").
        dining_hall: Filter by dining hall name.
        scrape_date: Filter by scrape date (defaults to today).

    Returns:
        List of dish dictionaries with dish_id field for API compatibility.
    """
    client = get_client()

    # Default to today's date
    if scrape_date is None:
        scrape_date = str(date.today())

    query = client.table("dishes").select("*").eq("scrape_date", scrape_date)

    if meal_period:
        query = query.ilike("meal_period", f"%{meal_period}%")

    if dining_hall:
        query = query.ilike("dining_hall", f"%{dining_hall}%")

    response = query.execute()

    # Rename 'id' to 'dish_id' for API compatibility
    dishes = []
    for dish in response.data:
        dish["dish_id"] = dish.pop("id")
        # Remove created_at as it's not in the model
        dish.pop("created_at", None)
        dishes.append(dish)

    return dishes


def upsert_dishes(dishes: list[dict]) -> int:
    """
    Insert or update dishes in the database.

    Uses the unique constraint (dish_name, dining_hall, meal_period, scrape_date)
    to handle duplicates via upsert.

    Args:
        dishes: List of dish dictionaries from scraper.

    Returns:
        Number of dishes upserted.
    """
    if not dishes:
        return 0

    client = get_client()

    # Ensure scrape_date is set and clean up data
    today = str(date.today())
    seen = set()
    unique_dishes = []

    for dish in dishes:
        if "scrape_date" not in dish:
            dish["scrape_date"] = today
        # Remove dish_id if present (database generates it)
        dish.pop("dish_id", None)

        # Create unique key to deduplicate
        key = (
            dish.get("dish_name", ""),
            dish.get("dining_hall", ""),
            dish.get("meal_period", ""),
            dish.get("scrape_date", "")
        )

        if key not in seen:
            seen.add(key)
            unique_dishes.append(dish)

    if not unique_dishes:
        return 0

    # Upsert based on unique constraint
    response = client.table("dishes").upsert(
        unique_dishes,
        on_conflict="dish_name,dining_hall,meal_period,scrape_date"
    ).execute()

    return len(response.data)


def is_menu_fresh() -> bool:
    """
    Check if today's menu data exists in the database.

    Returns:
        True if dishes exist for today, False otherwise.
    """
    client = get_client()
    today = str(date.today())

    response = (
        client.table("dishes")
        .select("id", count="exact")
        .eq("scrape_date", today)
        .limit(1)
        .execute()
    )

    return response.count > 0 if response.count else False


def delete_old_dishes(days_to_keep: int = 7) -> int:
    """
    Delete dishes older than specified days.

    Note: This function is available for scheduled maintenance or manual cleanup.
    Not called automatically - run via cron job or admin endpoint if needed.

    Args:
        days_to_keep: Number of days of data to retain.

    Returns:
        Number of dishes deleted.
    """
    from datetime import timedelta

    client = get_client()
    cutoff_date = str(date.today() - timedelta(days=days_to_keep))

    response = (
        client.table("dishes")
        .delete()
        .lt("scrape_date", cutoff_date)
        .execute()
    )

    return len(response.data)


# ===========================================
# User Profile Functions
# ===========================================

def get_user_profile(user_id: str) -> Optional[dict]:
    """
    Get a user's dietary profile.

    Args:
        user_id: The user's identifier.

    Returns:
        Profile dictionary or None if not found.
    """
    client = get_client()

    response = (
        client.table("user_profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        profile = response.data[0]
        # Remove database-specific fields for API compatibility
        profile.pop("id", None)
        profile.pop("created_at", None)
        profile.pop("updated_at", None)
        profile.pop("user_id", None)
        return profile

    return None


def upsert_user_profile(user_id: str, profile: dict) -> dict:
    """
    Create or update a user's dietary profile.

    Args:
        user_id: The user's identifier.
        profile: Dictionary of profile fields.

    Returns:
        The upserted profile.
    """
    client = get_client()

    # Add user_id to profile data
    data = {**profile, "user_id": user_id}

    # Remove any None values
    data = {k: v for k, v in data.items() if v is not None}

    response = (
        client.table("user_profiles")
        .upsert(data, on_conflict="user_id")
        .execute()
    )

    if response.data:
        result = response.data[0]
        result.pop("id", None)
        result.pop("created_at", None)
        result.pop("updated_at", None)
        result.pop("user_id", None)
        return result

    return profile


# ===========================================
# Feedback Functions
# ===========================================

def get_user_feedback(user_id: str) -> list[dict]:
    """
    Get all feedback entries for a user.

    Args:
        user_id: The user's identifier.

    Returns:
        List of feedback dictionaries.
    """
    client = get_client()

    response = (
        client.table("feedback")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def submit_feedback(
    user_id: str,
    dish_id: int,
    dish_name: str,
    liked: bool
) -> dict:
    """
    Submit or update feedback for a dish.

    Uses upsert to handle one rating per user per dish per day.

    Args:
        user_id: The user's identifier.
        dish_id: The dish's database ID.
        dish_name: The dish name (for denormalized querying).
        liked: True if user liked the dish, False otherwise.

    Returns:
        The feedback entry.
    """
    client = get_client()
    today = str(date.today())

    data = {
        "user_id": user_id,
        "dish_id": dish_id,
        "dish_name": dish_name,
        "liked": liked,
        "rating_date": today
    }

    response = (
        client.table("feedback")
        .upsert(data, on_conflict="user_id,dish_id,rating_date")
        .execute()
    )

    return response.data[0] if response.data else data


def get_feedback_stats(user_id: str) -> dict:
    """
    Get feedback statistics for a user.

    Args:
        user_id: The user's identifier.

    Returns:
        Dictionary with total_ratings, liked_count, disliked_count, today_ratings.
    """
    client = get_client()
    today = str(date.today())

    # Get all user feedback
    response = (
        client.table("feedback")
        .select("liked, rating_date")
        .eq("user_id", user_id)
        .execute()
    )

    feedback = response.data
    total = len(feedback)
    liked = sum(1 for f in feedback if f["liked"])
    today_count = sum(1 for f in feedback if f["rating_date"] == today)

    return {
        "total_ratings": total,
        "liked_count": liked,
        "disliked_count": total - liked,
        "today_ratings": today_count
    }


def get_dish_feedback(user_id: str, dish_id: int) -> Optional[bool]:
    """
    Get a user's feedback for a specific dish today.

    Args:
        user_id: The user's identifier.
        dish_id: The dish's database ID.

    Returns:
        True if liked, False if disliked, None if no feedback.
    """
    client = get_client()
    today = str(date.today())

    response = (
        client.table("feedback")
        .select("liked")
        .eq("user_id", user_id)
        .eq("dish_id", dish_id)
        .eq("rating_date", today)
        .execute()
    )

    if response.data:
        return response.data[0]["liked"]

    return None


# ===========================================
# User Mood Functions
# ===========================================

VALID_MOODS = {"happy", "grumpy", "stressed", "tired", "adventurous"}


def get_user_mood(user_id: str) -> str:
    """
    Get a user's current mood.

    Args:
        user_id: The user's identifier.

    Returns:
        Mood string, defaults to "happy" if not set.
    """
    client = get_client()

    response = (
        client.table("user_moods")
        .select("mood")
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        return response.data[0]["mood"]

    return "happy"


def set_user_mood(user_id: str, mood: str) -> str:
    """
    Set a user's mood.

    Args:
        user_id: The user's identifier.
        mood: The mood to set (must be valid).

    Returns:
        The set mood.

    Raises:
        ValueError: If mood is not valid.
    """
    mood = mood.lower()

    if mood not in VALID_MOODS:
        raise ValueError(f"Invalid mood. Valid options: {VALID_MOODS}")

    client = get_client()

    response = (
        client.table("user_moods")
        .upsert({"user_id": user_id, "mood": mood}, on_conflict="user_id")
        .execute()
    )

    return mood


# ===========================================
# Utility Functions
# ===========================================

def health_check() -> dict:
    """
    Check database connectivity and basic stats.

    Returns:
        Dictionary with health status and counts.
    """
    try:
        client = get_client()
        today = str(date.today())

        # Count today's dishes
        dishes_response = (
            client.table("dishes")
            .select("id", count="exact")
            .eq("scrape_date", today)
            .execute()
        )

        # Count total users
        users_response = (
            client.table("user_profiles")
            .select("id", count="exact")
            .execute()
        )

        return {
            "status": "healthy",
            "database": "connected",
            "dishes_today": dishes_response.count or 0,
            "total_users": users_response.count or 0
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


# ===========================================
# pgvector / Embedding Functions
# ===========================================

def search_dishes_by_embedding(
    query_embedding: list[float],
    dish_ids: list[int],
    match_count: int = 30
) -> list[dict]:
    """
    Search dishes by embedding similarity using pgvector.

    Args:
        query_embedding: 384-dimensional query vector
        dish_ids: List of dish IDs to search within
        match_count: Maximum number of results

    Returns:
        List of {"dish_id": int, "similarity": float} sorted by similarity
    """
    client = get_client()

    try:
        result = client.rpc(
            "search_dishes_by_embedding",
            {
                "query_embedding": query_embedding,
                "dish_ids": dish_ids,
                "match_count": match_count
            }
        ).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"pgvector search error: {e}")
        return []


def get_dishes_without_embeddings(
    scrape_date: Optional[str] = None,
    limit: int = 100
) -> list[dict]:
    """
    Get dishes that need embedding generation.

    Args:
        scrape_date: Target date (defaults to today)
        limit: Maximum number of dishes to return

    Returns:
        List of dish dicts without embeddings
    """
    client = get_client()
    target_date = scrape_date or str(date.today())

    try:
        result = client.rpc(
            "get_dishes_without_embeddings",
            {
                "target_date": target_date,
                "batch_limit": limit
            }
        ).execute()
        return result.data if result.data else []
    except Exception as e:
        # Fallback: direct query
        print(f"RPC failed, using direct query: {e}")
        response = (
            client.table("dishes")
            .select("id, dish_name, category, dining_hall, meal_period, is_vegan, is_vegetarian, is_halal, is_kosher")
            .eq("scrape_date", target_date)
            .is_("embedding", "null")
            .limit(limit)
            .execute()
        )
        # Rename id to dish_id for consistency
        dishes = []
        for dish in response.data:
            dish["dish_id"] = dish.pop("id")
            dishes.append(dish)
        return dishes


def update_dish_embedding(
    dish_id: int,
    embedding: list[float],
    embedding_text: str
) -> bool:
    """
    Update a single dish's embedding.

    Args:
        dish_id: Dish ID to update
        embedding: 384-dimensional embedding vector
        embedding_text: Text used to generate the embedding

    Returns:
        True if successful
    """
    client = get_client()

    try:
        # Convert embedding list to pgvector format
        embedding_str = f"[{','.join(str(x) for x in embedding)}]"

        response = (
            client.table("dishes")
            .update({
                "embedding": embedding_str,
                "embedding_text": embedding_text
            })
            .eq("id", dish_id)
            .execute()
        )
        return len(response.data) > 0
    except Exception as e:
        print(f"Failed to update embedding for dish {dish_id}: {e}")
        return False


def batch_update_embeddings(updates: list[dict]) -> int:
    """
    Batch update dish embeddings.

    Args:
        updates: List of {"dish_id": int, "embedding": list, "embedding_text": str}

    Returns:
        Number of dishes updated
    """
    client = get_client()

    # Format embeddings for pgvector
    formatted_updates = []
    for update in updates:
        embedding = update.get("embedding", [])
        embedding_str = f"[{','.join(str(x) for x in embedding)}]"
        formatted_updates.append({
            "dish_id": update["dish_id"],
            "embedding": embedding_str,
            "embedding_text": update.get("embedding_text", "")
        })

    try:
        result = client.rpc(
            "batch_update_embeddings",
            {"updates": formatted_updates}
        ).execute()
        return result.data if isinstance(result.data, int) else 0
    except Exception as e:
        # Fallback: individual updates
        print(f"Batch update failed, using individual updates: {e}")
        count = 0
        for update in updates:
            if update_dish_embedding(
                update["dish_id"],
                update["embedding"],
                update.get("embedding_text", "")
            ):
                count += 1
        return count


def get_dish_embeddings(scrape_date: Optional[str] = None) -> dict[int, list[float]]:
    """
    Get all dish embeddings for a date.

    Args:
        scrape_date: Target date (defaults to today)

    Returns:
        Dict mapping dish_id -> embedding vector
    """
    client = get_client()
    target_date = scrape_date or str(date.today())

    response = (
        client.table("dishes")
        .select("id, embedding")
        .eq("scrape_date", target_date)
        .not_.is_("embedding", "null")
        .execute()
    )

    embeddings = {}
    for dish in response.data:
        dish_id = dish["id"]
        embedding = dish.get("embedding")
        if embedding:
            # Parse pgvector format if needed
            if isinstance(embedding, str):
                # Remove brackets and split
                embedding = [float(x) for x in embedding.strip("[]").split(",")]
            embeddings[dish_id] = embedding

    return embeddings


def get_dishes_with_embeddings(
    scrape_date: Optional[str] = None,
    meal_period: Optional[str] = None
) -> list[dict]:
    """
    Get dishes with their embeddings.

    Args:
        scrape_date: Target date (defaults to today)
        meal_period: Optional meal period filter

    Returns:
        List of dish dicts including embedding field
    """
    client = get_client()
    target_date = scrape_date or str(date.today())

    query = (
        client.table("dishes")
        .select("*")
        .eq("scrape_date", target_date)
    )

    if meal_period:
        query = query.ilike("meal_period", f"%{meal_period}%")

    response = query.execute()

    # Process results
    dishes = []
    for dish in response.data:
        dish["dish_id"] = dish.pop("id")
        dish.pop("created_at", None)

        # Parse embedding if present
        embedding = dish.get("embedding")
        if embedding and isinstance(embedding, str):
            dish["embedding"] = [float(x) for x in embedding.strip("[]").split(",")]

        dishes.append(dish)

    return dishes
