# API Reference (Beginner-Friendly Guide)

This document explains all the API endpoints in BerkeleyBites - the "contracts" between frontend and backend.

---

## What is an API?

**API** = Application Programming Interface

It's how different programs talk to each other. Think of it like a restaurant:

```
You (Frontend)              Waiter (API)              Kitchen (Backend)
     │                          │                           │
     │──"I want pasta"─────────▶│                           │
     │                          │──"Order: pasta"──────────▶│
     │                          │                           │ (makes pasta)
     │                          │◀──"Here's the pasta"──────│
     │◀──"Your pasta, sir"──────│                           │
     │                          │                           │
```

The API is the **messenger** that carries requests and responses between frontend and backend.

---

## How APIs Work (HTTP Basics)

### HTTP Methods

| Method | Purpose | Like In Real Life |
|--------|---------|-------------------|
| **GET** | Read data | "Show me the menu" |
| **POST** | Create data | "I'd like to order this" |
| **PUT** | Update data | "Change my order to..." |
| **DELETE** | Remove data | "Cancel my order" |

### Request Structure

```
GET /api/menu?user_id=abc123&meal=Lunch HTTP/1.1
│   │         └─────────────┬─────────┘
│   │               Query Parameters
│   └── Path (which endpoint)
└── Method (what action)

Headers:
Content-Type: application/json

Body (for POST/PUT):
{"dish_id": 42, "liked": true}
```

### Response Structure

```
HTTP/1.1 200 OK
│        └── Status Code (success/failure)
└── Protocol version

Headers:
Content-Type: application/json

Body:
{"dish_name": "Pasta", "dining_hall": "Commons"}
```

---

## Status Codes (Know These!)

| Code | Name | Meaning | Example |
|------|------|---------|---------|
| **200** | OK | Success | "Here's your data" |
| **201** | Created | New resource created | "Your rating was saved" |
| **400** | Bad Request | You sent invalid data | "meal must be Lunch/Dinner" |
| **401** | Unauthorized | Not logged in | "Please log in first" |
| **404** | Not Found | Resource doesn't exist | "That dish doesn't exist" |
| **422** | Unprocessable | Validation failed | "dish_id must be a number" |
| **500** | Server Error | Something broke | "Our bad, try again" |
| **503** | Unavailable | Service is down | "Database unavailable" |

---

## Base URLs

```
Development: http://localhost:8000/api
Production:  https://your-domain.com/api
```

All endpoints are prefixed with `/api`.

---

## Authentication (Current System)

**Current approach:** Session-based identification using `user_id`
- All requests require `user_id` query parameter
- User ID is generated client-side (in browser)
- Stored in localStorage for persistence
- No passwords or tokens (yet)

```
Every request looks like:
GET /api/menu?user_id=user_abc123
                      └─────────┘
                   Required for all endpoints
```

---

## Endpoints Reference

### Health Check

#### GET `/api/health`

Check if the API is running and menu data is loaded.

**Why it exists:** Load balancers and monitoring tools ping this to know if the server is healthy.

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "date": "2026-02-03",
  "menu_loaded": true,
  "dish_count": 245
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "healthy" or error message |
| `date` | string | Today's date |
| `menu_loaded` | boolean | Is menu data available? |
| `dish_count` | integer | How many dishes today |

---

### Menu Endpoints

#### GET `/api/menu`

Get menu items filtered by user's dietary restrictions and optional filters.

**Request:**
```bash
curl "http://localhost:8000/api/menu?user_id=abc123&meal=Lunch&hall=Dining%20Commons"
```

**Query Parameters:**

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `user_id` | Yes | string | User session ID |
| `hall` | No | string | Filter by dining hall |
| `meal` | No | string | "Breakfast", "Lunch", or "Dinner" |
| `category` | No | string | "Entrees", "Soups", etc. |

