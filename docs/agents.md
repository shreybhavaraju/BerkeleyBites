# AI Agents System (Beginner-Friendly)

This document explains how BerkeleyBites uses AI to make personalized food recommendations.

---

## What is an "Agent"?

An **agent** is a piece of software that:
1. Has a specific job
2. Can be called when needed
3. Returns useful information

Think of agents like specialists in a hospital:
- The **cardiologist** specializes in hearts
- The **dermatologist** specializes in skin
- They each do their job, then report to the primary care doctor

In BerkeleyBites:
- The **Question Agent** collects user preferences (mood, craving, spice, time)
- The **Taste Agent** generates UI summaries from feedback history
- The **Hybrid Retriever + Scoring** is the real recommendation engine
- The **Orchestrator** coordinates them all (like the primary care doctor)

---

## Why Multiple Agents?

### The Problem with One Big AI Prompt

You might think: "Why not just ask ChatGPT everything at once?"

```
Bad approach:
"I'm a UC Berkeley student feeling tired. I want something healthy.
I've liked Asian food before. What should I eat from today's menu?"
```

**Problems:**
1. **AI doesn't know today's menu** - It might suggest dishes that don't exist
2. **AI can't see your past likes** - No access to your history
3. **Hard to test** - If something's wrong, where's the bug?
4. **Expensive** - Every request uses costly AI API calls

### The Solution: Specialized Agents

```
Good approach:

1. Question Agent: "User is tired, wants healthy, mild spice, normal time"
2. Hybrid Retriever: Runs 4-stage pipeline with mood weights in scoring
3. Taste Agent: [for UI] "User likes Asian, dislikes heavy foods"
4. Food Agent: [for UI] "Today's menu has 245 dishes, 12 match filters"
5. Orchestrator: Returns scored dishes + LLM-written explanation
```

**Benefits:**
- Each agent does ONE thing well
- Most agents don't need expensive AI calls
- If one fails, others still work
- Easy to test and debug
- Easy to add new agents

---

## The Agent Files

Here's every file in the `/agents/` folder and what it does:

```
agents/
├── __init__.py              # Makes this a Python package
├── orchestrator.py          # The coordinator (calls all other agents)
├── question_agent.py        # Manages the Q&A flow (mood, craving, spice, time)
├── food_availability_agent.py # UI summary: available dishes
├── taste_preferences_agent.py # UI summary: user's likes/dislikes
├── hybrid_retriever.py      # The smart dish selection system (REAL ENGINE)
├── scoring.py               # How dishes are ranked (includes mood weights)
├── embedding_service.py     # Converts text to numbers
└── cache.py                 # Speeds things up
```

**Architecture Note:** The "agents" are not AI agents - they're specialized modules:
- **question_agent**: Collects user preferences
- **hybrid_retriever + scoring**: The actual recommendation engine
- **taste_preferences_agent & food_availability_agent**: Generate UI summary cards only

---

## Agent 1: Food Availability Agent

**File:** `agents/food_availability_agent.py`

**Job:** Query the database for available dishes

**How it works:**
1. Receives filters (meal period, dietary restrictions, etc.)
2. Queries the pandas DataFrame (in-memory copy of database)
3. Returns matching dishes

```python
def get_available_dishes(
    meal_period="",      # "Breakfast", "Lunch", "Dinner"
    dining_hall="",      # "Dining Commons", etc.
    category="",         # "Entrees", "Soups", etc.
    is_vegetarian=False,
    is_vegan=False,
    limit=15
):
    # Start with all dishes
    df = _menu_df.copy()

    # Apply filters
    if meal_period:
        df = df[df['meal_period'] == meal_period]
    if dining_hall:
        df = df[df['dining_hall'] == dining_hall]
    if is_vegan:
        df = df[df['is_vegan'] == True]
    elif is_vegetarian:
        df = df[df['is_vegetarian'] == True]

    # Return limited results
    return df.head(limit)
```

**Example:**
```
Input: meal_period="Lunch", is_vegetarian=True
Output: [
    "Garden Salad - Dining Commons - Salads",
    "Pasta Primavera - Café Strada - Entrees",
    "Veggie Burger - Crossroads - Grill",
    ...
]
```

