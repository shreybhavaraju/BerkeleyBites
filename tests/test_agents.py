"""
Unit tests for BerkeleyBites Multi-Agent System
"""

import pytest
import pandas as pd
from datetime import date, datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.mood_agent import get_user_mood, set_user_mood, MOOD_GUIDANCE
from agents.food_availability_agent import (
    get_available_dishes,
    get_menu_summary,
    set_menu_data,
)
from agents.taste_preferences_agent import (
    get_taste_preferences,
    get_similar_liked_dishes,
    set_feedback_data,
)
from agents.orchestrator import (
    set_orchestrator_context,
    get_user_profile_str,
    gather_agent_context,
)


# ============================================
# TEST FIXTURES
# ============================================

@pytest.fixture
def sample_menu_df():
    """Create a sample menu DataFrame for testing."""
    return pd.DataFrame([
        {
            "dish_id": "dish_001",
            "dish_name": "Vegan Buddha Bowl",
            "dining_hall": "Crossroads",
            "meal_period": "Lunch",
            "category": "Entrees",
            "is_vegan": True,
            "is_vegetarian": True,
            "is_halal": True,
            "is_kosher": False,
            "has_gluten": False,
            "has_milk": False,
            "has_egg": False,
            "has_fish": False,
            "has_pork": False,
            "has_shellfish": False,
            "has_tree_nuts": False,
            "has_soybeans": True,
        },
        {
            "dish_id": "dish_002",
            "dish_name": "Grilled Chicken Sandwich",
            "dining_hall": "Crossroads",
            "meal_period": "Lunch",
            "category": "Grill",
            "is_vegan": False,
            "is_vegetarian": False,
            "is_halal": True,
            "is_kosher": False,
            "has_gluten": True,
            "has_milk": False,
            "has_egg": False,
            "has_fish": False,
            "has_pork": False,
            "has_shellfish": False,
            "has_tree_nuts": False,
            "has_soybeans": False,
        },
        {
            "dish_id": "dish_003",
            "dish_name": "Tomato Soup",
            "dining_hall": "Cafe 3",
            "meal_period": "Dinner",
            "category": "Soups",
            "is_vegan": True,
            "is_vegetarian": True,
            "is_halal": True,
            "is_kosher": True,
            "has_gluten": False,
            "has_milk": False,
            "has_egg": False,
            "has_fish": False,
            "has_pork": False,
            "has_shellfish": False,
            "has_tree_nuts": False,
            "has_soybeans": False,
        },
        {
            "dish_id": "dish_004",
            "dish_name": "Pepperoni Pizza",
            "dining_hall": "Cafe 3",
            "meal_period": "Dinner",
            "category": "Pizza",
            "is_vegan": False,
            "is_vegetarian": False,
            "is_halal": False,
            "is_kosher": False,
            "has_gluten": True,
            "has_milk": True,
            "has_egg": False,
            "has_fish": False,
            "has_pork": True,
            "has_shellfish": False,
            "has_tree_nuts": False,
            "has_soybeans": False,
        },
        {
            "dish_id": "dish_005",
            "dish_name": "Caesar Salad",
            "dining_hall": "Crossroads",
            "meal_period": "Lunch",
            "category": "Salads",
            "is_vegan": False,
            "is_vegetarian": True,
            "is_halal": True,
            "is_kosher": False,
            "has_gluten": True,
            "has_milk": True,
            "has_egg": True,
            "has_fish": False,
            "has_pork": False,
            "has_shellfish": False,
            "has_tree_nuts": False,
            "has_soybeans": False,
        },
    ])


@pytest.fixture
def sample_feedback_df():
    """Create a sample feedback DataFrame for testing."""
    return pd.DataFrame([
        {
            "user_id": "test_user_123",
            "dish_id": "dish_001",
            "dish_name": "Vegan Buddha Bowl",
            "liked": 1,
            "timestamp": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_003",
            "dish_name": "Tomato Soup",
            "liked": 1,
            "timestamp": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_004",
            "dish_name": "Pepperoni Pizza",
            "liked": 0,
            "timestamp": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_002",
            "dish_name": "Grilled Chicken Sandwich",
            "liked": 1,
            "timestamp": datetime.now().isoformat(),
            "date": str(date.today()),
        },
    ])


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return {
        "is_vegetarian": False,
        "is_vegan": False,
        "is_pescatarian": False,
        "is_halal": False,
        "is_kosher": False,
        "avoid_milk": False,
        "avoid_eggs": False,
        "avoid_gluten": False,
        "avoid_nuts": False,
        "avoid_soy": False,
    }


