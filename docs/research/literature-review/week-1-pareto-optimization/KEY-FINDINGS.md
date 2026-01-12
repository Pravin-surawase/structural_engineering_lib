# Week 1: Key Findings & Insights

## Consolidation of Pareto Optimization Research

This document consolidates the key insights from all Week 1 papers. Update daily as you read.

---

## Main Insights (Evolving)

### What is a Pareto Frontier?
*[To be filled as you read papers on Pareto theory]*

- **Definition:**
- **Key properties:**
- **Why it matters:**

### Pareto Optimality in Engineering Design
*[Insights from concrete design and MOO papers]*

- **How it applies to structural design:**
- **Trade-offs engineers care about:**
- **Constraints that matter:**

---

## Research Q&A ✅ ANSWERED FROM PHASE 1.2 PAPERS (WEB RESEARCH)

### Q1: How do engineers choose between competing objectives in practice?
**Answer:** *Phase 1.2 Web Research Findings (6 abstracts analyzed)*
- **Decision Psychology (Noti et al., 2025):** There is a fundamental trade-off between recommending the most accurate features vs. those that align with the human's existing understanding. System patience and human learning speed significantly impact long-term decision quality.
- **Preference Structures (Chen et al., 2025):** Engineers often use "soft" (aspirational) and "hard" (non-negotiable) bounds. Trust is built when the system can prove that no superior alternatives were missed (using sensitivity analysis like T-MoSH).

### Q2: What decision support systems and interfaces exist?
**Answer:**
- **ParetoLens (Ma et al., 2025):** An algorithm-agnostic visual analytics framework that uses modular interactive representations to explore high-dimensional Pareto sets, specifically designed to mitigate visual clutter.
- **Active-MoSH (Chen et al., 2025):** An interactive local-global framework that maintains probabilistic preference models to guide users through expensive evaluation spaces.
- **Orbit (Yang et al., 2024):** A conceptual framework for objective-centric iteration. It uses "boundary objects" to facilitate communication between cross-functional teams and allows real-time exploration of design trade-offs.
- **EMO Visual Analytics (Huang et al., 2023):** Provides interactive visualization for comparing internal evolutionary processes of multiple algorithms, moving beyond black-box analysis.

### Q3: How are constraints handled in real applications?
**Answer:**
- **Inverse Design (Awan et al., 2025):** Inverse design (structure-to-property mapping) uses constrained multi-objective regression. q-EHVI remains the gold standard for convergence in these high-dimensional numerical spaces.
- **Probabilistic Scaling (Chen et al., 2025):** Handling strict "hard" bounds alongside soft preferences is a key requirement for high-stakes domains (comparable to structural codes).
- **Concept Identification (Lanfermann et al., 2023):** Sorting configuration options into "concepts" based on description spaces (partitioning objectives and parameters) helps manage thousands of Pareto solutions by grouping them into meaningful viable sets.

### Q4: Robustness and sensitivity analysis approaches?
**Answer:**
- **T-MoSH (Chen et al., 2025):** Employs multi-objective sensitivity analysis to identify potentially overlooked high-value points beyond the immediate feedback loop, reinforcing decision-maker trust.
- **Lexicographic Sorting (Zhang et al., 2024):** Uses lexicographic optimization to handle non-monotonic criteria and rectify inconsistencies in decision-maker preference feedback, ensuring robust preference learning.
- **Trustworthy Automation Guidelines (Jelinek et al., 2025):** Emphasizes calibrated trust through Gricean communication maxims—ensuring the system provides relevant, true, and clear cues for the user to accurately assess system reliability.

### Q5: Uncertainty quantification and probabilistic design?
**Answer:**
- **Collaborative UQ (Noorani et al., 2025):** AI should complement human experts by identifying outcomes they missed while avoiding "counterfactual harm" (not degrading correct human judgment). Optimal sets follow a two-threshold structure over a single score function.
- **Pareto Set Learning (Lin et al., 2022):** Learns a continuous model of the entire Pareto set rather than just a finite set of points. This allows for infinite high-quality trade-off exploration and better capture of structural properties in expensive MOO.
- **Preference-Guided Diffusion (Annadani et al., 2025):** Uses classifier-guided diffusion models (trained on preferences) to generate diverse Pareto-optimal designs outside the initial training distribution.

---

## Literature Landscape Map

### Week 1 Research Categories

```
PARETO OPTIMIZATION
├── Theory
│   ├── Pareto frontier definition & properties
│   ├── Efficiency metrics
│   └── Mathematical foundations
│
├── Algorithms
│   ├── Genetic algorithms (NSGA-II workhorse)
│   ├── Bayesian Optimization (qEHVI - Benchmark Gold Standard)
│   ├── Pareto Set Learning (PSL - modeling continuous manifolds)
│   ├── Classifier-Guided Diffusion (Generative Pareto sets)
│   └── Evolutionary Multi-Objective Optimization (EMO)
│
├── Engineering Applications
│   ├── Structural design (Arch dams, Building reconstruction - code integration)
│   ├── Mechanical Design (Vehicle suspension recommendation - multi-fidelity)
│   ├── Materials Informatics (Inverse design for resins/polymers)
│   ├── Energy Management (Building efficiency concepts)
│   └── Structural Health Monitoring (NN architecture selection)
│
└── Decision Support & HCI
    ├── Visual Analytics (ParetoLens - modular charts; EMO comparison)
    ├── Preference Elicitation (Active-MoSH, Direct Preference Optimization - DPO)
    ├── Collaborative UQ (Human-AI complementarity; Avoiding Counterfactual Harm)
    ├── Trustworthiness Assessment (Six Design Guidelines; calibrated trust)
    └── Decision Psychology (Learning vs Accuracy trade-offs; Boundary objects)
```

