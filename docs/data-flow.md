# Data Flow Diagrams (Beginner-Friendly Guide)

This document shows how data moves through the BerkeleyBites application with visual diagrams and explanations.

---

## Why Data Flow Matters

Understanding data flow helps you:
- Debug problems ("where did the data get lost?")
- Explain the system in interviews
- Know which component to modify for a feature
- Understand dependencies between parts

---

## 1. The Big Picture

Before diving into details, here's how everything connects:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER'S COMPUTER                              │
│                                                                     │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐  │
│   │   Browser   │◀───────▶│   React     │◀───────▶│ localStorage│  │
│   │  (Chrome)   │  UI     │   App       │  Cache  │  (Browser)  │  │
│   └─────────────┘         └──────┬──────┘         └─────────────┘  │
│                                  │                                  │
└──────────────────────────────────┼──────────────────────────────────┘
                                   │
                                   │ HTTP Requests (API calls)
                                   │ Port 5173 → Port 8000
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUR SERVER                                   │
│                                                                     │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐  │
│   │   FastAPI   │◀───────▶│    AI       │◀───────▶│   Cache     │  │
│   │  Endpoints  │ Coord.  │   Agents    │  Speed  │  (Memory)   │  │
│   └──────┬──────┘         └──────┬──────┘         └─────────────┘  │
│          │                       │                                  │
│          └───────────┬───────────┘                                  │
│                      │                                              │
│                      ▼                                              │
│             ┌─────────────┐                                         │
│             │  Supabase   │                                         │
│             │ (Database)  │                                         │
│             └─────────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ External APIs
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES                              │
│                                                                     │
│   ┌─────────────┐                               ┌─────────────┐     │
│   │ UC Berkeley │                               │  Perplexity │     │
│   │  Dining     │                               │    (LLM)    │     │
│   └─────────────┘                               └─────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. User Request Flow (Step by Step)

When a user clicks something, here's exactly what happens:

```
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER ACTION                                                   │
│                                                                       │
│   User clicks "Get Recommendation" button                            │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: REACT COMPONENT                                               │
│                                                                       │
│   ChatInput.tsx receives click event                                 │
│                    │                                                 │
│   onClick={() => sendMessage("/recommend")}                          │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: CONTEXT (AppContext.tsx)                                      │
│                                                                       │
│   The sendMessage function is defined in context                     │
│                    │                                                 │
│   Updates loading state: setIsLoading(true)                          │
│   Adds message to chat: setMessages([...messages, newMsg])           │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: API CLIENT (client.ts)                                        │
│                                                                       │
│   async function sendChatMessage(message, sessionId, userId) {       │
│     const response = await fetch('/api/chat?user_id=' + userId, {    │
│       method: 'POST',                                                │
│       headers: { 'Content-Type': 'application/json' },               │
│       body: JSON.stringify({ message, session_id: sessionId })       │
│     });                                                              │
│     return response.json();                                          │
│   }                                                                   │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     │ HTTP POST to localhost:8000
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 5: VITE PROXY                                                    │
│                                                                       │
│   Request to localhost:5173/api/chat                                 │
│           ↓                                                          │
│   Proxied to localhost:8000/api/chat                                 │
│                                                                       │
│   (Configured in vite.config.ts)                                     │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 6: FASTAPI BACKEND                                               │
│                                                                       │
│   @app.post("/api/chat")                                             │
│   async def chat(message: ChatMessage, user_id: str):                │
│       # Validate request with Pydantic                               │
│       # Load user profile, mood, feedback                            │
│       # Call AI agents                                               │
│       # Return response                                              │
│                    │                                                 │
│                    ▼                                                 │
└──────────────────────────────────────────────────────────────────────┘
                     │
                     │ JSON response travels back
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 7: BACK TO REACT                                                 │
│                                                                       │
│   Response received in context                                       │
│                    │                                                 │
│   setIsLoading(false)                                                │
│   setMessages([...messages, responseMsg])                            │
│                    │                                                 │
│   React re-renders ChatPanel with new message                        │
│                    │                                                 │
│                    ▼                                                 │
│   User sees the response on screen!                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Menu Data Pipeline

How we get menu data from Berkeley's website to the user:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      DAILY MENU SCRAPING                              │
│                                                                       │
│   Triggered: Manually via /api/menu/refresh or scheduled daily       │
└──────────────────────────────────────────────────────────────────────┘

  STEP 1: FETCH
  ┌─────────────────────┐
  │  UC Berkeley        │
  │  Dining Website     │
  │  dining.berkeley.edu│
  └──────────┬──────────┘
             │
             │ HTTP GET (requests library)
             ▼
  STEP 2: PARSE
  ┌─────────────────────┐
  │    scraper.py       │
  │                     │
  │  BeautifulSoup      │
  │  parses HTML:       │
  │                     │
  │  soup.find_all(     │
  │    'div',           │
  │    class_='item'    │
  │  )                  │
  └──────────┬──────────┘
             │
             │ Extracted data
             ▼
  STEP 3: TRANSFORM
  ┌─────────────────────────────────────────────────────────────────┐
  │                        DATA TRANSFORMATION                       │
  │                                                                  │
  │  Raw HTML                        Pandas DataFrame               │
  │  ┌──────────────────┐           ┌─────────────────────────────┐│
  │  │ <div class="item">│           │ dish_name  | has_milk | ... ││
  │  │   <h3>Pasta</h3>  │    ───▶   │ ─────────────────────────── ││
  │  │   <span>Wheat    │           │ Pasta      | false    | ... ││
  │  │   </span>        │           │ Soup       | true     | ... ││
  │  │ </div>           │           │                             ││
  │  └──────────────────┘           └─────────────────────────────┘│
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
             │
             │ DataFrame
             ▼
  STEP 4: STORE
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌─────────┐
│Supabase │     │  CSV    │
│ dishes  │     │ Backup  │
│ table   │     │         │
└─────────┘     └─────────┘

  STEP 5: SERVE
  ┌─────────────────────┐
  │  When user requests │
  │  /api/menu:         │
  │                     │
  │  1. Load from DB    │
  │  2. Filter by prefs │
  │  3. Return JSON     │
  └─────────────────────┘
```

---

## 4. User Session Flow

How we track users without passwords:

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SESSION MANAGEMENT                            │
└──────────────────────────────────────────────────────────────────────┘

  FIRST VISIT                              RETURN VISIT
  ───────────                              ────────────

  User opens app                           User opens app
       │                                        │
       ▼                                        ▼
  ┌─────────────────┐                    ┌─────────────────┐
  │ Check           │                    │ Check           │
  │ localStorage    │                    │ localStorage    │
  │ for user_id     │                    │ for user_id     │
  └────────┬────────┘                    └────────┬────────┘
           │                                      │
           │ Not found!                           │ Found: "user_abc123"
           ▼                                      ▼
  ┌─────────────────┐                    ┌─────────────────┐
  │ Generate new ID │                    │ Use existing ID │
  │                 │                    │                 │
  │ "user_" +       │                    │ All requests    │
  │ timestamp +     │                    │ include this ID │
  │ random string   │                    │                 │
  │                 │                    │ ?user_id=user_  │
  │ = "user_170...  │                    │ abc123          │
  │    abc123"      │                    │                 │
  └────────┬────────┘                    └────────┬────────┘
           │                                      │
           │ Store in localStorage                │
           ▼                                      ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                        DATABASE LOOKUP                           │
  │                                                                  │
  │  First visit: No data found → Create new records                │
  │  Return visit: Load existing profile, mood, feedback            │
  │                                                                  │
  │  user_profiles        user_moods           feedback              │
  │  ┌────────────┐      ┌────────────┐      ┌────────────┐         │
  │  │user_abc123 │      │user_abc123 │      │user_abc123 │         │
  │  │is_vegan:   │      │mood: happy │      │dish_42:👍  │         │
  │  │  false     │      │            │      │dish_15:👎  │         │
  │  └────────────┘      └────────────┘      └────────────┘         │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