**Why this design:**
- Database operations are fast (~5ms)
- No AI cost
- Filters are applied in sequence (most restrictive first)
- Samples from multiple dining halls for variety

---

## Agent 3: Taste Preferences Agent

**File:** `agents/taste_preferences_agent.py`

**Job:** Analyze user's feedback history to identify patterns

**How it works:**
1. Load all feedback for this user
2. Analyze liked vs disliked dishes
3. Identify preferred categories and dining halls

```python
MIN_FEEDBACK_COUNT = 3  # Need at least 3 ratings to analyze

def get_taste_preferences():
    if len(_feedback_df) < MIN_FEEDBACK_COUNT:
        return "Not enough ratings yet. Rate more dishes for personalized suggestions!"

    # Separate liked and disliked
    liked = _feedback_df[_feedback_df['liked'] == True]
    disliked = _feedback_df[_feedback_df['liked'] == False]

    # Find favorite categories
    favorite_categories = liked['category'].value_counts().head(3).index.tolist()

    # Find avoided categories
    disliked_categories = disliked['category'].value_counts().head(2).index.tolist()

    # Calculate satisfaction rate
    like_ratio = len(liked) / len(_feedback_df) * 100

    return f"""
    Taste Analysis ({len(_feedback_df)} ratings):

    Favorite categories: {', '.join(favorite_categories)}
    Usually avoids: {', '.join(disliked_categories) or 'Nothing specific'}
    Overall satisfaction: {like_ratio:.0f}% liked
    """
```

**Example:**
```
User has rated 15 dishes:
- Liked: 12 (80%)
- Disliked: 3 (20%)

Output:
"Favorite categories: Asian, Italian, Salads
 Usually avoids: Heavy Entrees
 Overall satisfaction: 80% liked"
```

**Why this design:**
- Minimum threshold prevents unreliable analysis
- Identifies both positive and negative patterns
- Works without AI (pure data analysis)

---

## Agent 4: Question Agent

**File:** `agents/question_agent.py`

**Job:** Manage the multi-turn question flow before recommendation

**The Questions:**
```python
QUESTIONS = [
    {
        "id": "mood",
        "question_text": "How are you feeling right now?",
        "options": [
            {"value": "happy", "label": "Happy", "emoji": "😊"},
            {"value": "stressed", "label": "Stressed", "emoji": "😤"},
            {"value": "tired", "label": "Tired", "emoji": "😴"},
            {"value": "adventurous", "label": "Adventurous", "emoji": "🤠"},
            {"value": "grumpy", "label": "Grumpy", "emoji": "😠"},
        ]
    },
    {
        "id": "craving",
        "question_text": "What kind of food sounds good?",
        "options": [
            {"value": "comfort", "label": "Comfort Food", "emoji": "🍲"},
            {"value": "healthy", "label": "Something Healthy", "emoji": "🥗"},
            {"value": "quick", "label": "Quick Bite", "emoji": "🥪"},
            {"value": "filling", "label": "Big Meal", "emoji": "🍛"},
        ]
    },
    {
        "id": "spice",
        "question_text": "How adventurous with spice today?",
        "options": [
            {"value": "none", "label": "No Spice", "emoji": "🌶️"},
            {"value": "mild", "label": "Mild", "emoji": "🌶️🌶️"},
            {"value": "medium", "label": "Medium", "emoji": "🌶️🌶️🌶️"},
            {"value": "hot", "label": "Bring the Heat!", "emoji": "🔥"},
        ]
    },
    {
        "id": "time",
        "question_text": "How much time do you have?",
        "options": [
            {"value": "rush", "label": "In a Rush", "emoji": "⚡"},
            {"value": "normal", "label": "Normal", "emoji": "🕐"},
            {"value": "leisurely", "label": "Taking My Time", "emoji": "☕"},
        ]
    },
]
```

**How it works:**
```python
def get_next_question(answered_questions):
    """Return the next unanswered question"""
    for question in QUESTIONS:
        if question["id"] not in answered_questions:
            return question
    return None  # All questions answered

def all_questions_answered(answered):
    """Check if we have all answers"""
    return len(answered) >= len(QUESTIONS)
```

