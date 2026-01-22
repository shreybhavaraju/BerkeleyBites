"""
BerkeleyBites Scraper

Scrapes UC Berkeley dining hall menus and transforms them into a clean DataFrame.
Combines scraping and transformation into a single module.
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date


def is_data_fresh() -> bool:
    """
    Check if dining_data_clean.csv exists and was scraped today.

    Returns:
        True if data is from today, False if stale or missing.
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'dining_data_clean.csv')

    if not os.path.exists(csv_path):
        return False

    try:
        df = pd.read_csv(csv_path)
        if 'scrape_date' not in df.columns or df.empty:
            return False
        return df['scrape_date'].iloc[0] == str(date.today())
    except Exception:
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
    Main entry point: scrape website, transform data, save to CSV.

    Returns:
        Clean DataFrame ready for use in the app.
    """
    # Scrape
    data = scrape_website()

    # Transform
    df = transform_to_dataframe(data)

    # Save to CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'dining_data_clean.csv')
    df.to_csv(csv_path, index=False)

    return df


if __name__ == "__main__":
    print("Scraping Berkeley dining website...")
    df = scrape_and_transform()
    print(f"Saved {len(df)} dishes to dining_data_clean.csv")
    print(f"\nStatistics:")
    print(f"  Dining halls: {df['dining_hall'].nunique()}")
    print(f"  Vegan options: {df['is_vegan'].sum()}")
    print(f"  Vegetarian options: {df['is_vegetarian'].sum()}")
