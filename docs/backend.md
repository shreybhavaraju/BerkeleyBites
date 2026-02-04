# Backend Architecture (Beginner-Friendly Guide)

This document explains the backend - the "brain" of BerkeleyBites that runs on a server and does all the heavy lifting.

---

## What is a Backend?

Think of a restaurant:
- **Frontend** = The dining room (what customers see)
- **Backend** = The kitchen (where food is actually made)
- **Database** = The pantry (where ingredients are stored)

The backend is code that runs on a server (not in your browser). It:
- Receives requests from the frontend
- Processes data and runs business logic
- Talks to the database
- Sends responses back

```
User's Browser                    Our Server
┌──────────────┐                 ┌──────────────┐
│   Frontend   │ ───request──▶  │   Backend    │
│   (React)    │ ◀──response─── │   (Python)   │
└──────────────┘                 └──────┬───────┘
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │   Database   │
                                 │  (Supabase)  │
                                 └──────────────┘
```

---

## Technology Stack

| Technology | What It Is | Why We Use It |
|------------|------------|---------------|
| **Python** | Programming language | Great for AI/ML, readable, huge community |
| **FastAPI** | Web framework | Fast, automatic docs, type checking |
| **Uvicorn** | Server software | Runs our Python code, handles connections |
| **Pydantic** | Data validation | Ensures data is correct before using it |
| **Pandas** | Data manipulation | Process menu data efficiently |
| **BeautifulSoup** | HTML parser | Scrape the Berkeley dining website |
| **Supabase SDK** | Database client | Talk to our PostgreSQL database |

---

## What is FastAPI?

FastAPI is a Python **web framework** - a toolkit for building APIs (ways for programs to talk to each other).

### Why FastAPI? (Interview Question!)

| Feature | Benefit | Example |
|---------|---------|---------|
| **Fast** | One of the fastest Python frameworks | Handles thousands of requests/second |
| **Type Hints** | Catches bugs before runtime | `def greet(name: str) -> str` |
| **Auto Documentation** | Free API docs at `/docs` | No manual documentation needed |
| **Async Support** | Handle multiple requests at once | Chat while loading menu |
| **Pydantic Integration** | Automatic request validation | Rejects bad data automatically |

### Basic FastAPI Example

```python
# This is how simple FastAPI is:
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")  # When someone visits /hello
def say_hello():
    return {"message": "Hello, world!"}
```

That `@app.get("/hello")` is called a **decorator** - it "wraps" the function and tells FastAPI "when someone makes a GET request to /hello, run this function."

---

## Project Structure

```
backend/
├── __init__.py           # Makes this folder a Python package
├── main.py               # All API endpoints live here
├── models.py             # Data structures (what data looks like)
├── database.py           # Talks to Supabase

# Related files at repo root:
├── scraper.py            # Gets menu from Berkeley website
└── requirements.txt      # List of Python packages needed
```

### What Each File Does

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | API endpoints | `/api/menu`, `/api/chat`, `/api/profile` |
| `models.py` | Define data shapes | `UserProfile`, `Dish`, `ChatMessage` |
| `database.py` | Database operations | `get_dishes()`, `submit_feedback()` |
| `scraper.py` | Web scraping | `scrape_and_transform()` |

---

## How the Backend Starts

```python
# backend/main.py (simplified)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# Create the FastAPI application
app = FastAPI(
    title="BerkeleyBites API",
    description="Food recommendation API for UC Berkeley dining halls",
    version="1.0.0"
)

# Allow frontend to make requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Our frontend's address
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE
    allow_headers=["*"],  # Allow any headers
)
```

### What is CORS?

**CORS** (Cross-Origin Resource Sharing) is a security feature.

**The Problem:** By default, a website at `localhost:5173` can't make requests to `localhost:8000` - they're different "origins."

**The Solution:** CORS headers tell the browser "it's okay, I trust this other website."

