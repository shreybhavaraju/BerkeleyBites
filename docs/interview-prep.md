# BerkeleyBites - Complete Technical Guide

> A personalized food recommendation system for UC Berkeley dining halls using a multi-agent RAG architecture.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack & Why Each Tool](#2-tech-stack--why-each-tool)
3. [Project Structure](#3-project-structure)
4. [System Architecture](#4-system-architecture)
5. [Data Pipeline](#5-data-pipeline)
6. [The Recommendation Flow](#6-the-recommendation-flow)
7. [File-by-File Breakdown](#7-file-by-file-breakdown)
8. [Key Design Decisions](#8-key-design-decisions)
9. [Interview Q&A](#9-interview-qa)

---

## 1. Project Overview

### What is BerkeleyBites?
BerkeleyBites is an AI-powered food recommendation app for UC Berkeley students. It scrapes daily dining hall menus, learns user preferences from feedback, and generates personalized meal recommendations using a multi-agent system with RAG (Retrieval Augmented Generation).

### The Problem It Solves
- Berkeley has 4+ dining halls with 200+ dishes daily
- Students waste time browsing menus manually
- No personalization based on mood, dietary needs, or taste history
- Existing solutions don't consider real-time availability

### Key Features
1. **Real-time menu data** - Scraped daily from Berkeley dining website
2. **Dietary filtering** - Vegan, vegetarian, halal, kosher, allergen-free
3. **Mood-based recommendations** - Different suggestions for stressed vs. happy
4. **Taste learning** - Remembers what you like/dislike via feedback
5. **Multi-agent AI** - Specialized agents for mood, preferences, availability
6. **Hybrid RAG retrieval** - SQL + Vector + Scoring + LLM pipeline

---

## 2. Tech Stack & Why Each Tool

### Frontend

| Tool | Version | Why This Tool |
|------|---------|---------------|
| **React** | 19.2.0 | Component-based UI, large ecosystem, industry standard |
| **TypeScript** | 5.9 | Type safety catches bugs at compile time, better IDE support |
| **Vite** | 7.2.4 | 10x faster than webpack, instant HMR, native ES modules |
| **Tailwind CSS** | 4.1 | Utility-first CSS, no context switching, rapid prototyping |

### Backend

| Tool | Version | Why This Tool |
|------|---------|---------------|
| **FastAPI** | 0.100+ | Async by default, automatic OpenAPI docs, Pydantic integration |
| **Pydantic** | 2.5+ | Request validation, type coercion, automatic error messages |
| **Uvicorn** | 0.23+ | ASGI server, async support, production-ready |
| **Python** | 3.11+ | Required for type hints, async/await, pattern matching |

### Database

| Tool | Why This Tool |
|------|---------------|
| **Supabase** | Hosted PostgreSQL, built-in auth, real-time subscriptions, free tier |
| **PostgreSQL** | ACID compliance, JSON support, mature ecosystem |
| **pgvector** | Vector similarity search in SQL, no separate vector DB needed |

### AI/ML

| Tool | Why This Tool |
|------|---------------|
| **LangChain** | Abstractions for LLM apps, message history, prompt templates |
| **Perplexity API** | Fast inference, grounded responses, cheaper than GPT-4 |
| **sentence-transformers** | Local embeddings, no API costs, 384-dim vectors |
| **all-MiniLM-L6-v2** | Fast inference (~10ms), good quality, small model size |

### Data Processing

| Tool | Why This Tool |
|------|---------------|
| **pandas** | DataFrame operations, filtering, aggregation |
| **BeautifulSoup** | HTML parsing for web scraping |
| **requests** | HTTP client for scraping Berkeley website |

### Development

| Tool | Why This Tool |
|------|---------------|
| **pytest** | Testing framework, fixtures, parametrization |
| **python-dotenv** | Environment variable management |
| **ESLint** | JavaScript/TypeScript linting |

---

## 3. Project Structure

```
BerkeleyBites/
├── scraper.py                    # Daily menu scraping + embedding generation
│
├── backend/                      # ALL BACKEND CODE
│   ├── __init__.py
│   ├── main.py                   # FastAPI endpoints (API layer)
│   ├── database.py               # Supabase operations (data layer)
│   ├── models.py                 # Pydantic request/response models
│   ├── food_agent.py             # Legacy chat agent (free-form commands)
│   │
│   └── agents/                   # Multi-agent recommendation system
│       ├── __init__.py           # Package exports
│       ├── orchestrator.py       # Coordinates all agents
│       ├── mood_agent.py         # Mood → food guidance mapping
│       ├── question_agent.py     # Handles preference questions
│       ├── taste_preferences_agent.py  # Analyzes feedback history
│       ├── food_availability_agent.py  # Queries available dishes
│       ├── hybrid_retriever.py   # 4-stage RAG pipeline
│       ├── scoring.py            # Multi-factor dish ranking
│       ├── embedding_service.py  # Vector embedding generation
│       └── cache.py              # In-memory caching layer
│
├── frontend/
│   └── src/
│       ├── main.tsx              # React entry point
│       ├── App.tsx               # Root component, routing
│       ├── index.css             # Tailwind imports
│       ├── api/
│       │   └── client.ts         # HTTP requests to backend
│       ├── context/
│       │   └── AppContext.tsx    # Global state (profile, mood, messages)
│       ├── hooks/
│       │   ├── useChat.ts        # Chat/recommendation logic
│       │   ├── useMenu.ts        # Menu fetching/filtering
│       │   └── useProfile.ts     # Profile CRUD operations
│       ├── types/
│       │   └── index.ts          # TypeScript interfaces
│       └── components/
│           ├── chat/             # Chat UI components
│           ├── menu/             # Menu browser components
│           ├── profile/          # Profile editor components
│           └── layout/           # Header, shell components
│
├── tests/
│   ├── test_agents.py            # Unit tests for agents
│   └── test_e2e.py               # End-to-end flow tests
│
├── docs/                         # Documentation
├── supabase/                     # Database migrations
├── scripts/                      # Utility scripts
└── requirements.txt              # Python dependencies
```

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER'S BROWSER                                  │
│                                                                             │
│   React Frontend (TypeScript) ─── Port 5173                                 │
│   ├── ChatPanel        → Chat UI, questions, recommendations                │
│   ├── MenuBrowser      → Browse dishes by hall/meal                         │
│   ├── ProfileEditor    → Set dietary preferences                            │
│   └── AppContext       → Global state management                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP (Vite proxy /api/* → :8000)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND                                 │
│                              Port 8000                                       │
│                                                                             │
│   backend/main.py                                                           │
│   ├── GET  /api/menu          → Filtered dishes                             │
│   ├── GET  /api/profile       → User preferences                            │
│   ├── PUT  /api/profile       → Update preferences                          │
│   ├── POST /api/feedback      → Submit like/dislike                         │
│   ├── POST /api/chat          → AI recommendation (main endpoint)           │
│   └── GET  /api/health        → System status                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
        ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
        │   database.py │   │  food_agent   │   │  orchestrator │
        │               │   │   (legacy)    │   │  (multi-agent)│
        │  Supabase     │   │               │   │               │
        │  Operations   │   │  Free-form    │   │  /recommend   │
        │               │   │  chat cmds    │   │  questions    │
        └───────┬───────┘   └───────────────┘   └───────┬───────┘
                │                                       │
                ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SUPABASE (PostgreSQL)                           │
│                                                                             │
│   Tables:                                                                   │
│   ├── dishes          → Menu items (scraped daily)                          │
│   ├── dish_embeddings → Vector embeddings (384-dim)                         │
│   ├── user_profiles   → Dietary preferences                                 │
│   ├── user_moods      → Current mood state                                  │
│   └── feedback        → Like/dislike history                                │
│                                                                             │
│   Extensions: pgvector (vector similarity search)                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Pipeline

### Daily Data Ingestion (scraper.py)

```
UC Berkeley Website          scraper.py              Supabase
dining.berkeley.edu    →    BeautifulSoup     →     dishes table
      │                     parse HTML               │
      │                          │                   │
      │                          ▼                   ▼
      │                     Transform to        embedding_service.py
      │                     DataFrame           sentence-transformers
      │                          │                   │
      │                          │                   ▼
      │                          │              dish_embeddings table
      │                          │              (384-dim vectors)
      └──────────────────────────┴───────────────────┘

Timeline:
1. HTTP GET to dining.berkeley.edu/menus (~500ms)
2. Parse HTML, extract dishes, allergens, dietary flags (~100ms)
3. Transform to DataFrame with boolean columns (~50ms)
4. Upsert to Supabase dishes table (~200ms)
5. Generate embeddings for new dishes (~2s for 200 dishes)
6. Store embeddings in dish_embeddings table (~100ms)
```

### User Interaction Flow

```
User Action                  Frontend                 Backend                  Database
───────────────────────────────────────────────────────────────────────────────────────

1. Load App            →    App.tsx              →  GET /api/profile    →   user_profiles
                            AppContext               GET /api/menu           dishes
                                                     GET /api/mood           user_moods

2. Set Preferences     →    ProfileEditor        →  PUT /api/profile    →   user_profiles
                            useProfile.ts

3. Browse Menu         →    MenuBrowser          →  GET /api/menu       →   dishes
                            useMenu.ts               (with filters)

4. Rate Dish           →    DishCard (👍/👎)     →  POST /api/feedback  →   feedback
                            useMenu.ts

5. Get Recommendation  →    ChatPanel            →  POST /api/chat      →   All tables
                            useChat.ts               orchestrator.py
                                                     hybrid_retriever.py
```

---

## 6. The Recommendation Flow

When a user clicks "Get Recommendation", here's exactly what happens:

### Step 1: Frontend Initiates Request
```typescript
// useChat.ts
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: '/recommend lunch' })
});
```

### Step 2: Backend Receives Request
```python
# backend/main.py - POST /api/chat
@app.post("/api/chat")
async def chat(message: ChatMessage, user_id: str):
    if message.message.startswith("/recommend"):
        # Start question flow
        return get_next_question({})
```

### Step 3: Question Agent Asks 4 Questions
```
Question 1: "What's your mood today?"
           → Options: Happy, Stressed, Tired, Grumpy, Adventurous

Question 2: "What are you craving?"
           → Options: Healthy, Comfort Food, Something Light, Protein-Rich

Question 3: "Spice preference?"
           → Options: Mild, Medium, Spicy, No Preference

Question 4: "How much time do you have?"
           → Options: Quick Bite, Normal Meal, Leisurely Dining
```

### Step 4: Orchestrator Gathers Context
```python
# backend/agents/orchestrator.py
def gather_agent_context(meal: str) -> dict:
    return {
        "mood": get_user_mood.invoke({}),           # Mood Agent
        "preferences": get_taste_preferences.invoke({}),  # Taste Agent
        "dishes": get_available_dishes.invoke({"meal_period": meal})  # Food Agent
    }
```

### Step 5: Hybrid Retriever Runs 4-Stage Pipeline

```
STAGE 1: SQL FILTERS (~5ms)
─────────────────────────
Query: SELECT * FROM dishes WHERE
       scrape_date = today AND
       meal_period = 'lunch' AND
       is_vegetarian = true  -- if user is vegetarian

Result: 245 dishes → 180 dishes (removed violations)


STAGE 2: VECTOR SEARCH (~15ms)
──────────────────────────────
1. Convert craving to embedding:
   "healthy" → [0.82, -0.15, 0.44, ...] (384 floats)

2. Cosine similarity search in pgvector:
   SELECT * FROM dish_embeddings
   ORDER BY embedding <=> query_embedding
   LIMIT 30

Result: 180 dishes → 30 candidates


STAGE 3: MULTI-FACTOR SCORING (~10ms)
─────────────────────────────────────
For each dish, compute weighted score:

score = (
    0.30 × feedback_score +      # Did user like similar dishes?
    0.25 × mood_score +          # Does it match current mood?
    0.25 × craving_score +       # Does it match craving?
    0.10 × variety_score +       # Is it different from recent picks?
    0.10 × category_bonus        # Preferred categories
)

Result: 30 candidates → 10 top-scored dishes


STAGE 4: LLM RECOMMENDATION (~800ms)
────────────────────────────────────
Prompt to Perplexity API:
- User profile (dietary restrictions)
- Current mood + food guidance
- Taste history (liked/disliked)
- Top 10 dishes with scores

LLM writes personalized 2-3 sentence recommendation
mentioning specific dishes and why they fit.

Result: Final recommendation text
```

### Step 6: Response Sent to Frontend
```json
{
  "agent_summaries": {
    "mood": {"icon": "😊", "title": "Mood", "points": ["Feeling happy", "Open to new flavors"]},
    "preferences": {"icon": "👤", "title": "Your Taste", "points": ["Likes Asian food", "Avoids heavy dishes"]},
    "availability": {"icon": "🍽️", "title": "Available", "points": ["180 dishes for lunch", "45 vegetarian options"]}
  },
  "recommendation": "Based on your happy mood and love for Asian flavors, I'd recommend the Teriyaki Chicken Bowl at Crossroads...",
  "session_id": "user_abc123"
}
```

---

## 7. File-by-File Breakdown

### Root Level

| File | Purpose | Used By |
|------|---------|---------|
| `scraper.py` | Scrapes Berkeley dining website, transforms data, generates embeddings | Cron job / manual trigger |
| `requirements.txt` | Python dependencies | pip install |

### backend/

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | FastAPI app, all API endpoints | `chat()`, `get_menu()`, `update_profile()` |
| `database.py` | Supabase client, all DB queries | `get_dishes()`, `submit_feedback()`, `get_user_profile()` |
| `models.py` | Pydantic models for validation | `UserProfile`, `Dish`, `ChatMessage`, `RecommendationResponse` |
| `food_agent.py` | Legacy LLM agent for free-form chat | `process_command()`, `set_context()` |

### backend/agents/

| File | Purpose | Key Functions |
|------|---------|---------------|
| `orchestrator.py` | Coordinates all agents, builds prompts | `get_recommendation()`, `gather_agent_context()` |
| `mood_agent.py` | Maps mood to food guidance (lookup table, no AI) | `get_user_mood()`, `MOOD_GUIDANCE` dict |
| `question_agent.py` | Manages the 4 preference questions | `get_next_question()`, `all_questions_answered()` |
| `taste_preferences_agent.py` | Analyzes user's feedback history | `get_taste_preferences()`, `get_similar_liked_dishes()` |
| `food_availability_agent.py` | Queries available dishes with filters | `get_available_dishes()`, `get_menu_summary()` |
| `hybrid_retriever.py` | 4-stage RAG pipeline | `retrieve()` - runs SQL→Vector→Score→LLM |
| `scoring.py` | Multi-factor dish ranking algorithm | `compute_dish_score()`, `DishScore` dataclass |
| `embedding_service.py` | Generates 384-dim vectors | `generate_embedding()`, `generate_batch_embeddings()` |
| `cache.py` | In-memory caching for <100ms retrieval | `get_cache()`, `set_cached_dishes()` |

### frontend/src/

| File | Purpose |
|------|---------|
| `main.tsx` | React entry point, renders App |
| `App.tsx` | Root component, sets up AppContext and layout |
| `api/client.ts` | All fetch() calls to backend |
| `context/AppContext.tsx` | Global state: profile, mood, messages, loading |
| `types/index.ts` | TypeScript interfaces matching backend models |

### frontend/src/hooks/

| File | Purpose |
|------|---------|
| `useChat.ts` | Manages chat state, sends messages, handles questions |
| `useMenu.ts` | Fetches menu, applies filters, handles feedback |
| `useProfile.ts` | Loads/saves user profile and mood |

### frontend/src/components/

| Directory | Components | Purpose |
|-----------|------------|---------|
| `chat/` | ChatPanel, ChatInput, ChatMessage, QuestionMessage, RecommendationMessage, AgentProgress, AgentSummaryCard | The recommendation UI |
| `menu/` | MenuBrowser, DishCard, DiningHallSelect, MealTabs, CategorySection | Browse and rate dishes |
| `profile/` | ProfileEditor, ProfileSummary, FeedbackStats | Set preferences, view stats |
| `layout/` | AppShell, Header | Page structure, navigation |

---

## 8. Key Design Decisions

### Why Multi-Agent Instead of One Big Prompt?

**Problem:** A single LLM prompt with all context is slow, expensive, and hard to debug.

**Solution:** Specialized agents that each do one thing:
- **Mood Agent** - Simple lookup table, no AI needed, ~1ms
- **Taste Agent** - SQL queries + statistics, no AI needed, ~10ms
- **Food Agent** - Database query with filters, no AI needed, ~5ms
- **LLM** - Only writes final recommendation, ~800ms

**Benefits:**
- 80% of work is fast, deterministic code
- Easy to test each agent in isolation
- Can change mood mappings without touching LLM
- Cheaper - LLM only called once at the end

### Why Hybrid Retrieval (SQL + Vector + Scoring)?

**Problem:** Pure vector search returns semantically similar dishes but ignores:
- Dietary restrictions (safety issue!)
- User's feedback history
- Current mood preferences

**Solution:** 4-stage pipeline:
1. **SQL filters first** - Guarantees dietary safety, fast elimination
2. **Vector search second** - Finds semantically relevant dishes
3. **Scoring third** - Ranks by multiple personalization factors
4. **LLM last** - Only sees pre-validated, highly relevant dishes

**Benefits:**
- Never recommends unsafe dishes (allergies, dietary violations)
- Combines meaning (vectors) with business logic (scores)
- LLM works with small, curated list (10 dishes, not 200)

### Why Local Embeddings Instead of OpenAI?

**Problem:** OpenAI embeddings cost $0.0001/1K tokens, adds latency, requires API key.

**Solution:** sentence-transformers running locally with `all-MiniLM-L6-v2`

**Trade-offs:**
| Factor | Local (MiniLM) | OpenAI (ada-002) |
|--------|----------------|------------------|
| Cost | Free | ~$0.10/day |
| Latency | ~10ms | ~200ms |
| Quality | Good (384-dim) | Better (1536-dim) |
| Privacy | Data stays local | Data sent to OpenAI |

For a dining app, local embeddings are sufficient quality and much faster.

### Why Supabase Instead of Firebase/MongoDB?

**Decision factors:**
1. **pgvector** - Vector search built into PostgreSQL, no separate vector DB
2. **SQL** - Complex filtering queries are natural in SQL
3. **Free tier** - 500MB storage, unlimited API calls
4. **Type safety** - PostgreSQL schemas enforce data integrity

### Why Perplexity Instead of OpenAI/Anthropic?

**Decision factors:**
1. **Grounded responses** - Less hallucination, more factual
2. **Speed** - Faster inference than GPT-4
3. **Cost** - Cheaper per token
4. **Simplicity** - OpenAI-compatible API, easy LangChain integration

---

## 9. Interview Q&A

### Architecture Questions

**Q: "Walk me through what happens when a user asks for a recommendation."**
> See Section 6 - The Recommendation Flow. Key points:
> 1. Frontend sends POST /api/chat
> 2. Question agent asks 4 preference questions
> 3. Orchestrator gathers context from mood, taste, food agents
> 4. Hybrid retriever runs 4-stage pipeline: SQL → Vector → Score → LLM
> 5. LLM writes personalized recommendation from top 10 dishes
> 6. Response includes agent summaries + recommendation text

**Q: "Why did you use multiple agents instead of one big system?"**
> Separation of concerns. Each agent does one thing well: Mood Agent handles mood logic with a simple lookup table (no AI needed), Taste Agent analyzes history with SQL queries, Food Agent filters dishes. This makes the system fast (80% is deterministic code), cheap (LLM only called once), and testable (each agent tested in isolation).

**Q: "How do you ensure the AI never recommends unsafe dishes?"**
> SQL filters run FIRST in the pipeline. Before any AI involvement, we eliminate dishes that violate dietary restrictions (vegan users never see meat, nut allergies never see tree nuts). The LLM only sees pre-validated dishes. This is a hard safety guarantee, not probabilistic.

### Technical Questions

**Q: "What is RAG and why did you use it?"**
> RAG = Retrieval Augmented Generation. Instead of letting the LLM hallucinate dishes, we RETRIEVE real dishes from our database, AUGMENT the prompt with that data, then let the AI GENERATE a response. This guarantees recommendations are for actual dishes available today.

**Q: "How do embeddings work in your system?"**
> We convert each dish name into a 384-dimensional vector using sentence-transformers (all-MiniLM-L6-v2). Similar meanings become similar vectors. When a user says "I want something healthy", we embed that text and find dishes with similar vectors using cosine similarity in pgvector. This finds "Garden Salad" even though it doesn't contain the word "healthy".

**Q: "What's the difference between your SQL search and vector search?"**
> SQL search is exact and logical: "is_vegetarian = true" finds vegetarian dishes. Vector search is semantic: "healthy" finds dishes that mean healthy even with different words. We use both: SQL for hard constraints (safety), vectors for soft preferences (meaning).

**Q: "How does your scoring algorithm work?"**
> Multi-factor weighted score:
> - 30% feedback (did user like similar dishes?)
> - 25% mood (does it match current mood guidance?)
> - 25% craving (semantic similarity to stated craving)
> - 10% variety (different from recent recommendations)
> - 10% category (preferred food categories)

### Design Questions

**Q: "Why is agents/ inside backend/ instead of at root?"**
> Cohesion. The agents are only consumed by the FastAPI backend - they're implementation details of the API, not a standalone library. Keeping them in backend/ makes it clear that all server-side code lives in one place. If agents were used by multiple consumers, separating would make sense.

**Q: "Why not microservices?"**
> For this scale, a monolith is correct. The agents share state (menu data, user context), so separating them into services adds network overhead without benefits. The system handles hundreds of users fine. If scaling to millions, I'd extract the embedding service first since it's CPU-intensive.

**Q: "How would you scale this system?"**
> 1. **Cache aggressively** - Menu doesn't change intra-day, embeddings are static
> 2. **Async everywhere** - FastAPI already async, add background tasks for scraping
> 3. **Read replicas** - Supabase supports read replicas for query scaling
> 4. **Extract embedding service** - Run on GPU instances if needed
> 5. **CDN for static** - Vite builds static assets, serve from CDN

### Code Quality Questions

**Q: "How do you test this system?"**
> - **Unit tests** (test_agents.py): Test each agent in isolation with mock data
> - **E2E tests** (test_e2e.py): Test full recommendation flow with mocked LLM
> - **Type checking**: TypeScript on frontend, Pydantic on backend
> - **Import validation**: Python imports verified at startup

**Q: "What would you improve if you had more time?"**
> 1. **Add WebSocket** for real-time menu updates
> 2. **Implement caching layer** with Redis for multi-instance deployment
> 3. **Add A/B testing** for recommendation algorithms
> 4. **Build mobile app** with React Native
> 5. **Add collaborative filtering** - "users like you also enjoyed..."

---

## Quick Reference

### API Endpoints
```
GET  /api/health        → System status
GET  /api/menu          → Filtered dishes
GET  /api/menu/summary  → Menu statistics
GET  /api/profile       → User preferences
PUT  /api/profile       → Update preferences
PUT  /api/profile/mood  → Update mood
POST /api/feedback      → Submit rating
POST /api/chat          → AI recommendation
```

### Database Tables
```
dishes           → Menu items (200+ daily)
dish_embeddings  → Vector representations
user_profiles    → Dietary preferences
user_moods       → Current mood state
feedback         → Rating history
```

### Environment Variables
```
SUPABASE_URL         → Database URL
SUPABASE_KEY         → Database API key
PERPLEXITY_API_KEY   → LLM API key
```

### Run Commands
```bash
# Backend
cd BerkeleyBites
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Scrape menu
python scraper.py

# Run tests
pytest tests/ -v
```
