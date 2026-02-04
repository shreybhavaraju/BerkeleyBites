"""
Unit tests for BerkeleyBites Recommendation System

Tests the core components:
- Orchestrator: set_orchestrator_context, get_recommendation
- Scoring: compute_dish_score, UserContext
- UI Summaries: _build_summaries
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.orchestrator import (
    set_orchestrator_context,
    _build_summaries,
)
from backend.agents.scoring import (
    UserContext,
    FeedbackSummary,
    compute_dish_score,
)


# ============================================
# TEST FIXTURES
# ============================================

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


@pytest.fixture
def sample_dish():
    """Create a sample dish for testing (dish_id=1 matches liked_dish_ids in sample_feedback_summary)."""
    return {
        "dish_id": 1,
        "dish_name": "Vegan Buddha Bowl",
        "dining_hall": "Crossroads",
        "meal_period": "Lunch",
        "category": "Entrees",
        "is_vegan": True,
        "is_vegetarian": True,
    }


@pytest.fixture
def sample_user_context():
    """Create a sample user context for testing."""
    return UserContext(
        user_id="test_user",
        mood="happy",
        craving="healthy",
        spice_level="mild",
        time_constraint="normal",
        meal_period="Lunch"
    )


@pytest.fixture
def sample_feedback_summary():
    """Create a sample feedback summary for testing."""
    return FeedbackSummary(
        liked_dish_ids={1, 3},  # dish_ids for Vegan Buddha Bowl, Tomato Soup
        disliked_dish_ids={4},  # dish_id for Pepperoni Pizza
        liked_categories={"Entrees": 2, "Soups": 1},
        disliked_categories={"Pizza": 1},
        total_ratings=4
    )


# ============================================
# ORCHESTRATOR TESTS
# ============================================

class TestOrchestrator:
    """Tests for the Orchestrator."""

    def test_set_orchestrator_context(self, sample_user_profile):
        """Test setting orchestrator context."""
        # Should not raise any exceptions
        set_orchestrator_context(
            user_profile=sample_user_profile,
            user_id="test_user_123"
        )

    def test_set_orchestrator_context_with_legacy_params(self, sample_user_profile):
        """Test that legacy parameters are accepted but ignored."""
        # Should not raise - **kwargs handles extra params
        set_orchestrator_context(
            user_profile=sample_user_profile,
            user_id="test_user",
            menu_df="ignored",
            feedback_df="ignored",
            user_mood="ignored"
        )


# ============================================
# UI SUMMARIES TESTS
# ============================================

class TestBuildSummaries:
    """Tests for the _build_summaries function."""

    def test_build_summaries_happy_mood(self):
        """Test summaries for happy mood."""
        question_context = {"mood": "happy"}
        summaries = _build_summaries(question_context, "Lunch")

        assert "mood" in summaries
        assert summaries["mood"]["title"] == "Mood Analysis"
        assert "happy" in summaries["mood"]["points"][0].lower()

    def test_build_summaries_stressed_mood(self):
        """Test summaries for stressed mood."""
        question_context = {"mood": "stressed"}
        summaries = _build_summaries(question_context, "Dinner")

        assert "stressed" in summaries["mood"]["points"][0].lower()

    def test_build_summaries_with_craving(self):
        """Test summaries include craving info."""
        question_context = {"mood": "happy", "craving": "comfort"}
        summaries = _build_summaries(question_context, "Lunch")

        assert "craving" in summaries
        assert "comfort" in summaries["craving"]["points"][0].lower()

    def test_build_summaries_with_spice(self):
        """Test summaries include spice preference."""
        question_context = {"mood": "happy", "spice_level": "spicy"}
        summaries = _build_summaries(question_context, "Lunch")

        assert "spice" in summaries
        assert "heat" in summaries["spice"]["points"][0].lower()

    def test_build_summaries_with_time(self):
        """Test summaries include time constraint."""
        question_context = {"mood": "happy", "time_constraint": "rush"}
        summaries = _build_summaries(question_context, "Lunch")

        assert "time" in summaries
        assert "hurry" in summaries["time"]["points"][0].lower()

    def test_build_summaries_empty_context(self):
        """Test summaries with empty context."""
        summaries = _build_summaries({}, "Lunch")

        assert "mood" in summaries
        assert summaries["mood"]["points"][0] == "Ready for a great meal"


# ============================================
# SCORING TESTS
# ============================================

class TestScoring:
    """Tests for the scoring module."""

    def test_compute_dish_score_basic(self, sample_dish, sample_user_context, sample_feedback_summary):
        """Test basic dish scoring."""
        score = compute_dish_score(
            dish=sample_dish,
            context=sample_user_context,
            feedback=sample_feedback_summary,
            embedding_similarity=0.8
        )

        assert score.dish_name == "Vegan Buddha Bowl"
        assert score.total_score > 0
        assert score.total_score <= 1.0

    def test_compute_dish_score_liked_dish(self, sample_dish, sample_user_context, sample_feedback_summary):
        """Test scoring for a previously liked dish."""
        score = compute_dish_score(
            dish=sample_dish,
            context=sample_user_context,
            feedback=sample_feedback_summary,
            embedding_similarity=0.8
        )

        # Liked dish should have positive taste score
        assert score.taste_score > 0
        assert score.is_liked == True

    def test_compute_dish_score_new_dish(self, sample_user_context, sample_feedback_summary):
        """Test scoring for a new dish."""
        new_dish = {
            "dish_id": 999,
            "dish_name": "New Mystery Dish",
            "dining_hall": "Cafe 3",
            "meal_period": "Lunch",
            "category": "Specials",
        }

        score = compute_dish_score(
            dish=new_dish,
            context=sample_user_context,
            feedback=sample_feedback_summary,
            embedding_similarity=0.5
        )

        assert score.is_new == True
        assert score.is_liked == False

    def test_user_context_creation(self):
        """Test UserContext dataclass creation."""
        context = UserContext(
            user_id="user123",
            mood="tired",
            craving="filling",
            spice_level="medium",
            time_constraint="leisurely",
            meal_period="Dinner"
        )

        assert context.user_id == "user123"
        assert context.mood == "tired"
        assert context.craving == "filling"

    def test_feedback_summary_creation(self):
        """Test FeedbackSummary dataclass creation."""
        summary = FeedbackSummary(
            liked_dish_ids={1, 2},
            disliked_dish_ids={3},
            liked_categories={"Entrees": 2},
            disliked_categories={"Grill": 1},
            total_ratings=3
        )

        assert len(summary.liked_dish_ids) == 2
        assert summary.total_ratings == 3


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests for the recommendation system."""

    def test_full_scoring_flow(self, sample_user_profile):
        """Test the full scoring flow."""
        # Set up context
        set_orchestrator_context(
            user_profile=sample_user_profile,
            user_id="test_user"
        )

        # Create user context
        user_context = UserContext(
            user_id="test_user",
            mood="happy",
            craving="healthy",
            spice_level="mild",
            time_constraint="normal",
            meal_period="Lunch"
        )

        # Create feedback summary
        feedback = FeedbackSummary(
            liked_dish_ids=set(),
            disliked_dish_ids=set(),
            liked_categories={},
            disliked_categories={},
            total_ratings=0
        )

        # Score a dish
        dish = {
            "dish_id": 1,
            "dish_name": "Test Dish",
            "dining_hall": "Crossroads",
            "meal_period": "Lunch",
            "category": "Entrees",
        }

        score = compute_dish_score(
            dish=dish,
            context=user_context,
            feedback=feedback,
            embedding_similarity=0.7
        )

        assert score.dish_name == "Test Dish"
        assert 0 <= score.total_score <= 1

    def test_summaries_match_context(self):
        """Test that summaries correctly reflect question context."""
        question_context = {
            "mood": "adventurous",
            "craving": "healthy",
            "spice_level": "spicy",
            "time_constraint": "leisurely"
        }

        summaries = _build_summaries(question_context, "Dinner")

        # All context items should be represented
        assert "mood" in summaries
        assert "craving" in summaries
        assert "spice" in summaries
        assert "time" in summaries

        # Values should match
        assert "adventurous" in summaries["mood"]["points"][0].lower()
        assert "healthy" in summaries["craving"]["points"][0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
