# BerkeleyBites - Complete Technical Guide

> A personalized food recommendation system for UC Berkeley dining halls using a multi-agent RAG architecture.

**This guide assumes ZERO coding knowledge.** Every concept is explained from first principles.

---

## Table of Contents

### Part 1: Foundational Concepts
1. [What is an API?](#1-what-is-an-api)
2. [What is a Database?](#2-what-is-a-database)
3. [What is Full Stack?](#3-what-is-full-stack)
4. [What are LLMs?](#4-what-are-llms)
5. [What is RAG?](#5-what-is-rag)
6. [What are Embeddings?](#6-what-are-embeddings)

### Part 2: Technology Stack
7. [Frontend Technologies](#7-frontend-technologies)
8. [Backend Technologies](#8-backend-technologies)
9. [Database Technologies](#9-database-technologies)
10. [AI/ML Technologies](#10-aiml-technologies)

### Part 3: Project Architecture
11. [Project Overview](#11-project-overview)
12. [Project Structure](#12-project-structure)
13. [System Architecture Diagram](#13-system-architecture-diagram)
14. [Database Schema](#14-database-schema)

### Part 4: File-by-File Deep Dive
15. [Scraper (scraper.py)](#15-scraper-scraperpy)
16. [Backend Files](#16-backend-files)
17. [Agent Files](#17-agent-files)
18. [Frontend Files](#18-frontend-files)

### Part 5: The Complete Request Flow
19. [Step-by-Step Recommendation Flow](#19-step-by-step-recommendation-flow)
20. [The 4-Stage RAG Pipeline](#20-the-4-stage-rag-pipeline)

### Part 6: Design Decisions
21. [Why These Design Choices?](#21-why-these-design-choices)
22. [Interview Q&A](#22-interview-qa)

---

# PART 1: FOUNDATIONAL CONCEPTS

Before understanding this project, you need to understand the building blocks of modern software.

---

## 1. What is an API?

**API = Application Programming Interface**

Think of an API like a waiter at a restaurant:
- You (the customer) don't go into the kitchen yourself
- You tell the waiter what you want (place an order)
- The waiter goes to the kitchen, gets your food, brings it back
- You never see how the kitchen works

In software:
- Your phone/browser (the customer) doesn't directly access servers
- It sends requests to an API (the waiter)
- The API processes the request, talks to databases/services
- The API sends back a response

### Types of API Requests

| Method | Purpose | Example |
|--------|---------|---------|
| **GET** | Retrieve data | "Show me today's menu" |
| **POST** | Create/send data | "Submit my food rating" |
| **PUT** | Update existing data | "Change my dietary preferences" |
| **DELETE** | Remove data | "Delete my account" |

### What This Looks Like in Code

When you click a button in BerkeleyBites, the frontend sends a request like this:

```
Request: GET /api/menu?dining_hall=crossroads&meal=lunch
```

The backend receives this, queries the database, and responds:

```json
{
  "dishes": [
    {"name": "Teriyaki Chicken", "calories": 450, "is_vegan": false},
    {"name": "Garden Salad", "calories": 120, "is_vegan": true}
  ]
}
```

**In BerkeleyBites:** All communication between the user's browser and our server happens through APIs defined in `backend/main.py`.

---

## 2. What is a Database?

**A database is organized storage for data.**

Think of it like a very sophisticated Excel spreadsheet:
- Data is stored in **tables** (like sheets)
- Each table has **columns** (like headers: Name, Age, Email)
- Each table has **rows** (like individual entries)

### Example: Our `dishes` Table

| id | name | dining_hall | meal_period | is_vegan | is_vegetarian |
|----|------|-------------|-------------|----------|---------------|
| 1 | Teriyaki Chicken | Crossroads | lunch | false | false |
| 2 | Garden Salad | Crossroads | lunch | true | true |
| 3 | Cheese Pizza | Foothill | dinner | false | true |

### SQL: How We Talk to Databases

SQL (Structured Query Language) is the language databases understand.

```sql
-- "Give me all vegan dishes available for lunch"
SELECT * FROM dishes
WHERE is_vegan = true AND meal_period = 'lunch';
```

This returns rows 2 from our example above.

**In BerkeleyBites:** All database operations are in `backend/database.py`. We use Supabase, which is PostgreSQL (a type of database) hosted in the cloud.

---

## 3. What is Full Stack?

**Full Stack = Frontend + Backend + Database**

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (What users see and interact with)                 │
│  - Buttons, forms, colors, animations                        │
│  - Runs in the user's browser                                │
│  - Technologies: React, TypeScript, CSS                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests (APIs)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (Business logic and data processing)                │
│  - Validates inputs, enforces rules                          │
│  - Talks to databases and external services                  │
│  - Runs on a server (not user's computer)                    │
│  - Technologies: Python, FastAPI                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQL Queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (Persistent storage)                               │
│  - Stores all data permanently                               │
│  - Tables for dishes, users, feedback                        │
│  - Technologies: PostgreSQL (via Supabase)                   │
└─────────────────────────────────────────────────────────────┘
```

**Why separate them?**
- **Security**: Users can't directly access the database
- **Maintainability**: Can update one layer without touching others
- **Scalability**: Can add more servers for busy components

---

## 4. What are LLMs?

**LLM = Large Language Model**

An LLM is a type of AI that understands and generates human language. Examples: ChatGPT, Claude, Perplexity.

### How LLMs Work (Simplified)

1. **Training**: The model reads billions of pages of text (books, websites, code)
2. **Learning patterns**: It learns that "The cat sat on the ___" is likely followed by words like "mat", "chair", "couch"
3. **Generating text**: When you ask a question, it predicts the most likely next words based on patterns

### What LLMs Can't Do

- **Access real-time data** - They only know what was in training data
- **Access your database** - They can't see your specific data unless you give it to them
- **Be perfectly accurate** - They can "hallucinate" (make up facts)

### How We Use LLMs in BerkeleyBites

We use the Perplexity API to generate the final recommendation text:

```
We tell the LLM:
"The user is feeling stressed, likes Asian food, has 20 minutes for lunch.
These dishes are available: [Teriyaki Bowl, Pho, Sushi].
Write a personalized 2-sentence recommendation."

LLM responds:
"Since you're stressed and short on time, I'd recommend the Teriyaki Bowl at
Crossroads - it's a warm, satisfying comfort food that pairs perfectly with
your love for Asian flavors."
```

**Important**: We tell the LLM which dishes exist. It doesn't know on its own.

---

## 5. What is RAG?

**RAG = Retrieval Augmented Generation**

This is the key technique that makes BerkeleyBites work reliably.

### The Problem RAG Solves

Without RAG:
```
User: "Recommend me lunch at Berkeley dining halls"
LLM: "Try the Grilled Salmon at Crossroads!"
Reality: Grilled Salmon isn't on today's menu. The LLM hallucinated.
```

With RAG:
```
Step 1 (RETRIEVAL): Query database for today's actual dishes
Step 2 (AUGMENT): Add those dishes to the prompt
Step 3 (GENERATION): LLM picks from REAL dishes only
```

### RAG Pipeline Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                             │
│                                                                  │
│  User Query: "I'm stressed, want healthy lunch"                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STEP 1: RETRIEVAL                                        │    │
│  │ Query our database for dishes that match:                │    │
│  │ - Available today                                        │    │
│  │ - Lunch period                                           │    │
│  │ - Matches "healthy" semantically                         │    │
│  │                                                          │    │
│  │ Result: [Garden Salad, Grain Bowl, Grilled Chicken]      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STEP 2: AUGMENTATION                                     │    │
│  │ Build prompt with retrieved context:                     │    │
│  │                                                          │    │
│  │ "User is stressed, wants healthy food.                   │    │
│  │  Available dishes: Garden Salad, Grain Bowl, Chicken.    │    │
│  │  User previously liked: Asian dishes.                    │    │
│  │  Generate recommendation."                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STEP 3: GENERATION                                       │    │
│  │ LLM reads the augmented prompt and generates:            │    │
│  │                                                          │    │
│  │ "For a stressed day, the Grain Bowl is perfect - light   │    │
│  │  but satisfying, with complex carbs to stabilize your    │    │
│  │  energy. It's at Crossroads, ready in 5 minutes."        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why RAG is important**:
- Guarantees recommendations are for REAL dishes
- Dishes are actually available TODAY
- No hallucination - LLM can only mention what we give it

---

## 6. What are Embeddings?

**Embeddings convert text into numbers that capture meaning.**

### The Problem Embeddings Solve

How do you find dishes similar to "healthy food" in a database?

**Keyword search fails:**
- "Garden Salad" doesn't contain the word "healthy"
- "Grilled Chicken Breast" doesn't contain "healthy"
- But both ARE healthy!

**Embeddings solution:**
- Convert "healthy" to numbers: [0.8, -0.2, 0.5, ...] (384 numbers)
- Convert "Garden Salad" to numbers: [0.75, -0.15, 0.48, ...]
- These are SIMILAR because the meanings are similar!

### How Similarity Works

Imagine a 2D map where similar concepts are close together:

```
                    HEALTHY
                       │
        Salad ●        │       ● Grilled Fish
                       │
        Fruit Bowl ●   │   ● Steamed Vegetables
                       │
   ────────────────────┼────────────────────
                       │
        Burger ●       │       ● Fried Chicken
                       │
        Pizza ●        │       ● Mac & Cheese
                       │
                   UNHEALTHY
```

In reality, we use 384 dimensions instead of 2, but the concept is the same.

### How Embeddings are Generated

```python
# We use a model called "all-MiniLM-L6-v2"
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert text to 384 numbers
embedding = model.encode("Teriyaki Chicken Bowl")
# Result: [0.034, -0.128, 0.891, 0.234, ...] (384 floats)
```

**In BerkeleyBites:**
- `backend/agents/embedding_service.py` generates embeddings
- `scraper.py` creates embeddings for all dishes when scraping
- `dish_embeddings` table stores the vectors in our database
- `pgvector` (a PostgreSQL extension) enables fast similarity search

---

# PART 2: TECHNOLOGY STACK

Now let's understand every tool we use and WHY we chose it.

---

## 7. Frontend Technologies

The frontend is what users see and interact with in their browser.

### React (v19.2.0)

**What it is**: A JavaScript library for building user interfaces.

**How it works**: Instead of building pages as one big HTML file, React breaks the UI into reusable "components":

```
┌─────────────────────────────────────────────────────────┐
│  App (root component)                                    │
│  ├── Header (navigation bar)                             │
│  ├── ChatPanel (recommendation chat)                     │
│  │   ├── ChatMessage (individual message)                │
│  │   ├── QuestionMessage (preference question)           │
│  │   └── ChatInput (text input)                          │
│  └── MenuBrowser (dish list)                             │
│      └── DishCard (single dish)                          │
└─────────────────────────────────────────────────────────┘
```

**Why React over alternatives?**
- Huge ecosystem and community
- Component reusability
- Virtual DOM for performance
- Industry standard (valuable for job interviews)

### TypeScript (v5.9)

**What it is**: JavaScript with type annotations.

**Plain JavaScript:**
```javascript
function addNumbers(a, b) {
  return a + b;
}
addNumbers("5", 3); // Returns "53" (string concatenation!)
// No error - JavaScript allows this mistake
```

**TypeScript:**
```typescript
function addNumbers(a: number, b: number): number {
  return a + b;
}
addNumbers("5", 3); // ERROR: Argument of type 'string' is not assignable
// Catches the bug BEFORE you run the code
```

**Why TypeScript?**
- Catches bugs at compile time, not runtime
- Better IDE autocomplete
- Self-documenting code
- Industry standard for serious projects

### Vite (v7.2.4)

**What it is**: A build tool and development server.

**What build tools do:**
- Bundle many JavaScript files into one
- Compile TypeScript → JavaScript
- Process CSS
- Hot reload (update browser without refresh)

**Why Vite over Webpack?**
- 10-100x faster startup
- Instant hot reload
- Native ES modules (modern approach)
- Zero configuration needed

### Tailwind CSS (v4.1)

**What it is**: A utility-first CSS framework.

**Traditional CSS:**
```css
/* styles.css */
.button-primary {
  background-color: blue;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
}
```
```html
<button class="button-primary">Click me</button>
```

**Tailwind CSS:**
```html
<button class="bg-blue-500 text-white px-4 py-2 rounded">Click me</button>
```

**Why Tailwind?**
- No context switching between CSS and HTML files
- Consistent design system built-in
- Smaller final CSS (only includes what you use)
- Rapid prototyping

---

## 8. Backend Technologies

The backend runs on a server and handles business logic.

### Python (v3.11+)

**What it is**: A programming language known for readability.

**Why Python for AI/ML backends?**
- Best ecosystem for AI/ML libraries
- Simple, readable syntax
- Great for data processing
- LangChain, sentence-transformers, etc. all Python

### FastAPI

**What it is**: A modern Python web framework for building APIs.

**How it works:**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/menu")
async def get_menu(dining_hall: str = None):
    dishes = database.get_dishes(dining_hall=dining_hall)
    return {"dishes": dishes}
```

This creates an endpoint that:
- Listens for GET requests to `/api/menu`
- Accepts optional `dining_hall` parameter
- Returns JSON data

**Why FastAPI over Flask/Django?**
- **Async by default**: Can handle many requests simultaneously
- **Automatic documentation**: Creates API docs at `/docs`
- **Pydantic integration**: Automatic request validation
- **Type hints**: Modern Python with full type support

### Pydantic

**What it is**: Data validation using Python type hints.

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    user_id: str
    is_vegetarian: bool = False
    is_vegan: bool = False
    allergies: list[str] = []

# This validates and converts input automatically
profile = UserProfile(user_id="user123", is_vegetarian="true")
# is_vegetarian becomes True (boolean), not "true" (string)

# This throws an error
profile = UserProfile(user_id=123)  # ERROR: user_id must be string
```

**Why Pydantic?**
- Validates all incoming API requests
- Converts types automatically
- Clear error messages for invalid data
- Documents what data each endpoint expects

### Uvicorn

**What it is**: An ASGI server that runs FastAPI.

Think of it as the "waiter" that listens for incoming requests and hands them to FastAPI.

```bash
uvicorn backend.main:app --port 8000
# This starts the server on port 8000
```

---

## 9. Database Technologies

### Supabase

**What it is**: A hosted PostgreSQL database with extra features.

**Why Supabase over raw PostgreSQL?**
- Free tier (500MB, unlimited API calls)
- Web dashboard to view/edit data
- Built-in authentication (not used in this project)
- Automatic API generation
- Handles hosting, backups, scaling

### PostgreSQL

**What it is**: A powerful open-source relational database.

**Why PostgreSQL?**
- ACID compliance (data integrity guaranteed)
- Complex queries with JOINs
- JSON support for flexible data
- Most mature, battle-tested database

### pgvector

**What it is**: A PostgreSQL extension for vector similarity search.

**Without pgvector**, we'd need a separate vector database like Pinecone.

**With pgvector**, we can do this directly in PostgreSQL:

```sql
-- Find dishes similar to embedding [0.1, 0.2, 0.3, ...]
SELECT name, embedding <=> '[0.1, 0.2, ...]' AS distance
FROM dish_embeddings
ORDER BY distance
LIMIT 10;
```

The `<=>` operator computes cosine distance between vectors.

**Why pgvector?**
- No separate vector database to manage
- All data in one place
- SQL queries can combine filtering + similarity
- Free (unlike Pinecone)

---

## 10. AI/ML Technologies

### LangChain

**What it is**: A framework for building LLM applications.

**What it provides:**
- Abstractions for different LLM providers
- Message history management
- Prompt templates
- Tool calling

**In BerkeleyBites:**

```python
from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatPerplexity(model="llama-3.1-sonar-small-128k-online")

messages = [
    SystemMessage(content="You are a helpful food recommendation assistant."),
    HumanMessage(content="Recommend lunch from these options: ...")
]

response = llm.invoke(messages)
```

### Perplexity API

**What it is**: An LLM API similar to OpenAI but with grounded responses.

**Why Perplexity over OpenAI/Anthropic?**
- Less hallucination
- Faster inference
- Cheaper per token
- OpenAI-compatible API format

### sentence-transformers

**What it is**: A Python library for generating embeddings locally.

**Why local embeddings?**
- Free (no API costs)
- Fast (~10ms per embedding)
- No data sent to external servers
- Good enough quality for this use case

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Teriyaki Chicken")  # Returns 384-dim vector
```

### all-MiniLM-L6-v2

**What it is**: A specific embedding model we use.

**Specs:**
- 384-dimensional vectors
- ~10ms per embedding
- 22M parameters (small)
- Good balance of speed/quality

---

# PART 3: PROJECT ARCHITECTURE

---

## 11. Project Overview

### What is BerkeleyBites?

BerkeleyBites is an AI-powered food recommendation app for UC Berkeley students.

**The Problem:**
- 4+ dining halls with 200+ dishes daily
- Students waste time browsing menus
- No personalization for mood, diet, or taste
- Existing solutions don't track real-time availability

**The Solution:**
- Scrape daily menus automatically
- Learn user preferences from feedback
- Multi-agent AI system considers mood, cravings, time
- Hybrid RAG ensures recommendations are real dishes

### Key Features

1. **Real-time menu data** - Scraped daily from Berkeley dining website
2. **Dietary filtering** - Vegan, vegetarian, halal, kosher, allergen-free
3. **Mood-based recommendations** - Different suggestions for stressed vs. happy
4. **Taste learning** - Remembers likes/dislikes
5. **Multi-agent AI** - Specialized agents for mood, preferences, availability
6. **Hybrid RAG** - SQL + Vector + Scoring + LLM pipeline

---

## 12. Project Structure

```
BerkeleyBites/
│
├── scraper.py                    # Scrapes Berkeley dining website
│
├── backend/                      # ALL SERVER-SIDE CODE
│   ├── __init__.py              # Makes backend a Python package
│   ├── main.py                  # API endpoints (FastAPI)
│   ├── database.py              # Database operations (Supabase)
│   ├── models.py                # Data validation (Pydantic)
│   │
│   └── agents/                  # Multi-agent system
│       ├── __init__.py          # Package exports
│       ├── orchestrator.py      # Coordinates all agents
│       ├── mood_agent.py        # Mood → food mapping
│       ├── question_agent.py    # Preference questions
│       ├── taste_preferences_agent.py   # Feedback analysis
│       ├── food_availability_agent.py   # Available dishes
│       ├── hybrid_retriever.py  # 4-stage RAG pipeline
│       ├── scoring.py           # Dish ranking algorithm
│       ├── embedding_service.py # Vector generation
│       └── cache.py             # Performance caching
│
├── frontend/                    # ALL CLIENT-SIDE CODE
│   └── src/
│       ├── main.tsx             # React entry point
│       ├── App.tsx              # Root component
│       ├── index.css            # Tailwind imports
│       │
│       ├── api/
│       │   └── client.ts        # HTTP requests to backend
│       │
│       ├── context/
│       │   └── AppContext.tsx   # Global state management
│       │
│       ├── hooks/
│       │   ├── useChat.ts       # Chat/recommendation logic
│       │   ├── useMenu.ts       # Menu fetching/filtering
│       │   └── useProfile.ts    # Profile CRUD
│       │
│       ├── types/
│       │   └── index.ts         # TypeScript interfaces
│       │
│       └── components/
│           ├── chat/            # Chat UI components
│           ├── menu/            # Menu browser components
│           ├── profile/         # Profile editor components
│           └── layout/          # Header, shell components
│
├── tests/
│   ├── test_agents.py           # Agent unit tests
│   └── test_e2e.py              # End-to-end tests
│
├── docs/                        # Documentation
├── supabase/                    # Database migrations
├── scripts/                     # Utility scripts
└── requirements.txt             # Python dependencies
```

---

## 13. System Architecture Diagram

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
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
        ┌───────────────┐                   ┌───────────────┐
        │   database.py │                   │  orchestrator │
        │               │                   │  (multi-agent)│
        │  Supabase     │                   │               │
        │  Operations   │                   │  /recommend   │
        │               │                   │  questions    │
        └───────┬───────┘                   └───────┬───────┘
                │                                   │
                ▼                                   ▼
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

## 14. Database Schema

### Table: `dishes`

Stores every menu item scraped from Berkeley dining.

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Unique identifier |
| name | text | Dish name ("Teriyaki Chicken") |
| dining_hall | text | Location ("Crossroads", "Foothill") |
| meal_period | text | "breakfast", "lunch", "dinner" |
| station | text | Station within hall ("Grill", "Salad Bar") |
| is_vegan | boolean | Contains no animal products |
| is_vegetarian | boolean | Contains no meat |
| is_halal | boolean | Prepared according to Islamic law |
| is_kosher | boolean | Prepared according to Jewish law |
| has_gluten | boolean | Contains gluten |
| has_nuts | boolean | Contains tree nuts |
| has_dairy | boolean | Contains dairy |
| has_eggs | boolean | Contains eggs |
| calories | integer | Calorie count (if available) |
| scrape_date | date | When this was scraped |

### Table: `dish_embeddings`

Vector representations for semantic search.

| Column | Type | Description |
|--------|------|-------------|
| dish_id | uuid | Foreign key to dishes |
| embedding | vector(384) | 384-dimensional float array |
| created_at | timestamp | When embedding was generated |

### Table: `user_profiles`

User dietary preferences.

| Column | Type | Description |
|--------|------|-------------|
| user_id | text | User identifier |
| is_vegetarian | boolean | Vegetarian preference |
| is_vegan | boolean | Vegan preference |
| is_halal | boolean | Halal preference |
| is_kosher | boolean | Kosher preference |
| allergies | text[] | List of allergens to avoid |
| preferred_dining_halls | text[] | Favorite locations |
| created_at | timestamp | Profile creation time |
| updated_at | timestamp | Last update time |

### Table: `user_moods`

Current mood state (one row per user).

| Column | Type | Description |
|--------|------|-------------|
| user_id | text | User identifier |
| mood | text | Current mood ("happy", "stressed", etc.) |
| updated_at | timestamp | When mood was last set |

### Table: `feedback`

User ratings on dishes (for taste learning).

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Unique identifier |
| user_id | text | Who rated |
| dish_name | text | What was rated |
| rating | integer | 1 (dislike) or 5 (like) |
| created_at | timestamp | When rating was submitted |

---

# PART 4: FILE-BY-FILE DEEP DIVE

This section explains **HOW** each file works, not just what it does.

---

## 15. Scraper (scraper.py)

**Purpose:** Fetch daily menu data from Berkeley dining website and store it in our database.

**Location:** Root directory

### How It Works (Step by Step)

```
1. HTTP REQUEST
   └── Send GET request to dining.berkeley.edu/menus

2. HTML PARSING
   └── BeautifulSoup parses the HTML response
   └── Extracts: dish name, dining hall, meal, dietary flags

3. DATA TRANSFORMATION
   └── Convert to pandas DataFrame
   └── Normalize column names
   └── Add scrape_date

4. DATABASE STORAGE
   └── Upsert to dishes table (insert or update)
   └── Delete dishes older than 7 days

5. EMBEDDING GENERATION
   └── For each NEW dish not in dish_embeddings:
       └── Generate 384-dim vector using all-MiniLM-L6-v2
       └── Store in dish_embeddings table
```

### Key Code Sections

**HTTP request and parsing:**
```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://dining.berkeley.edu/menus/")
soup = BeautifulSoup(response.text, 'html.parser')

# Find all dish elements
dishes = soup.find_all('div', class_='menu-item')
```

**Embedding generation:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

for dish in new_dishes:
    embedding = model.encode(dish['name'])
    store_embedding(dish['id'], embedding)
```

### When It Runs

- Manually: `python scraper.py`
- In production: Scheduled via cron job or cloud scheduler
- Frequency: Once per day (menus change daily)

---

## 16. Backend Files

### backend/main.py

**Purpose:** Defines all API endpoints. This is the "front door" of the backend.

**What calls it:** Frontend HTTP requests via `api/client.ts`

**What it calls:** `database.py`, `orchestrator.py`

### All Endpoints Explained

```python
# Health check - verify server is running
@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now()}
```

```python
# Get menu with optional filters
@app.get("/api/menu")
async def get_menu(
    dining_hall: str = None,    # Filter by location
    meal_period: str = None,    # Filter by breakfast/lunch/dinner
    user_id: str = None         # Apply dietary restrictions
):
    # 1. Get user profile (if user_id provided)
    # 2. Query dishes with filters
    # 3. Apply dietary restrictions
    # 4. Return filtered list
```

```python
# Main chat/recommendation endpoint
@app.post("/api/chat")
async def chat(message: ChatMessage, user_id: str):
    # If message is "/recommend lunch":
    #   → Start question flow via question_agent
    # If message is answering a question:
    #   → Store answer, get next question or final recommendation
    # Otherwise:
    #   → Return helpful message about using /recommend
```

### How Requests Flow Through main.py

```
Frontend sends: POST /api/chat {"message": "/recommend lunch"}
                                    │
                                    ▼
main.py receives request
    │
    ├── Validates message format (Pydantic)
    │
    ├── Detects "/recommend" command
    │
    ├── Calls orchestrator.get_recommendation()
    │       │
    │       ├── Calls mood_agent
    │       ├── Calls taste_preferences_agent
    │       ├── Calls food_availability_agent
    │       └── Runs hybrid_retriever
    │
    └── Returns JSON response to frontend
```

---

### backend/database.py

**Purpose:** All database operations. No other file talks directly to Supabase.

**What calls it:** `main.py`, all agents

**What it calls:** Supabase Python client

### Key Functions

```python
def get_dishes(
    dining_hall: str = None,
    meal_period: str = None,
    is_vegan: bool = None,
    is_vegetarian: bool = None,
    exclude_allergens: list = None
) -> list[dict]:
    """
    Fetch dishes with filtering.

    HOW IT WORKS:
    1. Start with base query: SELECT * FROM dishes WHERE scrape_date = today
    2. Add filters dynamically based on parameters
    3. Execute query via Supabase client
    4. Return list of dish dictionaries
    """
```

```python
def get_user_profile(user_id: str) -> dict:
    """
    Fetch user's dietary preferences.

    HOW IT WORKS:
    1. Query user_profiles table WHERE user_id = X
    2. If no profile exists, return default profile
    3. Return profile dictionary
    """
```

```python
def submit_feedback(user_id: str, dish_name: str, rating: int):
    """
    Store user's dish rating.

    HOW IT WORKS:
    1. Insert row into feedback table
    2. If user already rated this dish, update existing row
    3. Return success/failure
    """
```

```python
def get_user_feedback_history(user_id: str) -> list[dict]:
    """
    Get all ratings for a user.

    HOW IT WORKS:
    1. Query feedback table WHERE user_id = X
    2. Order by timestamp descending (newest first)
    3. Return list of {dish_name, rating, created_at}
    """
```

### Supabase Client Usage

```python
from supabase import create_client

# Initialize client (credentials from environment variables)
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# Example query
result = supabase.table("dishes").select("*").eq("meal_period", "lunch").execute()
dishes = result.data  # List of dictionaries
```

---

### backend/models.py

**Purpose:** Define the shape of all data going in and out of the API.

**How Pydantic works:**

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    user_id: str
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_halal: bool = False
    is_kosher: bool = False
    allergies: list[str] = []
    preferred_dining_halls: list[str] = []

# When a request comes in:
# {"user_id": "abc", "is_vegetarian": "true"}
#
# Pydantic automatically:
# 1. Validates user_id is a string ✓
# 2. Converts "true" to True (boolean) ✓
# 3. Sets defaults for missing fields ✓
# 4. Returns error if user_id is missing ✗
```

### All Models

```python
class Dish(BaseModel):
    """A menu item"""
    id: str
    name: str
    dining_hall: str
    meal_period: str
    is_vegan: bool
    is_vegetarian: bool
    # ... other fields

class ChatMessage(BaseModel):
    """Incoming chat message"""
    message: str
    session_id: str = None
    answered_questions: dict = {}

class RecommendationResponse(BaseModel):
    """What we return after recommendation"""
    agent_summaries: dict
    recommendation: str
    session_id: str

class FeedbackRequest(BaseModel):
    """Rating submission"""
    user_id: str
    dish_name: str
    rating: int  # 1 or 5
```

---

## 17. Agent Files

The agents in `backend/agents/` form a multi-agent system. Each agent has a specific responsibility.

### backend/agents/orchestrator.py

**Purpose:** The "conductor" that coordinates all other agents.

**What calls it:** `main.py` when user wants a recommendation

**What it calls:** mood_agent, taste_preferences_agent, food_availability_agent, hybrid_retriever

### How Orchestration Works

```python
def get_recommendation(
    user_id: str,
    meal_period: str,
    answered_questions: dict
) -> RecommendationResponse:
    """
    Coordinate agents to generate a recommendation.

    STEP-BY-STEP:

    1. SET MOOD CONTEXT
       mood_agent.set_user_mood(answered_questions["mood"])
       # This updates global state so mood_agent knows current mood

    2. GATHER AGENT CONTEXTS (in parallel conceptually)
       mood_context = mood_agent.get_user_mood()
       # Returns: "Current Mood: STRESSED\nFood Guidance: Go for comfort food..."

       taste_context = taste_preferences_agent.get_taste_preferences()
       # Returns: "Based on history: Likes Asian, dislikes heavy pasta..."

       availability_context = food_availability_agent.get_available_dishes()
       # Returns: "Found 180 dishes for lunch, 45 vegetarian options..."

    3. BUILD PROMPT
       prompt = f'''
       User Context:
       {mood_context}
       {taste_context}

       Available Dishes:
       {availability_context}

       Generate a personalized recommendation.
       '''

    4. RUN HYBRID RETRIEVER
       final_recommendation = hybrid_retriever.retrieve(
           query=answered_questions["craving"],
           user_context=prompt,
           ...
       )

    5. FORMAT RESPONSE
       return RecommendationResponse(
           agent_summaries={
               "mood": format_mood_summary(mood_context),
               "preferences": format_taste_summary(taste_context),
               "availability": format_availability_summary(availability_context)
           },
           recommendation=final_recommendation
       )
    """
```

### Agent Summary Formatting

The orchestrator formats agent outputs into nice summaries for the UI:

```python
def format_mood_summary(mood_text: str) -> dict:
    """Convert mood agent output to UI-friendly format."""
    # Input: "Current Mood: STRESSED\nFood Guidance: Go for comfort..."
    # Output: {
    #     "icon": "😤",
    #     "title": "Mood",
    #     "points": ["Feeling stressed", "Go for comfort food"]
    # }
```

---

### backend/agents/mood_agent.py

**Purpose:** Map user mood to food guidance. No AI - just a lookup table.

**Why no AI?** This is deterministic logic. "Stressed → comfort food" is a fixed rule. No need to waste API calls on something predictable.

### How It Works

```python
# The mapping table
MOOD_GUIDANCE = {
    "happy": {
        "description": "Feeling happy and content",
        "food_suggestion": "Try something adventurous or celebratory!",
        "prefer_categories": ["entrees", "chef's special"],
        "avoid_categories": []
    },
    "stressed": {
        "description": "Feeling anxious or overwhelmed",
        "food_suggestion": "Go for comfort food. Warm soups, pasta...",
        "prefer_categories": ["soups", "comfort food", "pasta"],
        "avoid_categories": ["fried foods"]
    },
    # ... more moods
}

# Global state (set by orchestrator)
_user_mood: str = "happy"

def set_user_mood(mood: str):
    """Called by orchestrator before getting mood guidance."""
    global _user_mood
    _user_mood = mood

@tool  # LangChain tool decorator
def get_user_mood() -> str:
    """
    Get mood-based food guidance.

    HOW IT WORKS:
    1. Look up current mood in MOOD_GUIDANCE dict
    2. Format as readable string
    3. Return guidance text
    """
    guidance = MOOD_GUIDANCE[_user_mood]
    return f"""Current Mood: {_user_mood.upper()}
{guidance['description']}
Food Guidance: {guidance['food_suggestion']}
Preferred categories: {guidance['prefer_categories']}"""
```

---

### backend/agents/question_agent.py

**Purpose:** Manage the 4 preference questions asked before generating a recommendation.

### The Questions

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
            {"value": "filling", "label": "Big Filling Meal", "emoji": "🍛"},
        ]
    },
    {
        "id": "spice",
        "question_text": "How adventurous with spice today?",
        "options": [...]
    },
    {
        "id": "time",
        "question_text": "How much time do you have?",
        "options": [...]
    }
]

QUESTION_ORDER = ["mood", "craving", "spice", "time"]
```

### Key Functions

```python
def get_next_question(answered: dict) -> dict | None:
    """
    Get the next unanswered question.

    HOW IT WORKS:
    1. Iterate through QUESTION_ORDER
    2. Find first question not in answered dict
    3. Return that question, or None if all answered

    Example:
    answered = {"mood": "happy"}
    → Returns craving question (next unanswered)

    answered = {"mood": "happy", "craving": "healthy", "spice": "mild", "time": "normal"}
    → Returns None (all answered, ready for recommendation)
    """
    for q_id in QUESTION_ORDER:
        if q_id not in answered:
            return next(q for q in QUESTIONS if q["id"] == q_id)
    return None

def all_questions_answered(answered: dict) -> bool:
    """Check if we have all 4 answers."""
    return all(q_id in answered for q_id in QUESTION_ORDER)
```

---

### backend/agents/taste_preferences_agent.py

**Purpose:** Analyze user's feedback history to understand their taste preferences.

**What calls it:** orchestrator.py

**What it calls:** database.py to get feedback history

### How It Works

```python
@tool
def get_taste_preferences(user_id: str) -> str:
    """
    Analyze user's past ratings to understand preferences.

    HOW IT WORKS:

    1. FETCH HISTORY
       feedback = database.get_user_feedback_history(user_id)
       # Returns: [
       #   {"dish_name": "Teriyaki Chicken", "rating": 5},
       #   {"dish_name": "Caesar Salad", "rating": 5},
       #   {"dish_name": "Heavy Pasta", "rating": 1},
       # ]

    2. CATEGORIZE
       liked = [f for f in feedback if f["rating"] == 5]
       disliked = [f for f in feedback if f["rating"] == 1]

    3. DETECT PATTERNS
       # Look for common themes in liked dishes
       patterns = analyze_dish_names(liked)
       # e.g., "Asian" appears frequently → user likes Asian food

    4. FORMAT OUTPUT
       return f'''
       Taste Profile for {user_id}:

       Liked dishes ({len(liked)}):
       - Teriyaki Chicken
       - Caesar Salad

       Disliked dishes ({len(disliked)}):
       - Heavy Pasta

       Detected patterns:
       - Prefers Asian flavors
       - Avoids heavy carbs
       '''
    """
```

---

### backend/agents/food_availability_agent.py

**Purpose:** Query what dishes are actually available right now.

### How It Works

```python
@tool
def get_available_dishes(
    meal_period: str,
    dietary_restrictions: dict = None
) -> str:
    """
    Get available dishes with filtering.

    HOW IT WORKS:

    1. QUERY DATABASE
       dishes = database.get_dishes(
           scrape_date=today,
           meal_period=meal_period,
           is_vegan=dietary_restrictions.get("is_vegan"),
           exclude_allergens=dietary_restrictions.get("allergies")
       )

    2. GROUP BY DINING HALL
       by_hall = group_dishes_by_hall(dishes)
       # {
       #   "Crossroads": [dish1, dish2, ...],
       #   "Foothill": [dish3, dish4, ...],
       # }

    3. FORMAT OUTPUT
       output = f"Found {len(dishes)} dishes for {meal_period}:\n\n"
       for hall, hall_dishes in by_hall.items():
           output += f"{hall}: {len(hall_dishes)} items\n"
       return output
    """
```

---

### backend/agents/hybrid_retriever.py

**Purpose:** The 4-stage RAG pipeline that finds the best dishes to recommend.

**This is the most complex and important file in the system.**

### The 4 Stages

```
STAGE 1: SQL Filters       →  Guarantee safety (dietary restrictions)
STAGE 2: Vector Search     →  Find semantically relevant dishes
STAGE 3: Multi-Factor Score →  Rank by personalization factors
STAGE 4: LLM Generation    →  Write human-readable recommendation
```

### Stage-by-Stage Breakdown

```python
def retrieve(
    query: str,                  # User's craving ("healthy", "comfort food")
    user_id: str,
    meal_period: str,
    mood: str,
    dietary_restrictions: dict
) -> str:
    """
    4-stage retrieval pipeline.
    """

    # ═══════════════════════════════════════════════════════════════
    # STAGE 1: SQL FILTERS (~5ms)
    # Purpose: GUARANTEE dietary safety, eliminate invalid dishes
    # ═══════════════════════════════════════════════════════════════

    sql_filtered = database.get_dishes(
        scrape_date=today,
        meal_period=meal_period,
        is_vegan=dietary_restrictions.get("is_vegan"),
        is_vegetarian=dietary_restrictions.get("is_vegetarian"),
        exclude_allergens=dietary_restrictions.get("allergies")
    )
    # Example: 245 dishes → 180 dishes (removed meat for vegetarian user)

    # ═══════════════════════════════════════════════════════════════
    # STAGE 2: VECTOR SEARCH (~15ms)
    # Purpose: Find dishes semantically similar to the query
    # ═══════════════════════════════════════════════════════════════

    # Convert query to embedding
    query_embedding = embedding_service.generate_embedding(query)
    # "healthy" → [0.82, -0.15, 0.44, ...] (384 floats)

    # Find similar dishes using pgvector
    similar_dishes = database.vector_search(
        query_embedding=query_embedding,
        dish_ids=[d["id"] for d in sql_filtered],  # Only search within filtered
        limit=30
    )
    # 180 dishes → 30 most semantically similar

    # ═══════════════════════════════════════════════════════════════
    # STAGE 3: MULTI-FACTOR SCORING (~10ms)
    # Purpose: Rank dishes by multiple personalization signals
    # ═══════════════════════════════════════════════════════════════

    scored_dishes = []
    for dish in similar_dishes:
        score = scoring.compute_dish_score(
            dish=dish,
            user_id=user_id,
            mood=mood,
            query=query
        )
        scored_dishes.append((dish, score))

    # Sort by score, take top 10
    top_dishes = sorted(scored_dishes, key=lambda x: x[1], reverse=True)[:10]

    # ═══════════════════════════════════════════════════════════════
    # STAGE 4: LLM GENERATION (~800ms)
    # Purpose: Write a human-readable, personalized recommendation
    # ═══════════════════════════════════════════════════════════════

    prompt = f"""You are a helpful Berkeley dining assistant.

    User Context:
    - Mood: {mood}
    - Craving: {query}
    - Dietary restrictions: {dietary_restrictions}

    Top recommended dishes:
    {format_dishes(top_dishes)}

    Write a friendly 2-3 sentence recommendation mentioning specific dishes."""

    response = llm.invoke(prompt)
    return response.content
```

---

### backend/agents/scoring.py

**Purpose:** Compute a personalization score for each dish.

### The Scoring Formula

```python
def compute_dish_score(
    dish: dict,
    user_id: str,
    mood: str,
    query: str
) -> float:
    """
    Multi-factor weighted score.

    WEIGHTS:
    - 30% feedback_score    (Did user like similar dishes?)
    - 25% mood_score        (Does it match current mood?)
    - 25% craving_score     (Semantic similarity to query)
    - 10% variety_score     (Different from recent picks?)
    - 10% category_bonus    (Is it in preferred categories?)
    """

    # FEEDBACK SCORE (30%)
    # Check if user liked/disliked similar dishes
    similar_ratings = get_ratings_for_similar_dishes(user_id, dish)
    feedback_score = average(similar_ratings) if similar_ratings else 0.5

    # MOOD SCORE (25%)
    # Check if dish category matches mood guidance
    mood_guidance = MOOD_GUIDANCE[mood]
    if dish["category"] in mood_guidance["prefer_categories"]:
        mood_score = 1.0
    elif dish["category"] in mood_guidance["avoid_categories"]:
        mood_score = 0.0
    else:
        mood_score = 0.5

    # CRAVING SCORE (25%)
    # Semantic similarity between query and dish name
    query_embedding = generate_embedding(query)
    dish_embedding = get_dish_embedding(dish["id"])
    craving_score = cosine_similarity(query_embedding, dish_embedding)

    # VARIETY SCORE (10%)
    # Penalize dishes recommended recently
    recent = get_recent_recommendations(user_id)
    variety_score = 0.0 if dish["name"] in recent else 1.0

    # CATEGORY BONUS (10%)
    # Bonus for user's preferred food categories
    preferred = get_user_preferred_categories(user_id)
    category_bonus = 1.0 if dish["category"] in preferred else 0.0

    # WEIGHTED SUM
    total = (
        0.30 * feedback_score +
        0.25 * mood_score +
        0.25 * craving_score +
        0.10 * variety_score +
        0.10 * category_bonus
    )

    return total
```

---

### backend/agents/embedding_service.py

**Purpose:** Generate vector embeddings for text.

### How It Works

```python
from sentence_transformers import SentenceTransformer

# Load model once at startup (expensive operation)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list[float]:
    """
    Convert text to 384-dimensional vector.

    HOW IT WORKS:
    1. Tokenize text into subwords
    2. Pass through transformer neural network
    3. Pool outputs into single vector
    4. Return 384 floats

    Example:
    generate_embedding("Teriyaki Chicken Bowl")
    → [0.034, -0.128, 0.891, 0.234, ...]
    """
    embedding = model.encode(text)
    return embedding.tolist()  # Convert numpy array to Python list

def generate_batch_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts efficiently."""
    embeddings = model.encode(texts)
    return [e.tolist() for e in embeddings]
```

---

### backend/agents/cache.py

**Purpose:** Cache frequently accessed data for faster responses.

### How It Works

```python
from functools import lru_cache
from datetime import datetime, timedelta

# In-memory cache
_cache = {}
_cache_times = {}
CACHE_TTL = timedelta(minutes=30)

def get_cached(key: str):
    """Get from cache if not expired."""
    if key in _cache:
        if datetime.now() - _cache_times[key] < CACHE_TTL:
            return _cache[key]
        else:
            del _cache[key]
            del _cache_times[key]
    return None

def set_cached(key: str, value):
    """Store in cache."""
    _cache[key] = value
    _cache_times[key] = datetime.now()

# Usage in other files:
def get_dishes_cached(meal_period: str):
    key = f"dishes_{meal_period}_{today}"
    cached = get_cached(key)
    if cached:
        return cached

    dishes = database.get_dishes(meal_period=meal_period)
    set_cached(key, dishes)
    return dishes
```

---

## 18. Frontend Files

### frontend/src/main.tsx

**Purpose:** Entry point. Renders the React app into the HTML page.

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Find the div with id="root" in index.html
// Render our App component inside it
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

### frontend/src/App.tsx

**Purpose:** Root component. Sets up providers and layout.

```tsx
import { AppProvider } from './context/AppContext'
import { AppShell } from './components/layout/AppShell'
import { ChatPanel } from './components/chat/ChatPanel'
import { MenuBrowser } from './components/menu/MenuBrowser'

function App() {
  return (
    // AppProvider gives all children access to global state
    <AppProvider>
      <AppShell>
        {/* Main content area */}
        <div className="grid grid-cols-2 gap-4">
          <ChatPanel />      {/* Left: Recommendation chat */}
          <MenuBrowser />    {/* Right: Browse menu */}
        </div>
      </AppShell>
    </AppProvider>
  )
}
```

### frontend/src/context/AppContext.tsx

**Purpose:** Global state management. Stores data needed by multiple components.

```tsx
import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../api/client'

// Define what's in our global state
interface AppState {
  profile: UserProfile | null
  mood: string
  messages: Message[]
  loading: boolean
}

// Create the context
const AppContext = createContext<AppState | null>(null)

// Provider component wraps the app
export function AppProvider({ children }) {
  const [profile, setProfile] = useState(null)
  const [mood, setMood] = useState('happy')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  // Load profile on mount
  useEffect(() => {
    async function loadProfile() {
      const data = await api.getProfile()
      setProfile(data)
    }
    loadProfile()
  }, [])

  return (
    <AppContext.Provider value={{
      profile, setProfile,
      mood, setMood,
      messages, setMessages,
      loading, setLoading
    }}>
      {children}
    </AppContext.Provider>
  )
}

// Hook to use the context
export function useApp() {
  return useContext(AppContext)
}
```

### frontend/src/api/client.ts

**Purpose:** All HTTP requests to the backend.

```typescript
const BASE_URL = '/api'  // Vite proxies this to localhost:8000

export const api = {
  // Get menu with filters
  async getMenu(params: { dining_hall?: string, meal_period?: string }) {
    const query = new URLSearchParams(params).toString()
    const response = await fetch(`${BASE_URL}/menu?${query}`)
    return response.json()
  },

  // Get user profile
  async getProfile(userId: string) {
    const response = await fetch(`${BASE_URL}/profile?user_id=${userId}`)
    return response.json()
  },

  // Update profile
  async updateProfile(profile: UserProfile) {
    const response = await fetch(`${BASE_URL}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    })
    return response.json()
  },

  // Submit feedback
  async submitFeedback(userId: string, dishName: string, rating: number) {
    const response = await fetch(`${BASE_URL}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, dish_name: dishName, rating })
    })
    return response.json()
  },

  // Chat/recommendation
  async chat(message: string, sessionId?: string, answeredQuestions?: object) {
    const response = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        answered_questions: answeredQuestions
      })
    })
    return response.json()
  }
}
```

### frontend/src/hooks/useChat.ts

**Purpose:** Manage chat state and recommendation flow.

```typescript
import { useState } from 'react'
import { api } from '../api/client'
import { useApp } from '../context/AppContext'

export function useChat() {
  const { messages, setMessages } = useApp()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [answeredQuestions, setAnsweredQuestions] = useState({})
  const [currentQuestion, setCurrentQuestion] = useState(null)

  // Start recommendation flow
  async function startRecommendation(mealPeriod: string) {
    setAnsweredQuestions({})  // Reset

    const response = await api.chat(`/recommend ${mealPeriod}`)

    if (response.question) {
      // Backend is asking a question
      setCurrentQuestion(response.question)
      setSessionId(response.session_id)
    } else {
      // Got final recommendation (shouldn't happen on first call)
      setMessages([...messages, { type: 'recommendation', content: response }])
    }
  }

  // Answer a question
  async function answerQuestion(questionId: string, answer: string) {
    const newAnswers = { ...answeredQuestions, [questionId]: answer }
    setAnsweredQuestions(newAnswers)

    const response = await api.chat(
      `/answer ${answer}`,
      sessionId,
      newAnswers
    )

    if (response.question) {
      // More questions
      setCurrentQuestion(response.question)
    } else {
      // Final recommendation!
      setCurrentQuestion(null)
      setMessages([...messages, { type: 'recommendation', content: response }])
    }
  }

  return {
    messages,
    currentQuestion,
    startRecommendation,
    answerQuestion
  }
}
```

---

# PART 5: THE COMPLETE REQUEST FLOW

---

## 19. Step-by-Step Recommendation Flow

Let's trace exactly what happens when a user clicks "Get Recommendation".

### Step 1: User Clicks Button

```
User clicks "Get Recommendation" for lunch
```

### Step 2: Frontend Sends Request

```typescript
// ChatPanel.tsx
<button onClick={() => startRecommendation('lunch')}>
  Get Recommendation
</button>

// useChat.ts
async function startRecommendation(mealPeriod: string) {
  const response = await api.chat(`/recommend ${mealPeriod}`)
  // ...
}

// client.ts
async chat(message: string, ...) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: '/recommend lunch' })
  })
}
```

**HTTP Request:**
```
POST /api/chat
Content-Type: application/json

{"message": "/recommend lunch"}
```

### Step 3: Backend Receives, Starts Question Flow

```python
# backend/main.py
@app.post("/api/chat")
async def chat(message: ChatMessage):
    if message.message.startswith("/recommend"):
        # Extract meal period
        meal_period = "lunch"

        # Get first question
        next_q = question_agent.get_next_question({})

        return {
            "question": next_q,
            "session_id": generate_session_id()
        }
```

**Response:**
```json
{
  "question": {
    "id": "mood",
    "question_text": "How are you feeling right now?",
    "options": [
      {"value": "happy", "label": "Happy", "emoji": "😊"},
      ...
    ]
  },
  "session_id": "sess_abc123"
}
```

### Step 4: User Answers 4 Questions

This loop repeats 4 times:

1. Frontend displays question
2. User clicks an option
3. Frontend sends answer
4. Backend returns next question (or final recommendation)

```python
# After all 4 questions answered:
answered_questions = {
    "mood": "stressed",
    "craving": "healthy",
    "spice": "mild",
    "time": "normal"
}
```

### Step 5: Orchestrator Gathers Agent Context

```python
# backend/agents/orchestrator.py
def get_recommendation(user_id, meal_period, answered_questions):

    # Set mood for mood agent
    mood_agent.set_user_mood(answered_questions["mood"])

    # Get context from each agent
    mood_context = mood_agent.get_user_mood()
    # "Current Mood: STRESSED
    #  Food Guidance: Go for comfort food..."

    taste_context = taste_preferences_agent.get_taste_preferences(user_id)
    # "Taste Profile: Likes Asian food, avoids heavy pasta..."

    availability = food_availability_agent.get_available_dishes(meal_period)
    # "Found 180 dishes for lunch..."
```

### Step 6: Hybrid Retriever Runs 4-Stage Pipeline

```
Stage 1: SQL Filters
├── Input: 245 total lunch dishes
├── Apply: is_vegetarian = true (if user is vegetarian)
├── Apply: exclude nut dishes (if user has nut allergy)
└── Output: 180 dishes

Stage 2: Vector Search
├── Input: 180 filtered dishes
├── Query: "healthy" → [0.82, -0.15, ...]
├── pgvector cosine similarity
└── Output: 30 most similar dishes

Stage 3: Scoring
├── Input: 30 dishes
├── Score each by:
│   ├── 30% feedback history
│   ├── 25% mood match
│   ├── 25% craving match
│   ├── 10% variety
│   └── 10% category preference
└── Output: Top 10 dishes with scores

Stage 4: LLM Generation
├── Input: Top 10 dishes + user context
├── Prompt: "Generate personalized recommendation..."
└── Output: Natural language recommendation
```

### Step 7: Response Sent to Frontend

```json
{
  "agent_summaries": {
    "mood": {
      "icon": "😤",
      "title": "Mood",
      "points": ["Feeling stressed", "Comfort food recommended"]
    },
    "preferences": {
      "icon": "👤",
      "title": "Your Taste",
      "points": ["Likes Asian food", "Avoids heavy dishes"]
    },
    "availability": {
      "icon": "🍽️",
      "title": "Available",
      "points": ["180 dishes for lunch", "45 vegetarian"]
    }
  },
  "recommendation": "Since you're feeling stressed, I'd recommend the Grain Bowl at Crossroads - it's light but satisfying, perfect for a busy day. The warm grains and fresh vegetables will help you feel energized without weighing you down.",
  "session_id": "sess_abc123"
}
```

### Step 8: Frontend Displays Recommendation

```tsx
// RecommendationMessage.tsx
<div className="recommendation">
  {/* Agent summary cards */}
  <div className="flex gap-2">
    {Object.entries(response.agent_summaries).map(([key, summary]) => (
      <AgentSummaryCard
        icon={summary.icon}
        title={summary.title}
        points={summary.points}
      />
    ))}
  </div>

  {/* Main recommendation text */}
  <p className="mt-4 text-lg">
    {response.recommendation}
  </p>
</div>
```

---

## 20. The 4-Stage RAG Pipeline

### Why 4 Stages?

Each stage solves a specific problem:

| Stage | Problem Solved | Technique |
|-------|---------------|-----------|
| 1. SQL | Safety (dietary) | Boolean filters |
| 2. Vector | Meaning | Semantic similarity |
| 3. Scoring | Personalization | Multi-factor ranking |
| 4. LLM | Communication | Natural language |

### Detailed Pipeline Visualization

```
                    USER QUERY
                "I want something healthy"
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│              STAGE 1: SQL FILTERS                          │
│              Purpose: SAFETY GUARANTEE                     │
│              Time: ~5ms                                    │
│                                                           │
│  Query: SELECT * FROM dishes WHERE                        │
│         scrape_date = '2024-01-15' AND                    │
│         meal_period = 'lunch' AND                         │
│         is_vegetarian = true AND  -- User is vegetarian   │
│         NOT has_nuts              -- User allergic to nuts │
│                                                           │
│  Input:  245 dishes                                       │
│  Output: 180 dishes (removed violations)                  │
│                                                           │
│  WHY FIRST: A vegetarian must NEVER see meat.             │
│  This is a hard safety requirement, not a preference.     │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│              STAGE 2: VECTOR SEARCH                        │
│              Purpose: SEMANTIC RELEVANCE                   │
│              Time: ~15ms                                   │
│                                                           │
│  1. Convert "healthy" to embedding:                       │
│     [0.82, -0.15, 0.44, 0.23, ...]  (384 floats)         │
│                                                           │
│  2. For each dish in 180 filtered:                        │
│     - Get dish embedding from dish_embeddings table       │
│     - Compute cosine similarity                           │
│                                                           │
│  3. Sort by similarity, take top 30                       │
│                                                           │
│  Input:  180 dishes                                       │
│  Output: 30 semantically relevant dishes                  │
│                                                           │
│  WHY: "Garden Salad" doesn't contain "healthy" but        │
│  its embedding is similar → found via vector search       │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│              STAGE 3: MULTI-FACTOR SCORING                 │
│              Purpose: PERSONALIZATION                      │
│              Time: ~10ms                                   │
│                                                           │
│  For each of 30 dishes, compute:                          │
│                                                           │
│  feedback_score (30%):                                    │
│    └── User liked similar dishes before? (+)              │
│    └── User disliked similar dishes? (-)                  │
│                                                           │
│  mood_score (25%):                                        │
│    └── Dish category in mood's "prefer"? (+)              │
│    └── Dish category in mood's "avoid"? (-)               │
│                                                           │
│  craving_score (25%):                                     │
│    └── Already computed in Stage 2 (similarity)           │
│                                                           │
│  variety_score (10%):                                     │
│    └── Recommended recently? (-) Novelty bonus? (+)       │
│                                                           │
│  category_bonus (10%):                                    │
│    └── In user's preferred categories? (+)                │
│                                                           │
│  Input:  30 dishes                                        │
│  Output: 10 top-scored dishes                             │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│              STAGE 4: LLM GENERATION                       │
│              Purpose: NATURAL COMMUNICATION                │
│              Time: ~800ms                                  │
│                                                           │
│  Prompt to Perplexity:                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │ You are a friendly Berkeley dining assistant.       │   │
│  │                                                     │   │
│  │ User Context:                                       │   │
│  │ - Mood: Stressed                                    │   │
│  │ - Craving: Healthy food                             │   │
│  │ - Time: Normal (15-30 min)                          │   │
│  │ - Dietary: Vegetarian, no nuts                      │   │
│  │                                                     │   │
│  │ Top Dishes (pre-validated, safe to recommend):      │   │
│  │ 1. Grain Bowl (Crossroads) - Score: 0.89            │   │
│  │ 2. Garden Salad (Foothill) - Score: 0.85            │   │
│  │ 3. Veggie Stir Fry (Cafe 3) - Score: 0.82           │   │
│  │ ...                                                 │   │
│  │                                                     │   │
│  │ Write a friendly 2-3 sentence recommendation.       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  LLM Response:                                            │
│  "Since you're feeling stressed, the Grain Bowl at        │
│   Crossroads is perfect - it's comforting yet light,      │
│   with complex carbs to stabilize your energy..."         │
│                                                           │
│  Input:  10 dishes + context                              │
│  Output: Natural language recommendation                  │
└───────────────────────────────────────────────────────────┘
```

---

# PART 6: DESIGN DECISIONS

---

## 21. Why These Design Choices?

### Why Multi-Agent Instead of One Big Prompt?

**The Problem with One Big Prompt:**
```
Prompt: "You are a food assistant. The user is stressed, vegetarian,
allergic to nuts, likes Asian food, has 15 minutes. Today's menu has
245 dishes: [huge list]. Their past ratings are: [huge list].
Recommend something."

Issues:
1. Expensive - sending 245 dishes every time
2. Slow - LLM processing all that text
3. Unreliable - LLM might miss dietary restrictions
4. Hard to debug - what went wrong?
```

**Multi-Agent Solution:**
```
Mood Agent:      "Stressed → comfort food" (lookup, 1ms)
Taste Agent:     "Likes Asian, dislikes pasta" (SQL, 10ms)
Food Agent:      "180 dishes available" (SQL, 5ms)
Retriever:       "Top 10 dishes" (vector + scoring, 25ms)
LLM:             "Writes recommendation" (only sees 10 dishes, 800ms)

Benefits:
1. Cheaper - LLM only sees 10 dishes
2. Faster - 80% is deterministic code
3. Safer - SQL guarantees dietary safety
4. Testable - each agent tested separately
```

### Why SQL Filters BEFORE Vector Search?

**Safety First Principle:**
- A vegetarian must NEVER see meat dishes
- Nut allergy must NEVER see nut dishes
- This is not a preference, it's safety

**If Vector Search First:**
```
Vector search for "comfort food"
→ Returns: Mac & Cheese, Beef Stew, Grilled Chicken, Tofu Curry
→ Then filter: Remove meat for vegetarian
→ Problem: Might remove the MOST relevant dishes, leaving poor options
```

**If SQL First:**
```
SQL filter: vegetarian dishes only
→ Returns: Mac & Cheese, Tofu Curry, Veggie Soup, Pasta Primavera
→ Vector search for "comfort food"
→ Returns: Mac & Cheese, Tofu Curry (both are relevant AND safe)
```

### Why Local Embeddings Instead of OpenAI?

| Factor | Local (MiniLM) | OpenAI API |
|--------|----------------|------------|
| Cost | Free | ~$0.10/day |
| Latency | ~10ms | ~200ms + network |
| Quality | Good for dish names | Slightly better |
| Privacy | Data stays local | Data sent externally |
| Reliability | No API dependency | API can go down |

For dish names like "Teriyaki Chicken", local embeddings are sufficient.

### Why Supabase?

**Alternatives Considered:**
- **Firebase**: No vector search, NoSQL (harder joins)
- **MongoDB**: No built-in vector search
- **Pinecone + PostgreSQL**: Two systems to manage

**Supabase Advantages:**
- PostgreSQL with pgvector = one database for everything
- Free tier (500MB, unlimited API)
- Web dashboard for debugging
- Automatic backups

### Why FastAPI Instead of Flask/Django?

| Factor | FastAPI | Flask | Django |
|--------|---------|-------|--------|
| Async | Built-in | Extension | Extension |
| Type hints | Required | Optional | Optional |
| Validation | Pydantic | Manual | Django Forms |
| Auto docs | Yes | No | DRF needed |
| Performance | High | Medium | Medium |

FastAPI's Pydantic integration means validation is automatic:

```python
# FastAPI (automatic validation)
@app.post("/api/profile")
async def update_profile(profile: UserProfile):
    # profile is already validated by Pydantic
    pass

# Flask (manual validation)
@app.route("/api/profile", methods=["POST"])
def update_profile():
    data = request.json
    # Must manually check is_vegetarian is boolean, etc.
    pass
```

---

## 22. Interview Q&A

### General Questions

**Q: "What does this project do in one sentence?"**
> BerkeleyBites is an AI-powered food recommendation app that scrapes daily Berkeley dining menus and generates personalized recommendations using mood, taste history, and dietary preferences.

**Q: "Walk me through the tech stack."**
> Frontend: React 19 + TypeScript for type-safe components, Tailwind for styling, Vite for fast builds.
> Backend: FastAPI (Python) for async APIs with automatic validation via Pydantic.
> Database: Supabase (PostgreSQL) with pgvector for vector similarity search.
> AI: Local embeddings via sentence-transformers, Perplexity API for natural language generation.

### Architecture Questions

**Q: "Walk me through what happens when a user asks for a recommendation."**
> 1. Frontend sends POST /api/chat with "/recommend lunch"
> 2. Question agent asks 4 preference questions (mood, craving, spice, time)
> 3. Orchestrator gathers context from mood agent, taste agent, food agent
> 4. Hybrid retriever runs 4-stage pipeline: SQL filters → Vector search → Scoring → LLM
> 5. LLM writes personalized recommendation from top 10 dishes
> 6. Response includes agent summaries + recommendation text

**Q: "Why multiple agents instead of one LLM call?"**
> Separation of concerns. Each agent does one thing: Mood agent uses a lookup table (no AI needed), Taste agent analyzes history with SQL, Food agent queries available dishes. This makes the system:
> - Fast (80% is deterministic code, not LLM)
> - Cheap (LLM only called once at the end)
> - Safe (SQL guarantees dietary restrictions)
> - Testable (each agent tested in isolation)

**Q: "How do you ensure dietary safety?"**
> SQL filters run FIRST in the pipeline. Before any AI involvement, we eliminate dishes that violate restrictions. A vegetarian never sees meat dishes. The LLM only sees pre-validated dishes. This is a hard guarantee, not probabilistic.

### Technical Questions

**Q: "What is RAG?"**
> RAG = Retrieval Augmented Generation. Instead of letting the LLM make up dishes, we:
> 1. RETRIEVE real dishes from our database
> 2. AUGMENT the prompt with that data
> 3. Let the LLM GENERATE a response
> This guarantees recommendations are for actual dishes available today.

**Q: "How do embeddings work?"**
> Embeddings convert text into 384 numbers that capture meaning. Similar meanings become similar vectors. "Garden Salad" and "healthy" are similar even though they share no words. We use cosine similarity to find matches. pgvector handles this efficiently in PostgreSQL.

**Q: "Explain the scoring algorithm."**
> Multi-factor weighted score:
> - 30% feedback (liked similar dishes?)
> - 25% mood (matches mood guidance?)
> - 25% craving (semantic similarity)
> - 10% variety (not recommended recently?)
> - 10% category (preferred categories?)

### Design Questions

**Q: "Why SQL + Vector instead of just vector search?"**
> Pure vector search ignores hard constraints. "Healthy" might return chicken dishes to a vegetarian because chicken is semantically similar to healthy. SQL filters first guarantee safety, then vector search finds relevant options within the safe set.

**Q: "Why not microservices?"**
> For this scale, a monolith is correct. The agents share state (menu data, user context), so separating them adds network overhead without benefits. If scaling to millions of users, I'd extract the embedding service first since it's CPU-intensive.

**Q: "How would you scale this?"**
> 1. Cache menu data (doesn't change intra-day)
> 2. Read replicas for database queries
> 3. Extract embedding service to GPU instances
> 4. CDN for static frontend assets
> 5. Horizontal scaling for FastAPI with load balancer

### Code Quality Questions

**Q: "How do you test this?"**
> - Unit tests (test_agents.py): Test each agent with mock data
> - E2E tests (test_e2e.py): Test full flow with mocked LLM
> - Type checking: TypeScript (frontend), Pydantic (backend)
> - All tests run with pytest

**Q: "What would you improve?"**
> 1. WebSocket for real-time menu updates
> 2. Redis cache for multi-instance deployment
> 3. A/B testing for recommendation algorithms
> 4. Mobile app with React Native
> 5. Collaborative filtering ("users like you also enjoyed...")

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
dish_embeddings  → Vector representations (384-dim)
user_profiles    → Dietary preferences
user_moods       → Current mood state
feedback         → Rating history (likes/dislikes)
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

### Key Files Quick Reference

| Task | File |
|------|------|
| Add API endpoint | backend/main.py |
| Add database query | backend/database.py |
| Change mood mappings | backend/agents/mood_agent.py |
| Modify questions | backend/agents/question_agent.py |
| Adjust scoring weights | backend/agents/scoring.py |
| Change retrieval pipeline | backend/agents/hybrid_retriever.py |
| Add frontend component | frontend/src/components/ |
| Modify API calls | frontend/src/api/client.ts |
| Change global state | frontend/src/context/AppContext.tsx |
