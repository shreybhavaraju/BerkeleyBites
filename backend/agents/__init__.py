"""
BerkeleyBites Recommendation System

Core Components:
- Orchestrator: Coordinates the recommendation flow
- HybridRetriever: 4-stage retrieval pipeline (SQL → Vector → Score → LLM)
- Scoring: Multi-factor scoring for personalized ranking
- Cache: Multi-layer caching for <100ms retrieval
- EmbeddingService: Generates dish embeddings using sentence-transformers
- QuestionAgent: Collects user preferences (mood, craving, spice, time)
"""

from .orchestrator import get_recommendation, set_orchestrator_context
from .scoring import DishScore, UserContext, FeedbackSummary, compute_dish_score
from .hybrid_retriever import HybridRetriever, get_retriever
from .cache import get_cache, warm_cache_sync

__all__ = [
    # Orchestrator
    "get_recommendation",
    "set_orchestrator_context",
    # Scoring
    "DishScore",
    "UserContext",
    "FeedbackSummary",
    "compute_dish_score",
    # Retriever
    "HybridRetriever",
    "get_retriever",
    # Cache
    "get_cache",
    "warm_cache_sync",
]