**Response:**
```json
[
  {
    "dish_id": 42,
    "dish_name": "Teriyaki Chicken Bowl",
    "dining_hall": "Dining Commons",
    "dining_hall_status": "Open",
    "meal_period": "Lunch",
    "category": "Entrees",
    "has_milk": false,
    "has_egg": false,
    "has_gluten": true,
    "is_vegan": false,
    "is_vegetarian": false,
    "scrape_date": "2026-02-03"
  }
]
```

**What the backend does:**
1. Load user's dietary profile
2. Load today's menu
3. Apply hall/meal/category filters
4. Remove dishes that violate user's restrictions
5. Return filtered list

---

#### GET `/api/menu/summary`

Get statistics about today's menu (no user_id needed).

**Request:**
```bash
curl http://localhost:8000/api/menu/summary
```

**Response:**
```json
{
  "total_dishes": 245,
  "dining_halls": ["Dining Commons", "Café Strada", "Crossroads"],
  "meal_periods": ["Breakfast", "Lunch", "Dinner"],
  "categories": ["Entrees", "Soups", "Salads", "Sides"],
  "vegan_count": 45,
  "vegetarian_count": 120,
  "halal_count": 30
}
```

---

#### POST `/api/menu/refresh`

Trigger a fresh scrape of the Berkeley dining website.

**When to use:** Menu data is stale or missing.

**Request:**
```bash
curl -X POST http://localhost:8000/api/menu/refresh
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Menu scraped and updated. Loaded 245 dishes."
}
```

**Response (Error):**
```json
{
  "detail": "Failed to scrape menu: Connection timeout"
}
```

---

### Profile Endpoints

#### GET `/api/profile`

Get user's dietary preferences.

**Request:**
```bash
curl "http://localhost:8000/api/profile?user_id=abc123"
```

**Response:**
```json
{
  "is_vegetarian": true,
  "is_vegan": false,
  "is_pescatarian": false,
  "is_halal": false,
  "is_kosher": false,
  "avoid_milk": false,
  "avoid_eggs": false,
  "avoid_gluten": true,
  "avoid_nuts": true,
  "avoid_soy": false,
  "prefer_low_carbon": false
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `is_vegetarian` | boolean | No meat (dairy/eggs OK) |
| `is_vegan` | boolean | No animal products at all |
| `is_pescatarian` | boolean | Fish OK, no other meat |
| `is_halal` | boolean | Islamic dietary laws |
| `is_kosher` | boolean | Jewish dietary laws |
| `avoid_*` | boolean | Allergy or intolerance |
| `prefer_low_carbon` | boolean | Sustainability preference |

---

#### PUT `/api/profile`

Update user's dietary preferences.

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/profile?user_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "is_vegetarian": true,
    "avoid_gluten": true,
    "avoid_nuts": true
  }'
```

**Response:** Returns the updated profile (same format as GET).

---

#### GET `/api/profile/mood`

Get user's current mood and available options.

**Request:**
```bash
curl "http://localhost:8000/api/profile/mood?user_id=abc123"
```

**Response:**
```json
{
  "current_mood": "happy",
  "available_moods": [
    {"value": "happy", "label": "Happy", "emoji": "😊"},
    {"value": "stressed", "label": "Stressed", "emoji": "😤"},
    {"value": "tired", "label": "Tired", "emoji": "😴"},
    {"value": "adventurous", "label": "Adventurous", "emoji": "🤠"},
    {"value": "grumpy", "label": "Grumpy", "emoji": "😠"}
  ]
}
```

---

#### PUT `/api/profile/mood`

Update user's current mood.

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/profile/mood?user_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{"mood": "stressed"}'
```

**Response:**
```json
{
  "mood": "stressed",
  "description": "Feeling anxious or overwhelmed",
  "food_suggestion": "Choose simple, easy-to-eat comfort foods."
}
```

---

### Feedback Endpoints

#### POST `/api/feedback`

Submit a like/dislike rating for a dish.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/feedback?user_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "dish_id": 42,
    "dish_name": "Teriyaki Chicken Bowl",
    "liked": true
  }'
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `dish_id` | Yes | integer | Dish database ID |
| `dish_name` | Yes | string | Dish name (for display) |
| `liked` | Yes | boolean | true = 👍, false = 👎 |

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded"
}
```

