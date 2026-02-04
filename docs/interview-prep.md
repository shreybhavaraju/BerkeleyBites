# BerkeleyBites: Complete Interview Guide (Zero to Hero)

This guide assumes you know NOTHING about programming. By the end, you'll understand every part of this project and be able to answer any interview question.

---

# PART 1: THE ABSOLUTE BASICS

Before we talk about BerkeleyBites, let's understand what we're even building.

---

## What is a "Web Application"?

A **web application** (or "web app") is a program that runs in your browser (like Chrome, Safari, Firefox).

```
Examples of web apps:
- Gmail (email in your browser)
- Google Docs (documents in your browser)
- Netflix (videos in your browser)
- BerkeleyBites (food recommendations in your browser)
```

**How is this different from a regular app?**
- Regular app: You download it to your phone/computer
- Web app: You just open a website, nothing to download

---

## The Client-Server Model (CRITICAL CONCEPT!)

Every web app has two parts that talk to each other:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   YOUR COMPUTER (Client)              COMPANY'S COMPUTER (Server)       │
│   ─────────────────────               ───────────────────────────       │
│                                                                         │
│   ┌─────────────┐                           ┌─────────────┐            │
│   │   Browser   │  ──── "Give me data" ───► │   Server    │            │
│   │  (Chrome)   │                           │  (Python)   │            │
│   │             │  ◄─── "Here's the data"── │             │            │
│   └─────────────┘                           └─────────────┘            │
│                                                                         │
│   This is the                               This is the                │
│   FRONTEND                                  BACKEND                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Real-World Analogy: A Restaurant

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   CUSTOMER (You)           WAITER              KITCHEN                  │
│   ──────────────           ──────              ───────                  │
│                                                                         │
│   "I'd like the    ───►    Writes down    ───►  Chef cooks             │
│    pasta please"           your order           the pasta               │
│                                                                         │
│   Eats pasta       ◄───    Brings plate   ◄───  Pasta ready!           │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   FRONTEND                 API                  BACKEND                 │
│   (What you see)           (Messenger)          (Does the work)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "What is the difference between frontend and backend?"**

> **ANSWER:** "The frontend is what users see and interact with - buttons, text, images, forms. It runs in the user's browser. The backend is the server that processes requests, runs business logic, talks to databases, and sends data back. The frontend and backend communicate through APIs."

---

## What is an API?

**API** = Application Programming Interface

It's a contract that says: "If you send me THIS, I'll send you back THAT."

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   WITHOUT AN API:                                                       │
│   ───────────────                                                       │
│   Frontend: "Hey backend, I need... um... something about food?"       │
│   Backend: "What? I don't understand. What format? What data?"         │
│   Frontend: "Ugh, never mind."                                         │
│                                                                         │
│   WITH AN API:                                                          │
│   ─────────────                                                         │
│   API Contract: "Send GET request to /api/menu, receive list of dishes"│
│                                                                         │
│   Frontend: "GET /api/menu"                                            │
│   Backend: "[{name: 'Pasta'}, {name: 'Salad'}, {name: 'Soup'}]"       │
│   Frontend: "Perfect! I know exactly what to expect."                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "What is an API?"**

> **ANSWER:** "An API is a defined way for two programs to communicate. It specifies exactly what request to send and what response to expect. In BerkeleyBites, our API has endpoints like /api/menu which returns today's dishes, and /api/chat which handles AI recommendations. The frontend calls these endpoints to get data from the backend."

---

## What is a Database?

A **database** is where we store data permanently. Without it, everything disappears when you close the app.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   WITHOUT A DATABASE:                                                   │
│   ───────────────────                                                   │
│                                                                         │
│   User: "I'm vegan, remember that!"                                    │
│   App: "Got it!"                                                       │
│   [User closes browser]                                                │
│   [User opens browser again]                                           │
│   User: "What am I?"                                                   │
│   App: "Who are you? I've never seen you before."                      │
│                                                                         │
│   WITH A DATABASE:                                                      │
│   ─────────────────                                                     │
│                                                                         │
│   User: "I'm vegan, remember that!"                                    │
│   App: "Saved to database!"                                            │
│   [User closes browser]                                                │
│   [User opens browser again]                                           │
│   User: "What am I?"                                                   │
│   App: "You're vegan! I looked it up in the database."                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Database = Like a giant Excel spreadsheet that never forgets.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         dishes TABLE                                     │
├────────┬──────────────────────┬─────────────┬────────────┬─────────────┤
│   id   │      dish_name       │ dining_hall │ is_vegan   │ has_nuts    │
├────────┼──────────────────────┼─────────────┼────────────┼─────────────┤
│   1    │ Teriyaki Chicken     │ Commons     │ false      │ false       │
│   2    │ Garden Salad         │ Commons     │ true       │ false       │
│   3    │ Pad Thai             │ Crossroads  │ false      │ true        │
│   4    │ Veggie Burger        │ Café 3      │ true       │ false       │
└────────┴──────────────────────┴─────────────┴────────────┴─────────────┘
```

**INTERVIEW QUESTION: "Why do you need a database?"**

> **ANSWER:** "A database stores data permanently. Without it, we'd lose all user preferences, menu items, and feedback every time the server restarts. We use Supabase, which is PostgreSQL under the hood - a powerful relational database. We store dishes, user profiles, feedback ratings, and more."

---

## HTTP: How Computers Talk

When your browser talks to a server, it uses **HTTP** (HyperText Transfer Protocol).

There are 4 main types of requests (think of them as verbs):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   HTTP METHOD        MEANING              REAL-WORLD ANALOGY            │
│   ───────────        ───────              ──────────────────            │
│                                                                         │
│   GET                "Give me data"       "Show me the menu"            │
│                                                                         │
│   POST               "Create something"   "I'd like to place an order"  │
│                                                                         │
│   PUT                "Update something"   "Actually, change my order"   │
│                                                                         │
│   DELETE             "Remove something"   "Cancel my order"             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**In BerkeleyBites:**
```
GET  /api/menu      →  "Show me today's dishes"
GET  /api/profile   →  "Show me my dietary preferences"
PUT  /api/profile   →  "Update my dietary preferences"
POST /api/feedback  →  "Save my rating for this dish"
POST /api/chat      →  "Send a chat message"
```

**INTERVIEW QUESTION: "What HTTP methods did you use?"**

> **ANSWER:** "We use GET to retrieve data like the menu and user profiles. POST to create new data like feedback ratings and chat messages. PUT to update existing data like user preferences. We follow REST conventions where the URL represents a resource and the HTTP method represents the action."

---

## JSON: The Language of Data

**JSON** (JavaScript Object Notation) is how we format data when sending it between frontend and backend.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   JSON looks like this:                                                 │
│                                                                         │
│   {                                                                     │
│     "dish_name": "Teriyaki Chicken Bowl",                              │
│     "dining_hall": "Dining Commons",                                   │
│     "is_vegan": false,                                                 │
│     "allergens": ["soy", "wheat"],                                     │
│     "rating": 4.5                                                      │
│   }                                                                     │
│                                                                         │
│   KEY RULES:                                                            │
│   - Keys are always in "quotes"                                        │
│   - Strings use "double quotes"                                        │
│   - Numbers have no quotes                                             │
│   - true/false are lowercase                                           │
│   - Arrays use [brackets]                                              │
│   - Objects use {braces}                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Why JSON?**
- Human-readable (you can look at it and understand it)
- Every programming language can read/write it
- Lightweight (not bloated with extra stuff)

---

# PART 2: THE TECHNOLOGIES WE USE

Now let's understand each technology in our stack.

---

## React (Frontend)

**React** is a JavaScript library for building user interfaces. Created by Facebook.

### The Big Idea: Components

Everything in React is a **component** - a reusable piece of UI.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   A WEBPAGE IS MADE OF COMPONENTS:                                      │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                        <Header />                                │  │
│   │   Logo        Navigation Links                    User Avatar   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌─────────────────────────────┐  ┌────────────────────────────────┐  │
│   │                             │  │                                │  │
│   │       <ChatPanel />         │  │       <MenuBrowser />          │  │
│   │                             │  │                                │  │
│   │   ┌───────────────────┐    │  │  ┌────────────────────────┐   │  │
│   │   │  <ChatMessage />  │    │  │  │    <DishCard />        │   │  │
│   │   └───────────────────┘    │  │  │  Teriyaki Chicken      │   │  │
│   │   ┌───────────────────┐    │  │  │  [👍] [👎]             │   │  │
│   │   │  <ChatMessage />  │    │  │  └────────────────────────┘   │  │
│   │   └───────────────────┘    │  │  ┌────────────────────────┐   │  │
│   │   ┌───────────────────┐    │  │  │    <DishCard />        │   │  │
│   │   │  <ChatInput />    │    │  │  │  Garden Salad          │   │  │
│   │   └───────────────────┘    │  │  └────────────────────────┘   │  │
│   │                             │  │                                │  │
│   └─────────────────────────────┘  └────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### How a Component Works

```jsx
// A simple React component
function DishCard({ dish }) {
  return (
    <div className="dish-card">
      <h3>{dish.name}</h3>           {/* Display the dish name */}
      <p>{dish.dining_hall}</p>      {/* Display where it's served */}
      <button>👍 Like</button>
      <button>👎 Dislike</button>
    </div>
  );
}

// Use it like this:
<DishCard dish={{name: "Pasta", dining_hall: "Commons"}} />
<DishCard dish={{name: "Salad", dining_hall: "Crossroads"}} />
```

### State: Data That Changes

**State** is data that can change over time. When state changes, React automatically updates the UI.

```jsx
function LikeButton() {
  // useState creates a variable that React "watches"
  const [liked, setLiked] = useState(false);

  // When clicked, toggle the state
  const handleClick = () => {
    setLiked(!liked);  // This changes state
    // React automatically re-renders the button!
  };

  return (
    <button onClick={handleClick}>
      {liked ? "❤️ Liked" : "🤍 Like"}
    </button>
  );
}
```

**INTERVIEW QUESTION: "Why did you choose React?"**

> **ANSWER:** "React is ideal for building interactive UIs. Its component-based architecture lets us create reusable pieces like DishCard and ChatMessage. The virtual DOM makes updates efficient. It has a huge ecosystem and community. It's also an industry standard, used by Facebook, Netflix, Airbnb, and most modern web companies."

**INTERVIEW QUESTION: "How does React manage state?"**

> **ANSWER:** "We use several state management approaches. Local state with useState for component-specific data like form inputs. React Context for shared state that many components need - like user profile, current mood, and chat messages. This avoids 'prop drilling' where you'd have to pass data through many layers. The Context is defined in AppContext.tsx and accessed anywhere with useApp()."

---

## TypeScript (Type-Safe JavaScript)

**TypeScript** is JavaScript with types. It catches errors BEFORE you run the code.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   JAVASCRIPT (No types - errors happen at runtime):                    │
│   ─────────────────────────────────────────────────                    │
│                                                                         │
│   function add(a, b) {                                                 │
│     return a + b;                                                      │
│   }                                                                     │
│                                                                         │
│   add(5, 10);        // Returns 15 ✓                                   │
│   add("5", 10);      // Returns "510" ✗ (string + number = weird)      │
│                      // No error! Just wrong behavior.                 │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   TYPESCRIPT (Has types - errors happen while coding):                 │
│   ─────────────────────────────────────────────────                    │
│                                                                         │
│   function add(a: number, b: number): number {                         │
│     return a + b;                                                      │
│   }                                                                     │
│                                                                         │
│   add(5, 10);        // Returns 15 ✓                                   │
│   add("5", 10);      // ERROR! "5" is not a number!                    │
│                      // You see this error BEFORE running the code.    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "Why use TypeScript over JavaScript?"**

> **ANSWER:** "TypeScript adds type safety, catching errors at compile time rather than runtime. This is especially valuable in a team setting and for larger codebases. It also improves IDE support with better autocomplete and refactoring tools. The types serve as documentation, making the code self-documenting."

---

## Python + FastAPI (Backend)

**Python** is the programming language. **FastAPI** is a framework that makes building APIs easy.

### Why Python?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   PYTHON IS GREAT FOR:                                                  │
│                                                                         │
│   ✓ AI/Machine Learning (TensorFlow, PyTorch, LangChain)               │
│   ✓ Data processing (Pandas, NumPy)                                    │
│   ✓ Readable, beginner-friendly syntax                                 │
│   ✓ Huge ecosystem of libraries                                        │
│   ✓ Most popular language for backend AI applications                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### How FastAPI Works

```python
from fastapi import FastAPI

app = FastAPI()

# This creates an endpoint!
@app.get("/api/menu")
def get_menu():
    return [
        {"name": "Pasta", "is_vegan": False},
        {"name": "Salad", "is_vegan": True}
    ]

