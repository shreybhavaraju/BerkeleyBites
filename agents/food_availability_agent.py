"""
Food Availability Agent for BerkeleyBites

A deterministic agent that queries the menu DataFrame to find available dishes.
"""

from typing import Optional
import pandas as pd
from langchain_core.tools import tool

# Global menu DataFrame (set by orchestrator)
_menu_df: Optional[pd.DataFrame] = None


def set_menu_data(menu_df: pd.DataFrame) -> None:
    """Set the menu DataFrame (called by orchestrator)."""
    global _menu_df
    _menu_df = menu_df


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
        print(f"Database query failed: {e}")

    return _menu_df


@tool
def get_available_dishes(
    meal_period: str = "",
    dining_hall: str = "",
    category: str = "",
    is_vegetarian: bool = False,
    is_vegan: bool = False,
    limit: int = 15
) -> str:
    """
    Get available dishes from today's menu with optional filters.

    Args:
        meal_period: Filter by meal (e.g., "Breakfast", "Lunch", "Dinner"). Empty for all.
        dining_hall: Filter by dining hall name. Empty for all.
        category: Filter by food category (e.g., "Entrees", "Soups"). Empty for all.
        is_vegetarian: If True, only show vegetarian options.
        is_vegan: If True, only show vegan options.
        limit: Maximum number of dishes to return (default 15).

    Returns:
        A formatted string listing available dishes with their details.
    """
    menu_df = _get_menu_df()

    if menu_df is None or menu_df.empty:
        return "No menu data available. The menu may not have been loaded yet."

    df = menu_df.copy()

    # Apply filters
    if meal_period:
        df = df[df['meal_period'].str.lower().str.contains(meal_period.lower())]

    if dining_hall:
        df = df[df['dining_hall'].str.lower().str.contains(dining_hall.lower())]

    if category:
        df = df[df['category'].str.lower().str.contains(category.lower())]

    if is_vegan:
        df = df[df['is_vegan'] == True]
    elif is_vegetarian:
        df = df[df['is_vegetarian'] == True]

    if df.empty:
        return f"No dishes found matching the specified filters."

    # Format results
    total_count = len(df)

    # Sample dishes from multiple dining halls for variety (instead of just taking first N)
    if len(df) > limit:
        # Group by dining hall and sample proportionally
        sampled_dfs = []
        halls = df['dining_hall'].unique()
        per_hall = max(1, limit // len(halls))

        for hall in halls:
            hall_df = df[df['dining_hall'] == hall]
            sample_size = min(len(hall_df), per_hall)
            sampled_dfs.append(hall_df.sample(n=sample_size, random_state=42))

        df = pd.concat(sampled_dfs).head(limit)
    else:
        df = df.head(limit)

    results = []
    results.append(f"Found {total_count} dishes{f' (showing first {limit})' if total_count > limit else ''}:\n")

    for _, dish in df.iterrows():
        tags = []
        if dish.get('is_vegan'):
            tags.append("VEGAN")
        elif dish.get('is_vegetarian'):
            tags.append("VEGETARIAN")
        if dish.get('is_halal'):
            tags.append("HALAL")
        if dish.get('is_kosher'):
            tags.append("KOSHER")

        tag_str = f" [{', '.join(tags)}]" if tags else ""

        results.append(
            f"- {dish['dish_name']}{tag_str}\n"
            f"  Location: {dish['dining_hall']} | {dish['meal_period']} | {dish['category']}"
        )

    return "\n".join(results)


@tool
def get_menu_summary() -> str:
    """
    Get a summary of today's menu including dining halls, meal periods, and dish counts.

    Returns:
        A formatted string with menu overview statistics.
    """
    menu_df = _get_menu_df()

    if menu_df is None or menu_df.empty:
        return "No menu data available."

    df = menu_df

    # Gather statistics
    total_dishes = len(df)
    dining_halls = df['dining_hall'].unique().tolist()
    meal_periods = df['meal_period'].unique().tolist()
    categories = df['category'].unique().tolist()

    # Dietary counts
    vegan_count = df['is_vegan'].sum() if 'is_vegan' in df.columns else 0
    vegetarian_count = df['is_vegetarian'].sum() if 'is_vegetarian' in df.columns else 0
    halal_count = df['is_halal'].sum() if 'is_halal' in df.columns else 0

    # Build summary
    summary = f"""Today's Menu Summary:

Total Dishes Available: {total_dishes}

Dining Halls ({len(dining_halls)}):
{chr(10).join(f'  - {hall}' for hall in dining_halls)}

Meal Periods:
{chr(10).join(f'  - {meal}' for meal in meal_periods)}

Food Categories ({len(categories)}):
{chr(10).join(f'  - {cat}' for cat in categories[:10])}
{f'  ... and {len(categories) - 10} more categories' if len(categories) > 10 else ''}

Dietary Options:
  - Vegan dishes: {vegan_count}
  - Vegetarian dishes: {vegetarian_count}
  - Halal dishes: {halal_count}
"""

    # Dishes per dining hall
    summary += "\nDishes by Dining Hall:\n"
    for hall in dining_halls:
        count = len(df[df['dining_hall'] == hall])
        summary += f"  - {hall}: {count} dishes\n"

    return summary
