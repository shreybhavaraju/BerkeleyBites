name: frontend-design
description: Create distinctive, production-grade frontend interfaces using UC Berkeley brand guidelines. Use this skill when the user asks to build web components, pages, or applications for BerkeleyBites.
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(bun:*), Bash(npm:*), mcp__shadcn__*
---

This skill guides creation of distinctive, production-grade frontend interfaces using **UC Berkeley brand colors and typography** with a light mode, minimalistic aesthetic. Implement real working code with exceptional attention to aesthetic details.

## BerkeleyBites Project Stack

**Tech Stack:**
- React 19 + Vite + Tailwind CSS v4
- TypeScript
- shadcn/ui components (use shadcn MCP tools to search, view, and get add commands)

**Directory Structure:**
```
frontend/src/
├── api/           # API client functions
├── assets/        # Static assets
├── components/    # Reusable UI components
├── context/       # React context providers
├── hooks/         # Custom React hooks
├── types/         # TypeScript type definitions
├── App.tsx        # Main app component
├── main.tsx       # Entry point
└── index.css      # Global styles
```

---

## Design Philosophy: UC Berkeley Brand

**Core Principles:**
- **Light backgrounds** - Clean whites and soft grays as base
- **Berkeley Blue & California Gold** - Primary brand colors for accents and CTAs
- **Clear typography** - Source Serif Pro for headlines, Source Sans Pro for body
- **Generous white space** - Let content breathe
- **Subtle shadows** - Soft depth, not harsh drop shadows
- **Rounded corners** - Consistent 8-12px radius

**NEVER:**
- Dark mode or neon aesthetics
- Colors that clash with Berkeley Blue/Gold
- Overly busy layouts with competing elements
- Generic AI aesthetics

---

## UC Berkeley Color System

### Primary Colors

```css
/* Berkeley Blue - Primary brand color */
--berkeley-blue: #003262;

/* California Gold - Secondary brand color */
--california-gold: #FDB515;
```

### Extended Palette

```css
/* Founders Rock - Lighter blue for accents */
--founders-rock: #3B7EA1;

/* Medalist - Darker gold for hover states */
--medalist: #C4820E;

/* Web Gray - For muted text and borders */
--web-gray: #888888;

/* Wellman Tile - Warm accent */
--wellman-tile: #D9661F;

/* Lawrence - Cyan accent */
--lawrence: #00B0DA;

/* Sather Gate - Soft green for success states */
--sather-gate: #B9D3B6;
```

### Semantic Color Mapping

```css
--background: #FAFAFA;          /* Near white */
--foreground: #003262;          /* Berkeley Blue for headings */
--muted: #6b7280;               /* Gray for body text */
--muted-foreground: #888888;    /* Web Gray */
--primary: #003262;             /* Berkeley Blue */
--primary-foreground: #ffffff;
--secondary: #FDB515;           /* California Gold */
--secondary-foreground: #003262;
--accent: #3B7EA1;              /* Founders Rock */
--accent-foreground: #ffffff;
--card: #ffffff;
--card-shadow: 0 2px 8px rgba(0, 50, 98, 0.08);
--success: #B9D3B6;             /* Sather Gate */
--warning: #FDB515;             /* California Gold */
--error: #D9661F;               /* Wellman Tile */
```

---

## Typography System

### Font Stack

Use Google Fonts for free alternatives to UC Berkeley's licensed fonts:

```css
/* Headlines - Source Serif Pro (similar to Freight Text Pro) */
font-family: 'Source Serif Pro', Georgia, serif;

/* Body - Source Sans Pro (similar to Proxima Nova) */
font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Include in index.html:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&family=Source+Serif+Pro:wght@600;700&display=swap" rel="stylesheet">
```

### Typography Scale

```css
/* Headlines */
h1: text-5xl font-bold font-serif     /* 48px */
h2: text-4xl font-bold font-serif     /* 36px */
h3: text-2xl font-semibold font-serif /* 24px */
h4: text-xl font-semibold             /* 20px */

/* Body */
body: text-base font-sans             /* 16px */
small: text-sm                        /* 14px */
caption: text-xs                      /* 12px */

/* Line heights */
leading-tight: 1.25
leading-normal: 1.5
leading-relaxed: 1.75
```

