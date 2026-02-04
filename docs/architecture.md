# System Architecture (Beginner-Friendly)

This document explains how all the pieces of BerkeleyBites fit together, assuming no prior knowledge.

---

## What is "Architecture"?

Software architecture is like a building's blueprint. It shows:
- What parts exist
- How they connect
- Why we made certain choices

---

## The Three Main Layers

Every web application has these layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    LAYER 1: PRESENTATION (Frontend)                                         │
│    ─────────────────────────────────                                        │
│    What the user sees and interacts with                                    │
│                                                                             │
│    Technology: React + TypeScript + Tailwind CSS                            │
│    Location: /frontend/src/                                                 │
│    Port: 5173                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │  HTTP Requests (JSON)
                                    │  "GET /api/menu"
                                    │  "POST /api/feedback"
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    LAYER 2: BUSINESS LOGIC (Backend)                                        │
│    ────────────────────────────────                                         │
│    Processes requests, runs AI, enforces rules                              │
│                                                                             │
│    Technology: Python + FastAPI + LangChain                                 │
│    Location: /backend/ and /agents/                                         │
│    Port: 8000                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │  Database Queries (SQL)
                                    │  "SELECT * FROM dishes"
                                    │  "INSERT INTO feedback"
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    LAYER 3: DATA (Database)                                                 │
│    ────────────────────────                                                 │
│    Stores data permanently                                                  │
│                                                                             │
│    Technology: Supabase (PostgreSQL)                                        │
│    Location: Cloud (or local via supabase start)                           │
│    Port: 54321 (local)                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why These Three Layers?

### Separation of Concerns

Each layer has ONE job:

| Layer | Job | Example |
|-------|-----|---------|
| Frontend | Display things beautifully | Show a dish card with an image |
| Backend | Make decisions | "Is this user allowed to see this dish?" |
| Database | Remember things | Store that the user liked this dish |

### Benefits

1. **Easier to Change**: Want a new design? Change only the frontend.
2. **Easier to Test**: Test each layer independently.
3. **Easier to Scale**: Add more servers for the layer that's slow.
4. **Easier to Understand**: Each file has a clear purpose.

---

## Detailed Component Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                                   │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                         App.tsx                                    │    │
│   │                    (Main Application)                              │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                  │                                          │
│          ┌───────────────────────┼───────────────────────┐                 │
│          │                       │                       │                 │
│          ▼                       ▼                       ▼                 │
│   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐           │
│   │  ChatPanel  │        │ MenuBrowser │        │ProfileEditor│           │
│   │             │        │             │        │             │           │
│   │ AI chat     │        │ Browse food │        │ Set dietary │           │
│   │ interface   │        │ by hall/meal│        │ preferences │           │
│   └─────────────┘        └─────────────┘        └─────────────┘           │
│          │                       │                       │                 │
│          └───────────────────────┼───────────────────────┘                 │
│                                  │                                          │
│                                  ▼                                          │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                       AppContext.tsx                               │    │
│   │              (Shared State: profile, mood, menu)                   │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                  │                                          │
│                                  ▼                                          │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                        api/client.ts                               │    │
│   │               (Makes HTTP requests to backend)                     │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ fetch("/api/...")
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                         main.py                                    │    │
│   │                    (API Endpoints)                                 │    │
│   │                                                                    │    │
│   │   /api/menu      - Get dishes                                     │    │
│   │   /api/profile   - User preferences                               │    │
│   │   /api/feedback  - Like/dislike dishes                            │    │
│   │   /api/chat      - AI recommendations                             │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                    │                           │                            │
│                    ▼                           ▼                            │
│   ┌───────────────────────────┐    ┌────────────────────────────────┐     │
│   │       models.py           │    │    AI AGENTS (/agents/)        │     │
│   │                           │    │                                │     │
│   │  Data definitions:        │    │  orchestrator.py (coordinator) │     │
│   │  - Dish                   │    │  question_agent.py             │     │
│   │  - UserProfile            │    │  taste_preferences_agent.py    │     │
│   │  - ChatMessage            │    │  food_availability_agent.py    │     │
│   │  - etc.                   │    │  hybrid_retriever.py (engine)  │     │
│   └───────────────────────────┘    │  scoring.py (mood weights)     │     │
│                                    │  embedding_service.py          │     │
│                                    │  cache.py                      │     │
│                                    └────────────────────────────────┘     │
│                                                 │                          │
│                                                 ▼                          │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                       database.py                                  │    │
│   │               (Connects to Supabase/PostgreSQL)                    │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ SQL queries
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE (Supabase/PostgreSQL)                       │
│                                                                             │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│   │     dishes      │  │    feedback     │  │  user_profiles  │           │
│   │─────────────────│  │─────────────────│  │─────────────────│           │
│   │ id              │  │ id              │  │ id              │           │
│   │ dish_name       │  │ user_id         │  │ user_id         │           │
│   │ dining_hall     │  │ dish_id         │  │ is_vegetarian   │           │
│   │ meal_period     │  │ liked           │  │ is_vegan        │           │
│   │ is_vegetarian   │  │ created_at      │  │ avoid_nuts      │           │
│   │ has_nuts        │  │                 │  │ ...             │           │
│   │ ...             │  │                 │  │                 │           │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                             │
│   ┌─────────────────┐  ┌─────────────────┐                                │
│   │   user_moods    │  │ dish_embeddings │                                │
│   │─────────────────│  │─────────────────│                                │
│   │ user_id         │  │ dish_id         │                                │
│   │ mood            │  │ embedding       │  ← Vector (384 numbers)        │
│   │ updated_at      │  │ created_at      │                                │
│   └─────────────────┘  └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The AI Agent System

