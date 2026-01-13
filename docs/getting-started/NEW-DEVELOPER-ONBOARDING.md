# Onboarding Guide for New Developers
**Welcome to structural_engineering_lib! 🎓**

This guide is for you if:
- ✅ You're new to this project
- ✅ You don't know where to start
- ✅ You want to understand the big picture first
- ✅ You prefer plain English over jargon

---

## 30-Minute Getting Started

### Step 1: Understand the Mission (5 min)
**What is this project?**
- A library that automates concrete beam design following IS 456 (Indian standard)
- Takes beam dimensions + loads → outputs required steel + details
- Used by structural engineers to design beams faster and more accurately

**Real scenario:**
```
An engineer has 100 beams to design in a building.
Instead of 10 hours of hand calculations, they run our library.
Result: 10 minutes of work, zero manual errors, auditable outputs.
```

### Step 2: Understand the Layers (5 min)
**The library has 3 layers:**

```
┌─────────────────────────────────────────┐
│  LAYER 1: USER INTERFACE               │  ← You use this
│  (Excel, CLI, DXF export)              │
├─────────────────────────────────────────┤
│  LAYER 2: APPLICATION LOGIC            │  ← Coordinates work
│  (Orchestration, pipelines, jobs)      │
├─────────────────────────────────────────┤
│  LAYER 3: CORE MATH                    │  ← Pure calculations
│  (Flexure, shear, detailing, tables)   │
└─────────────────────────────────────────┘
```

**Why this matters:**
- Core math is **pure** (no Excel, no UI, no side effects)
- Application layer **coordinates** (calls core functions, makes decisions)
- User layer **displays** (formats results, handles input/output)

**Benefit:** You can change the UI without touching core math. Or add new calculations without touching the UI.

### Step 3: See One Complete Example (10 min)

**The simplest code:**
```python
from structural_lib import flexure

# Inputs (all in mm and N/mm²)
beam_width = 300          # b in mm
effective_depth = 450     # d in mm
moment = 150              # Mu in kN·m
concrete_grade = 25       # fck in N/mm²
steel_grade = 500         # fy in N/mm²

# Call the library
result = flexure.design_singly_reinforced(
    b=beam_width,
    d=effective_depth,
    mu_knm=moment,
    fck=concrete_grade,
    fy=steel_grade
)

# Get the answer
print(f"Steel needed: {result.ast_required:.0f} mm²")
print(f"Status: {'✅ SAFE' if result.is_safe else '❌ UNSAFE'}")
```

**What happened:**
1. We imported the `flexure` module (handles bending)
2. Defined beam properties and loads
3. Called `design_singly_reinforced()` (designs a beam with steel only on tension side)
4. Got back a result object with `ast_required` (area of steel needed) and `is_safe` (pass/fail)

**That's it.** Everything else is variations on this theme.

### Step 4: Understand the Directory Layout (5 min)

```
project_root/
├── Python/
│   ├── structural_lib/          ← The actual library
│   │   ├── flexure.py           ← Functions for bending
│   │   ├── shear.py             ← Functions for sideways forces
│   │   ├── detailing.py         ← Where to put steel bars
│   │   ├── materials.py         ← Concrete/steel properties
│   │   ├── tables.py            ← IS 456 lookup tables
│   │   ├── api.py               ← User-friendly functions (START HERE)
│   │   ├── validation.py        ← Check if inputs are valid
│   │   ├── codes/               ← Code-specific stuff (IS 456, etc.)
│   │   └── insights/            ← Design suggestions & analysis
│   │
│   ├── tests/                   ← Unit + integration tests
│   ├── examples/                ← Real usage examples
│   └── README.md
│
├── docs/                        ← Documentation
│   ├── README.md                ← Documentation index
│   ├── reference/               ← API docs
│   ├── getting-started/         ← Beginner guides
│   ├── research/                ← Research docs (like this!)
│   └── architecture/            ← Design decisions
│
├── scripts/                     ← Automation scripts
├── VBA/                         ← Excel macros (parallel to Python)
├── Excel/                       ← Excel workbooks
└── .github/workflows/           ← CI/CD automation
```

**Key files for you:**
- `Python/structural_lib/api.py` — Start here, cleanest API
- `docs/reference/api.md` — Function reference
- `docs/getting-started/` — Beginner tutorials
- `Python/tests/` — Real examples in test form

---

## Understanding the Code: Terms You'll See

| Term | Means | Example |
|------|-------|---------|
| **b** | Beam width (mm) | `b=300` → 300mm wide |
| **d** | Effective depth (mm) | `d=450` → 450mm from top to steel |
| **D** | Total depth (mm) | `D=500` → 500mm top to bottom |
| **Mu** or **Mu_knm** | Bending moment (kN·m) | `mu_knm=150` → 150 kN·m applied load |
| **Vu** or **Vu_kn** | Shear force (kN) | `vu_kn=100` → 100 kN sideways force |
| **Ast** | Area of steel (mm²) | Result = `942` → need 942 mm² of steel |
| **fck** | Concrete strength (N/mm²) | `fck=25` → 25 N/mm² concrete |
| **fy** | Steel strength (N/mm²) | `fy=500` → 500 N/mm² steel (same as Grade 500) |
| **is_safe** | Boolean (True/False) | `True` → beam is safe, `False` → unsafe |

**Units convention:**
- Dimensions: **mm**
- Stresses: **N/mm²** (same as MPa)
- Moments: **kN·m**
- Forces: **kN**
- Areas: **mm²**

**Why units matter:** We convert between mm and N at boundaries, but internally everything is consistent. If you use wrong units, you'll get wrong answers.

---

## The Big Picture: From Input to Output

