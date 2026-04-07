---
Type: Research
Audience: All Agents
Status: Active
Importance: Critical
Created: 2026-04-08
Last Updated: 2026-04-08
---

# 2026 State-of-the-Art: What a Cutting-Edge Structural Engineering Python Library Must Be

> **See also:** [2026 Python Toolchain Report](./2026-python-toolchain-report.md) for the definitive tools/versions guide.

**Research Method:** Web research (anaStruct, handcalcs, efficalc, IfcOpenShell, buildingSMART IFC, efficalc.com), codebase analysis of existing capabilities, competitive landscape review, and domain expertise synthesis.

---

## 1. Engineer Persona Analysis

### Entry-Level Engineer (0-4 years)

**Profile:** Recently graduated, comfortable with Python, unfamiliar with design codes, overwhelmed by ETABS/SAFE complexity.

**Needs:**
- **Learning mode**: Show formulas alongside results. "Why is Ast = 1256 mm²?" not just "Ast = 1256 mm²"
- **Code clause references**: Every result should cite its IS 456 clause (e.g., "per Cl 26.5.1.1(b)")
- **Worked examples** that mirror textbook problems (Varghese, Pillai & Menon, Jain)
- **Guardrails**: Warn when inputs are unreasonable (span > 20m for a beam, b < 200mm)
- **Quick start**: `pip install structural-lib-is456` → design a beam in 5 lines of code
- **Visual feedback**: Cross-section diagrams, moment diagrams, rebar layout

**What they'd say:** *"I want to understand what IS 456 Clause 26.5.1.1(b) actually means by running it with different inputs and seeing how the result changes."*

### Senior Engineer (10-20 years)

**Profile:** Expert in IS 456, skeptical of automation, needs to verify every result, handles complex projects with irregular geometry and multiple load combinations.

**Needs:**
- **Transparency**: Full calculation trace with intermediate values, not a black box
- **Verification**: Results must match hand calculations and commercial tools to 4 significant figures
- **Parametric studies**: "What if I change fck from M25 to M30? Show me cost, reinforcement, and utilization changes"
- **Batch processing**: 200+ beams from an ETABS model, designed in one go with a comprehensive report
- **Professional reports**: PDF output matching the quality of TEDDS / Hilti PROFIS reports
- **Multi-code awareness**: "We do projects in the Middle East too — I need ACI 318 eventually"
- **Override capability**: Ability to override automatic selections (bar sizes, spacing) with engineering judgment

**What they'd say:** *"I won't trust it until its numbers match my hand calc sheet for 50 different beam configurations."*

### Firm Owner / Technical Director

**Profile:** Responsible for quality, liability, and profitability. Evaluates tools for the entire team.

**Needs:**
- **Audit trail**: Who designed beam B12? When? With what inputs? Did it change since the last revision?
- **Quality assurance**: Verified against published benchmarks (SP 16 charts, IS 456 examples)
- **Productivity gain**: Must save at least 40% time vs current workflow to justify adoption
- **Risk management**: Professional disclaimer language, version pinning, reproducible results
- **Integration**: Must work alongside ETABS/SAP2000, not replace them — import ETABS CSV → design → export BBS
- **Training cost**: How quickly can a junior engineer become productive? (< 1 week is the target)
- **Licensing**: Open-source is fine for in-house tools. For client deliverables, needs professional indemnity language

**What they'd say:** *"Can I point a reviewer to the source code to verify the formulas? That's more trustworthy than a black-box commercial tool."*

---

## 2. Pain Points with Current Tools

### ETABS / SAP2000 / SAFE (CSI Products)
- **Black box calculations**: Results cannot be traced step-by-step. "Why did it pick 6#20 instead of 4#25?"
- **Expensive licensing**: ₹2-5 lakh/year per seat. Small firms can't afford multi-seat licenses
- **Clunky API**: ETABS OAPI exists but is COM-based, poorly documented, and Windows-only
- **No parametric design**: Want to try 10 concrete grades × 5 section sizes = manual iteration
- **Report generation**: ETABS reports are database dumps, not engineering narratives
- **Black box IS 456 design**: No visibility into which clauses were applied or skipped
- **Lock-in**: Proprietary file formats, no easy way to move to another tool

