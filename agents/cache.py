"""
BerkeleyBites Caching Layer

Multi-layer caching for sub-100ms retrieval performance.

Cache Layers:
- Layer 1: Dish cache (invalidates at midnight)
- Layer 2: User feedback cache (2-min TTL)
- Layer 3: Embedding cache (preloaded, daily refresh)
"""

import asyncio
from datetime import datetime, date
from typing import Optional, Any
from dataclasses import dataclass, field
import threading

# ===========================================
# Cache Entry
# ===========================================


@dataclass
class CacheEntry:
    """Single cache entry with TTL support."""
    value: Any
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.expires_at


# ===========================================
# Cache Configuration
# ===========================================

@dataclass
class CacheConfig:
    """Cache TTL configuration in seconds."""
    dishes_ttl: int = 86400  # 24 hours (midnight invalidation)
    feedback_ttl: int = 120  # 2 minutes
    embedding_ttl: int = 86400  # 24 hours
    query_embedding_ttl: int = 60  # 1 minute (context changes frequently)


# ===========================================
# Cache Manager
# ===========================================

class CacheManager:
    """
    Thread-safe multi-layer cache manager.

    Provides fast in-memory caching with configurable TTLs.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

        # Track cache date for midnight invalidation
        self._cache_date: Optional[date] = None

    def _check_date_invalidation(self) -> None:
        """Invalidate dish/embedding caches at midnight."""
        today = date.today()
        if self._cache_date and self._cache_date != today:
            # New day - clear dish and embedding caches
            keys_to_clear = [
                k for k in self._cache.keys()
                if k.startswith("dishes:") or k.startswith("embeddings:")
            ]
            for key in keys_to_clear:
                self._cache.pop(key, None)
        self._cache_date = today

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            self._check_date_invalidation()

            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        from datetime import timedelta

        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry existed and was deleted
        """
        with self._lock:
            return self._cache.pop(key, None) is not None

    def clear_prefix(self, prefix: str) -> int:
        """
        Clear all entries with given prefix.

        Args:
            prefix: Key prefix to match

        Returns:
            Number of entries cleared
        """
        with self._lock:
            keys_to_clear = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_clear:
                del self._cache[key]
            return len(keys_to_clear)

    def clear_all(self) -> int:
        """
        Clear entire cache.

        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for e in self._cache.values() if e.is_expired())
            by_prefix = {}
            for key in self._cache.keys():
                prefix = key.split(":")[0]
                by_prefix[prefix] = by_prefix.get(prefix, 0) + 1

            return {
                "total_entries": total,
                "expired_entries": expired,
                "by_category": by_prefix,
                "cache_date": str(self._cache_date) if self._cache_date else None
            }


# ===========================================
# Global Cache Instance
# ===========================================

_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# ===========================================
# Dish Cache Functions
# ===========================================

def get_cached_dishes(scrape_date: str, meal_period: Optional[str] = None) -> Optional[list[dict]]:
    """
    Get dishes from cache.

    Args:
        scrape_date: Date string
        meal_period: Optional meal filter

    Returns:
        List of dishes or None if not cached
    """
    cache = get_cache()
    key = f"dishes:{scrape_date}:{meal_period or 'all'}"
    return cache.get(key)


def set_cached_dishes(
    dishes: list[dict],
    scrape_date: str,
    meal_period: Optional[str] = None
) -> None:
    """
    Cache dishes.

    Args:
        dishes: List of dish dicts
        scrape_date: Date string
        meal_period: Optional meal filter
    """
    cache = get_cache()
    key = f"dishes:{scrape_date}:{meal_period or 'all'}"
    cache.set(key, dishes, cache.config.dishes_ttl)


def invalidate_dishes_cache() -> int:
    """Invalidate all dish caches."""
    return get_cache().clear_prefix("dishes:")


# ===========================================
# Feedback Cache Functions
# ===========================================

def get_cached_feedback(user_id: str) -> Optional[list[dict]]:
    """Get cached user feedback."""
    return get_cache().get(f"feedback:{user_id}")


def set_cached_feedback(user_id: str, feedback: list[dict]) -> None:
    """Cache user feedback."""
    cache = get_cache()
    cache.set(f"feedback:{user_id}", feedback, cache.config.feedback_ttl)


def invalidate_feedback_cache(user_id: str) -> bool:
    """Invalidate specific user's feedback cache."""
    return get_cache().delete(f"feedback:{user_id}")


