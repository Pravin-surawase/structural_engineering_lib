# RESEARCH FOLDER INDEX — How to Use These Documents

**Type:** Navigation Guide
**Status:** Active
**Created:** 2026-01-13
**Archive After:** 2026-01-27

---

## 📂 FOLDER STRUCTURE

```
docs/research/
├── PHASE-4-PARETO-DEEP-RESEARCH.md
│   └─ The original deep dive (where we identified unsolved problems)
│
├── PHASE-5-PRAGMATIC-PARETO.md
│   └─ Your breakthrough insight (visual approach instead of GA)
│
├── RESEARCH-STATUS-VISUAL.md
│   └─ Summary of 6 big ideas + decision matrix
│
├── _online-research/ (THIS FOLDER - ARCHIVE JAN 27)
│   ├── INDEX.md (this file)
│   ├── VISUALIZATION-BEST-PRACTICES.md (how to make "wow" graphs)
│   ├── API-CAPABILITY-ANALYSIS.md (what your library can do)
│   ├── ISSUES-RISKS-CONSIDERATIONS.md (gotchas + best practices)
│   └── RESEARCH-SYNTHESIS.md (ready to build summary)
│
└── [Other research docs...]
```

---

## 🎯 QUICK NAVIGATION

### If you want to understand the VISUALIZATION STRATEGY:
→ Read: `RESEARCH-STATUS-VISUAL.md` (5 min overview)
→ Then: `_online-research/VISUALIZATION-BEST-PRACTICES.md` (detailed guide)

### If you want to know WHAT YOUR LIBRARY CAN DO:
→ Read: `_online-research/API-CAPABILITY-ANALYSIS.md` (complete inventory)

### If you want to PLAN THE IMPLEMENTATION:
→ Read: `_online-research/RESEARCH-SYNTHESIS.md` (implementation plan)
→ Then: `_online-research/ISSUES-RISKS-CONSIDERATIONS.md` (gotchas)

### If you want ALL THE DETAILS on Pareto theory:
→ Read: `PHASE-4-PARETO-DEEP-RESEARCH.md` (comprehensive background)

### If you want YOUR specific approach explained:
→ Read: `PHASE-5-PRAGMATIC-PARETO.md` (your visual frontier method)

---

## 📋 DOCUMENTS AT A GLANCE

| Document | Purpose | Read Time | When to Use |
|----------|---------|-----------|------------|
| VISUALIZATION-BEST-PRACTICES.md | How to make graphs that make engineers say "wow" | 20 min | Design UI mockups |
| API-CAPABILITY-ANALYSIS.md | What functions exist, what you need to build | 25 min | Plan coding tasks |
| ISSUES-RISKS-CONSIDERATIONS.md | Gotchas, assumptions to validate, best practices | 15 min | Risk planning |
| RESEARCH-SYNTHESIS.md | Implementation plan + readiness checklist | 15 min | Start coding |
| PHASE-4-PARETO-DEEP-RESEARCH.md | Theory background + prior work | 30 min | Deep dive |
| PHASE-5-PRAGMATIC-PARETO.md | Your approach explained in detail | 20 min | Understanding your method |
| RESEARCH-STATUS-VISUAL.md | High-level summary of ideas | 10 min | Quick overview |

---

## 🔑 KEY FINDINGS (TL;DR)

### For Visualization
✅ Use 2D scatter plot (cost vs weight)
✅ Color-code for 3rd objective (carbon, depth)
✅ Interactive exploration beats static charts
✅ Cluster into 5-7 archetypes for decision-making
⚠️ Avoid >4 objectives per visualization (gets confusing)

### For Your Library
✅ 80% ready to go (design, cost, validation all exist)
🔨 Need: carbon module, batch processor, design space expansion
⏱️ Performance: 1-2 min for 1000 designs (acceptable)
💡 No surrogates needed—just use your fast library!