# When someone visits /api/menu, they get that list!
```

The `@app.get("/api/menu")` part is called a **decorator**. It says "when someone makes a GET request to /api/menu, run this function."

**INTERVIEW QUESTION: "Why FastAPI instead of Flask or Django?"**

> **ANSWER:** "FastAPI offers several advantages: It's one of the fastest Python frameworks due to async support. It has automatic request/response validation using Pydantic. It generates interactive API documentation automatically at /docs. It has excellent type hint support which improves code quality. Flask would work but requires more manual setup. Django is overkill for an API-only backend and adds unnecessary complexity."

---

## Supabase + PostgreSQL (Database)

**PostgreSQL** is a powerful database. **Supabase** makes it easy to use.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   WHY SUPABASE?                                                         │
│                                                                         │
│   Raw PostgreSQL alone:          Supabase:                             │
│   ─────────────────────          ─────────                             │
│   - Set up your own server       - They host it for you                │
│   - Configure backups            - Automatic backups                   │
│   - Manage security              - Built-in security                   │
│   - Install admin tools          - Web dashboard included              │
│   - Lots of DevOps work          - Just use it!                        │
│                                                                         │
│   Think of Supabase as "PostgreSQL as a Service"                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "Why Supabase instead of Firebase or raw PostgreSQL?"**

> **ANSWER:** "Supabase gives us the power of PostgreSQL (industry-standard relational database) without the DevOps overhead. Unlike Firebase (NoSQL), we get proper SQL with joins, transactions, and strong consistency. Supabase also provides a great local development experience with 'supabase start', auto-generated APIs, and a web dashboard. The free tier is generous for development."

---

# PART 3: HOW BERKELEYBITES WORKS

Now let's put it all together and understand our specific application.

---

## The Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     BERKELEYBITES ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────┘

         USER'S BROWSER                              OUR SERVERS
    ┌─────────────────────────┐            ┌─────────────────────────────┐
    │                         │            │                             │
    │   ┌─────────────────┐   │            │   ┌─────────────────────┐   │
    │   │                 │   │            │   │                     │   │
    │   │   React App     │   │  HTTP      │   │    FastAPI Server   │   │
    │   │   (TypeScript)  │───┼───────────►│   │    (Python)         │   │
    │   │                 │   │  Requests  │   │                     │   │
    │   │   Components:   │   │            │   │    Endpoints:       │   │
    │   │   - ChatPanel   │   │            │   │    - /api/menu      │   │
    │   │   - MenuBrowser │◄──┼────────────│   │    - /api/chat      │   │
    │   │   - DishCard    │   │  JSON      │   │    - /api/profile   │   │
    │   │   - Profile     │   │  Responses │   │    - /api/feedback  │   │
    │   │                 │   │            │   │                     │   │
    │   └─────────────────┘   │            │   └──────────┬──────────┘   │
    │                         │            │              │              │
    │   Port 5173             │            │              │              │
    │                         │            │              ▼              │
    └─────────────────────────┘            │   ┌─────────────────────┐   │
                                           │   │                     │   │
                                           │   │    AI AGENTS        │   │
                                           │   │    ───────────      │   │
                                           │   │                     │   │
                                           │   │    - Orchestrator   │   │
                                           │   │    - Mood Agent     │   │
                                           │   │    - Question Agent │   │
                                           │   │    - Taste Agent    │   │
                                           │   │    - Food Agent     │   │
                                           │   │    - Retriever      │   │
                                           │   │                     │   │
                                           │   └──────────┬──────────┘   │
                                           │              │              │
                                           │              ▼              │
                                           │   ┌─────────────────────┐   │
                                           │   │                     │   │
                                           │   │   Supabase          │   │
                                           │   │   (PostgreSQL)      │   │
                                           │   │                     │   │
                                           │   │   Tables:           │   │
                                           │   │   - dishes          │   │
                                           │   │   - user_profiles   │   │
                                           │   │   - feedback        │   │
                                           │   │   - user_moods      │   │
                                           │   │   - embeddings      │   │
                                           │   │                     │   │
                                           │   └─────────────────────┘   │
                                           │                             │
                                           │   Port 8000                 │
                                           └─────────────────────────────┘
```

---

## The User Journey (Step by Step)

Let's trace exactly what happens when someone uses BerkeleyBites:

### Step 1: User Opens the App

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER OPENS APP                                                  │
└─────────────────────────────────────────────────────────────────────────┘

User types: berkeleybites.com (or localhost:5173 in development)

Browser does this:
1. Downloads HTML, CSS, JavaScript files
2. React app starts running
3. App checks localStorage for user_id
   - If found: Use existing ID
   - If not: Generate new ID like "user_abc123"
4. App calls GET /api/menu to load today's dishes
5. App calls GET /api/profile to load user's dietary preferences
6. User sees the menu!
```

### Step 2: User Clicks "Get Recommendation"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: RECOMMENDATION FLOW                                             │
└─────────────────────────────────────────────────────────────────────────┘

User clicks "Get Recommendation" button

QUESTION 1: "How are you feeling?"
┌─────────────────────────────────────────────────────┐
│  😊 Happy    😤 Stressed    😴 Tired    🤠 Adventurous │
└─────────────────────────────────────────────────────┘
User selects: 😊 Happy

QUESTION 2: "What kind of food are you craving?"
┌─────────────────────────────────────────────────────┐
│  🍝 Comfort Food    🥗 Healthy    🌶️ Something New    │
└─────────────────────────────────────────────────────┘
User selects: 🥗 Healthy

QUESTION 3: "How spicy do you want it?"
┌─────────────────────────────────────────────────────┐
│  😌 Mild    🌶️ Medium    🔥 Spicy    💀 Extra Hot      │
└─────────────────────────────────────────────────────┘
User selects: 😌 Mild

QUESTION 4: "How much time do you have?"
┌─────────────────────────────────────────────────────┐
│  ⚡ Quick (grab & go)    🕐 Normal    🍽️ Leisurely     │
└─────────────────────────────────────────────────────┘
User selects: 🕐 Normal
```

### Step 3: AI Agents Process the Request

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: AI AGENTS DO THEIR THING                                        │
└─────────────────────────────────────────────────────────────────────────┘

All answers collected. Now the Orchestrator coordinates:

┌─────────────────┐
│  ORCHESTRATOR   │  "I'm the conductor. Let me ask each agent..."
└────────┬────────┘
         │
         ├──────────────────────────────────────────────────────────────┐
         │                                                              │
         ▼                                                              ▼
┌─────────────────┐                                          ┌─────────────────┐
│   MOOD AGENT    │                                          │ QUESTION AGENT  │
│                 │                                          │                 │
│ Input: "happy"  │                                          │ Input: answers  │
│                 │                                          │                 │
│ Output:         │                                          │ Output:         │
│ "Happy mood =   │                                          │ "Wants healthy  │
│  open to new    │                                          │  food, mild     │
│  things, fresh  │                                          │  spice, normal  │
│  flavors OK"    │                                          │  dining time"   │
└─────────────────┘                                          └─────────────────┘
         │                                                              │
         ├──────────────────────────────────────────────────────────────┤
         │                                                              │
         ▼                                                              ▼
┌─────────────────┐                                          ┌─────────────────┐
│  TASTE AGENT    │                                          │   FOOD AGENT    │
│                 │                                          │                 │
│ Input: user's   │                                          │ Input: user's   │
│  past feedback  │                                          │  diet + filters │
│                 │                                          │                 │
│ Output:         │                                          │ Output:         │
│ "User has liked │                                          │ "245 dishes     │
│  Asian food 5x, │                                          │  today. 120     │
│  dislikes heavy │                                          │  are vegetarian.│
│  dishes"        │                                          │  15 match all   │
│                 │                                          │  criteria."     │
└─────────────────┘                                          └─────────────────┘
```

### Step 4: Hybrid Retrieval Finds Best Dishes

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: HYBRID RETRIEVAL PIPELINE                                       │
└─────────────────────────────────────────────────────────────────────────┘

The retriever uses a 4-stage pipeline to find the BEST dishes:

STAGE 1: SQL FILTERS (removes dishes that violate restrictions)
─────────────────────────────────────────────────────────────
245 total dishes
  │
  │  User is vegetarian? Remove all meat dishes.
  │  User avoids nuts? Remove dishes with nuts.
  │  Only lunch? Remove breakfast/dinner dishes.
  │
  ▼
180 dishes remain


STAGE 2: VECTOR SEARCH (finds semantically similar dishes)
─────────────────────────────────────────────────────────────
User wants "healthy" food
  │
  │  Convert "healthy" to a vector: [0.82, -0.15, 0.44, ...]
  │  Find dishes with similar vectors:
  │    - "Garden Salad" → very similar! ✓
  │    - "Grilled Chicken" → similar! ✓
  │    - "Deep Fried Oreos" → very different ✗
  │
  ▼
30 candidate dishes


STAGE 3: MULTI-FACTOR SCORING (ranks dishes by multiple factors)
─────────────────────────────────────────────────────────────

Each dish gets a score from 0 to 1:

┌─────────────────────────────────────────────────────────────────────┐
│                         SCORING FORMULA                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   TASTE PREFERENCE (30%)                                            │
│   → Has user liked similar dishes before?                           │
│   → Example: User liked "Teriyaki Bowl" → similar Asian dishes +30% │
│                                                                     │
│   CRAVING MATCH (25%)                                               │
│   → Does it match what they said they want?                         │
│   → Example: User wants "healthy" → "Garden Salad" +25%             │
│                                                                     │
│   MOOD ALIGNMENT (15%)                                              │
│   → Is it good for their current mood?                              │
│   → Example: User is "happy" → fresh foods +15%                     │
│                                                                     │
│   CATEGORY PREFERENCE (10%)                                         │
│   → From a category they usually like?                              │
│   → Example: User often picks "Asian" → Asian dishes +10%           │
│                                                                     │
│   SPICE MATCH (10%)                                                 │
│   → Matches their spice preference?                                 │
│   → Example: User wants "mild" → mild dishes +10%                   │
│                                                                     │
│   EMBEDDING SIMILARITY (5%)                                         │
│   → Semantically similar to what they described?                    │
│                                                                     │
│   NOVELTY BONUS (+5%)                                               │
│   → User hasn't tried this before? Small bonus!                     │
│                                                                     │
│   DISLIKE PENALTY (-30%)                                            │
│   → User disliked this before? Big penalty!                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Result: Top 8 dishes sent to AI

  1. Teriyaki Chicken Bowl    (score: 0.87)
  2. Garden Salad             (score: 0.82)
  3. Grilled Salmon           (score: 0.79)
  4. Vegetable Stir Fry       (score: 0.76)
  5. ...


STAGE 4: LLM WRITES THE RECOMMENDATION
─────────────────────────────────────────────────────────────

AI receives:
- Top 8 dishes with scores
- User's mood (happy)
- User's craving (healthy)
- User's past preferences

AI writes:
"Based on your happy mood and craving for healthy food, I recommend
the **Teriyaki Chicken Bowl** from Dining Commons! It's a lighter
option with fresh vegetables, and it matches your preference for
Asian cuisine. The dining hall is currently open for lunch."
```

---

## The Multi-Agent System (VERY IMPORTANT FOR INTERVIEWS!)

### Why Multiple Agents?