# ============================================
# MOOD AGENT TESTS
# ============================================

class TestMoodAgent:
    """Tests for the Mood Agent."""

    def test_set_and_get_mood(self):
        """Test setting and getting user mood."""
        set_user_mood("grumpy")
        result = get_user_mood.invoke({})

        assert "GRUMPY" in result
        assert "comfort food" in result.lower()

    def test_all_moods_have_guidance(self):
        """Test that all moods have defined guidance."""
        moods = ["happy", "grumpy", "stressed", "tired", "adventurous"]

        for mood in moods:
            assert mood in MOOD_GUIDANCE
            assert "description" in MOOD_GUIDANCE[mood]
            assert "food_suggestion" in MOOD_GUIDANCE[mood]
            assert "prefer_categories" in MOOD_GUIDANCE[mood]

    def test_mood_happy(self):
        """Test happy mood guidance."""
        set_user_mood("happy")
        result = get_user_mood.invoke({})

        assert "HAPPY" in result
        assert "adventurous" in result.lower() or "celebratory" in result.lower()

    def test_mood_stressed(self):
        """Test stressed mood guidance."""
        set_user_mood("stressed")
        result = get_user_mood.invoke({})

        assert "STRESSED" in result
        assert "light" in result.lower() or "easy" in result.lower()

    def test_mood_tired(self):
        """Test tired mood guidance."""
        set_user_mood("tired")
        result = get_user_mood.invoke({})

        assert "TIRED" in result
        assert "energy" in result.lower() or "protein" in result.lower()

    def test_invalid_mood_defaults_to_current(self):
        """Test that invalid mood doesn't crash."""
        set_user_mood("happy")  # Set a valid mood first
        set_user_mood("invalid_mood")  # Try invalid
        result = get_user_mood.invoke({})

        # Should still return valid result (keeps previous mood)
        assert "Current Mood:" in result


# ============================================
# FOOD AVAILABILITY AGENT TESTS
# ============================================

