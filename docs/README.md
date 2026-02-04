# BerkeleyBites Documentation

## For Your Interview Tomorrow

**Start here:** [Interview Prep Guide](./interview-prep.md)

This single document contains EVERYTHING you need:
- Part 1: Absolute basics (what is a web app, frontend, backend, API, database)
- Part 2: Technologies explained (React, TypeScript, Python, FastAPI, Supabase)
- Part 3: How BerkeleyBites works (step-by-step with diagrams)
- Part 4: Every possible interview question with answers
- Part 5: Quick reference cheat sheet

---

## What is BerkeleyBites?

A web app that helps UC Berkeley students decide what to eat. Instead of scrolling through menus, users answer 4 questions and get personalized food recommendations.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HOW IT WORKS                                    │
└─────────────────────────────────────────────────────────────────────────┘

   USER                          APP                           AI SYSTEM
     │                            │                                │
     │  "I'm happy, want          │                                │
     │   healthy food"            │                                │
     │ ──────────────────────────►│                                │
     │                            │  Asks 4 questions              │
     │                            │  (mood, craving, spice, time)  │
     │                            │                                │
     │                            │  Collects answers              │
     │                            │ ──────────────────────────────►│
     │                            │                                │
     │                            │                                │ Mood Agent
     │                            │                                │ Taste Agent
     │                            │                                │ Food Agent
     │                            │                                │ Scoring
     │                            │                                │ LLM
     │                            │                                │
     │                            │◄───────────────────────────────│
     │                            │  "Try the Teriyaki Chicken     │
     │◄───────────────────────────│   Bowl!"                       │
     │                            │                                │
     │  Sees recommendation!      │                                │
     │                            │                                │
```

---

## Tech Stack (Quick Reference)

| What | Technology | Why |
|------|------------|-----|
| Frontend | React + TypeScript | Interactive UI, type safety |
| Styling | Tailwind CSS | Fast, utility-based |
| Backend | Python + FastAPI | Fast, AI-friendly |
| Database | Supabase (PostgreSQL) | Managed, powerful |
| AI | Perplexity LLM | Cost-effective recommendations |
| Embeddings | all-MiniLM-L6-v2 | Semantic search |

---

## Project Structure

```
BerkeleyBites/
├── frontend/          # React app (what users see)
│   └── src/
│       ├── components/  # UI pieces (ChatPanel, DishCard, etc.)
│       ├── api/         # Talks to backend
│       └── context/     # Shared state
│
├── backend/           # FastAPI server (processes requests)
│   ├── main.py        # API endpoints
│   └── database.py    # Database operations
│
├── agents/            # AI recommendation system
│   ├── orchestrator.py      # Coordinates everything
│   ├── mood_agent.py        # Maps mood to food guidance
│   ├── question_agent.py    # Handles the 4 questions
│   ├── taste_preferences_agent.py  # Analyzes past likes
│   ├── food_availability_agent.py  # Gets available dishes
│   ├── hybrid_retriever.py  # 4-stage ranking pipeline
│   └── scoring.py           # Multi-factor scoring
│
├── scraper.py         # Gets menu from Berkeley website
└── docs/              # You are here!
```

---

## The AI System (Key Differentiator)

What makes this project interesting is the **multi-agent architecture**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Instead of ONE big AI prompt, we use SPECIALIZED AGENTS:              │
│                                                                         │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│   │ Mood Agent   │  │ Taste Agent  │  │ Food Agent   │                 │
│   │              │  │              │  │              │                 │
│   │ "Happy =     │  │ "User likes  │  │ "15 dishes   │                 │
│   │  adventurous │  │  Asian food" │  │  available"  │                 │
│   │  foods OK"   │  │              │  │              │                 │
│   └──────────────┘  └──────────────┘  └──────────────┘                 │
│          │                 │                 │                          │
│          └─────────────────┴─────────────────┘                          │
│                            │                                            │
│                            ▼                                            │
│                   ┌──────────────────┐                                  │
│                   │ Hybrid Retriever │                                  │
│                   │                  │                                  │
│                   │ 1. SQL filters   │                                  │
│                   │ 2. Vector search │                                  │
│                   │ 3. Scoring       │                                  │
│                   │ 4. LLM writes    │                                  │
│                   └──────────────────┘                                  │
│                            │                                            │
│                            ▼                                            │
│                   "I recommend the Teriyaki Chicken Bowl!"              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Other Documentation

| Document | What It Covers |
|----------|----------------|
| [Interview Prep](./interview-prep.md) | **START HERE** - Complete guide with Q&A |
| [Glossary](./glossary.md) | All technical terms defined |
| [Architecture](./architecture.md) | System design details |
| [Backend](./backend.md) | API and server details |
| [Database](./database.md) | Tables and queries |
| [Agents](./agents.md) | AI system deep dive |
| [API Reference](./api-reference.md) | All endpoints |
| [Data Flow](./data-flow.md) | How data moves through the system |

---

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start the app
# Terminal 1:
uvicorn backend.main:app --reload --port 8000

# Terminal 2:
cd frontend && npm run dev

# 4. Open http://localhost:5173
```

---

**Good luck with your interview! Read the [Interview Prep Guide](./interview-prep.md) first!**
