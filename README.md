# BerkeleyBites

A personalized food recommendation system for UC Berkeley dining halls. Scrapes the campus dining menus daily, learns your taste in a 4-question flow, and ranks dishes using a 4-stage hybrid RAG pipeline.

## What it does

Pick a meal (breakfast / lunch / dinner / late night), answer four short questions — mood, craving, cuisine vibe, and dietary fit — and BerkeleyBites returns the top dishes from across the dining halls ranked by your current preferences. Dietary preferences (vegan, gluten-free, etc.) persist across sessions and act as hard filters.

## Architecture

High-level data flow:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  scraper.py      │ ──▶ │  Supabase        │ ──▶ │  FastAPI backend │
│  (daily)         │     │  (PostgreSQL)    │     │  + agent layer   │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  React frontend  │
                                                  │  (TypeScript)    │
                                                  └──────────────────┘
```

### The recommendation engine: 4-stage hybrid RAG

The core isn't "wrap an LLM" — it's a 4-stage pipeline that uses cheap deterministic operations to do the heavy lifting and only calls the LLM at the end on a small pre-scored candidate set. Total budget: ~530ms per recommendation, one LLM call.

```
User context (mood, craving, spice, time, dietary profile)
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 1 — SQL hard filters (~5ms, no AI cost)                       │
│   • Deterministic dietary safety. Vegan never sees meat, period.    │
│   • 245 dishes → ~180 dietary-safe candidates                       │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 2 — Vector similarity (~15ms, no AI cost)                     │
│   • Query embedding from (mood + craving + meal)                    │
│   • pgvector cosine similarity over the dietary-safe set            │
│   • ~180 → top 30 semantically similar dishes                       │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 3 — Multi-factor scoring (~10ms, no AI cost)                  │
│   total = taste(35%) + craving(28%) + mood(17%)                     │
│         + category(10%) + embedding(5%)                             │
│         + novelty_bonus − dislike_penalty                           │
│   • 100% deterministic and debuggable                               │
│   • 30 dishes → top 8 by total score                                │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 4 — LLM final selection (~500ms, 1 API call)                  │
│   • LLM only sees the top 8 pre-scored dishes                       │
│   • Picks 3–4 diverse final dishes, writes explanations             │
│   • Can't hallucinate — the dish set is closed                      │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
Final: 3–4 recommendations with personalized explanations
```

**Why this design** (and not a single LLM call):
- A pure LLM wouldn't know today's menu → hallucinated dishes
- A pure LLM can't *guarantee* dietary safety → dangerous for vegan/allergic users
- Every request becoming an API call → slow, expensive, hard to debug
- The hybrid approach moves cheap, safety-critical work into deterministic code and uses the LLM only where it earns its cost: final diversity + natural-language explanations

### Scoring weights

`backend/agents/scoring.py`. Weighted sum of six signals. Weights are chosen so taste (your rating history) is the dominant driver, with current mood/craving as modulators:

| Component | Weight | Source |
|---|---|---|
| Taste score | 35% | Has the user liked/disliked this dish before? |
| Craving score | 28% | Does dish match the "healthy" / "comfort" / etc. craving? |
| Mood score | 17% | Mood→food mapping (stressed → light/fresh, etc.) |
| Category score | 10% | User's history with this dish's category |
| Embedding score | 5% | Stage 2 similarity passed through |
| Novelty bonus | +5% | Dish user hasn't tried yet |
| Dislike penalty | −30% | Hard penalty on explicit dislikes |

Concrete example — scoring a *Garden Salad* for a stressed user who wants healthy food:
- Taste: never rated → 0.50 (neutral)
- Craving: "salad" in `CRAVING_KEYWORDS["healthy"]["high"]` → 1.00
- Mood: salad category in `MOOD_FOOD_MAPPING["stressed"]` → 0.60
- Category: liked 5 salads, disliked 0 → 1.00
- Embedding similarity from Stage 2 → 0.87
- Novelty bonus: new dish → +0.05
- Final: 0.5×0.35 + 1.0×0.28 + 0.6×0.17 + 1.0×0.10 + 0.87×0.05 + 0.05 = **0.75**

### Agent layer (`backend/agents/`)

- **orchestrator** — runs the question loop, calls the retriever, returns ranked dishes
- **question_agent** — manages the 4-question preference flow
- **hybrid_retriever** — the 4-stage pipeline above
- **scoring** — the weighted scoring above
- **embedding_service** — local 384-dim vectors via `all-MiniLM-L6-v2` (CPU, no embedding API costs)
- **cache** — in-memory cache for embeddings and recent recommendations

Full step-by-step request trace, file reference, and database schema live in [`docs/architecture.md`](docs/architecture.md).

## Tech stack

- **Backend:** Python, FastAPI, Supabase (PostgreSQL with pgvector), LangChain, Perplexity API, sentence-transformers
- **Frontend:** React 19, TypeScript, Vite, Tailwind v4
- **Scraping:** BeautifulSoup4

## Running it

Requires Python 3.10+, Node 20+, and a local Supabase setup.

**Backend**
```bash
pip install -r requirements.txt
cp .env.example .env          # fill in PERPLEXITY_API_KEY and SUPABASE_* values
supabase start                # or point at a hosted Supabase project
python scraper.py             # one-time menu pull
uvicorn backend.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Or use the helper scripts in `scripts/` (`start.sh`, `status.sh`, `stop.sh`) to bring up the whole stack at once.

## Status

Personal project, not currently deployed. The scraper, RAG pipeline, scoring, and chat UI all work end-to-end locally. A small test suite in `tests/` covers the agent layer.