Without CORS configuration, the frontend would get an error like:
```
Access to fetch at 'http://localhost:8000/api/menu' has been blocked by CORS policy
```

---

## Data Models (Pydantic)

**Pydantic** models define what data should look like. Think of them as "contracts" - if data doesn't match, it's rejected.

### Why Use Pydantic?

```python
# WITHOUT Pydantic - dangerous!
def update_profile(data):
    user.age = data["age"]  # What if age is "banana"?

# WITH Pydantic - safe!
class UserProfile(BaseModel):
    age: int  # Must be integer

def update_profile(profile: UserProfile):
    user.age = profile.age  # Guaranteed to be an integer
```

### Our Key Models

```python
# backend/models.py

from pydantic import BaseModel

class UserProfile(BaseModel):
    """What a user's preferences look like."""

    # Dietary preferences (True/False)
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_pescatarian: bool = False
    is_halal: bool = False
    is_kosher: bool = False

    # Allergens to avoid (True/False)
    avoid_milk: bool = False
    avoid_eggs: bool = False
    avoid_gluten: bool = False
    avoid_nuts: bool = False
    avoid_soy: bool = False

    # Other
    prefer_low_carbon: bool = False


class Dish(BaseModel):
    """What a menu item looks like."""

    dish_id: int
    dish_name: str
    dining_hall: str
    dining_hall_status: str    # "Open" or "Closed"
    meal_period: str           # "Breakfast", "Lunch", "Dinner"
    category: str              # "Entrees", "Soups", etc.

    # Allergen flags
    has_milk: bool = False
    has_egg: bool = False
    has_gluten: bool = False
    # ... more allergens

    # Dietary flags
    is_vegan: bool = False
    is_vegetarian: bool = False
    # ... more dietary flags

    scrape_date: str  # When we got this data


class ChatMessage(BaseModel):
    """What a chat message from the frontend looks like."""
    message: str
    session_id: str
```

---

## API Endpoints Explained

### What is an Endpoint?

An **endpoint** is a specific URL that does something. Like different counters at a post office:
- Counter 1: Send packages (POST /send)
- Counter 2: Pick up packages (GET /pickup)
- Counter 3: Return packages (DELETE /return)

### Our Endpoints Overview

| Method | Endpoint | What It Does |
|--------|----------|--------------|
| GET | `/api/health` | Check if server is running |
| GET | `/api/menu` | Get today's dishes |
| GET | `/api/profile` | Get user preferences |
| PUT | `/api/profile` | Update user preferences |
| POST | `/api/feedback` | Submit a dish rating |
| POST | `/api/chat` | Send a chat message |

### Detailed Endpoint Examples

#### GET `/api/menu` - Fetch Menu Items

```python
@app.get("/api/menu", response_model=list[Dish])
async def get_menu(
    user_id: str = Query(..., description="User session ID"),  # Required
    hall: str = Query("", description="Filter by dining hall"),  # Optional
    meal: str = Query("", description="Filter by meal period"),  # Optional
):
    """
    Get menu items filtered by user's dietary restrictions.

    Example: GET /api/menu?user_id=abc123&meal=Lunch
    Returns: List of Dish objects the user can eat
    """
    # 1. Get user's dietary restrictions
    profile = get_user_profile(user_id)

    # 2. Load today's menu
    menu_df = load_menu_data()

    # 3. Apply user's filters (hall, meal)
    if hall:
        menu_df = menu_df[menu_df['dining_hall'] == hall]
    if meal:
        menu_df = menu_df[menu_df['meal_period'] == meal]

    # 4. Filter out dishes that violate dietary restrictions
    if profile.is_vegan:
        menu_df = menu_df[menu_df['is_vegan'] == True]
    if profile.avoid_gluten:
        menu_df = menu_df[menu_df['has_gluten'] == False]

    # 5. Return the filtered dishes
    return [Dish(**row) for row in menu_df.to_dict('records')]
```

