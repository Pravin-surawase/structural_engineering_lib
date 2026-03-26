# 200-Paper Literature Review — Complete Plan

**Status:** Ready to start
**Duration:** Jan 13 - Feb 10, 2026
**Target:** 200 papers systematically reviewed
**Scope:** Pareto optimization, visualization, carbon, automation

---

## Why 3 Weeks of Research?

You initially planned 7 weeks for implementation. But before coding, you realized:

1. **Academic rigor matters** — Code based on research is stronger than code based on assumptions
2. **Problem clarity matters** — The right problem, solved well, beats the wrong problem, solved perfectly
3. **Literature positioning matters** — Understanding what exists prevents reinventing wheels and clarifies your novel contribution

**Decision:** Invest 3 weeks in research foundation (Jan 13 - Feb 3), then 4 weeks in implementation (Feb 10 - Mar 3), informed by 200 papers.

**Output:** By Feb 10, you'll know:
- What's already been done (no need to repeat)
- What gaps exist (your opportunity)
- Best practices in visualization and automation (guide MVP)
- Carbon metrics for Indian context (ground sustainability module)

---

## Your 3-Week Research Mission

### Week 1: Pareto Optimization Fundamentals (70 papers)
**Jan 13-20**

**Questions to answer:**
- What is Pareto optimization really about?
- How do you extract Pareto frontiers efficiently?
- What algorithms work best?
- Has anyone applied this to concrete design?
- How do engineers understand trade-offs?

**Papers by phase:**
- Phase 1.1 (15): Pareto theory & algorithms
- Phase 1.2 (20): Multi-objective design methods
- Phase 1.3 (20): Concrete design optimization (existing approaches)
- Phase 1.4 (15): Decision-making under uncertainty

**Deliverable:** `week-1/KEY-FINDINGS.md` with answers to above questions

---

### Week 2: Visualization & HCI (70 papers)
**Jan 20-27**

**Questions to answer:**
- How do you visualize 3-4 competing objectives?
- What visualization patterns work best?
- How do engineers interact with trade-off data?
- What role does color play?
- What barriers prevent tool adoption?

**Papers by phase:**
- Phase 2.1 (15): Pareto front visualization
- Phase 2.2 (20): Information visualization for engineering
- Phase 2.3 (18): Decision support systems & UI
- Phase 2.4 (12): Color, perception & graphics
- Phase 2.5 (5): Clustering & archetypes

**Deliverable:** `week-2/KEY-FINDINGS.md` + recommended MVP visualization approach

---

### Week 3: Carbon & Automation (60 papers)
**Jan 27 - Feb 3**

**Questions to answer:**
- What are realistic carbon values for Indian concrete?
- How should carbon be weighted in optimization?
- What can be automated in design?
- Is ML/digital twins ready for design optimization?
- What are implementation barriers?

**Papers by phase:**
- Phase 3.1 (20): Carbon footprint & LCA
- Phase 3.2 (15): Sustainable design optimization
- Phase 3.3 (15): Design automation & algorithmic design
- Phase 3.4 (10): Digital twins & ML

**Deliverable:** `week-3/KEY-FINDINGS.md` + carbon data table + automation feasibility assessment

---

### Week 4: Synthesis & Positioning (Feb 3-10)
**No new papers this week — consolidation only**

**Outputs (4 documents):**

1. **SYNTHESIS-AND-GAPS.md**
   - What problems does literature solve?
   - What gaps exist?
   - Where does your work fit?

2. **UNIQUE-POSITIONING.md**
   - Your novel research angle
   - Why this hasn't been done before
   - Why you're uniquely positioned to do it

3. **ANNOTATED-BIBLIOGRAPHY.md**
   - All 200 papers organized by topic
   - Full citations + 1-2 sentence summary of each
   - Ready for your journal paper

4. **KEY-PAPERS.md**
   - Top 15-20 seminal papers
   - Why each matters
   - How each shapes your approach

**Output Timeline:**
- Feb 3: Draft outputs (rough)
- Feb 7: Review & consolidate
- Feb 10: Final outputs (ready for publication)

---

## Reading Pace & Daily Routine

