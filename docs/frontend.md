# Frontend Guide (Beginner-Friendly)

This document explains the user interface of BerkeleyBites - what users see and interact with.

---

## What is a "Frontend"?

The **frontend** is everything users see and interact with in their browser:
- Buttons they click
- Text they read
- Forms they fill out
- Colors, layouts, animations

Think of it like the dining room of a restaurant - it's what customers experience, while the kitchen (backend) does the cooking.

---

## Technologies Used

| Technology | What It Does | Why We Use It |
|------------|--------------|---------------|
| **React** | Builds the user interface | Most popular UI library, lots of jobs use it |
| **TypeScript** | Adds type checking to JavaScript | Catches bugs before they happen |
| **Tailwind CSS** | Styles the UI with utility classes | Fast to write, consistent design |
| **Vite** | Development server and build tool | Super fast, great developer experience |

### What is React?

React is a JavaScript library for building user interfaces. Its key idea:

**UI = function of data**

When data changes, the UI automatically updates.

```jsx
// This is a React component
function Counter() {
  const [count, setCount] = useState(0);  // State: data that can change

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}

// When count changes, the button text automatically updates!
```

### What is TypeScript?

TypeScript is JavaScript with type checking:

```typescript
// JavaScript - no error until you run it
function greet(name) {
  return "Hello, " + name.toUppercase();  // Bug: toUppercase should be toUpperCase
}

// TypeScript - catches the error while you write
function greet(name: string): string {
  return "Hello, " + name.toUppercase();  // ERROR: toUppercase doesn't exist
}
```

### What is Tailwind CSS?

Traditional CSS:
```css
/* styles.css */
.button {
  background-color: blue;
  padding: 8px 16px;
  border-radius: 8px;
  color: white;
}
```

Tailwind CSS:
```html
<!-- No separate CSS file needed -->
<button class="bg-blue-500 px-4 py-2 rounded-lg text-white">
  Click me
</button>
```

Benefits:
- Faster to write
- No naming conflicts
- Easy to see styles in the HTML

---

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point (starts the app)
│   ├── App.tsx               # Main component (root of UI tree)
│   ├── index.css             # Global styles
│   │
│   ├── api/
│   │   └── client.ts         # Talks to the backend
│   │
│   ├── context/
│   │   └── AppContext.tsx    # Shared state (data used by many components)
│   │
│   ├── hooks/
│   │   └── useChat.ts        # Chat logic
│   │
│   ├── types/
│   │   └── index.ts          # TypeScript type definitions
│   │
│   └── components/
│       ├── layout/           # Page structure
│       │   ├── AppShell.tsx     # Main container
│       │   └── Header.tsx       # Top navigation
│       │
│       ├── chat/             # AI chat interface
│       │   ├── ChatPanel.tsx    # The chat window
│       │   ├── ChatInput.tsx    # Where you type messages
│       │   ├── ChatMessage.tsx  # Individual messages
│       │   └── AgentProgress.tsx # Shows agent status
│       │
│       ├── menu/             # Menu browsing
│       │   ├── MenuBrowser.tsx  # Main menu view
│       │   ├── DishCard.tsx     # Single dish display
│       │   └── MealTabs.tsx     # Breakfast/Lunch/Dinner tabs
│       │
│       └── profile/          # User settings
│           ├── ProfileEditor.tsx   # Edit preferences
│           └── FeedbackStats.tsx   # Your rating history
│
├── package.json              # Dependencies list
├── vite.config.ts            # Build configuration
├── tsconfig.json             # TypeScript configuration
└── index.html                # The HTML page that loads React
```

---

## How Files Connect

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              index.html                                      │
│                                                                             │
│   The browser loads this file first. It has one empty div:                  │
│   <div id="root"></div>                                                     │
│                                                                             │
│   And a script tag that loads main.tsx                                      │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              main.tsx                                        │
│                                                                             │
│   Renders the React app into the #root div:                                 │
│                                                                             │
│   ReactDOM.createRoot(document.getElementById('root')).render(              │
│     <App />                                                                 │
│   );                                                                        │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              App.tsx                                         │
│                                                                             │
│   The main component that contains everything:                              │
│                                                                             │
│   function App() {                                                          │
│     return (                                                                │
│       <AppProvider>              {/* Provides shared state */}              │
│         <AppShell>               {/* Layout wrapper */}                     │
│           <ChatPanel />          {/* AI chat */}                            │
│           <MenuBrowser />        {/* Browse menu */}                        │
│           <ProfileEditor />      {/* Settings */}                           │
│         </AppShell>                                                         │
│       </AppProvider>                                                        │
│     );                                                                      │
│   }                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key File Explanations

### 1. `api/client.ts` - Talking to the Backend

This file contains functions that communicate with the backend server.

```typescript
// The base URL for all API calls
const API_BASE = '/api';  // Vite proxies this to localhost:8000

