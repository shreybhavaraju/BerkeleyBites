# Glossary: Technical Terms Explained Simply

This glossary explains every technical term you'll encounter in this project, assuming zero prior knowledge.

---

## A

### API (Application Programming Interface)
**Simple:** A set of rules for how programs talk to each other.

**Analogy:** Think of a restaurant. You (the customer/frontend) don't go into the kitchen. Instead, you tell the waiter (API) what you want, and they bring back food from the kitchen (backend).

**In this project:** The frontend calls APIs like `/api/menu` to get data from the backend.

### ASGI (Asynchronous Server Gateway Interface)
**Simple:** A way for Python web servers to handle multiple requests at once.

**Why it matters:** Instead of handling one user at a time, the server can handle thousands simultaneously.

**In this project:** Uvicorn is our ASGI server that runs FastAPI.

### Async/Await
**Simple:** A way to do multiple things at once without waiting.

**Analogy:** Instead of waiting for water to boil before chopping vegetables, you start boiling water, then chop while it heats up.

```python
# Without async (slow):
data1 = get_menu()       # Wait 2 seconds
data2 = get_profile()    # Wait 1 second
# Total: 3 seconds

# With async (fast):
data1, data2 = await asyncio.gather(
    get_menu(),          # Starts immediately
    get_profile()        # Also starts immediately
)
# Total: 2 seconds (they run at the same time)
```

---

## B

### Backend
**Simple:** The part of an application users don't see - the server, database, and business logic.

**What it does:**
- Processes requests from the frontend
- Stores and retrieves data
- Runs complex calculations (like AI)
- Validates data

**In this project:** Python + FastAPI running on port 8000.

### Boolean
**Simple:** A value that's either `true` or `false`.

```python
is_vegetarian = True
has_nuts = False
```

---

## C

### Cache
**Simple:** Temporary storage that makes things faster by remembering previous results.

**Analogy:** If someone asks "What's 7 × 8?", you calculate it once (56), then remember it. Next time, you don't recalculate.