### Pace Target
- **5-8 papers per day** (Mon-Fri during work weeks)
- **Reading depth:** Abstract + key sections (not cover-to-cover)
- **Time per paper:** 15-20 minutes
- **Time per day:** 2-3 hours
- **Weekly capacity:** 25-40 papers (target 70, 70, 60)

### Daily Routine (Example)

**Morning (30 min):**
1. Open SEARCH-STRATEGY.md
2. Identify today's phase
3. Find 5-8 new papers using provided queries
4. Record in PAPER-TRACKER.csv with status `📌 To Read`

**Afternoon/Evening (90-120 min):**
1. Read papers (10-20 min each)
2. Write 1-paragraph summary per paper
3. Update PAPER-TRACKER.csv: mark `✅ Read`
4. Add insights to `KEY-FINDINGS.md` for the week

**Sunday (30 min) — Weekly Consolidation:**
1. Review all papers from the week
2. Consolidate patterns in KEY-FINDINGS.md
3. Identify top papers from week (⭐ Key Paper status)
4. Prepare questions for next week

### Status Markers
Use these in PAPER-TRACKER.csv:
- `📌 To Read` — Found but not yet read
- `📖 Reading` — Currently reading
- `✅ Read` — Finished and summarized
- `⭐ Key Paper` — Top paper for this research
- `⚠️ Tangential` — Related but less critical

---

## Success Metrics

| Week | Target | Success Metric |
|------|--------|----------------|
| **1** | 70 papers | All papers in PAPER-TRACKER.csv, Phase 1 KEY-FINDINGS.md complete |
| **2** | 70 papers | Visualization recommendations documented, HCI lessons captured |
| **3** | 60 papers | Carbon data table populated, automation assessment complete |
| **4** | Synthesis | 4 outputs complete, positioning clear, 200-paper list done |

---

## File Structure

```
literature-review/
├── QUICK-START.md                              ← Start here!
├── SEARCH-STRATEGY.md                          ← All search queries (use this!)
├── PAPER-TRACKER.csv                           ← Master tracking (populate as you go)
├── 00-LITERATURE-REVIEW-PLAN.md                ← This file
├── README.md                                   ← Detailed instructions
│
├── week-1-pareto-optimization/
│   ├── 00-PAPERS-SUMMARY.md                   ← Add papers here as you read
│   └── KEY-FINDINGS.md                         ← Consolidate weekly insights
│
├── week-2-visualization-hci/
│   ├── 00-PAPERS-SUMMARY.md
│   └── KEY-FINDINGS.md
│
├── week-3-carbon-automation/
│   ├── 00-PAPERS-SUMMARY.md
│   └── KEY-FINDINGS.md
│
└── [Created Feb 10:]
    ├── SYNTHESIS-AND-GAPS.md                  ← Literature gaps
    ├── UNIQUE-POSITIONING.md                   ← Your novel angle
    ├── ANNOTATED-BIBLIOGRAPHY.md               ← Full 200-paper list
    └── KEY-PAPERS.md                           ← Top 15-20 papers
```

---

## Paper Source Quality Hierarchy

### Tier 1 (Prefer)
- Peer-reviewed journal articles
- Conference papers (IEEE, ACM, etc.)
- University theses (PhDs especially)
- Established conferences (ASCE, ACI for structural engineering)

### Tier 2 (Use with notes)
- Preprints (arXiv, ResearchGate)
- Industry white papers
- Technical reports
- Standards documents (IS 456, etc.)

### Tier 3 (Avoid or note limitations)
- Blog posts
- Lecture notes
- Non-peer-reviewed online content
- Marketing materials

---

## Search Strategies

### Google Scholar (Primary)
1. Go to scholar.google.com
2. Use search queries from SEARCH-STRATEGY.md
3. Sort by "recent first" OR "by citation count" (depends on goal)
4. Skim abstracts for relevance
5. Click "Cited by X" to find newer papers on same topic

### IEEE Xplore (Secondary)
1. Go to ieeexplore.ieee.org
2. Use Boolean search operators (AND, OR, NOT)
3. Filter by Content Type (Conferences, Journals)
4. Filter by publication date (last 10 years recommended)

