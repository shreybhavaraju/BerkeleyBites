"""
End-to-end tests for BerkeleyBites Multi-Agent System

These tests verify the complete recommendation flow without making actual LLM calls.
"""

import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import (
    set_orchestrator_context,
    get_recommendation,
    build_recommendation_prompt,
    gather_agent_context,
    clear_orchestrator_history,
    print("HI")
)


@pytest.fixture
def full_menu_df():
    """Create a comprehensive menu DataFrame for e2e testing."""
    dishes = [
        # Breakfast items
        {"dish_id": "b1", "dish_name": "Scrambled Eggs", "dining_hall": "Crossroads", "meal_period": "Breakfast", "category": "Hot Breakfast", "is_vegan": False, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": False, "has_milk": True, "has_egg": True, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "b2", "dish_name": "Oatmeal with Berries", "dining_hall": "Crossroads", "meal_period": "Breakfast", "category": "Hot Cereal", "is_vegan": True, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": True, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "b3", "dish_name": "Bacon Strips", "dining_hall": "Cafe 3", "meal_period": "Breakfast", "category": "Hot Breakfast", "is_vegan": False, "is_vegetarian": False, "is_halal": False, "is_kosher": False, "has_gluten": False, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": True, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},

        # Lunch items
        {"dish_id": "l1", "dish_name": "Chicken Teriyaki Bowl", "dining_hall": "Crossroads", "meal_period": "Lunch", "category": "Entrees", "is_vegan": False, "is_vegetarian": False, "is_halal": True, "is_kosher": False, "has_gluten": True, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": True},
        {"dish_id": "l2", "dish_name": "Mediterranean Salad", "dining_hall": "Crossroads", "meal_period": "Lunch", "category": "Salads", "is_vegan": True, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": False, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "l3", "dish_name": "Tomato Basil Soup", "dining_hall": "Cafe 3", "meal_period": "Lunch", "category": "Soups", "is_vegan": True, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": False, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "l4", "dish_name": "BBQ Pulled Pork Sandwich", "dining_hall": "Cafe 3", "meal_period": "Lunch", "category": "Grill", "is_vegan": False, "is_vegetarian": False, "is_halal": False, "is_kosher": False, "has_gluten": True, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": True, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},

        # Dinner items
        {"dish_id": "d1", "dish_name": "Grilled Salmon", "dining_hall": "Crossroads", "meal_period": "Dinner", "category": "Entrees", "is_vegan": False, "is_vegetarian": False, "is_halal": True, "is_kosher": False, "has_gluten": False, "has_milk": False, "has_egg": False, "has_fish": True, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "d2", "dish_name": "Mushroom Risotto", "dining_hall": "Crossroads", "meal_period": "Dinner", "category": "Entrees", "is_vegan": False, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": False, "has_milk": True, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
        {"dish_id": "d3", "dish_name": "Vegan Stir Fry", "dining_hall": "Cafe 3", "meal_period": "Dinner", "category": "Entrees", "is_vegan": True, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": True, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": True},
        {"dish_id": "d4", "dish_name": "Minestrone Soup", "dining_hall": "Cafe 3", "meal_period": "Dinner", "category": "Soups", "is_vegan": True, "is_vegetarian": True, "is_halal": True, "is_kosher": True, "has_gluten": True, "has_milk": False, "has_egg": False, "has_fish": False, "has_pork": False, "has_shellfish": False, "has_tree_nuts": False, "has_soybeans": False},
    ]
    return pd.DataFrame(dishes)


@pytest.fixture
def user_feedback_df():
    """Create feedback history for testing."""
    return pd.DataFrame([
        {"user_id": "e2e_user", "dish_id": "l1", "dish_name": "Chicken Teriyaki Bowl", "liked": 1, "timestamp": datetime.now().isoformat(), "date": str(date.today())},
        {"user_id": "e2e_user", "dish_id": "l2", "dish_name": "Mediterranean Salad", "liked": 1, "timestamp": datetime.now().isoformat(), "date": str(date.today())},
        {"user_id": "e2e_user", "dish_id": "l3", "dish_name": "Tomato Basil Soup", "liked": 1, "timestamp": datetime.now().isoformat(), "date": str(date.today())},
        {"user_id": "e2e_user", "dish_id": "l4", "dish_name": "BBQ Pulled Pork Sandwich", "liked": 0, "timestamp": datetime.now().isoformat(), "date": str(date.today())},
    ])


class TestEndToEnd:
    """End-to-end tests for the complete recommendation flow."""

    def test_prompt_contains_all_context(self, full_menu_df, user_feedback_df):
        """Test that the recommendation prompt includes all agent contexts."""
        profile = {"is_vegetarian": False, "is_vegan": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        context = gather_agent_context(meal="Lunch")
        prompt = build_recommendation_prompt(context, meal="Lunch")

        # Check all sections are present
        assert "User's Dietary Profile" in prompt
        assert "User's Current Mood" in prompt
        assert "User's Taste Preferences" in prompt
        assert "Available Dishes" in prompt

        # Check context content is included
        assert "HAPPY" in prompt
        assert "Lunch" in prompt

    def test_prompt_reflects_mood_changes(self, full_menu_df, user_feedback_df):
        """Test that different moods produce different prompts."""
        profile = {"is_vegetarian": False}

        # Test with stressed mood
        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="stressed"
        )
        context_stressed = gather_agent_context()
        prompt_stressed = build_recommendation_prompt(context_stressed)

        # Test with adventurous mood
        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="adventurous"
        )
        context_adventurous = gather_agent_context()
        prompt_adventurous = build_recommendation_prompt(context_adventurous)

        # Prompts should differ in mood section
        assert "STRESSED" in prompt_stressed
        assert "ADVENTUROUS" in prompt_adventurous
        assert prompt_stressed != prompt_adventurous

    def test_dietary_restrictions_in_prompt(self, full_menu_df, user_feedback_df):
        """Test that dietary restrictions appear in the prompt."""
        vegan_profile = {
            "is_vegan": True,
            "avoid_gluten": True,
            "avoid_nuts": True,
        }

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=vegan_profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        context = gather_agent_context()
        prompt = build_recommendation_prompt(context)

        assert "VEGAN" in prompt
        assert "gluten" in prompt
        assert "nuts" in prompt

    @patch('agents.orchestrator.get_llm')
    def test_get_recommendation_calls_llm(self, mock_get_llm, full_menu_df, user_feedback_df):
        """Test that get_recommendation properly calls the LLM."""
        # Setup mock
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Based on your preferences, I recommend:\n1. Mediterranean Salad - great for your happy mood!\n2. Chicken Teriyaki Bowl - you've enjoyed this before!"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        # Clear any previous history
        clear_orchestrator_history("e2e_user")

        result = get_recommendation(
            query="/recommend lunch",
            meal="Lunch",
            session_id="e2e_user"
        )

        # Verify LLM was called
        assert mock_llm.invoke.called

        # Verify response contains our mock content
        assert "Mediterranean Salad" in result
        assert "Chicken Teriyaki Bowl" in result

    @patch('agents.orchestrator.get_llm')
    def test_recommendation_with_different_meals(self, mock_get_llm, full_menu_df, user_feedback_df):
        """Test recommendations for different meal periods."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Here are my breakfast recommendations!"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="tired"
        )

        clear_orchestrator_history("e2e_user")

        result = get_recommendation(
            query="/recommend breakfast",
            meal="Breakfast",
            session_id="e2e_user"
        )

        # Check the prompt that was passed to the LLM
        call_args = mock_llm.invoke.call_args
        messages = call_args[0][0]
        system_message = messages[0].content

        # Should include breakfast-specific context
        assert "Breakfast" in system_message

    @patch('agents.orchestrator.get_llm')
    def test_error_handling(self, mock_get_llm, full_menu_df, user_feedback_df):
        """Test that errors are handled gracefully."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_get_llm.return_value = mock_llm

        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        clear_orchestrator_history("e2e_user")

        result = get_recommendation(
            query="/recommend lunch",
            meal="Lunch",
            session_id="e2e_user"
        )

        # Should return error message, not crash
        assert "Error" in result or "error" in result

    @patch('agents.orchestrator.get_llm')
    def test_rate_limit_handling(self, mock_get_llm, full_menu_df, user_feedback_df):
        """Test that rate limit errors are handled specially."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("Rate limit exceeded")
        mock_get_llm.return_value = mock_llm

        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        clear_orchestrator_history("e2e_user")

        result = get_recommendation(
            query="/recommend lunch",
            meal="Lunch",
            session_id="e2e_user"
        )

        # Should return friendly rate limit message
        assert "busy" in result.lower() or "try again" in result.lower()


class TestContextGathering:
    """Test the context gathering from all agents."""

    def test_all_agents_called(self, full_menu_df, user_feedback_df):
        """Test that all four agents contribute to the context."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="grumpy"
        )

        context = gather_agent_context(meal="Dinner")

        # All three agents should have contributed
        assert "mood" in context
        assert "preferences" in context
        assert "dishes" in context

        # Each should have meaningful content
        assert len(context["mood"]) > 50
        assert len(context["dishes"]) > 50

    def test_context_respects_meal_filter(self, full_menu_df, user_feedback_df):
        """Test that meal filter affects available dishes."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            menu_df=full_menu_df,
            feedback_df=user_feedback_df,
            user_profile=profile,
            user_id="e2e_user",
            user_mood="happy"
        )

        # Get lunch context
        lunch_context = gather_agent_context(meal="Lunch")

        # Get dinner context
        dinner_context = gather_agent_context(meal="Dinner")

        # Dish lists should differ
        assert "Chicken Teriyaki Bowl" in lunch_context["dishes"]
        assert "Grilled Salmon" in dinner_context["dishes"]
        assert "Grilled Salmon" not in lunch_context["dishes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