class TestFoodAvailabilityAgent:
    """Tests for the Food Availability Agent."""

    def test_get_available_dishes_no_filter(self, sample_menu_df):
        """Test getting all dishes without filters."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({})

        assert "Found 5 dishes" in result
        assert "Vegan Buddha Bowl" in result
        assert "Grilled Chicken Sandwich" in result

    def test_get_available_dishes_meal_filter(self, sample_menu_df):
        """Test filtering by meal period."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({"meal_period": "Lunch"})

        assert "Vegan Buddha Bowl" in result
        assert "Grilled Chicken Sandwich" in result
        assert "Tomato Soup" not in result  # Dinner only

    def test_get_available_dishes_vegan_filter(self, sample_menu_df):
        """Test filtering for vegan dishes."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({"is_vegan": True})

        assert "Vegan Buddha Bowl" in result
        assert "Tomato Soup" in result
        assert "Grilled Chicken" not in result
        assert "VEGAN" in result

    def test_get_available_dishes_vegetarian_filter(self, sample_menu_df):
        """Test filtering for vegetarian dishes."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({"is_vegetarian": True})

        assert "Caesar Salad" in result
        assert "VEGETARIAN" in result

    def test_get_available_dishes_dining_hall_filter(self, sample_menu_df):
        """Test filtering by dining hall."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({"dining_hall": "Cafe 3"})

        assert "Tomato Soup" in result
        assert "Pepperoni Pizza" in result
        assert "Vegan Buddha Bowl" not in result  # Crossroads only

    def test_get_menu_summary(self, sample_menu_df):
        """Test menu summary generation."""
        set_menu_data(sample_menu_df)
        result = get_menu_summary.invoke({})

        assert "Total Dishes Available: 5" in result
        assert "Crossroads" in result
        assert "Cafe 3" in result
        assert "Vegan dishes:" in result
        assert "Vegetarian dishes:" in result

    def test_no_menu_data(self):
        """Test handling when no menu data is set."""
        set_menu_data(pd.DataFrame())
        result = get_available_dishes.invoke({})

        assert "No menu data available" in result

    def test_limit_parameter(self, sample_menu_df):
        """Test that limit parameter works."""
        set_menu_data(sample_menu_df)
        result = get_available_dishes.invoke({"limit": 2})

        assert "showing first 2" in result


# ============================================
# TASTE PREFERENCES AGENT TESTS
# ============================================

class TestTastePreferencesAgent:
    """Tests for the Taste Preferences Agent."""

    def test_get_taste_preferences_with_history(self, sample_feedback_df, sample_menu_df):
        """Test getting preferences with feedback history."""
        set_feedback_data(sample_feedback_df, "test_user_123", sample_menu_df)
        result = get_taste_preferences.invoke({})

        assert "Liked Dishes" in result
        assert "Vegan Buddha Bowl" in result
        assert "Disliked Dishes" in result
        assert "Pepperoni Pizza" in result

    def test_get_taste_preferences_new_user(self):
        """Test preferences for new user with no history."""
        set_feedback_data(pd.DataFrame(), "new_user", None)
        result = get_taste_preferences.invoke({})

        assert "No feedback history" in result or "new user" in result.lower()

    def test_get_taste_preferences_insufficient_history(self, sample_menu_df):
        """Test with insufficient feedback count."""
        # Create feedback with only 2 entries (below threshold)
        small_feedback = pd.DataFrame([
            {
                "user_id": "test_user",
                "dish_id": "dish_001",
                "dish_name": "Test Dish",
                "liked": 1,
                "timestamp": datetime.now().isoformat(),
                "date": str(date.today()),
            },
            {
                "user_id": "test_user",
                "dish_id": "dish_002",
                "dish_name": "Another Dish",
                "liked": 0,
                "timestamp": datetime.now().isoformat(),
                "date": str(date.today()),
            },
        ])
        set_feedback_data(small_feedback, "test_user", sample_menu_df)
        result = get_taste_preferences.invoke({})

        assert "Limited feedback" in result or "Need at least" in result

    def test_get_similar_liked_dishes(self, sample_feedback_df, sample_menu_df):
        """Test finding similar dishes."""
        set_feedback_data(sample_feedback_df, "test_user_123", sample_menu_df)
        result = get_similar_liked_dishes.invoke({})

        # Should suggest dishes or mention preferences
        assert "Based on" in result or "favorites" in result or "No liked dishes" in result

    def test_get_similar_liked_dishes_no_history(self):
        """Test similar dishes with no history."""
        set_feedback_data(pd.DataFrame(), "new_user", pd.DataFrame())
        result = get_similar_liked_dishes.invoke({})

        assert "No feedback history" in result


# ============================================
# ORCHESTRATOR TESTS
# ============================================

class TestOrchestrator:
    """Tests for the Orchestrator."""

    def test_set_orchestrator_context(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test setting orchestrator context."""
        # Should not raise any exceptions
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user_123",
            user_mood="happy"
        )

    def test_get_user_profile_str_no_restrictions(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test profile string with no restrictions."""
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user",
            user_mood="happy"
        )
        result = get_user_profile_str()

        assert result == "No dietary restrictions"

    def test_get_user_profile_str_vegan(self, sample_menu_df, sample_feedback_df):
        """Test profile string for vegan user."""
        vegan_profile = {
            "is_vegan": True,
            "is_vegetarian": False,
            "avoid_gluten": True,
        }
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=vegan_profile,
            user_id="test_user",
            user_mood="happy"
        )
        result = get_user_profile_str()

        assert "VEGAN" in result
        assert "gluten" in result

    def test_gather_agent_context(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test gathering context from all agents."""
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user_123",
            user_mood="happy"
        )

        context = gather_agent_context(meal="Lunch")

        assert "mood" in context
        assert "preferences" in context
        assert "dishes" in context

        # Mood should reflect happy
        assert "HAPPY" in context["mood"]

        # Dishes should be filtered for lunch
        assert "Vegan Buddha Bowl" in context["dishes"]


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests for the multi-agent system."""

    def test_full_context_gathering(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test full context gathering flow."""
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user_123",
            user_mood="tired"
        )

        context = gather_agent_context(meal="")

        # All context should be gathered
        assert len(context) == 3
        assert all(key in context for key in ["mood", "preferences", "dishes"])

        # Mood should be tired
        assert "TIRED" in context["mood"]
        assert "energy" in context["mood"].lower()

    def test_mood_affects_context(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test that mood changes affect the context."""
        # Set stressed mood
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user",
            user_mood="stressed"
        )
        context_stressed = gather_agent_context()

        # Set adventurous mood
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user",
            user_mood="adventurous"
        )
        context_adventurous = gather_agent_context()

        # Contexts should be different
        assert context_stressed["mood"] != context_adventurous["mood"]
        assert "STRESSED" in context_stressed["mood"]
        assert "ADVENTUROUS" in context_adventurous["mood"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
