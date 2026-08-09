---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 12: Starting a Project From Scratch — The Complete Guide

## The Big Idea

This is the module that ties everything together. You've learned the concepts — architecture, APIs, testing, CI/CD, debugging. Now the question is: **how do you start a real project from zero?** Not "how to write code," but "how to think, plan, and build like a professional."

Most beginners jump straight to coding. Professionals spend time **thinking** before they write a single line. This module teaches you how to think.

---

## Part 1: Before You Write Any Code — The 10 Questions

Answer these BEFORE opening your editor:

```
 1. What problem am I solving?
    → "Design RC beams per IS 456:2000"

 2. Who is this for?
    → "Structural engineers who need quick design checks"

 3. What does success look like?
    → "Engineer inputs beam dimensions, gets steel area in 2 seconds"

 4. What's the simplest version that's useful? (MVP)
    → "Single beam, flexure only, one concrete grade"

 5. What technology should I use?
    → "Python for math, FastAPI for API, React for UI"

 6. How will I organize the code?
    → "4-layer architecture: core → math → services → UI"

 7. How will people use it?
    → "pip install for Python devs, web UI for non-programmers"

 8. How will I know it's correct?
    → "Benchmark tests against SP-16 tables and textbook examples"

 9. How will I handle changes?
    → "Git + branches + PRs + CI checks"

10. What's my first milestone?
    → "Week 1: calculate_ast() with 3 passing tests"
```

**If you can't answer these clearly, you're not ready to code.** Research more.

---

## Part 2: The Project Lifecycle — Seven Stages

Every project goes through these stages, whether it's a weekend hack or a multi-year product:

```
Stage 1         Stage 2          Stage 3          Stage 4
IDEA            RESEARCH         DEFINITION       PLANNING
"I want to      "What exists?    "Here's exactly  "Here's how
build X"        How do others    what we'll       we'll build it
                do it?"          build"           and when"
   │                │                │                │
   ▼                ▼                ▼                ▼

Stage 5         Stage 6          Stage 7
EXECUTION       VALIDATION       MAINTENANCE
"Build it,      "Does it work?   "Keep it working,
test it,        Test, review,    fix bugs, add
iterate"        benchmark"       features"
```

### Stage 1: Idea (1-2 days)
```
Input:  A problem you noticed
Output: A one-sentence project description

Example:
  Problem: "Engineers calculate beam steel area by hand. It takes 30 minutes
            and errors are common."
  Idea:    "A Python library that automates IS 456 beam design calculations."
```

### Stage 2: Research (2-5 days)
```
What to research:
  ✓ Does something like this already exist?
  ✓ What standards/codes apply? (IS 456, ACI 318, Eurocode)
  ✓ What are the key formulas?
  ✓ Who would use this?
  ✓ What similar projects can I learn from?

Output: A research document with findings
```

### Stage 3: Definition (1-2 days)
```
Define clearly:
  ✓ Scope: what's IN and what's OUT
  ✓ MVP: minimum features for v1.0
  ✓ Success criteria: measurable checkboxes
  ✓ Non-goals: things you explicitly WON'T do

Output: Project definition document

Example scope:
  IN:  Singly reinforced beams, IS 456:2000, M15-M80 concrete
  OUT: Doubly reinforced beams, other codes, column design
  MVP: Calculate Ast for flexure + check shear
  Non-goal: Replace professional structural design software
```

### Stage 4: Planning (2-3 days)
```
Create:
  ✓ Architecture diagram (layers, boundaries)
  ✓ Folder structure
  ✓ Milestone plan (what by when)
  ✓ Technology choices (with reasons)

Output: Architecture doc + milestone plan
```

### Stage 5: Execution (weeks to months)
```
The actual coding, following the plan:
  ✓ Set up project structure
  ✓ Implement core logic first
  ✓ Write tests alongside code
  ✓ Build API layer
  ✓ Build UI layer
  ✓ Iterate based on testing
```

### Stage 6: Validation (1-2 weeks)
```
Verify everything works:
  ✓ All tests pass
  ✓ Benchmark against known answers
  ✓ Try to break it with edge cases
  ✓ Have someone else use it
  ✓ Documentation is complete
```

### Stage 7: Maintenance (ongoing)
```
After release:
  ✓ Fix reported bugs
  ✓ Update dependencies
  ✓ Add requested features
  ✓ Keep docs current
  ✓ Monitor for security issues
```

---

## Part 3: Folder Structure — Your First Architecture Decision

Before writing code, create the folder structure. This IS your architecture.