### STAAD.Pro
- **Legacy architecture**: Feels like software from 2005 with a modern skin
- **Inconsistent IS 456 implementation**: Known discrepancies with hand calculations for certain clause combinations
- **Post-processing nightmare**: Getting usable output requires third-party tools or VB macros
- **Windows-only**: No Linux/Mac support, limiting use in cloud and CI pipelines

### TEDDS (Tekla Tedds)
- **Closed calculation templates**: Cannot inspect or modify the underlying formulas
- **Limited Indian code support**: IS 456 module exists but is basic compared to Eurocode or ACI modules
- **No programmability**: Cannot script batch designs or integrate into pipelines
- **Expensive add-on**: Sold as a module on top of Tekla, not standalone

### Excel Spreadsheets (The Industry Reality)
- **70%+ of structural calculations still happen in Excel** (industry estimate)
- No version control, no audit trail, formulas hidden in cells
- Copy-paste errors are the #1 source of design errors
- Cannot be tested, reviewed as code, or reproduced reliably
- **This is our biggest competitor and our biggest opportunity**

### Emerging Open-Source Tools (Competitive Landscape)

| Tool | Stars | What It Does | Gap vs Our Library |
|------|-------|--------------|-------------------|
| **anaStruct** | 441 | 2D frame analysis (FEM) | Analysis only, no IS 456 design, no reports |
| **handcalcs** | 5,800 | Renders Python calcs as LaTeX | Rendering only, no engineering knowledge |
| **efficalc** | 48 | Calculation templates → reports | Generic framework, no code-specific design |
| **IfcOpenShell** | 2,400 | IFC/BIM manipulation | Geometry/data only, no structural design |
| **OpenSees** | — | Advanced nonlinear FEM | Research tool, not design tool, steep learning curve |
| **PyNite** | ~200 | 3D structural analysis | Analysis only, no code-based design |
| **ClearCalcs** | SaaS | Cloud-based design | Commercial, AUS-focused, not IS 456 |

**Key insight:** No open-source tool combines **code-based design + verification trail + professional reports + IS 456**. This is our unique position.

---

## 3. Proof & Verification Framework

This is the #1 missing capability in structural engineering software and the #1 reason firms are reluctant to adopt new tools.

### 3.1 Calculation Audit Trail

Every design result should carry a complete provenance record:

```python
@dataclass
class CalculationAuditRecord:
    # Identity
    calculation_id: str           # UUID
    timestamp: datetime           # When calculated
    library_version: str          # e.g., "0.21.4"

    # Inputs
    inputs: dict                  # All input parameters with units
    input_source: str             # "manual" | "etabs_csv" | "api"

    # Method
    design_code: str              # "IS 456:2000"
    clauses_applied: list[str]    # ["Cl 38.1", "Cl 26.5.1.1(b)", "Cl 40.4"]
    assumptions: list[str]        # ["Rectangular section", "Singly reinforced"]

    # Results
    outputs: dict                 # All output values with units
    intermediate_values: dict     # Every intermediate calculation step

    # Verification
    status_checks: dict           # {"flexure": "SAFE", "shear": "SAFE", ...}
    utilization_ratios: dict      # {"flexure": 0.87, "shear": 0.65}
    warnings: list[str]           # Any engineering warnings

    # Traceability
    computed_by: str              # User/system identifier
    reviewed_by: str | None       # Reviewer (if applicable)
    revision: int                 # Revision number
```

### 3.2 Verification Against Known Benchmarks

**Benchmark categories:**
1. **SP 16 chart verification**: Every design result must match SP 16 charts to within 1%
2. **Textbook examples**: Reproduce examples from Varghese, Pillai & Menon, Jain — with exact match
3. **ETABS comparison**: For a reference building, match ETABS IS 456 design results within 2%
4. **Hand calculation verification**: For every function, provide a worked example that can be verified by hand
5. **Round-trip tests**: Design → extract inputs → redesign → same result (deterministic)

