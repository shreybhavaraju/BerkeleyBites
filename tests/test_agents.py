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

from backend.agents.food_availability_agent import (
    get_available_dishes,
    get_menu_summary,
    set_menu_data,
)
from backend.agents.taste_preferences_agent import (
    get_taste_preferences,
    get_similar_liked_dishes,
    set_feedback_data,
)
from backend.agents.orchestrator import (
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
            "created_at": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_003",
            "dish_name": "Tomato Soup",
            "liked": 1,
            "created_at": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_004",
            "dish_name": "Pepperoni Pizza",
            "liked": 0,
            "created_at": datetime.now().isoformat(),
            "date": str(date.today()),
        },
        {
            "user_id": "test_user_123",
            "dish_id": "dish_002",
            "dish_name": "Grilled Chicken Sandwich",
            "liked": 1,
            "created_at": datetime.now().isoformat(),
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
                "created_at": datetime.now().isoformat(),
                "date": str(date.today()),
            },
            {
                "user_id": "test_user",
                "dish_id": "dish_002",
                "dish_name": "Another Dish",
                "liked": 0,
                "created_at": datetime.now().isoformat(),
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

        # gather_agent_context now takes question_context for mood
        context = gather_agent_context(meal="Lunch", question_context={"mood": "happy"})

        assert "mood" in context
        assert "preferences" in context
        assert "dishes" in context

        # Mood should reflect happy (passed through question_context)
        assert context["mood"] == "happy"

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

        # Mood is now passed through question_context
        context = gather_agent_context(meal="", question_context={"mood": "tired"})

        # All context should be gathered
        assert len(context) == 3
        assert all(key in context for key in ["mood", "preferences", "dishes"])

        # Mood should be tired (from question_context)
        assert context["mood"] == "tired"

    def test_mood_affects_context(self, sample_menu_df, sample_feedback_df, sample_user_profile):
        """Test that mood changes affect the context."""
        set_orchestrator_context(
            menu_df=sample_menu_df,
            feedback_df=sample_feedback_df,
            user_profile=sample_user_profile,
            user_id="test_user",
            user_mood="stressed"
        )

        # Mood is now passed through question_context
        context_stressed = gather_agent_context(question_context={"mood": "stressed"})
        context_adventurous = gather_agent_context(question_context={"mood": "adventurous"})

        # Contexts should have different moods
        assert context_stressed["mood"] != context_adventurous["mood"]
        assert context_stressed["mood"] == "stressed"
        assert context_adventurous["mood"] == "adventurous"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
