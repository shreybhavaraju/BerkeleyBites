# BerkeleyBites Documentation

## What is This Project?

**BerkeleyBites** is a web application that helps UC Berkeley students decide what to eat at campus dining halls. Instead of scrolling through menus, users answer a few questions and get personalized food recommendations based on:

- Their dietary restrictions (vegan, vegetarian, allergies, etc.)
- Their current mood (happy, stressed, tired)
- What kind of food they're craving
- Foods they've liked or disliked before

---

## Understanding Full-Stack Development (For Beginners)

### What is "Full-Stack"?

A "full-stack" application has two main parts:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                  │
│                                                              │
│   What users see and interact with in their browser         │
│   (buttons, forms, text, images)                            │
│                                                              │
│   Technologies: React, HTML, CSS, JavaScript                │
└─────────────────────────────────────────────────────────────┘
                           ↕
               (They communicate via "APIs")
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND                                   │
│                                                              │
│   The "brain" - processes requests, talks to databases,     │
│   runs AI models, handles business logic                    │
│                                                              │
│   Technologies: Python, FastAPI, databases                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Terms You'll See

| Term | Simple Explanation |
|------|-------------------|
| **API** | A way for programs to talk to each other. Like a waiter taking orders between customers (frontend) and the kitchen (backend) |
| **Endpoint** | A specific URL that does something. `/api/menu` gets the menu, `/api/profile` gets user settings |
| **Database** | Where data is stored permanently (like a filing cabinet) |
| **Component** | A reusable piece of UI (like a "DishCard" that shows one food item) |
| **State** | Data that can change (like "is the menu loading?" or "what's the user's mood?") |
| **REST API** | A common way to design APIs using HTTP methods (GET = read, POST = create, PUT = update) |

---

## Documentation Index

| Document | What You'll Learn |
|----------|-------------------|
| [Glossary](./glossary.md) | **START HERE** - All technical terms explained simply |
| [Architecture](./architecture.md) | How all the pieces connect together |
| [Frontend](./frontend.md) | The user interface (React, what users see) |
| [Backend](./backend.md) | The server (FastAPI, Python, business logic) |
| [Agents](./agents.md) | The AI system that makes recommendations |
| [Database](./database.md) | How data is stored and retrieved |
| [API Reference](./api-reference.md) | Every endpoint and what it does |
| [Data Flow](./data-flow.md) | Visual diagrams of how data moves |
| [Interview Prep](./interview-prep.md) | Questions you might be asked |

---

## The Big Picture

Here's how BerkeleyBites works at the highest level:

```
USER                         BROWSER                      SERVER                    DATABASE
  │                             │                            │                          │
  │  Opens berkeleybites.com    │                            │                          │
  │ ──────────────────────────► │                            │                          │
  │                             │                            │                          │
  │                             │  "Give me today's menu"    │                          │
  │                             │ ─────────────────────────► │                          │
  │                             │                            │                          │
  │                             │                            │  "Get dishes for today"  │
  │                             │                            │ ───────────────────────► │
  │                             │                            │                          │
  │                             │                            │  ◄─── [dish1, dish2...]  │
  │                             │                            │                          │
  │                             │ ◄─── [formatted dishes]    │                          │
  │                             │                            │                          │
  │  ◄─── Sees menu on screen   │                            │                          │
  │                             │                            │                          │
  │  Clicks "Get Recommendation"│                            │                          │
  │ ──────────────────────────► │                            │                          │
  │                             │                            │                          │
  │                             │  "Run AI recommendation"   │                          │
  │                             │ ─────────────────────────► │                          │
  │                             │                            │                          │
  │                             │                            │   [AI Agents Process]    │
  │                             │                            │   - Check mood           │
  │                             │                            │   - Check cravings       │
  │                             │                            │   - Check past likes     │
  │                             │                            │   - Score all dishes     │
  │                             │                            │   - Pick best matches    │
  │                             │                            │                          │
  │                             │ ◄─── "Try the Teriyaki     │                          │
  │                             │       Chicken Bowl!"       │                          │
  │                             │                            │                          │
  │  ◄─── Sees recommendation   │                            │                          │
```

---

## Project Structure (What's in Each Folder)

```
BerkeleyBites/
│
├── frontend/                 # What users see (React app)
│   ├── src/
│   │   ├── App.tsx          # Main application file
│   │   ├── components/      # Reusable UI pieces
│   │   ├── api/             # Code that talks to backend
│   │   └── context/         # Shared application state
│   └── package.json         # Frontend dependencies
│
├── backend/                  # The server (FastAPI)
│   ├── main.py              # All API endpoints
│   ├── models.py            # Data structure definitions
│   └── database.py          # Database connection code
│
├── agents/                   # AI recommendation system
│   ├── orchestrator.py      # Coordinates all agents
│   ├── mood_agent.py        # Mood-based suggestions
│   ├── question_agent.py    # Manages question flow
│   ├── hybrid_retriever.py  # Smart dish selection
│   ├── scoring.py           # How dishes are ranked
│   ├── embedding_service.py # Semantic understanding
│   └── cache.py             # Speed optimization
│
├── supabase/                 # Database configuration
│   └── migrations/          # Database structure changes
│
├── scraper.py               # Gets menu from UC Berkeley website
├── requirements.txt         # Python packages needed
└── docs/                    # This documentation
```

---

## Quick Start (Running the App)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Perplexity API key (for AI recommendations)

### Step 1: Install Dependencies

```bash
# Backend (Python packages)
pip install -r requirements.txt

# Frontend (JavaScript packages)
cd frontend
npm install
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your keys:
# PERPLEXITY_API_KEY=your_key_here
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key
```

### Step 3: Start the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Step 4: Open in Browser

Go to `http://localhost:5173`

---

## Why This Architecture?

### Why separate Frontend and Backend?

1. **Specialization**: Different tools for different jobs
   - React is great for building UIs
   - Python is great for AI/ML and data processing

2. **Scalability**: Can upgrade one without breaking the other

3. **Team collaboration**: Frontend and backend developers can work independently

### Why use AI Agents?

Instead of one big AI prompt, we use specialized "agents":

| Agent | Job | Why Separate? |
|-------|-----|---------------|
| Mood Agent | Understand emotions → food | Simple mapping, no AI needed |
| Question Agent | Gather user preferences | Manages conversation flow |
| Food Agent | Query available dishes | Database operation |
| Taste Agent | Analyze past preferences | Data analysis |

**Benefits**:
- Each agent is simple and testable
- If one fails, others still work
- Easy to add new agents

### Why use a Database?

Without a database, data disappears when the server restarts. The database:
- Stores menu items (updated daily)
- Remembers user preferences
- Tracks what users liked/disliked
- Enables learning from feedback

---

## Next Steps

1. **Start with [Glossary](./glossary.md)** - Learn the terms
2. **Read [Architecture](./architecture.md)** - Understand the big picture
3. **Explore [Agents](./agents.md)** - The most interesting part
4. **Review [Interview Prep](./interview-prep.md)** - Practice explaining it

Good luck with your interview!