---

#### GET `/api/feedback/stats`

Get aggregated feedback statistics.

**Request:**
```bash
curl "http://localhost:8000/api/feedback/stats?user_id=abc123"
```

**Response:**
```json
{
  "total_ratings": 24,
  "liked_count": 18,
  "disliked_count": 6,
  "today_ratings": 3,
  "like_percentage": 75.0
}
```

---

#### GET `/api/feedback/{dish_id}`

Get user's rating for a specific dish.

**Request:**
```bash
curl "http://localhost:8000/api/feedback/42?user_id=abc123"
```

**Response (Has rated):**
```json
{
  "dish_id": 42,
  "dish_name": "Teriyaki Chicken Bowl",
  "liked": true,
  "rating_date": "2026-02-03"
}
```

**Response (Not rated):**
```json
{
  "dish_id": 42,
  "liked": null
}
```

---

### Chat Endpoint

#### POST `/api/chat`

Main AI interaction endpoint. This is the most complex endpoint - it handles the entire recommendation conversation.

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | User's message or command |
| `session_id` | string | Conversation session ID |

**Message Types:**

| Message | What It Does |
|---------|--------------|
| `/recommend` | Start recommendation flow |
| `answer:question_id:value` | Answer a question |
| Anything else | General chat response |

---

### Chat Flow Example

**Step 1: Start Recommendation**

```bash
curl -X POST "http://localhost:8000/api/chat?user_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{"message": "/recommend", "session_id": "session_1"}'
```

**Response (Question):**
```json
{
  "response_type": "question",
  "question_id": "mood",
  "question_text": "How are you feeling right now?",
  "options": [
    {"value": "happy", "label": "Happy", "emoji": "😊"},
    {"value": "stressed", "label": "Stressed", "emoji": "😤"},
    {"value": "tired", "label": "Tired", "emoji": "😴"}
  ],
  "session_id": "session_1"
}
```

---

**Step 2: Answer Question**

```bash
curl -X POST "http://localhost:8000/api/chat?user_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{"message": "answer:mood:happy", "session_id": "session_1"}'
```

**Response (Next Question):**
```json
{
  "response_type": "question",
  "question_id": "craving",
  "question_text": "What kind of food are you craving?",
  "options": [
    {"value": "comfort", "label": "Comfort Food", "emoji": "🍝"},
    {"value": "healthy", "label": "Healthy", "emoji": "🥗"},
    {"value": "adventurous", "label": "Try Something New", "emoji": "🌶️"}
  ],
  "session_id": "session_1"
}
```

---

**Step 3-4: Continue answering...**

---

**Step 5: Final Recommendation**

After all questions are answered:

