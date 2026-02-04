"""
BerkeleyBites Hybrid Retriever

4-stage retrieval pipeline combining:
1. SQL hard filters (~5ms) - dietary compliance, allergens, meal period
2. Vector similarity (~15ms) - semantic search using pgvector
3. Multi-factor scoring (~10ms) - personalization-weighted scoring
4. LLM final selection (~500ms) - diversity and explanation generation

Target: <100ms retrieval + ~500ms LLM = <600ms total
"""

import os
import logging
from datetime import date
from typing import Optional
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .scoring import (
    DishScore, UserContext, FeedbackSummary,
    compute_dish_score, build_feedback_summary
)
from .embedding_service import generate_query_embedding, compute_cosine_similarity
from .cache import (
    get_cached_dishes, set_cached_dishes,
    get_cached_feedback, set_cached_feedback,
    get_cached_dish_embeddings,
    get_cached_query_embedding, set_cached_query_embedding,
    compute_context_hash
)

logger = logging.getLogger(__name__)

# ===========================================
# Configuration
# ===========================================

@dataclass
class RetrieverConfig:
    """Hybrid retriever configuration."""
    # Stage 2: Vector search
    vector_candidates: int = 30  # Number of dishes from vector search

    # Stage 3: Scoring
    top_k_for_llm: int = 8  # Number of top-scored dishes for LLM

    # Stage 4: LLM
    final_selection: int = 4  # Target number of recommendations
    use_llm: bool = True  # Enable/disable LLM for testing

    # Performance
    use_cache: bool = True


# ===========================================
# Hybrid Retriever
# ===========================================