// Helper function to make requests
async function apiFetch<T>(endpoint: string, options = {}): Promise<T> {
  const userId = getUserId();  // Get user ID from localStorage

  const response = await fetch(`${API_BASE}${endpoint}?user_id=${userId}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Specific API functions
export const getMenu = () => apiFetch<Dish[]>('/menu');
export const getProfile = () => apiFetch<UserProfile>('/profile');
export const submitFeedback = (dishId: number, liked: boolean) =>
  apiFetch('/feedback', {
    method: 'POST',
    body: JSON.stringify({ dish_id: dishId, liked }),
  });
```

**Key Concept: User ID**

Since we don't have login, we generate a random ID and store it:

```typescript
function getUserId(): string {
  let userId = localStorage.getItem('berkeleybites_user_id');

  if (!userId) {
    // Generate new ID: "user_1706987234_abc123"
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('berkeleybites_user_id', userId);
  }

  return userId;
}
```

---

### 2. `context/AppContext.tsx` - Shared State

React Context lets you share data across many components without passing it through each one.

```typescript
// What data is shared
interface AppContextType {
  // User's dietary preferences
  profile: UserProfile;
  setProfile: (profile: UserProfile) => Promise<void>;

  // Current mood
  mood: string;
  setMood: (mood: string) => Promise<void>;

  // Menu data
  menuSummary: MenuSummary | null;

  // Chat messages (temporary, in memory only)
  chatMessages: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;

  // Loading states
  isLoading: boolean;
  error: string | null;
}

// Create the context
const AppContext = createContext<AppContextType | null>(null);

// Provider component (wraps the app)
export function AppProvider({ children }) {
  const [profile, setProfileState] = useState<UserProfile>(defaultProfile);
  const [mood, setMoodState] = useState('happy');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);

  // Update profile (saves to backend)
  const setProfile = async (newProfile: UserProfile) => {
    setProfileState(newProfile);
    await updateProfile(newProfile);  // API call
    localStorage.setItem('profile', JSON.stringify(newProfile));  // Cache locally
  };

  return (
    <AppContext.Provider value={{
      profile, setProfile,
      mood, setMood,
      chatMessages, addChatMessage: (msg) => setChatMessages([...chatMessages, msg]),
      // ... etc
    }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
```

**Usage in a component:**

```tsx
function ProfileEditor() {
  const { profile, setProfile } = useApp();  // Get data from context

  return (
    <label>
      <input
        type="checkbox"
        checked={profile.is_vegetarian}
        onChange={() => setProfile({ ...profile, is_vegetarian: !profile.is_vegetarian })}
      />
      Vegetarian
    </label>
  );
}
```

---

### 3. `components/chat/ChatPanel.tsx` - The Chat Interface

This is where users interact with the AI.

```tsx
function ChatPanel() {
  const { chatMessages, addChatMessage, isChatLoading } = useApp();
  const [inputValue, setInputValue] = useState('');

  // Send a message
  const handleSend = async () => {
    if (!inputValue.trim()) return;

    // Add user message to UI immediately
    addChatMessage({ role: 'user', content: inputValue });
    setInputValue('');

    // Send to backend and wait for response
    const response = await sendChatMessage(inputValue);

    // Add AI response to UI
    if (response.response_type === 'question') {
      addChatMessage({
        role: 'assistant',
        content: response.question_text,
        isQuestion: true,
        options: response.options,
      });
    } else {
      addChatMessage({
        role: 'assistant',
        content: response.recommendation,
        isRecommendation: true,
        agentSummaries: response.agent_summaries,
      });
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {isChatLoading && <div>Thinking...</div>}
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask for a recommendation..."
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>
    </div>
  );
}
```

---

### 4. `components/menu/DishCard.tsx` - Displaying a Dish

```tsx
interface DishCardProps {
  dish: Dish;
}

function DishCard({ dish }: DishCardProps) {
  const [feedback, setFeedback] = useState<'liked' | 'disliked' | null>(null);

  // Handle like/dislike
  const handleFeedback = async (liked: boolean) => {
    await submitFeedback(dish.dish_id, dish.dish_name, liked);
    setFeedback(liked ? 'liked' : 'disliked');
  };

  // Collect dietary badges
  const badges = [];
  if (dish.is_vegan) badges.push({ label: 'Vegan', color: 'green' });
  else if (dish.is_vegetarian) badges.push({ label: 'Vegetarian', color: 'green' });
  if (dish.has_gluten) badges.push({ label: 'Gluten', color: 'amber' });
  if (dish.has_nuts) badges.push({ label: 'Nuts', color: 'amber' });

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Name and location */}
      <h3 className="font-semibold text-lg">{dish.dish_name}</h3>
      <p className="text-gray-600 text-sm">
        {dish.dining_hall} • {dish.category}
      </p>

      {/* Badges */}
      <div className="flex gap-1 mt-2">
        {badges.map((badge) => (
          <span
            key={badge.label}
            className={`px-2 py-1 text-xs rounded bg-${badge.color}-100 text-${badge.color}-800`}
          >
            {badge.label}
          </span>
        ))}
      </div>

      {/* Feedback buttons */}
      <div className="flex gap-2 mt-3">
        <button
          onClick={() => handleFeedback(true)}
          className={`p-2 rounded ${feedback === 'liked' ? 'bg-green-100' : ''}`}
        >
          👍
        </button>
        <button
          onClick={() => handleFeedback(false)}
          className={`p-2 rounded ${feedback === 'disliked' ? 'bg-red-100' : ''}`}
        >
          👎
        </button>
      </div>
    </div>
  );
}
```

---

## State Management Explained

State is data that can change. React re-renders the UI when state changes.

### Three Layers of State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: localStorage (Browser Storage)                                      │
│                                                                             │
│ Persists across browser sessions (even if you close the browser)           │
│                                                                             │
│ What we store:                                                              │
│ • user_id: Unique identifier for this user                                 │
│ • profile: Cached dietary preferences (for fast initial load)              │
│ • mood: Cached current mood                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: React Context (In-Memory)                                           │
│                                                                             │
│ Shared across components, but lost on page refresh                         │
│                                                                             │
│ What we store:                                                              │
│ • profile: Current dietary preferences                                     │
│ • mood: Current mood                                                        │
│ • menuSummary: Today's menu overview                                       │
│ • chatMessages: Conversation history (ephemeral)                           │
│ • loading states: isLoading, error                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: Backend Database (Supabase)                                         │
│                                                                             │
│ Source of truth, persists forever                                          │
│                                                                             │
│ What we store:                                                              │
│ • user_profiles: Dietary preferences                                       │
│ • user_moods: Current mood                                                  │
│ • feedback: All likes/dislikes                                             │
│ • dishes: Today's menu                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How Data Syncs

```
App Load:
1. Read from localStorage (instant, cached values)
2. Display UI immediately with cached data
3. Fetch from backend (latest data)
4. Update UI + localStorage with fresh data

Profile Update:
1. User changes a setting
2. Update React state (UI updates immediately)
3. Save to localStorage (for next visit)
4. POST to backend (persist to database)
```

---

## Design Choices & Why

### Why React Context instead of Redux?

| React Context | Redux |
|--------------|-------|
| Simple setup | More boilerplate |
| Built into React | Separate library |
| Good for small/medium apps | Good for large, complex apps |

BerkeleyBites has ~10 pieces of global state - Context is sufficient.

### Why TypeScript instead of JavaScript?

| TypeScript | JavaScript |
|------------|------------|
| Catches bugs at compile time | Bugs appear at runtime |
| Better IDE autocomplete | Limited autocomplete |
| Self-documenting code | Need comments for types |
| Steeper learning curve | Easier to start |

For a production app, TypeScript's benefits outweigh the learning curve.

### Why Tailwind instead of CSS/Bootstrap?

| Tailwind | Traditional CSS | Bootstrap |
|----------|----------------|-----------|
| Classes in HTML | Separate files | Predefined components |
| Highly customizable | Fully custom | Limited customization |
| No naming conflicts | Need BEM or similar | Some naming conventions |
| Small final bundle | Can get large | Medium size |

Tailwind is fast to write and produces consistent designs.

---

## Potential Improvements

### 1. Better Error Handling
**Current:** Basic error messages
**Improvement:** Toast notifications, retry buttons, offline support

### 2. Loading States
**Current:** Simple "Loading..." text
**Improvement:** Skeleton loaders, progress indicators

### 3. Accessibility
**Current:** Basic accessibility
**Improvement:** Screen reader support, keyboard navigation, ARIA labels

### 4. Testing
**Current:** Manual testing
**Improvement:** Unit tests (Jest), component tests (Testing Library), E2E tests (Playwright)

### 5. State Management
**Current:** React Context
**Improvement:** Could migrate to Zustand or Redux for more complex features

---

## Running the Frontend

### Development

```bash
cd frontend
npm install    # Install dependencies
npm run dev    # Start dev server at localhost:5173
```

### Production Build

```bash
npm run build  # Creates optimized files in /dist
```

### Key Configuration Files

**package.json** - Dependencies and scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  }
}
```

**vite.config.ts** - Build configuration
```typescript
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'  // Forward API calls to backend
    }
  }
});
```

**tsconfig.json** - TypeScript configuration
```json
{
  "compilerOptions": {
    "strict": true,        // Enable all strict checks
    "jsx": "react-jsx",    // React 17+ JSX transform
    "target": "ES2020"     // Modern JavaScript
  }
}
```
