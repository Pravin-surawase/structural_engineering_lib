# Function Catalog Research — One Day Plan
**Date:** 2026-01-13
**Duration:** Today (single day)
**Goal:** Map every function in the library with plain-English explanations

---

## What We're Doing (Simple Version)

Think of a structural engineering library like a toolbox. We have:
- **Hammers** (basic tools) → Calculate beam dimensions, check materials
- **Wrenches** (medium tools) → Check if designs are safe, calculate stresses
- **Specialized tools** (complex tools) → Design rebar patterns, export DXF files

**Today's Goal:** List every tool, what it does, and when to use it.

---

## Today's Tasks

### Task 1: Core Function Audit (2 hours)
Read through these files and list every function:
- `flexure.py` — Functions that check if a beam can handle bending
- `shear.py` — Functions that check if a beam can handle sideways forces
- `detailing.py` — Functions that decide where to put steel bars
- `materials.py` — Functions for concrete and steel properties
- `tables.py` — Functions that look up values from IS 456 tables
- `validation.py` — Functions that check if inputs are valid

**Output:** `01-CORE-FUNCTIONS.md` (list with descriptions)

### Task 2: API Functions Audit (1 hour)
Read `api.py` and list public functions people actually use:
- These are the "user-facing" tools
- They combine multiple core functions

**Output:** `02-API-FUNCTIONS.md` (user-friendly functions)

### Task 3: Workflow Functions (1 hour)
Read these to understand the flow:
- `beam_pipeline.py` — Orchestrates the design process
- `job_runner.py` — Runs batch designs
- `dxf_export.py` — Creates CAD drawings

**Output:** `03-WORKFLOW-FUNCTIONS.md` (how things connect)

### Task 4: Explain and Document (1 hour)
Write simplified explanations for each function:
- What it does (one sentence)
- When to use it (real scenario)
- What it needs (inputs)
- What it gives back (outputs)

**Output:** `FUNCTION-GUIDE.md` (complete beginner guide)

---

## Key Concepts (Learn These First)

**Before diving in, understand these 4 things:**

### 1. Beam Design (What We're Solving)
```
A concrete beam carries a load. We need to answer:
- How much steel do we need? (Ast)
- Is the concrete strong enough? (Check stresses)
- Will it bend too much? (Deflection check)
- Can we actually build it? (Bar spacing rules)

Answer = Beam is SAFE or UNSAFE
```

### 2. Inputs (What We Ask For)
```
b = width of beam (mm)
d = effective depth of beam (mm) [from top to center of steel]
D = total depth of beam (mm) [top to bottom]
fck = concrete strength (N/mm²)
fy = steel strength (N/mm²)
Mu = bending moment applied (kN·m)
Vu = shear force applied (kN)
```

### 3. Outputs (What We Give Back)
```
Ast = area of steel needed (mm²)
Asc = compression steel needed (mm²)
Stirrup details = stirrup diameter and spacing
is_safe = YES or NO
error = Why it failed (if it did)
```

### 4. IS 456 (The Rules)
```
IS 456 is an Indian standard — the "rulebook" for concrete beam design.
It says things like:
- "Concrete strength must be at least 15 N/mm²"
- "Steel spacing must not exceed 300mm"
- "Use these formulas to calculate safe loads"

Every function in our library follows these rules.
```

---

## File Map (Where to Look)

```
Python/structural_lib/
├── flexure.py              ← Functions for bending (Mu loads)
├── shear.py                ← Functions for sideways forces (Vu loads)
├── detailing.py            ← Functions for placing steel bars
├── materials.py            ← Properties of concrete/steel
├── tables.py               ← Lookup tables from IS 456
├── validation.py           ← Check if inputs make sense
├── api.py                  ← User-friendly wrappers (START HERE)
├── beam_pipeline.py        ← Orchestrates design flow
├── job_runner.py           ← Runs many beams at once
├── dxf_export.py           ← Creates CAD drawings
└── codes/is456/            ← IS 456-specific functions
```

---

## Success Criteria

By end of day:
- ✅ List of 100+ functions with 1-sentence descriptions
- ✅ Examples of when each function is used
- ✅ Simple explanations (no jargon)
- ✅ Connection map (how functions call each other)

---

## Next Steps (Tomorrow or Later)

Once we map all functions, we can:
- Write better tests
- Simplify the API (reduce 50+ functions to 10 most-used)
- Create interactive examples
- Build a design tutorial

---

**Let's start! Open `api.py` first — it's the cleanest entry point.**
