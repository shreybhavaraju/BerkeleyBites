"""
End-to-end tests for BerkeleyBites Recommendation System

These tests verify the complete recommendation flow.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.orchestrator import (
    set_orchestrator_context,
    get_recommendation,
    _build_summaries,
    clear_orchestrator_history,
)
from backend.agents.scoring import UserContext, FeedbackSummary


class TestEndToEnd:
    """End-to-end tests for the complete recommendation flow."""

    def test_get_recommendation_returns_dict(self):
        """Test that get_recommendation returns proper structure."""
        profile = {"is_vegetarian": False, "is_vegan": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="e2e_user"
        )

        clear_orchestrator_history("e2e_user")

        # Mock the hybrid retriever to avoid database calls
        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_result = {
                "recommendations": [
                    {"dish_name": "Test Dish", "dining_hall": "Crossroads", "explanation": "Great choice!"}
                ],
                "top_scores": [],
                "stage_stats": {"stage1_count": 10, "total_ms": 50}
            }
            mock_retriever.return_value.retrieve_recommendations.return_value = mock_result

            result = get_recommendation(
                query="/recommend lunch",
                meal="Lunch",
                session_id="e2e_user",
                question_context={"mood": "happy", "craving": "healthy"}
            )

            assert "agent_summaries" in result
            assert "recommendation" in result
            assert "Test Dish" in result["recommendation"]

    def test_recommendation_includes_summaries(self):
        """Test that recommendation result includes UI summaries."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="e2e_user"
        )

        clear_orchestrator_history("e2e_user")

        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_result = {
                "recommendations": [
                    {"dish_name": "Salad", "dining_hall": "Cafe 3", "explanation": "Fresh!"}
                ],
                "top_scores": [],
                "stage_stats": {"stage1_count": 5, "total_ms": 30}
            }
            mock_retriever.return_value.retrieve_recommendations.return_value = mock_result

            result = get_recommendation(
                query="/recommend lunch",
                meal="Lunch",
                session_id="e2e_user",
                question_context={
                    "mood": "stressed",
                    "craving": "comfort",
                    "spice_level": "mild",
                    "time_constraint": "rush"
                }
            )

            summaries = result["agent_summaries"]
            assert "mood" in summaries
            assert "craving" in summaries
            assert "spice" in summaries
            assert "time" in summaries

    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="e2e_user"
        )

        clear_orchestrator_history("e2e_user")

        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_retriever.return_value.retrieve_recommendations.side_effect = Exception("API Error")

            result = get_recommendation(
                query="/recommend lunch",
                meal="Lunch",
                session_id="e2e_user"
            )

            # Should return error message, not crash
            assert "Error" in result["recommendation"] or "error" in result["recommendation"].lower()

    def test_rate_limit_handling(self):
        """Test that rate limit errors are handled specially."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="e2e_user"
        )

        clear_orchestrator_history("e2e_user")

        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_retriever.return_value.retrieve_recommendations.side_effect = Exception("Rate limit exceeded")

            result = get_recommendation(
                query="/recommend lunch",
                meal="Lunch",
                session_id="e2e_user"
            )

            # Should return friendly rate limit message
            assert "busy" in result["recommendation"].lower() or "try again" in result["recommendation"].lower()

    def test_no_results_handling(self):
        """Test handling when no recommendations are found."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="e2e_user"
        )

        clear_orchestrator_history("e2e_user")

        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_result = {
                "recommendations": [],
                "top_scores": [],
                "stage_stats": {}
            }
            mock_retriever.return_value.retrieve_recommendations.return_value = mock_result

            result = get_recommendation(
                query="/recommend lunch",
                meal="Lunch",
                session_id="e2e_user"
            )

            # Should return helpful message
            assert "couldn't find" in result["recommendation"].lower() or "no dishes" in result["recommendation"].lower()


class TestSummaries:
    """Test UI summary generation."""

    def test_summaries_reflect_all_context(self):
        """Test that summaries include all question context."""
        question_context = {
            "mood": "adventurous",
            "craving": "healthy",
            "spice_level": "spicy",
            "time_constraint": "leisurely"
        }

        summaries = _build_summaries(question_context, "Dinner")

        assert "mood" in summaries
        assert "craving" in summaries
        assert "spice" in summaries
        assert "time" in summaries

    def test_mood_summaries_vary(self):
        """Test that different moods produce different summaries."""
        happy_summaries = _build_summaries({"mood": "happy"}, "Lunch")
        stressed_summaries = _build_summaries({"mood": "stressed"}, "Lunch")

        assert happy_summaries["mood"]["points"] != stressed_summaries["mood"]["points"]
        assert "happy" in happy_summaries["mood"]["points"][0].lower()
        assert "stressed" in stressed_summaries["mood"]["points"][0].lower()

    def test_craving_summaries(self):
        """Test craving-specific summaries."""
        comfort_summaries = _build_summaries({"mood": "happy", "craving": "comfort"}, "Lunch")
        healthy_summaries = _build_summaries({"mood": "happy", "craving": "healthy"}, "Lunch")

        assert "comfort" in comfort_summaries["craving"]["points"][0].lower()
        assert "healthy" in healthy_summaries["craving"]["points"][0].lower()


class TestQuestionContext:
    """Test that question context flows through properly."""

    def test_context_passed_to_retriever(self):
        """Test that question context is passed to the hybrid retriever."""
        profile = {"is_vegetarian": False}

        set_orchestrator_context(
            user_profile=profile,
            user_id="test_user"
        )

        question_context = {
            "mood": "tired",
            "craving": "filling",
            "spice_level": "medium",
            "time_constraint": "normal"
        }

        with patch('backend.agents.orchestrator.get_retriever') as mock_retriever:
            mock_result = {
                "recommendations": [{"dish_name": "Test", "dining_hall": "X", "explanation": "Y"}],
                "top_scores": [],
                "stage_stats": {}
            }
            mock_retriever.return_value.retrieve_recommendations.return_value = mock_result

            get_recommendation(
                query="/recommend dinner",
                meal="Dinner",
                session_id="test_user",
                question_context=question_context
            )

            # Verify the retriever was called with correct user context
            call_args = mock_retriever.return_value.retrieve_recommendations.call_args
            user_context = call_args.kwargs.get("user_context") or call_args[1].get("user_context")

            assert user_context.mood == "tired"
            assert user_context.craving == "filling"
            assert user_context.spice_level == "medium"
            assert user_context.time_constraint == "normal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
