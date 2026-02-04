# Interview Preparation Guide

This document prepares you for technical interviews about BerkeleyBites. It includes explanations of key concepts, common questions, and how to answer them.

---

## Your Elevator Pitch (30 seconds)

Practice saying this out loud:

> "BerkeleyBites is a full-stack AI-powered food recommendation system for UC Berkeley dining halls. Users answer a few questions about their mood and cravings, and the app recommends dishes based on their dietary restrictions, preferences, and what they've liked before.
>
> The frontend is built with React and TypeScript, the backend uses Python with FastAPI, and we store data in Supabase which is PostgreSQL. The AI system uses a multi-agent architecture where specialized agents handle mood, questions, and taste preferences, then a hybrid retrieval system ranks dishes using a weighted scoring algorithm before an LLM writes the final recommendation."

---

## Core Concepts You Must Understand

### 1. What is Full-Stack Development?

**Full-stack** means building both the frontend (what users see) and backend (the server logic).

```
FULL STACK = Frontend + Backend + Database

Frontend: React, TypeScript, Tailwind CSS
         ↓ API calls (HTTP)
Backend:  Python, FastAPI, AI Agents
         ↓ SQL queries
Database: PostgreSQL (via Supabase)
```

### 2. What is an API?

**API** = Application Programming Interface

It's how programs talk to each other. Like a waiter in a restaurant:
- Customer (frontend) tells waiter (API) what they want
- Waiter goes to kitchen (backend) to get it
- Waiter brings food back to customer

```
Frontend                     Backend
   │                            │
   │──── GET /api/menu ────────►│
   │                            │ (Looks up menu in database)
   │◄─── [list of dishes] ──────│
   │                            │
```

### 3. What is REST?

**REST** = Representational State Transfer

A set of conventions for designing APIs:

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Read data | Get the menu |
| POST | Create data | Submit a new rating |
| PUT | Update data | Change profile settings |
| DELETE | Remove data | Delete an account |

### 4. What is RAG?

**RAG** = Retrieval Augmented Generation

Instead of asking AI "what should I eat?" (which might hallucinate):
1. **Retrieve** actual dishes from the database
2. **Augment** the AI prompt with real data
3. **Generate** a recommendation from real options

### 5. What are Embeddings?

Text converted to numbers that capture meaning:

```
"Chicken Soup" → [0.23, -0.15, 0.87, ...]  (384 numbers)
"Chicken Broth" → [0.21, -0.18, 0.85, ...]  (similar numbers!)
"Ice Cream" → [-0.45, 0.72, -0.33, ...]     (very different numbers)
```

Similar text = similar numbers = similar meaning

---

## The Tech Stack (Know This Cold)

### Frontend Technologies

| Technology | What It Is | Why We Use It |
|------------|------------|---------------|
| **React** | UI library | Build reusable components, automatic UI updates |
| **TypeScript** | JavaScript + types | Catch bugs at compile time |
| **Tailwind CSS** | Utility CSS framework | Fast styling, consistent design |
| **Vite** | Build tool | Fast dev server, hot reload |

### Backend Technologies

| Technology | What It Is | Why We Use It |
|------------|------------|---------------|
| **Python** | Programming language | Great for AI/ML, data processing |
| **FastAPI** | Web framework | Fast, automatic docs, type hints |
| **Pydantic** | Data validation | Validates request/response data |
| **LangChain** | AI framework | Easy to build AI agents |
| **Perplexity** | LLM provider | Cost-effective AI model |

### Database Technologies

| Technology | What It Is | Why We Use It |
|------------|------------|---------------|
| **Supabase** | Database service | Managed PostgreSQL, easy setup |
| **PostgreSQL** | Relational database | Industry standard, powerful SQL |
| **pgvector** | Vector extension | Stores embeddings for semantic search |

---

## Project Structure (File by File)

### Frontend Files