### For a Python library:
```
my-project/
├── .github/
│   └── workflows/           ← CI/CD
│       └── ci.yml
├── src/
│   └── my_library/
│       ├── __init__.py      ← Package root
│       ├── core/            ← Layer 4: Types, constants
│       │   └── types.py
│       ├── math/            ← Layer 3: Pure calculations
│       │   └── flexure.py
│       └── services/        ← Layer 2: Orchestration
│           └── api.py
├── tests/
│   ├── test_flexure.py
│   └── conftest.py          ← Shared fixtures
├── .gitignore
├── pyproject.toml            ← Project metadata + deps
├── README.md
└── LICENSE
```

### For a full-stack app:
```
my-project/
├── .github/
│   └── workflows/
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI app
│   │   ├── models/          ← Pydantic schemas
│   │   └── routers/         ← API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      ← React components
│   │   ├── hooks/           ← Custom hooks
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── core-library/             ← Shared business logic
│   ├── src/
│   └── tests/
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## Part 4: Setting Up the Project — Step by Step

### Step 1: Create the repository
```bash
mkdir my-project && cd my-project
git init
```

### Step 2: Create essential files
```
README.md          — What this project does, how to use it
LICENSE            — How others can use your code (MIT, Apache, etc.)
.gitignore         — Files Git should ignore
pyproject.toml     — Project metadata and dependencies
```

### Step 3: Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv/bin/python
pip install pytest ruff pyright
```

### Step 4: Create the package structure
```bash
mkdir -p src/my_library/core src/my_library/math tests
touch src/my_library/__init__.py
touch src/my_library/core/__init__.py
touch src/my_library/math/__init__.py
```

### Step 5: Write your first function + test
```python
# src/my_library/math/flexure.py
def calculate_area(width_mm: float, height_mm: float) -> float:
    """Calculate cross-sectional area in mm²."""
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Dimensions must be positive")
    return width_mm * height_mm
```

```python
# tests/test_flexure.py
from my_library.math.flexure import calculate_area

def test_basic_area():
    assert calculate_area(300, 500) == 150000

def test_negative_raises():
    with pytest.raises(ValueError):
        calculate_area(-300, 500)
```

### Step 6: Run your test
```bash
pytest tests/ -v
# PASSED!
```

### Step 7: First commit
```bash
git add .
git commit -m "feat: initial project setup with area calculation"
```

**You now have a working, tested, version-controlled project.** Everything from here is iteration.

---

## Part 5: Key Documents to Create

### 1. README.md — The front door
```markdown
# My Beam Design Library

IS 456:2000 RC beam design calculations.

## Installation
pip install my-library

## Quick Start
from my_library import design_beam
result = design_beam(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=150)

## Features
- Flexure design (Clause 38.1)
- Shear design (Clause 40)
- Detailing checks (Clause 26)
```

### 2. TASKS.md — What needs to be done
```markdown
# Tasks

## In Progress
- [ ] Add shear calculation (Clause 40)

## To Do
- [ ] Add doubly reinforced beam
- [ ] Add exposure-based cover
- [ ] Add deflection check

## Done
- [x] Basic flexure calculation
- [x] Unit tests for flexure
```

### 3. ADR (Architecture Decision Record)
```markdown
# ADR-001: Use 4-Layer Architecture

## Status: Accepted
## Date: 2024-01-15

## Context
We need to separate math from I/O so the library works standalone.

## Decision
4 layers: Core → Code Math → Services → UI. No upward imports.

## Consequences
- Math can be tested without HTTP
- Library can be used via pip, API, or CLI
- Requires discipline to maintain boundaries
```

---

## Part 6: Planning Your Work — Milestones

Break work into milestones (not tasks). Each milestone is a demo-able, usable checkpoint.

```
MILESTONE 1 (Week 1-2): "Calculate steel area"
  ✓ Flexure calculation function
  ✓ 3 unit tests with known answers
  ✓ Basic README
  ✓ pyproject.toml
  Demo: "I can calculate Ast for a beam from Python"

MILESTONE 2 (Week 3-4): "Full beam design"
  ✓ Shear calculation
  ✓ Detailing checks
  ✓ Combined design function
  ✓ 15+ tests with benchmarks
  Demo: "Design a complete beam with one function call"

MILESTONE 3 (Week 5-6): "API for non-programmers"
  ✓ FastAPI endpoints
  ✓ Pydantic input validation
  ✓ Auto-generated API docs
  ✓ Docker deployment
  Demo: "Anyone can design a beam from a web browser"

MILESTONE 4 (Week 7-8): "Professional UI"
  ✓ React frontend
  ✓ 3D visualization
  ✓ CSV import
  ✓ Report export
  Demo: "Full workflow from CSV to PDF report"
```

