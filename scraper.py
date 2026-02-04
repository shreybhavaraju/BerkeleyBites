"""
BerkeleyBites Scraper

Scrapes UC Berkeley dining hall menus and transforms them into a clean DataFrame.
Combines scraping and transformation into a single module.

Data is stored in Supabase (PostgreSQL).
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def is_data_fresh() -> bool:
    """
    Check if menu data exists and was scraped today.

    Returns:
        True if data is from today, False if stale or missing.
    """
    try:
        from backend.database import is_menu_fresh
        return is_menu_fresh()
    except Exception as e:
        print(f"Database check failed: {e}")
        return False


def scrape_website() -> dict:
    """
    Scrape Berkeley dining website.

    Returns:
        Nested dictionary with structure:
        {dining_hall: {status, meals: {meal_period: {category: [items]}}}}
    """
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all dining halls
    all_dining_halls = soup.find_all('li', class_='location-name')

    dining_data = {}

    for hall in all_dining_halls:
        # Get dining hall name and status
        hall_name = hall.find('span', class_='cafe-title').text.strip()
        hall_status = hall.find('span', class_='status').text.strip()

        dining_data[hall_name] = {
            "status": hall_status,
            "meals": {}
        }

        # Find all meal periods for this dining hall
        meal_periods = hall.find_all('li', class_='preiod-name')

        for meal in meal_periods:
            meal_name = meal.find('span').text.strip()
            meal_name = meal_name.replace('', '').strip()

            dining_data[hall_name]["meals"][meal_name] = {}

            # Find all categories in this meal
            categories = meal.find_all('div', class_='cat-name')

            for category in categories:
                cat_name = category.find('span').text.strip()
                dining_data[hall_name]["meals"][meal_name][cat_name] = []

                # Find all food items in this category
                food_items = category.find_all('li', class_='recip')

                for item in food_items:
                    food_name = item.find('span').text.strip()

                    # Get tags (allergens/dietary info)
                    item_classes = item.get('class', [])
                    tags = [c for c in item_classes if c != 'recip']

                    food_dict = {
                        "name": food_name,
                        "tags": tags
                    }
                    dining_data[hall_name]["meals"][meal_name][cat_name].append(food_dict)

    return dining_data


def transform_to_dataframe(dining_data: dict) -> pd.DataFrame:
    """
    Transform nested dictionary into a flat pandas DataFrame.

    Each row represents one dish at one dining hall for one meal.

    Args:
        dining_data: Nested dict from scrape_website()

    Returns:
        Flat DataFrame with boolean columns for dietary tags.
    """
    rows = []

    for hall_name, hall_info in dining_data.items():
        hall_status = hall_info.get("status", "Unknown")
        meals = hall_info.get("meals", {})

        for meal_name, meal_data in meals.items():
            for category_name, items in meal_data.items():
                for item in items:
                    dish_name = item["name"]
                    tags = item.get("tags", [])

                    row = {
                        # Identifiers
                        'dish_name': dish_name,
                        'dining_hall': hall_name,
                        'dining_hall_status': hall_status,
                        'meal_period': meal_name,
                        'category': category_name,

                        # Allergens
                        'has_milk': 'milk' in tags,
                        'has_egg': 'egg' in tags,
                        'has_fish': 'fish' in tags,
                        'has_shellfish': 'shellfish' in tags,
                        'has_tree_nuts': 'tree-nuts' in tags,
                        'has_wheat': 'wheat' in tags,
                        'has_peanuts': 'peanuts' in tags,
                        'has_soybeans': 'soybeans' in tags,
                        'has_sesame': 'sesame' in tags,
                        'has_gluten': 'gluten' in tags,

                        # Dietary options
                        'is_vegan': 'vegan-option' in tags,
                        'is_vegetarian': 'vegetarian-option' in tags,
                        'is_halal': 'halal' in tags,
                        'is_kosher': 'kosher' in tags,

                        # Other
                        'has_pork': 'pork' in tags,
                        'has_alcohol': 'alcohol' in tags,

                        # Metadata
                        'scrape_date': str(date.today())
                    }

                    rows.append(row)

    df = pd.DataFrame(rows)

    # Add unique ID for each row
    if not df.empty:
        df.insert(0, 'dish_id', range(1, len(df) + 1))

    return df


def scrape_and_transform() -> pd.DataFrame:
    """
    Main entry point: scrape website, transform data, save to Supabase.

    Returns:
        Clean DataFrame ready for use in the app.
    """
    # Scrape
    data = scrape_website()

    # Transform
    df = transform_to_dataframe(data)

    # Save to Supabase
    try:
        from backend.database import upsert_dishes
        dishes = df.to_dict('records')
        count = upsert_dishes(dishes)
        print(f"Saved {count} dishes to Supabase")
    except Exception as e:
        print(f"Failed to save to Supabase: {e}")
        raise

    return df


def generate_embeddings_for_new_dishes(batch_size: int = 50) -> int:
    """
    Generate embeddings for dishes that don't have them.

    This should be called after scraping to ensure all dishes have embeddings.

    Args:
        batch_size: Number of dishes to process at once

    Returns:
        Number of dishes with embeddings generated
    """
    try:
        from backend.database import get_dishes_without_embeddings, batch_update_embeddings
        from agents.embedding_service import generate_batch_embeddings
    except ImportError as e:
        print(f"Cannot generate embeddings - missing dependencies: {e}")
        return 0

    total_generated = 0

    while True:
        # Get dishes without embeddings
        dishes = get_dishes_without_embeddings(limit=batch_size)

        if not dishes:
            break

        print(f"Generating embeddings for {len(dishes)} dishes...")

        # Generate embeddings
        results = generate_batch_embeddings(dishes)

        # Format for database update
        updates = [
            {
                "dish_id": dish_id,
                "embedding": embedding,
                "embedding_text": text
            }
            for dish_id, text, embedding in results
        ]

        # Update database
        count = batch_update_embeddings(updates)
        total_generated += count
        print(f"  Updated {count} dishes")

        # If we got fewer than batch_size, we're done
        if len(dishes) < batch_size:
            break

    return total_generated


def scrape_and_generate_embeddings() -> tuple[pd.DataFrame, int]:
    """
    Full pipeline: scrape, save, and generate embeddings.

    Returns:
        Tuple of (DataFrame, number of embeddings generated)
    """
    # Scrape and save
    df = scrape_and_transform()

    # Generate embeddings for new dishes
    embedding_count = generate_embeddings_for_new_dishes()

    return df, embedding_count


if __name__ == "__main__":
    import sys

    print("Scraping Berkeley dining website...")
    df = scrape_and_transform()
    print(f"\nStatistics:")
    print(f"  Total dishes: {len(df)}")
    print(f"  Dining halls: {df['dining_hall'].nunique()}")
    print(f"  Vegan options: {df['is_vegan'].sum()}")
    print(f"  Vegetarian options: {df['is_vegetarian'].sum()}")

    # Generate embeddings if requested
    if "--embeddings" in sys.argv or "-e" in sys.argv:
        print("\nGenerating embeddings...")
        count = generate_embeddings_for_new_dishes()
        print(f"  Generated embeddings for {count} dishes")