**INTERVIEW QUESTION: "Why use multiple agents instead of one big AI prompt?"**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ONE BIG PROMPT (BAD):                                                │
│   ─────────────────────                                                 │
│                                                                         │
│   "Hey ChatGPT, the user is happy and wants healthy food and has       │
│    liked Asian food before and is vegetarian and it's lunch time       │
│    and here's all 245 dishes and their allergens and please            │
│    consider their past 50 ratings and also..."                         │
│                                                                         │
│   Problems:                                                             │
│   ✗ Too much in one prompt (confusing for AI)                          │
│   ✗ Expensive (long prompts cost more)                                 │
│   ✗ Slow (AI has to process everything)                                │
│   ✗ Hard to test (can't test pieces individually)                      │
│   ✗ If anything fails, EVERYTHING fails                                │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   MULTIPLE AGENTS (GOOD):                                              │
│   ───────────────────────                                               │
│                                                                         │
│   Mood Agent:     "Happy → user is open to new things"    (no AI!)     │
│   Question Agent: "Wants healthy, mild spice"             (no AI!)     │
│   Taste Agent:    "Likes Asian food"                      (database)   │
│   Food Agent:     "Here are 15 matching dishes"           (database)   │
│   LLM:            "Write a nice recommendation"           (AI)         │
│                                                                         │
│   Benefits:                                                             │
│   ✓ Each agent is simple and focused                                   │
│   ✓ Most agents don't need expensive AI calls!                         │
│   ✓ Fast (parallel processing possible)                                │
│   ✓ Easy to test each agent separately                                 │
│   ✓ If one fails, others still work                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

> **ANSWER:** "A single prompt approach has several problems. First, it's expensive - long prompts cost more tokens. Second, it's slow - the AI has to process everything at once. Third, it's unreliable - the AI might miss important details in a long prompt. Fourth, it's hard to test.

> With multi-agent architecture, each agent has one job. The Mood Agent just maps emotions to food guidance - no AI needed, just a simple lookup table. The Food Agent queries the database. Only the final step needs the LLM. This makes the system faster, cheaper, more reliable, and easier to maintain."

---

## What is RAG? (Retrieval Augmented Generation)

**RAG** is a technique to make AI more accurate by giving it real data to work with.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   WITHOUT RAG:                                                          │
│   ─────────────                                                         │
│                                                                         │
│   User: "What should I eat for lunch?"                                 │
│   AI: "I recommend the Margherita Pizza!"                              │
│   User: "But... that's not on the menu today."                         │
│   AI: "Oops. I just made that up."    ← HALLUCINATION!                 │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   WITH RAG:                                                             │
│   ─────────                                                             │
│                                                                         │
│   1. RETRIEVE: Get today's actual menu from database                   │
│      [Teriyaki Chicken, Garden Salad, Pasta Primavera, ...]           │
│                                                                         │
│   2. AUGMENT: Add this real data to the AI prompt                      │
│      "Here are today's dishes: [list]. Recommend one."                 │
│                                                                         │
│   3. GENERATE: AI picks from REAL options                              │
│      "I recommend the Teriyaki Chicken Bowl!"                          │
│                                                                         │
│   User: "Great, that's actually available!"   ← NO HALLUCINATION!      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "What is RAG and why do you use it?"**

> **ANSWER:** "RAG stands for Retrieval Augmented Generation. The problem with LLMs is they can 'hallucinate' - make up information that sounds real but isn't. By retrieving actual data from our database first, then giving that to the AI, we ensure it can only recommend dishes that actually exist on today's menu. This makes the system much more reliable and trustworthy."

---

## What are Embeddings?

**Embeddings** convert text into numbers that capture meaning. This lets us do "semantic search" - finding things by meaning, not just keywords.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   THE PROBLEM:                                                          │
│   ─────────────                                                         │
│                                                                         │
│   User searches: "warm comfort food"                                   │
│                                                                         │
│   KEYWORD SEARCH:                                                       │
│   Looking for exact words "warm" or "comfort" or "food"...             │
│   Found: Nothing! (No dish has "comfort" in its name)                  │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════  │
│                                                                         │
│   THE SOLUTION - EMBEDDINGS:                                            │
│   ──────────────────────────                                            │
│                                                                         │
│   Step 1: Convert "warm comfort food" to numbers (a vector)            │
│   "warm comfort food" → [0.82, -0.15, 0.44, 0.91, -0.23, ...]         │
│                                                                         │
│   Step 2: Compare to all dish embeddings                               │
│   "Chicken Noodle Soup"  → [0.79, -0.18, 0.41, 0.88, -0.25, ...] CLOSE!│
│   "Mac and Cheese"       → [0.65, -0.12, 0.38, 0.72, -0.19, ...] Close │
│   "Ice Cream"            → [-0.45, 0.72, -0.33, 0.12, 0.81, ...] Far   │
│                                                                         │
│   Step 3: Return dishes with similar vectors                           │
│   Found: Chicken Noodle Soup, Mac and Cheese, Beef Stew, ...          │
│                                                                         │
│   These are all "warm comfort foods" even without those exact words!   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**INTERVIEW QUESTION: "How do embeddings work?"**

> **ANSWER:** "Embeddings convert text into vectors - lists of numbers that capture semantic meaning. We use the all-MiniLM-L6-v2 model which creates 384-dimensional vectors. Similar meanings produce similar vectors, so 'chicken soup' and 'warm broth' end up close together mathematically. We store embeddings for all dishes in the database, then use cosine similarity to find dishes that match what the user is looking for, even if they use different words."

---

# PART 4: ALL POSSIBLE INTERVIEW QUESTIONS

Here's every question you might be asked, with detailed answers.

---

## General Project Questions

### Q: "Tell me about this project."

> **ANSWER:** "BerkeleyBites is a full-stack web application that helps UC Berkeley students decide what to eat at campus dining halls. Instead of scrolling through long menus, users answer four quick questions about their mood, cravings, spice preference, and time. The app then uses a multi-agent AI system to generate personalized recommendations based on their dietary restrictions, past preferences, and current cravings.
>
> The frontend is built with React and TypeScript. The backend uses Python with FastAPI. We store data in Supabase, which is PostgreSQL. The AI system uses a multi-agent architecture where specialized agents handle different aspects - mood analysis, preference tracking, food availability - and then a hybrid retrieval system ranks dishes using a weighted scoring algorithm before an LLM writes the final recommendation."

### Q: "What problem does this solve?"

> **ANSWER:** "UC Berkeley has multiple dining halls with hundreds of dishes that change daily. Students waste time scrolling through menus, often picking the same things out of habit. BerkeleyBites solves this by making personalized recommendations in seconds. It also helps students discover new dishes they'd actually like, based on what they've enjoyed before."

### Q: "What was the hardest part?"

> **ANSWER:** "The hardest part was designing the multi-agent system and the scoring algorithm. We needed to balance multiple factors - taste preferences, mood, cravings, dietary restrictions - in a way that produces good recommendations. We went through several iterations of the scoring weights before finding a balance that works well. Another challenge was making the system fast enough - we implemented caching and optimized the hybrid retrieval pipeline to get response times under one second."

---

## Architecture Questions

### Q: "Walk me through the architecture."

> **ANSWER:** "The app has three main layers:
>
> 1. **Frontend** - A React app with TypeScript running on port 5173. It has components for the chat interface, menu browser, and user profile. State is managed with React Context.
>
> 2. **Backend** - A FastAPI server running on port 8000. It exposes REST endpoints for menu data, user profiles, feedback, and chat. It also contains the AI agent system.
>
> 3. **Database** - Supabase (PostgreSQL) storing dishes, user profiles, feedback ratings, moods, and embeddings.
>
> The AI system uses a multi-agent architecture: an Orchestrator coordinates specialized agents (Mood, Question, Taste, Food), then a Hybrid Retriever uses a 4-stage pipeline (SQL filters, vector search, scoring, LLM refinement) to find the best recommendations."

### Q: "Why separate frontend and backend?"

> **ANSWER:** "Separation of concerns. Each part has a clear responsibility - frontend handles presentation, backend handles logic, database handles persistence. This makes the code easier to maintain, test, and scale. Different developers can work on each part independently. We can also use the best tool for each job - React for UI, Python for AI/ML."

### Q: "How do frontend and backend communicate?"

> **ANSWER:** "Through REST API calls over HTTP. The frontend makes fetch requests to endpoints like /api/menu or /api/chat. The backend processes these, possibly querying the database or running AI agents, then returns JSON responses. During development, Vite's proxy forwards /api requests from port 5173 to 8000."

---

## Frontend Questions

### Q: "Why React?"

> **ANSWER:** "React is ideal for building interactive UIs with its component-based architecture. It has excellent TypeScript support, a huge ecosystem, and is an industry standard used by Facebook, Netflix, Airbnb. The virtual DOM makes updates efficient, and React's declarative approach makes the code easier to reason about."

### Q: "How do you manage state?"

> **ANSWER:** "Three layers: localStorage for persisting user ID across sessions, React Context for shared state that multiple components need (profile, mood, chat messages), and Supabase as the source of truth. On load, we read from localStorage for instant display, fetch fresh data from the backend, then sync everything."

### Q: "What components did you build?"

> **ANSWER:** "Key components include ChatPanel for the AI chat interface, ChatMessage for individual messages with question buttons, MenuBrowser for browsing dishes by hall and meal, DishCard for displaying individual dishes with rating buttons, ProfileEditor for dietary preferences, and Header for navigation and mood display."

---

## Backend Questions

### Q: "Why FastAPI?"

> **ANSWER:** "FastAPI is one of the fastest Python frameworks. It has automatic request/response validation with Pydantic, generates interactive API documentation at /docs, and has excellent async support for handling concurrent requests. It's also great for AI/ML projects, which we need for the recommendation system."

### Q: "What endpoints do you have?"

> **ANSWER:** "Main endpoints are:
> - GET /api/menu - Returns dishes filtered by user's dietary restrictions
> - GET/PUT /api/profile - Get or update user preferences
> - POST /api/feedback - Submit a dish rating
> - POST /api/chat - Main AI interaction endpoint for recommendations
> - GET /api/health - Health check for monitoring"

### Q: "How do you handle errors?"

> **ANSWER:** "Multiple layers: Pydantic validates requests automatically and returns 422 for invalid data. We use HTTPException for business logic errors with appropriate status codes (400 for bad requests, 404 for not found, 500 for server errors). External service failures use graceful degradation - for example, if the database is slow, we fall back to cached data or CSV backup."

---

## Database Questions

### Q: "What tables do you have?"

> **ANSWER:** "Five main tables:
> - **dishes**: Menu items with allergen and dietary flags, refreshed daily from web scraping
> - **user_profiles**: Dietary preferences and restrictions
> - **feedback**: User ratings (liked/disliked) for dishes
> - **user_moods**: Current mood for each user
> - **dish_embeddings**: Vector embeddings for semantic search"

### Q: "Why PostgreSQL?"

> **ANSWER:** "PostgreSQL is an industry-standard relational database. It's powerful, has excellent performance, supports advanced features like JSON columns and vector operations, and has strong data integrity with ACID compliance. Supabase makes it easy to use without managing infrastructure."

### Q: "How do you prevent duplicate data?"

> **ANSWER:** "Unique constraints in the database. For dishes, we have a composite unique key on (dish_name, dining_hall, meal_period, scrape_date). For feedback, it's (user_id, dish_id, rating_date) so users can only rate a dish once per day. We use upsert operations to handle duplicates gracefully."

---

## AI/ML Questions

### Q: "What LLM do you use?"

> **ANSWER:** "Perplexity's Sonar model via their API. It's cost-effective, has fast response times, and provides an OpenAI-compatible API which makes it easy to integrate with LangChain. For our use case of food recommendations, we don't need GPT-4 level reasoning - Sonar is sufficient and more affordable."

### Q: "What embedding model do you use?"

> **ANSWER:** "all-MiniLM-L6-v2 from sentence-transformers. It runs locally (free, no API costs), generates 384-dimensional vectors, and is only 80MB. It has good quality for semantic similarity tasks. We enhance dish names before embedding by adding related terms to create richer vectors."

### Q: "How does the scoring work?"

> **ANSWER:** "Each dish gets a score from 0 to 1 based on multiple weighted factors:
> - 30% taste preference (based on past likes)
> - 25% craving match (matches what they asked for)
> - 15% mood alignment (good for their emotional state)
> - 10% category preference (from categories they usually like)
> - 10% spice match (matches their spice tolerance)
> - 5% embedding similarity (semantically similar)
> Plus a novelty bonus for dishes they haven't tried, and a penalty for previously disliked dishes."

---

## System Design Questions

### Q: "How would you scale this?"

> **ANSWER:** "Several approaches:
> - **Horizontal scaling**: The backend is stateless, so we can run multiple instances behind a load balancer
> - **Database**: Supabase handles scaling, but we could add read replicas for heavy read workloads
> - **Caching**: Move from in-memory caching to Redis for distributed caching
> - **CDN**: Serve the frontend from edge locations for faster load times
> - **Queue**: Add a message queue for handling AI requests to smooth out load spikes"

### Q: "What would you add with more time?"

> **ANSWER:** "Top priorities:
> 1. **User authentication** - Proper accounts so preferences sync across devices
> 2. **Testing** - Unit tests, integration tests, end-to-end tests
> 3. **Monitoring** - Error tracking, performance metrics, usage analytics
> 4. **Nutritional data** - Calories, macros, and nutrition facts
> 5. **Social features** - See what friends are eating, share recommendations"

### Q: "How do you ensure reliability?"

> **ANSWER:** "Graceful degradation is key. If the database is slow, we use cached data. If cached data is stale, we use CSV backup. If one agent fails, others still work. We log errors for debugging. The multi-agent architecture means the system keeps working even if parts fail - we just get slightly less personalized recommendations."

---

## Behavioral Questions

### Q: "What did you learn from this project?"

> **ANSWER:** "Several things:
> 1. How to design a multi-agent AI system with clear responsibilities for each component
> 2. The importance of RAG to prevent AI hallucination
> 3. How to balance multiple factors in a recommendation algorithm
> 4. Full-stack development with React, FastAPI, and PostgreSQL
> 5. The value of caching for performance"

### Q: "What would you do differently?"

> **ANSWER:** "I would add comprehensive testing from the start rather than adding it later. I'd also set up proper CI/CD pipelines for automated deployment. And I'd consider using a more sophisticated feedback system that captures why users like or dislike dishes, not just binary thumbs up/down."

---

# PART 5: QUICK REFERENCE CHEAT SHEET

Print this page and review before your interview!

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + TypeScript | User interface |
| Styling | Tailwind CSS | Fast styling |
| Build Tool | Vite | Development server |
| Backend | FastAPI (Python) | API server |
| Validation | Pydantic | Request/response validation |
| Database | Supabase (PostgreSQL) | Data storage |
| AI | Perplexity Sonar LLM | Recommendation text |
| Embeddings | all-MiniLM-L6-v2 | Semantic search |

## Key Numbers

| Metric | Value |
|--------|-------|
| Embedding dimensions | 384 |
| Vector search candidates | 30 |
| Dishes sent to LLM | 8 |
| Final recommendations | 3-4 |
| Taste score weight | 30% |
| Craving score weight | 25% |
| Menu cache TTL | 24 hours |

## File Structure

```
BerkeleyBites/
├── frontend/src/
│   ├── App.tsx              # Main app
│   ├── components/          # React components
│   ├── api/client.ts        # API calls
│   └── context/             # State management
├── backend/
│   ├── main.py              # API endpoints
│   ├── models.py            # Data models
│   └── database.py          # DB operations
├── agents/
│   ├── orchestrator.py      # Coordinates agents
│   ├── mood_agent.py        # Mood → food mapping
│   ├── question_agent.py    # Preference questions
│   ├── taste_preferences_agent.py  # Feedback analysis
│   ├── food_availability_agent.py  # Available dishes
│   ├── hybrid_retriever.py  # 4-stage pipeline
│   ├── scoring.py           # Scoring algorithm
│   └── embedding_service.py # Vector embeddings
└── scraper.py               # Menu scraping
```

## The 4-Stage Hybrid Retrieval Pipeline

```
1. SQL FILTERS     →  Remove dietary violations
2. VECTOR SEARCH   →  Find semantically similar dishes
3. SCORING         →  Rank by multiple factors
4. LLM REFINEMENT  →  Write personalized recommendation
```

---

# PART 6: THE COMPLETE SYSTEM DIAGRAM

This is the entire BerkeleyBites system - every component, every tool, every data flow.

## Master Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                            BERKELEYBITES - COMPLETE SYSTEM                              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════════
                                    DATA INGESTION (Daily)
═══════════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│                     │          │                     │          │                     │
│   UC BERKELEY       │  HTTP    │     SCRAPER         │  Parse   │    SUPABASE         │
│   DINING WEBSITE    │ ────────►│                     │ ────────►│    DATABASE         │
│                     │  Request │   scraper.py        │  & Save  │                     │
│   dining.berkeley   │          │                     │          │   dishes table      │
│   .edu/menus        │          │   Tools:            │          │   ┌───────────────┐ │
│                     │          │   - requests        │          │   │ id            │ │
│   (HTML page with   │          │   - BeautifulSoup   │          │   │ dish_name     │ │
│    today's menu)    │          │   - pandas          │          │   │ dining_hall   │ │
│                     │          │                     │          │   │ meal_period   │ │
└─────────────────────┘          │   Extracts:         │          │   │ is_vegan      │ │
                                 │   - Dish names      │          │   │ has_nuts      │ │
                                 │   - Dining halls    │          │   │ scrape_date   │ │
                                 │   - Meal periods    │          │   │ ...           │ │
                                 │   - Allergens       │          │   └───────────────┘ │
                                 │   - Dietary flags   │          │                     │
                                 └─────────────────────┘          └──────────┬──────────┘
                                                                             │
                                                                             │
                                                                             ▼
═══════════════════════════════════════════════════════════════════════════════════════════
                                    EMBEDDING GENERATION
═══════════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│                     │          │                     │          │                     │
│   DISHES FROM DB    │  Load    │   EMBEDDING         │  Store   │    SUPABASE         │
│                     │ ────────►│   SERVICE           │ ────────►│    DATABASE         │
│   "Teriyaki         │          │                     │          │                     │
│    Chicken Bowl"    │          │   embedding_        │          │  dish_embeddings    │
│   "Garden Salad"    │          │   service.py        │          │   table             │
│   "Pad Thai"        │          │                     │          │   ┌───────────────┐ │
│   ...               │          │   Model:            │          │   │ dish_id       │ │
│                     │          │   all-MiniLM-L6-v2  │          │   │ embedding     │ │
│                     │          │   (runs locally)    │          │   │ [384 floats]  │ │
│                     │          │                     │          │   └───────────────┘ │
│                     │          │   Output:           │          │                     │
│                     │          │   384-dim vector    │          │   Enables semantic  │
│                     │          │   per dish          │          │   similarity search │
│                     │          │                     │          │                     │
└─────────────────────┘          └─────────────────────┘          └─────────────────────┘



═══════════════════════════════════════════════════════════════════════════════════════════
                                    USER INTERACTION FLOW
═══════════════════════════════════════════════════════════════════════════════════════════


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                   USER'S BROWSER                                        │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │                              REACT FRONTEND                                     │  │
│   │                              (TypeScript)                                       │  │
│   │                              Port 5173                                          │  │
│   │                                                                                 │  │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│   │   │   Header    │  │  ChatPanel  │  │ MenuBrowser │  │ProfileEditor│          │  │
│   │   │             │  │             │  │             │  │             │          │  │
│   │   │ Shows mood  │  │ Chat UI     │  │ Browse menu │  │ Set dietary │          │  │
│   │   │             │  │ Questions   │  │ by hall/    │  │ preferences │          │  │
│   │   │             │  │ Answers     │  │ meal        │  │             │          │  │
│   │   │             │  │ Recommend-  │  │             │  │ is_vegan    │          │  │
│   │   │             │  │ ations      │  │ DishCards   │  │ avoid_nuts  │          │  │
│   │   │             │  │             │  │ with 👍👎   │  │ etc.        │          │  │
│   │   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│   │                                                                                 │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐  │  │
│   │   │                         AppContext.tsx                                  │  │  │
│   │   │                    (React Context - Shared State)                       │  │  │
│   │   │                                                                         │  │  │
│   │   │   Stores: profile, mood, chatMessages, menuData, isLoading             │  │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘  │  │
│   │                                         │                                       │  │
│   │                                         │                                       │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐  │  │
│   │   │                          api/client.ts                                  │  │  │
│   │   │                     (Makes HTTP requests)                               │  │  │
│   │   │                                                                         │  │  │
│   │   │   fetch('/api/menu')  fetch('/api/chat')  fetch('/api/profile')        │  │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘  │  │
│   │                                         │                                       │  │
│   └─────────────────────────────────────────┼───────────────────────────────────────┘  │
│                                             │                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                              localStorage                                       │  │
│   │                         (Browser Persistence)                                   │  │
│   │                                                                                 │  │
│   │   Stores: user_id (e.g., "user_abc123"), cached preferences                    │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
                                             │ HTTP Requests
                                             │ (Vite proxy forwards /api/* to port 8000)
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                   FASTAPI BACKEND                                       │
│                                   (Python)                                              │
│                                   Port 8000                                             │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                              backend/main.py                                    │  │
│   │                              (API Endpoints)                                    │  │
│   │                                                                                 │  │
│   │   GET  /api/health     →  Health check                                         │  │
│   │   GET  /api/menu       →  Get filtered dishes                                  │  │
│   │   GET  /api/profile    →  Get user preferences                                 │  │
│   │   PUT  /api/profile    →  Update user preferences                              │  │
│   │   POST /api/feedback   →  Submit dish rating                                   │  │
│   │   POST /api/chat       →  AI recommendation (main endpoint!)                   │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                             │                                          │
│                                             │ POST /api/chat triggers...               │
│                                             ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │                              AI AGENT SYSTEM                                    │  │
│   │                              (agents/ folder)                                   │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘



═══════════════════════════════════════════════════════════════════════════════════════════
                              AI AGENT SYSTEM (The Brain)
═══════════════════════════════════════════════════════════════════════════════════════════


                              ┌─────────────────────────┐
                              │                         │
                              │      ORCHESTRATOR       │
                              │                         │
                              │    orchestrator.py      │
                              │                         │
                              │    "I coordinate        │
                              │     everything"         │
                              │                         │
                              └────────────┬────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│                         │  │                         │  │                         │
│      MOOD AGENT         │  │    QUESTION AGENT       │  │      TASTE AGENT        │
│                         │  │                         │  │                         │
│    mood_agent.py        │  │   question_agent.py     │  │ taste_preferences_      │
│                         │  │                         │  │ agent.py                │
│    Input:               │  │    Input:               │  │                         │
│    User's mood          │  │    User's answers to    │  │    Input:               │
│    ("happy")            │  │    4 questions          │  │    User's feedback      │
│                         │  │                         │  │    history from DB      │
│    Process:             │  │    Process:             │  │                         │
│    Simple lookup        │  │    Parse answers        │  │    Process:             │
│    table (no AI!)       │  │    (no AI!)             │  │    Analyze patterns     │
│                         │  │                         │  │    (no AI!)             │
│    Output:              │  │    Output:              │  │                         │
│    "Happy = open to     │  │    craving: "healthy"   │  │    Output:              │
│     new foods, fresh    │  │    spice: "mild"        │  │    "Likes Asian,        │
│     flavors OK"         │  │    time: "normal"       │  │     dislikes heavy      │
│                         │  │                         │  │     dishes"             │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
              │                            │                            │
              │                            │                            │
              ▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                  FOOD AVAILABILITY AGENT                                │
│                                                                                         │
│                              food_availability_agent.py                                 │
│                                                                                         │
│    Input: User's dietary profile + filters from other agents                           │
│                                                                                         │
│    Process: Query Supabase for matching dishes                                         │
│                                                                                         │
│    Output: "245 dishes today. 120 vegetarian. 15 match all filters."                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ All agent outputs collected
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                               HYBRID RETRIEVER                                          │
│                                                                                         │
│                             hybrid_retriever.py                                         │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   STAGE 1: SQL FILTERS                                            ~5ms         │  │
│   │   ─────────────────────                                                         │  │
│   │                                                                                 │  │
│   │   Query Supabase with WHERE clauses:                                           │  │
│   │   - is_vegetarian = true (if user is vegetarian)                               │  │
│   │   - has_nuts = false (if user avoids nuts)                                     │  │
│   │   - meal_period = 'Lunch' (current meal)                                       │  │
│   │   - scrape_date = today                                                        │  │
│   │                                                                                 │  │
│   │   245 dishes → 180 dishes (removed violations)                                 │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                            │
│                                           ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   STAGE 2: VECTOR SEARCH                                          ~15ms        │  │
│   │   ──────────────────────                                                        │  │
│   │                                                                                 │  │
│   │   1. Convert user's craving ("healthy") to embedding vector                    │  │
│   │      "healthy" → [0.82, -0.15, 0.44, ...]  (384 numbers)                       │  │
│   │                                                                                 │  │
│   │   2. Compare to all dish embeddings using cosine similarity                    │  │
│   │                                                                                 │  │
│   │   3. Keep top 30 most similar dishes                                           │  │
│   │                                                                                 │  │
│   │   180 dishes → 30 candidates                                                   │  │
│   │                                                                                 │  │
│   │   Tool: embedding_service.py + pgvector in Supabase                            │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                            │
│                                           ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   STAGE 3: MULTI-FACTOR SCORING                                   ~10ms        │  │
│   │   ─────────────────────────────                                                 │  │
│   │                                                                                 │  │
│   │   File: scoring.py                                                             │  │
│   │                                                                                 │  │
│   │   For each dish, calculate weighted score:                                     │  │
│   │                                                                                 │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐  │  │
│   │   │                                                                         │  │  │
│   │   │   SCORE = (taste_pref × 0.30)      ← From feedback history             │  │  │
│   │   │         + (craving_match × 0.25)   ← Matches "healthy"?                │  │  │
│   │   │         + (mood_align × 0.15)      ← Good for "happy" mood?            │  │  │
│   │   │         + (category_pref × 0.10)   ← From favorite categories          │  │  │
│   │   │         + (spice_match × 0.10)     ← Matches "mild" preference?        │  │  │
│   │   │         + (embedding_sim × 0.05)   ← Semantic similarity               │  │  │
│   │   │         + (novelty × 0.05)         ← Bonus if not tried before         │  │  │
│   │   │         - (dislike × 0.30)         ← Penalty if disliked before        │  │  │
│   │   │                                                                         │  │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                                 │  │
│   │   Sort by score, take top 8:                                                   │  │
│   │   1. Teriyaki Chicken Bowl  (0.87)                                             │  │
│   │   2. Garden Salad           (0.82)                                             │  │
│   │   3. Grilled Salmon         (0.79)                                             │  │
│   │   ...                                                                          │  │
│   │                                                                                 │  │
│   │   30 candidates → 8 top dishes                                                 │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                            │
│                                           ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   STAGE 4: LLM REFINEMENT                                         ~500ms       │  │
│   │   ───────────────────────                                                       │  │
│   │                                                                                 │  │
│   │   Send to Perplexity Sonar LLM:                                                │  │
│   │                                                                                 │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐  │  │
│   │   │                                                                         │  │  │
│   │   │   SYSTEM: "You are a food recommendation assistant for UC Berkeley     │  │  │
│   │   │            dining halls. Given the context, recommend 3-4 dishes       │  │  │
│   │   │            with personalized explanations."                            │  │  │
│   │   │                                                                         │  │  │
│   │   │   CONTEXT:                                                              │  │  │
│   │   │   - Mood: Happy (open to new things)                                   │  │  │
│   │   │   - Craving: Healthy food                                              │  │  │
│   │   │   - Spice: Mild                                                        │  │  │
│   │   │   - Past preferences: Likes Asian cuisine                              │  │  │
│   │   │   - Top 8 dishes with scores: [...]                                    │  │  │
│   │   │                                                                         │  │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                                 │  │
│   │   LLM writes personalized recommendation:                                      │  │
│   │   "Based on your happy mood and craving for healthy food, I recommend          │  │
│   │    the **Teriyaki Chicken Bowl** from Dining Commons!..."                      │  │
│   │                                                                                 │  │
│   │   8 dishes → 3-4 recommendations with explanation                              │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ JSON Response
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                               RESPONSE TO FRONTEND                                      │
│                                                                                         │
│   {                                                                                     │
│     "agent_summaries": {                                                               │
│       "mood": { "icon": "😊", "title": "Mood", "points": ["Happy!", "Open to new"] }, │
│       "preferences": { "icon": "🎯", "points": ["Healthy", "Mild spice"] },           │
│       "taste": { "icon": "👤", "points": ["Likes Asian cuisine"] },                   │
│       "availability": { "icon": "🍽️", "points": ["15 dishes match"] }                 │
│     },                                                                                  │
│     "recommendation": "Based on your happy mood and craving for healthy food..."       │
│   }                                                                                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘



═══════════════════════════════════════════════════════════════════════════════════════════
                                    DATABASE (Supabase)
═══════════════════════════════════════════════════════════════════════════════════════════


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              SUPABASE (PostgreSQL)                                      │
│                                                                                         │
│   ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐                  │
│   │                   │  │                   │  │                   │                  │
│   │   dishes          │  │   user_profiles   │  │    feedback       │                  │
│   │                   │  │                   │  │                   │                  │
│   │ ┌───────────────┐ │  │ ┌───────────────┐ │  │ ┌───────────────┐ │                  │
│   │ │ id            │ │  │ │ user_id       │ │  │ │ user_id       │ │                  │
│   │ │ dish_name     │ │  │ │ is_vegetarian │ │  │ │ dish_id       │ │                  │
│   │ │ dining_hall   │ │  │ │ is_vegan      │ │  │ │ dish_name     │ │                  │
│   │ │ meal_period   │ │  │ │ avoid_nuts    │ │  │ │ liked (bool)  │ │                  │
│   │ │ category      │ │  │ │ avoid_gluten  │ │  │ │ rating_date   │ │                  │
│   │ │ is_vegan      │ │  │ │ is_halal      │ │  │ └───────────────┘ │                  │
│   │ │ is_vegetarian │ │  │ │ ...           │ │  │                   │                  │
│   │ │ has_nuts      │ │  │ └───────────────┘ │  │   Stores 👍/👎    │                  │
│   │ │ has_gluten    │ │  │                   │  │   ratings         │                  │
│   │ │ scrape_date   │ │  │   Stores dietary  │  │                   │                  │
│   │ └───────────────┘ │  │   preferences     │  └───────────────────┘                  │
│   │                   │  │                   │                                          │
│   │   Refreshed daily │  └───────────────────┘                                          │
│   │   from scraper    │                                                                 │
│   └───────────────────┘                                                                 │
│                                                                                         │
│   ┌───────────────────┐  ┌───────────────────┐                                          │
│   │                   │  │                   │                                          │
│   │   user_moods      │  │  dish_embeddings  │                                          │
│   │                   │  │                   │                                          │
│   │ ┌───────────────┐ │  │ ┌───────────────┐ │                                          │
│   │ │ user_id       │ │  │ │ dish_id       │ │                                          │
│   │ │ mood          │ │  │ │ embedding     │ │  ← 384-dimensional vector               │
│   │ │ updated_at    │ │  │ │ created_at    │ │    for semantic search                  │
│   │ └───────────────┘ │  │ └───────────────┘ │                                          │
│   │                   │  │                   │                                          │
│   │   Current mood    │  │   Vector store    │                                          │
│   │   per user        │  │   for similarity  │                                          │
│   │                   │  │   search          │                                          │
│   └───────────────────┘  └───────────────────┘                                          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘



═══════════════════════════════════════════════════════════════════════════════════════════
                                    TECHNOLOGY SUMMARY
═══════════════════════════════════════════════════════════════════════════════════════════


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   COMPONENT              TECHNOLOGY              PURPOSE                                │
│   ─────────              ──────────              ───────                                │
│                                                                                         │
│   Web Scraper            Python + BeautifulSoup  Extract menu from Berkeley website    │
│                          + requests + pandas                                           │
│                                                                                         │
│   Embedding Generator    sentence-transformers   Convert dish names to vectors         │
│                          (all-MiniLM-L6-v2)      (runs locally, free)                  │
│                                                                                         │
│   Frontend               React + TypeScript      User interface                        │
│                          + Tailwind CSS                                                │
│                                                                                         │
│   State Management       React Context           Share data between components         │
│                          + localStorage          Persist user ID                       │
│                                                                                         │
│   Build Tool             Vite                    Development server, bundling          │
│                                                                                         │
│   Backend Server         FastAPI (Python)        API endpoints, request handling       │
│                                                                                         │
│   Data Validation        Pydantic                Validate requests/responses           │
│                                                                                         │
│   AI Orchestration       Custom Python           Coordinate multiple agents            │
│                          (orchestrator.py)                                             │
│                                                                                         │
│   Agent Logic            Custom Python           Mood, taste, food analysis            │
│                          (no AI for most!)       (simple logic, database queries)      │
│                                                                                         │
│   Retrieval Pipeline     Custom Python           SQL → Vectors → Scoring → LLM        │
│                          (hybrid_retriever.py)                                         │
│                                                                                         │
│   Scoring Algorithm      Custom Python           Multi-factor weighted scoring         │
│                          (scoring.py)                                                  │
│                                                                                         │
│   LLM (Final Step)       Perplexity Sonar        Write personalized recommendation    │
│                          (via API)               (only AI call in the pipeline!)       │
│                                                                                         │
│   Database               Supabase (PostgreSQL)   Store all data permanently           │
│                          + pgvector              Vector similarity search              │
│                                                                                         │
│   Caching                In-memory (Python)      Speed up repeated queries            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘



═══════════════════════════════════════════════════════════════════════════════════════════
                                    DATA FLOW SUMMARY
═══════════════════════════════════════════════════════════════════════════════════════════


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   DAILY (Data Ingestion):                                                              │
│   ───────────────────────                                                               │
│                                                                                         │
│   Berkeley Website → scraper.py → Supabase (dishes table)                              │
│                           ↓                                                            │
│                   embedding_service.py → Supabase (dish_embeddings table)              │
│                                                                                         │
│                                                                                         │
│   PER REQUEST (Recommendation Flow):                                                   │
│   ──────────────────────────────────                                                    │
│                                                                                         │
│   User clicks button                                                                   │
│         ↓                                                                              │
│   React sends POST /api/chat                                                           │
│         ↓                                                                              │
│   FastAPI receives request                                                             │
│         ↓                                                                              │
│   Orchestrator coordinates agents:                                                     │
│      • Mood Agent (lookup table)                                                       │
│      • Question Agent (parse answers)                                                  │
│      • Taste Agent (query feedback from Supabase)                                      │
│      • Food Agent (query dishes from Supabase)                                         │
│         ↓                                                                              │
│   Hybrid Retriever runs 4 stages:                                                      │
│      1. SQL filters (Supabase query)                                                   │
│      2. Vector search (Supabase pgvector)                                              │
│      3. Scoring (Python calculation)                                                   │
│      4. LLM (Perplexity API call)                                                      │
│         ↓                                                                              │
│   JSON response sent to frontend                                                       │
│         ↓                                                                              │
│   React displays recommendation                                                        │
│                                                                                         │
│                                                                                         │
│   USER FEEDBACK:                                                                       │
│   ──────────────                                                                        │
│                                                                                         │
│   User clicks 👍 or 👎                                                                 │
│         ↓                                                                              │
│   React sends POST /api/feedback                                                       │
│         ↓                                                                              │
│   FastAPI saves to Supabase (feedback table)                                           │
│         ↓                                                                              │
│   Next recommendation uses this data! (via Taste Agent)                                │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

═══════════════════════════════════════════════════════════════════════════════════════════
                    PART 7: AI/ML TERMINOLOGY & HOW WE USE THEM
═══════════════════════════════════════════════════════════════════════════════════════════

This section explains the AI/ML buzzwords and concepts you'll encounter. For each term,
I'll explain what it means AND how BerkeleyBites uses it.

---

## RAG (Retrieval Augmented Generation)

### What is RAG?

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   THE PROBLEM WITH BASIC AI:                                                            │
│   ──────────────────────────                                                            │
│                                                                                         │
│   User: "What food is available at Crossroads today?"                                   │
│                                                                                         │
│   Basic AI: "I don't know. My training data is from 2023 and I don't have              │
│              access to today's menu. I'll just make something up!"                      │
│                                                                                         │
│              → HALLUCINATION! AI invents dishes that don't exist                        │
│                                                                                         │
│                                                                                         │
│   THE RAG SOLUTION:                                                                     │
│   ─────────────────                                                                     │
│                                                                                         │
│   Step 1: RETRIEVE real data (today's menu from database)                              │
│   Step 2: AUGMENT the AI prompt with that data                                         │
│   Step 3: GENERATE response using real data                                            │
│                                                                                         │
│   User: "What food is available at Crossroads today?"                                   │
│                                                                                         │
│   RAG System:                                                                           │
│      1. Query database → "Today's dishes: [Teriyaki Bowl, Garden Salad, ...]"          │
│      2. Give AI this context: "Here are today's actual dishes: [...]"                  │
│      3. AI responds with REAL dishes, no hallucination!                                │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### RAG = Retrieval + Augmented + Generation

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │
│  RETRIEVAL    │ ───► │  AUGMENTED    │ ───► │  GENERATION   │
│               │      │               │      │               │
│  "Get real    │      │  "Add to AI   │      │  "AI writes   │
│   data from   │      │   prompt"     │      │   response"   │
│   database"   │      │               │      │               │
│               │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
```

### How BerkeleyBites Uses RAG

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   OUR RAG IMPLEMENTATION:                                                               │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   1. RETRIEVAL (Stages 1-3 of our pipeline)                                    │  │
│   │   ─────────────────────────────────────────                                     │  │
│   │                                                                                 │  │
│   │   • SQL filters get today's dishes from Supabase                               │  │
│   │   • Vector search finds semantically relevant dishes                           │  │
│   │   • Scoring ranks the best matches                                             │  │
│   │                                                                                 │  │
│   │   Result: Top 8 REAL dishes that exist TODAY                                   │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                             │
│                                          ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   2. AUGMENTATION (Building the LLM prompt)                                    │  │
│   │   ─────────────────────────────────────────                                     │  │
│   │                                                                                 │  │
│   │   "Here is the context for making a recommendation:                            │  │
│   │    - User mood: Happy                                                          │  │
│   │    - User craving: Healthy                                                     │  │
│   │    - Top dishes available TODAY:                                               │  │
│   │      1. Teriyaki Chicken Bowl (score: 0.87)                                    │  │
│   │      2. Garden Salad (score: 0.82)                                             │  │
│   │      ..."                                                                      │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                             │
│                                          ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   3. GENERATION (LLM writes the response)                                      │  │
│   │   ───────────────────────────────────────                                       │  │
│   │                                                                                 │  │
│   │   Perplexity Sonar reads the context and writes:                               │  │
│   │   "Based on your happy mood and craving for healthy food,                      │  │
│   │    I recommend the Teriyaki Chicken Bowl from Crossroads!"                     │  │
│   │                                                                                 │  │
│   │   → Response uses REAL dishes, not hallucinations!                             │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│   WHY RAG MATTERS:                                                                      │
│   ────────────────                                                                      │
│                                                                                         │
│   Without RAG: AI might recommend "Pizza" when pizza isn't served today               │
│   With RAG:    AI can ONLY recommend dishes that actually exist in our database       │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Embeddings (Vector Representations)

### What Are Embeddings?

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   THE PROBLEM:                                                                          │
│   ────────────                                                                          │
│                                                                                         │
│   User searches: "something healthy"                                                    │
│                                                                                         │
│   Keyword search would fail for:                                                        │
│   • "Garden Salad" ← doesn't contain "healthy"!                                        │
│   • "Grilled Salmon" ← doesn't contain "healthy"!                                      │
│                                                                                         │
│   But these ARE healthy foods! How do we find them?                                    │
│                                                                                         │
│                                                                                         │
│   THE SOLUTION: EMBEDDINGS                                                              │
│   ───────────────────────────                                                           │
│                                                                                         │
│   Convert text to NUMBERS that capture MEANING:                                         │
│                                                                                         │
│   "healthy"       → [0.82, -0.15, 0.44, 0.12, -0.33, ...]  (384 numbers)              │
│   "Garden Salad"  → [0.79, -0.18, 0.41, 0.15, -0.30, ...]  (384 numbers)              │
│   "Cheeseburger"  → [0.12, 0.65, -0.22, 0.45, 0.18, ...]   (384 numbers)              │
│                                                                                         │
│   Similar meanings → Similar numbers → Can calculate similarity!                       │
│                                                                                         │
│   "healthy" is CLOSER to "Garden Salad" than to "Cheeseburger"                        │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Embedding Model: all-MiniLM-L6-v2

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   MODEL: all-MiniLM-L6-v2                                                               │
│                                                                                         │
│   ┌──────────────────────┐                                                              │
│   │                      │                                                              │
│   │   "Teriyaki Bowl"    │ ───► TRANSFORMER MODEL ───► [0.23, -0.45, 0.67, ...]       │
│   │                      │      (Neural Network)        384 dimensions                 │
│   │   (text input)       │                             (number output)                 │
│   │                      │                                                              │
│   └──────────────────────┘                                                              │
│                                                                                         │
│   WHY THIS MODEL?                                                                       │
│   ───────────────                                                                       │
│                                                                                         │
│   • FREE and open source (no API costs!)                                               │
│   • Runs LOCALLY on our server (fast, private)                                         │
│   • 384 dimensions (good balance of quality vs. speed)                                 │
│   • Trained on millions of text pairs to understand similarity                         │
│                                                                                         │
│   DIMENSIONS EXPLAINED:                                                                 │
│   ─────────────────────                                                                 │
│                                                                                         │
│   384 dimensions = 384 numbers that represent meaning                                   │
│                                                                                         │
│   Think of it like coordinates, but in 384D space:                                     │
│   • 2D: (x, y) → position on a map                                                     │
│   • 3D: (x, y, z) → position in 3D space                                               │
│   • 384D: (x₁, x₂, ..., x₃₈₄) → position in "meaning space"                           │
│                                                                                         │
│   Similar meanings = close together in this space                                       │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### How BerkeleyBites Uses Embeddings

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   STEP 1: PRE-COMPUTE DISH EMBEDDINGS (Daily)                                          │
│   ───────────────────────────────────────────                                           │
│                                                                                         │
│   After scraping, we run embedding_service.py:                                         │
│                                                                                         │
│   "Teriyaki Chicken Bowl"  → [0.23, -0.45, ...]  → Saved to dish_embeddings table     │
│   "Garden Salad"           → [0.79, -0.18, ...]  → Saved to dish_embeddings table     │
│   "Pepperoni Pizza"        → [0.12, 0.65, ...]   → Saved to dish_embeddings table     │
│   ... (all dishes)                                                                     │
│                                                                                         │
│                                                                                         │
│   STEP 2: QUERY TIME (Per Request)                                                     │
│   ────────────────────────────────                                                      │
│                                                                                         │
│   User craving: "healthy"  → [0.82, -0.15, ...]  (computed on the fly)                │
│                                                                                         │
│   Compare to all dish embeddings using COSINE SIMILARITY:                              │
│                                                                                         │
│   similarity("healthy", "Garden Salad")      = 0.92  ← HIGH! Similar meaning          │
│   similarity("healthy", "Teriyaki Bowl")     = 0.78  ← Pretty good                    │
│   similarity("healthy", "Pepperoni Pizza")   = 0.31  ← LOW! Different meaning         │
│                                                                                         │
│   Return top matches → "Garden Salad" ranks highest for "healthy"                      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Semantic Search vs. Keyword Search

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   KEYWORD SEARCH (Traditional):                                                         │
│   ─────────────────────────────                                                         │
│                                                                                         │
│   Query: "chicken"                                                                      │
│                                                                                         │
│   ✓ "Teriyaki Chicken Bowl"  ← Contains "chicken"                                      │
│   ✓ "Chicken Tenders"        ← Contains "chicken"                                      │
│   ✗ "Poultry Stir Fry"       ← Doesn't contain "chicken" (but IS chicken!)            │
│                                                                                         │
│   Problem: Misses synonyms and related concepts                                        │
│                                                                                         │
│                                                                                         │
│   SEMANTIC SEARCH (What We Use):                                                        │
│   ──────────────────────────────                                                        │
│                                                                                         │
│   Query: "chicken" → embedding → compare to all dish embeddings                        │
│                                                                                         │
│   ✓ "Teriyaki Chicken Bowl"  (similarity: 0.95)                                        │
│   ✓ "Chicken Tenders"        (similarity: 0.93)                                        │
│   ✓ "Poultry Stir Fry"       (similarity: 0.88)  ← Found it!                          │
│   ✗ "Garden Salad"           (similarity: 0.21)                                        │
│                                                                                         │
│   Understands MEANING, not just exact words!                                           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Cosine Similarity

### What Is It?

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   Cosine similarity measures the ANGLE between two vectors:                            │
│                                                                                         │
│                                                                                         │
│              Vector A                         Vector A    Vector B                      │
│                 ↗                                  ↗        ↗                           │
│                /                                  /        /                            │
│               /  θ (angle)                       / (small /                             │
│              /─────                             /  angle) /                             │
│             /      ↘                           /         /                              │
│            ●        Vector B                  ●─────────●                               │
│                                                                                         │
│         Large angle = Different              Small angle = Similar                      │
│         cos(θ) ≈ 0                           cos(θ) ≈ 1                                │
│                                                                                         │
│                                                                                         │
│   FORMULA:                                                                              │
│   ────────                                                                              │
│                          A · B                                                          │
│   cosine_similarity = ─────────────                                                    │
│                       ||A|| × ||B||                                                    │
│                                                                                         │
│   • A · B = dot product (multiply corresponding elements, sum them up)                 │
│   • ||A|| = magnitude (length) of vector A                                             │
│                                                                                         │
│   Result ranges from -1 to 1:                                                          │
│   • 1.0 = Identical meaning                                                            │
│   • 0.0 = Unrelated                                                                    │
│   • -1.0 = Opposite meaning                                                            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### How We Use It

```python
# In Supabase, we use pgvector's built-in cosine similarity:

SELECT dish_name,
       1 - (embedding <=> query_embedding) AS similarity
FROM dish_embeddings
ORDER BY embedding <=> query_embedding  -- <=> is the cosine distance operator
LIMIT 30;
```

---

## pgvector (Vector Database Extension)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS PGVECTOR?                                                                     │
│   ─────────────────                                                                     │
│                                                                                         │
│   A PostgreSQL extension that adds:                                                    │
│   • VECTOR data type (store embeddings in database)                                    │
│   • Similarity search operators (<=> for cosine distance)                              │
│   • Fast vector indexes (IVFFlat, HNSW)                                               │
│                                                                                         │
│                                                                                         │
│   NORMAL POSTGRESQL:                     POSTGRESQL + PGVECTOR:                        │
│   ────────────────────                   ──────────────────────                         │
│                                                                                         │
│   Can store: text, numbers,              Can ALSO store: vectors!                      │
│              dates, JSON                                                               │
│                                                                                         │
│   Can query: WHERE name = 'x'            Can ALSO query: ORDER BY similarity           │
│              WHERE price > 10                            (vector operations!)          │
│                                                                                         │
│                                                                                         │
│   HOW WE USE IT:                                                                        │
│   ──────────────                                                                        │
│                                                                                         │
│   Supabase has pgvector built-in! Our dish_embeddings table:                          │
│                                                                                         │
│   CREATE TABLE dish_embeddings (                                                        │
│     id SERIAL PRIMARY KEY,                                                             │
│     dish_id INTEGER REFERENCES dishes(id),                                             │
│     embedding VECTOR(384),  ← pgvector type! 384 floats                               │
│     created_at TIMESTAMP                                                               │
│   );                                                                                    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## LLM (Large Language Model)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS AN LLM?                                                                       │
│   ───────────────                                                                       │
│                                                                                         │
│   A type of AI trained on MASSIVE amounts of text that can:                            │
│   • Understand natural language                                                        │
│   • Generate human-like text                                                           │
│   • Answer questions, summarize, translate, etc.                                       │
│                                                                                         │
│   Examples: GPT-4, Claude, Llama, Perplexity Sonar                                     │
│                                                                                         │
│                                                                                         │
│   HOW LLMS WORK (Simplified):                                                          │
│   ───────────────────────────                                                           │
│                                                                                         │
│   Input: "The capital of France is"                                                    │
│                                                                                         │
│   LLM predicts the most likely next word based on patterns                             │
│   learned from billions of text examples:                                              │
│                                                                                         │
│   "Paris" (99.9% likely)                                                               │
│   "a" (0.05% likely)                                                                   │
│   "unknown" (0.01% likely)                                                             │
│                                                                                         │
│   → Outputs: "Paris"                                                                    │
│                                                                                         │
│                                                                                         │
│   OUR LLM: PERPLEXITY SONAR                                                            │
│   ─────────────────────────                                                             │
│                                                                                         │
│   • Cheaper than GPT-4 or Claude                                                       │
│   • Fast response times                                                                │
│   • Good enough for our use case (writing recommendations)                             │
│   • Called via API (we send prompt, get response)                                      │
│                                                                                         │
│   IMPORTANT: We only use the LLM for ONE thing:                                        │
│              Writing the final recommendation text!                                     │
│                                                                                         │
│   The "smart" work (finding relevant dishes) is done by                                │
│   our retrieval pipeline BEFORE the LLM sees anything.                                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS MULTI-AGENT?                                                                  │
│   ────────────────────                                                                  │
│                                                                                         │
│   Instead of ONE big monolithic system, we break the task into                         │
│   SPECIALIZED AGENTS that each handle one thing:                                        │
│                                                                                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│   │ Mood Agent  │  │Question Agt │  │ Taste Agent │  │ Food Agent  │                   │
│   │             │  │             │  │             │  │             │                   │
│   │ "I only     │  │ "I only     │  │ "I only     │  │ "I only     │                   │
│   │  handle     │  │  parse      │  │  analyze    │  │  query      │                   │
│   │  moods"     │  │  answers"   │  │  history"   │  │  dishes"    │                   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘                   │
│          │                │                │                │                          │
│          └────────────────┴────────────────┴────────────────┘                          │
│                                    │                                                   │
│                                    ▼                                                   │
│                          ┌─────────────────┐                                           │
│                          │   ORCHESTRATOR  │                                           │
│                          │                 │                                           │
│                          │ "I coordinate   │                                           │
│                          │  everyone"      │                                           │
│                          └─────────────────┘                                           │
│                                                                                         │
│                                                                                         │
│   WHY MULTI-AGENT?                                                                      │
│   ────────────────                                                                      │
│                                                                                         │
│   1. SEPARATION OF CONCERNS                                                            │
│      Each agent does one thing well                                                    │
│                                                                                         │
│   2. EASIER TO DEBUG                                                                   │
│      Problem with mood? Check mood_agent.py only                                       │
│                                                                                         │
│   3. EASIER TO MODIFY                                                                  │
│      Want to change taste analysis? Only touch taste_preferences_agent.py             │
│                                                                                         │
│   4. PARALLEL EXECUTION                                                                │
│      Agents can run simultaneously (faster!)                                           │
│                                                                                         │
│                                                                                         │
│   IMPORTANT: Most of our agents are NOT AI!                                            │
│   ──────────────────────────────────────────                                            │
│                                                                                         │
│   • Mood Agent: Simple lookup table (no AI)                                            │
│   • Question Agent: Parse strings (no AI)                                              │
│   • Taste Agent: Database queries + statistics (no AI)                                 │
│   • Food Agent: Database queries (no AI)                                               │
│                                                                                         │
│   Only the FINAL step (LLM writing the response) uses AI!                              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Hybrid Retrieval

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS HYBRID RETRIEVAL?                                                             │
│   ─────────────────────────                                                             │
│                                                                                         │
│   Combining MULTIPLE retrieval methods instead of just one:                            │
│                                                                                         │
│   METHOD 1: SQL/Keyword Search (exact filters)                                         │
│   METHOD 2: Vector/Semantic Search (meaning similarity)                                │
│   METHOD 3: Custom Scoring (weighted factors)                                          │
│   METHOD 4: LLM Reranking (final polish)                                               │
│                                                                                         │
│                                                                                         │
│   WHY HYBRID?                                                                           │
│   ───────────                                                                           │
│                                                                                         │
│   Each method has strengths and weaknesses:                                            │
│                                                                                         │
│   SQL Search:                                                                          │
│   ✓ Perfect for exact filters (is_vegetarian = true)                                  │
│   ✗ Can't understand "something healthy"                                              │
│                                                                                         │
│   Vector Search:                                                                       │
│   ✓ Understands meaning ("healthy" → salads, grilled items)                           │
│   ✗ Might return items that violate dietary restrictions                              │
│                                                                                         │
│   Scoring:                                                                             │
│   ✓ Incorporates user preferences and history                                         │
│   ✗ Still needs good candidates to score                                              │
│                                                                                         │
│   LLM:                                                                                 │
│   ✓ Writes compelling, personalized text                                              │
│   ✗ Expensive, slow, can hallucinate without good data                                │
│                                                                                         │
│                                                                                         │
│   HYBRID = Best of all worlds!                                                         │
│   ───────────────────────────                                                           │
│                                                                                         │
│   SQL  →  Guarantees dietary requirements are met                                      │
│   Vector  →  Finds semantically relevant items                                         │
│   Scoring  →  Personalizes based on history                                            │
│   LLM  →  Writes the final recommendation (with REAL data!)                           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Web Scraping

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS WEB SCRAPING?                                                                 │
│   ─────────────────────                                                                 │
│                                                                                         │
│   Automatically extracting data from websites by reading their HTML.                   │
│                                                                                         │
│   Website HTML:                                                                         │
│   <div class="menu-item">                                                              │
│     <h3>Teriyaki Chicken Bowl</h3>                                                     │
│     <span class="tag vegetarian">Vegetarian</span>                                     │
│   </div>                                                                                │
│                                                                                         │
│   Scraper extracts:                                                                     │
│   {                                                                                     │
│     "name": "Teriyaki Chicken Bowl",                                                   │
│     "is_vegetarian": true                                                              │
│   }                                                                                     │
│                                                                                         │
│                                                                                         │
│   OUR TOOLS:                                                                            │
│   ──────────                                                                            │
│                                                                                         │
│   • requests: Fetches the webpage HTML                                                 │
│   • BeautifulSoup: Parses HTML and extracts data                                       │
│   • pandas: Organizes data into tables                                                 │
│                                                                                         │
│                                                                                         │
│   HOW WE USE IT:                                                                        │
│   ──────────────                                                                        │
│                                                                                         │
│   scraper.py runs daily:                                                               │
│   1. Fetches Berkeley dining website                                                   │
│   2. Parses all menu items                                                             │
│   3. Extracts: name, hall, meal, dietary info                                          │
│   4. Saves to Supabase dishes table                                                    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## API (Application Programming Interface)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS AN API?                                                                       │
│   ───────────────                                                                       │
│                                                                                         │
│   A way for programs to talk to each other using standardized requests.                │
│                                                                                         │
│   Think of it like a restaurant:                                                       │
│                                                                                         │
│   Customer          Waiter              Kitchen                                         │
│   (Frontend)        (API)               (Backend)                                       │
│       │                │                    │                                           │
│       │ "I want soup"  │                    │                                           │
│       │───────────────►│                    │                                           │
│       │                │ Takes order        │                                           │
│       │                │───────────────────►│                                           │
│       │                │                    │ Makes soup                                │
│       │                │◄───────────────────│                                           │
│       │                │ Brings soup        │                                           │
│       │◄───────────────│                    │                                           │
│       │                │                    │                                           │
│                                                                                         │
│   You don't need to know HOW the kitchen makes soup.                                   │
│   You just ask the waiter (API) and get a result.                                      │
│                                                                                         │
│                                                                                         │
│   OUR APIS:                                                                             │
│   ─────────                                                                             │
│                                                                                         │
│   1. OUR OWN API (FastAPI backend):                                                    │
│      POST /api/chat    → Get recommendation                                            │
│      GET  /api/menu    → Get dishes                                                    │
│      PUT  /api/profile → Update preferences                                            │
│                                                                                         │
│   2. EXTERNAL APIS WE USE:                                                             │
│      Perplexity API → Send prompt, get AI response                                     │
│      Supabase API   → Database operations                                              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP (Model Context Protocol)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS MCP?                                                                          │
│   ────────────                                                                          │
│                                                                                         │
│   Model Context Protocol is a standard for giving AI models access to                  │
│   external tools and data sources.                                                     │
│                                                                                         │
│   Traditional AI:                                                                       │
│   ─────────────────                                                                     │
│   User → AI → Response (AI only knows its training data)                               │
│                                                                                         │
│   AI with MCP:                                                                          │
│   ──────────────                                                                        │
│   User → AI → [MCP Tools: Database, Files, APIs] → Response                           │
│                                                                                         │
│   MCP lets AI "reach out" and get real-time information!                               │
│                                                                                         │
│                                                                                         │
│   DO WE USE MCP?                                                                        │
│   ──────────────                                                                        │
│                                                                                         │
│   Not directly in the traditional MCP sense. However, our architecture                 │
│   achieves the SAME GOAL through our multi-agent + RAG setup:                          │
│                                                                                         │
│   • We give the LLM access to real data (today's menu)                                 │
│   • We give the LLM access to user preferences (from database)                         │
│   • We control what context the LLM sees                                               │
│                                                                                         │
│   This is essentially what MCP does, but we built it ourselves!                        │
│                                                                                         │
│   MCP CONCEPTS IN OUR PROJECT:                                                         │
│   ─────────────────────────────                                                         │
│                                                                                         │
│   MCP Concept              Our Implementation                                          │
│   ───────────              ──────────────────                                           │
│   Tools                    Agents (mood, taste, food)                                  │
│   Resources                Supabase tables                                             │
│   Context Window           Hybrid retriever output                                     │
│   Prompts                  orchestrator.py builds them                                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Transformer (Neural Network Architecture)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS A TRANSFORMER?                                                                │
│   ──────────────────────                                                                │
│                                                                                         │
│   The neural network architecture behind ALL modern AI:                                │
│   GPT, Claude, BERT, our embedding model—all use Transformers!                         │
│                                                                                         │
│   KEY INNOVATION: ATTENTION MECHANISM                                                   │
│   ───────────────────────────────────                                                   │
│                                                                                         │
│   Input: "The chicken was delicious but the rice was cold"                             │
│                                                                                         │
│   When processing "delicious", attention looks at the whole sentence                   │
│   and figures out that "delicious" refers to "chicken", not "rice".                    │
│                                                                                         │
│   This lets the model understand CONTEXT and RELATIONSHIPS!                            │
│                                                                                         │
│                                                                                         │
│   WHERE WE USE TRANSFORMERS:                                                            │
│   ──────────────────────────                                                            │
│                                                                                         │
│   1. all-MiniLM-L6-v2 (for embeddings)                                                 │
│      A transformer model that converts text → vectors                                  │
│      "L6" means 6 transformer layers                                                   │
│                                                                                         │
│   2. Perplexity Sonar (for recommendations)                                            │
│      A transformer LLM that generates text                                             │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Pydantic (Data Validation)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   WHAT IS PYDANTIC?                                                                     │
│   ─────────────────                                                                     │
│                                                                                         │
│   A Python library that validates data automatically.                                  │
│                                                                                         │
│   WITHOUT PYDANTIC:                                                                     │
│   ─────────────────                                                                     │
│                                                                                         │
│   def create_user(data):                                                               │
│       # Have to manually check everything!                                             │
│       if "email" not in data:                                                          │
│           raise Error("email required")                                                │
│       if not isinstance(data["email"], str):                                           │
│           raise Error("email must be string")                                          │
│       if "@" not in data["email"]:                                                     │
│           raise Error("invalid email")                                                 │
│       # ... 50 more lines of validation                                                │
│                                                                                         │
│                                                                                         │
│   WITH PYDANTIC:                                                                        │
│   ──────────────                                                                        │
│                                                                                         │
│   from pydantic import BaseModel, EmailStr                                             │
│                                                                                         │
│   class User(BaseModel):                                                               │
│       email: EmailStr          # Automatic email validation!                           │
│       is_vegetarian: bool      # Must be true/false                                    │
│       age: int                 # Must be a number                                      │
│                                                                                         │
│   # Pydantic validates automatically:                                                  │
│   user = User(email="test@email.com", is_vegetarian=True, age=21)  # ✓ Works          │
│   user = User(email="not-an-email", ...)  # ✗ Raises validation error                 │
│                                                                                         │
│                                                                                         │
│   HOW WE USE IT:                                                                        │
│   ──────────────                                                                        │
│                                                                                         │
│   FastAPI uses Pydantic for ALL request/response validation:                           │
│                                                                                         │
│   class ChatRequest(BaseModel):                                                        │
│       user_id: str                                                                     │
│       mood: str                                                                        │
│       craving: str                                                                     │
│       spice_level: str                                                                 │
│                                                                                         │
│   @app.post("/api/chat")                                                               │
│   async def chat(request: ChatRequest):  # Pydantic validates automatically!          │
│       ...                                                                              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: AI/ML Concepts in BerkeleyBites

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   CONCEPT              WHERE WE USE IT                   FILE                          │
│   ───────              ─────────────────                 ────                          │
│                                                                                         │
│   RAG                  Entire pipeline                   hybrid_retriever.py           │
│                        (Retrieval + LLM)                 orchestrator.py               │
│                                                                                         │
│   Embeddings           Convert dishes to vectors         embedding_service.py          │
│                        Search by meaning                 dish_embeddings table         │
│                                                                                         │
│   Semantic Search      Find similar dishes               hybrid_retriever.py           │
│                                                          (Stage 2)                     │
│                                                                                         │
│   Cosine Similarity    Compare embeddings                pgvector in Supabase          │
│                                                                                         │
│   pgvector             Store & search vectors            Supabase extension            │
│                                                                                         │
│   LLM                  Write recommendations             Perplexity API                │
│                                                          hybrid_retriever.py (Stage 4) │
│                                                                                         │
│   Multi-Agent          Separate concerns                 agents/ folder                │
│                        Mood, taste, food agents          orchestrator.py               │
│                                                                                         │
│   Hybrid Retrieval     Combine SQL + Vector + Scoring    hybrid_retriever.py           │
│                                                                                         │
│   Web Scraping         Get daily menus                   scraper.py                    │
│                                                                                         │
│   Transformer          Embedding model architecture      all-MiniLM-L6-v2              │
│                        LLM architecture                  Perplexity Sonar              │
│                                                                                         │
│   Pydantic             Validate API requests             backend/main.py               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Interview Answers for AI/ML Terms

**Q: "What is RAG and why did you use it?"**
> RAG stands for Retrieval Augmented Generation. Instead of letting the AI hallucinate dishes that don't exist, we first RETRIEVE real dishes from our database, then AUGMENT the AI prompt with that data, then let the AI GENERATE a response. This guarantees recommendations are for actual dishes available today.

**Q: "How do embeddings work?"**
> Embeddings convert text into numbers (vectors) that capture meaning. Similar meanings become similar numbers. We use all-MiniLM-L6-v2 to convert dishes into 384-dimensional vectors, then use cosine similarity to find dishes that match what the user is craving—even if they use different words.

**Q: "What's the difference between keyword and semantic search?"**
> Keyword search finds exact word matches. Semantic search finds meaning matches. If a user searches "healthy", keyword search only finds dishes containing "healthy". Semantic search finds "Garden Salad" even though it doesn't contain the word—because it understands the meaning.

**Q: "Why use multiple agents instead of one big system?"**
> Separation of concerns. Each agent does one thing well: Mood Agent handles mood logic, Taste Agent analyzes history, Food Agent queries dishes. Easier to debug, test, and modify. Also allows parallel execution for speed.

**Q: "Where does AI actually run in your system?"**
> Only in the final step! The Perplexity LLM writes the recommendation text. Everything else—mood mapping, preference analysis, dish filtering, scoring—is deterministic Python code. This makes the system fast, cheap, and predictable.

---

═══════════════════════════════════════════════════════════════════════════════════════════
                           PART 8: FILE-BY-FILE BREAKDOWN
═══════════════════════════════════════════════════════════════════════════════════════════

This section explains EVERY file in the project, what it does, and how to talk about it.

---

## Project Structure Overview

```
BerkeleyBites/
├── scraper.py                    # Gets menu from Berkeley website
├── food_agent.py                 # Legacy file (can mention: "early prototype")
│
├── backend/                      # Python server (API)
│   ├── __init__.py              # Makes folder a Python package
│   ├── main.py                  # API endpoints (the heart of the backend!)
│   ├── database.py              # Supabase connection and queries
│   └── models.py                # Pydantic models for validation
│
├── agents/                       # AI recommendation system
│   ├── __init__.py              # Package init
│   ├── orchestrator.py          # Coordinates all agents
│   ├── mood_agent.py            # Maps mood to food guidance
│   ├── question_agent.py        # Handles the 4 questions
│   ├── taste_preferences_agent.py  # Analyzes feedback history
│   ├── food_availability_agent.py  # Gets available dishes
│   ├── hybrid_retriever.py      # 4-stage retrieval pipeline
│   ├── scoring.py               # Multi-factor scoring algorithm
│   ├── embedding_service.py     # Creates dish embeddings
│   └── cache.py                 # In-memory caching
│
├── frontend/                     # React app (what users see)
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Main app component
│   │   ├── index.css            # Tailwind CSS styles
│   │   ├── api/
│   │   │   └── client.ts        # HTTP requests to backend
│   │   ├── context/
│   │   │   └── AppContext.tsx   # Shared state management
│   │   ├── hooks/
│   │   │   ├── useChat.ts       # Chat functionality
│   │   │   ├── useMenu.ts       # Menu data fetching
│   │   │   └── useProfile.ts    # Profile management
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript types
│   │   └── components/
│   │       ├── chat/            # Chat UI components
│   │       ├── menu/            # Menu browser components
│   │       ├── profile/         # Profile components
│   │       └── layout/          # Layout components
│   │
│   ├── index.html               # HTML entry point
│   ├── package.json             # Dependencies
│   ├── vite.config.ts           # Build configuration
│   └── tailwind.config.js       # Styling configuration
│
├── tests/                        # Test files
│   └── test_e2e.py              # End-to-end tests
│
├── docs/                         # Documentation (you're reading this!)
├── supabase/                     # Database migrations
├── scripts/                      # Utility scripts
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variables template
```

---

## Backend Files (backend/)

### backend/main.py - "The API Server"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: backend/main.py                                                                 │
│   ─────────────────────                                                                 │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Defines all the API endpoints that the frontend calls.                               │
│   This is the "front door" to the backend.                                             │
│                                                                                         │
│   ENDPOINTS IT CREATES:                                                                 │
│                                                                                         │
│   GET  /api/health       →  "Is the server running?"                                   │
│   GET  /api/menu         →  "Give me today's dishes" (filtered)                        │
│   GET  /api/profile      →  "Get user's dietary preferences"                           │
│   PUT  /api/profile      →  "Update user's preferences"                                │
│   POST /api/feedback     →  "Save 👍/👎 rating"                                        │
│   POST /api/chat         →  "Get AI recommendation" (THE MAIN ONE!)                    │
│                                                                                         │
│   KEY FUNCTIONS:                                                                        │
│   • get_menu() - Queries dishes table, applies filters                                 │
│   • chat() - Calls orchestrator, returns recommendation                                │
│   • update_profile() - Saves preferences to Supabase                                   │
│                                                                                         │
│   TECHNOLOGIES USED:                                                                    │
│   • FastAPI (web framework)                                                            │
│   • Pydantic (request validation)                                                      │
│   • async/await (non-blocking I/O)                                                     │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "main.py is where all HTTP requests land. It validates input with Pydantic,         │
│    calls the appropriate agent or database function, and returns JSON responses."      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### backend/database.py - "The Database Layer"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: backend/database.py                                                             │
│   ─────────────────────────                                                             │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Handles ALL communication with Supabase (our database).                              │
│   Keeps database logic separate from API logic.                                        │
│                                                                                         │
│   KEY FUNCTIONS:                                                                        │
│   • get_supabase_client() - Creates database connection                                │
│   • get_dishes() - Query dishes table                                                  │
│   • get_user_profile() - Get preferences                                               │
│   • save_feedback() - Store 👍/👎 ratings                                              │
│   • get_user_feedback() - Get rating history                                           │
│                                                                                         │
│   TECHNOLOGIES USED:                                                                    │
│   • supabase-py (Python client for Supabase)                                           │
│   • Environment variables for credentials                                              │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "I separated database operations into database.py to follow separation of           │
│    concerns. If we ever switch databases, we only change this file."                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### backend/models.py - "Data Structures"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: backend/models.py                                                               │
│   ───────────────────────                                                               │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Defines Pydantic models for request/response validation.                             │
│   Ensures data has the right shape and types.                                          │
│                                                                                         │
│   KEY MODELS:                                                                           │
│   • ChatRequest - What frontend sends to /api/chat                                     │
│   • ChatResponse - What backend returns                                                │
│   • ProfileUpdate - User preference updates                                            │
│   • Dish - Structure of a dish object                                                  │
│   • Feedback - Structure of a rating                                                   │
│                                                                                         │
│   EXAMPLE:                                                                              │
│   class ChatRequest(BaseModel):                                                        │
│       user_id: str                                                                     │
│       mood: str                                                                        │
│       craving: str                                                                     │
│       spice_level: str                                                                 │
│       time_available: str                                                              │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "Pydantic models give us automatic validation. If someone sends a request           │
│    without user_id, FastAPI automatically returns a 422 error. No manual checks!"     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Files (agents/)

### agents/orchestrator.py - "The Brain"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/orchestrator.py                                                          │
│   ────────────────────────────                                                          │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Coordinates all the other agents. When /api/chat is called,                          │
│   the orchestrator is what runs.                                                       │
│                                                                                         │
│   THE FLOW:                                                                             │
│   1. Receive user input (mood, craving, etc.)                                          │
│   2. Call Mood Agent → get mood interpretation                                         │
│   3. Call Question Agent → parse answers                                               │
│   4. Call Taste Agent → get preference patterns                                        │
│   5. Call Food Agent → get available dishes                                            │
│   6. Call Hybrid Retriever → run 4-stage pipeline                                      │
│   7. Return recommendation to backend                                                  │
│                                                                                         │
│   KEY FUNCTION:                                                                         │
│   async def get_recommendation(user_id, mood, craving, spice, time):                   │
│       # Calls all agents, combines results                                             │
│       # Returns personalized recommendation                                            │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The orchestrator is like a project manager. It doesn't do the work itself—         │
│    it delegates to specialized agents and combines their outputs."                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/mood_agent.py - "The Mood Interpreter"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/mood_agent.py                                                            │
│   ──────────────────────────                                                            │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Converts a mood (like "happy") into food guidance.                                   │
│   Uses a SIMPLE LOOKUP TABLE, not AI!                                                  │
│                                                                                         │
│   THE MAPPING:                                                                          │
│   "happy"    → "Open to new flavors, adventurous choices OK"                           │
│   "stressed" → "Comfort food, familiar favorites"                                      │
│   "tired"    → "Quick energy, light meals"                                             │
│   "focused"  → "Brain food, balanced meals"                                            │
│                                                                                         │
│   KEY FUNCTION:                                                                         │
│   def get_mood_guidance(mood: str) -> str:                                             │
│       return MOOD_MAP.get(mood, "Balanced meal recommended")                           │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "I chose a lookup table instead of AI for the mood agent because the mappings       │
│    are static and well-defined. No need to spend money on an API call for             │
│    something a dictionary can do in microseconds."                                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/question_agent.py - "The Answer Parser"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/question_agent.py                                                        │
│   ──────────────────────────────                                                        │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Parses and structures the user's answers to the 4 questions.                         │
│   Also NOT AI—just simple parsing logic.                                               │
│                                                                                         │
│   THE 4 QUESTIONS:                                                                      │
│   1. What's your mood today?                                                           │
│   2. What are you craving? (healthy, comfort, etc.)                                    │
│   3. Spice preference? (mild, medium, spicy)                                           │
│   4. How much time do you have?                                                        │
│                                                                                         │
│   WHAT IT OUTPUTS:                                                                      │
│   {                                                                                     │
│     "craving": "healthy",                                                              │
│     "spice_level": "mild",                                                             │
│     "time_available": "normal"                                                         │
│   }                                                                                     │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The question agent normalizes user input. If they type 'not too spicy',            │
│    it becomes 'mild'. This standardization makes downstream processing easier."        │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/taste_preferences_agent.py - "The History Analyzer"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/taste_preferences_agent.py                                               │
│   ───────────────────────────────────────                                               │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Analyzes the user's feedback history (👍/👎) to find patterns.                       │
│   Database queries + simple statistics, NOT AI!                                        │
│                                                                                         │
│   WHAT IT FIGURES OUT:                                                                  │
│   • Favorite categories (e.g., "likes Asian food")                                     │
│   • Disliked categories (e.g., "avoids heavy dishes")                                  │
│   • Preference patterns (e.g., "prefers grilled over fried")                           │
│                                                                                         │
│   HOW IT WORKS:                                                                         │
│   1. Query feedback table for user's ratings                                           │
│   2. Group by category, count likes vs dislikes                                        │
│   3. Calculate preference scores                                                       │
│   4. Return summary                                                                    │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The taste agent learns from user behavior. If you keep liking Asian dishes,        │
│    the system remembers that and weights future recommendations accordingly."          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/food_availability_agent.py - "The Menu Scout"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/food_availability_agent.py                                               │
│   ───────────────────────────────────────                                               │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Queries what's actually available TODAY from the database.                           │
│   Applies dietary filters (vegetarian, nut-free, etc.)                                 │
│                                                                                         │
│   KEY FUNCTION:                                                                         │
│   def get_available_dishes(                                                            │
│       user_profile,      # dietary restrictions                                        │
│       dining_hall=None,  # optional filter                                             │
│       meal_period=None   # breakfast/lunch/dinner                                      │
│   ):                                                                                   │
│                                                                                         │
│   WHAT IT RETURNS:                                                                      │
│   • List of dishes matching all filters                                                │
│   • Count by category                                                                  │
│   • Summary: "245 dishes today, 120 vegetarian"                                        │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The food agent is the reality check. It ensures we only recommend                  │
│    dishes that actually exist today and meet the user's dietary needs."               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/hybrid_retriever.py - "The 4-Stage Pipeline"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/hybrid_retriever.py                                                      │
│   ────────────────────────────────                                                      │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Runs the 4-stage retrieval pipeline that finds the best dishes.                      │
│   THIS IS WHERE THE MAGIC HAPPENS!                                                     │
│                                                                                         │
│   THE 4 STAGES:                                                                         │
│                                                                                         │
│   STAGE 1: SQL FILTERS                                                                 │
│   ─────────────────────                                                                 │
│   • Apply dietary restrictions (vegetarian, nut-free)                                  │
│   • Filter by meal period, dining hall                                                 │
│   • 245 dishes → 180 dishes                                                            │
│                                                                                         │
│   STAGE 2: VECTOR SEARCH                                                               │
│   ──────────────────────                                                                │
│   • Convert craving to embedding                                                       │
│   • Compare to all dish embeddings                                                     │
│   • Keep top 30 semantically similar                                                   │
│   • 180 dishes → 30 candidates                                                         │
│                                                                                         │
│   STAGE 3: SCORING                                                                     │
│   ────────────────                                                                      │
│   • Apply weighted scoring (see scoring.py)                                            │
│   • Consider taste preferences, mood, craving                                          │
│   • 30 candidates → 8 top dishes                                                       │
│                                                                                         │
│   STAGE 4: LLM REFINEMENT                                                              │
│   ───────────────────────                                                               │
│   • Send top dishes + context to Perplexity                                            │
│   • LLM writes personalized recommendation                                             │
│   • 8 dishes → 3-4 recommendations with explanation                                    │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The hybrid retriever combines SQL precision with semantic understanding.            │
│    SQL guarantees no dietary violations, vectors understand meaning,                   │
│    scoring personalizes, and the LLM makes it human-readable."                         │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/scoring.py - "The Ranking Algorithm"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/scoring.py                                                               │
│   ───────────────────────                                                               │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Calculates a numerical score for each dish based on multiple factors.                │
│                                                                                         │
│   THE FORMULA:                                                                          │
│                                                                                         │
│   SCORE = (taste_preference × 0.30)    ← User's history with this type                │
│         + (craving_match × 0.25)       ← Matches what they want?                       │
│         + (mood_alignment × 0.15)      ← Good for their mood?                          │
│         + (category_preference × 0.10) ← Favorite category?                            │
│         + (spice_match × 0.10)         ← Right spice level?                            │
│         + (embedding_similarity × 0.05)← Semantic match                                │
│         + (novelty_bonus × 0.05)       ← Haven't tried before?                         │
│         - (dislike_penalty × 0.30)     ← Did they dislike this before?                │
│                                                                                         │
│   WHY THESE WEIGHTS?                                                                   │
│   • Taste preference (30%): Past behavior is best predictor                            │
│   • Craving match (25%): They told us what they want                                   │
│   • Mood (15%): Important but not dominant                                             │
│   • Others (5-10%): Fine-tuning factors                                                │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The weights were determined through testing. Taste history is weighted             │
│    highest because past behavior predicts future preferences better than              │
│    stated preferences."                                                                │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/embedding_service.py - "The Vector Generator"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/embedding_service.py                                                     │
│   ─────────────────────────────────                                                     │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Converts text (dish names, cravings) into embedding vectors.                         │
│   Uses the all-MiniLM-L6-v2 model.                                                     │
│                                                                                         │
│   KEY FUNCTIONS:                                                                        │
│   • get_embedding(text) → Returns 384-dim vector                                       │
│   • generate_dish_embeddings() → Batch process all dishes                              │
│   • calculate_similarity(vec1, vec2) → Cosine similarity                               │
│                                                                                         │
│   WHEN IT RUNS:                                                                         │
│   1. Daily: After scraper runs, embed all new dishes                                   │
│   2. Per request: Embed user's craving for comparison                                  │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "We use sentence-transformers because it runs locally (free!) and                   │
│    produces high-quality embeddings. The 384 dimensions capture semantic              │
│    meaning well enough for food matching."                                             │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### agents/cache.py - "The Speed Booster"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: agents/cache.py                                                                 │
│   ─────────────────────                                                                 │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Stores frequently accessed data in memory to avoid repeated database calls.          │
│                                                                                         │
│   WHAT WE CACHE:                                                                        │
│   • Menu data (refreshes every 5 minutes)                                              │
│   • Dish embeddings (refreshes daily)                                                  │
│   • User profiles (refreshes every 1 minute)                                           │
│                                                                                         │
│   HOW IT WORKS:                                                                         │
│   cache = {}                                                                           │
│   cache_timestamps = {}                                                                │
│                                                                                         │
│   def get_cached(key, fetch_func, ttl=300):                                            │
│       if key in cache and not expired:                                                 │
│           return cache[key]  # Fast!                                                   │
│       else:                                                                            │
│           data = fetch_func()  # Slow (DB call)                                        │
│           cache[key] = data                                                            │
│           return data                                                                  │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "Caching reduces database load and improves response time. The menu                 │
│    only changes a few times a day, so there's no reason to query it                   │
│    on every request."                                                                  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Root Files

### scraper.py - "The Data Collector"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: scraper.py                                                                      │
│   ────────────────                                                                      │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Visits the Berkeley dining website and extracts today's menu.                        │
│   Runs daily (or on-demand).                                                           │
│                                                                                         │
│   THE PROCESS:                                                                          │
│   1. Send HTTP request to Berkeley dining URL                                          │
│   2. Parse HTML with BeautifulSoup                                                     │
│   3. Extract: dish name, dining hall, meal, dietary tags                               │
│   4. Clean and normalize data                                                          │
│   5. Save to Supabase dishes table                                                     │
│                                                                                         │
│   TECHNOLOGIES:                                                                         │
│   • requests (HTTP library)                                                            │
│   • BeautifulSoup (HTML parser)                                                        │
│   • pandas (data manipulation)                                                         │
│                                                                                         │
│   CHALLENGES:                                                                           │
│   • Website structure changes (need to update selectors)                               │
│   • Rate limiting (be respectful)                                                      │
│   • Data cleaning (inconsistent naming)                                                │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "Scraping was trickier than expected. The Berkeley site uses dynamic                │
│    elements, so I had to analyze the HTML structure carefully. I also                 │
│    added error handling for when the site is down or changes format."                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Files (frontend/src/)

### App.tsx - "The Root Component"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/App.tsx                                                            │
│   ──────────────────────────                                                            │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   The main React component that renders the entire app.                                │
│   Sets up the component tree and context provider.                                     │
│                                                                                         │
│   STRUCTURE:                                                                            │
│   <AppProvider>           ← Context for shared state                                   │
│     <AppShell>            ← Layout wrapper                                             │
│       <Header />          ← Top bar with mood                                          │
│       <ChatPanel />       ← Left side: chat/recommendations                            │
│       <MenuBrowser />     ← Right side: menu browsing                                  │
│     </AppShell>                                                                        │
│   </AppProvider>                                                                       │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "App.tsx is minimal by design. It just sets up the structure and lets              │
│    child components handle their own logic. This makes testing easier."               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### context/AppContext.tsx - "The State Manager"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/context/AppContext.tsx                                             │
│   ─────────────────────────────────────────                                             │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   React Context that holds all shared state.                                           │
│   Any component can access this data without prop drilling.                            │
│                                                                                         │
│   STATE IT MANAGES:                                                                     │
│   • user_id: Current user identifier                                                   │
│   • profile: Dietary preferences                                                       │
│   • mood: Current mood                                                                 │
│   • chatMessages: Chat history                                                         │
│   • menuData: Fetched dishes                                                           │
│   • isLoading: Loading states                                                          │
│   • selectedHall: Filter state                                                         │
│   • selectedMeal: Filter state                                                         │
│                                                                                         │
│   WHY CONTEXT INSTEAD OF REDUX?                                                        │
│   • Simpler for this app size                                                          │
│   • No extra dependencies                                                              │
│   • Easier to understand                                                               │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "I chose Context over Redux because the app isn't large enough to need              │
│    Redux's complexity. Context handles our state needs without boilerplate."          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### api/client.ts - "The Backend Communicator"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/api/client.ts                                                      │
│   ────────────────────────────────                                                      │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Contains all functions that call the backend API.                                    │
│   Uses fetch() with proper error handling.                                             │
│                                                                                         │
│   FUNCTIONS:                                                                            │
│   • fetchMenu(filters) → GET /api/menu                                                 │
│   • getProfile(userId) → GET /api/profile                                              │
│   • updateProfile(userId, data) → PUT /api/profile                                     │
│   • submitFeedback(data) → POST /api/feedback                                          │
│   • sendChatMessage(data) → POST /api/chat                                             │
│                                                                                         │
│   EXAMPLE:                                                                              │
│   export async function sendChatMessage(request: ChatRequest) {                        │
│     const response = await fetch('/api/chat', {                                        │
│       method: 'POST',                                                                  │
│       headers: { 'Content-Type': 'application/json' },                                 │
│       body: JSON.stringify(request)                                                    │
│     });                                                                                │
│     if (!response.ok) throw new Error('Chat failed');                                  │
│     return response.json();                                                            │
│   }                                                                                    │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "I centralized API calls in client.ts to keep components clean.                     │
│    Components just call fetchMenu() without knowing HTTP details."                    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### components/chat/ChatPanel.tsx - "The Chat Interface"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/components/chat/ChatPanel.tsx                                      │
│   ────────────────────────────────────────────────                                      │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   The main chat interface where users interact with the AI.                            │
│   Shows questions, answers, and recommendations.                                       │
│                                                                                         │
│   KEY FEATURES:                                                                         │
│   • Displays chat message history                                                      │
│   • Shows the 4 questions with answer options                                          │
│   • Displays loading state while AI thinks                                             │
│   • Renders recommendation with agent summaries                                        │
│   • "New Chat" button to start over                                                    │
│                                                                                         │
│   SUB-COMPONENTS:                                                                       │
│   • ChatMessage.tsx - Individual message bubble                                        │
│   • ChatInput.tsx - Text input (if using free text)                                    │
│   • QuestionMessage.tsx - Question with button options                                 │
│   • AgentSummaryCard.tsx - Shows agent analysis results                                │
│   • RecommendationMessage.tsx - Final recommendation display                           │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "ChatPanel orchestrates the question flow. It tracks which question                 │
│    we're on, collects answers, and triggers the recommendation when done."            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### components/menu/MenuBrowser.tsx - "The Menu Explorer"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/components/menu/MenuBrowser.tsx                                    │
│   ──────────────────────────────────────────────────                                    │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Lets users browse the full menu (separate from AI recommendations).                  │
│   Filter by dining hall, meal, and category.                                           │
│                                                                                         │
│   SUB-COMPONENTS:                                                                       │
│   • DiningHallSelect.tsx - Dropdown to pick hall                                       │
│   • MealTabs.tsx - Breakfast/Lunch/Dinner tabs                                         │
│   • CategorySection.tsx - Groups dishes by category                                    │
│   • DishCard.tsx - Individual dish with 👍/👎 buttons                                  │
│                                                                                         │
│   USER FLOW:                                                                            │
│   1. Select dining hall (or "All")                                                     │
│   2. Click meal tab                                                                    │
│   3. Browse dishes by category                                                         │
│   4. Click 👍 or 👎 to rate                                                            │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "The menu browser serves two purposes: users can explore freely, and                │
│    their 👍/👎 ratings feed into the AI's taste learning system."                      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### components/menu/DishCard.tsx - "The Dish Display"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/components/menu/DishCard.tsx                                       │
│   ───────────────────────────────────────────────                                       │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Displays a single dish with dietary tags and feedback buttons.                       │
│                                                                                         │
│   WHAT IT SHOWS:                                                                        │
│   • Dish name                                                                          │
│   • Dietary tags (🥬 vegetarian, 🥜 contains nuts, etc.)                               │
│   • Dining hall and category                                                           │
│   • 👍 and 👎 buttons                                                                  │
│                                                                                         │
│   ON CLICK:                                                                             │
│   User clicks 👍 → calls submitFeedback(dish_id, liked=true)                          │
│   User clicks 👎 → calls submitFeedback(dish_id, liked=false)                         │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "DishCard is intentionally simple. It just displays data and handles               │
│    feedback clicks. The actual API call is delegated to the parent."                  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### hooks/useChat.ts - "The Chat Logic Hook"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/hooks/useChat.ts                                                   │
│   ───────────────────────────────────                                                   │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Custom React hook that encapsulates all chat logic.                                  │
│   Handles state, API calls, and message flow.                                          │
│                                                                                         │
│   WHAT IT PROVIDES:                                                                     │
│   const {                                                                              │
│     messages,           // Chat history                                                │
│     isLoading,         // Waiting for API                                              │
│     currentQuestion,   // Which question (1-4)                                         │
│     sendMessage,       // Function to send answer                                      │
│     startNewChat,      // Reset function                                               │
│     recommendation     // AI recommendation                                            │
│   } = useChat();                                                                       │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "useChat is a custom hook that separates logic from UI. ChatPanel.tsx               │
│    just renders based on the hook's state—it doesn't manage state itself."            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### types/index.ts - "The TypeScript Types"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE: frontend/src/types/index.ts                                                     │
│   ─────────────────────────────────                                                     │
│                                                                                         │
│   WHAT IT DOES:                                                                         │
│   Defines TypeScript interfaces for all data structures.                               │
│   Ensures type safety across the frontend.                                             │
│                                                                                         │
│   KEY TYPES:                                                                            │
│   interface Dish {                                                                     │
│     id: number;                                                                        │
│     dish_name: string;                                                                 │
│     dining_hall: string;                                                               │
│     meal_period: string;                                                               │
│     is_vegetarian: boolean;                                                            │
│     // ...                                                                             │
│   }                                                                                    │
│                                                                                         │
│   interface ChatResponse {                                                             │
│     recommendation: string;                                                            │
│     agent_summaries: AgentSummary[];                                                   │
│   }                                                                                    │
│                                                                                         │
│   INTERVIEW TALKING POINT:                                                             │
│   "TypeScript catches errors at compile time. If the backend changes a                │
│    field name, TypeScript tells me immediately rather than failing at runtime."       │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: What Each File Does

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   FILE                          ONE-LINE DESCRIPTION                                    │
│   ────                          ────────────────────                                    │
│                                                                                         │
│   BACKEND                                                                               │
│   backend/main.py               API endpoints (FastAPI)                                │
│   backend/database.py           Database operations (Supabase)                         │
│   backend/models.py             Request/response validation (Pydantic)                 │
│                                                                                         │
│   AGENTS                                                                                │
│   agents/orchestrator.py        Coordinates all agents                                 │
│   agents/mood_agent.py          Mood → food guidance (lookup table)                    │
│   agents/question_agent.py      Parse user's answers                                   │
│   agents/taste_preferences_agent.py  Analyze feedback history                          │
│   agents/food_availability_agent.py  Get available dishes                              │
│   agents/hybrid_retriever.py    4-stage retrieval pipeline                             │
│   agents/scoring.py             Calculate dish scores                                  │
│   agents/embedding_service.py   Generate embeddings (all-MiniLM-L6-v2)                │
│   agents/cache.py               In-memory caching                                      │
│                                                                                         │
│   ROOT                                                                                  │
│   scraper.py                    Scrape Berkeley dining website                         │
│                                                                                         │
│   FRONTEND                                                                              │
│   App.tsx                       Root component, sets up structure                      │
│   context/AppContext.tsx        Shared state (React Context)                           │
│   api/client.ts                 HTTP requests to backend                               │
│   hooks/useChat.ts              Chat logic hook                                        │
│   hooks/useMenu.ts              Menu fetching hook                                     │
│   hooks/useProfile.ts           Profile management hook                                │
│   types/index.ts                TypeScript type definitions                            │
│   components/chat/*             Chat UI components                                     │
│   components/menu/*             Menu browser components                                │
│   components/profile/*          Profile editor components                              │
│   components/layout/*           Layout components (Header, AppShell)                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## One-Sentence Summary

> **BerkeleyBites scrapes the daily menu, embeds dishes for semantic search, then uses a multi-agent system to gather context (mood, preferences, availability), runs a 4-stage hybrid retrieval pipeline (SQL → Vectors → Scoring → LLM), and delivers a personalized food recommendation—all powered by RAG to prevent AI hallucination.**

---

**Good luck with your interview! You've got this!**