The most unique part of BerkeleyBites is the multi-agent AI system. Here's how it works:

### Why Multiple Agents?

**Problem**: One big AI prompt can't:
- Query databases efficiently
- Be tested in isolation
- Handle failures gracefully
- Process user preferences systematically

**Solution**: Specialized agents that each do one thing well.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE ORCHESTRATOR                                     │
│                      (agents/orchestrator.py)                               │
│                                                                             │
│   The "conductor" that coordinates all agents                               │
│                                                                             │
│   1. Sets up context (user profile, menu, feedback)                        │
│   2. Calls each agent                                                       │
│   3. Combines their outputs                                                 │
│   4. Sends to AI for final recommendation                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│    MOOD AGENT     │   │  QUESTION AGENT   │   │    TASTE AGENT    │
│                   │   │                   │   │                   │
│ Input: user mood  │   │ Input: user       │   │ Input: feedback   │
│                   │   │        answers    │   │        history    │
│ Output: food      │   │                   │   │                   │
│         guidance  │   │ Output: craving,  │   │ Output: preferred │
│                   │   │ spice, time prefs │   │         categories│
│ "Stressed? Try    │   │                   │   │ "User likes Asian │
│  comfort food"    │   │ "Wants healthy,   │   │  food, dislikes   │
│                   │   │  mild spice"      │   │  heavy dishes"    │
└───────────────────┘   └───────────────────┘   └───────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HYBRID RETRIEVER                                     │
│                    (agents/hybrid_retriever.py)                             │
│                                                                             │
│   A 4-stage pipeline to find the best dishes:                              │
│                                                                             │
│   Stage 1: SQL FILTERS (~5ms)                                              │
│   ─────────────────────────────                                            │
│   Remove dishes that violate dietary restrictions                          │
│   "User is vegan → remove all meat dishes"                                 │
│                                                                             │
│   Stage 2: VECTOR SEARCH (~15ms)                                           │
│   ─────────────────────────────                                            │
│   Find semantically similar dishes                                         │
│   "User wants 'comfort food' → find warm, hearty dishes"                   │
│                                                                             │
│   Stage 3: MULTI-FACTOR SCORING (~10ms)                                    │
│   ─────────────────────────────────────                                    │
│   Score each dish on multiple factors:                                     │
│   - Taste preference (30%): Based on past likes                            │
│   - Craving match (25%): Does it match what they want?                     │
│   - Mood alignment (15%): Good for their current mood?                     │
│   - Category preference (10%): From a liked category?                      │
│   - Spice preference (10%): Matches spice tolerance?                       │
│   - Novelty bonus (+5%): Haven't tried it before?                          │
│   - Dislike penalty (-30%): Previously disliked?                           │
│                                                                             │
│   Stage 4: LLM REFINEMENT (~500ms)                                         │
│   ─────────────────────────────────                                        │
│   AI picks final recommendations and writes explanation                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: From Click to Recommendation

