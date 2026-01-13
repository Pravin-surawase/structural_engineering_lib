# Welcome to Your Onboarding! 👋

**You now have everything you need to learn this project.**

---

## 📚 Files Created For You Today

| File | Purpose | Read This | Duration |
|------|---------|-----------|----------|
| **NEW-DEVELOPER-ONBOARDING.md** | Understand the project mission, layers, and code structure | 1st (30 min) | 30 min |
| **QUICK-START.md** | Run your first beam design in 5 minutes | 2nd (actually run code) | 5 min |
| **FUNCTION-GUIDE.md** | Learn what each function does in plain English | 3rd (reference) | 60 min (skim) |
| **RESEARCH-PLAN.md** | Today's research task breakdown | 4th (optional) | 20 min |

---

## 🚀 Your Path (Recommended Order)

### Right Now (30 minutes total)
1. Read `NEW-DEVELOPER-ONBOARDING.md` — Understand big picture
2. Read `QUICK-START.md` — Run one example code
3. You'll understand: **What the library does, how it's organized, how to use it**

### Today (2-3 hours if interested)
4. Create and run `my_first_beam.py` from QUICK-START.md
5. Skim `FUNCTION-GUIDE.md` — Learn what functions exist
6. Try the batch design option (CSV → results)
7. You'll understand: **How to design beams, how to run code, where functions are**

### This Week (when you have time)
8. Read `docs/architecture/project-overview.md` — Design philosophy
9. Look at `Python/structural_lib/codes/is456/flexure.py` — See real code
10. Read tests: `grep -r "design_singly" Python/tests/` — See usage examples
11. You'll understand: **How code is structured, why decisions were made**

### This Month (ongoing)
12. Build something small (e.g., design 10 beams and compare to hand calc)
13. Write a test or documentation improvement
14. You'll understand: **How to contribute, how testing works**

---

## 💡 Key Concepts (Remember These)

### The Library Does One Thing
```
Input (beam dimensions, load, materials)
    → Pass through IS 456 rules
    → Output (required steel, safe or unsafe)
```

### Three Layers
1. **Core** = Pure math (flexure.py, shear.py, detailing.py)
2. **App** = Coordination (beam_pipeline.py, job_runner.py)
3. **UI** = User interface (CLI, Excel, DXF export)

### Units (IMPORTANT!)
- Dimensions: **mm** (not meters!)
- Stresses: **N/mm²** (same as MPa)
- Moments: **kN·m**
- Forces: **kN**

### Three Main Functions (95% of what you'll use)
1. `flexure.design_singly_reinforced()` — "How much steel do I need?"
2. `shear.design_shear()` — "What stirrup spacing?"
3. `detailing.decide_bar_arrangement()` — "Which bars to use?"

---

## ❓ Common Questions (Answered)

### Q: "I'm not a structural engineer. Can I still use this?"
**A:** Yes! Read the function guide. It explains without jargon. The code handles the IS 456 rules.

### Q: "How long until I can design a beam?"
**A:** 5 minutes. Run QUICK-START.md right now.

### Q: "What if I make a mistake?"
**A:** The library will tell you (e.g., "Beam is UNSAFE"). You won't accidentally create bad designs.

### Q: "Where do I find what a function does?"
**A:** Check `FUNCTION-GUIDE.md` in this folder. Or read the docstring in the code.

### Q: "Do I need to understand all 100+ functions?"
**A:** No. Focus on the 10 main ones first. You'll learn the rest as needed.

### Q: "Can I contribute?"
**A:** Yes! Start small: improve a docstring, add a test, fix a typo. Message me with ideas.

---

## 📍 Where Things Are

```
structural_engineering_lib/
├── docs/
│   ├── getting-started/
│   │   └── NEW-DEVELOPER-ONBOARDING.md   ← Start here!
│   ├── reference/
│   │   └── api.md                        ← Full API reference
│   ├── architecture/
│   │   └── project-overview.md           ← Design philosophy
│   └── research/
│       └── 01-function-catalog-research/ ← This folder
│           ├── README.md                 ← You are here
│           ├── QUICK-START.md            ← Run code
│           ├── FUNCTION-GUIDE.md         ← Learn functions
│           └── RESEARCH-PLAN.md          ← Today's tasks
│
├── Python/
│   ├── structural_lib/
│   │   ├── codes/is456/
│   │   │   ├── flexure.py                ← Bending functions
│   │   │   ├── shear.py                  ← Shear functions
│   │   │   └── detailing.py              ← Bar placement functions
│   │   ├── api.py                        ← User-friendly wrappers
│   │   └── ... (40+ other modules)
│   ├── tests/                            ← Real usage examples
│   └── examples/                         ← Sample designs
│
├── README.md                             ← Project overview
└── .github/                              ← CI/CD (ignore for now)
```

---

## ⚡ Super Quick Summary

**What is this library?**
A tool that tells you how much steel a concrete beam needs, using IS 456 rules.

**How do you use it?**
Pass beam dimensions + loads → get required steel.

**What language?**
Python (with VBA parallel).

**Who needs it?**
Structural engineers designing beams.

**Where's the code?**
`Python/structural_lib/`

**Where's the docs?**
`docs/` (and in this folder for beginners)

---

## 🎯 Your First Task (Optional)

If you want to learn by doing:

1. Open `QUICK-START.md`
2. Run the first example (5 minutes)
3. You'll see that designing a beam works!
4. Then read `FUNCTION-GUIDE.md` to understand what happened

---

## 🙋 Questions?

**When stuck:**
1. Check `FUNCTION-GUIDE.md` (probably answers it)
2. Check the docstring: `help(flexure.design_singly_reinforced)`
3. Look at tests: `grep -r "design_singly" Python/tests/`
4. Ask in the project issues

---

## 📝 Notes

- This project is **well-tested** (2,270 tests, 86% coverage)
- The **code is clean** (type hints, clear names, no jargon)
- **No previous knowledge needed** (guides are beginner-friendly)
- **It's production-ready** (published on PyPI, used in real projects)

---

## Next Steps

✅ Read: `NEW-DEVELOPER-ONBOARDING.md` (30 min)
✅ Run: `QUICK-START.md` (5 min)
✅ Learn: `FUNCTION-GUIDE.md` (reference as needed)
✅ Build: Design some beams (today or tomorrow)

---

**You're ready to start! Good luck! 🚀**

---

Created: 2026-01-13
For: New developers like you
Questions? Check the docs or create an issue
