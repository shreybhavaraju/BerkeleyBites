"""
BerkeleyBites Multi-Agent System

This package provides specialized agents for food recommendation:
- MoodAgent: Reads user mood and provides food guidance
- FoodAvailabilityAgent: Queries menu data
- TastePreferencesAgent: Analyzes user feedback history
- Orchestrator: Coordinates all agents for recommendations

RAG System Components:
- EmbeddingService: Generates dish embeddings using sentence-transformers
- Scoring: Multi-factor scoring for personalized ranking
- HybridRetriever: 4-stage retrieval pipeline (SQL -> Vector -> Score -> LLM)
- Cache: Multi-layer caching for <100ms retrieval
"""

from .mood_agent import get_user_mood
from .food_availability_agent import get_available_dishes, get_menu_summary
from .taste_preferences_agent import get_taste_preferences, get_similar_liked_dishes
from .orchestrator import get_recommendation, set_orchestrator_context

# RAG system exports (lazy loaded to avoid startup delay)
from .scoring import DishScore, UserContext, FeedbackSummary, compute_dish_score
from .hybrid_retriever import HybridRetriever, get_retriever
from .cache import get_cache, warm_cache_sync

__all__ = [
    # Original agents
    "get_user_mood",
    "get_available_dishes",
    "get_menu_summary",
    "get_taste_preferences",
    "get_similar_liked_dishes",
    "get_recommendation",
    "set_orchestrator_context",
    # RAG system
    "DishScore",
    "UserContext",
    "FeedbackSummary",
    "compute_dish_score",
    "HybridRetriever",
    "get_retriever",
    "get_cache",
    "warm_cache_sync",
]