| File | What It Does |
|------|--------------|
| `App.tsx` | Main component, renders entire app |
| `api/client.ts` | Functions that call the backend API |
| `context/AppContext.tsx` | Shared state (profile, mood, menu) |
| `components/chat/ChatPanel.tsx` | The AI chat interface |
| `components/menu/DishCard.tsx` | Displays one dish with ratings |
| `components/profile/ProfileEditor.tsx` | Edit dietary preferences |

### Backend Files

| File | What It Does |
|------|--------------|
| `main.py` | All API endpoints (`/api/menu`, `/api/chat`, etc.) |
| `models.py` | Data structures (Dish, UserProfile, etc.) |
| `database.py` | Connects to Supabase, runs queries |

### Agent Files

| File | What It Does |
|------|--------------|
| `orchestrator.py` | Coordinates all agents, generates recommendations |
| `mood_agent.py` | Maps mood → food suggestions |
| `question_agent.py` | Manages the 4-question preference flow |
| `food_availability_agent.py` | Queries available dishes |
| `taste_preferences_agent.py` | Analyzes user's like/dislike history |
| `question_agent.py` | Manages the 4-question flow |
| `hybrid_retriever.py` | 4-stage pipeline to find best dishes |
| `scoring.py` | Multi-factor scoring algorithm |
| `embedding_service.py` | Converts text to vectors |
| `cache.py` | Speeds up repeated requests |

---

## Common Interview Questions

### Architecture Questions

#### Q: "Why did you separate frontend and backend?"

> "Separation of concerns. Each part has a clear responsibility:
> - Frontend handles presentation (what users see)
> - Backend handles logic (business rules, AI)
> - Database handles persistence (storing data)
>
> This makes the code easier to maintain, test, and scale. Different developers can work on each part without conflicts. We can also change one part without breaking others."

#### Q: "Why use multiple AI agents instead of one big prompt?"

