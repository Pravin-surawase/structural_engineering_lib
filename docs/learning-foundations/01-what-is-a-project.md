---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 1: What Is a Real Software Project

## The Big Idea

A real project is NOT just writing code. Code is maybe 30-40% of the work.

A real project is a **structured effort** to turn an idea into a working product under constraints: time, money, people, quality, and changing requirements.

If you only know how to code, you can build a script. To build a **product**, you need to understand everything in this module.

---

## Part 1: The 5 Core Questions

Before writing a single line of code, every serious project answers these:

```
1. WHY are we building it?        → Problem statement
2. WHAT exactly are we building?  → Scope and features
3. HOW will we build it?          → Architecture and tools
4. WHO will do what?              → Roles and responsibilities
5. HOW do we know it's working?   → Success criteria and tests
```

If these aren't clear, projects drift, get bloated, and become messy.

**Bad start:** "I want to make a library."
**Good start:** "I want to build a Python library that designs reinforced concrete beams per IS 456, with clean APIs, automated tests, and professional outputs."

The second version tells you what, who it's for, and what quality means.

---

## Part 2: The 7 Stages of a Project

Every real project goes through these stages, whether you plan for them or not:

```
┌──────────────────────────────────────────────────────────┐
│  Stage 1: IDEA          "What problem exists?"           │
│  Stage 2: RESEARCH      "What solutions already exist?"  │
│  Stage 3: DEFINITION    "What exactly will WE build?"    │
│  Stage 4: PLANNING      "How will we build it?"          │
│  Stage 5: EXECUTION     "Build it."                      │
│  Stage 6: VALIDATION    "Does it actually work?"         │
│  Stage 7: MAINTENANCE   "Keep it alive and growing."     │
└──────────────────────────────────────────────────────────┘
```

### Stage 1 — Idea / Problem

You ask:
- What problem are we solving?
- Who has this problem?
- Why does this matter?
- Why now?

**Example:** "Structural engineers waste hours doing repetitive beam calculations in spreadsheets. The formulas are error-prone. There's no reusable, tested library."

### Stage 2 — Research

Before building, study:
- What tools already exist? (ETABS, STAAD, manual spreadsheets)
- What's missing? (no open-source IS 456 Python library)
- What are the technical challenges? (unit consistency, code compliance)
- Is this feasible for one person?

**This is where most beginners skip ahead.** They start coding on day 1. Then they discover 3 weeks later that their architecture doesn't work.

### Stage 3 — Definition

Now you define precisely:
- **Vision:** The big-picture future
- **Scope:** What's in v1, what's NOT in v1
- **Goals:** Specific outcomes ("design beams per IS 456")
- **Non-goals:** What you deliberately skip ("no slab design in v1")
- **Success criteria:** How you know it's done ("100 tests pass, pip install works")

### Stage 4 — Planning

You decide:
- Architecture (layers, modules, how they connect)
- Folder structure
- Tools (Python, pytest, GitHub Actions)
- Milestones (v0.1 = basic flexure, v0.5 = full beam, v1.0 = production-ready)
- Testing strategy
- Documentation plan

### Stage 5 — Execution

Now you actually code. But notice — this is stage 5, not stage 1.
- Write code
- Write tests
- Write docs
- Review your work
- Fix bugs
- Iterate

### Stage 6 — Validation

Check:
- Does it solve the actual problem?
- Can someone else install and use it?
- Are the results correct? (benchmark tests)
- Is the documentation understandable?

### Stage 7 — Maintenance