```json
{
  "agent_summaries": {
    "mood": {
      "icon": "😊",
      "title": "Mood Analysis",
      "points": [
        "You're feeling happy today",
        "Great time to try something new!"
      ]
    },
    "preferences": {
      "icon": "🎯",
      "title": "Your Preferences",
      "points": [
        "Looking for healthy options",
        "Mild spice preferred"
      ]
    },
    "taste_preferences": {
      "icon": "👤",
      "title": "Your Taste",
      "points": [
        "You tend to like Asian cuisines",
        "Favorite hall: Dining Commons"
      ]
    },
    "availability": {
      "icon": "🍽️",
      "title": "Available Now",
      "points": [
        "15 dishes match your preferences",
        "3 vegetarian options available"
      ]
    }
  },
  "recommendation": "Based on your happy mood and preference for healthy food, I recommend the **Teriyaki Chicken Bowl** from Dining Commons! It's one of your favorite categories (Asian cuisine), and it's fresh and flavorful. The dining hall is currently open.",
  "session_id": "session_1"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Format

When Pydantic validation fails:

```json
{
  "detail": [
    {
      "loc": ["query", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `loc` | Where the error is (query param, body field) |
| `msg` | Human-readable error message |
| `type` | Error type for programmatic handling |

---

## Testing with cURL

### Quick Test Commands

```bash
# Health check
curl http://localhost:8000/api/health

# Get menu for lunch
curl "http://localhost:8000/api/menu?user_id=test&meal=Lunch"

# Get user profile
curl "http://localhost:8000/api/profile?user_id=test"

# Update profile (make vegetarian)
curl -X PUT "http://localhost:8000/api/profile?user_id=test" \
  -H "Content-Type: application/json" \
  -d '{"is_vegetarian": true}'

# Submit feedback
curl -X POST "http://localhost:8000/api/feedback?user_id=test" \
  -H "Content-Type: application/json" \
  -d '{"dish_id": 1, "dish_name": "Test Dish", "liked": true}'

# Start recommendation
curl -X POST "http://localhost:8000/api/chat?user_id=test" \
  -H "Content-Type: application/json" \
  -d '{"message": "/recommend", "session_id": "test"}'
```

---

## Auto-Generated Documentation

FastAPI creates interactive docs automatically:

| URL | What It Is |
|-----|------------|
| http://localhost:8000/docs | **Swagger UI** - Try API calls in browser! |
| http://localhost:8000/redoc | **ReDoc** - Prettier documentation |
| http://localhost:8000/openapi.json | **OpenAPI Spec** - Machine-readable |

**Swagger UI is amazing for testing!** You can:
- See all endpoints
- Try requests directly
- See request/response schemas
- No code needed

---

## CORS (Cross-Origin Resource Sharing)

**What:** Security feature controlling which websites can call your API.

**Our Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Our frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why:** Without CORS, browsers block requests from `localhost:5173` (frontend) to `localhost:8000` (backend) because they're different origins.

---

## Design Choices

### Why Query Parameters for user_id?

```
GET /api/profile?user_id=abc123  ← Query parameter
vs
GET /api/profile                 ← With auth header
Authorization: Bearer abc123
```

**Current (Query Param):**
- Simple to implement
- Easy to test with cURL
- No authentication system needed

**Future (Auth Header):**
- More secure
- Standard practice
- Requires auth system

### Why RESTful Design?

| Principle | How We Follow It |
|-----------|------------------|
| **Resources** | /menu, /profile, /feedback |
| **HTTP Methods** | GET for read, POST for create, PUT for update |
| **Stateless** | Each request is independent |
| **JSON** | Standard data format |

---

## Potential Improvements

### Current Limitations

1. **No authentication** - user_id is just a string
2. **No rate limiting** - could be spammed
3. **No API versioning** - breaking changes affect everyone

### Future Improvements

```python
# 1. Add authentication
@app.get("/api/profile")
def get_profile(token: str = Depends(verify_jwt_token)):
    user_id = token.sub  # From JWT
    ...

# 2. Add rate limiting
@app.get("/api/chat")
@limiter.limit("30/minute")
async def chat(...):
    ...

# 3. Add versioning
@app.get("/api/v1/menu")
@app.get("/api/v2/menu")  # New version with different response
```

---

## Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check if server is running |
| `/api/menu` | GET | Get filtered menu items |
| `/api/menu/summary` | GET | Get menu statistics |
| `/api/menu/refresh` | POST | Trigger new scrape |
| `/api/profile` | GET/PUT | Get/update dietary preferences |
| `/api/profile/mood` | GET/PUT | Get/update current mood |
| `/api/feedback` | POST | Submit dish rating |
| `/api/feedback/stats` | GET | Get rating statistics |
| `/api/feedback/{id}` | GET | Get rating for specific dish |
| `/api/chat` | POST | AI chat and recommendations |

**Key Concepts:**
- **API** = How frontend talks to backend
- **HTTP Methods** = GET (read), POST (create), PUT (update), DELETE (remove)
- **Status Codes** = 200 (OK), 400 (bad request), 404 (not found), 500 (server error)
- **Query Parameters** = Data in URL (`?user_id=abc123`)
- **Request Body** = Data in JSON format
- **CORS** = Security allowing cross-origin requests