> "A single prompt can't do everything well:
> 1. It can't query our database for today's menu
> 2. It can't analyze user feedback history
> 3. It can't manage multi-step question flows
> 4. If something fails, everything fails
>
> By using specialized agents, each one does one thing well. The mood agent just maps emotions to food guidance - no AI needed, just a simple lookup. The question agent manages the preference gathering flow. Only the final recommendation actually needs the LLM.
>
> Benefits: easier to test, cheaper (less AI calls), more reliable (one failure doesn't break everything)."

#### Q: "What is your hybrid retrieval system?"

> "It's a 4-stage pipeline that finds the best dishes:
>
> **Stage 1: SQL Filters (~5ms)** - Remove dishes that violate dietary restrictions. If someone is vegan, we filter out non-vegan dishes immediately.
>
> **Stage 2: Vector Search (~15ms)** - Use embeddings to find semantically similar dishes. If someone wants 'comfort food', we find dishes like soups and pasta that are semantically similar.
>
> **Stage 3: Multi-factor Scoring (~10ms)** - Score each dish on multiple factors:
> - 30% taste preference (what they've liked before)
> - 25% craving match (does it match what they want?)
> - 15% mood alignment (good for their emotional state?)
> - 10% category preference, 10% spice preference
> - Plus bonuses for novelty, penalties for previously disliked items
>
> **Stage 4: LLM Refinement (~500ms)** - Send the top 8 scored dishes to the AI, which picks 3-4 and writes a personalized explanation.
>
> This is much better than just asking an AI 'what should I eat?' because the AI can only choose from real dishes, and most of the work is deterministic and fast."

#### Q: "Why FastAPI instead of Flask or Django?"

> "FastAPI offers:
> - **Speed**: One of the fastest Python frameworks
> - **Type hints**: Catches bugs before runtime
> - **Auto documentation**: Free Swagger UI at `/docs`
> - **Async support**: Handle many concurrent requests
> - **Pydantic integration**: Automatic request/response validation
>
> Flask would work but needs more setup. Django is overkill for an API-only backend."

#### Q: "Why Supabase instead of just PostgreSQL?"

> "Supabase provides:
> - **Managed hosting**: No server administration
> - **Local development**: `supabase start` for testing
> - **Built-in features**: Auth, real-time, storage
> - **PostgreSQL underneath**: Standard SQL, no vendor lock-in
> - **Free tier**: Great for development
>
> Raw PostgreSQL would require setting up servers, backups, security ourselves."

---

### Frontend Questions

#### Q: "Why React instead of Vue or Angular?"

> "React is:
> - Most popular (lots of jobs, big community)
> - Flexible (just a library, not a full framework)
> - Well-documented with lots of learning resources
> - Used by major companies (Facebook, Netflix, Airbnb)
>
> Vue is also good but smaller community. Angular is more opinionated and has a steeper learning curve."

#### Q: "Why TypeScript instead of JavaScript?"

> "TypeScript catches bugs at compile time instead of runtime:
> ```typescript
> function greet(name: string): string {
>   return name.toUppercase();  // ERROR: toUppercase doesn't exist
> }
> ```
>
> Also provides better IDE support (autocomplete, refactoring) and serves as documentation (you can see what types functions expect)."

#### Q: "How do you manage state?"

> "Three layers:
> 1. **localStorage**: Persists user ID and cached preferences across browser sessions
> 2. **React Context**: Shared state across components (profile, mood, chat messages)
> 3. **Supabase**: Source of truth for all data
>
> On load, we read from localStorage for instant display, then fetch from backend to sync. Updates go to all three layers."

#### Q: "Why not use Redux?"

> "BerkeleyBites has about 10 pieces of global state. React Context is simpler and sufficient for this scale. Redux adds boilerplate that's only justified for large, complex applications with hundreds of state pieces and complex state transitions."

---

### Backend Questions

#### Q: "How do API endpoints work?"

> "FastAPI uses decorators to define endpoints:
> ```python
> @app.get('/api/menu')
> async def get_menu(user_id: str):
>     dishes = database.get_dishes()
>     return dishes
> ```
>
> When a request comes to `/api/menu`, FastAPI:
> 1. Validates the request (user_id must be a string)
> 2. Calls the function
> 3. Serializes the response to JSON
> 4. Sends it back with proper headers"

#### Q: "How do you handle errors?"

> "Multiple layers:
> 1. **Pydantic validation**: Rejects malformed requests automatically
> 2. **HTTP exceptions**: Return proper status codes (400, 404, 500)
> 3. **Try/catch in agents**: Graceful degradation (if database fails, use CSV backup)
> 4. **Frontend error states**: Display user-friendly messages
> 5. **Logging**: Record errors for debugging"

#### Q: "Explain the caching strategy."

> "Different data has different TTLs (time to live):
> - **Dishes**: 24 hours (menu changes daily)
> - **User feedback**: 2 minutes (might be updated)
> - **Embeddings**: 24 hours (text doesn't change)
>
> Cache hits return immediately (~1ms). Misses fetch fresh data and update the cache. This achieves sub-100ms response times for most requests."

---

### Database Questions

#### Q: "What tables do you have?"

> "Five main tables:
> - **dishes**: Menu items with allergen/dietary flags (refreshed daily)
> - **feedback**: User ratings (user_id, dish_id, liked, date)
> - **user_profiles**: Dietary preferences (is_vegan, avoid_nuts, etc.)
> - **user_moods**: Current mood for each user
> - **dish_embeddings**: Vector embeddings for semantic search"

#### Q: "How do you prevent duplicate entries?"

> "Unique constraints in the database:
> ```sql
> UNIQUE(dish_name, dining_hall, meal_period, scrape_date)
> UNIQUE(user_id, dish_id, rating_date)  -- One rating per dish per day
> ```
>
> We use upsert (insert or update) to handle duplicates gracefully."

---

### AI/ML Questions

#### Q: "What LLM do you use and why?"

> "Perplexity's Sonar model via their API. It's:
> - Cost-effective for simple recommendations
> - Fast response times
> - OpenAI-compatible API (easy LangChain integration)
>
> For food recommendations, we don't need GPT-4 level reasoning. Sonar is sufficient and cheaper."

#### Q: "What embedding model do you use?"

> "all-MiniLM-L6-v2 from sentence-transformers. It:
> - Runs locally (free, no API costs)
> - Generates 384-dimensional vectors
> - Is only 80MB (small model)
> - Has good quality for semantic similarity
>
> We enhance dish names before embedding ('soup' → 'soup, broth, warm, comforting') for richer vectors."

#### Q: "What happens if an external service fails?"

> "Graceful degradation. For example, if the database is slow:
> ```python
> try:
>     data = supabase.query()
> except Exception:
>     data = pd.read_csv("dining_data_clean.csv")  # CSV backup
> ```
>
> We log the error, use fallback data, and continue. The user still gets a recommendation."

---

### System Design Questions

#### Q: "How would you scale this system?"

> "Several improvements:
> 1. **Backend**: It's stateless, so add more instances behind a load balancer
> 2. **Database**: Supabase handles scaling, or add read replicas
> 3. **Caching**: Move from in-memory to Redis for distributed caching
> 4. **AI calls**: Add request queuing, response caching
> 5. **CDN**: Serve frontend from edge locations"

#### Q: "What would you add with more time?"

> "Top priorities:
> 1. **Authentication**: User accounts for cross-device sync
> 2. **Testing**: Unit tests, integration tests, E2E tests
> 3. **Monitoring**: Error tracking, performance metrics
> 4. **Better caching**: Redis instead of in-memory
> 5. **Nutritional data**: Calories, macros for each dish"

---

## Key Numbers to Remember

| Metric | Value | Why |
|--------|-------|-----|
| Embedding dimensions | 384 | all-MiniLM-L6-v2 model |
| Vector candidates | 30 | How many dishes from vector search |
| Top K for LLM | 8 | How many dishes sent to AI |
| Final recommendations | 3-4 | What user sees |
| Taste score weight | 30% | Most important factor |
| Craving score weight | 25% | Second most important |
| Menu cache TTL | 24 hours | Menu changes daily |
| Feedback cache TTL | 2 min | User ratings may update |

---

## Questions YOU Should Ask

At the end of an interview, you'll be asked if you have questions. Ask these:

1. "What does a typical day look like for someone in this role?"
2. "What's the tech stack you're using?"
3. "How do you handle code reviews and deployments?"
4. "What are the biggest technical challenges you're facing?"
5. "What does success look like in the first 90 days?"

---

## Technical Vocabulary Cheat Sheet

| Term | Simple Definition |
|------|-------------------|
| API | Way for programs to talk to each other |
| REST | Convention for designing APIs with HTTP methods |
| Endpoint | A specific URL that does something |
| JSON | Text format for data (key-value pairs) |
| Component | Reusable piece of UI in React |
| State | Data that can change and triggers UI updates |
| Props | Data passed from parent to child component |
| Hook | Function to use React features (useState, useEffect) |
| Context | Way to share data across many components |
| Async/Await | Way to handle operations that take time |
| Promise | Object representing future value |
| Middleware | Code that runs between request and response |
| ORM | Tool to interact with database using code instead of SQL |
| Migration | Version control for database schema changes |
| Singleton | Design pattern ensuring only one instance exists |
| Decorator | `@something` syntax that modifies functions |
| TTL | Time To Live - how long cached data is valid |
| Embedding | Text converted to numbers for ML |
| Vector | List of numbers representing something |
| LLM | Large Language Model (like ChatGPT) |
| RAG | Retrieval Augmented Generation |

---

## Final Tips

1. **Be honest**: If you don't know something, say "I'm not sure, but I would approach it by..."
2. **Think out loud**: Interviewers want to see your thought process
3. **Use examples**: Reference specific files or code from the project
4. **Stay calm**: It's okay to pause and think
5. **Ask clarifying questions**: "Just to make sure I understand, are you asking about...?"

**Good luck with your interview!**