### For Implementation
🎯 MVP: Scatter plot + filters + click-to-details (4 weeks)
📈 Phase 2: Archetypes + comparison + carbon insights (2 weeks)
✅ Validation: Spot-check 20 designs against hand-calcs (1 week)
👥 User testing: 3-5 engineers, iterate (1-2 weeks)
📄 Paper + open-source: Publish + release (1 week)

### For Risks
⚠️ Cost accuracy ±20% (document, don't over-optimize)
⚠️ Design space limited in current lib (extend M20, M35, M40)
⚠️ Real-time interactivity trades off against accuracy
⚠️ Validation is 20% of effort (don't skip!)

---

## 🚀 HOW TO USE THESE DOCS

### Phase 1: PLAN (This Week - Jan 13-17)
1. Read `RESEARCH-SYNTHESIS.md` (understand what to build)
2. Read `ISSUES-RISKS-CONSIDERATIONS.md` (understand gotchas)
3. Read `API-CAPABILITY-ANALYSIS.md` (understand tools)
4. Read `VISUALIZATION-BEST-PRACTICES.md` (design mockups)
→ **Output:** Implementation plan + design mockups

### Phase 2: BUILD (Weeks 2-5 - Jan 17-Feb 10)
- Keep `API-CAPABILITY-ANALYSIS.md` handy (code reference)
- Reference `ISSUES-RISKS-CONSIDERATIONS.md` when making decisions
- Consult `VISUALIZATION-BEST-PRACTICES.md` for UI design
- Use `RESEARCH-SYNTHESIS.md` weekly implementation plan
→ **Output:** Working MVP

### Phase 3: VALIDATE (Week 6 - Feb 10-17)
- Reference `ISSUES-RISKS-CONSIDERATIONS.md` (validation strategy)
- Use `RESEARCH-SYNTHESIS.md` (spot-check 20 designs)
- Test with engineers → iterate
→ **Output:** Validated tool

### Phase 4: PUBLISH (Week 7-8 - Feb 17-24)
- Use all docs for paper writing
- Reference theory from `PHASE-4-PARETO-DEEP-RESEARCH.md`
- Reference approach from `PHASE-5-PRAGMATIC-PARETO.md`
→ **Output:** Journal paper + code release

---

## 📌 DOCUMENT DEPENDENCIES

```
Start Here
    ↓
RESEARCH-SYNTHESIS.md (overview)
    ├──→ API-CAPABILITY-ANALYSIS.md (what to build)
    ├──→ ISSUES-RISKS-CONSIDERATIONS.md (what to watch out for)
    ├──→ VISUALIZATION-BEST-PRACTICES.md (UI design)
    ↓
Implementation Planning
    ├──→ PHASE-5-PRAGMATIC-PARETO.md (your approach)
    ├──→ PHASE-4-PARETO-DEEP-RESEARCH.md (theory deep-dive)
    └──→ Code + Build
```

---

## 🎯 WHAT TO KEEP AFTER ARCHIVAL

When you archive this folder (Jan 27), keep these insights in your main documentation:

**In:** `docs/research/PARETO-OPTIMIZATION-FINAL.md` (new file when archiving)

```markdown
## Key Implementation Insights (from Jan 13 research)

1. **Visual Approach Works**
   - Your 2D scatter + interactivity is better than complex algorithms
   - Engineers learn more from exploring graphs than reading papers

2. **Library is Ready**
   - 80% complete, need only: carbon + batch + extended search space
   - ~10 hours to extend, then ready to generate 1000 designs

3. **Validation is Critical**
   - Spot-check 20 designs against hand calcs (non-negotiable)
   - Takes 1 week but prevents embarrassment in paper

4. **Archetypes Help**
   - Clustering 50 frontier designs into 5-7 archetypes reduces paralysis
   - Engineers pick "philosophy" first, then design within it

5. **MVP Timeline**
   - Weeks 1-4: Core visualization (scatter + filters + details)
   - Weeks 5-6: Insights (archetypes + comparison)
   - Week 7: User testing & iteration
   - Week 8: Paper & release
```

---

## 📅 ARCHIVAL PLAN

**When:** January 27, 2026 (or when implementation fully starts)

**How:**
1. Move entire `_online-research/` folder to `docs/_archive/research-20260113/`
2. Create note: "Archived after MVP implementation start. Key insights preserved in PARETO-OPTIMIZATION-FINAL.md"
3. Keep only `PHASE-4-PARETO-DEEP-RESEARCH.md` and `PHASE-5-PRAGMATIC-PARETO.md` in main research folder

**Why:**
- Keep working research folder focused on current work
- Archive detailed research for historical reference
- Prevents research folder from becoming "folder of old stuff"

---

## 💡 TIPS FOR USING THESE DOCS

### Tip 1: Print the Summary
Print `RESEARCH-SYNTHESIS.md` (2-3 pages) and keep it on your desk
- Quick reference during implementation
- Shows you're on track

### Tip 2: Use as Architecture Guide
`API-CAPABILITY-ANALYSIS.md` shows exactly what functions to call
- Section "Step 1-5" is your code blueprint
- Just translate to Python/Streamlit

### Tip 3: Risk Checklist Before Coding
Before each week, review `ISSUES-RISKS-CONSIDERATIONS.md`
- "Are we falling into any anti-patterns?"
- "What did we need to remember?"

### Tip 4: Visualization Reference
`VISUALIZATION-BEST-PRACTICES.md` shows what works
- Come back to it when UX feels wrong
- Has citations for why certain approaches work

### Tip 5: Theory When Doubting
If you doubt the approach, read `PHASE-5-PRAGMATIC-PARETO.md`
- Reminds you why visual frontier is better than GA
- Boosts confidence when implementation gets hard

---

## 🤔 COMMON QUESTIONS

**Q: Can I skip the research and just code?**
A: No, don't. The research saved you from:
- Building surrogates (wrong approach)
- Implementing complex GA (unnecessary)
- Missing carbon footprint (essential for wow)
- Skipping validation (will break paper)

**Q: Do I need to read all documents?**
A: No, start with `RESEARCH-SYNTHESIS.md`, then read as needed

**Q: When should I archive these?**
A: Jan 27 when you've finished Week 1 planning. Earlier if you're confident in the plan.

**Q: Can I modify these after starting?**
A: Yes, if you discover new issues:
1. Add to `ISSUES-RISKS-CONSIDERATIONS.md`
2. Update `RESEARCH-SYNTHESIS.md` if plan changes
3. Note the date of change

---

## ✅ VERIFICATION CHECKLIST

Before moving to implementation, verify:

- [ ] Read `RESEARCH-SYNTHESIS.md` (understand plan)
- [ ] Reviewed `API-CAPABILITY-ANALYSIS.md` (know what exists)
- [ ] Identified risks from `ISSUES-RISKS-CONSIDERATIONS.md`
- [ ] Sketched visualizations from `VISUALIZATION-BEST-PRACTICES.md`
- [ ] Understand your approach from `PHASE-5-PRAGMATIC-PARETO.md`
- [ ] Understand why this approach from `PHASE-4-PARETO-DEEP-RESEARCH.md`
- [ ] Have implementation plan written (from synthesis doc)
- [ ] Identified 3-5 engineers for user testing
- [ ] Target journal/venue identified
- [ ] GitHub repo ready for open-source

If all ✅, you're ready to build! 🚀

---

## 📞 QUICK REFERENCE LINKS

**For UI Design Questions:** `_online-research/VISUALIZATION-BEST-PRACTICES.md`
**For Coding Questions:** `_online-research/API-CAPABILITY-ANALYSIS.md`
**For Risk Questions:** `_online-research/ISSUES-RISKS-CONSIDERATIONS.md`
**For Timeline Questions:** `_online-research/RESEARCH-SYNTHESIS.md`
**For Theory Questions:** `PHASE-4-PARETO-DEEP-RESEARCH.md`
**For Approach Explanation:** `PHASE-5-PRAGMATIC-PARETO.md`

---

**Last Updated:** 2026-01-13
**Archive Status:** Ready to archive Jan 27
**Next Review:** Before moving to Phase 2 planning (Jan 17)
