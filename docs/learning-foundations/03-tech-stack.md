# Module 3: The Tech Stack — Languages, Tools, and Why

## The Big Idea

A "tech stack" is the set of languages, frameworks, and tools you pick to build your project. Every choice has trade-offs. Understanding what each tool does and why it exists prevents you from using the wrong tool for the job.

---

## Part 1: What Is a Tech Stack?

A tech stack is a vertical slice of technologies from the user's screen down to the server.

```
┌─────────────────────────────────────────┐
│         What the user sees              │
│   ┌───────────┐  ┌────────────────┐     │
│   │  React 19 │  │  Tailwind CSS  │     │  ← Frontend
│   │ (UI logic)│  │   (styling)    │     │
│   └───────────┘  └────────────────┘     │
├─────────────────────────────────────────┤
│         How they communicate            │
│   ┌───────────────────────────────┐     │
│   │    HTTP / REST / JSON         │     │  ← Transport
│   └───────────────────────────────┘     │
├─────────────────────────────────────────┤
│         What processes requests         │
│   ┌───────────────────────────────┐     │
│   │         FastAPI (Python)      │     │  ← Backend
│   └───────────────────────────────┘     │
├─────────────────────────────────────────┤
│         What does the real work         │
│   ┌───────────────────────────────┐     │
│   │  structural_lib (Python lib)  │     │  ← Core library
│   └───────────────────────────────┘     │
├─────────────────────────────────────────┤
│         Where it runs                   │
│   ┌───────────────────────────────┐     │
│   │   Docker / Colima (container) │     │  ← Infrastructure
│   └───────────────────────────────┘     │
└─────────────────────────────────────────┘
```

---

## Part 2: Programming Languages — Python vs JavaScript/TypeScript

### Python

**What it is:** A general-purpose language known for readability and simplicity.

```python
# Python reads like English
def calculate_area(width, height):
    return width * height

result = calculate_area(300, 500)
print(f"Area: {result} mm²")
```

**Best for:** Math, science, data, backend APIs, automation, scripting.
**Used in this project for:** IS 456 structural calculations, FastAPI backend, all scripts.

### JavaScript / TypeScript

**JavaScript:** The language of the web browser. Every browser has a JS engine built in.
**TypeScript:** JavaScript + types. Catches errors before you run the code.

```typescript
// TypeScript adds type safety to JavaScript
function calculateArea(width: number, height: number): number {
  return width * height;
}

const result = calculateArea(300, 500);  // OK
const bad = calculateArea("hello", 500); // ERROR — TypeScript catches this
```

**Best for:** Frontend UIs, interactive web pages, Node.js servers.
**Used in this project for:** React frontend, 3D visualization with R3F.

### When to Use Which?

| Task | Best Language | Why |
|------|--------------|-----|
| Math / engineering | Python | NumPy, SciPy, clean math syntax |
| Backend API | Python (FastAPI) | Fast to develop, auto-docs, type hints |
| Web frontend | TypeScript + React | Browser-native, component model |
| Scripting / automation | Python | OS integration, readability |
| Mobile app | TypeScript (React Native) | Cross-platform |
| Machine learning | Python | TensorFlow, PyTorch |

---

## Part 3: Frameworks — Don't Reinvent the Wheel

A **framework** gives you pre-built structure so you focus on YOUR logic, not plumbing.

### Without a framework:
```python
# Building an API from scratch — terrible idea
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8000))
server.listen(5)
while True:
    client, addr = server.accept()
    data = client.recv(1024).decode()
    if "GET /design" in data:
        # Parse headers manually...
        # Parse body manually...
        # Validate input manually...
        # Handle errors manually...
        client.send(b"HTTP/1.1 200 OK\r\n\r\n{result}")
```

### With FastAPI:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BeamInput(BaseModel):
    width_mm: float
    depth_mm: float

@app.post("/design")
def design_beam(input: BeamInput):
    result = calculate(input.width_mm, input.depth_mm)
    return {"steel_mm2": result}
