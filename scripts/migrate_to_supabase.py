#!/usr/bin/env python3
"""
BerkeleyBites Migration Script

Migrates existing CSV data to Supabase database.
- Reads dining_data_clean.csv -> inserts into `dishes` table
- Reads feedback.csv (if exists) -> inserts into `feedback` table

Run: python scripts/migrate_to_supabase.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from backend.database import get_client, upsert_dishes


def migrate_dishes(csv_path: str) -> int:
    """
    Migrate dishes from CSV to Supabase.

    Args:
        csv_path: Path to dining_data_clean.csv

    Returns:
        Number of dishes migrated.
    """
    print(f"Reading dishes from {csv_path}...")

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} dishes in CSV")

    # Convert DataFrame to list of dicts
    dishes = df.to_dict("records")

    # Convert boolean columns (pandas reads them as strings)
    bool_columns = [
        "has_milk", "has_egg", "has_fish", "has_shellfish",
        "has_tree_nuts", "has_wheat", "has_peanuts", "has_soybeans",
        "has_sesame", "has_gluten", "is_vegan", "is_vegetarian",
        "is_halal", "is_kosher", "has_pork", "has_alcohol"
    ]

    for dish in dishes:
        for col in bool_columns:
            if col in dish:
                # Handle various truthy values
                val = dish[col]
                if isinstance(val, str):
                    dish[col] = val.lower() in ("true", "1", "yes")
                elif isinstance(val, (int, float)):
                    dish[col] = bool(val)

    print("Upserting dishes to Supabase...")
    count = upsert_dishes(dishes)
    print(f"Successfully migrated {count} dishes")

    return count


def migrate_feedback(csv_path: str) -> int:
    """
    Migrate feedback from CSV to Supabase.

    Note: This requires dishes to be migrated first to get proper dish_ids.

    Args:
        csv_path: Path to feedback.csv

    Returns:
        Number of feedback entries migrated.
    """
    print(f"\nReading feedback from {csv_path}...")

    if not os.path.exists(csv_path):
        print("No feedback.csv found - skipping feedback migration")
        return 0

    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} feedback entries in CSV")

    if df.empty:
        print("Feedback CSV is empty - skipping")
        return 0

    client = get_client()

    # Get dish mapping (dish_name -> dish_id from database)
    # We need to match by dish_name since CSV dish_ids may not match DB ids
    dishes_response = client.table("dishes").select("id, dish_name").execute()
    dish_map = {d["dish_name"].lower(): d["id"] for d in dishes_response.data}

    migrated = 0
    skipped = 0

    for _, row in df.iterrows():
        dish_name = row.get("dish_name", "")
        dish_id = dish_map.get(dish_name.lower())

        if not dish_id:
            # Try to find dish by original dish_id if available
            original_id = row.get("dish_id")
            if original_id:
                # Look up by matching index in today's dishes
                for name, db_id in dish_map.items():
                    if db_id == original_id:
                        dish_id = db_id
                        break

        if not dish_id:
            skipped += 1
            continue

        feedback_data = {
            "user_id": row.get("user_id", "default"),
            "dish_id": dish_id,
            "dish_name": dish_name,
            "liked": bool(row.get("liked", 0)),
            "rating_date": row.get("date", str(pd.Timestamp.today().date()))
        }

        try:
            client.table("feedback").upsert(
                feedback_data,
                on_conflict="user_id,dish_id,rating_date"
            ).execute()
            migrated += 1
        except Exception as e:
            print(f"Error migrating feedback for {dish_name}: {e}")
            skipped += 1

    print(f"Migrated {migrated} feedback entries, skipped {skipped}")
    return migrated


def verify_migration():
    """Verify migration by checking row counts."""
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)

    client = get_client()

    # Count dishes
    dishes_response = client.table("dishes").select("id", count="exact").execute()
    print(f"Dishes in database: {dishes_response.count}")

    # Count feedback
    feedback_response = client.table("feedback").select("id", count="exact").execute()
    print(f"Feedback in database: {feedback_response.count}")

    # Count user profiles
    profiles_response = client.table("user_profiles").select("id", count="exact").execute()
    print(f"User profiles: {profiles_response.count}")

    # Count user moods
    moods_response = client.table("user_moods").select("id", count="exact").execute()
    print(f"User moods: {moods_response.count}")

    # Sample dishes
    print("\nSample dishes:")
    sample = client.table("dishes").select("dish_name, dining_hall, meal_period").limit(5).execute()
    for dish in sample.data:
        print(f"  - {dish['dish_name']} @ {dish['dining_hall']} ({dish['meal_period']})")


def main():
    """Run the migration."""
    print("=" * 50)
    print("BerkeleyBites Migration to Supabase")
    print("=" * 50)

    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("\nERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        print("Run 'supabase start' and copy values from 'supabase status'")
        sys.exit(1)

    base_path = Path(__file__).parent.parent

    # Migrate dishes
    dishes_csv = base_path / "dining_data_clean.csv"
    dishes_count = migrate_dishes(str(dishes_csv))

    if dishes_count == 0:
        print("\nNo dishes migrated. Please ensure dining_data_clean.csv exists.")
        print("Run the scraper first: python scraper.py")
        sys.exit(1)

    # Migrate feedback
    feedback_csv = base_path / "feedback.csv"
    migrate_feedback(str(feedback_csv))

    # Verify
    verify_migration()

    print("\n" + "=" * 50)
    print("Migration complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
