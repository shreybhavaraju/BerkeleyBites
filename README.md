# BerkeleyBites

A personalized food recommendation system for UC Berkeley dining halls. Scrapes the campus dining menus daily, learns your taste in a 4-question flow, and ranks dishes using a multi-agent RAG pipeline.

## What it does

Pick a meal (breakfast / lunch / dinner / late night), answer four short questions — mood, craving, cuisine vibe, and dietary fit — and BerkeleyBites returns the top dishes from across the dining halls ranked by your current preferences. Dietary preferences (vegan, gluten-free, etc.) persist across sessions and act as hard filters.

## Architecture

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

Backend agent layer (in `backend/agents/`):

- **orchestrator** — runs the question loop, calls the retriever, returns ranked dishes
- **question_agent** — manages the 4-question preference flow
- **hybrid_retriever** — 4-stage retrieval: dietary filter → semantic search → reranking → scoring
- **scoring** — multi-factor scoring weighted by mood and craving signals
- **embedding_service** — local 384-dim vectors via `all-MiniLM-L6-v2` (no embedding API costs)
- **cache** — in-memory cache for embeddings and recent recommendations

Full design doc with request flow, file reference, and schema: [`docs/architecture.md`](docs/architecture.md).

## Tech stack

- **Backend:** Python, FastAPI, Supabase (PostgreSQL), LangChain, Perplexity API, sentence-transformers
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

## Notable design choices

- **Embeddings stay local.** `all-MiniLM-L6-v2` runs on CPU; no embedding API costs or latency.
- **Dietary filters are hard, not soft.** Vegan/gluten-free constraints filter the candidate set *before* scoring — never just downranked.
- **Mood and craving are weights, not filters.** The same dish can be the top pick when you're stressed and a mid pick when you're energetic.