```

**Frameworks handle:** routing, validation, serialization, error handling, docs, security headers, CORS, etc.

### Major Frameworks

| Category | Framework | Language | What It Does |
|----------|-----------|----------|-------------|
| Backend API | **FastAPI** | Python | REST APIs with auto-docs |
| Backend API | Express | JavaScript | Minimal Node.js server |
| Backend API | Django | Python | Full-featured (ORM, admin, auth) |
| Frontend | **React** | TypeScript | Component-based UI |
| Frontend | Vue | JavaScript | Approachable, template-based UI |
| Frontend | Angular | TypeScript | Enterprise, opinionated |
| 3D Graphics | **React Three Fiber** | TypeScript | Three.js in React components |
| CSS | **Tailwind CSS** | CSS classes | Utility-first styling |

---

## Part 4: Package Managers — Installing Other People's Code

Instead of writing everything from scratch, you install **packages** (libraries other people wrote).

### Python: pip
```bash
pip install fastapi              # Install one package
pip install -r requirements.txt  # Install all project dependencies
```

**Key files:**
- `requirements.txt` — List of packages and versions
- `pyproject.toml` — Modern project metadata + dependencies
- `requirements-lock.txt` — Exact versions for reproducibility

### JavaScript: npm
```bash
npm install react              # Install one package
npm install                    # Install all from package.json
```

**Key files:**
- `package.json` — Dependencies + scripts + metadata
- `package-lock.json` — Exact versions (auto-generated)

### Why Lock Files Matter

```
requirements.txt says:     fastapi>=0.100
Today installs:            fastapi==0.115.0
Tomorrow might install:    fastapi==0.120.0  ← could have breaking changes!

requirements-lock.txt says: fastapi==0.115.0
Always installs:            fastapi==0.115.0  ← reproducible!
```

**Rule:** Always commit lock files. They ensure everyone gets the same versions.

---

## Part 5: Virtual Environments — Isolated Workspaces

**Problem:** You have two projects. Project A needs `fastapi==0.100`. Project B needs `fastapi==0.115`. Both are on the same computer.

**Solution:** Virtual environments. Each project gets its own isolated Python installation.

```
Your computer
├── Project A/
│   └── .venv/          ← Has fastapi 0.100
│       └── bin/python  ← This Python has Project A's packages
├── Project B/
│   └── .venv/          ← Has fastapi 0.115
│       └── bin/python  ← This Python has Project B's packages
└── System Python        ← Don't install project packages here!
```

### How to use:
```bash
# Create a virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Or just use the full path (no activation needed)
.venv/bin/python my_script.py
.venv/bin/pip install fastapi
.venv/bin/pytest tests/
```

**Rule in this project:** Always use `.venv/bin/python`, never bare `python`.

---

## Part 6: Build Tools — From Source Code to Something Usable

Build tools transform your source code into something that can run or be distributed.

### Python build tools:
```bash
# pyproject.toml defines how to build
python -m build                    # Creates .whl and .tar.gz
pip install dist/my_package.whl    # Install the built package
```

### JavaScript build tools:
```
Source code       →  Build tool  →  Optimized output
  ┌──────────┐      ┌──────┐      ┌──────────────┐
  │ .tsx files│  →   │ Vite │  →   │ .js bundles  │
  │ .css files│      │      │      │ (minified,   │
  │ .ts files│      └──────┘      │  tree-shaken) │
  └──────────┘                     └──────────────┘
```

**Vite** (this project's build tool):
- Instant dev server (Hot Module Replacement)
- Fast production builds
- Handles TypeScript, JSX, CSS, images
- Tree-shaking removes unused code

```bash
cd react_app
npm run dev     # Start dev server at :5173 (instant reload)
npm run build   # Create optimized production bundle
```

---

## Part 7: Docker — Run Anywhere

Docker packages your application + its dependencies into a container that runs identically anywhere.

```
Without Docker:                  With Docker:
"Works on my machine"            "Works on ANY machine"

Developer A: Python 3.11         Container: Python 3.11
Developer B: Python 3.9          Container: Python 3.11
Server:      Python 3.8          Container: Python 3.11
```

**Key concepts:**
- **Image:** A blueprint (like a recipe)
- **Container:** A running instance of an image (like the dish)
- **Dockerfile:** Instructions to build an image
- **docker-compose.yml:** Run multiple containers together

```yaml
# docker-compose.yml — runs the whole stack
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"    # Your API at localhost:8000
```

More details in [Module 8 — Backend](08-backend.md).

---

## Part 8: Development Workflow Tools

### Code Editor: VS Code
- Extensions for Python, TypeScript, Docker
- Integrated terminal
- GitHub Copilot for AI assistance
- Debugger built in

### Linter: Checks code style
```bash
# Python
ruff check .              # Fast Python linter