**Key Concepts:**
- `@app.get(...)` = This function handles GET requests
- `Query(...)` = Get value from URL query string
- `response_model=list[Dish]` = Return type validation
- `async def` = This function can run asynchronously

#### POST `/api/chat` - Main Chat Handler

This is the most complex endpoint - it handles the entire recommendation flow:

```python
@app.post("/api/chat")
async def chat(
    message: ChatMessage,  # Request body (JSON)
    user_id: str = Query(...)  # From URL
):
    """
    Handle chat messages. Three cases:
    1. "/recommend" - Start recommendation flow
    2. "answer:question_id:value" - Answer a question
    3. Anything else - General chat response
    """

    # Case 1: Start recommendation
    if message.message == "/recommend":
        # Return first question
        return QuestionResponse(
            question_id="mood",
            question_text="How are you feeling right now?",
            options=[
                {"value": "happy", "label": "Happy", "emoji": "😊"},
                {"value": "stressed", "label": "Stressed", "emoji": "😤"},
                # ... more options
            ],
            session_id=message.session_id
        )

    # Case 2: Answer a question
    if message.message.startswith("answer:"):
        # Parse: "answer:mood:happy" -> question_id="mood", value="happy"
        parts = message.message.split(":")
        question_id = parts[1]
        value = parts[2]

        # Store answer, check if all questions answered
        # If yes, generate recommendation
        # If no, return next question
        ...

    # Case 3: General message
    return ChatResponse(
        response="Try '/recommend' for personalized suggestions!",
        session_id=message.session_id
    )
```

---

## The Web Scraper

### What is Web Scraping?

**Web scraping** = Automatically extracting data from websites.

We scrape the UC Berkeley dining website daily to get the current menu.

```python
# scraper.py (simplified)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date

def scrape_and_transform():
    """
    1. Fetch the dining website HTML
    2. Parse it to find dish information
    3. Return a pandas DataFrame
    """

    # Step 1: Get the webpage
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url, timeout=30)
    html = response.text

    # Step 2: Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Step 3: Find all menu items
    rows = []
    for item in soup.find_all('div', class_='menu-item'):
        rows.append({
            "dish_name": item.find('h3').text,
            "dining_hall": item.find('.hall').text,
            "has_milk": "milk" in item.get('data-allergens', ''),
            "is_vegetarian": 'vegetarian' in item.get('data-flags', ''),
            # ... extract more data
            "scrape_date": str(date.today())
        })

    # Step 4: Return as DataFrame
    return pd.DataFrame(rows)
```

### Why Pandas?

**Pandas** is a Python library for data manipulation. A DataFrame is like a spreadsheet in code.

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame([
    {"name": "Pasta", "is_vegan": False},
    {"name": "Salad", "is_vegan": True},
])

# Filter (like Excel filter)
vegan_dishes = df[df['is_vegan'] == True]

# This is MUCH faster than:
vegan_dishes = [d for d in dishes if d['is_vegan'] == True]
```

---

## Error Handling

### HTTPException Pattern

When something goes wrong, we return proper HTTP error codes:

```python
from fastapi import HTTPException

@app.get("/api/profile")
async def get_profile(user_id: str = Query(...)):
    # Validate input
    if not user_id:
        raise HTTPException(
            status_code=400,  # "Bad Request"
            detail="user_id is required"
        )

    try:
        profile = db.get_user_profile(user_id)
        return profile or UserProfile()  # Return default if not found
    except Exception as e:
        raise HTTPException(
            status_code=500,  # "Internal Server Error"
            detail=f"Database error: {str(e)}"
        )
```

### HTTP Status Codes (Know These!)

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Client sent invalid data |
| 401 | Unauthorized | Not logged in |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Server crashed |
| 503 | Service Unavailable | External service down |

### Graceful Degradation

When external services fail, we don't crash - we use fallbacks:

```python
def get_menu_data():
    try:
        # Try the database
        return supabase.table("dishes").select("*").execute()
    except Exception as e:
        # Log the error
        logger.error(f"Database query failed: {e}")
        # Return fallback data from CSV
        return pd.read_csv("dining_data_clean.csv")