**Why no passwords?**
- Simpler to implement
- Good enough for dining recommendations
- User data isn't sensitive
- Future improvement: Add authentication

---

## 5. Recommendation Generation Flow

The most complex flow - how AI generates recommendations:

```
┌──────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION PIPELINE                            │
│                                                                       │
│   Total time: ~800ms (most is waiting for LLM)                       │
└──────────────────────────────────────────────────────────────────────┘

  POST /api/chat { message: "/recommend" }
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 1: QUESTION FLOW (~50ms each)                                   │
│                                                                       │
│   Backend asks 4 questions, one at a time:                           │
│                                                                       │
│   Q1: "How are you feeling?"                                         │
│       → User: "😊 Happy"                                             │
│                                                                       │
│   Q2: "What are you craving?"                                        │
│       → User: "🥗 Healthy"                                           │
│                                                                       │
│   Q3: "Spice preference?"                                            │
│       → User: "🌶️ Mild"                                              │
│                                                                       │
│   Q4: "How much time?"                                               │
│       → User: "🕐 Normal"                                            │
│                                                                       │
│   Answers stored in session: { mood: happy, craving: healthy, ... }  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    │ All 4 questions answered
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CONTEXT GATHERING (~50ms)                                    │
│                                                                       │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                 set_orchestrator_context()                    │   │
│   │                                                               │   │
│   │   Load from database:                                         │   │
│   │   • menu_df = today's dishes (filtered by dietary prefs)     │   │
│   │   • feedback_df = user's past ratings                        │   │
│   │   • user_profile = dietary restrictions                      │   │
│   │   • user_mood = current mood                                 │   │
│   │                                                               │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 3: AGENT EXECUTION (~100ms total)                               │
│                                                                       │
│   All agents run to gather context:                                  │
│                                                                       │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │
│   │ Mood Agent  │   │Question Agt │   │ Taste Agent │               │
│   │ (~1ms)      │   │ (~5ms)      │   │ (~10ms)     │               │
│   │             │   │             │   │             │               │
│   │ Input:      │   │ Input:      │   │ Input:      │               │
│   │  "happy"    │   │  answers    │   │  feedback   │               │
│   │             │   │             │   │  history    │               │
│   │ Output:     │   │ Output:     │   │             │               │
│   │ "try new    │   │ "healthy,   │   │ Output:     │               │
│   │  things,    │   │  mild       │   │ "likes      │               │
│   │  fresh      │   │  spice"     │   │  Asian,     │               │
│   │  options"   │   │             │   │  Italian"   │               │
│   └─────────────┘   └─────────────┘   └─────────────┘               │
│                                                                       │
│   ┌───────────────────────────────────────────────────────┐          │
│   │              Food Availability Agent (~30ms)          │          │
│   │                                                       │          │
│   │  Input: menu_df, question answers                    │          │
│   │                                                       │          │
│   │  Output: "15 dishes match your preferences"          │          │
│   │          List of available dishes with details       │          │
│   │                                                       │          │
│   └───────────────────────────────────────────────────────┘          │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 4: HYBRID RETRIEVAL (~100ms)                                    │
│                                                                       │
│   4-stage pipeline to find best dishes:                              │
│                                                                       │
│   Stage 1: SQL Filters (~5ms)                                        │
│   ┌───────────────────────────────────────────────────┐              │
│   │ Remove dishes violating dietary restrictions      │              │
│   │ 100 dishes → 45 dishes (vegan filter applied)    │              │
│   └───────────────────────────────────────────────────┘              │
│                           │                                          │
│                           ▼                                          │
│   Stage 2: Vector Search (~15ms)                                     │
│   ┌───────────────────────────────────────────────────┐              │
│   │ Find semantically similar dishes to craving      │              │
│   │ "healthy" → dishes similar to salads, grains     │              │
│   │ 45 dishes → 30 candidates                        │              │
│   └───────────────────────────────────────────────────┘              │
│                           │                                          │
│                           ▼                                          │
│   Stage 3: Multi-factor Scoring (~10ms)                              │
│   ┌───────────────────────────────────────────────────┐              │
│   │ Score each dish:                                 │              │
│   │ • 30% taste preference (what you've liked)       │              │
│   │ • 25% craving match (healthy = high score)       │              │
│   │ • 15% mood alignment (happy = fresh foods)       │              │
│   │ • Bonuses: novelty (haven't tried yet)           │              │
│   │ • Penalties: previously disliked                 │              │
│   │                                                  │              │
│   │ 30 candidates → ranked by score                  │              │
│   └───────────────────────────────────────────────────┘              │
│                           │                                          │
│                           ▼                                          │
│   Stage 4: Take Top 8                                                │
│   ┌───────────────────────────────────────────────────┐              │
│   │ Send 8 highest-scoring dishes to LLM             │              │
│   └───────────────────────────────────────────────────┘              │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 5: LLM SYNTHESIS (~500ms)                                       │
│                                                                       │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                    Perplexity Sonar LLM                       │   │
│   │                                                               │   │
│   │   System Prompt:                                              │   │
│   │   "You are a food recommendation assistant for UC Berkeley.  │   │
│   │    Given the user's mood, cravings, preferences, and dishes, │   │
│   │    recommend 3-4 dishes with personalized explanations."     │   │
│   │                                                               │   │
│   │   Context provided:                                           │   │
│   │   • Mood analysis: "Happy, open to new things"               │   │
│   │   • Craving: "Healthy food, mild spice"                      │   │
│   │   • Taste preferences: "Likes Asian, Italian"                │   │
│   │   • Top 8 dishes with scores and details                     │   │
│   │                                                               │   │
│   │   Output:                                                     │   │
│   │   "Based on your happy mood and healthy food craving,        │   │
│   │    I recommend the **Teriyaki Chicken Bowl** from Dining     │   │
│   │    Commons! It's one of your favorite categories..."         │   │
│   │                                                               │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    │ RecommendationResponse JSON
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 6: DISPLAY TO USER                                              │
│                                                                       │
│   Response sent back to frontend:                                    │
│                                                                       │
│   {                                                                   │
│     "agent_summaries": {                                             │
│       "mood": { "icon": "😊", "title": "Mood", "points": [...] },   │
│       "prefs": { "icon": "🎯", "title": "Prefs", "points": [...] }  │
│       ...                                                            │
│     },                                                               │
│     "recommendation": "Based on your happy mood..."                  │
│   }                                                                   │
│                                                                       │
│   React renders:                                                     │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │  Agent Summary Cards                                          │   │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │   │
│   │  │ 😊 Mood │ │ 🎯 Prefs│ │ 👤 Taste│ │ 🍽️ Menu │            │   │
│   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │   │
│   │                                                              │   │
│   │  ┌────────────────────────────────────────────────────────┐ │   │
│   │  │ "Based on your happy mood and healthy food craving,    │ │   │
│   │  │  I recommend the **Teriyaki Chicken Bowl**..."         │ │   │
│   │  └────────────────────────────────────────────────────────┘ │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 6. Feedback Learning Loop

How user ratings improve future recommendations:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      FEEDBACK LEARNING LOOP                           │
└──────────────────────────────────────────────────────────────────────┘

  STEP 1: User Rates Dish
  ┌─────────────────┐
  │ User clicks 👍  │
  │ on Teriyaki     │
  │ Chicken         │
  └────────┬────────┘
           │
           │ POST /api/feedback
           │ { dish_id: 42, liked: true }
           ▼

  STEP 2: Store Feedback
  ┌─────────────────────────────────────────────────────────────────┐
  │                      Supabase: feedback table                    │
  │                                                                  │
  │   user_id    │ dish_id │ dish_name          │ liked │ date      │
  │   ───────────────────────────────────────────────────────────── │
  │   user_abc   │   42    │ Teriyaki Chicken   │ true  │ 02-03     │
  │   user_abc   │   15    │ Mystery Casserole  │ false │ 02-02     │
  │   user_abc   │   28    │ Garden Salad       │ true  │ 02-01     │
  │   user_abc   │    7    │ Miso Soup          │ true  │ 01-31     │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
           │
           │ Next time user asks for recommendation
           ▼

  STEP 3: Analyze Feedback History
  ┌─────────────────────────────────────────────────────────────────┐
  │                  Taste Preferences Agent                         │
  │                                                                  │
  │   Analyzes all past ratings:                                    │
  │                                                                  │
  │   LIKED (pattern detection):                                    │
  │   ├── Category: Asian cuisine (4 times)    ← Strong signal!    │
  │   ├── Category: Salads (3 times)                               │
  │   ├── Hall: Dining Commons (5 times)       ← Preferred location│
  │   └── Trait: Light meals (3 times)                             │
  │                                                                  │
  │   DISLIKED (avoid these):                                       │
  │   ├── Category: Mystery items (2 times)    ← Red flag!         │
  │   └── Trait: Heavy/greasy (2 times)                            │
  │                                                                  │
  │   Generated insight:                                            │
  │   "User prefers Asian cuisine and salads from Dining Commons.  │
  │    Avoid mystery items and heavy dishes."                       │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
           │
           │ Insights feed into scoring
           ▼

  STEP 4: Better Recommendations
  ┌─────────────────────────────────────────────────────────────────┐
  │                    Scoring Algorithm                             │
  │                                                                  │
  │   For each candidate dish:                                      │
  │                                                                  │
  │   Kung Pao Tofu (Asian, Dining Commons):                       │
  │   ├── Taste preference score: +0.30 (likes Asian!)             │
  │   ├── Location preference: +0.10 (likes this hall)             │
  │   ├── Novelty bonus: +0.05 (hasn't tried yet)                  │
  │   └── Total: 0.45 ← HIGH SCORE, will recommend!                │
  │                                                                  │
  │   Mystery Meatloaf (Unknown, Crossroads):                       │
  │   ├── Taste preference score: -0.20 (dislikes mystery)         │
  │   ├── Location preference: 0.00 (neutral)                      │
  │   └── Total: -0.20 ← LOW SCORE, won't recommend                │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
           │
           ▼

  STEP 5: Personalized Output
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │   "I noticed you've been enjoying Asian dishes lately!          │
  │    The new Kung Pao Tofu at Dining Commons looks perfect        │
  │    for you today. It's similar to the Teriyaki Chicken          │
  │    you liked yesterday!"                                         │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 7. State Synchronization

How data stays consistent across browser, memory, and database:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      THREE LAYERS OF STATE                            │
└──────────────────────────────────────────────────────────────────────┘

     BROWSER (Client)                         SERVER
┌──────────────────────────────┐    ┌────────────────────────────────┐
│                              │    │                                │
│  localStorage    React State │    │  In-Memory       Supabase      │
│  ┌──────────┐   ┌──────────┐│    │  ┌──────────┐   ┌──────────┐  │
│  │ user_id  │   │ profile  ││    │  │ _cache   │   │ user_    │  │
│  │ profile  │◀─▶│ mood     ││◀──▶│  │ (quick   │◀─▶│ profiles │  │
│  │ (cached) │   │ messages ││    │  │  lookup) │   │ feedback │  │
│  └──────────┘   │ loading  ││    │  └──────────┘   │ dishes   │  │
│      │          └──────────┘│    │                  └──────────┘  │
│      │               │      │    │                       │        │
│      │               │      │    │                       │        │
└──────┼───────────────┼──────┘    └───────────────────────┼────────┘
       │               │                                    │
       └───────────────┼────────────────────────────────────┘
                       │
                    SYNC EVENTS

  ┌─────────────────────────────────────────────────────────────────┐
  │ 1. APP LOAD                                                      │
  │                                                                  │
  │    a) Read localStorage → Show cached data immediately (fast!)  │
  │    b) Fetch from Supabase → Update with fresh data             │
  │    c) Update localStorage → Keep cache fresh                    │
  │                                                                  │
  │    Why? User sees something instantly, then gets accurate data  │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ 2. PROFILE UPDATE (user changes dietary preferences)            │
  │                                                                  │
  │    a) Update React state → UI updates immediately               │
  │    b) Send to Supabase → Persist permanently                    │
  │    c) Update localStorage → Keep cache in sync                  │
  │                                                                  │
  │    Why? User sees change instantly, data is safe in database    │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ 3. RECOMMENDATION REQUEST                                        │
  │                                                                  │
  │    a) Check in-memory cache → Return if fresh (<5min old)       │
  │    b) If stale, fetch from Supabase                             │
  │    c) Process with agents                                        │
  │    d) Update cache                                               │
  │                                                                  │
  │    Why? Fast responses for repeated requests                    │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 8. Error Handling Flow

What happens when things go wrong:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING CHAIN                             │
│                                                                       │
│   Errors are caught at multiple layers, each with fallback behavior  │
└──────────────────────────────────────────────────────────────────────┘

  Request arrives
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ LAYER 1: Frontend Validation                                     │
  │                                                                  │
  │   Before sending request, check basics:                         │
  │                                                                  │
  │   if (!userId) {                                                │
  │     showError("Please refresh the page");                       │
  │     return;  // Don't even send request                         │
  │   }                                                              │
  │                                                                  │
  │   Result: Bad requests never leave the browser                  │
  └─────────────────────────────────────────────────────────────────┘
       │
       │ Valid request sent
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ LAYER 2: Network / API Client                                    │
  │                                                                  │
  │   try {                                                         │
  │     const response = await fetch('/api/...');                   │
  │     if (!response.ok) {                                         │
  │       throw new Error(`HTTP ${response.status}`);               │
  │     }                                                           │
  │     return response.json();                                     │
  │   } catch (error) {                                             │
  │     setError("Network error. Please try again.");               │
  │   }                                                              │
  │                                                                  │
  │   Result: Network failures show friendly message                │
  └─────────────────────────────────────────────────────────────────┘
       │
       │ Request reaches server
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ LAYER 3: Pydantic Validation                                     │
  │                                                                  │
  │   FastAPI + Pydantic automatically validate:                    │
  │                                                                  │
  │   class ChatMessage(BaseModel):                                 │
  │       message: str  # Must be string                            │
  │       session_id: str  # Must be string                         │
  │                                                                  │
  │   If validation fails → 422 Unprocessable Entity                │
  │                                                                  │
  │   Result: Invalid data rejected before hitting our code         │
  └─────────────────────────────────────────────────────────────────┘
       │
       │ Valid data
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ LAYER 4: Business Logic                                          │
  │                                                                  │
  │   Our code checks business rules:                               │
  │                                                                  │
  │   if not menu_loaded:                                           │
  │       raise HTTPException(503, "Menu not available yet")        │
  │                                                                  │
  │   if dish_id not in available_dishes:                           │
  │       raise HTTPException(404, "Dish not found")                │
  │                                                                  │
  │   Result: Clear error messages for business logic failures      │
  └─────────────────────────────────────────────────────────────────┘
       │
       │ Calling external services
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ LAYER 5: External Services (Graceful Degradation)                │
  │                                                                  │
  │   Database fails? Use CSV backup:                               │
  │   ┌──────────────────────────────────────────────────────────┐  │
  │   │ try:                                                      │  │
  │   │     data = supabase.query()                               │  │
  │   │ except Exception as e:                                    │  │
  │   │     logger.error(f"Database failed: {e}")                 │  │
  │   │     data = pd.read_csv("dining_data_clean.csv")           │  │
  │   └──────────────────────────────────────────────────────────┘  │
  │                                                                  │
  │   LLM API fails? Use simple fallback:                           │
  │   ┌──────────────────────────────────────────────────────────┐  │
  │   │ try:                                                      │  │
  │   │     response = llm.generate(prompt)                       │  │
  │   │ except Exception:                                         │  │
  │   │     response = "Here are top dishes based on your prefs"  │  │
  │   └──────────────────────────────────────────────────────────┘  │
  │                                                                  │
  │   Result: App keeps working even when services are down         │
  └─────────────────────────────────────────────────────────────────┘
       │
       ▼
  Success! Response sent to user
```