**Implementation approach:**
- `tests/benchmarks/` directory with categorized verification tests
- Each test cites its source (book, page number, ETABS model file)
- CI runs benchmarks on every commit — any regression fails the build
- Public benchmark report published with each release

### 3.3 Professional Liability Framework

```
DISCLAIMER (Required on every output):
────────────────────────────────────────
This calculation was produced by structural-lib-is456 v{version}.
It implements IS 456:2000 as amended up to {amendment_date}.

This software is a CALCULATION TOOL, not a substitute for engineering judgment.
All outputs must be independently verified by a qualified structural engineer
before use in any structural design.

The authors accept no liability for structural designs based on this software.
All designs must comply with local building codes and be approved by the
relevant authority having jurisdiction.

License: {license}
Verification status: {test_count} benchmark tests passing
────────────────────────────────────────
```

### 3.4 Verification Stamp System

```python
class VerificationLevel(Enum):
    UNVERIFIED = "unverified"          # Raw calculation output
    SELF_CHECKED = "self_checked"      # Automated benchmark match
    PEER_REVIEWED = "peer_reviewed"    # Another engineer has reviewed
    INDEPENDENTLY_VERIFIED = "verified" # Verified against independent calc

@dataclass
class VerificationStamp:
    level: VerificationLevel
    checker: str
    date: datetime
    benchmark_ref: str | None     # "SP16-Table-2, Row 12"
    notes: str
```

---

## 4. Innovative 2026 Features

### 4.1 Transparent Calculations (handcalcs-Inspired)

**The killer feature no competitor has**: Show every step, every formula, every substitution — like writing by hand, but automated.

```python
result = design_beam_is456(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=180)

# result.calculation_trace returns:
"""
Design of RC Beam per IS 456:2000
═══════════════════════════════════

Input Parameters (Cl 38.1):
  b = 300 mm, d = 500 mm
  fck = 25 N/mm², fy = 500 N/mm²
  Mu = 180 kN·m

Step 1: Limiting Moment of Resistance (Cl 38.1, Annex G)
  xu_max/d = 0.46  (for Fe 500, Table G-1.1)
  xu_max = 0.46 × 500 = 230.0 mm
  Mu_lim = 0.36 × fck × b × xu_max × (d - 0.42 × xu_max)
         = 0.36 × 25 × 300 × 230 × (500 - 0.42 × 230)
         = 0.36 × 25 × 300 × 230 × 403.4
         = 250.5 kN·m

  Since Mu (180) < Mu_lim (250.5): SINGLY REINFORCED ✓

Step 2: Depth of Neutral Axis (Cl 38.1)
  Mu = 0.36 × fck × b × xu × (d - 0.42 × xu)
  180 × 10⁶ = 0.36 × 25 × 300 × xu × (500 - 0.42 × xu)
  Solving: xu = 148.2 mm
  xu/d = 148.2/500 = 0.296 < 0.46 ✓ (Under-reinforced)

Step 3: Area of Tension Steel (Cl 38.1)
  Ast = Mu / (0.87 × fy × (d - 0.42 × xu))
      = 180 × 10⁶ / (0.87 × 500 × (500 - 0.42 × 148.2))
      = 180 × 10⁶ / (435 × 437.8)
      = 945.1 mm²
"""
```

This is inspired by `handcalcs` (5.8K stars) but built into the design engine itself — not a rendering layer. Every result is self-documenting.

### 4.2 Generative Design with Pareto Front

Not just "find the cheapest" — generate ALL valid designs and let the engineer CHOOSE:

```python
designs = generate_design_space(
    span_m=6.0, load_kN_per_m=30,
    objectives=["cost", "carbon", "utilization"],
    constraints={"code": "IS456", "max_depth_mm": 600}
)

# Returns 50-200 valid designs on a Pareto front:
# Design 1: 300×500, M25, 4#16 — ₹2,100 | 42 kgCO₂ | utilization 0.89
# Design 2: 250×550, M30, 3#20 — ₹2,350 | 38 kgCO₂ | utilization 0.78
# Design 3: 350×450, M25, 5#16 — ₹2,050 | 45 kgCO₂ | utilization 0.92
# ...
```

**Why this changes everything:** Current tools give ONE answer. This gives engineers the TRADE-OFF SPACE. "I can save 10% carbon for just 5% more cost" is a decision only a human should make.

### 4.3 Sustainability Scoring (First in Industry)

Already in research phase — see [innovation-sustainability-scoring.md](innovation-sustainability-scoring.md).

```python
carbon = score_embodied_carbon(design_result)
# Returns: CarbonScore(
#   concrete_kgCO2=312.5,    # 0.15 m³ × M25 factor
#   steel_kgCO2=188.4,       # 23.55 kg × steel factor
#   total_kgCO2=500.9,
#   rating="B",               # A-F scale
#   benchmark_percentile=62,  # vs typical Indian practice
#   net_zero_gap_pct=34       # distance from 2050 target
# )
```

**No open-source structural design library scores individual element designs for carbon.** ETABS, SAP2000, SAFE — none do this at element level.

### 4.4 Natural Language Design Interface

```python
result = design_from_description(
    "Design a simply supported beam spanning 6 meters, "
    "carrying a superimposed dead load of 10 kN/m and live load of 15 kN/m, "
    "using M25 concrete and Fe500 steel, "
    "with 25mm cover for mild exposure"
)

# Step 1: Parse → confirmed parameters shown to user
# Step 2: Calculate self-weight iteratively
# Step 3: Apply load factors (IS 456 Table 18)
# Step 4: Design → full result with audit trail
```

### 4.5 ETABS Integration Pipeline

**The most requested feature by Indian structural firms:**

```python
from structural_lib import ETABSPipeline

pipeline = ETABSPipeline("path/to/etabs_csvs/")
results = pipeline.design_all_beams()
pipeline.export_bbs("output/bbs.xlsx")    # Bar Bending Schedule
pipeline.export_report("output/calc.pdf")  # Full design calculation book
pipeline.export_dxf("output/rebar.dxf")    # AutoCAD reinforcement layout
```

This turns a 2-week manual process into a 2-hour automated pipeline.

### 4.6 What-If / Parametric Analysis Engine

```python
study = parametric_study(
    base_design={"b_mm": 300, "d_mm": 500, "fck": 25, "Mu_kNm": 180},
    vary={"fck": [20, 25, 30, 35, 40], "d_mm": range(400, 700, 50)},
    metrics=["Ast", "cost", "carbon", "utilization"]
)

study.plot_heatmap(x="fck", y="d_mm", color="cost")
study.plot_sensitivity(metric="Ast")
study.to_excel("parametric_results.xlsx")
```

---

## 5. Report & Output Requirements

### 5.1 Required Report Types

| Report Type | Format | Audience | Content |
|-------------|--------|----------|---------|
| Design Calculation | PDF, HTML | Reviewer/authority | Full step-by-step calc with clause refs |
| Design Summary | PDF, Excel | Client/architect | Key results: section, reinforcement, checks |
| Bar Bending Schedule | Excel, PDF | Contractor/site | Rebar cutting lengths, bending shapes, weight |
| Beam Schedule | Excel | Drafter | b, D, reinforcement at each section |
| DXF Drawing | DXF/DWG | Drafter/CAD | Cross-section with rebar positions |
| Comparison Report | HTML, PDF | Design team | Side-by-side alternatives with trade-offs |
| Parametric Study | HTML, Excel | Engineer | Sensitivity analysis results |
| Carbon Report | PDF | Green building cert | Embodied carbon per element |

### 5.2 Report Quality Standards