**Why this design:**
- Questions gather context without AI
- Emojis make selection fun and quick
- Sequential flow prevents overwhelming users
- Answers feed into the scoring system

---

## The Orchestrator

**File:** `agents/orchestrator.py`

**Job:** Coordinate all agents and generate the final recommendation

**The Flow:**
```python
def get_recommendation(user_id, user_profile, message, session_id):

    # Step 1: Set context for all agents
    set_orchestrator_context(
        menu_df=filtered_menu,
        feedback_df=user_feedback,
        user_profile=user_profile,
        user_id=user_id,
        user_mood=current_mood
    )

    # Step 2: Gather context from all agents
    context = gather_agent_context()
    # Returns:
    # {
    #     "mood": "User is happy, try adventurous foods...",
    #     "preferences": "Likes Asian, dislikes heavy...",
    #     "dishes": "245 available, 12 match filters...",
    #     "questions": "Wants healthy, mild spice, normal time..."
    # }

    # Step 3: Try hybrid retrieval (fast, deterministic)
    if _use_hybrid_retriever:
        result = _get_hybrid_recommendation(question_context)
        if result:
            return result

    # Step 4: Fallback to LLM-only
    return _get_legacy_recommendation(context)
```

**Why this design:**
- Single coordination point
- Feature flag for hybrid retriever
- Fallback ensures recommendations always work
- Clear separation of responsibilities

---

## The Hybrid Retriever (RAG System)

**File:** `agents/hybrid_retriever.py`

**What is RAG?**

**RAG** = **R**etrieval **A**ugmented **G**eneration

Instead of asking AI "what should I eat?" (and getting hallucinated answers), we:
1. **Retrieve** relevant dishes from the database
2. **Augment** the AI prompt with real data
3. **Generate** a recommendation based on actual options

**The 4-Stage Pipeline:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HYBRID RETRIEVER PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────┘

STAGE 1: SQL HARD FILTERS (~5ms)
───────────────────────────────────────────────────────────────────────────────
Remove dishes that violate dietary restrictions

    Input: 245 dishes

    Filters applied:
    - User is vegan? Remove all non-vegan dishes
    - User avoids gluten? Remove dishes with gluten
    - User avoids nuts? Remove dishes with nuts

    Output: 180 dishes (dietary-safe)


STAGE 2: VECTOR SEARCH (~15ms)
───────────────────────────────────────────────────────────────────────────────
Find semantically similar dishes using embeddings

    User's craving: "comfort food"

    Embedding: "comfort food" → [0.23, -0.15, 0.87, ...]

    Compare to all dish embeddings:
    - "Chicken Noodle Soup" → similarity: 0.92 ✓
    - "Mac and Cheese" → similarity: 0.88 ✓
    - "Sushi Roll" → similarity: 0.34 ✗

    Output: Top 30 similar dishes


STAGE 3: MULTI-FACTOR SCORING (~10ms)
───────────────────────────────────────────────────────────────────────────────
Score each dish on multiple factors

    For each dish, calculate:

    taste_score (30%)     → Based on past likes/dislikes
    craving_score (25%)   → Matches what user wants
    mood_score (15%)      → Good for current mood
    category_score (10%)  → From a preferred category
    spice_score (10%)     → Matches spice preference
    embedding_score (5%)  → Semantic similarity

    Bonuses/Penalties:
    + novelty_bonus (5%)  → Haven't tried it before
    - dislike_penalty (30%) → Previously disliked

    Output: Ranked list with scores


STAGE 4: LLM REFINEMENT (~500ms)
───────────────────────────────────────────────────────────────────────────────
AI selects final recommendations and writes explanation

    Input to AI:
    "Here are the top 8 dishes with scores:
     1. Teriyaki Chicken (0.87)
     2. Garden Salad (0.82)
     3. Pasta Primavera (0.79)
     ...

     User context:
     - Mood: happy
     - Craving: healthy
     - Spice: mild

     Select 3-4 dishes and explain why."

    Output: Final recommendation with explanation
