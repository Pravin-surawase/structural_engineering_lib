# Phase 1.3: Bridging MOO with Structural Engineering (IS 456)

**Type:** Research
**Audience:** Developers, Structural Engineers, AI Agents
**Status:** In-Progress
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Related Tasks:** RESEARCH-1.3 (docs/planning/TASKS.md)

---

## 🏗️ Overview

This phase synthesizes the "bridge" between the broad multi-objective optimization (MOO) methodologies researched in Phase 1.2 and the domain-specific constraints of reinforced concrete (RC) beam design according to **IS 456:2000**.

The goal is to move from theoretical Pareto fronts (Cost vs. Area) to "Code-Compliant" Pareto sets that respect non-linear structural constraints (Serviceability, Detailing, etc.).

---

## 📑 Key Technical Synthesis

### 1. Parhi et al. (2026): Interpretable Structural Logic
**Paper:** *Design of structural elements for residential buildings utilizing non-linear multi-objective optimization and interpretable data-driven learning.*

*   **Algorithm:** NSGA-II as the optimizer; Lasso/Elastic Net as the interpreter.
*   **Significance:** It addresses the "Black Box" problem of MOO in structural engineering. It uses Interpretable ML to explain *why* certain beam configurations are on the Pareto front (e.g., explaining the dominance of depth over steel percentage in certain load regimes).
*   **IS 456 Context:** Explicitly integrates structural code compliance as the feasibility boundary for the MOEA.

### 2. Hong & Nguyen (2023): The "Hong-Lagrange" ANN Approach
**Paper:** *Pareto frontier for steel-reinforced concrete beam developed based on ANN-based Hong-Lagrange algorithm.*

*   **Algorithm:** Hybrid ANN + Lagrange Multipliers for constraint handling.
*   **Significance:** Focuses on the trade-off between **Cost** and **Structural Performance (Load Capacity)**.
*   **Utility:** Provides a model for "expensive" function evaluation where an ANN acts as a surrogate for the calculation engine, accelerating Pareto exploration by ~100x.

### 3. Santos et al. (2023): The Sustainable Trade-off (Triple Objective)
**Paper:** *Towards sustainable reinforced concrete beams: multi-objective optimization for cost, CO2 emission, and crack prevention.*

*   **Objectives:**
    1.  **Minimize Cost** (Materials + Labor).
    2.  **Minimize CO2 Emissions** (Embodied carbon in concrete/steel).
    3.  **Minimize Crack Width** (Serviceability objective).
*   **Constraint Mapping:** Uses IS 456-like serviceability limits (0.3mm / 0.2mm) as optimization objectives rather than just hard constraints.

---

## 📐 Algorithmic Mapping to IS 456 Library

Based on the 2024-2026 literature, the following mapping is proposed for the `structural_engineering_lib` optimization module:

| Component | Literature Recommendation | Library Implementation |
| :--- | :--- | :--- |
| **Optimizer** | **NSGA-II** or **qEHVI** (Awan et al., 2025) | `BoTorch` implementation of qEHVI for high-dimensional convergence. |
| **Constraint Handling** | **Lexicographic Sorting** (Zhang et al., 2024) | Prioritize Code Compliance (IS 456) > Serviceability > Aesthetics. |
| **Interpretability** | **Lasso/SHAP** (Parhi et al., 2026) | Provide SHAP values for Pareto points to explain "Why this beam?". |
| **Surrogate** | **ANN/SVR** (Hong et al., 2023) | Batch calculation of IS 456 checks for initial Pareto seeding. |

---

## 🚨 Emerging Challenges for Phase 1.4

1.  **Discrete vs. Continuous**: Structural detailing (rebar numbers, diameters) is discrete. Standard MOEAs struggle with the "jumpiness" of the IS 456 rebar tables.
2.  **Interpretable Constraints**: How to translate a "Feasible/Infeasible" bool into a "Distance to Feasibility" metric for the optimizer?
3.  **HCI in Detailing**: Users want "Standard" rebar sizes (12, 16, 20, 25mm), not the theoretical 14.2mm.

---

## 📝 References
(See [PAPER-TRACKER.csv](../PAPER-TRACKER.csv) for full metadata)

- Parhi, S. K., et al. (2026). *Design of structural elements...* SMOP.
- Hong, X., & Nguyen, T. (2023). *Pareto frontier for steel-reinforced concrete beam...* JABBE.
- Santos, T., et al. (2023). *Towards sustainable reinforced concrete beams...* AJCE.