class HybridRetriever:
    """
    Hybrid RAG retriever combining vector search with multi-factor scoring.

    Usage:
        retriever = HybridRetriever(db_client)
        recommendations = await retriever.retrieve_recommendations(
            user_id="user123",
            user_context=UserContext(mood="happy", craving="comfort"),
            meal_period="lunch"
        )
    """

    def __init__(self, db_client=None, config: Optional[RetrieverConfig] = None):
        """
        Initialize retriever.

        Args:
            db_client: Supabase client (optional, will use singleton if not provided)
            config: Retriever configuration
        """
        self._db_client = db_client
        self.config = config or RetrieverConfig()
        self._llm = None

    def _get_db(self):
        """Get database client (lazy loaded)."""
        if self._db_client is None:
            from backend.database import get_client
            self._db_client = get_client()
        return self._db_client

    def _get_llm(self):
        """Get LLM instance (lazy loaded)."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="sonar",
                temperature=0.7,
                api_key=os.getenv("PERPLEXITY_API_KEY"),
                base_url="https://api.perplexity.ai",
            )
        return self._llm

    # ===========================================
    # Stage 1: SQL Hard Filters
    # ===========================================

    def _filter_by_dietary(
        self,
        dishes: list[dict],
        user_profile: Optional[dict]
    ) -> list[dict]:
        """
        Apply dietary restriction filters.

        Args:
            dishes: List of dish dicts
            user_profile: User's dietary profile

        Returns:
            Filtered list of dishes
        """
        if not user_profile:
            return dishes

        filtered = dishes

        # Dietary preferences (strict filters)
        if user_profile.get("is_vegan"):
            filtered = [d for d in filtered if d.get("is_vegan")]
        elif user_profile.get("is_vegetarian"):
            filtered = [d for d in filtered if d.get("is_vegetarian")]
        elif user_profile.get("is_pescatarian"):
            filtered = [d for d in filtered
                       if d.get("is_vegetarian") or d.get("has_fish")]

        if user_profile.get("is_halal"):
            filtered = [d for d in filtered if d.get("is_halal")]

        if user_profile.get("is_kosher"):
            filtered = [d for d in filtered if d.get("is_kosher")]

        # Allergen exclusions
        if user_profile.get("avoid_milk"):
            filtered = [d for d in filtered if not d.get("has_milk")]

        if user_profile.get("avoid_eggs"):
            filtered = [d for d in filtered if not d.get("has_egg")]

        if user_profile.get("avoid_gluten"):
            filtered = [d for d in filtered if not d.get("has_gluten")]

        if user_profile.get("avoid_nuts"):
            filtered = [d for d in filtered
                       if not d.get("has_tree_nuts") and not d.get("has_peanuts")]

        if user_profile.get("avoid_soy"):
            filtered = [d for d in filtered if not d.get("has_soybeans")]

        return filtered

    def _filter_by_meal_period(
        self,
        dishes: list[dict],
        meal_period: Optional[str]
    ) -> list[dict]:
        """Filter dishes by meal period."""
        if not meal_period:
            return dishes

        meal_lower = meal_period.lower()
        return [d for d in dishes
                if meal_lower in d.get("meal_period", "").lower()]

    def stage1_sql_filters(
        self,
        scrape_date: str,
        user_profile: Optional[dict] = None,
        meal_period: Optional[str] = None
    ) -> list[dict]:
        """
        Stage 1: Apply SQL-equivalent hard filters.

        Args:
            scrape_date: Date to query
            user_profile: User's dietary profile
            meal_period: Meal period filter

        Returns:
            List of candidate dishes
        """
        # Try cache first
        if self.config.use_cache:
            cached = get_cached_dishes(scrape_date, meal_period)
            if cached:
                return self._filter_by_dietary(cached, user_profile)

        # Load from database
        from backend.database import get_dishes
        dishes = get_dishes(meal_period=meal_period, scrape_date=scrape_date)

        # Cache the results
        if self.config.use_cache and dishes:
            set_cached_dishes(dishes, scrape_date, meal_period)

        # Apply dietary filters
        return self._filter_by_dietary(dishes, user_profile)

    # ===========================================
    # Stage 2: Vector Similarity
    # ===========================================

    def stage2_vector_search(
        self,
        candidates: list[dict],
        context: UserContext
    ) -> list[tuple[dict, float]]:
        """
        Stage 2: Compute vector similarity for candidates.

        Args:
            candidates: List of candidate dishes
            context: User context for query embedding

        Returns:
            List of (dish, similarity_score) tuples
        """
        if not candidates:
            return []

        # Generate or get cached query embedding
        context_hash = compute_context_hash(
            mood=context.mood,
            craving=context.craving,
            meal_period=context.meal_period
        )

        query_embedding = None
        if self.config.use_cache:
            query_embedding = get_cached_query_embedding(context_hash)

        if query_embedding is None:
            query_embedding = generate_query_embedding(
                mood=context.mood,
                craving=context.craving,
                meal_period=context.meal_period
            )
            if self.config.use_cache:
                set_cached_query_embedding(context_hash, query_embedding)

        # Try pgvector search first
        dish_ids = [d.get("dish_id") or d.get("id") for d in candidates]
        similarities = self._pgvector_search(dish_ids, query_embedding)

        if similarities:
            # Map similarities back to dishes
            sim_map = {s["dish_id"]: s["similarity"] for s in similarities}
            results = []
            for dish in candidates:
                dish_id = dish.get("dish_id") or dish.get("id")
                sim = sim_map.get(dish_id, 0.5)  # Default similarity
                results.append((dish, sim))
            return results

        # Fallback: local similarity computation
        return self._local_vector_search(candidates, query_embedding)

    def _pgvector_search(
        self,
        dish_ids: list[int],
        query_embedding: list[float]
    ) -> list[dict]:
        """
        Search using pgvector (database-side).

        Returns:
            List of {"dish_id": int, "similarity": float}
        """
        try:
            client = self._get_db()
            # Call the search function
            result = client.rpc(
                "search_dishes_by_embedding",
                {
                    "query_embedding": query_embedding,
                    "dish_ids": dish_ids,
                    "match_count": self.config.vector_candidates
                }
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"pgvector search failed, using local fallback: {e}")
            return []

    def _local_vector_search(
        self,
        candidates: list[dict],
        query_embedding: list[float]
    ) -> list[tuple[dict, float]]:
        """
        Fallback: compute similarity locally.

        Args:
            candidates: List of dishes with optional embeddings
            query_embedding: Query embedding vector

        Returns:
            List of (dish, similarity) tuples
        """
        # Try to get cached embeddings
        today = str(date.today())
        cached_embeddings = get_cached_dish_embeddings(today)

        results = []
        for dish in candidates:
            dish_id = dish.get("dish_id") or dish.get("id")

            # Check for embedding in dish or cache
            embedding = dish.get("embedding")
            if not embedding and cached_embeddings:
                embedding = cached_embeddings.get(dish_id)

            if embedding:
                sim = compute_cosine_similarity(query_embedding, embedding)
            else:
                sim = 0.5  # Neutral if no embedding

            results.append((dish, sim))

        return results

    # ===========================================
    # Stage 3: Multi-Factor Scoring
    # ===========================================

    def stage3_scoring(
        self,
        dishes_with_similarity: list[tuple[dict, float]],
        context: UserContext,
        feedback: FeedbackSummary
    ) -> list[DishScore]:
        """
        Stage 3: Apply multi-factor scoring.

        Args:
            dishes_with_similarity: List of (dish, similarity) from stage 2
            context: User context
            feedback: User's feedback summary

        Returns:
            List of DishScore objects, sorted by total_score descending
        """
        scores = []
        for dish, similarity in dishes_with_similarity:
            score = compute_dish_score(
                dish=dish,
                context=context,
                feedback=feedback,
                embedding_similarity=similarity
            )
            scores.append(score)

        # Sort by total score descending
        scores.sort(key=lambda s: s.total_score, reverse=True)

        return scores

    # ===========================================
    # Stage 4: LLM Final Selection
    # ===========================================

    def stage4_llm_selection(
        self,
        top_scores: list[DishScore],
        context: UserContext
    ) -> list[dict]:
        """
        Stage 4: Use LLM for final selection and explanations.

        Args:
            top_scores: Top K scored dishes
            context: User context

        Returns:
            List of recommendation dicts with explanations
        """
        if not self.config.use_llm:
            # Return top dishes without LLM explanations
            return [
                {
                    "dish_name": s.dish_name,
                    "dining_hall": s.dining_hall,
                    "meal_period": s.meal_period,
                    "category": s.category,
                    "score": s.total_score,
                    "explanation": f"Score: {s.total_score:.2f}"
                }
                for s in top_scores[:self.config.final_selection]
            ]

        # Build prompt for LLM
        prompt = self._build_llm_prompt(top_scores, context)

        try:
            llm = self._get_llm()
            messages = [
                SystemMessage(content=prompt["system"]),
                HumanMessage(content=prompt["user"])
            ]
            response = llm.invoke(messages)
            return self._parse_llm_response(response.content, top_scores)
        except Exception as e:
            logger.error(f"LLM selection failed: {e}")
            # Fallback to top scored dishes
            return [
                {
                    "dish_name": s.dish_name,
                    "dining_hall": s.dining_hall,
                    "meal_period": s.meal_period,
                    "category": s.category,
                    "score": s.total_score,
                    "explanation": "Highly matched to your preferences"
                }
                for s in top_scores[:self.config.final_selection]
            ]

    def _build_llm_prompt(
        self,
        top_scores: list[DishScore],
        context: UserContext
    ) -> dict:
        """Build prompt for LLM selection."""
        # Format dish options
        dish_list = []
        for i, score in enumerate(top_scores, 1):
            dish_list.append(
                f"{i}. {score.dish_name} ({score.dining_hall}, {score.meal_period})\n"
                f"   Category: {score.category}\n"
                f"   Scores: Taste={score.taste_score:.2f}, Craving={score.craving_score:.2f}, "
                f"Mood={score.mood_score:.2f}\n"
                f"   Total: {score.total_score:.2f}"
            )

        dishes_text = "\n\n".join(dish_list)

        # Build context description
        context_parts = []
        if context.mood:
            context_parts.append(f"Mood: {context.mood}")
        if context.craving:
            context_parts.append(f"Craving: {context.craving}")
        if context.spice_level:
            context_parts.append(f"Spice preference: {context.spice_level}")
        if context.time_constraint:
            context_parts.append(f"Time: {context.time_constraint}")
        context_text = ", ".join(context_parts) if context_parts else "General recommendation"

        system_prompt = """You are a food recommendation assistant for UC Berkeley dining halls.

