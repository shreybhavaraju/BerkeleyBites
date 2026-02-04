"""
BerkeleyBites Multi-Factor Scoring System

Deterministic scoring functions for personalized dish ranking.
Combines multiple signals into a weighted composite score.

Score Weights (personalization-heavy):
- taste_preference: 0.35 (from feedback history)
- craving_match: 0.28 (from question answers)
- mood_alignment: 0.17 (mood-to-food mapping)
- category_preference: 0.10 (from feedback patterns)
- embedding_similarity: 0.05 (semantic match)
- novelty_bonus: +0.05 (untried dishes)
- dislike_penalty: -0.30 (disliked dishes)
"""

from typing import Optional
from dataclasses import dataclass, field

# ===========================================
# Data Classes
# ===========================================


@dataclass
class DishScore:
    """Complete scoring breakdown for a dish."""
    dish_id: int
    dish_name: str
    dining_hall: str
    meal_period: str
    category: str

    # Individual scores (0.0 to 1.0)
    taste_score: float = 0.0
    craving_score: float = 0.0
    mood_score: float = 0.0
    category_score: float = 0.0
    embedding_score: float = 0.0
    novelty_bonus: float = 0.0
    dislike_penalty: float = 0.0

    # Final weighted score
    total_score: float = 0.0

    # Extra metadata
    is_liked: bool = False
    is_disliked: bool = False
    is_new: bool = True

    # Raw dish data for LLM context
    dish_data: dict = field(default_factory=dict)

    def compute_total(self) -> float:
        """Compute weighted total score."""
        self.total_score = (
            self.taste_score * 0.35 +
            self.craving_score * 0.28 +
            self.mood_score * 0.17 +
            self.category_score * 0.10 +
            self.embedding_score * 0.05 +
            self.novelty_bonus -
            self.dislike_penalty
        )
        return self.total_score


@dataclass
class UserContext:
    """User context for scoring."""
    user_id: str
    mood: Optional[str] = None
    craving: Optional[str] = None
    spice_level: Optional[str] = None
    time_constraint: Optional[str] = None
    meal_period: Optional[str] = None


@dataclass
class FeedbackSummary:
    """Summarized feedback data for a user."""
    liked_dish_ids: set = field(default_factory=set)
    disliked_dish_ids: set = field(default_factory=set)
    liked_categories: dict = field(default_factory=dict)  # category -> count
    disliked_categories: dict = field(default_factory=dict)  # category -> count
    total_ratings: int = 0


# ===========================================
# Craving Scoring
# ===========================================

# Keywords that match each craving type
CRAVING_KEYWORDS = {
    "comfort": {
        "high": ["soup", "stew", "mac and cheese", "pasta", "casserole", "grilled cheese",
                 "mashed", "pot pie", "gravy", "meatloaf", "comfort"],
        "medium": ["rice", "noodle", "bowl", "warm", "cheese", "creamy", "hearty"],
        "categories": ["soup", "soups", "pasta", "comfort", "entree", "entrees"]
    },
    "healthy": {
        "high": ["salad", "grilled", "steamed", "fresh", "vegetable", "lean", "light"],
        "medium": ["roasted", "baked", "greens", "grain", "quinoa", "tofu"],
        "categories": ["salad", "salads", "vegetables", "greens", "healthy"]
    },
    "quick": {
        "high": ["sandwich", "wrap", "grab", "to go", "quick", "deli", "pre-made"],
        "medium": ["simple", "toast", "bagel", "light", "snack"],
        "categories": ["deli", "bakery", "sandwiches", "grab and go"]
    },
    "filling": {
        "high": ["double", "large", "hearty", "loaded", "xl", "combo", "plate"],
        "medium": ["bowl", "entree", "protein", "rice", "potato", "meat"],
        "categories": ["entree", "entrees", "grill", "bowls", "asian"]
    }
}


