# Database Architecture (Beginner-Friendly Guide)

This document explains how BerkeleyBites stores and retrieves data. We use **Supabase**, which is a managed PostgreSQL database.

---

## What is a Database?

A **database** is a structured way to store data permanently. Think of it as a super-powered spreadsheet:

```
Regular Spreadsheet           vs        Database
────────────────────────────────────────────────────
- One person at a time                 - Thousands of users simultaneously
- Limited rows                         - Millions of rows
- File on your computer                - Server accessible from anywhere
- No relationships                     - Tables can reference each other
- Manual backup                        - Automatic backup and recovery
```

### Types of Databases

| Type | Example | How It Works | Best For |
|------|---------|--------------|----------|
| **Relational (SQL)** | PostgreSQL, MySQL | Data in tables with rows and columns | Structured data with relationships |
| **NoSQL** | MongoDB, Firebase | Flexible document storage | Unstructured or changing data |

**We use PostgreSQL** (relational) because our data has clear structure and relationships.

---

## What is Supabase?

**Supabase** is a service that gives you a PostgreSQL database plus extra features:

| Feature | What It Is | Why It's Useful |
|---------|------------|-----------------|
| **Managed Database** | Someone else runs the server | No DevOps work for us |
| **Local Development** | `supabase start` for testing | Same database locally and in production |
| **Free Tier** | Free for small projects | Great for development |
| **SQL Editor** | Web interface for queries | Easy to explore data |
| **Auto-generated API** | REST/GraphQL built-in | (We don't use this - we use our own API) |

### Why Supabase Instead of Raw PostgreSQL?

| Supabase | Raw PostgreSQL |
|----------|----------------|
| Ready to use in minutes | Need to set up server |
| Automatic backups | Configure backups yourself |
| Web dashboard included | Install pgAdmin separately |
| Easy local dev with CLI | Set up Docker yourself |
| Free tier available | Pay for hosting immediately |

---

## Our Database Schema

**Schema** = The structure/blueprint of your database (what tables exist, what columns they have).

### Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OUR DATABASE                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        dishes           │   ← Menu items (refreshed daily)
├─────────────────────────┤
│ id                      │   ← Unique identifier
│ dish_name               │   ← "Teriyaki Chicken"
│ dining_hall             │   ← "Dining Commons"
│ meal_period             │   ← "Lunch"
│ category                │   ← "Entrees"
│ has_milk, has_egg...    │   ← Allergen flags (true/false)
│ is_vegan, is_vegetarian │   ← Dietary flags (true/false)
│ scrape_date             │   ← When we got this data
└───────────┬─────────────┘
            │
            │ dish_id (foreign key)
            ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│       feedback          │       │     user_profiles       │
├─────────────────────────┤       ├─────────────────────────┤
│ id                      │       │ id                      │
│ user_id                 │       │ user_id (unique)        │
│ dish_id ────────────────┼───────│ is_vegetarian           │
│ dish_name               │       │ is_vegan                │
│ liked (true/false)      │       │ avoid_gluten            │
│ rating_date             │       │ avoid_nuts              │
└─────────────────────────┘       │ ... more preferences    │
                                  └─────────────────────────┘

┌─────────────────────────┐       ┌─────────────────────────┐
│      user_moods         │       │   dish_embeddings       │
├─────────────────────────┤       ├─────────────────────────┤
│ id                      │       │ id                      │
│ user_id (unique)        │       │ dish_id                 │
│ mood                    │       │ embedding (384 numbers) │
│ updated_at              │       │ created_at              │
└─────────────────────────┘       └─────────────────────────┘
```

---

## Table Definitions

### Table: `dishes`

Stores today's menu items (scraped daily from Berkeley dining website).

```sql
CREATE TABLE dishes (
    -- Every row needs a unique ID
    id SERIAL PRIMARY KEY,

    -- Basic information
    dish_name VARCHAR(255) NOT NULL,        -- "Teriyaki Chicken Bowl"
    dining_hall VARCHAR(100) NOT NULL,      -- "Dining Commons"
    dining_hall_status VARCHAR(50) NOT NULL,-- "Open" or "Closed"
    meal_period VARCHAR(100) NOT NULL,      -- "Breakfast", "Lunch", "Dinner"
    category VARCHAR(100) NOT NULL,         -- "Entrees", "Soups", etc.

    -- Allergen flags (all boolean = true/false)
    has_milk BOOLEAN DEFAULT FALSE,
    has_egg BOOLEAN DEFAULT FALSE,
    has_fish BOOLEAN DEFAULT FALSE,
    has_shellfish BOOLEAN DEFAULT FALSE,
    has_tree_nuts BOOLEAN DEFAULT FALSE,
    has_wheat BOOLEAN DEFAULT FALSE,
    has_peanuts BOOLEAN DEFAULT FALSE,
    has_soybeans BOOLEAN DEFAULT FALSE,
    has_sesame BOOLEAN DEFAULT FALSE,
    has_gluten BOOLEAN DEFAULT FALSE,

    -- Dietary flags
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_halal BOOLEAN DEFAULT FALSE,
    is_kosher BOOLEAN DEFAULT FALSE,
    has_pork BOOLEAN DEFAULT FALSE,
    has_alcohol BOOLEAN DEFAULT FALSE,

    -- When this data was collected
    scrape_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent duplicate entries: same dish + hall + meal + date = already exists
    UNIQUE(dish_name, dining_hall, meal_period, scrape_date)
);
```

**Key Concepts:**
- `SERIAL PRIMARY KEY` = Auto-incrementing unique ID
- `VARCHAR(255)` = Text up to 255 characters
- `BOOLEAN DEFAULT FALSE` = True/false, defaults to false
- `UNIQUE(...)` = These columns combined must be unique

**Sample Data:**

| id | dish_name | dining_hall | meal_period | is_vegetarian | has_gluten |
|----|-----------|-------------|-------------|---------------|------------|
| 1 | Scrambled Eggs | Dining Commons | Breakfast | true | false |
| 2 | Pancakes | Dining Commons | Breakfast | true | true |
| 3 | Teriyaki Chicken | Café Strada | Lunch | false | true |

---

### Table: `user_profiles`

Stores each user's dietary preferences and restrictions.

```sql
CREATE TABLE user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,  -- From frontend localStorage

    -- Dietary preferences
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_pescatarian BOOLEAN DEFAULT FALSE,
    is_halal BOOLEAN DEFAULT FALSE,
    is_kosher BOOLEAN DEFAULT FALSE,

    -- Allergens to avoid
    avoid_milk BOOLEAN DEFAULT FALSE,
    avoid_eggs BOOLEAN DEFAULT FALSE,
    avoid_gluten BOOLEAN DEFAULT FALSE,
    avoid_nuts BOOLEAN DEFAULT FALSE,
    avoid_soy BOOLEAN DEFAULT FALSE,

    -- Other preferences
    prefer_low_carbon BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Why `user_id` is UNIQUE:** Each user can only have one profile. If they update preferences, we update the existing row instead of creating a new one.

---

### Table: `feedback`

Stores user ratings (thumbs up/down) for dishes.

```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    dish_id INTEGER REFERENCES dishes(id),  -- Links to dishes table
    dish_name VARCHAR(255) NOT NULL,        -- Stored here too for quick access
    liked BOOLEAN NOT NULL,                 -- true = liked, false = disliked
    rating_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- One rating per user per dish per day
    UNIQUE(user_id, dish_id, rating_date)
);
```

**What is a Foreign Key?**
`dish_id INTEGER REFERENCES dishes(id)` means:
- This column stores a number
- That number must exist in the `dishes` table's `id` column
- This creates a **relationship** between tables

```
feedback table:          dishes table:
user_id | dish_id       id | dish_name
─────────────────       ─────────────────
abc123  | 3     ──────▶  3 | Teriyaki Chicken
abc123  | 1     ──────▶  1 | Scrambled Eggs
```

---

### Table: `user_moods`

Stores each user's current mood (just one value per user, updated when they change it).

```sql
CREATE TABLE user_moods (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    mood VARCHAR(50) NOT NULL DEFAULT 'happy',
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Only allow valid mood values
    CONSTRAINT valid_mood CHECK (
        mood IN ('happy', 'grumpy', 'stressed', 'tired', 'adventurous')
    )
);
```

**What is a CHECK constraint?**
It enforces valid values. If someone tries to insert `mood = 'angry'`, the database will reject it because 'angry' isn't in the allowed list.

---

### Table: `dish_embeddings` (For AI/Semantic Search)

Stores vector embeddings for semantic search.

```sql
CREATE TABLE dish_embeddings (
    id SERIAL PRIMARY KEY,
    dish_id INTEGER REFERENCES dishes(id),
    embedding vector(384),  -- 384-dimensional vector
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**What are embeddings?**
Text converted to numbers that capture meaning. "Chicken Soup" becomes `[0.23, -0.15, 0.87, ...]` (384 numbers). Similar foods have similar numbers.

---

## Database Operations (CRUD)

**CRUD** = Create, Read, Update, Delete - the four basic operations.

### Python Database Client

```python
# backend/database.py

from supabase import create_client, Client
import os

# Singleton pattern: only create one connection
_client: Client | None = None

def get_client() -> Client:
    """Get or create database connection."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        _client = create_client(url, key)
    return _client
```

**What is a Singleton?**
A pattern ensuring only ONE instance exists. Without it:
```python
# BAD: Creates new connection every time (slow!)
def get_data():
    client = create_client(url, key)  # 100ms each time
    return client.table("dishes").select("*").execute()

# GOOD: Reuses one connection
_client = None
def get_data():
    client = get_client()  # First call: 100ms. After: 0ms
    return client.table("dishes").select("*").execute()
```

### CRUD Examples

#### Create (INSERT)

```python
def submit_feedback(user_id: str, dish_id: int, liked: bool):
    """Save a user's rating for a dish."""
    client = get_client()

    data = {
        "user_id": user_id,
        "dish_id": dish_id,
        "dish_name": "Teriyaki Chicken",  # Denormalized for quick access
        "liked": liked,
        "rating_date": str(date.today())
    }

    # Upsert = Insert if new, Update if exists
    result = client.table("feedback") \
        .upsert(data, on_conflict="user_id,dish_id,rating_date") \
        .execute()

    return result.data[0]
```

#### Read (SELECT)

```python
def get_dishes(meal_period: str = None, dining_hall: str = None):
    """Fetch dishes with optional filters."""
    client = get_client()

    # Start with all dishes
    query = client.table("dishes").select("*")

    # Add filters if provided
    if meal_period:
        query = query.eq("meal_period", meal_period)
    if dining_hall:
        query = query.eq("dining_hall", dining_hall)

    result = query.execute()
    return result.data  # List of dicts
```

#### Update

```python
def update_user_profile(user_id: str, profile: dict):
    """Update user preferences."""
    client = get_client()

    data = {"user_id": user_id, **profile}

    # Upsert: create if doesn't exist, update if does
    result = client.table("user_profiles") \
        .upsert(data, on_conflict="user_id") \
        .execute()

    return result.data[0]
```

#### Delete

```python
def delete_feedback(user_id: str, dish_id: int):
    """Remove a user's rating."""
    client = get_client()

    client.table("feedback") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("dish_id", dish_id) \
        .execute()
```

---

## Indexes (Making Queries Fast)

**Index** = A data structure that makes lookups faster (like an index in a book).

Without index: Database scans EVERY row to find matches
With index: Database jumps directly to matching rows

```sql
-- We query by these columns often, so we index them
CREATE INDEX idx_dishes_scrape_date ON dishes(scrape_date);
CREATE INDEX idx_dishes_dining_hall ON dishes(dining_hall);
CREATE INDEX idx_dishes_meal_period ON dishes(meal_period);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
```

**When to add an index:**
- Column used in WHERE clauses frequently
- Column used in JOIN conditions
- Column used for sorting (ORDER BY)

**Trade-off:**
- Faster reads
- Slower writes (index must be updated)
- More storage space

---

## CSV Fallback

When Supabase is unavailable (offline development, connection issues), we fall back to CSV files.

```python
# backend/main.py

USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")

if USE_SUPABASE:
    from . import database as db
else:
    # Use in-memory storage + CSV files
    _user_profiles: dict[str, UserProfile] = {}
    _user_moods: dict[str, str] = {}
    _menu_df = pd.read_csv("dining_data_clean.csv")
```

### CSV File Format

**`dining_data_clean.csv`:**
```csv
dish_name,dining_hall,meal_period,category,has_milk,is_vegetarian,scrape_date
Scrambled Eggs,Dining Commons,Breakfast,Hot Breakfast,false,true,2026-02-03
Pancakes,Dining Commons,Breakfast,Hot Breakfast,true,true,2026-02-03
```

---

## Local Development with Supabase

### Starting Local Database

```bash
# Navigate to supabase folder
cd supabase

# Start local Supabase (PostgreSQL, API, Studio)
supabase start

# This starts:
# - PostgreSQL on port 54322
# - REST API on port 54321
# - Studio (Web UI) on port 54323
```

### Supabase Studio

Open http://localhost:54323 to:
- View and edit tables visually
- Run SQL queries
- See database structure

### Running Migrations

**Migration** = Version control for database changes.

```bash
# Apply all migrations
supabase db push

# Create a new migration
supabase migration new add_new_column

# This creates a file like:
# supabase/migrations/20260203123456_add_new_column.sql
```

### Stopping Local Database

```bash
supabase stop
```

---

## Environment Configuration

```bash
# .env file

# Local Supabase
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=eyJhbGc...  # Local anon key (safe to share for local dev)

# Toggle Supabase on/off
USE_SUPABASE=true
```

---

## Query Examples

### Get Today's Vegetarian Lunch Options

```python
def get_vegetarian_lunch():
    from datetime import date
    client = get_client()

    result = client.table("dishes") \
        .select("dish_name, dining_hall, category") \
        .eq("scrape_date", str(date.today())) \
        .eq("meal_period", "Lunch") \
        .eq("is_vegetarian", True) \
        .execute()

    return result.data
```

### Get User's Favorite Categories

```python
def get_favorite_categories(user_id: str):
    """Analyze what categories a user likes most."""
    client = get_client()

    # Get all liked dishes
    result = client.table("feedback") \
        .select("dish_name, dishes(category)") \
        .eq("user_id", user_id) \
        .eq("liked", True) \
        .execute()

    # Count categories
    from collections import Counter
    categories = [f["dishes"]["category"] for f in result.data if f.get("dishes")]
    return Counter(categories).most_common(5)

# Result: [("Asian", 4), ("Salads", 3), ("Soups", 2)]
```

### Get Open Dining Halls

```python
def get_open_halls():
    from datetime import date
    client = get_client()

    result = client.table("dishes") \
        .select("dining_hall") \
        .eq("scrape_date", str(date.today())) \
        .eq("dining_hall_status", "Open") \
        .execute()

    # Remove duplicates
    return list(set(d["dining_hall"] for d in result.data))
```

---

## Query Optimization Tips

### Do Filtering in the Database, Not Python

```python
# BAD: Fetches ALL dishes, then filters in Python (slow!)
result = client.table("dishes").select("*").execute()
vegetarian = [d for d in result.data if d["is_vegetarian"]]

# GOOD: Database does the filtering (fast!)
result = client.table("dishes") \
    .select("*") \
    .eq("is_vegetarian", True) \
    .execute()
```

### Select Only What You Need

```python
# BAD: Fetches all columns (might be 20+ columns)
result = client.table("dishes").select("*").execute()

# GOOD: Fetches only what we need
result = client.table("dishes") \
    .select("dish_name, dining_hall, meal_period") \
    .execute()
```

### Use Limits for Large Tables

```python
# BAD: Fetches potentially millions of rows
result = client.table("feedback").select("*").execute()

# GOOD: Limit to what we need
result = client.table("feedback") \
    .select("*") \
    .eq("user_id", user_id) \
    .order("created_at", desc=True) \
    .limit(50) \
    .execute()
```

---

## Design Choices & Why

### Why PostgreSQL?

| Reason | Explanation |
|--------|-------------|
| **Industry standard** | Used by most companies |
| **Powerful features** | JSON, full-text search, vectors |
| **ACID compliance** | Data integrity guaranteed |
| **Great tooling** | pgAdmin, Supabase Studio |

### Why Store `dish_name` in `feedback` Table?

This is **denormalization** - storing redundant data for performance:

```
# Normalized (correct but slow):
feedback: user_id, dish_id
dishes: id, dish_name

# To show "You liked: Teriyaki Chicken", we need to JOIN tables

# Denormalized (faster reads):
feedback: user_id, dish_id, dish_name  ← dish_name stored twice

# We can display dish_name directly without joining
```

**Trade-off:**
- Faster reads (no JOIN needed)
- More storage space
- Must update dish_name in both places if it changes

### Why UUID for User IDs?

```sql
user_id UUID DEFAULT gen_random_uuid()
```

**UUID** (Universally Unique Identifier) like `550e8400-e29b-41d4-a716-446655440000`:
- Globally unique - no collisions
- Can be generated client-side
- Hard to guess (security)
- No central counter needed

---

## Potential Improvements

### Current Limitations

1. **No data archiving** - Old menu data stays forever
2. **No connection pooling** - Could run out of connections under load
3. **Simple caching** - No distributed cache

### Future Improvements

```sql
-- 1. Archive old data (keep only last 30 days)
DELETE FROM dishes WHERE scrape_date < NOW() - INTERVAL '30 days';

-- 2. Add partitioning for large tables
CREATE TABLE dishes_2026_01 PARTITION OF dishes
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- 3. Add full-text search
ALTER TABLE dishes ADD COLUMN search_vector tsvector;
CREATE INDEX idx_dishes_search ON dishes USING gin(search_vector);
```

---

## Summary

| Concept | What It Is |
|---------|------------|
| **Database** | Structured storage for data |
| **PostgreSQL** | Relational database we use |
| **Supabase** | Managed PostgreSQL service |
| **Schema** | Structure/blueprint of database |
| **Table** | Collection of rows with columns |
| **Primary Key** | Unique identifier for each row |
| **Foreign Key** | Reference to another table |
| **Index** | Speeds up queries |
| **Migration** | Version control for schema |
| **CRUD** | Create, Read, Update, Delete |

**Our Tables:**
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `dishes` | Today's menu | dish_name, dining_hall, allergens |
| `user_profiles` | Dietary preferences | is_vegan, avoid_gluten |
| `feedback` | User ratings | user_id, dish_id, liked |
| `user_moods` | Current mood | user_id, mood |
| `dish_embeddings` | Vectors for AI | embedding (384 numbers) |