### Time allocation guideline:
```
 Coding          30%  ████████████░░░░░░░░░░░░░░░░░░░░
 Testing         15%  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░
 Debug/Fix       15%  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░
 Research        10%  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 Design/Plan     10%  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 Documentation   10%  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 Review/Iterate  10%  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

Most beginners allocate 90% to coding and 10% to everything else. Professionals know that coding is only 30% of the work.

---

## Part 7: Technology Choices — How to Decide

### Decision framework:

```
For each technology choice, ask:

1. Does it solve my actual problem?
   (Don't use Kubernetes for a script)

2. Can I learn it in a reasonable time?
   (Pick familiar tools for critical paths)

3. Is it well-maintained?
   (Check: last release date, open issues, community size)

4. Will I regret it in 6 months?
   (Avoid hype-driven choices)

5. What's the simplest option that works?
   (Start simple, add complexity later)
```

### Common decisions and recommendations:

| Decision | For Beginners | For Experienced |
|----------|--------------|----------------|
| Language | Python (versatile) | Match the problem domain |
| Web framework | FastAPI (Python) or Express (JS) | Depends on team expertise |
| Frontend | React (largest ecosystem) | Evaluate based on needs |
| Testing | pytest (Python), Vitest (React) | Same |
| CI | GitHub Actions (free for public repos) | Same or Jenkins |
| Container | Docker (industry standard) | Same |
| Database | SQLite → PostgreSQL (when needed) | PostgreSQL from start |

---

## Part 8: The 10 Biggest Mistakes When Starting

| # | Mistake | What Happens | Do This Instead |
|---|---------|-------------|----------------|
| 1 | **Start coding immediately** | Build the wrong thing, waste weeks | Spend 2 days planning first |
| 2 | **No version control** | Lose work, can't undo, can't collaborate | `git init` on day 1 |
| 3 | **No tests** | Bugs hide for weeks, refactoring is scary | First test within the first hour |
| 4 | **No clear scope** | Feature creep, never "done" | Write scope doc with IN/OUT |
| 5 | **Wrong abstraction too early** | Over-engineered code that's hard to change | Start concrete, abstract when patterns emerge |
| 6 | **Ignoring edge cases** | Crashes on real data | Test with zeros, negatives, huge values |
| 7 | **No documentation** | Even YOU forget how it works in 3 months | README from day 1, update as you go |
| 8 | **Monolithic code** | One giant file, impossible to understand | Split into modules from the start |
| 9 | **No CI** | "Works on my machine" fails everywhere else | Add CI in the first week |
| 10 | **Perfect is the enemy of done** | Polishing forever, never releasing | Ship the MVP, iterate |

---

## Part 9: Thinking Like an Engineer

### Engineering mindset vs. cowboy coding:

```
COWBOY CODING:                      ENGINEERING:
"It works!" ← success criteria      "It's correct, tested, documented,
                                     and maintainable" ← success criteria

Write code → run → looks right       Research → Plan → Code → Test →
→ ship                                Review → Document → Ship

Fix bugs when users report them      Prevent bugs with tests before shipping

"I'll remember how this works"       Write it down. You won't remember.

One giant file                        Modules with clear boundaries
```

### Questions an engineer asks before coding:

```
□ What are the inputs and outputs?
□ What are the edge cases?
□ What errors can occur?
□ What are the units?
□ How will I test this?
□ How will someone else understand this?
□ What if requirements change?
□ What's the performance requirement?
```

---

## Part 10: The Learning Map — What to Study Next

Based on what you've learned in these 12 modules, here's your learning path:

```
FOUNDATION (you are here)
  ✓ Architecture
  ✓ APIs, HTTP, REST
  ✓ Types and validation
  ✓ Testing
  ✓ Frontend basics
  ✓ Backend basics
  ✓ Git and CI/CD
  ✓ Error handling
         │
         ▼
INTERMEDIATE (next 3-6 months)
  □ Database design (PostgreSQL, SQLAlchemy)
  □ Authentication (JWT, OAuth)
  □ Advanced React patterns (context, suspense, server components)
  □ Advanced Python (decorators, generators, async)
  □ Docker compose advanced (volumes, networks, secrets)
  □ Performance optimization (profiling, caching)
  □ Security basics (OWASP Top 10, input sanitization)
         │
         ▼
ADVANCED (6-12 months)
  □ System design (scaling, load balancing, message queues)
  □ Domain-driven design (bounded contexts, aggregates)
  □ Microservices patterns (when actually needed)
  □ Infrastructure as Code (Terraform, AWS CDK)
  □ Observability (metrics, tracing, alerting)
  □ Machine learning integration
```

---

## Part 11: Practical Checklist — Starting Your Next Project

Copy this checklist for every new project:

```
WEEK 0: THINK
  □ Answer the 10 Questions (Part 1)
  □ Research existing solutions
  □ Define scope (IN / OUT)
  □ Define MVP (minimum viable product)
  □ Choose tech stack (with reasons documented)
  □ Draw architecture diagram (even rough ASCII)

DAY 1: SET UP
  □ Create repository (git init)
  □ Create .gitignore
  □ Create README.md (what + why + how)
  □ Create pyproject.toml or package.json
  □ Set up virtual environment
  □ Create folder structure
  □ Install dependencies
  □ First commit: "feat: initial project setup"

DAY 2: FIRST FEATURE
  □ Write the simplest useful function
  □ Write a test for it
  □ Run the test — it passes
  □ Second commit: "feat: add [feature]"

WEEK 1: CORE LOGIC
  □ Implement core business logic
  □ Write tests for every function
  □ Add CI (GitHub Actions)
  □ Add type hints
  □ Document functions

WEEK 2: API LAYER
  □ Add FastAPI (or equivalent)
  □ Create Pydantic models
  □ Write API tests
  □ Verify API docs at /docs

WEEK 3+: ITERATE
  □ Add features based on milestones
  □ Keep tests passing
  □ Keep docs updated
  □ Get feedback from users
  □ Release v0.1.0 when MVP is done
```

---

## Part 12: From This Library to Your Library

Here's how the structural_engineering_lib was built, mapped to concepts you've learned:

| Concept | How This Repo Did It |
|---------|---------------------|
| Architecture | 4-layer: Core → IS 456 Math → Services → UI/API |
| Tech stack | Python + FastAPI + React + Docker |
| Types | `b_mm`, `fck`, Pydantic models at every boundary |
| Testing | pytest + benchmarks against SP-16 and textbooks |
| Frontend | React 19 + R3F for 3D + Tailwind for styling |
| Backend | FastAPI with 13 routers, 60+ endpoints |
| Git | Automated via ai_commit.sh, conventional commits |
| CI/CD | 28 checks, 3 quality gate levels, GitHub Actions |
| Error handling | ValueError → HTTPException → toast message |
| Documentation | MkDocs site, inline docs, session logs |

**You can build something similar.** Start with the checklist above. Build one layer at a time. Test everything. Document as you go.

---

## Part 13: Exercises

1. **Plan a project:** Pick a problem you care about. Answer all 10 questions from Part 1. Write a 1-page project definition.
2. **Set up from scratch:** Create a new repo, folder structure, first function, first test, and first commit.
3. **Draw architecture:** Take the project you planned and draw the layers. What modules exist? What are the boundaries?
4. **First milestone:** Define Milestone 1. What's the absolute minimum you could build in a week that someone could use?
5. **Create a TASKS.md:** List 10 tasks for your project, split into "To Do" and "Future" categories.

---

## Part 14: Self-Check

1. **What should you do BEFORE writing code?** Answer the 10 questions: problem, audience, success, MVP, tech, architecture, usage, verification, changes, first milestone.
2. **What's the first file to create?** README.md (and .gitignore, and pyproject.toml/package.json).
3. **When should you write your first test?** Within the first hour of coding.
4. **What percentage of time should be spent on coding?** About 30%. The rest is planning, testing, debugging, documenting, and reviewing.
5. **What's the biggest mistake beginners make?** Starting to code before planning.
6. **What does a good Milestone 1 look like?** One feature that works correctly with tests, that someone could actually use.

---

## Final Takeaway

> **Building software is 30% coding and 70% thinking.** The best engineers aren't the fastest typists — they're the clearest thinkers. Before you write a line of code, answer: What am I building? Why? For whom? How do I know it works? Start small, test everything, and iterate.

---

## Where to Go From Here

You've completed all 12 modules. Here's what to do next:

1. **Build something.** Apply these concepts to a real project — even a small one.
2. **Read this project's source code.** You now have the vocabulary to understand what's happening.
3. **Contribute.** Submit a bug fix or documentation improvement to an open-source project.
4. **Teach someone.** The best way to solidify knowledge is to explain it.

Go back to [the index](README.md) to review any module.
