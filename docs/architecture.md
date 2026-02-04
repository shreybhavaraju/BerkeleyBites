# BerkeleyBites - Complete Architecture Guide

A personalized food recommendation system for UC Berkeley dining halls.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Complete Request Flow](#complete-request-flow)
3. [File Reference](#file-reference)
4. [The Recommendation Engine (RAG + Scoring)](#the-recommendation-engine)
5. [Database Schema](#database-schema)
6. [Key Relationships Diagram](#key-relationships-diagram)

---

## Project Structure

```
BerkeleyBites/
├── scraper.py                      # Scrapes Berkeley dining website daily
│
├── backend/
│   ├── main.py                     # FastAPI app, all API endpoints
│   ├── database.py                 # All Supabase/PostgreSQL operations
│   ├── models.py                   # Pydantic models for request/response validation
│   │
│   └── agents/
│       ├── __init__.py             # Package exports
│       ├── orchestrator.py         # Coordinates the recommendation flow
│       ├── question_agent.py       # Manages the 4 preference questions
│       ├── hybrid_retriever.py     # THE REAL ENGINE: 4-stage RAG pipeline
│       ├── scoring.py              # Multi-factor scoring with mood/craving weights
│       ├── embedding_service.py    # Generates 384-dim vectors for semantic search
│       ├── cache.py                # In-memory caching for performance
│       ├── food_availability_agent.py   # Generates UI summary cards (not for ranking)
│       └── taste_preferences_agent.py   # Generates UI summary cards (not for ranking)
│
├── frontend/
│   └── src/
│       ├── main.tsx                # React entry point
│       ├── App.tsx                 # Root component with routing
│       ├── api/client.ts           # All HTTP calls to backend
│       ├── context/AppContext.tsx  # Global state (profile, messages)
│       ├── hooks/
│       │   ├── useChat.ts          # Chat/recommendation state management
│       │   ├── useMenu.ts          # Menu fetching and filtering
│       │   └── useProfile.ts       # Profile CRUD operations
│       └── components/             # React components
│
└── tests/
    └── test_agents.py              # Unit tests for agents
```

---

## Complete Request Flow

### When User First Loads BerkeleyBites

```
1. Browser loads React app (frontend/src/main.tsx)
        │
        ▼
2. App.tsx renders, AppContext.tsx initializes
        │
        ▼
3. useProfile.ts calls GET /api/profile?user_id=default
        │
        ▼
4. main.py handles request → database.py.get_user_profile()
        │
        ▼
5. Returns dietary preferences (is_vegan, avoid_gluten, etc.)
        │
        ▼
6. useMenu.ts calls GET /api/menu?user_id=default
        │
        ▼
7. main.py → update_agent_context() → filter_by_profile()
        │
        ▼
8. Returns filtered menu (dishes safe for user's diet)
```

### When User Clicks "Get Recommendation"

This is the main flow. Here's every step:

```
FRONTEND
═══════════════════════════════════════════════════════════════════════════════

1. User clicks "/recommend lunch" button
        │
        ▼
2. useChat.ts → api/client.ts → POST /api/chat
   Body: {"message": "/recommend lunch", "session_id": "..."}


BACKEND - main.py
═══════════════════════════════════════════════════════════════════════════════

3. chat() endpoint receives request
        │
        ├── Detects "/recommend" command
        │
        ▼
4. Creates pending recommendation state
   _pending_recommendations[session_id] = {"meal": "lunch", "answered": {}}
        │
        ▼
5. Calls question_agent.get_next_question({})
        │
        ▼
6. Returns FIRST QUESTION to frontend:
   {
     "response_type": "question",
     "question_id": "mood",
     "question_text": "How are you feeling right now?",
     "options": [{"value": "happy", "label": "Happy", "emoji": "😊"}, ...]
   }


FRONTEND - Question Loop (repeats 4 times)
═══════════════════════════════════════════════════════════════════════════════

7. User sees question, clicks an option (e.g., "Stressed")
        │
        ▼
8. useChat.ts → POST /api/chat
   Body: {"message": "answer:mood:stressed"}


BACKEND - main.py (question loop)
═══════════════════════════════════════════════════════════════════════════════

9. handle_question_answer() parses "answer:mood:stressed"
        │
        ▼
10. Updates pending state:
    _pending_recommendations[session_id]["answered"]["mood"] = "stressed"
        │
        ▼
11. Checks: all_questions_answered()? NO
        │
        ▼
12. Returns NEXT QUESTION ("What kind of food sounds good?")
        │
        ▼
    ... repeats for craving, spice, time ...
        │
        ▼
13. After 4th answer, all_questions_answered() = YES
        │
        ▼
14. Calls generate_recommendation(session_id, user_id, "lunch", answered)


BACKEND - generate_recommendation() in main.py
═══════════════════════════════════════════════════════════════════════════════

15. format_context_for_recommendation(answered) converts answers:
    {
      "mood": "stressed",
      "craving": "healthy",
      "spice_level": "mild",
      "time_constraint": "normal"
    }
        │
        ▼
16. Saves mood to database for future sessions:
    save_user_mood(user_id, "stressed")
        │
        ▼
17. Calls orchestrator.get_recommendation(
      query="/recommend lunch",
      meal="lunch",
      session_id="...",
      question_context={mood, craving, spice_level, time_constraint}
    )


BACKEND - orchestrator.py
═══════════════════════════════════════════════════════════════════════════════

18. get_recommendation() is called
        │
        ▼
19. _use_hybrid_retriever is True, so calls:
    _get_hybrid_recommendation(meal="lunch", question_context={...})
        │
        ▼
20. Builds UserContext from question_context:
    UserContext(
      user_id="default",
      mood="stressed",
      craving="healthy",
      spice_level="mild",
      time_constraint="normal",
      meal_period="lunch"
    )
        │
        ▼
21. Builds UI summaries from question answers:
    _build_summaries_from_questions(question_context, "lunch")
    → {"mood": {...}, "craving": {...}, "spice": {...}, "time": {...}}
        │
        ▼
22. Gets the retriever and calls:
    retriever.retrieve_recommendations(
      user_id="default",
      user_context=UserContext(...),
      meal_period="lunch",
      user_profile={is_vegan: False, avoid_gluten: True, ...}
    )


BACKEND - hybrid_retriever.py (THE REAL ENGINE)
═══════════════════════════════════════════════════════════════════════════════

23. retrieve_recommendations() runs the 4-STAGE PIPELINE:

    ┌─────────────────────────────────────────────────────────────────────┐
    │ STAGE 1: SQL HARD FILTERS (~5ms)                                     │
    │                                                                      │
    │ stage1_sql_filters(scrape_date, user_profile, meal_period)          │
    │                                                                      │
    │ • Loads today's dishes from database.get_dishes()                   │
    │ • Filters by meal_period (e.g., "lunch")                            │
    │ • Applies dietary restrictions:                                      │
    │   - is_vegan=True? Keep only vegan dishes                           │
    │   - avoid_gluten=True? Remove dishes with has_gluten=True           │
    │   - etc.                                                            │
    │                                                                      │
    │ Input:  245 total dishes                                            │
    │ Output: 180 dishes (dietary-safe)                                   │
    └─────────────────────────────────────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ STAGE 2: VECTOR SIMILARITY SEARCH (~15ms)                            │
    │                                                                      │
    │ stage2_vector_search(candidates, user_context)                      │
    │                                                                      │
    │ • Generates query embedding from mood + craving + meal:             │
    │   "stressed healthy lunch" → [0.23, -0.15, 0.87, ...] (384 floats)  │
    │                                                                      │
    │ • Calls pgvector in PostgreSQL to find similar dishes:              │
    │   SELECT dish_id, 1 - (embedding <=> query_embedding) AS similarity │
    │   FROM dishes WHERE dish_id IN (filtered_ids)                       │
    │   ORDER BY similarity DESC LIMIT 30                                 │
    │                                                                      │
    │ • Returns dishes with similarity scores (0.0 to 1.0)                │
    │                                                                      │
    │ Input:  180 dietary-safe dishes                                     │
    │ Output: 30 semantically similar dishes with similarity scores       │
    └─────────────────────────────────────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ STAGE 3: MULTI-FACTOR SCORING (~10ms)                                │
    │                                                                      │
    │ stage3_scoring(dishes_with_similarity, user_context, feedback)      │
    │                                                                      │
    │ For EACH dish, scoring.py computes:                                 │
    │                                                                      │
    │   taste_score (35%)                                                 │
    │     → Did user like/dislike this dish before?                       │
    │     → Liked = 1.0, Disliked = 0.0, New = 0.5                        │
    │                                                                      │
    │   craving_score (28%)                                               │
    │     → Does dish match "healthy" craving?                            │
    │     → CRAVING_KEYWORDS["healthy"]["high"] = ["salad", "grilled"...] │
    │     → "Garden Salad" contains "salad" → score = 1.0                 │
    │                                                                      │
    │   mood_score (17%)                                                  │
    │     → Does dish match "stressed" mood?                              │
    │     → MOOD_FOOD_MAPPING["stressed"]["high"] = ["light", "fresh"...] │
    │     → "Fresh Garden Salad" contains "fresh" → score = 1.0           │
    │                                                                      │
    │   category_score (10%)                                              │
    │     → Does user historically like this category?                    │
    │     → User liked 5 salads, disliked 1 → score = 5/6 = 0.83          │
    │                                                                      │
    │   embedding_score (5%)                                              │
    │     → Semantic similarity from Stage 2                              │
    │                                                                      │
    │   novelty_bonus (+5%)                                               │
    │     → Dish user hasn't tried before                                 │
    │                                                                      │
    │   dislike_penalty (-30%)                                            │
    │     → Dish user explicitly disliked                                 │
    │                                                                      │
    │ TOTAL = (taste × 0.35) + (craving × 0.28) + (mood × 0.17)          │
    │       + (category × 0.10) + (embedding × 0.05)                      │
    │       + novelty_bonus - dislike_penalty                             │
    │                                                                      │
    │ Input:  30 dishes with similarity scores                            │
    │ Output: 30 dishes sorted by total_score, take top 8                 │
    └─────────────────────────────────────────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │ STAGE 4: LLM FINAL SELECTION (~500ms)                                │
    │                                                                      │
    │ stage4_llm_selection(top_8_scores, user_context)                    │
    │                                                                      │
    │ • Builds prompt with top 8 pre-scored dishes                        │
    │ • Sends to Perplexity API (LLM)                                     │
    │ • LLM picks 3-4 diverse dishes and writes explanations              │
    │                                                                      │
    │ Prompt:                                                             │
    │ "User Context: stressed, wants healthy, mild spice                  │
    │  Pre-scored Dishes:                                                 │
    │  1. Garden Salad (Crossroads) - Score: 0.87                         │
    │  2. Grain Bowl (Foothill) - Score: 0.82                             │
    │  3. Grilled Chicken (Cafe 3) - Score: 0.79                          │
    │  ...                                                                │
    │  Select 3-4 diverse dishes and write explanations."                 │
    │                                                                      │
    │ LLM Response (JSON):                                                │
    │ [                                                                   │
    │   {"dish_name": "Garden Salad", "dining_hall": "Crossroads",        │
    │    "explanation": "Light and refreshing, perfect for a stressful   │
    │    day when you want something healthy but not heavy."},            │
    │   ...                                                               │
    │ ]                                                                   │
    │                                                                      │
    │ Input:  Top 8 scored dishes                                         │
    │ Output: 3-4 recommendations with personalized explanations          │
    └─────────────────────────────────────────────────────────────────────┘


RESPONSE FLOWS BACK UP
═══════════════════════════════════════════════════════════════════════════════

24. hybrid_retriever returns to orchestrator:
    {
      "recommendations": [{"dish_name": "...", "explanation": "..."}, ...],
      "top_scores": [DishScore objects],
      "stage_stats": {"stage1_ms": 5, "stage2_ms": 15, ...}
    }
        │
        ▼
25. orchestrator._get_hybrid_recommendation() adds retrieval stats to summaries
        │
        ▼
26. Returns to main.py.generate_recommendation()
        │
        ▼
27. main.py converts summaries to AgentSummary models, returns:
    RecommendationResponse(
      agent_summaries={"mood": {...}, "craving": {...}, ...},
      recommendation="Here are my top picks for you:\n\n### 1. Garden Salad...",
      session_id="..."
    )
        │
        ▼
28. Frontend receives JSON, useChat.ts updates messages state
        │
        ▼
29. React renders recommendation with summary cards
```

---

## File Reference

### Backend Core

| File | Purpose | Called By | Calls |
|------|---------|-----------|-------|
| **main.py** | FastAPI app, all API endpoints, request routing | Frontend HTTP | database.py, orchestrator.py, question_agent.py |
| **database.py** | All Supabase/PostgreSQL operations | main.py, hybrid_retriever.py, agents | Supabase client |
| **models.py** | Pydantic models for validation | main.py | - |

### Agents

| File | Purpose | Called By | Calls |
|------|---------|-----------|-------|
| **orchestrator.py** | Coordinates recommendation flow, builds UI summaries | main.py | hybrid_retriever.py, question_agent (indirectly) |
| **question_agent.py** | Manages 4 preference questions (mood, craving, spice, time) | main.py | - |
| **hybrid_retriever.py** | THE REAL ENGINE: 4-stage RAG pipeline | orchestrator.py | database.py, scoring.py, embedding_service.py, cache.py |
| **scoring.py** | Multi-factor scoring (taste, craving, mood, category) | hybrid_retriever.py | - |
| **embedding_service.py** | Generates 384-dim vectors using sentence-transformers | hybrid_retriever.py, scraper.py | sentence-transformers model |
| **cache.py** | In-memory caching for dishes, embeddings, feedback | hybrid_retriever.py | - |
| **food_availability_agent.py** | Generates UI summary card for available dishes | orchestrator.py (legacy path only) | - |
| **taste_preferences_agent.py** | Generates UI summary card for user's taste history | orchestrator.py (legacy path only) | - |

### Frontend

| File | Purpose | Called By | Calls |
|------|---------|-----------|-------|
| **main.tsx** | React entry point, renders App | Browser | App.tsx |
| **App.tsx** | Root component, routing, providers | main.tsx | AppContext, components |
| **api/client.ts** | All HTTP calls to backend | hooks | fetch() → backend |
| **context/AppContext.tsx** | Global state (profile, messages, loading) | App.tsx, hooks | - |
| **hooks/useChat.ts** | Chat state, question/answer flow | components | api/client.ts |
| **hooks/useMenu.ts** | Menu fetching, filtering | components | api/client.ts |
| **hooks/useProfile.ts** | Profile CRUD | components | api/client.ts |

### Other

| File | Purpose | Called By | Calls |
|------|---------|-----------|-------|
| **scraper.py** | Scrapes Berkeley dining website, generates embeddings | Cron job / manual | database.py, embedding_service.py |

---

## The Recommendation Engine

### Why This Architecture?

**Problem with pure LLM approach:**
- LLM doesn't know today's menu → hallucinations
- LLM can't guarantee dietary safety → dangerous
- Every request = expensive API call → slow & costly
- Hard to debug → "why did it recommend that?"

**Solution: Hybrid RAG with deterministic scoring**

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         HYBRID RAG ARCHITECTURE                             │
│                                                                            │
│  User Input                                                                │
│  (mood, craving, spice, time, dietary profile)                            │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 1: SQL FILTERS                                                 │  │
│  │ • 100% deterministic                                                 │  │
│  │ • Guarantees dietary safety (vegan sees NO meat)                     │  │
│  │ • Fast (~5ms)                                                        │  │
│  │ • No AI cost                                                         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 2: VECTOR SEARCH                                               │  │
│  │ • Semantic similarity via embeddings                                 │  │
│  │ • "healthy" finds "Garden Salad" (no keyword match needed)           │  │
│  │ • pgvector in PostgreSQL                                             │  │
│  │ • Fast (~15ms)                                                       │  │
│  │ • No AI cost (embeddings pre-computed)                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 3: MULTI-FACTOR SCORING                                        │  │
│  │ • 100% deterministic                                                 │  │
│  │ • Weights: taste(35%) + craving(28%) + mood(17%) + category(10%)    │  │
│  │            + embedding(5%) + novelty_bonus - dislike_penalty         │  │
│  │ • Debuggable: can explain every score                                │  │
│  │ • Fast (~10ms)                                                       │  │
│  │ • No AI cost                                                         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 4: LLM REFINEMENT                                              │  │
│  │ • Only sees top 8 pre-scored dishes                                  │  │
│  │ • Can only pick from REAL dishes                                     │  │
│  │ • Writes personalized explanations                                   │  │
│  │ • Ensures diversity (different categories/halls)                     │  │
│  │ • ~500ms (but only 1 API call)                                       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│       │                                                                    │
│       ▼                                                                    │
│  Final Recommendations (3-4 dishes with explanations)                      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Scoring Deep Dive

Located in `scoring.py`. Here's exactly how a dish gets scored:

```python
# Example: Scoring "Garden Salad" for a stressed user who wants healthy food

# User context:
#   mood = "stressed"
#   craving = "healthy"
#   user has previously: liked 5 salads, disliked 1 pizza

# TASTE SCORE (35% weight)
# Has user rated this specific dish?
# → New dish, never rated → 0.5 (neutral)

# CRAVING SCORE (28% weight)
# Does "Garden Salad" match "healthy" craving?
# CRAVING_KEYWORDS["healthy"]["high"] = ["salad", "grilled", "steamed", ...]
# "salad" is in dish name → 1.0

# MOOD SCORE (17% weight)
# Does "Garden Salad" match "stressed" mood?
# MOOD_FOOD_MAPPING["stressed"]["high"] = ["light", "fresh", "simple", ...]
# No direct match, but category "salad" is in mapping → 0.6

# CATEGORY SCORE (10% weight)
# User's history with "salad" category:
# liked_count = 5, disliked_count = 0
# like_ratio = 5 / 5 = 1.0

# EMBEDDING SCORE (5% weight)
# From Stage 2 vector similarity = 0.87

# NOVELTY BONUS
# User has 6+ ratings, dish is new → +0.05

# DISLIKE PENALTY
# Not previously disliked → 0.0

# TOTAL SCORE:
# (0.5 × 0.35) + (1.0 × 0.28) + (0.6 × 0.17) + (1.0 × 0.10) + (0.87 × 0.05) + 0.05 - 0.0
# = 0.175 + 0.28 + 0.102 + 0.10 + 0.0435 + 0.05
# = 0.75
```

### What Are Embeddings?

Embeddings convert text into numbers that capture meaning:

```
"Garden Salad"     → [0.82, -0.15, 0.44, 0.23, ...] (384 numbers)
"healthy food"     → [0.79, -0.12, 0.48, 0.21, ...] (similar numbers!)
"Pepperoni Pizza"  → [-0.45, 0.72, -0.33, 0.12, ...] (very different)
```

Similar meanings = similar numbers = can find matches without keyword overlap.

We use `all-MiniLM-L6-v2` model (runs locally, free, ~10ms per embedding).

---

## Database Schema

### Tables

**dishes** - Today's menu items (scraped daily)
```sql
id              UUID PRIMARY KEY
dish_name       TEXT NOT NULL
dining_hall     TEXT NOT NULL
meal_period     TEXT NOT NULL        -- "Breakfast", "Lunch", "Dinner"
category        TEXT
is_vegan        BOOLEAN DEFAULT FALSE
is_vegetarian   BOOLEAN DEFAULT FALSE
is_halal        BOOLEAN DEFAULT FALSE
is_kosher       BOOLEAN DEFAULT FALSE
has_gluten      BOOLEAN DEFAULT FALSE
has_milk        BOOLEAN DEFAULT FALSE
has_egg         BOOLEAN DEFAULT FALSE
has_tree_nuts   BOOLEAN DEFAULT FALSE
has_soybeans    BOOLEAN DEFAULT FALSE
embedding       VECTOR(384)          -- pgvector for semantic search
scrape_date     DATE NOT NULL
UNIQUE(dish_name, dining_hall, meal_period, scrape_date)
```

**user_profiles** - Dietary preferences
```sql
id              UUID PRIMARY KEY
user_id         TEXT UNIQUE NOT NULL
is_vegan        BOOLEAN DEFAULT FALSE
is_vegetarian   BOOLEAN DEFAULT FALSE
is_halal        BOOLEAN DEFAULT FALSE
is_kosher       BOOLEAN DEFAULT FALSE
avoid_gluten    BOOLEAN DEFAULT FALSE
avoid_milk      BOOLEAN DEFAULT FALSE
avoid_nuts      BOOLEAN DEFAULT FALSE
-- etc.
```

**feedback** - User ratings (for taste learning)
```sql
id              UUID PRIMARY KEY
user_id         TEXT NOT NULL
dish_id         UUID REFERENCES dishes(id)
dish_name       TEXT NOT NULL
liked           BOOLEAN NOT NULL     -- TRUE = liked, FALSE = disliked
rating_date     DATE NOT NULL
UNIQUE(user_id, dish_id, rating_date)
```

**user_moods** - Current mood state
```sql
user_id         TEXT PRIMARY KEY
mood            TEXT NOT NULL        -- "happy", "stressed", "tired", etc.
updated_at      TIMESTAMP
```

---

## Key Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND                                      │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   useChat   │────▶│ api/client  │────▶│   HTTP      │                  │
│   │   useMenu   │     │    .ts      │     │  Requests   │                  │
│   │  useProfile │     └─────────────┘     └──────┬──────┘                  │
│   └─────────────┘                                │                          │
│                                                  │                          │
└──────────────────────────────────────────────────┼──────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                BACKEND                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                           main.py                                    │  │
│   │                                                                      │  │
│   │  /api/chat ──────┬──▶ question_agent.py (4 questions)               │  │
│   │                  │                                                   │  │
│   │                  └──▶ generate_recommendation()                      │  │
│   │                              │                                       │  │
│   │  /api/menu ──────────────────┼──▶ update_agent_context()            │  │
│   │  /api/profile ───────────────┼──▶ database.py                       │  │
│   │  /api/feedback ──────────────┘                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        orchestrator.py                               │  │
│   │                                                                      │  │
│   │  get_recommendation() ──▶ _get_hybrid_recommendation()              │  │
│   │                                      │                               │  │
│   │                                      ▼                               │  │
│   │                          builds UserContext from                     │  │
│   │                          question_context                            │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                      hybrid_retriever.py                             │  │
│   │                      (THE REAL ENGINE)                               │  │
│   │                                                                      │  │
│   │  retrieve_recommendations()                                          │  │
│   │       │                                                              │  │
│   │       ├──▶ Stage 1: stage1_sql_filters() ──▶ database.py            │  │
│   │       │                                                              │  │
│   │       ├──▶ Stage 2: stage2_vector_search() ──▶ embedding_service.py │  │
│   │       │                                        cache.py              │  │
│   │       │                                                              │  │
│   │       ├──▶ Stage 3: stage3_scoring() ──▶ scoring.py                 │  │
│   │       │                                                              │  │
│   │       └──▶ Stage 4: stage4_llm_selection() ──▶ Perplexity API       │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         database.py                                  │  │
│   │                                                                      │  │
│   │  get_dishes()           → dishes table                               │  │
│   │  get_user_profile()     → user_profiles table                        │  │
│   │  get_user_feedback()    → feedback table                             │  │
│   │  get_dish_embeddings()  → dishes.embedding column (pgvector)         │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE (PostgreSQL)                                │
│                                                                             │
│   ┌──────────────┐  ┌───────────────┐  ┌──────────┐  ┌────────────┐        │
│   │    dishes    │  │ user_profiles │  │ feedback │  │ user_moods │        │
│   │              │  │               │  │          │  │            │        │
│   │ + embedding  │  │ + dietary     │  │ + liked  │  │ + mood     │        │
│   │   (pgvector) │  │   preferences │  │   history│  │            │        │
│   └──────────────┘  └───────────────┘  └──────────┘  └────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | System status |
| `/api/menu` | GET | Get filtered dishes |
| `/api/menu/summary` | GET | Menu statistics |
| `/api/profile` | GET/PUT | User dietary preferences |
| `/api/profile/mood` | GET/PUT | Current mood |
| `/api/feedback` | POST | Submit like/dislike |
| `/api/chat` | POST | Main recommendation endpoint |

### Run Commands

```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Scrape menu
python scraper.py

# Run tests
pytest tests/ -v
```

### Environment Variables

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PERPLEXITY_API_KEY=your_perplexity_key
```