```

**Configuration:**
```python
vector_candidates = 30   # How many dishes from vector search
top_k_for_llm = 8        # How many to send to AI
final_selection = 4      # How many recommendations to show
```

**Why this design:**
- **Speed**: Database + vectors faster than pure AI
- **Accuracy**: AI only chooses from real dishes
- **Cost**: Less tokens sent to AI
- **Control**: Deterministic scoring is predictable
- **Transparency**: Can explain why each dish was chosen

---

## The Scoring System

**File:** `agents/scoring.py`

**How dishes are ranked:**

```python
# Weight distribution (must sum to ~1.0)
WEIGHTS = {
    "taste": 0.30,      # Most important: past preferences
    "craving": 0.25,    # What they want right now
    "mood": 0.15,       # Mood-appropriate food
    "category": 0.10,   # Preferred categories
    "spice": 0.10,      # Spice preference match
    "embedding": 0.05,  # Semantic similarity
}

# Bonuses and penalties
NOVELTY_BONUS = 0.05     # Never tried before
DISLIKE_PENALTY = -0.30  # Previously disliked
```

**Example Calculation:**

```
Dish: "Teriyaki Chicken Bowl"
User: happy mood, wants "healthy", likes Asian food, mild spice

taste_score = 0.8      # User liked similar dishes before
craving_score = 0.7    # "Healthy" matches chicken bowl
mood_score = 0.9       # Happy → adventurous foods OK
category_score = 0.85  # Asian is a preferred category
spice_score = 0.9      # Mild dish matches mild preference
embedding_score = 0.6  # Moderate semantic match

weighted_score = (0.8 × 0.30) + (0.7 × 0.25) + (0.9 × 0.15) +
                 (0.85 × 0.10) + (0.9 × 0.10) + (0.6 × 0.05)
               = 0.24 + 0.175 + 0.135 + 0.085 + 0.09 + 0.03
               = 0.755

novelty_bonus = 0.05   # Never tried before

final_score = 0.755 + 0.05 = 0.805 ≈ 0.81
```

**Craving Keywords:**
```python
CRAVING_KEYWORDS = {
    "comfort": ["soup", "pasta", "warm", "cheese", "bread"],
    "healthy": ["salad", "grain", "vegetable", "lean", "fresh"],
    "quick": ["sandwich", "wrap", "grab", "simple"],
    "filling": ["bowl", "plate", "hearty", "protein", "rice"],
}
```

**Why these weights?**
- **Taste (30%)**: Past behavior is the best predictor
- **Craving (25%)**: Immediate want is very important
- **Mood (15%)**: Emotional state affects food satisfaction
- **Category (10%)**: Supporting signal for preferred food types
- **Spice (10%)**: Matches user's spice tolerance
- **Embedding (5%)**: Semantic backup for similarity

---

## The Embedding Service

**File:** `agents/embedding_service.py`

**What are Embeddings?**

Embeddings convert text into numbers (vectors) that capture meaning:

```
"Chicken Noodle Soup" → [0.23, -0.15, 0.87, 0.44, ..., 0.12]
                        └─────────── 384 numbers ───────────┘
```

**Why?** Similar meanings have similar numbers:
```
"Chicken Broth"     → [0.21, -0.18, 0.85, 0.41, ...]  # Very similar!
"Ice Cream Sundae"  → [-0.45, 0.72, -0.33, 0.12, ...] # Very different!
```

**The Model:**
```python
model_name = "all-MiniLM-L6-v2"  # Small, fast, good quality
vector_size = 384                 # 384 numbers per embedding
```

**Why this model?**
- **Free**: Runs locally, no API costs
- **Fast**: ~10ms per embedding
- **Small**: Only 80MB model size
- **Quality**: Good enough for food recommendations

**Text Enhancement:**

Before embedding, we expand terse names:
```python
def enhance_text(dish_name):
    # "Soup" → "soup, broth, warm, comforting, liquid"
    # "Salad" → "salad, fresh, vegetables, healthy, light"

    # Also infer cuisine:
    # "Teriyaki Chicken" → add "Japanese, Asian"
    # "Pasta Carbonara" → add "Italian"