CRITICAL RULES:
- ONLY select from the pre-scored dishes listed below
- NEVER add dishes that aren't in the provided list
- NEVER search for or include external information
- NEVER include dates, times, or timestamps
- Keep explanations focused on the user's preferences and the dish attributes

Your goals:
1. Ensure diversity (different categories, different dining halls when possible)
2. Write brief, personalized explanations (1-2 sentences each)
3. Consider the user's specific context when writing explanations

Output format - respond with ONLY a JSON array:
[
  {"dish_name": "...", "dining_hall": "...", "explanation": "..."},
  ...
]

Do not include any text before or after the JSON array."""

        user_prompt = f"""User Context: {context_text}

Pre-scored Dishes (ranked by personalization score):

{dishes_text}

Select 3-4 diverse dishes and write personalized explanations."""

        return {"system": system_prompt, "user": user_prompt}

    def _parse_llm_response(
        self,
        response_text: str,
        top_scores: list[DishScore]
    ) -> list[dict]:
        """Parse LLM response into recommendations."""
        import json

        try:
            # Try to parse JSON from response
            # Handle potential markdown code blocks
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            recommendations = json.loads(text)

            # Enrich with score data
            score_map = {s.dish_name: s for s in top_scores}
            enriched = []
            for rec in recommendations:
                dish_name = rec.get("dish_name", "")
                score = score_map.get(dish_name)
                enriched.append({
                    "dish_name": dish_name,
                    "dining_hall": rec.get("dining_hall", score.dining_hall if score else ""),
                    "meal_period": score.meal_period if score else "",
                    "category": score.category if score else "",
                    "score": score.total_score if score else 0,
                    "explanation": rec.get("explanation", "")
                })
            return enriched

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            # Fallback to top scores
            return [
                {
                    "dish_name": s.dish_name,
                    "dining_hall": s.dining_hall,
                    "meal_period": s.meal_period,
                    "category": s.category,
                    "score": s.total_score,
                    "explanation": "Highly matched to your preferences"
                }
                for s in top_scores[:self.config.final_selection]
            ]

    # ===========================================
    # Main Retrieval Method
    # ===========================================

    def retrieve_recommendations(
        self,
        user_id: str,
        user_context: UserContext,
        meal_period: Optional[str] = None,
        user_profile: Optional[dict] = None,
        scrape_date: Optional[str] = None
    ) -> dict:
        """
        Main retrieval pipeline.

        Args:
            user_id: User identifier
            user_context: User context (mood, craving, etc.)
            meal_period: Meal period filter
            user_profile: User's dietary profile
            scrape_date: Date to query (defaults to today)

        Returns:
            Dict with:
                - recommendations: List of final recommendations
                - top_scores: Full scoring breakdown for top dishes
                - stage_stats: Timing and count stats per stage
        """
        import time

        target_date = scrape_date or str(date.today())
        stats = {}

        # Stage 1: SQL Hard Filters
        start = time.time()
        candidates = self.stage1_sql_filters(
            scrape_date=target_date,
            user_profile=user_profile,
            meal_period=meal_period
        )
        stats["stage1_ms"] = (time.time() - start) * 1000
        stats["stage1_count"] = len(candidates)

        if not candidates:
            return {
                "recommendations": [],
                "top_scores": [],
                "stage_stats": stats
            }

        # Stage 2: Vector Search
        start = time.time()
        dishes_with_similarity = self.stage2_vector_search(candidates, user_context)
        stats["stage2_ms"] = (time.time() - start) * 1000

        # Load user feedback for scoring
        feedback_list = self._load_user_feedback(user_id)
        feedback_summary = build_feedback_summary(feedback_list)

        # Stage 3: Multi-Factor Scoring
        start = time.time()
        all_scores = self.stage3_scoring(
            dishes_with_similarity,
            user_context,
            feedback_summary
        )
        stats["stage3_ms"] = (time.time() - start) * 1000
        stats["stage3_count"] = len(all_scores)

        # Get top K for LLM
        top_scores = all_scores[:self.config.top_k_for_llm]

        # Stage 4: LLM Final Selection
        start = time.time()
        recommendations = self.stage4_llm_selection(top_scores, user_context)
        stats["stage4_ms"] = (time.time() - start) * 1000
        stats["final_count"] = len(recommendations)

        # Total time
        stats["total_ms"] = sum(
            stats.get(k, 0) for k in ["stage1_ms", "stage2_ms", "stage3_ms", "stage4_ms"]
        )

        return {
            "recommendations": recommendations,
            "top_scores": top_scores,
            "stage_stats": stats
        }

    def _load_user_feedback(self, user_id: str) -> list[dict]:
        """Load user feedback with caching."""
        if self.config.use_cache:
            cached = get_cached_feedback(user_id)
            if cached is not None:
                return cached

        from backend.database import get_user_feedback
        feedback = get_user_feedback(user_id)

        if self.config.use_cache:
            set_cached_feedback(user_id, feedback)

        return feedback


# ===========================================
# Module-level Instance
# ===========================================

_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """Get or create global retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever
