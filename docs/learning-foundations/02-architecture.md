---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 2: Architecture — How Software Gets Organized

## The Big Idea

Architecture is how you split a system into parts and define the rules for how those parts interact.

Without architecture, code becomes spaghetti — everything depends on everything, a change in one place breaks five other places, and nobody can understand the system.

With architecture, each part has a clear job, clear boundaries, and clear rules about what it can and can't touch.

---

## Part 1: What Architecture Actually Means

People use "architecture" loosely. Here's what it really means:

```
Architecture answers THREE questions:

1. What are the big parts of the system?
2. How do they connect to each other?
3. What rules govern their interaction?
```

**Example — A restaurant:**
```
┌──────────────┐    order    ┌──────────────┐   ingredients   ┌──────────────┐
│   Customers  │ ──────────→ │   Kitchen    │ ←───────────── │   Suppliers  │
│   (eat food) │ ←────────── │ (make food)  │                │ (provide raw │
│              │   food      │              │                │  materials)  │
└──────────────┘             └──────────────┘                └──────────────┘
```

The kitchen doesn't seat customers. Customers don't cook. Suppliers don't serve food. Each part has a job and clear boundaries. That's architecture.

---

## Part 2: Why Architecture Matters

### Without architecture:
```python
# Everything mixed together — this is spaghetti code
def design_beam(csv_path):
    # Parse CSV (I/O)
    data = open(csv_path).read()
    rows = data.split("\n")
    width = float(rows[1].split(",")[0])

    # IS 456 math
    Ast = 0.5 * (fck / fy) * width * d * (1 - sqrt(1 - 4.6 * Mu / (fck * width * d**2)))

    # Generate HTML report (UI)
    html = f"<h1>Beam Design</h1><p>Steel: {Ast} mm²</p>"
    with open("report.html", "w") as f:
        f.write(html)

    # Print to console
    print(f"Required steel: {Ast} mm²")
    return Ast
```

**Problems:**
- Can't test the math without a CSV file
- Can't change the report format without touching the math
- Can't reuse the math from an API — it's tied to file I/O
- A bug in CSV parsing can corrupt the math
- Can't test each piece independently

### With architecture:
```python
# Layer 1: I/O (reads CSV)
def parse_csv(path):
    return {"width_mm": 300, "depth_mm": 500, "mu_knm": 150}

# Layer 2: Math (pure calculation — no I/O)
def calculate_ast(width_mm, depth_mm, fck, fy, mu_knm):
    # ... IS 456 math ...
    return 1206.5  # mm²

# Layer 3: Output (generates report)
def generate_report(result):
    return f"<h1>Beam Design</h1><p>Steel: {result} mm²</p>"
```

**Now you can:**
- Test the math with just numbers (no CSV needed)
- Change the report without touching the math
- Call the math from a web API, CLI, or notebook
- Each piece is small, testable, and replaceable

---

## Part 3: Layers — The Most Common Architecture Pattern

The most widely used architecture pattern is **layered architecture**. Each layer has a specific job and can only talk to layers below it.

```
┌─────────────────────────────────────────────┐
│            LAYER 1: USER INTERFACE           │
│   What the user sees and interacts with      │
│   Web UI, CLI, API endpoints, reports        │
│                     │                        │
│                     ▼                        │
├─────────────────────────────────────────────┤
│            LAYER 2: BUSINESS LOGIC           │
│   The rules and workflows of your domain     │
│   "Design a beam" = flexure + shear + detail │
│                     │                        │
│                     ▼                        │
├─────────────────────────────────────────────┤
│            LAYER 3: CORE / DOMAIN            │
│   Pure calculations, data types              │
│   Math formulas, result structures           │
│                     │                        │
│                     ▼                        │
├─────────────────────────────────────────────┤
│            LAYER 4: INFRASTRUCTURE           │
│   File I/O, database, network, external APIs │
│   CSV reading, PDF generation, HTTP calls    │
└─────────────────────────────────────────────┘
```

### The ONE rule of layered architecture:

> **Each layer can only import from layers below it. Never above.**

