# Quick Reference: Problem Selection Guide

**Use this to make a quick decision (5 min)**

---

## 🎯 THE FAST DECISION TREE

```
START HERE
│
├─ Question 1: How much time can you invest?
│  ├─ < 2 weeks total → Go to QUICK WINS
│  ├─ 2-4 weeks total → Go to MEDIUM EFFORT
│  └─ 4+ weeks total → Go to DEEP RESEARCH
│
├─ Question 2: What's your primary goal?
│  ├─ Ship user value ASAP → Pick QUICK WINS
│  ├─ Build next big feature → Pick DEEP RESEARCH
│  └─ Improve quality baseline → Pick QUALITY IMPROVEMENTS
│
└─ Question 3: What's your technical interest?
   ├─ Optimization, algorithms → #1 Bar Placement
   ├─ Numerical methods, solvers → #2 Depth Iterator
   ├─ Rules, validation, QA → #6 Congestion
   └─ Advanced physics/stats → #3, #4, #5
```

---

## 📊 THREE RECOMMENDATION COMBOS

### 🏃 **OPTION 1: SPRINT (Ship in 2 Weeks)**
- **Pick: #2 Effective Depth Solver**
- **Effort:** 4-5 days (1 week)
- **Then:** Add #6 Congestion (7-8 days) if time allows
- **Ship:** v0.17.1 with 2 features
- **Best For:** Quick momentum, user feedback
- **Risk:** Low

```
Week 1: Depth Solver (prototype + test)
Week 2: Congestion Analysis OR release #2 only
Release v0.17.1
```

### 🎯 **OPTION 2: FLAGSHIP (Ship in 6-8 Weeks)**
- **Pick: #1 Bar Placement Optimization**
- **Effort:** 17 days (research + dev + test)
- **First:** 2 weeks of research (algorithms, cost models, validation)
- **Then:** 2 weeks of development (discrete optimizer)
- **Finally:** 1-2 weeks of testing + integration
- **Ship:** v0.17.2 or v0.18.0 (major feature)
- **Best For:** Market differentiation, big impact
- **Risk:** Medium (optimization complexity)

```
Week 1-2: Research bar algorithms + IS 456 table parsing
Week 3-4: Prototype ILP solver with simple cost model
Week 5-6: Integration into BBS + comprehensive testing
Week 7-8: Buffer + refinement
Ship v0.18.0 (flagship feature)
```

### ⚖️ **OPTION 3: BALANCED (Ship Quick + Plan Big)**
- **Pick: #2 + #6 for v0.17.1, then deep research on #1**
- **Effort:** 2 weeks sprint (shipping) + 2 weeks research (planning)
- **Best For:** Maintaining momentum while planning next innovation
- **Risk:** Low

```
Week 1: #2 Depth Solver (4-5 days)
Week 2: #6 Congestion Analysis (7-8 days) → Ship v0.17.1
Week 3-4: Deep research on #1 (lit review, algorithm design, validation plan)
Week 5+: Decide: commit to #1 or pivot?
```

---

## 🔍 QUICK PROBLEM SUMMARIES

### **#1: Bar Placement Optimization** 🌟 FLAGSHIP
- **What:** Auto-suggest bar diameters and spacing (e.g., "4×Φ16 @ 150mm")
- **Why:** Saves engineers 40% of design time, improves quality
- **Time:** 17 days (2.5 weeks)
- **Math:** Integer linear programming (discrete optimization)
- **Pick if:** You want a game-changing feature that differentiates the product

---

### **#2: Effective Depth Iterator** ⚡ QUICK WIN
- **What:** Auto-find minimum depth D that satisfies flexure and shear
- **Why:** Saves engineers 15% time on iterative design
- **Time:** 4-5 days (less than 1 week)
- **Math:** Binary search (simple univariate optimization)
- **Pick if:** You want to ship value FAST and build momentum

---

### **#3: Crack Width Prediction** 📐 MISSING FEATURE
- **What:** Calculate concrete crack width under service loads (IS 456 Cl. 39.1)
- **Why:** Completes durability/serviceability checks
- **Time:** 9-11 days
- **Math:** Empirical formulas + iterative calculation
- **Pick if:** You want professional-grade completeness

---

### **#4: Multi-Span Continuous Beams** 🏗️ MAJOR EXPANSION
- **What:** Design 3+ span continuous beams with moment redistribution
- **Why:** Covers 60% of real-world buildings (vs. single-span now)
- **Time:** 28-30 days (6 weeks)
- **Math:** Structural FEA, slope-deflection method
- **Pick if:** You're ready for v1.0 scope expansion

---

### **#5: Probabilistic Design** 📊 ADVANCED
- **What:** Quantify safety margins under material/load uncertainty
- **Why:** Appeals to research users, climate adaptation, risk assessment
- **Time:** 22 days
- **Math:** Monte Carlo, UQ, fragility curves
- **Pick if:** You want to serve advanced users (research/consulting)

---

### **#6: Bar Spacing & Congestion** ✅ QUALITY
- **What:** Validate that proposed bars physically fit (spacing rules, width constraints)
- **Why:** Catches design errors before they reach site
- **Time:** 7-8 days
- **Math:** Constraint satisfaction (simple rules)
- **Pick if:** You want to improve quality baseline without big innovations

---

## 💬 QUICK POLL (Pick ONE)

**Which of these resonates with you most?**

A. "We need to ship something FAST to keep momentum" → **#2 (4-5 days)**
B. "We need a flagship feature that sets us apart" → **#1 (17 days)**
C. "We need to improve professional credibility" → **#3 or #6** (9-11 days or 7-8 days)
D. "We need to handle real-world complexity" → **#4 (28-30 days)**
E. "We need to serve advanced users" → **#5 (22 days)**
F. "I want to explore all of these before deciding" → **Feasibility study** (Path D)

---

## 🎬 IMMEDIATE NEXT STEPS

### If you picked A, B, C, or E:
```bash
# I'll create detailed spec & pseudocode for your choice
# You can start coding TODAY
```

### If you picked D:
```bash
# This is big - need to research structural FEA libraries first
# Would you like a 3-day feasibility study?
```

### If you picked F:
```bash
# I'll create 2-day deep-dive research for top 3 problems
# Report back in 1 week with findings
```

---

## 📌 DECISION CHECKLIST

Before you pick, answer:

- [ ] **Timeline:** Do you have 1 week, 2-3 weeks, or 6+ weeks?
- [ ] **Team:** Are you solo, duo, or team of 3+?
- [ ] **User Demand:** What do customers ask for most?
- [ ] **Product Vision:** What does v0.17 / v0.18 / v1.0 need?
- [ ] **Technical Interest:** What excites you to research?

---

## 🚀 LET'S SHIP

**Tell me which letter (A-F) and I'll:**
1. Create a detailed specification document
2. Outline the pseudocode/algorithm
3. Identify test cases
4. Set up a task in TASKS.md
5. Get you ready to code TODAY

What's your pick? 🎯
