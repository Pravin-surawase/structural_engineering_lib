# Phase 1.4: Human-AI Interaction & Decision Support
> **Focus**: Transforming optimization data into engineering decisions through calibrated trust and visual analytics.

## 1. Executive Summary
While Phase 1.1-1.3 established the *computational* capability to generate optimal structural designs, Phase 1.4 addresses the *cognitive* challenge: how engineers verify, trust, and select from these solutions. Review of 2024-2025 literature reveals a shift from "black-box automation" to "AI-assisted decision support," where the goal is not just finding the pareto front, but helping the engineer understand the trade-offs it represents.

## 2. The Psychology of Engineering Trust

### 2.1 Calibrated Trust (Jelinek et al., 2025)
Trust in engineering tools must be "calibrated"—users should trust the system exactly as much as it deserves, no more, no less. Over-trust leads to catastrophic failures (accepting unsafe designs), while under-trust leads to abandonment of useful tools.

**Key Guidelines for Our Tool:**
1.  **Expose Uncertainty**: Never present a single "optimal" beam design as absolute fact. Show confidence intervals or sensitivity (e.g., "This design is optimal, but sensitive to concrete grade variations").
2.  **Common Ground**: Use terminology familiar to IS 456 engineers (e.g., "Pt %" instead of "Reinforcement Ratio", "Mu" instead of "Bending Moment").
3.  **Situational Context**: The UI must adapt. A design checker needs different info than a conceptual designer.

### 2.2 Human Learning vs. Accuracy (Noti et al., 2025)
Standard AI maximizes immediate accuracy, often by taking over the decision. However, in engineering, maintaining the human's expertise is critical. Noti et al. demonstrate that AI systems that explain *why* a decision is made (even if it takes longer) lead to better long-term performance because the human operator learns to spot edge cases the AI might miss.

**Implication**: Our "Cost vs. Safety" plots should allow engineers to click a point and see the *calculation trace*, reinforcing their own understanding of the code.

## 3. Visual Analytics for High-Dimensional Trade-offs

### 3.1 ParetoLens Framework (Ma et al., 2025)
Visualizing 3+ objectives (Cost, CO2, Deflection, Safety) is cognitively overwhelming. Ma et al. introduce **ParetoLens**, a framework for exploring these solution sets.

**Core Mechanics:**
*   **Dual-View Interface**:
    *   *Objective Space*: Parallel coordinates or scatter matrices showing performance metrics.
    *   *Decision Space*: Physical representation (beam cross-section) linked to the selected point.
*   **Ranking & Filtering**: Allow engineers to set "hard constraints" (e.g., "Deflection < 20mm") dynamically to cull the pareto front.

### 3.2 Orbit Framework (Yang et al., 2024)
Yang et al. emphasize "Boundary Objects"—visual artifacts that facilitate communication between stakeholders (e.g., Engineer vs. Client).

**Application**: The tool should generate "Decision Cards"—summary views of top 3 distinct options (e.g., "The Cheapest", "The Thinnest", "The Most Sustainable") to facilitate team discussions, rather than just showing a raw scatter plot.

## 4. Implementation Strategy: The "Engineer-in-the-Loop" UI

Based on this research, the UI for our Structural Library will follow a **"Verify-then-Trust"** pattern:

### Step 1: Input & Context (Establishing Common Ground)
*   Inputs mirror standard IS 456 workflow (Span, Load, Grade).
*   No "magic numbers"—all defaults are visible and explainable.

### Step 2: The Pareto Dashboard (Visual Analytics)
*   **Primary View**: Cost vs. Depth scatter plot (familiar trade-off).
*   **Secondary View**: Carbon footprint heatmap overlay.
*   **Interactivity**: Hovering over a point shows the *physical* beam section (ParetoLens principle).

### Step 3: Deep Dive (Calibrated Trust)
*   Clicking a design opens the "compliance pane".
*   Shows *exactly* which IS 456 clauses governed the design (e.g., "Controlled by Cl. 26.5.1.1 Min Spacing").
*   Highlights active constraints (e.g., "Warning: Utilization ratio 0.98 - near limit").

## 5. Key References

*   **P2-003**: Jelinek, G. et al. (2025). *Six Guidelines for Trustworthy Automation Design*. arXiv.
*   **P2-006**: Ma, Y. et al. (2025). *ParetoLens: A Visual Analytics Framework for Exploring Solution Sets of MOEA*. arXiv.
*   **P2-005**: Noti, G. et al. (2025). *AI-Assisted Decision Making with Human Learning*. arXiv.
*   **P2-002**: Noorani, E. et al. (2025). *Human-AI Collaborative Uncertainty Quantification*. arXiv.