```

---

## Logging

Logging helps us understand what's happening and debug issues:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Use in code
@app.get("/api/menu")
async def get_menu(user_id: str):
    logger.info(f"Fetching menu for user: {user_id}")  # Info: normal operation
    try:
        dishes = load_menu_data()
        logger.info(f"Loaded {len(dishes)} dishes")
        return dishes
    except Exception as e:
        logger.error(f"Menu fetch failed: {e}")  # Error: something wrong
        raise HTTPException(status_code=503, detail="Menu unavailable")
```

**Log Levels:**
| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed info for debugging |
| INFO | Normal operations |
| WARNING | Something unexpected but not broken |
| ERROR | Something failed |
| CRITICAL | System is broken |

---

## Running the Backend

### Development Mode

```bash
# From the repo root
cd backend
uvicorn main:app --reload --port 8000
```

**Flags:**
- `main:app` = "In main.py, use the `app` variable"
- `--reload` = Restart when code changes (development only!)
- `--port 8000` = Run on port 8000

### Environment Variables

Create a `.env` file with secrets (never commit this!):

```bash
# .env
PERPLEXITY_API_KEY=sk_xxx...
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=eyJhbGc...
USE_SUPABASE=true
```

### Auto-Generated Documentation

FastAPI automatically creates interactive API docs:

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI (try API calls!) |
| http://localhost:8000/redoc | ReDoc (prettier docs) |
| http://localhost:8000/openapi.json | Raw API specification |

---

## Design Choices & Why

### Why Python for Backend?

| Reason | Explanation |
|--------|-------------|
| **AI/ML ecosystem** | Best libraries for AI (LangChain, transformers) |
| **Readability** | Easy to understand and maintain |
| **FastAPI** | Modern, fast, great documentation |
| **Team familiarity** | Common first language for students |

### Why Not Node.js?

Node.js would work, but:
- AI/ML libraries are better in Python
- LangChain (our AI framework) is Python-native
- Async in Python is similar to Node.js now

### Why Separate Backend from Frontend?

| Benefit | Explanation |
|---------|-------------|
| **Separation of concerns** | Each part has one job |
| **Independent scaling** | Scale backend without touching frontend |
| **Different languages** | Use best tool for each job |
| **Team parallelism** | Different people can work on each |
| **Testability** | Test API without UI, test UI without API |

---

## Potential Improvements

### Current Limitations

1. **No authentication** - Anyone with user_id can access data
2. **In-memory caching** - Lost on server restart
3. **Single server** - Can't handle massive traffic
4. **No rate limiting** - Someone could spam the API

### Future Improvements

```python
# 1. Add authentication (JWT tokens)
from fastapi_jwt_auth import AuthJWT

@app.get("/api/profile")
def get_profile(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()  # Must be logged in
    user_id = Authorize.get_jwt_subject()
    ...

# 2. Add Redis caching (distributed, persistent)
import redis
cache = redis.Redis(host='localhost', port=6379)
cache.set("menu:today", json.dumps(dishes), ex=86400)  # 24hr TTL

# 3. Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/chat")
@limiter.limit("30/minute")  # Max 30 requests per minute
async def chat(...):
    ...
```

---

## Summary

| Concept | What It Is |
|---------|------------|
| **Backend** | Server-side code that processes requests |
| **FastAPI** | Python framework for building APIs |
| **Endpoint** | A URL that does something specific |
| **Pydantic** | Library for data validation |
| **CORS** | Security feature allowing cross-origin requests |
| **Scraping** | Automatically extracting data from websites |
| **Logging** | Recording what happens for debugging |
| **HTTPException** | How to return error responses |

**Key Files:**
- `backend/main.py` - All API endpoints
- `backend/models.py` - Data structures
- `backend/database.py` - Database operations
- `scraper.py` - Menu scraping logic