**A professional calculation report must include:**
1. **Cover page**: Project name, engineer, date, revision, company logo placeholder
2. **Table of contents**: Auto-generated from design elements
3. **Input summary**: All inputs in a parameter table with units
4. **Design methodology**: Which code, which clauses, which assumptions
5. **Step-by-step calculations**: Formula → substitution → result (handcalcs-style)
6. **Code check summary**: Pass/fail table for all applicable checks
7. **Cross-section diagram**: With dimensions and rebar positions
8. **Bar Bending Schedule**: If detailing is requested
9. **Disclaimer**: Professional liability statement
10. **Revision history**: Change log for the document

### 5.3 Output Format Requirements

- **PDF**: Professional, printable, signable. Use `reportlab` or `weasyprint`
- **HTML**: Interactive, linkable, embeddable in web apps. Already supported via React frontend
- **Excel/CSV**: For data exchange, further processing, and client familiarity
- **DXF**: For import into AutoCAD (already partially implemented via `export_dxf`)
- **IFC**: For BIM integration — structural elements with properties (future, via IfcOpenShell)
- **JSON**: Machine-readable results for API consumers (already the primary format)

---

## 6. Multi-Code UX Design

### 6.1 How Users Should Interact with Multi-Code

**Recommended approach: Configuration-based with sensible defaults**

```python
# Option A: Module-level selection (recommended for single-code projects)
from structural_lib.codes.is456 import design_beam
result = design_beam(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=180)

# Option B: Explicit code parameter (for comparison workflows)
from structural_lib import design_beam
result_is456 = design_beam(code="IS456", b=300, d=500, fck=25, fy=500, Mu=180)
result_aci = design_beam(code="ACI318", b=300, d=500, fc=25, fy=500, Mu=180)

# Option C: Config file for project-wide settings
# structural_lib.toml
# [design]
# code = "IS456"
# units = "SI"
# safety_factors = "code_default"  # NEVER allow overriding safety factors
```

### 6.2 Design Principles for Multi-Code

1. **Each code is a complete, independent module** — never mix safety factor systems
2. **Parameter names follow each code's conventions** — IS 456 uses `fck`, ACI uses `f'c`, EC2 uses `fck`
3. **Units follow each code's conventions** — IS 456 uses mm/N, ACI often uses inches/lb
4. **Safety factors are HARDCODED per code** — never exposed as parameters
5. **Comparison mode** shows results side by side with different formatting per code
6. **import path makes the code explicit** — `from structural_lib.codes.is456 import ...`

### 6.3 How Commercial Tools Handle This

| Tool | Multi-code Approach |
|------|-------------------|
| ETABS | Dropdown menu: "Design Code → IS 456:2000" — applies to entire model |
| STAAD.Pro | Parameter in input file: `DEFINE IS456 DESIGN` |
| TEDDS | Separate calculation templates per code |
| IDEA StatiCa | Code selection at project level, never per-element |
| ClearCalcs | Separate products per code region |

**Our approach combines the best**: Module-level separation (like TEDDS) with comparison capability (unique to us).

---

## 7. Firm Adoption Strategy

### 7.1 What Makes a Firm Adopt a Python Library

Based on industry patterns, the adoption funnel is:

```
AWARENESS:  "There's an open-source IS 456 design library"
  ↓
TRIAL:      pip install → design one beam → compare with hand calc
  ↓
VALIDATION: Design 10 beams from a real project → match ETABS results
  ↓
PILOT:      One engineer uses it for a small project (non-critical)
  ↓
ADOPTION:   Team-wide use for specific workflows (batch design, BBS)
  ↓