def compute_craving_match(dish: dict, craving: Optional[str]) -> float:
    """
    Score how well a dish matches the user's craving.

    Args:
        dish: Dish dictionary
        craving: Craving type (comfort, healthy, quick, filling)

    Returns:
        Score between 0.0 and 1.0
    """
    if not craving or craving.lower() not in CRAVING_KEYWORDS:
        return 0.5  # Neutral

    craving_lower = craving.lower()
    keywords = CRAVING_KEYWORDS[craving_lower]
    dish_name = dish.get("dish_name", "").lower()
    category = dish.get("category", "").lower()

    score = 0.0

    # Check high-match keywords (full points)
    for keyword in keywords["high"]:
        if keyword in dish_name:
            score = max(score, 1.0)
            break

    # Check medium-match keywords (partial points)
    if score < 1.0:
        for keyword in keywords["medium"]:
            if keyword in dish_name:
                score = max(score, 0.7)
                break

    # Check category match
    if score < 1.0 and category in keywords["categories"]:
        score = max(score, 0.8)

    # Default baseline if no matches
    if score == 0.0:
        score = 0.3  # Small baseline for neutral dishes

    return score


# ===========================================
# Mood Scoring
# ===========================================

# Mood to food mappings
MOOD_FOOD_MAPPING = {
    "happy": {
        "high": ["celebration", "special", "favorite", "deluxe", "premium"],
        "medium": ["fresh", "colorful", "variety", "new", "unique"],
        "categories": ["entree", "grill", "pizza", "asian"]
    },
    "grumpy": {
        "high": ["comfort", "warm", "creamy", "cheese", "familiar"],
        "medium": ["soup", "pasta", "potato", "bread", "soft"],
        "categories": ["soup", "soups", "pasta", "comfort", "bakery"]
    },
    "stressed": {
        "high": ["light", "fresh", "simple", "clean", "mild"],
        "medium": ["salad", "vegetable", "healthy", "lean", "green"],
        "categories": ["salad", "salads", "vegetables", "healthy"]
    },
    "tired": {
        "high": ["protein", "energy", "boost", "hearty", "substantial"],
        "medium": ["chicken", "beef", "eggs", "beans", "grain"],
        "categories": ["entree", "entrees", "grill", "breakfast"]
    },
    "adventurous": {
        "high": ["exotic", "spicy", "unique", "fusion", "international"],
        "medium": ["curry", "thai", "indian", "korean", "mexican"],
        "categories": ["asian", "indian", "mexican", "mediterranean"]
    }
}


def compute_mood_alignment(dish: dict, mood: Optional[str]) -> float:
    """
    Score how well a dish aligns with the user's mood.

    Args:
        dish: Dish dictionary
        mood: Current mood (happy, grumpy, stressed, tired, adventurous)

    Returns:
        Score between 0.0 and 1.0
    """
    if not mood or mood.lower() not in MOOD_FOOD_MAPPING:
        return 0.5  # Neutral

    mood_lower = mood.lower()
    mapping = MOOD_FOOD_MAPPING[mood_lower]
    dish_name = dish.get("dish_name", "").lower()
    category = dish.get("category", "").lower()

    score = 0.0

    # Check high-match keywords
    for keyword in mapping["high"]:
        if keyword in dish_name:
            score = max(score, 1.0)
            break

    # Check medium-match keywords
    if score < 1.0:
        for keyword in mapping["medium"]:
            if keyword in dish_name:
                score = max(score, 0.7)
                break

    # Check category match
    if score < 1.0 and category in mapping["categories"]:
        score = max(score, 0.6)

    # Default baseline
    if score == 0.0:
        score = 0.4

    return score


# ===========================================
# Taste Preference Scoring
# ===========================================

def compute_taste_preference(
    dish: dict,
    feedback: FeedbackSummary
) -> tuple[float, bool, bool]:
    """
    Score based on user's feedback history.

    Args:
        dish: Dish dictionary
        feedback: User's feedback summary

    Returns:
        Tuple of (score, is_liked, is_disliked)
    """
    dish_id = dish.get("dish_id") or dish.get("id")

    # Check if explicitly liked/disliked
    if dish_id in feedback.liked_dish_ids:
        return 1.0, True, False
    if dish_id in feedback.disliked_dish_ids:
        return 0.0, False, True

    # New dish - neutral score
    return 0.5, False, False