After launch:
- Fix bugs users report
- Add features carefully (not everything — scope control!)
- Keep docs current
- Publish updates
- Manage compatibility (don't break existing users)

---

## Part 3: What Is Scope?

Scope is the **boundary** around what your project will and won't do.

```
┌─────────────────────────────────┐
│          IN SCOPE (v1)          │
│                                 │
│  ✅ IS 456 beam design          │
│  ✅ Flexure, shear, detailing   │
│  ✅ Python API                  │
│  ✅ Automated tests             │
│  ✅ pip-installable package     │
│                                 │
├─────────────────────────────────┤
│         OUT OF SCOPE (v1)       │
│                                 │
│  ❌ Column design               │
│  ❌ Slab design                 │
│  ❌ Web UI                      │
│  ❌ Mobile app                  │
│  ❌ Live ETABS integration      │
│                                 │
└─────────────────────────────────┘
```

**Why scope matters:** Projects fail because scope is not controlled. Every "one more feature" adds complexity, bugs, testing, and documentation. The result? Nothing ships.

**Scope creep** is when features keep getting added without removing anything. It's the #1 project killer.

---

## Part 4: What Is an MVP?

MVP = **Minimum Viable Product**.

It's the smallest version of your product that actually solves the problem.

**Not an MVP:**
- "A full structural engineering platform with 15 design codes, 3D visualization, report generation, and cloud deployment"

**An MVP:**
- "A Python function that takes beam dimensions and loads, returns required steel area per IS 456, with 10 passing tests"

The MVP lets you:
1. Prove the idea works
2. Get feedback early
3. Build on a working foundation
4. Ship something instead of nothing

---

## Part 5: Success Criteria

How do you know the project is "done"? You define success criteria upfront.

**Bad:** "It should work"
**Good:**
```
□ Beam design returns correct Ast for 10 known benchmarks
□ pip install works on Python 3.11+
□ API docstrings on all public functions
□ 85% test coverage
□ README with quick-start example
□ No known bugs in flexure calculations
```

Without success criteria, you only "feel" like you're making progress. With them, you can objectively say "4 of 6 done, 2 remaining."

---

## Part 6: Roles in a Project

Even as a solo developer, you play multiple roles. Understanding them helps you think clearly.

| Role | Asks | Example |
|------|------|---------|
| **Product** | What should we build and why? | "Users need beam design, not database management" |
| **Architect** | How should the system be structured? | "Separate math from I/O" |
| **Developer** | Write the code | Implement `calculate_ast_required()` |
| **QA/Tester** | Does it actually work? | Write tests, find edge cases |
| **DevOps** | How does it get built, tested, released? | CI pipeline, PyPI publishing |
| **Documentation** | Can someone else understand it? | README, API docs, tutorials |

**When you're solo, you ARE all six roles.** The danger is spending all your time as "Developer" and ignoring the other five. That's how you end up with working code that nobody can install, understand, or trust.

---

## Part 7: Key Project Documents

Real projects have these documents. They're short, not novels.

### 1. Project Charter (1 page)
```
Project:     structural-lib-is456
Objective:   Python library for IS 456 RC beam design
Users:       Structural engineers, automation developers
Scope:       Beam flexure, shear, detailing, BBS export
Success:     100 benchmark tests, pip install, API docs
Owner:       You
Constraints: Solo developer, must be accurate, open-source
```

### 2. Architecture Decision Records (ADRs)
Short notes explaining WHY you made key decisions:
- "Why 4-layer architecture?" → Isolates math from UI
- "Why explicit units (b_mm not b)?" → Prevents unit confusion bugs
- "Why Python 3.11+?" → Type hints, performance, ecosystem

### 3. Roadmap
```
v0.1 — Core flexure calculation + 10 tests
v0.2 — Shear + detailing
v0.5 — Full beam pipeline + CSV import
v1.0 — Production: docs, CI, PyPI, benchmarks
```

### 4. Testing Plan
What gets tested, how, and what's the coverage target.

---

## Part 8: The 10 Biggest Mistakes

These kill projects. Every single one has happened in real codebases.

| # | Mistake | Consequence |
|---|---------|-------------|
| 1 | Starting with code too early | Building on fog — architecture doesn't work |
| 2 | No scope control | V1 tries to do everything, ships nothing |
| 3 | No target user defined | Product becomes confused |
| 4 | No architecture boundaries | Math leaks into UI, everything's tangled |
| 5 | No result schema | Loose dicts everywhere, no consistency |
| 6 | No testing strategy | Trust collapses, bugs ship |
| 7 | No documentation plan | Only the builder understands it |
| 8 | Too many features, weak fundamentals | Feature sprawl kills quality |
| 9 | No versioning discipline | Users can't trust updates |
| 10 | No decision records | 3 months later, nobody remembers why |

---

## Part 9: Time Planning

Real project time breakdown (approximate):

```
Research & planning:    15%  ← most beginners: 0%
Architecture & setup:   10%
Implementation:         30%  ← most beginners think this is 90%
Testing:                15%
Documentation:          10%
Bug fixing & polish:    10%
Release & deployment:    5%
Rework/unexpected:       5%
```

**The rule:** Real projects take 2-3x longer than "just the coding" suggests. Testing alone is 15% of the work. Documentation is 10%. If you skip them, the product isn't ready.

---

## Part 10: Exercises

1. **Write a problem statement** for a project you want to build. One sentence. Include: who, what, why.
2. **Define the scope** of your v1. List 5 things IN scope and 5 things OUT of scope.
3. **Write 5 success criteria.** Make them measurable (not "it should be good" but "10 tests pass").
4. **Create a simple roadmap** with 4 milestones (v0.1 through v1.0).

---

## Part 11: Self-Check

1. **What are the 7 project stages?** Idea → Research → Definition → Planning → Execution → Validation → Maintenance.
2. **What is scope creep?** Adding features without removing anything, causing the project to bloat.
3. **What is an MVP?** The smallest version that solves the core problem.
4. **Why define success criteria?** So you can objectively measure progress instead of guessing.
5. **What's the most common beginner mistake?** Starting with code before defining the problem, scope, and architecture.
6. **Name 3 roles you play as a solo developer.** Product (what to build), Developer (build it), Tester (verify it).
7. **What percentage of real project time is coding?** About 30%. The rest is planning, testing, docs, bug fixing, and release.

---

## Key Takeaway

> A real project is 30% coding, 70% decisions. If your decisions are good, the code flows naturally. If your decisions are bad, no amount of code fixes the mess.

**Next:** [Module 2 — Architecture](02-architecture.md) teaches you how to organize software so it doesn't become a tangled mess.