### Key Findings by Phase

**Phase 1.1 — Pareto Theory (15 papers)**
- Foundations: NSGA-II remains the industry workhorse; MOEA/D for high-dimensional problems.

**Phase 1.2 — MOO Methods (20 papers)**
- 2025 Trends: Convergence on qEHVI as performance ceiling; shift towards Interactive Preference Learning with soft/hard bounds; emergence of LLMs as fast generative optimizers for inverse design.

**Phase 1.3 — Concrete Design (20 papers)**
- **Emerging Frameworks (Parhi et al., 2026):** State-of-the-art approach integrating nonlinear MOEA with interpretable ML to ensure "rigorous compliance to structural codes" (IS 456 context).
- **RC Beam Pareto Sets (Hong & Nguyen, 2023):** Specialized algorithms (ANN-based Hong-Lagrange) now being used to generate frontiers specifically for reinforced concrete beams.
- **Sustainability Optimization (Santos et al., 2023):** Shifting focus from cost-only to tri-objective optimization: **Cost vs. CO2 vs. Performance (Crack Prevention)**.
- **Whole-Building Logic (Kumar et al., 2025):** Applying NSGA-II to entire reinforced concrete structures rather than isolated elements.

**Phase 1.4 — Decision-Making (15 papers)**
- [To be filled - Focus on UX/UI patterns for engineers]

---

## Conceptual Maps

### Pareto Frontier in Structural Design

```
Objectives for RC Beams
├── Cost
│   ├── Material cost
│   ├── Labor cost
│   └── Construction complexity
│
├── Performance
│   ├── Strength (ultimate)
│   ├── Stiffness (serviceability)
│   ├── Ductility
│   └── Durability
│
├── Environmental
│   ├── Carbon footprint
│   ├── Material embodied energy
│   └── Waste minimization
│
└── Constructability
    ├── Ease of reinforcement
    ├── Formwork complexity
    └── Quality assurance
```

### MOO Algorithm Selection Criteria

```
Choose algorithm based on:
├── Problem characteristics
│   ├── Number of objectives (2-5)
│   ├── Problem size (variables)
│   ├── Function complexity
│   └── Constraints (linear/nonlinear)
│
├── Desired properties
│   ├── Convergence speed
│   ├── Front diversity
│   ├── Computational cost
│   └── Implementation ease
│
└── Application context
    ├── Real-time vs batch
    ├── User interaction
    ├── Visualization needs
    └── Decision support needs
```

---

## Patterns Observed

### In Pareto Theory Literature
- [Observations will be added as you read]
- [What themes keep appearing?]
- [What's consistent vs controversial?]

### In Concrete Design Literature
- [What optimization attempts exist?]
- [What's been avoided?]
- [Why?]

### In Decision-Making Literature
- **Heavy User Integration (Kim et al., 2025):** Users often view AI as either "rational consultants" or "average human proxies." Integration involves social validation and optimized cognitive resource allocation.
- **Trust Calibration (Jelinek et al., 2025):** Trust is not absolute; it must be "calibrated"—meaning high trust in reliable ranges and rational skepticism in error-prone ranges.
- **Communication Maxims:** Effective decision support follows Gricean maxims (be reasonably informative, truthful, relevant, and clear).
- **Learning vs Accuracy (Noti et al., 2025):** Systems should balance recommending optimal solutions with preserving the human's ability to learn and stay engaged.

---

## Gaps Identified

### In Research Literature
- [ ] Gap 1: [To be identified]
- [ ] Gap 2: [To be identified]
- [ ] Gap 3: [To be identified]

### In Concrete Design Optimization
- [ ] No multi-objective approach for RC beams (maybe?)
- [ ] [More gaps to identify]

### In User Decision Support
- [ ] [Gaps in how tools support engineer decisions]

---

## Week 1 Deliverables Checklist

- [ ] 70 papers found and recorded in PAPER-TRACKER.csv
- [ ] All 70 papers summarized in this file (1-2 paragraphs each)
- [ ] Main insights consolidated (above sections filled in)
- [ ] Gaps identified for Weeks 2-3 research focus
- [ ] Key papers identified for deeper study (5-7 papers)
- [ ] Questions prepared for Week 2 visualization research

---

## Key Questions for Week 2

Based on Week 1 research, these questions will guide Week 2:

1. **Visualization Challenge:** How should we visualize 3-4 competing objectives for engineers?
2. **Interaction Patterns:** What interaction patterns help engineers explore Pareto trade-offs?
3. **Color & Perception:** How do engineers perceive trade-off information? (Color? Shape? Position?)
4. **Decision Support:** What additional information helps engineers make choices?
5. **Tool Usability:** What barriers prevent adoption of MOO-based design tools?

---

## Research Integrity Log

**Purpose:** Track sources and ensure citation accuracy

| Paper ID | Authors | Title | Status | Date Read | Notes |
|----------|---------|-------|--------|-----------|-------|
| P1-001   | [To fill] | [To fill] | ✅ | [To fill] | [To fill] |

*[Add row for each paper as you read it. This ensures we can cite everything properly later.]*

---

*Last updated: [Today's date] — Progress: [X/70 papers read]*
