"""
BerkeleyBites Embedding Service

Generates rich embeddings for dishes using sentence-transformers.
Handles sparse dish data by creating synthetic descriptive text.

Uses all-MiniLM-L6-v2 (384 dims) - fast, free, runs locally.
"""

import os
from typing import Optional
import numpy as np

# Lazy load sentence_transformers to avoid startup delay
_model = None
_model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast inference


def get_embedding_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_model_name)
    return _model


# ===========================================
# Category Expansions
# Maps terse category names to descriptive text
# ===========================================

CATEGORY_EXPANSIONS = {
    # Main dishes
    "entree": "main dish, entree, protein, hearty meal",
    "entrees": "main dish, entree, protein, hearty meal",
    "grill": "grilled food, barbecue, charred, smoky",
    "pizza": "pizza, Italian, cheesy, baked",
    "pasta": "pasta, Italian, noodles, sauce",
    "soup": "soup, broth, warm, comforting, liquid",
    "soups": "soup, broth, warm, comforting, liquid",
    "stir fry": "stir fry, Asian, wok, vegetables",
    "asian": "Asian cuisine, oriental, stir fry",

    # Breakfast
    "breakfast": "breakfast, morning, eggs, toast",
    "bakery": "bakery, bread, pastry, baked goods",
    "cereal": "cereal, breakfast, grains, milk",

    # Sides & vegetables
    "sides": "side dish, accompaniment, vegetable",
    "vegetables": "vegetables, healthy, greens, plant-based",
    "salad": "salad, fresh, greens, healthy, light",
    "salads": "salad, fresh, greens, healthy, light",
    "deli": "deli, sandwich, cold cuts, fresh",

    # Comfort & casual
    "comfort": "comfort food, hearty, warm, satisfying",
    "bowl": "bowl, grain bowl, one-dish meal",
    "bowls": "bowl, grain bowl, one-dish meal",

    # Beverages & desserts
    "beverages": "drinks, beverages, refreshing",
    "desserts": "dessert, sweet, treat, after meal",
    "dessert": "dessert, sweet, treat, after meal",

    # Ethnic cuisines
    "mexican": "Mexican, Latin, spicy, beans, tortilla",
    "indian": "Indian, curry, spiced, aromatic",
    "mediterranean": "Mediterranean, healthy, olive oil, fresh",
    "thai": "Thai, spicy, coconut, noodles",
    "chinese": "Chinese, Asian, stir fry, soy sauce",
    "japanese": "Japanese, sushi, umami, clean flavors",
    "korean": "Korean, fermented, spicy, sesame",
}

# ===========================================
# Cuisine Inference
# Infers cuisine type from dish name keywords
# ===========================================

CUISINE_KEYWORDS = {
    "asian": ["teriyaki", "stir fry", "fried rice", "noodle", "tofu", "sesame", "soy"],
    "mexican": ["taco", "burrito", "quesadilla", "enchilada", "salsa", "guacamole", "tortilla"],
    "italian": ["pasta", "pizza", "marinara", "alfredo", "parmesan", "lasagna", "pesto"],
    "indian": ["curry", "tikka", "masala", "naan", "paneer", "dal", "biryani"],
    "mediterranean": ["hummus", "falafel", "pita", "tzatziki", "olive", "feta"],
    "american": ["burger", "hot dog", "bbq", "mac and cheese", "fried chicken"],
    "breakfast": ["egg", "pancake", "waffle", "french toast", "oatmeal", "bacon", "sausage"],
    "comfort": ["soup", "stew", "casserole", "pot pie", "meatloaf", "grilled cheese"],
    "healthy": ["salad", "grilled", "steamed", "fresh", "light", "lean"],
}


def infer_cuisine(dish_name: str, category: str) -> str:
    """Infer cuisine type from dish name and category."""
    name_lower = dish_name.lower()
    category_lower = category.lower()

    for cuisine, keywords in CUISINE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower or keyword in category_lower:
                return cuisine

    return "general"


# ===========================================
# Meal Occasion Mapping
# Maps meal periods to descriptive occasions
# ===========================================

MEAL_OCCASIONS = {
    "breakfast": "breakfast, morning meal, start the day, early energy",
    "brunch": "brunch, late morning, weekend meal, relaxed",
    "lunch": "lunch, midday meal, afternoon refuel, quick bite",
    "dinner": "dinner, evening meal, end of day, substantial",
    "late night": "late night, after hours, midnight snack, late meal",
}


def get_meal_occasion(meal_period: str) -> str:
    """Get descriptive meal occasion text."""
    period_lower = meal_period.lower()
    for key, value in MEAL_OCCASIONS.items():
        if key in period_lower:
            return value
    return "meal, dining, food"


# ===========================================
# Embedding Text Generation
# ===========================================