```

**Why?**
- "Soup" alone doesn't capture much meaning
- Enhanced descriptions give richer embeddings
- Better semantic matches

---

## The Cache Layer

**File:** `agents/cache.py`

**What is Caching?**

Storing results so we don't recalculate them:

```python
# Without cache:
get_dishes()  # Takes 50ms (database query)
get_dishes()  # Takes 50ms (database query again)
get_dishes()  # Takes 50ms (database query again)

# With cache:
get_dishes()  # Takes 50ms (database query, saves result)
get_dishes()  # Takes 1ms (returns saved result)
get_dishes()  # Takes 1ms (returns saved result)
```

**Cache Configuration:**
```python
CACHE_TTLS = {
    "dishes": 86400,        # 24 hours (menu changes daily)
    "user_feedback": 120,   # 2 minutes (might be updated)
    "embeddings": 86400,    # 24 hours (don't change)
    "query_embeddings": 60, # 1 minute (user queries)
}
```

**How it works:**
```python
class CacheLayer:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()  # Thread safety

    def get(self, key, ttl_seconds):
        with self._lock:
            if key in self._cache:
                age = time.time() - self._timestamps[key]
                if age < ttl_seconds:
                    return self._cache[key]  # Cache hit!
            return None  # Cache miss

    def set(self, key, value):
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
```

**Why these TTLs?**
| Data | TTL | Reasoning |
|------|-----|-----------|
| Dishes | 24 hours | Menu scraped daily at midnight |
| Feedback | 2 minutes | User might update |
| Embeddings | 24 hours | Text doesn't change |
| Query embeddings | 1 minute | Same query = same embedding |

---

## Putting It All Together

**Complete Recommendation Flow:**

```
USER CLICKS "GET RECOMMENDATION"
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│ QUESTION PHASE (question_agent.py)                            │
│                                                               │
│ Q1: "How are you feeling?" → User: "😊 Happy"                │
│ Q2: "What food sounds good?" → User: "🥗 Healthy"            │
│ Q3: "Spice level?" → User: "🌶️ Mild"                         │
│ Q4: "Time available?" → User: "🕐 Normal"                    │
└───────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR (orchestrator.py)                                │
│                                                               │
│ Pass question_context directly to hybrid_retriever            │
│ (mood, craving, spice, time all go to scoring.py)            │
└───────────────────────────────────────────────────────────────┘
            │
            ▼
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│ HYBRID RETRIEVER (hybrid_retriever.py)                        │
│                                                               │
│ Stage 1: SQL Filters    │ 245 → 180 dishes                   │
│ Stage 2: Vector Search  │ 180 → 30 dishes                    │
│ Stage 3: Multi-factor   │ Score each dish                    │
│ Stage 4: LLM Refinement │ Pick top 4 + explain               │
└───────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│ RESPONSE TO USER                                              │
│                                                               │
│ Agent Summaries:                                             │
│ • 😊 Mood: You're feeling happy!                             │
│ • 🎯 Prefs: Looking for healthy, mild spice                  │
│ • 👤 Taste: Based on your love of Asian cuisines             │
│ • 🍽️ Menu: 180 dishes match your preferences                 │
│                                                               │
│ Recommendation:                                               │
│ "I recommend the **Teriyaki Chicken Bowl** from Dining       │
│  Commons! It's fresh, healthy, and matches your              │
│  adventurous mood perfectly."                                 │
└───────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways for Your Interview

1. **Agents are specialists**: Each does one thing well
2. **Most agents don't need AI**: Simple logic or database queries
3. **RAG prevents hallucination**: AI only chooses from real dishes
4. **Scoring is deterministic**: Predictable, debuggable
5. **Caching is crucial**: Sub-100ms response times
6. **Fallbacks ensure reliability**: If one thing fails, others work

**Questions you might be asked:**

- "Why not just use ChatGPT for everything?"
- "How does the scoring work?"
- "What happens if an external service fails?"
- "Why use embeddings instead of keyword search?"

(See [Interview Prep](./interview-prep.md) for detailed answers)