### ScienceDirect (Tertiary)
1. Go to sciencedirect.com
2. Check if your institution has access
3. Use provided search terms
4. Filter by publication date and subject

---

## Citation & Reference Management

### Track Everything
Use PAPER-TRACKER.csv to record:
- Paper ID (P1-001, P2-015, etc.)
- Authors & year
- Title
- Journal/Conference
- URL (or DOI)
- Citation count
- Key contribution (1-2 sentences)

### Get PDFs
- University library proxy (use VPN)
- Author ResearchGate profiles
- Google Scholar "PDF" link
- Institutional repositories
- DOI links (doi.org/xxxxx)

### Organize Files
Create `_papers/` folder:
```
_papers/
├── P1-001_Author_2023.pdf
├── P1-002_OtherAuthor_2022.pdf
└── ...
```

---

## Special Considerations for India Context

When finding papers, look for:
- **Indian codes:** IS 456 (RC code), IS 800 (steel code)
- **Indian climate:** Tropical conditions, monsoon effects
- **Indian materials:** Local cement types, available reinforcement
- **Indian costs:** Labor and material costs vary significantly
- **Indian construction practices:** Different standards than Western approaches

---

## Week-by-Week Timeline

```
JAN 13 (Mon)       Week 1 Starts — Phase 1.1: Pareto theory
JAN 14-17 (Tue-Fri) Phase 1.1 & 1.2 — 28 papers
JAN 20 (Mon)       Phase 1.3 & 1.4 finish — Week 1 complete (70 papers)
                   Week 2 Starts — Phase 2.1: Visualization
JAN 21-24 (Tue-Fri) Phase 2.2 & 2.3 — 35 papers
JAN 27 (Mon)       Phase 2.4 & 2.5 finish — Week 2 complete (70 papers)
                   Week 3 Starts — Phase 3.1: Carbon
JAN 28-31 (Tue-Fri) Phase 3.2 & 3.3 — 30 papers
FEB 3 (Mon)        Phase 3.4 finishes — Week 3 complete (60 papers)
                   TOTAL: 200 PAPERS ✓
FEB 3-10           Week 4: Synthesis & positioning (no new papers)
FEB 10 (Mon)       READY FOR IMPLEMENTATION
```

---

## Getting Started (Right Now!)

1. ✅ Skim this document (you just did!)
2. Open `QUICK-START.md` (5 min read)
3. Open `SEARCH-STRATEGY.md`
4. Find your first 5 papers using Phase 1.1 searches
5. Record in PAPER-TRACKER.csv
6. Tonight: Read 2-3 papers
7. Tomorrow: Continue pace (5-8/day)

---

## What Success Looks Like

By **Feb 10:**
- ✅ 200 papers researched & documented
- ✅ 4 synthesis documents written
- ✅ Clear understanding of:
  - State of Pareto optimization in structural design
  - Best visualization practices for trade-offs
  - Realistic carbon values for concrete (India context)
  - Feasibility of design automation
- ✅ **Ready to implement with confidence**

---

## Reference & Support

| Question | Answer Location |
|----------|-----------------|
| How do I search? | SEARCH-STRATEGY.md |
| What should I read today? | QUICK-START.md |
| How deep should summaries be? | week-1/00-PAPERS-SUMMARY.md (examples) |
| How do I consolidate insights? | week-1/KEY-FINDINGS.md (template) |
| What if I find an especially useful paper? | Mark as `⭐ Key Paper` in TRACKER |
| What if a paper isn't relevant? | Mark as `⚠️ Tangential` and move on |

---

## Commitment

You're committing to:
- **3 weeks (Jan 13 - Feb 3)** of focused research
- **5-8 papers/day** reading pace
- **Daily documentation** in KEY-FINDINGS.md
- **Weekly consolidation** of insights
- **Feb 10 deadline** for implementation readiness

**In exchange:** Research-grounded implementation that's unique, credible, and well-positioned in literature.

---

*This is your map. Follow it daily. Trust the process. See you Feb 10!*

---

**Last updated:** Jan 13, 2026
**Next review:** Jan 20, 2026 (end of Week 1)