def generate_dish_embedding_text(dish: dict) -> str:
    """
    Generate rich descriptive text for a dish embedding.

    Combines: dish name + category expansion + dietary descriptors
              + inferred cuisine + meal occasion

    Example output:
    "Dish: Teriyaki Chicken Bowl | Category: bowl, grain bowl, one-dish meal |
     Dietary: halal | Cuisine: asian | Occasion: lunch, midday refuel"

    Args:
        dish: Dictionary with dish_name, category, meal_period, and dietary flags

    Returns:
        Synthetic text suitable for embedding generation
    """
    dish_name = dish.get("dish_name", "")
    category = dish.get("category", "")
    meal_period = dish.get("meal_period", "")

    # Start with dish name (most important)
    parts = [f"Dish: {dish_name}"]

    # Add category expansion
    category_lower = category.lower()
    category_text = CATEGORY_EXPANSIONS.get(category_lower, category)
    parts.append(f"Category: {category_text}")

    # Add dietary descriptors
    dietary = []
    if dish.get("is_vegan"):
        dietary.append("vegan")
    if dish.get("is_vegetarian"):
        dietary.append("vegetarian")
    if dish.get("is_halal"):
        dietary.append("halal")
    if dish.get("is_kosher"):
        dietary.append("kosher")
    if dietary:
        parts.append(f"Dietary: {', '.join(dietary)}")

    # Add inferred cuisine
    cuisine = infer_cuisine(dish_name, category)
    parts.append(f"Cuisine: {cuisine}")

    # Add meal occasion
    occasion = get_meal_occasion(meal_period)
    parts.append(f"Occasion: {occasion}")

    return " | ".join(parts)


def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding vector for text.

    Args:
        text: Input text to embed

    Returns:
        384-dimensional embedding vector as list of floats
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_dish_embedding(dish: dict) -> tuple[str, list[float]]:
    """
    Generate embedding for a dish.

    Args:
        dish: Dish dictionary

    Returns:
        Tuple of (embedding_text, embedding_vector)
    """
    text = generate_dish_embedding_text(dish)
    embedding = generate_embedding(text)
    return text, embedding


def generate_batch_embeddings(dishes: list[dict]) -> list[tuple[int, str, list[float]]]:
    """
    Generate embeddings for multiple dishes efficiently.

    Uses batch encoding for better performance.

    Args:
        dishes: List of dish dictionaries (must have dish_id)

    Returns:
        List of (dish_id, embedding_text, embedding_vector) tuples
    """
    if not dishes:
        return []

    model = get_embedding_model()

    # Generate embedding texts
    texts = [generate_dish_embedding_text(dish) for dish in dishes]

    # Batch encode for efficiency
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=len(dishes) > 50)

    # Combine results
    results = []
    for dish, text, embedding in zip(dishes, texts, embeddings):
        dish_id = dish.get("dish_id") or dish.get("id")
        results.append((dish_id, text, embedding.tolist()))

    return results


# ===========================================
# Query Embedding Generation
# ===========================================

def generate_query_embedding(
    mood: Optional[str] = None,
    craving: Optional[str] = None,
    meal_period: Optional[str] = None
) -> list[float]:
    """
    Generate an embedding for a user query context.

    Combines mood, craving, and meal period into a searchable embedding.

    Args:
        mood: User's current mood (happy, stressed, tired, etc.)
        craving: Type of food craving (comfort, healthy, quick, filling)
        meal_period: Current meal period

    Returns:
        384-dimensional embedding vector
    """
    parts = []

    # Mood mapping
    mood_descriptions = {
        "happy": "celebratory food, adventurous eating, trying new things",
        "grumpy": "comfort food, warm soothing meals, familiar favorites",
        "stressed": "light nutritious food, easy to eat, calming meals",
        "tired": "energy-boosting food, protein-rich, revitalizing meals",
        "adventurous": "unique cuisine, exotic flavors, new experiences",
    }
    if mood and mood.lower() in mood_descriptions:
        parts.append(mood_descriptions[mood.lower()])

    # Craving mapping
    craving_descriptions = {
        "comfort": "comfort food, warm, hearty, satisfying, cozy",
        "healthy": "healthy food, fresh, nutritious, light, clean eating",
        "quick": "quick food, fast, convenient, grab and go",
        "filling": "filling food, substantial, big portions, hearty meal",
    }
    if craving and craving.lower() in craving_descriptions:
        parts.append(craving_descriptions[craving.lower()])

    # Meal period
    if meal_period:
        occasion = get_meal_occasion(meal_period)
        parts.append(occasion)

    # Default if no context provided
    if not parts:
        parts.append("good food, tasty meal, satisfying dish")

    query_text = " | ".join(parts)
    return generate_embedding(query_text)


# ===========================================
# Similarity Computation (Local Fallback)
# ===========================================

def compute_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Used as fallback when pgvector is unavailable.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score between 0 and 1
    """
    a = np.array(vec1)
    b = np.array(vec2)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def rank_dishes_by_similarity(
    dishes: list[dict],
    query_embedding: list[float],
    top_k: int = 30
) -> list[tuple[dict, float]]:
    """
    Rank dishes by similarity to query embedding (local computation).

    Used as fallback when pgvector is unavailable.

    Args:
        dishes: List of dish dicts with 'embedding' field
        query_embedding: Query embedding vector
        top_k: Number of top results to return

    Returns:
        List of (dish, similarity_score) tuples, sorted by similarity
    """
    scored = []
    for dish in dishes:
        embedding = dish.get("embedding")
        if embedding:
            similarity = compute_cosine_similarity(embedding, query_embedding)
            scored.append((dish, similarity))

    # Sort by similarity descending
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]