**In this project:** We cache:
- Menu data (so we don't hit the database every request)
- User feedback (to speed up preference analysis)
- Embeddings (so we don't recompute vectors)

### Component (React)
**Simple:** A reusable piece of user interface.

**Analogy:** Like LEGO blocks. A "Button" component can be used anywhere, a "DishCard" component displays any dish.

```jsx
// This is a component
function DishCard({ dish }) {
  return (
    <div>
      <h3>{dish.name}</h3>
      <p>{dish.description}</p>
    </div>
  );
}

// Use it multiple times
<DishCard dish={pasta} />
<DishCard dish={salad} />
<DishCard dish={soup} />
```

### Context (React)
**Simple:** A way to share data across many components without passing it through each one.

**Problem it solves:**
```jsx
// Without context - tedious "prop drilling"
<App user={user}>
  <Layout user={user}>
    <Sidebar user={user}>
      <UserProfile user={user} />  // Finally used here!
    </Sidebar>
  </Layout>
</App>

// With context - much cleaner
<UserContext.Provider value={user}>
  <App>
    <Layout>
      <Sidebar>
        <UserProfile />  // Gets user from context
      </Sidebar>
    </Layout>
  </App>
</UserContext.Provider>
```

### CORS (Cross-Origin Resource Sharing)
**Simple:** A security feature that controls which websites can access your API.

**Why it exists:** Without CORS, any website could make requests to your bank's API and steal your money.

**In this project:** We allow requests from `localhost:5173` (our frontend) but block others.

### CRUD
**Simple:** The four basic operations you can do with data:
- **C**reate (add new data)
- **R**ead (get existing data)
- **U**pdate (modify data)
- **D**elete (remove data)

---

## D

### Database
**Simple:** A structured way to store data permanently.

**Types:**
- **Relational (SQL):** Data in tables with rows and columns (like Excel). Example: PostgreSQL
- **NoSQL:** More flexible structures. Example: MongoDB

**In this project:** Supabase (which uses PostgreSQL).

### Dependency
**Simple:** Code that your code needs to work.

**Example:** BerkeleyBites depends on:
- `fastapi` - for the web server
- `pandas` - for data manipulation
- `react` - for the user interface

**Files that list dependencies:**
- `requirements.txt` - Python dependencies
- `package.json` - JavaScript dependencies

---

## E

### Embedding (AI)
**Simple:** Converting text into numbers that capture its meaning.

**Why:** Computers can't understand "chicken soup is warm and comforting" directly. We convert it to numbers like `[0.23, -0.45, 0.67, ...]` where similar meanings have similar numbers.

**In this project:** We embed dish names so "Chicken Noodle Soup" is mathematically similar to "Warm Broth Bowl".

### Endpoint
**Simple:** A specific URL that does something.

```
GET  /api/menu          → Returns list of dishes
POST /api/feedback      → Saves a user's rating
PUT  /api/profile       → Updates user preferences
```

### Environment Variables
**Simple:** Secret settings stored outside your code.

**Why:** You don't want to put passwords in your code (which might be public on GitHub).

```bash
# .env file (not committed to git)
PERPLEXITY_API_KEY=sk_secret_key_here
DATABASE_PASSWORD=super_secret
```

```python
# In code, read them:
import os
api_key = os.getenv("PERPLEXITY_API_KEY")
```

---

## F

### FastAPI
**Simple:** A Python framework for building APIs quickly.

**Why we use it:**
- Very fast performance
- Automatic documentation at `/docs`
- Built-in data validation
- Great for AI/ML projects

### Fetch
**Simple:** A JavaScript function to make HTTP requests.

```javascript
// Get data from server
const response = await fetch('/api/menu');
const dishes = await response.json();
```

### Frontend
**Simple:** The part of an application users see and interact with (the website/app interface).

**In this project:** React application running on port 5173.

---

## G

### GET, POST, PUT, DELETE (HTTP Methods)
**Simple:** Different types of requests telling the server what you want to do.

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Read data | Get the menu |
| POST | Create data | Submit a new rating |
| PUT | Update data | Change profile settings |
| DELETE | Remove data | Delete a saved item |

---

## H

### Hook (React)
**Simple:** A function that lets you use React features in components.

```javascript
// useState - remember values
const [count, setCount] = useState(0);

// useEffect - do something when things change
useEffect(() => {
  console.log("Count changed!");
}, [count]);
```

### HTTP (HyperText Transfer Protocol)
**Simple:** The language browsers and servers use to communicate.

```
Browser: "GET /api/menu HTTP/1.1"
Server: "HTTP/1.1 200 OK" + [menu data]
```

### Hybrid Retriever
**Simple:** Our custom system that combines multiple techniques to find the best dishes.

**4 Stages:**
1. **Filter:** Remove dishes that violate dietary restrictions
2. **Vector Search:** Find semantically similar dishes
3. **Score:** Rank by mood, cravings, preferences, etc.
4. **Refine:** Use AI to pick the final recommendations

---

## J

### JSON (JavaScript Object Notation)
**Simple:** A text format for storing and sending data.

```json
{
  "dish_name": "Teriyaki Chicken",
  "is_vegetarian": false,
  "allergens": ["soy", "wheat"]
}
```

**Why use it:** Human-readable and works with every programming language.

### JSX
**Simple:** A way to write HTML inside JavaScript (used in React).

```jsx
// This is JSX
function Welcome() {
  return <h1>Hello, {user.name}!</h1>;
}
```

---

## L

### LangChain
**Simple:** A framework for building applications with AI language models.

**What it helps with:**
- Connecting to AI providers (OpenAI, Perplexity)
- Managing conversation history
- Creating "tools" that AI can use

### LLM (Large Language Model)
**Simple:** An AI that understands and generates text (like ChatGPT).

**In this project:** We use Perplexity's "Sonar" model to write personalized recommendations.

### localStorage
**Simple:** Browser storage that persists even when you close the browser.

```javascript
// Save data
localStorage.setItem('user_id', 'user_123');

// Read data
const userId = localStorage.getItem('user_id');
```

**In this project:** Stores user ID and cached preferences.

---

## M

### Middleware
**Simple:** Code that runs between receiving a request and sending a response.

```
Request → [Middleware: Check CORS] → [Middleware: Log request] → Handler → Response
```

### Migration (Database)
**Simple:** A file that describes changes to the database structure.

```sql
-- migrations/001_create_dishes.sql
CREATE TABLE dishes (
  id SERIAL PRIMARY KEY,
  dish_name VARCHAR(255),
  is_vegetarian BOOLEAN
);
```

**Why:** Keeps track of database changes over time, like version control for your database.

### Model (Pydantic)
**Simple:** A definition of what data should look like.

```python
class Dish(BaseModel):
    name: str        # Must be text
    price: float     # Must be a number
    is_vegan: bool   # Must be true/false
```

**Benefit:** If someone sends wrong data, it's automatically rejected.

---

## O

### Orchestrator
**Simple:** The "conductor" that coordinates multiple agents.

**In this project:** `orchestrator.py` calls the mood agent, question agent, taste agent, etc., combines their outputs, and generates the final recommendation.

---

## P

### PostgreSQL
**Simple:** A powerful, open-source relational database.

**Think of it as:** A very advanced Excel with:
- Millions of rows
- Relations between tables
- Advanced queries
- Multiple users accessing simultaneously

### Prompt (AI)
**Simple:** Instructions you give to an AI.

```
System: "You are a food recommendation assistant for UC Berkeley..."
User: "I'm feeling tired and it's cold outside."
AI: "I recommend the Chicken Noodle Soup!"
```

### Proxy (Dev Server)
**Simple:** A middleman that forwards requests.

**Why we use it:** Frontend runs on port 5173, backend on port 8000. The proxy makes requests to `/api/...` automatically go to the backend.

```javascript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000'  // Forward /api requests to backend
  }
}
```

### Pydantic
**Simple:** A Python library for data validation.

```python
# If data doesn't match, Pydantic throws an error
class User(BaseModel):
    name: str
    age: int  # Must be integer

User(name="John", age="twenty")  # Error! "twenty" isn't an integer
```

---

## Q

### Query
**Simple:** A request for data from a database.

```sql
SELECT dish_name FROM dishes WHERE is_vegetarian = true;
```

### Query Parameter
**Simple:** Extra information added to a URL.

```
/api/menu?meal=lunch&hall=commons
         └── query parameters ──┘
```

---

## R

### RAG (Retrieval Augmented Generation)
**Simple:** A technique where AI retrieves relevant information before generating a response.

**Without RAG:**
```
AI: "I recommend pasta" (might not be available today)
```

**With RAG:**
```
1. Retrieve: Find dishes available today
2. Generate: "I recommend the Penne Arrabbiata from today's menu"
```

### React
**Simple:** A JavaScript library for building user interfaces.

**Key concept:** UI = function of state
```jsx
// When `count` changes, the UI automatically updates
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### REST API
**Simple:** A design pattern for APIs using HTTP methods and URLs.

```
GET    /api/dishes      → Read all dishes
GET    /api/dishes/42   → Read dish #42
POST   /api/dishes      → Create a dish
PUT    /api/dishes/42   → Update dish #42
DELETE /api/dishes/42   → Delete dish #42
```

---

## S

### Schema
**Simple:** The structure/blueprint of your data.

```
dishes table schema:
├── id: integer (auto-incrementing)
├── dish_name: text
├── is_vegetarian: boolean
├── has_nuts: boolean
└── created_at: timestamp
```

### Semantic Search
**Simple:** Finding things by meaning, not just keywords.

**Keyword search:** "warm food" only finds dishes with "warm" in the name
**Semantic search:** "warm food" finds soups, stews, hot beverages (conceptually warm)

### Singleton
**Simple:** A design pattern ensuring only one instance of something exists.

```python
# Without singleton - creates new connection each time (slow, wasteful)
def get_data():
    db = create_database_connection()  # Takes 100ms
    return db.query(...)

# With singleton - reuses one connection
_db = None
def get_db():
    global _db
    if _db is None:
        _db = create_database_connection()  # Only once
    return _db
```

### State
**Simple:** Data that can change over time in your application.

```jsx
// `isLoading` is state - it changes from true to false
const [isLoading, setIsLoading] = useState(true);

// When data loads:
setIsLoading(false);  // UI updates automatically
```

### Supabase
**Simple:** A service that provides a PostgreSQL database with extra features.

**What it gives you:**
- Database (PostgreSQL)
- Authentication (login/signup)
- Real-time subscriptions
- Storage for files
- Auto-generated API

---

## T

### Tailwind CSS
**Simple:** A CSS framework using utility classes instead of writing custom CSS.

```html
<!-- Without Tailwind -->
<div style="background: blue; padding: 16px; border-radius: 8px;">
  Hello
</div>

<!-- With Tailwind -->
<div class="bg-blue-500 p-4 rounded-lg">
  Hello
</div>
```

### TTL (Time To Live)
**Simple:** How long cached data stays valid.

```python
# Cache menu for 24 hours
menu_cache = {"data": menu, "ttl": 86400}  # 86400 seconds = 24 hours
```

### Type Hint (Python)
**Simple:** Telling Python what type of data a variable should be.

```python
def greet(name: str) -> str:  # Takes string, returns string
    return f"Hello, {name}"

age: int = 25  # This should be an integer
```

### TypeScript
**Simple:** JavaScript with type checking.

```typescript
// JavaScript - no error until runtime
function add(a, b) {
  return a + b;
}
add("1", 2);  // Returns "12" (oops, string concatenation)

// TypeScript - catches error before running
function add(a: number, b: number): number {
  return a + b;
}
add("1", 2);  // Error: "1" is not a number
```

---

## U

### URL (Uniform Resource Locator)
**Simple:** A web address.

```
https://berkeleybites.com/api/menu?meal=lunch
└─┬─┘   └──────┬───────┘ └──┬───┘ └───┬────┘
protocol    domain       path    query params
```

### Uvicorn
**Simple:** A fast web server that runs Python ASGI applications (like FastAPI).

```bash
uvicorn main:app --reload --port 8000
#       └─┬─┘    └──┬───┘  └───┬────┘
#    file:variable  auto-restart  port number
```

---

## V

### Validation
**Simple:** Checking that data is correct before using it.

```python
# Without validation - dangerous
def set_age(age):
    user.age = age  # What if age is "banana"?

# With validation - safe
def set_age(age: int):
    if age < 0 or age > 150:
        raise ValueError("Invalid age")
    user.age = age
```

### Vector
**Simple:** A list of numbers representing something.

```python
# Text embedding (simplified)
"chicken soup" → [0.82, -0.15, 0.44, 0.91, ...]

# Similar meanings have similar vectors
"chicken broth" → [0.79, -0.18, 0.41, 0.88, ...]  # Very close!
"ice cream"     → [-0.45, 0.72, -0.33, 0.12, ...] # Very different!
```

### Vite
**Simple:** A fast build tool for frontend development.

**What it does:**
- Starts a development server (instant updates when you save)
- Bundles code for production
- Handles imports, TypeScript, CSS

---

## W

### Web Scraping
**Simple:** Automatically extracting data from websites.

```python
# Get the UC Berkeley menu webpage
response = requests.get("https://dining.berkeley.edu/menus/")

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find all dish names
dishes = soup.find_all('div', class_='menu-item')
```

**In this project:** We scrape the Berkeley dining website daily to get fresh menu data.

---

## Numbers & Symbols

### 200, 400, 404, 500 (HTTP Status Codes)
**Simple:** Numbers that tell you if a request succeeded or failed.

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | "Here's your data" |
| 400 | Bad Request | "You sent invalid data" |
| 401 | Unauthorized | "You need to log in" |
| 404 | Not Found | "That page doesn't exist" |
| 500 | Server Error | "Something broke on our end" |

### `@app.get("/api/menu")` (Decorator)
**Simple:** A way to add functionality to a function.

```python
@app.get("/api/menu")  # This registers the function as a GET endpoint
def get_menu():
    return {"dishes": [...]}
```

The `@` symbol means "wrap this function with additional behavior."