Let's trace what happens when a user clicks "Get Recommendation":

```
STEP 1: USER CLICKS BUTTON
──────────────────────────────────────────────────────────────────────────────

User clicks "Get Recommendation" in the ChatPanel component

    ChatPanel.tsx
    └── onClick={() => sendMessage('/recommend')}


STEP 2: FRONTEND MAKES API CALL
──────────────────────────────────────────────────────────────────────────────

The API client sends a POST request to the backend

    api/client.ts
    └── fetch('/api/chat', {
          method: 'POST',
          body: JSON.stringify({
            message: '/recommend',
            session_id: 'user_123'
          })
        })


STEP 3: BACKEND RECEIVES REQUEST
──────────────────────────────────────────────────────────────────────────────

FastAPI routes the request to the chat handler

    backend/main.py
    └── @app.post("/api/chat")
        async def chat(message: ChatMessage):
            # Process the message...


STEP 4: QUESTION PHASE
──────────────────────────────────────────────────────────────────────────────

Backend asks clarifying questions (one at a time):

    Question 1: "How are you feeling?"
                User answers: "😊 Happy"

    Question 2: "What kind of food sounds good?"
                User answers: "🥗 Healthy"

    Question 3: "How spicy?"
                User answers: "🌶️ Mild"

    Question 4: "How much time do you have?"
                User answers: "🕐 Normal"


STEP 5: AGENT ORCHESTRATION
──────────────────────────────────────────────────────────────────────────────

Orchestrator gathers context from all agents:

    agents/orchestrator.py
    │
    ├── Mood Agent: "User is happy → adventurous foods OK"
    │
    ├── Question Agent: "Wants healthy food, mild spice, normal time"
    │
    ├── Taste Agent: "User likes Asian, Italian. Dislikes heavy foods."
    │
    └── Food Agent: "245 dishes available. 45 vegetarian. 12 match filters."


STEP 6: HYBRID RETRIEVAL
──────────────────────────────────────────────────────────────────────────────

The retriever finds the best matches:

    agents/hybrid_retriever.py
    │
    ├── Stage 1: 245 dishes → 180 (removed dietary violations)
    │
    ├── Stage 2: 180 dishes → 30 (vector search for "healthy")
    │
    ├── Stage 3: Score each dish:
    │            Teriyaki Chicken Bowl: 0.87
    │            Garden Salad: 0.82
    │            Pasta Primavera: 0.79
    │            ...
    │
    └── Stage 4: AI picks top 3 and explains why


STEP 7: RESPONSE TO FRONTEND
──────────────────────────────────────────────────────────────────────────────

Backend sends structured response:

    {
      "agent_summaries": {
        "mood": {
          "icon": "😊",
          "title": "Mood Analysis",
          "points": ["You're feeling happy!", "Great time to try new things"]
        },
        "preferences": {
          "icon": "🎯",
          "title": "Your Preferences",
          "points": ["Looking for healthy options", "Mild spice preferred"]
        },
        ...
      },
      "recommendation": "Based on your happy mood and preference for healthy
                        food, I recommend the **Teriyaki Chicken Bowl** from
                        Dining Commons! It's fresh, healthy, and matches
                        your preference for Asian cuisines."
    }


STEP 8: FRONTEND DISPLAYS RESULT
──────────────────────────────────────────────────────────────────────────────

React components render the recommendation:

    ChatPanel.tsx
    ├── AgentSummaryCard (mood)
    ├── AgentSummaryCard (preferences)
    ├── AgentSummaryCard (taste)
    └── RecommendationMessage (the actual suggestion)
```

---

## Why We Made These Design Choices

### 1. React for Frontend

**Choice**: React instead of plain HTML/JavaScript

**Why**:
- **Components**: Build UI from reusable pieces
- **State Management**: UI automatically updates when data changes
- **Large Ecosystem**: Lots of libraries and community support
- **Industry Standard**: Most jobs use React