# ===========================================
# Embedding Cache Functions
# ===========================================

def get_cached_dish_embeddings(scrape_date: str) -> Optional[dict[int, list[float]]]:
    """
    Get cached dish embeddings.

    Args:
        scrape_date: Date string

    Returns:
        Dict mapping dish_id -> embedding vector
    """
    return get_cache().get(f"embeddings:{scrape_date}")


def set_cached_dish_embeddings(
    embeddings: dict[int, list[float]],
    scrape_date: str
) -> None:
    """
    Cache dish embeddings.

    Args:
        embeddings: Dict mapping dish_id -> embedding vector
        scrape_date: Date string
    """
    cache = get_cache()
    cache.set(f"embeddings:{scrape_date}", embeddings, cache.config.embedding_ttl)


def get_cached_query_embedding(context_hash: str) -> Optional[list[float]]:
    """
    Get cached query embedding.

    Args:
        context_hash: Hash of query context

    Returns:
        Embedding vector or None
    """
    return get_cache().get(f"query_embedding:{context_hash}")


def set_cached_query_embedding(context_hash: str, embedding: list[float]) -> None:
    """
    Cache query embedding.

    Args:
        context_hash: Hash of query context
        embedding: Embedding vector
    """
    cache = get_cache()
    cache.set(f"query_embedding:{context_hash}", embedding, cache.config.query_embedding_ttl)


# ===========================================
# Cache Warmup
# ===========================================

async def warm_cache_async(
    load_dishes_fn,
    load_embeddings_fn,
    scrape_date: Optional[str] = None
) -> dict:
    """
    Warm caches on startup (async version).

    Args:
        load_dishes_fn: Async function to load dishes
        load_embeddings_fn: Async function to load embeddings
        scrape_date: Date to load (defaults to today)

    Returns:
        Dict with warmup statistics
    """
    from datetime import date as date_type

    target_date = scrape_date or str(date_type.today())
    stats = {"date": target_date, "dishes": 0, "embeddings": 0}

    try:
        # Load dishes
        dishes = await load_dishes_fn(target_date)
        if dishes:
            set_cached_dishes(dishes, target_date)
            stats["dishes"] = len(dishes)

        # Load embeddings
        embeddings = await load_embeddings_fn(target_date)
        if embeddings:
            set_cached_dish_embeddings(embeddings, target_date)
            stats["embeddings"] = len(embeddings)

    except Exception as e:
        stats["error"] = str(e)

    return stats


def warm_cache_sync(
    load_dishes_fn,
    load_embeddings_fn,
    scrape_date: Optional[str] = None
) -> dict:
    """
    Warm caches on startup (sync version).

    Args:
        load_dishes_fn: Function to load dishes
        load_embeddings_fn: Function to load embeddings
        scrape_date: Date to load (defaults to today)

    Returns:
        Dict with warmup statistics
    """
    from datetime import date as date_type

    target_date = scrape_date or str(date_type.today())
    stats = {"date": target_date, "dishes": 0, "embeddings": 0}

    try:
        # Load dishes
        dishes = load_dishes_fn(target_date)
        if dishes:
            set_cached_dishes(dishes, target_date)
            stats["dishes"] = len(dishes)

        # Load embeddings
        embeddings = load_embeddings_fn(target_date)
        if embeddings:
            set_cached_dish_embeddings(embeddings, target_date)
            stats["embeddings"] = len(embeddings)

    except Exception as e:
        stats["error"] = str(e)

    return stats


# ===========================================
# Context Hash for Query Embedding Cache
# ===========================================

def compute_context_hash(
    mood: Optional[str] = None,
    craving: Optional[str] = None,
    meal_period: Optional[str] = None
) -> str:
    """
    Compute hash for query context (for caching query embeddings).

    Args:
        mood: User mood
        craving: Food craving
        meal_period: Meal period

    Returns:
        Hash string
    """
    parts = [
        f"mood:{mood or 'none'}",
        f"craving:{craving or 'none'}",
        f"meal:{meal_period or 'none'}"
    ]

    return "|".join(parts)