```
✅ Business Logic imports from Core         (layer 2 → layer 3)
✅ UI imports from Business Logic            (layer 1 → layer 2)
❌ Core imports from UI                      (layer 3 → layer 1) FORBIDDEN
❌ Core imports from Business Logic           (layer 3 → layer 2) FORBIDDEN
```

**Why?** If Core (math) imports from UI (React), then changing the UI breaks the math. The math should work even if you delete the entire UI.

---

## Part 4: Modules — Splitting Code Into Pieces

A **module** is a self-contained piece of code with a clear purpose.

```
structural_lib/
├── core/              ← Module: data types, constants
│   ├── types.py
│   └── materials.py
├── codes/             ← Module: engineering code math
│   └── is456/
│       ├── flexure.py ← IS 456 flexure calculations
│       ├── shear.py   ← IS 456 shear calculations
│       └── detailing.py
├── services/          ← Module: orchestration
│   ├── api.py         ← "Design a beam" = calls flexure + shear + detail
│   └── adapters.py    ← CSV parsing, format conversion
└── visualization/     ← Module: 3D rendering helpers
    └── geometry_3d.py
```

**Good modules have:**
- One clear responsibility ("flexure calculations")
- A small public API (a few functions others can call)
- Hidden internals (implementation details stay private)
- No circular dependencies (A uses B, B doesn't use A)

**Bad modules:**
- `utils.py` (what ISN'T a utility?)
- `helpers.py` (same problem)
- `stuff.py` (obviously terrible)

---

## Part 5: Dependencies — What Uses What

A **dependency** is when one piece of code needs another to work.

```
                    depends on
   API endpoint ───────────────→ business logic
                    depends on
   business logic ─────────────→ math functions
                    depends on
   math functions ─────────────→ data types
```

### Dependency direction matters

```
GOOD (downward dependencies — easy to change):
   UI → Services → Math → Types
   If you change UI, nothing below breaks.

BAD (circular dependencies — everything breaks):
   UI → Services → Math → UI  ← circular!
   Changing anything breaks everything.
```

### How to visualize dependencies

Draw arrows from "who uses" to "what's used." If you see cycles (A→B→C→A), your architecture has a problem.

```
GOOD:                    BAD:
  A → B → C               A → B → C
                           ↑         │
                           └─────────┘ ← cycle!
```

---

## Part 6: Common Architecture Patterns

### Pattern 1: Monolith
Everything in one codebase, one deployment.

```
┌──────────────────────┐
│     One Application   │
│  ┌────┐ ┌────┐ ┌────┐│
│  │ UI │ │API │ │Math││
│  └────┘ └────┘ └────┘│
└──────────────────────┘
```

**When to use:** Most projects. Start here.
**Pros:** Simple, fast to develop, easy to deploy.
**Cons:** Can become messy if boundaries aren't enforced.

### Pattern 2: Monorepo with Services
One repository, but clear internal services that could be split later.

```
repo/
├── frontend/        ← Could be deployed separately
├── backend/         ← Could be deployed separately
├── core-library/    ← Shared by backend and others
└── scripts/
```

**When to use:** Medium projects with a frontend + backend.
**Pros:** One repo = easy to manage, but clear separation.
**Cons:** Requires discipline to maintain boundaries.

### Pattern 3: Microservices
Each feature is a separate deployable service.

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ User    │  │ Payment │  │ Invoice │
│ Service │  │ Service │  │ Service │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
              Message Bus
```

**When to use:** Large teams, high scale, independent deployment needs.
**Pros:** Independent scaling, independent deployment.
**Cons:** Complex, overkill for most projects. Do NOT start here.

### Which Should You Use?

| Project Size | Best Choice |
|-------------|-------------|
| Learning project | Monolith |
| Side project with UI | Monorepo |
| Startup with 2-5 people | Monorepo |
| Company with 20+ engineers | Consider microservices |

**Rule:** Start with monolith or monorepo. Split later if needed.

---

## Part 7: Boundaries — The Most Important Concept

A **boundary** is where one part of the system ends and another begins.

```
┌──────────────┐      boundary      ┌──────────────┐
│   Frontend   │ ←─── (HTTP API) ──→│   Backend    │
│   (React)    │                    │   (FastAPI)   │
└──────────────┘                    └──────────────┘
```

**At every boundary, you define:**
1. **What data crosses** (JSON with specific fields)
2. **What format** (the API contract)
3. **What's validated** (type checking, input validation)

**Why boundaries matter:**
- Each side can change independently
- Bugs are contained to one side
- Different people can work on different sides
- You can replace one side without touching the other

### The 4-layer boundary example

```
Layer 1 (UI)      ←→  Layer 2 (Services)     ← HTTP + JSON
Layer 2 (Services) ←→  Layer 3 (Math)          ← Function calls + typed params
Layer 3 (Math)     ←→  Layer 4 (Core Types)    ← Import + data classes
```

At each boundary, data gets validated:
- HTTP → Pydantic model validates JSON
- Function call → type hints validate parameters
- Data class → constructor validates fields

---

## Part 8: Real Example — Four-Layer Architecture

Here's a real architecture for a structural engineering library:

```
┌─────────────────────────────────────────────────────┐
│  LAYER 1: UI / IO                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  React   │  │  FastAPI  │  │   CLI    │          │
│  │  (web)   │  │  (API)    │  │ (terminal)│         │
│  └──────────┘  └──────────┘  └──────────┘          │
│                     │                               │
│─────────────────────┼───────────────────────────────│
│  LAYER 2: Services  │                               │
│  ┌──────────────────┴───────────────────┐           │
│  │ api.py — orchestrates design workflow │           │
│  │ adapters.py — CSV/Excel parsing       │           │
│  │ beam_pipeline.py — multi-step designs │           │
│  └──────────────────┬───────────────────┘           │
│                     │                               │
│─────────────────────┼───────────────────────────────│
│  LAYER 3: Code Math │                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ flexure  │  │  shear   │  │ detailing│          │
│  │  .py     │  │   .py    │  │   .py    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│           Pure math — NO I/O, NO imports up          │
│                     │                               │
│─────────────────────┼───────────────────────────────│
│  LAYER 4: Core      │                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  types   │  │ sections │  │materials │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│           Data classes, constants, enums              │
└─────────────────────────────────────────────────────┘
```

**Rules enforced:**
- Layer 3 (math) can NEVER import from Layer 1 (UI) or Layer 2 (services)
- Layer 4 (core) can NEVER import from anything above
- Data flows DOWN (top to bottom) through function calls
- Results flow UP through return values

---

## Part 9: Architecture Decisions to Make Early

When starting a project, decide these upfront:

| Decision | Options | Think About |
|----------|---------|-------------|
| One file or many? | Single script vs package | Will it grow? |
| How many layers? | 2 (simple) vs 4 (strict) | How complex is the domain? |
| Monolith or split? | One app vs frontend + backend | Do you need a web UI? |
| Where does I/O happen? | Everywhere vs outer layers only | Testability |
| How are modules connected? | Direct imports vs interfaces | Flexibility |
| Where is validation? | At boundaries vs everywhere | Performance vs safety |

**Rule of thumb:** Start simple. Add complexity only when the simple approach fails.

---

## Part 10: Exercises

1. **Draw the architecture** of an app you use daily (e.g., a food delivery app). What are the layers? Where are the boundaries?
2. **Identify the modules** in this repo's `Python/structural_lib/` folder. What does each one do?
3. **Find a dependency violation:** If `core/types.py` imported from `services/api.py`, why would that be bad?
4. **Choose a pattern:** You're building a calculator app. Monolith, monorepo, or microservices? Why?

---

## Part 11: Self-Check

1. **What 3 questions does architecture answer?** What are the parts? How do they connect? What rules govern them?
2. **What's the ONE rule of layered architecture?** Each layer only imports from layers below.
3. **What's a boundary?** Where one part of the system ends and another begins. Data is validated crossing it.
4. **What's a circular dependency?** A→B→C→A. Everything breaks when anything changes.
5. **Should you start with microservices?** No. Start with monolith or monorepo.
6. **Why separate math from I/O?** So you can test math with just numbers, without files or network.

---

## Key Takeaway

> Good architecture is about **separation** — separate concerns, separate layers, separate responsibilities. When things are separated properly, you can understand, test, change, and fix each piece independently.

**Next:** [Module 3 — The Tech Stack](03-tech-stack.md) explains the tools and languages that make architecture real.