**Trade-off**: Steeper learning curve than plain HTML

### 2. FastAPI for Backend

**Choice**: FastAPI instead of Flask or Django

**Why**:
- **Fast**: One of the fastest Python frameworks
- **Type Safety**: Catches bugs before runtime
- **Auto Documentation**: `/docs` endpoint for free
- **Async Support**: Handle many requests simultaneously
- **Modern**: Uses latest Python features

**Trade-off**: Smaller community than Django

### 3. Supabase for Database

**Choice**: Supabase instead of raw PostgreSQL or Firebase

**Why**:
- **Managed**: They handle backups, scaling, security
- **PostgreSQL**: Industry-standard, powerful SQL
- **Easy Setup**: `supabase start` for local development
- **Extra Features**: Auth, real-time, storage included
- **Free Tier**: Great for development

**Trade-off**: Vendor dependency

### 4. Multi-Agent Architecture

**Choice**: Multiple specialized agents instead of one big AI prompt

**Why**:
- **Reliability**: If one agent fails, others still work
- **Testability**: Test each agent independently
- **Modularity**: Add new agents without changing others
- **Performance**: Deterministic parts don't need expensive AI calls

**Trade-off**: More complex code structure

### 5. Hybrid Retrieval (RAG)

**Choice**: 4-stage retrieval instead of just asking AI

**Why**:
- **Speed**: Database filtering is 1000x faster than AI
- **Accuracy**: AI can't make up dishes that don't exist
- **Cost**: Less AI API calls = lower costs
- **Control**: Deterministic scoring is predictable

**Trade-off**: More engineering complexity

### 6. Caching Layer

**Choice**: Multi-layer caching with different TTLs

**Why**:
- **Speed**: Sub-100ms response times
- **Cost**: Fewer database queries and API calls
- **User Experience**: Instant-feeling application

**Cache TTLs**:
| Data | TTL | Why |
|------|-----|-----|
| Menu | 24 hours | Changes daily |
| User Feedback | 2 minutes | May be updated |
| Embeddings | 24 hours | Don't change |

**Trade-off**: Stale data possible

---

## Potential Improvements

### 1. Authentication
**Current**: Anonymous sessions via localStorage
**Improvement**: Add user accounts with login
**Why Not Yet**: Adds complexity, not needed for MVP

### 2. Real-time Updates
**Current**: Manual refresh for new data
**Improvement**: WebSockets for instant updates
**Why Not Yet**: Supabase supports this, but adds complexity

### 3. Better Caching
**Current**: In-memory Python dictionaries
**Improvement**: Redis for distributed caching
**Why Not Yet**: Single server is sufficient for now

### 4. Monitoring
**Current**: Basic logging
**Improvement**: Prometheus metrics, Grafana dashboards
**Why Not Yet**: Over-engineering for development stage

### 5. Testing
**Current**: Manual testing
**Improvement**: Unit tests, integration tests, E2E tests
**Why Not Yet**: Would be important for production

---

## Summary

BerkeleyBites follows a modern, scalable architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   FRONTEND          BACKEND             AI AGENTS         DATABASE     │
│   (React)           (FastAPI)           (LangChain)       (Supabase)   │
│                                                                         │
│   What users        Processes           Makes smart       Stores data  │
│   see and           requests and        recommendations   permanently  │
│   interact with     enforces rules                                     │
│                                                                         │
│   Components:       Endpoints:          Agents:           Tables:      │
│   - ChatPanel       - /api/menu         - Mood            - dishes     │
│   - MenuBrowser     - /api/profile      - Question        - feedback   │
│   - ProfileEditor   - /api/chat         - Taste           - profiles   │
│   - DishCard        - /api/feedback     - Orchestrator    - moods      │
│                                         - Retriever                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Takeaways**:
1. **Separation of concerns**: Each layer does one thing well
2. **Multi-agent AI**: Specialized agents > one big prompt
3. **Hybrid retrieval**: Database + vectors + AI = fast & accurate
4. **Caching**: Speed is a feature
5. **Modern stack**: React, FastAPI, PostgreSQL are industry standards