def compute_category_preference(
    dish: dict,
    feedback: FeedbackSummary
) -> float:
    """
    Score based on user's category preferences.

    Args:
        dish: Dish dictionary
        feedback: User's feedback summary

    Returns:
        Score between 0.0 and 1.0
    """
    category = dish.get("category", "").lower()

    if not feedback.liked_categories and not feedback.disliked_categories:
        return 0.5  # Neutral if no history

    liked_count = feedback.liked_categories.get(category, 0)
    disliked_count = feedback.disliked_categories.get(category, 0)
    total = liked_count + disliked_count

    if total == 0:
        return 0.5  # Neutral for unknown categories

    # Ratio of likes in this category
    like_ratio = liked_count / total
    return like_ratio


# ===========================================
# Novelty Bonus
# ===========================================

def compute_novelty_bonus(
    dish: dict,
    feedback: FeedbackSummary
) -> tuple[float, bool]:
    """
    Give bonus to dishes the user hasn't tried.

    Args:
        dish: Dish dictionary
        feedback: User's feedback summary

    Returns:
        Tuple of (bonus, is_new)
    """
    dish_id = dish.get("dish_id") or dish.get("id")

    # Check if user has rated this dish
    is_new = (
        dish_id not in feedback.liked_dish_ids and
        dish_id not in feedback.disliked_dish_ids
    )

    # Only give novelty bonus if user has some history
    # (encourages exploration after building baseline)
    if is_new and feedback.total_ratings >= 3:
        return 0.05, True

    return 0.0, is_new


# ===========================================
# Dislike Penalty
# ===========================================

def compute_dislike_penalty(
    dish: dict,
    feedback: FeedbackSummary
) -> float:
    """
    Apply penalty for previously disliked dishes.

    Args:
        dish: Dish dictionary
        feedback: User's feedback summary

    Returns:
        Penalty (positive number to subtract)
    """
    dish_id = dish.get("dish_id") or dish.get("id")

    if dish_id in feedback.disliked_dish_ids:
        return 0.30

    return 0.0


# ===========================================
# Composite Scoring
# ===========================================

def compute_dish_score(
    dish: dict,
    context: UserContext,
    feedback: FeedbackSummary,
    embedding_similarity: float = 0.5
) -> DishScore:
    """
    Compute complete multi-factor score for a dish.

    Args:
        dish: Dish dictionary with all fields
        context: User context (mood, craving, etc.)
        feedback: User's feedback summary
        embedding_similarity: Pre-computed embedding similarity (0-1)

    Returns:
        DishScore with all component scores and total
    """
    dish_id = dish.get("dish_id") or dish.get("id")

    # Create score object
    score = DishScore(
        dish_id=dish_id,
        dish_name=dish.get("dish_name", ""),
        dining_hall=dish.get("dining_hall", ""),
        meal_period=dish.get("meal_period", ""),
        category=dish.get("category", ""),
        dish_data=dish
    )

    # Compute individual scores
    taste, is_liked, is_disliked = compute_taste_preference(dish, feedback)
    score.taste_score = taste
    score.is_liked = is_liked
    score.is_disliked = is_disliked

    score.craving_score = compute_craving_match(dish, context.craving)
    score.mood_score = compute_mood_alignment(dish, context.mood)
    score.category_score = compute_category_preference(dish, feedback)
    score.embedding_score = embedding_similarity

    novelty, is_new = compute_novelty_bonus(dish, feedback)
    score.novelty_bonus = novelty
    score.is_new = is_new

    score.dislike_penalty = compute_dislike_penalty(dish, feedback)

    # Compute total
    score.compute_total()

    return score


def build_feedback_summary(feedback_list: list[dict]) -> FeedbackSummary:
    """
    Build FeedbackSummary from raw feedback list.

    Args:
        feedback_list: List of feedback dicts with dish_id, liked, category fields

    Returns:
        FeedbackSummary object
    """
    summary = FeedbackSummary()

    for fb in feedback_list:
        dish_id = fb.get("dish_id")
        liked = fb.get("liked")
        category = fb.get("category", "").lower()

        if dish_id is None:
            continue

        summary.total_ratings += 1

        if liked:
            summary.liked_dish_ids.add(dish_id)
            summary.liked_categories[category] = summary.liked_categories.get(category, 0) + 1
        else:
            summary.disliked_dish_ids.add(dish_id)
            summary.disliked_categories[category] = summary.disliked_categories.get(category, 0) + 1

    return summary
