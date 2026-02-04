"""
Taste Preferences Agent for BerkeleyBites

A deterministic agent that analyzes the user's feedback history
to understand their taste preferences.
"""

from typing import Optional
from collections import Counter
import pandas as pd
from langchain_core.tools import tool

# Global state (set by orchestrator)
_feedback_df: Optional[pd.DataFrame] = None
_user_id: Optional[str] = None
_menu_df: Optional[pd.DataFrame] = None

# Minimum feedback count for meaningful analysis
MIN_FEEDBACK_COUNT = 3


def set_feedback_data(feedback_df: pd.DataFrame, user_id: str, menu_df: pd.DataFrame = None) -> None:
    """Set the feedback DataFrame and user ID (called by orchestrator)."""
    global _feedback_df, _user_id, _menu_df
    _feedback_df = feedback_df
    _user_id = user_id
    _menu_df = menu_df


def _get_feedback_df() -> Optional[pd.DataFrame]:
    """Get feedback DataFrame from memory or database."""
    global _feedback_df

    if _feedback_df is not None and not _feedback_df.empty:
        return _feedback_df

    # Try loading from database if not in memory
    if _user_id:
        try:
            from backend.database import get_user_feedback
            feedback = get_user_feedback(_user_id)
            if feedback:
                _feedback_df = pd.DataFrame(feedback)
                return _feedback_df
        except Exception as e:
            print(f"Database feedback query failed: {e}")

    return _feedback_df


def _get_menu_df() -> Optional[pd.DataFrame]:
    """Get menu DataFrame from memory or database."""
    global _menu_df

    if _menu_df is not None and not _menu_df.empty:
        return _menu_df

    # Try loading from database if not in memory
    try:
        from backend.database import get_dishes
        dishes = get_dishes()
        if dishes:
            _menu_df = pd.DataFrame(dishes)
            return _menu_df
    except Exception as e:
        print(f"Database menu query failed: {e}")

    return _menu_df


@tool
def get_taste_preferences() -> str:
    """
    Analyze the user's feedback history to determine their taste preferences.

    Examines liked and disliked dishes to identify patterns in:
    - Preferred categories
    - Dietary preferences
    - Specific dishes they enjoyed

    Returns:
        A string describing the user's taste preferences based on their history.
    """
    feedback_df = _get_feedback_df()

    if feedback_df is None or feedback_df.empty or _user_id is None:
        return "No feedback history available. This appears to be a new user with no ratings yet."

    user_feedback = feedback_df[feedback_df['user_id'] == _user_id].copy()

    if len(user_feedback) < MIN_FEEDBACK_COUNT:
        count = len(user_feedback)
        return f"""Limited feedback history ({count} ratings).
Need at least {MIN_FEEDBACK_COUNT} ratings for meaningful preference analysis.
The user is still building their taste profile."""

    # Separate liked and disliked
    liked = user_feedback[user_feedback['liked'] == 1]['dish_name'].tolist()
    disliked = user_feedback[user_feedback['liked'] == 0]['dish_name'].tolist()

    # Try to get category info if menu data available
    liked_categories = []
    disliked_categories = []

    menu_df = _get_menu_df()
    if menu_df is not None and not menu_df.empty:
        for dish_name in liked:
            match = menu_df[menu_df['dish_name'].str.lower() == dish_name.lower()]
            if not match.empty:
                liked_categories.append(match.iloc[0]['category'])

        for dish_name in disliked:
            match = menu_df[menu_df['dish_name'].str.lower() == dish_name.lower()]
            if not match.empty:
                disliked_categories.append(match.iloc[0]['category'])

    # Analyze patterns
    result = f"""User Taste Preferences (based on {len(user_feedback)} ratings):

Liked Dishes ({len(liked)}):
{chr(10).join(f'  - {dish}' for dish in liked[-10:]) if liked else '  None recorded'}

Disliked Dishes ({len(disliked)}):
{chr(10).join(f'  - {dish}' for dish in disliked[-10:]) if disliked else '  None recorded'}
"""

    # Category analysis
    if liked_categories:
        cat_counts = Counter(liked_categories)
        top_cats = cat_counts.most_common(3)
        result += f"\nPreferred Categories (from liked dishes):\n"
        result += "\n".join(f"  - {cat}: {count} likes" for cat, count in top_cats)

    if disliked_categories:
        cat_counts = Counter(disliked_categories)
        avoid_cats = cat_counts.most_common(3)
        result += f"\n\nCategories to Potentially Avoid:\n"
        result += "\n".join(f"  - {cat}: {count} dislikes" for cat, count in avoid_cats)

    # Overall preference ratio
    like_ratio = len(liked) / len(user_feedback) * 100
    result += f"\n\nOverall Rating Pattern:"
    result += f"\n  - Like rate: {like_ratio:.0f}%"

    if like_ratio > 70:
        result += "\n  - This user is generally positive about dining hall food"
    elif like_ratio < 30:
        result += "\n  - This user is quite selective - recommend only highly-rated options"
    else:
        result += "\n  - This user has balanced preferences"

    return result


@tool
def get_similar_liked_dishes(dish_name: str = "") -> str:
    """
    Find dishes similar to ones the user has liked, or suggest based on overall preferences.

    Args:
        dish_name: Optional specific dish to find similar items to.

    Returns:
        Suggestions for dishes the user might like based on their history.
    """
    feedback_df = _get_feedback_df()
    menu_df = _get_menu_df()

    if feedback_df is None or feedback_df.empty or _user_id is None:
        return "No feedback history available to make personalized suggestions."

    if menu_df is None or menu_df.empty:
        return "No menu data available to find similar dishes."

    user_feedback = feedback_df[feedback_df['user_id'] == _user_id].copy()
    liked = user_feedback[user_feedback['liked'] == 1]['dish_name'].tolist()

    if not liked:
        return "No liked dishes recorded yet. Rate some dishes to get personalized suggestions!"

    # Find categories of liked dishes
    liked_categories = []
    for liked_dish in liked:
        match = menu_df[menu_df['dish_name'].str.lower() == liked_dish.lower()]
        if not match.empty:
            liked_categories.append(match.iloc[0]['category'])

    if not liked_categories:
        return f"Could not match liked dishes to current menu. Past favorites: {', '.join(liked[:5])}"

    # Find dishes in same categories that haven't been rated
    rated_dishes = user_feedback['dish_name'].str.lower().tolist()
    cat_counts = Counter(liked_categories)
    top_categories = [cat for cat, _ in cat_counts.most_common(3)]

    suggestions = []
    for category in top_categories:
        cat_dishes = menu_df[menu_df['category'] == category]
        for _, dish in cat_dishes.iterrows():
            if dish['dish_name'].lower() not in rated_dishes:
                suggestions.append({
                    'name': dish['dish_name'],
                    'category': category,
                    'dining_hall': dish['dining_hall'],
                    'meal': dish['meal_period'],
                })
                if len(suggestions) >= 5:
                    break
        if len(suggestions) >= 5:
            break

    if not suggestions:
        return f"You've rated most dishes in your preferred categories! Your favorites were: {', '.join(liked[:5])}"

    result = f"""Based on your taste preferences, you might enjoy:

"""
    for sug in suggestions:
        result += f"- **{sug['name']}** ({sug['category']})\n"
        result += f"  Available at: {sug['dining_hall']} - {sug['meal']}\n"

    result += f"\nThese are from categories you've enjoyed: {', '.join(top_categories)}"

    return result