---

## Component Patterns

### Navigation
```tsx
<nav className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100">
  <Logo /> {/* Berkeley Blue */}
  <div className="flex items-center gap-8">
    <NavLinks /> {/* text-sm font-medium text-muted hover:text-berkeley-blue */}
  </div>
  <Button className="bg-berkeley-blue text-white">Get Started</Button>
</nav>
```

### Primary Button (Berkeley Blue)
```tsx
<button className="bg-[#003262] text-white rounded-lg px-6 py-3 font-semibold hover:bg-[#003262]/90 transition-colors">
  Primary Action
</button>
```

### Secondary Button (California Gold)
```tsx
<button className="bg-[#FDB515] text-[#003262] rounded-lg px-6 py-3 font-semibold hover:bg-[#C4820E] transition-colors">
  Secondary Action
</button>
```

### Outlined Button
```tsx
<button className="border-2 border-[#003262] text-[#003262] rounded-lg px-6 py-3 font-semibold hover:bg-[#003262] hover:text-white transition-colors">
  Learn More
</button>
```

### Cards
```tsx
<div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100">
  {/* Card content */}
</div>
```

### Accent Card (Gold highlight)
```tsx
<div className="bg-[#FDB515] text-[#003262] rounded-xl p-6">
  <div className="text-4xl font-bold font-serif">Featured</div>
  <div className="text-sm mt-2">Highlighted content</div>
</div>
```

---

## Visual Style Guidelines

### Shadows
```css
shadow-sm: 0 1px 2px rgba(0, 50, 98, 0.05)
shadow-md: 0 4px 12px rgba(0, 50, 98, 0.08)
shadow-lg: 0 8px 24px rgba(0, 50, 98, 0.12)
```

### Borders
```css
border-gray-100  /* Very subtle */
border-gray-200  /* Standard */
border-[#003262]/20  /* Blue tinted */
```

### Rounded Corners
```css
rounded-lg: 8px    /* Buttons, inputs */
rounded-xl: 12px   /* Cards */
rounded-2xl: 16px  /* Large sections */
```

### Transitions
```css
transition-colors duration-200
transition-shadow duration-300
transition-transform duration-200
```

### Hover States
- Buttons: Slight darkening or opacity change
- Cards: Subtle shadow increase, optional lift (translate-y-[-2px])
- Links: Color change to California Gold

---

## BerkeleyBites Context

BerkeleyBites is an AI-powered food recommendation app for UC Berkeley students. The UI should feel:

- **Student-Friendly**: Approachable, modern, and easy to navigate
- **On-Brand**: Proudly UC Berkeley with blue and gold accents
- **Food-Focused**: Appetizing imagery, clear menu information
- **Clean & Fast**: Quick decisions for hungry students

**Key Features:**
- Dining hall menu browsing
- Personalized food recommendations via AI agents
- Dietary preference filtering
- Real-time availability

---

## Using shadcn MCP Tools

When building components, use the shadcn MCP tools:

1. **Search for components:** `mcp__shadcn__search_items_in_registries` with `registries: ["@shadcn"]`
2. **View component details:** `mcp__shadcn__view_items_in_registries`
3. **Get usage examples:** `mcp__shadcn__get_item_examples_from_registries`
4. **Get install command:** `mcp__shadcn__get_add_command_for_items`
5. **Audit after creating:** `mcp__shadcn__get_audit_checklist`

Always check if a shadcn component exists before building custom implementations.

---

## Implementation Checklist

Before finalizing any component or page:

1. **Light mode only** - No dark backgrounds
2. **Berkeley Blue & Gold** - Consistent brand colors throughout
3. **Typography hierarchy** - Source Serif for headlines, Source Sans for body
4. **Generous spacing** - When in doubt, add more white space
5. **Subtle interactions** - Smooth transitions, no jarring effects
6. **shadcn components** - Use existing components when available
7. **Mobile responsive** - Single-column on mobile, stacked elements
8. **Accessibility** - Proper contrast ratios, focus states, semantic HTML

Execute with precision and restraint. Go Bears!