```
USER INPUT (CSV, Excel, or code)
    ↓ [Validation]
VALIDATE DATA (Check b, d, Mu, etc. are sensible)
    ↓ [Design]
CALCULATE STEEL (Using flexure, shear formulas)
    ↓ [Detailing]
DECIDE BAR PLACEMENT (Using IS 13920 rules)
    ↓ [Export]
GENERATE OUTPUTS (JSON results, DXF drawings, BBS schedule)
    ↓
USER GETS (Results table, AutoCAD drawings, Bill of materials)
```

**Each arrow = a function call**

---

## Your First Task: Just Read Code

**Don't write anything yet. Just read.**

1. Open `Python/structural_lib/api.py`
2. Look at the `design_singly_reinforced()` function
3. See what it does:
   - Takes inputs (b, d, mu, fck, fy)
   - Calls core functions (in flexure.py)
   - Returns a result object
4. Now open `Python/structural_lib/flexure.py`
5. Look at the actual math inside `design_singly_reinforced()`
6. See:
   - Comments reference IS 456 clauses
   - Formulas match the clauses
   - Checks are done in order (geometry → strength → safety)

**Reading this flow shows you how it all works.**

---

## Common Mistakes (Learn From Others)

❌ **"I'll use wrong units"**
- Don't do: `b=0.3` (meters)
- Do this: `b=300` (millimeters)

❌ **"I won't check `is_safe` flag"**
- Always check if result is safe before using it
- Don't assume it will always succeed

❌ **"I'll skip the validation step"**
- Our validation catches 90% of user errors
- Always validate before designing

❌ **"I'll assume one function does everything"**
- Functions are single-purpose
- You'll often call multiple functions in sequence

✅ **Good practices:**
- Always use the type hints (they guide you)
- Read function docstrings first
- Look at examples in `Python/examples/`
- Run tests to see real usage: `grep -r "design_singly" tests/`

---

## What You Can Do With This Library

### 1. One Beam (Simple)
```python
from structural_lib import flexure

result = flexure.design_singly_reinforced(b=300, d=450, mu_knm=150, fck=25, fy=500)
print(result.ast_required)  # Done!
```

### 2. Multiple Beams (CSV)
```bash
python3 -m structural_lib design beams.csv -o results.json
```

### 3. Full Pipeline (Design → Detailing → Schedule → DXF)
```bash
python3 -m structural_lib design input.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

### 4. In Excel (VBA)
```vba
result = IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 415)
```

### 5. Insights & Optimization
```python
from structural_lib import api

insights = api.smart_analyze_design(
    b=300, d=450, fck=25, fy=500, mu_knm=150, vu_kn=80
)
# Get cost, suggestions, sensitivity analysis, etc.
```

---

## How to Learn More

### Reading Order (Recommended)
1. **Today:** This guide (you're here ✓)
2. **Today:** Read api.py (understand user-facing functions)
3. **Today:** Read flexure.py (understand core math)
4. **Tomorrow:** Function catalog research (map the whole library)
5. **This week:** docs/reference/api.md (complete reference)
6. **This week:** docs/architecture/project-overview.md (design philosophy)

### Interactive Learning
```bash
# See all available commands
python3 -m structural_lib --help

# Run a simple design
python3 -m structural_lib design examples/sample_beam_design.csv -o out/

# See what was output
cat out/results.json | python3 -m json.tool | head -50
```

### Running Examples
```bash
cd Python

# Run one example
python3 -c "
from structural_lib import flexure
r = flexure.design_singly_reinforced(b=300, d=450, mu_knm=150, fck=25, fy=500)
print(f'Ast = {r.ast_required:.0f} mm²')
"

# Run the full test suite to see patterns
python3 -m pytest tests/ -v -k "singly" | head -30
```

---

## The Project Structure (Simplified)

**What you should know:**
- Core logic lives in `Python/structural_lib/` (this is the real gem)
- Tests are in `Python/tests/` (learn by reading tests)
- Documentation is in `docs/` (reference as needed)
- Automation/scripts can be ignored for now (you don't need them)
- VBA is parallel (same functions, different language)

**What you can ignore for now:**
- Git workflow automation (not needed yet)
- Agent roles (that's for team collaboration)
- Governance scripts (too complex at first)
- The 730 markdown files (overwhelming; I already told you it's bloated)

---

## Today's Homework (Optional)

1. **Read:** This guide (30 min)
2. **Install:** Follow the Python setup in README.md (15 min)
3. **Run:** One simple example (10 min)
4. **Read:** Open `Python/structural_lib/api.py` and skim it (20 min)
5. **Explore:** Run `python3 -m structural_lib --help` (5 min)

**Total: ~80 minutes**

By end of day, you'll understand:
- ✅ What the library does
- ✅ How to use it in 3 ways (code, CLI, Excel)
- ✅ Where the main functions are
- ✅ What the core concept is (beam design = inputs → steel requirements)

---

## Questions to Ask Yourself

As you learn, ask these:
- "What inputs does this function take?" → Read function signature
- "What does it return?" → Read the docstring
- "When would I use this?" → Look at tests for examples
- "Does it follow IS 456?" → Read the comments with clause refs

---

## Next Steps (After Onboarding)

- **Week 1:** Read core modules (flexure, shear, detailing)
- **Week 2:** Understand the test structure and write your first test
- **Week 3:** Build something small (e.g., cost calculator for multiple grades)
- **Week 4:** Contribute a feature or doc improvement

---

## You're Ready! 🚀

**Seriously. You now know:**
1. What this library does
2. Where to find things
3. How to run it
4. Why it's organized this way

The rest is just reading code and asking questions.

**Start with:** `Python/structural_lib/api.py` — it's the cleanest entry point.

---

**Created:** 2026-01-13
**For:** New developers
**Questions?** Check `docs/getting-started/` or create an issue