---

## 9. Component Communication (React)

How React components talk to each other:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      REACT COMPONENT TREE                             │
│                                                                       │
│   Data flows DOWN through props                                      │
│   Actions flow UP through callbacks                                   │
│   Shared state lives in Context                                       │
└──────────────────────────────────────────────────────────────────────┘

  App.tsx
     │
     └── AppProvider (Context)  ← Holds all shared state
            │
            └── AppShell
                   │
       ┌───────────┼───────────┬───────────────┐
       │           │           │               │
       ▼           ▼           ▼               ▼
   Header      ChatPanel   MenuBrowser    ProfilePanel


  ┌─────────────────────────────────────────────────────────────────┐
  │ HEADER                                                           │
  │                                                                  │
  │   reads from context:                                           │
  │   • mood (to show current mood)                                 │
  │   • profile (to show dietary preferences)                       │
  │                                                                  │
  │   calls context methods:                                        │
  │   • setMood() when user clicks mood selector                    │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ CHAT PANEL                                                       │
  │                                                                  │
  │   reads from context:                                           │
  │   • chatMessages (array of messages)                            │
  │   • isLoading (show spinner?)                                   │
  │                                                                  │
  │   children:                                                     │
  │   ├── ChatMessage (×n)                                          │
  │   │     props: message content, onAnswer callback               │
  │   │                                                             │
  │   ├── AgentProgress                                             │
  │   │     props: steps, isActive                                  │
  │   │                                                             │
  │   └── ChatInput                                                 │
  │         props: onSend callback                                  │
  │         calls: sendMessage() in context                         │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ MENU BROWSER                                                     │
  │                                                                  │
  │   reads from context:                                           │
  │   • menuSummary (halls, meals, categories)                      │
  │   • selectedHall, selectedMeal                                  │
  │                                                                  │
  │   children:                                                     │
  │   ├── DiningHallSelect                                          │
  │   │     calls: setSelectedHall()                                │
  │   │                                                             │
  │   ├── MealTabs                                                  │
  │   │     calls: setSelectedMeal()                                │
  │   │                                                             │
  │   └── CategorySection (×n)                                      │
  │         └── DishCard (×n)                                       │
  │               calls: submitFeedback(dishId, liked)              │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘


  DATA FLOW VISUALIZATION:
  ────────────────────────

  Context (AppProvider)
       │
       │ provides values via useApp() hook
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
   Components READ                      Components WRITE
   ─────────────                        ──────────────
   profile                              setProfile()
   mood                                 setMood()
   chatMessages                         sendMessage()
   isLoading                            submitFeedback()
   menuSummary                          setSelectedHall()
                                        setSelectedMeal()
```

---

## Summary: Key Data Flows

| Flow | Start | End | Key Steps |
|------|-------|-----|-----------|
| **User Request** | Button click | Response displayed | Component → Context → API Client → Backend → Database |
| **Menu Pipeline** | Berkeley website | User's screen | Scrape → Parse → Store → Filter → Display |
| **Recommendation** | "/recommend" | AI response | Questions → Agents → Hybrid Retrieval → LLM |
| **Feedback Loop** | 👍/👎 click | Better recs | Store → Analyze patterns → Adjust scores |
| **State Sync** | User action | All layers updated | React → Supabase → localStorage |

**Key Insight:** Data flows through well-defined paths. Understanding these paths helps you:
- Debug issues ("where did it break?")
- Add features ("where do I plug this in?")
- Explain the system in interviews