# TypeScript
npx eslint .              # JavaScript/TypeScript linter
```

### Formatter: Auto-formats code
```bash
# Python
ruff format .             # Auto-format Python

# TypeScript / React
npx prettier --write .    # Auto-format everything
```

### Type Checker: Catches type errors
```bash
# Python
pyright                   # Static type analysis

# TypeScript (built into tsc)
npx tsc --noEmit          # Type-check without building
```

---

## Part 9: This Project's Complete Tech Stack

| Layer | Technology | Purpose | File(s) |
|-------|-----------|---------|---------|
| Frontend | React 19 | Component UI | `react_app/src/` |
| Frontend | TypeScript | Type-safe JS | `.tsx` and `.ts` files |
| Frontend | Tailwind CSS | Styling | Class utilities in JSX |
| Frontend | R3F (Three.js) | 3D visualization | `Viewport3D.tsx` |
| Frontend | Zustand | State management | `store/` |
| Frontend | Vite | Build + dev server | `vite.config.ts` |
| Transport | HTTP / REST | API communication | JSON over HTTP |
| Transport | WebSocket | Live updates | `/ws/design/{session}` |
| Transport | SSE | Batch streaming | Server-Sent Events |
| Backend | FastAPI | API framework | `fastapi_app/` |
| Backend | Pydantic V2 | Validation | `models/` |
| Backend | Uvicorn | ASGI server | Runs FastAPI |
| Library | Python 3.11+ | Core language | `Python/structural_lib/` |
| Library | NumPy (optional) | Numeric operations | Math functions |
| Testing | pytest | Python tests | `Python/tests/` |
| Testing | Vitest | React tests | `react_app/vitest.config.ts` |
| DevOps | Docker + Colima | Containerization | `Dockerfile.fastapi` |
| DevOps | GitHub Actions | CI/CD | `.github/workflows/` |
| DevOps | Git + hooks | Version control | `scripts/ai_commit.sh` |
| Docs | MkDocs | Documentation site | `mkdocs.yml` |

---

## Part 10: How to Choose Your Tech Stack

### For a new project, ask these questions:

```
1. What PROBLEM am I solving?
   → Math-heavy? → Python
   → Interactive UI? → React/TypeScript
   → Just an API? → FastAPI or Express

2. What does my TEAM know?
   → Team knows Python → FastAPI, not Express
   → Team knows JavaScript → Express, not FastAPI

3. What COMMUNITY supports it?
   → More users = more answers on StackOverflow
   → More packages = less code you write
   → Active maintenance = fewer security issues

4. What's the SIMPLEST stack that works?
   → Don't use microservices for a todo app
   → Don't use React for a static page
   → Don't use Docker for a single script
```

### Common starter stacks:

| Type | Stack | When |
|------|-------|------|
| Python script | Python + pytest | Automation, data processing |
| Python library | Python + pytest + pyproject.toml | Reusable code published to PyPI |
| Web API | FastAPI + Pydantic + pytest | Backend services |
| Full-stack web | React + FastAPI + Docker | Web application |
| Static site | HTML + Tailwind + Vite | Landing pages, docs |

---

## Part 11: Exercises

1. **Map the stack:** Open `package.json` and `pyproject.toml`. List every dependency and what it does.
2. **Why TypeScript?** Convert a 5-line Python function to TypeScript. What's different?
3. **Virtual env test:** Create a new venv, install `requests`, verify it's not in your global Python.
4. **Build something:** Run `cd react_app && npm run build`. Look at the `dist/` folder. What did Vite produce?

---

## Part 12: Self-Check

1. **What's a tech stack?** The set of languages, frameworks, and tools used to build a project.
2. **Why virtual environments?** Isolate project dependencies from each other.
3. **What does a build tool do?** Transforms source code into optimized, runnable output.
4. **Why lock files?** Ensure everyone gets exactly the same package versions.
5. **When should you use Docker?** When you need reproducible environments across machines.
6. **What's the simplest stack for a Python library?** Python + pytest + pyproject.toml.

---

## Key Takeaway

> Your tech stack is a set of **choices**, not requirements. Every tool exists to solve a specific problem. Pick the simplest combination that solves YOUR problem. You can always add complexity later — you can rarely remove it.

**Next:** [Module 4 — APIs](04-apis.md) explains how different parts of a system communicate.