DEPENDENCE: Embedded in firm's automation pipeline
```

### 7.2 Critical Success Factors

| Factor | Threshold | Current State |
|--------|-----------|---------------|
| **Accuracy** | < 1% deviation from SP 16 / hand calc | ✅ Tested |
| **Documentation** | Complete API docs + worked examples | 🔄 Partial |
| **Benchmarks** | Published verification against ETABS | 🔲 Not yet |
| **Installation** | `pip install` works first time | ✅ Working |
| **First result** | < 5 minutes from install to first design | ✅ Quick |
| **Report quality** | PDF matching TEDDS quality | 🔄 Basic |
| **ETABS integration** | Import CSV → design → export | ✅ Working |
| **Support** | GitHub Issues with < 48h response | 🔄 Informal |
| **Stability** | Semantic versioning, no breaking changes | ✅ v0.21.x |
| **Indian code focus** | IS 456 as first-class, not afterthought | ✅ Core focus |

### 7.3 Killer Use Cases for Firm Adoption

1. **ETABS post-processing**: Import beam forces → design all beams → generate BBS + reports. Saves 60-80% time.
2. **Parametric optimization**: "What's the cheapest section for 200 beams?" — impossible in ETABS, trivial here.
3. **Quality audit**: "Show me every beam where utilization > 0.95" — instant query on design database.
4. **Carbon reporting**: Required for GRIHA/LEED projects, no tool does this today.
5. **Training tool**: Juniors learn IS 456 by seeing every calculation step — better than any textbook.

---

## 8. Professional Standards

### 8.1 Disclaimers Required

Every output from the library must include:

1. **Software disclaimer**: "This is a calculation aid, not a substitute for engineering judgment"
2. **Code version**: "Implements IS 456:2000 as amended up to [date]"
3. **Verification status**: "This version has passed N benchmark tests"
4. **Limitation statement**: "This software handles [list] and does NOT handle [list]"
5. **License notice**: Open-source license terms

### 8.2 What the Library Must NOT Do

- **Never auto-approve a design** — always present results for engineer review
- **Never hide failing checks** — if a check fails, it must be prominently displayed
- **Never silently change inputs** — if the library adjusts inputs (e.g., minimum steel), it must say so
- **Never claim to replace an engineer** — it's a tool, not a designer
- **Never produce results outside its validated domain** — if inputs are outside tested ranges, refuse or warn

### 8.3 Verification Stamp vs PE Stamp

- **Our verification stamp** = "This calculation was produced by verified, tested software"
- **PE stamp** = "A licensed professional engineer has reviewed and approved this design"
- These are DIFFERENT and must never be conflated
- The library can facilitate the PE review process (by making calculations transparent) but cannot replace it

---

## 9. Top 10 Features That Would Make This the BEST Structural Engineering Library in the World

| Rank | Feature | Why It Wins | Difficulty | Current State |
|------|---------|-------------|------------|---------------|
| **1** | **Transparent Calculation Traces** | No competitor shows every step. handcalcs does rendering, but not design. We do both. Engineers can verify by reading the output. | M | 🔄 Partial (reports/) |
| **2** | **ETABS → Design → BBS Pipeline** | The #1 workflow for Indian structural firms. No open-source tool does this end-to-end. | M | ✅ Working |
| **3** | **Published Benchmark Verification** | A public matrix showing our results vs SP 16 / ETABS / hand calcs. Trust through transparency. | M | 🔲 Not yet |
| **4** | **Embodied Carbon Scoring** | First structural design library to score individual elements for CO₂. Industry-changing. | S | 🔄 Research |
| **5** | **Generative Multi-Objective Design** | Generate 50+ valid designs, Pareto-optimize cost × carbon × utilization. Engineers CHOOSE, not accept. | L | 🔲 Research |
| **6** | **Professional PDF Reports** | Calculation book quality matching TEDDS. Cover page, TOC, diagrams, BBS, disclaimer. | M | 🔄 Basic |
| **7** | **Parametric What-If Engine** | Vary any input, see impact on all outputs. Heatmaps, sensitivity plots, response surfaces. | M | 🔄 Partial (sensitivity.py) |
| **8** | **Natural Language Interface** | "Design a 6m beam for 30 kN/m" → parse → confirm → design → report. Democratizes access. | L | 🔄 Partial (smart_designer.py) |
| **9** | **Multi-Code Comparison** | Same beam designed per IS 456 vs ACI 318 vs EC2 — side by side. No tool does this for Indian code. | XL | 🔲 Not yet |
| **10** | **IFC/BIM Export** | Export designed elements as IFC entities with structural properties. Bridges design → BIM gap. | L | 🔲 Not yet |

### Why This Combination Wins

- **handcalcs** (5.8K stars) does rendering but has zero engineering knowledge
- **anaStruct** (441 stars) does analysis but has zero design capability
- **efficalc** (48 stars) does reports but has zero code-specific design
- **ETABS/SAFE** do design but are black boxes, expensive, and Windows-only
- **Excel spreadsheets** are the real incumbent — and they have zero transparency, zero testing, zero version control

**Our library is the only tool in the world that combines:**
1. IS 456 design knowledge (code-based, not generic)
2. Transparent calculation traces (handcalcs-quality, built-in)
3. Professional report generation (TEDDS-quality output)
4. Open-source verifiability (any engineer can read the source)
5. Python programmability (batch, parametric, integrated)
6. Carbon scoring (industry first)
7. Active AI agent development (16 agents, continuous improvement)

---

## 10. Action Items by Priority

### Immediate (This Quarter)

1. **Published benchmark matrix** — SP 16 tables, textbook examples, ETABS comparison
2. **Calculation trace in every result** — clause references, intermediate values, formula + substitution
3. **Professional PDF report template** — cover page, TOC, cross-section diagrams
4. **Embodied carbon scoring** — prototype to production (research already done)

### Next Quarter

5. **Parametric study engine** — extend sensitivity.py to full factorial with visualization
6. **Generative design prototype** — multi-objective optimization with Pareto front
7. **Multi-code architecture** — abstract `DesignCode` interface, ACI 318 as second code
8. **Natural language parser** — extend smart_designer.py with confirmation workflow

### Future

9. **IFC export** — via IfcOpenShell integration
10. **Load combination intelligence** — IS 456 Table 18 + IS 875 + IS 1893 auto-combinations

---

## Appendix A: Competitive Positioning Matrix

| Capability | Our Library | ETABS | Excel | handcalcs | efficalc | anaStruct |
|-----------|:-----------:|:-----:|:-----:|:---------:|:--------:|:---------:|
| IS 456 design | ✅ | ✅ | 🔄 | ❌ | ❌ | ❌ |
| Transparent calcs | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Professional reports | 🔄 | 🔄 | ❌ | 🔄 | ✅ | ❌ |
| Open source | ✅ | ❌ | N/A | ✅ | ✅ | ✅ |
| Programmable/API | ✅ | 🔄 | 🔄 | ✅ | ✅ | ✅ |
| Carbon scoring | 🔄 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Batch design | ✅ | 🔄 | ❌ | ❌ | ❌ | ❌ |
| Parametric study | 🔄 | ❌ | 🔄 | ❌ | ❌ | ❌ |
| BIM integration | 🔲 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-code | 🔲 | ✅ | 🔄 | N/A | N/A | N/A |
| Cost | Free | ₹2-5L/yr | Free | Free | Free/SaaS | Free |
| Verification | ✅ | ❌ | ❌ | N/A | 🔄 | ❌ |

Legend: ✅ Full | 🔄 Partial | 🔲 Planned | ❌ None

## Appendix B: Research Sources

- anaStruct: https://github.com/anastruct/anaStruct (441 stars, GPL-3.0, 2D frame analysis)
- handcalcs: https://github.com/connorferster/handcalcs (5.8K stars, Apache-2.0, LaTeX rendering)
- efficalc: https://github.com/youandvern/efficalc (48 stars, MIT, calculation reports)
- IfcOpenShell: https://github.com/IfcOpenShell/IfcOpenShell (2.4K stars, LGPL-3.0, BIM/IFC)
- buildingSMART IFC: https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/
- efficalc.com: https://efficalc.com/ (SaaS platform for engineering calculations)
- Wikipedia Structural Engineering: https://en.wikipedia.org/wiki/Structural_engineering
- Existing codebase research: docs/research/claw-code-harness-ideas.md, innovation-sustainability-scoring.md