# Brainstorming: Structural Automation Platform

**Type:** Architecture
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0

---

## The Core Problem We're Solving

Every structural engineering firm has the **same problem**:
- Engineers spend 60-70% of time on repetitive tasks (ETABS post-processing, report generation, compliance checks)
- Each firm builds their own Excel macros/scripts from scratch
- When the "Excel wizard" leaves, the automation dies with them
- Unlike software engineering, there's no "npm" or "pip" for structural engineering workflows

**We're building the missing infrastructure layer.**

---

## The Big Question: How Will Engineers Actually Use This?

This section explores **6 realistic delivery models** for the platform.

---

## Model A: Web Platform (Streamlit Cloud / Hosted)

### How it works
- Engineers visit `structuralsdk.com` (or similar)
- They use pre-built tools OR build their own using a visual editor
- All computation happens in the cloud
- Think: "Notion + Airtable" but for structural calculations

### User Experience
```
1. Login → Dashboard shows "My Tools" and "Template Gallery"
2. Click "IS 456 Beam Design" → Sliders for geometry + loads
3. Instant 3D rebar visualization + compliance panel
4. Export: PDF report, DXF, CSV summary
5. Save as "My Template" for reuse
```

### Pros
- Zero installation (works on any device)
- Always latest version
- Easy collaboration (share links)
- Centralized audit trail

### Cons
- Requires internet
- Data privacy concerns (some firms won't upload project data)
- Monthly subscription model may face resistance
- Can't integrate deeply with local ETABS/Excel

### Best For
- Small firms (1-10 engineers)
- Students and educators
- Quick one-off calculations
- Firms comfortable with cloud

### Revenue Model
- Freemium: Basic tools free, advanced exports/batch processing paid
- Team plans: Shared templates + audit logs

---

## Model B: Excel Add-in (PyXLL / xlwings Powered)

### How it works
- Install a `.xll` add-in (like solver or analysis toolpak)
- New ribbon tab: "Structural SDK"
- Excel functions like `=SK_BEAM_DESIGN(b, D, Mu, fck, fy)`
- Click a button → Python runs in background → Results in cells

### User Experience
```
1. Install add-in (one-time, IT-approved)
2. Open Excel → New "Structural SDK" ribbon appears
3. Fill standard input table (columns: b_mm, D_mm, Mu_kNm, etc.)
4. Click "Run Design" → Status column populates (Pass/Fail/Warnings)
5. Click "Generate Report" → PDF opens
6. Click "View 3D" → Browser opens with interactive rebar cage
```

### Technical Implementation
```python
# Using PyXLL (commercial) or xlwings (open-source)
@xl_func("float b, float D, float Mu, float fck, float fy: str")
def SK_BEAM_DESIGN(b, D, Mu, fck, fy):
    """Run IS456 beam design from Excel"""
    from structural_lib import api
    result = api.design_beam_is456(b_mm=b, D_mm=D, ...)
    return "PASS" if result.passed else f"FAIL: {result.governing_check}"
```

### Pros
- **Engineers stay in Excel** (comfort zone)
- Works offline
- Integrates with existing firm spreadsheets
- Easy IT approval (local software)
- Python power hidden behind familiar interface

### Cons
- Windows-only (PyXLL limitation)
- Installation/update friction
- Can't easily share "templates" across firms
- Excel version compatibility issues
- Requires Python runtime installed

### Best For
- Large firms with existing Excel workflows
- Engineers who refuse to leave Excel
- Firms with strict data policies (no cloud)

### Revenue Model
- Per-seat license (like PyXLL model)
- Enterprise site license

---

## Model C: Drag-and-Drop Automation Builder (No-Code)

### How it works
- Visual workflow builder (like n8n, Zapier, or node-red)
- Nodes: Input, Design, Detailing, Visualization, Export
- Connect nodes to create automation pipelines
- Non-programmers can build complex workflows

### User Experience
```
1. Open "Workflow Builder"
2. Drag "CSV Input" node → Configure columns mapping
3. Connect to "Batch IS456 Design" node
4. Connect to "Filter Failures" node
5. Branch: Failures → "Alert Email", Passes → "3D Viewer"
6. Connect passes to "PDF Report Generator"
7. Click "Run" → Entire pipeline executes
8. Save as "My ETABS Post-Processing Workflow"
```

### Visual Representation
```
┌──────────┐    ┌─────────────┐    ┌──────────────┐
│ CSV      │───→│ IS456       │───→│ 3D Viewer    │
│ Input    │    │ Batch Design│    │ (Pass)       │
└──────────┘    └─────────────┘    └──────────────┘
                      │
                      ↓
              ┌──────────────┐    ┌──────────────┐
              │ Filter       │───→│ Email Alert  │
              │ Failures     │    │ (Fail)       │
              └──────────────┘    └──────────────┘
```

### Pros
- **No coding required**
- Visual representation of workflow logic
- Easy to modify and experiment
- Shareable workflow templates
- Self-documenting (the diagram IS the documentation)

### Cons
- Learning curve for visual paradigm
- Complex logic can become "spaghetti nodes"
- Performance overhead vs pure code
- Limited flexibility for edge cases
- Requires robust node library

### Best For
- "Automation champions" in firms
- Teams without Python skills
- Standardizing firm-wide workflows
- Training and onboarding

### Revenue Model
- Free basic nodes, premium advanced nodes
- "Pro" features: scheduling, versioning, collaboration

---

## Model D: Python SDK (Pro-Code for Power Users)

### How it works
- `pip install structural-sdk`
- Full Python API for scripting
- Jupyter notebook integration
- CLI tools for batch processing

### User Experience
```python
# my_beam_tool.py
import structural_sdk as sk

# Load from ETABS export
beams = sk.io.read_etabs_csv("element_forces.csv")

# Batch design
results = sk.engine.batch_design(beams, code="IS456")

# Filter and report
failures = [r for r in results if not r.passed]
print(f"Failures: {len(failures)}/{len(results)}")

# Generate outputs
sk.io.export_summary_csv(results, "design_summary.csv")
sk.viz.batch_report(results, "batch_report.html")
```

### Pros
- **Maximum flexibility and power**
- Integrates with any Python ecosystem
- Version control with git
- Unit testing for workflows
- Best performance

### Cons
- Requires Python knowledge
- More setup and maintenance
- No visual feedback during development
- Harder for non-coders to modify

### Best For
- Engineering firms with developers
- R&D and advanced optimization
- Integration with other tools (ML, FEA)
- Building custom applications

### Revenue Model
- Open-source core, commercial extensions
- Enterprise support contracts
- Training and consulting

---

## Model E: Chat-First Interface (LLM-Powered)

### How it works
- Natural language interface powered by Claude/GPT
- "Design a 6m beam with M25 concrete"
- LLM interprets intent → calls verified tools → shows results
- Combines explanation with computation

### User Experience
```
User: "I have a beam with 5m span, load of 25 kN/m.
       Check if 230x450 works with M25 and Fe500."

AI:   Running IS456 beam design...

      Result: FAIL (Flexure)
      - Required Ast: 1256 mm²
      - Provided Ast (min): 345 mm²
      - Governing: Clause 26.5.1.1

      Suggestion: Increase depth to 550mm or use
      doubly reinforced section.

      [Show 3D] [Try 550mm depth] [Export Report]

User: "Try 550mm depth"

AI:   Running with D=550mm...

      Result: PASS ✓
      - Ast required: 785 mm²
      - Recommended: 3-20φ (942 mm²)
      - Utilization: 83%

      [View Rebar Layout] [Export DXF] [Compare]
```

### Pros
- **Lowest learning curve** (just talk)
- Explains "why" naturally
- Handles ambiguity through dialogue
- Accessible to students and beginners
- Can guide through complex workflows

### Cons
- Slower than direct input
- LLM can misunderstand intent
- Requires careful guardrails (no hallucinated numbers)
- Dependent on API availability
- May feel "gimmicky" to experienced engineers

### Best For
- Learning and education
- Quick exploration and "what-if"
- Engineers new to the platform
- Explaining results to non-engineers

### Revenue Model
- Free basic queries, token-based pricing for heavy use
- Enterprise: self-hosted LLM option

---

## Model F: Hybrid Desktop App (Electron/Tauri)

### How it works
- Installable desktop application
- Combines web UI with local Python runtime
- Works offline, syncs when online
- Think: "VSCode for structural engineering"

### User Experience
```
1. Download and install "Structural Studio"
2. Offline: Full design capabilities, local file storage
3. Online: Sync projects, access templates, updates
4. Integrated: Python console, 3D viewer, report generator
```

### Pros
- Best of both worlds (offline + cloud)
- Native performance
- Can integrate with local ETABS/AutoCAD
- Firm-controlled data storage

### Cons
- Development complexity (multiple platforms)
- Installation and updates friction
- Larger resource footprint

### Best For
- Medium-large firms
- Projects with strict data requirements
- Heavy daily users

---

## Recommendation: Start with a Hybrid Approach

Based on where structural engineering is today, I recommend **layered adoption**:

### Phase 1: SDK + Streamlit (Now → 6 months)
- Core Python SDK (`pip install structural-sdk`)
- Streamlit web apps as "reference implementations"
- Targets: Python-literate engineers and automation champions

### Phase 2: Excel Integration (6 → 12 months)
- xlwings-based add-in for Windows
- Custom functions + ribbon interface
- Targets: Engineers who live in Excel

### Phase 3: Chat + Builder (12+ months)
- LLM chat interface for exploration/learning
- Visual workflow builder for no-code users
- Targets: Broader adoption, students, small firms

---

## Competitive Landscape Analysis

| Platform | Strengths | Weaknesses | Our Opportunity |
|----------|-----------|------------|-----------------|
| **VIKTOR** | Mature, enterprise-ready, Python-based | Generic (no deep IS456), expensive, cloud-only | Domain-specific intelligence, lower cost |
| **Speckle** | Great data hub, versioning, connectors | Data plumbing only (no calculation engine) | Verified calculation kernels |
| **Excel+VBA** | Familiar, flexible, offline | Fragile, no visualization, no sharing | Bulletproof calcs + 3D + collaboration |
| **ETABS/SAP** | Industry standard, powerful | Black box, slow iteration, export hell | Glass-box transparency + instant feedback |
| **n8n/Zapier** | Great workflow automation | Zero domain knowledge | Structural-aware nodes + validation |

**Our Unique Value Proposition:**
> "The first automation platform built BY structural engineers FOR structural engineers, with verified IS456 calculations, instant 3D visualization, and workflows that actually understand your domain."

---

## What Engineers Actually Need (Jobs to be Done)

### Daily Pain Points (from research)
1. **"I just changed one parameter, now I have to redo everything"**
   - Solution: Live calculation loop (<100ms)

2. **"ETABS says O/S but I don't know why"**
   - Solution: Glass-box verification with clause references

3. **"The Excel file works on my machine but not his"**
   - Solution: Versioned, reproducible workflows

4. **"I need to check 100 beams and it takes all day"**
   - Solution: Batch processing with visual failure map

5. **"I can't visualize the congestion until detailing drawings"**
   - Solution: Instant 3D rebar cage preview

6. **"My junior engineer can't follow my calculations"**
   - Solution: Step-by-step explanation mode

---

## SDK Primitive Design (The "Lego Blocks")

### Input Layer (`sk.ui`)
```python
sk.ui.beam_geometry()      # Returns validated BeamInput
sk.ui.material_selector()  # Returns Material (fck, fy, E)
sk.ui.load_table()         # Multi-load case manager
sk.ui.etabs_import()       # ETABS CSV → normalized schema
sk.ui.csv_input()          # Generic CSV with schema mapping
```

### Engine Layer (`sk.engine`)
```python
sk.engine.design(input, code="IS456")     # Full design
sk.engine.verify(input, code="IS456")     # Check only (no sizing)
sk.engine.detail(result)                   # Rebar layout
sk.engine.optimize(input, objective="cost") # Auto-sizing
sk.engine.batch_design(inputs, code="IS456") # Multiple elements
sk.engine.sensitivity(input, params)       # Parameter sweep
```

### Visualization Layer (`sk.viz`)
```python
sk.viz.beam_3d(result)           # Interactive 3D rebar cage
sk.viz.compliance_panel(result)  # Traffic light status
sk.viz.comparison(results)       # Side-by-side comparison
sk.viz.heatmap(results, metric)  # Building-level view
sk.viz.diff(v1, v2)              # Structural diff visualization
```

### Output Layer (`sk.io`)
```python
sk.io.report_pdf(result)     # Calculation report
sk.io.report_html(result)    # Web-viewable report
sk.io.export_dxf(result)     # CAD-ready drawings
sk.io.export_bbs(result)     # Bar bending schedule
sk.io.export_csv(results)    # Summary table
sk.io.audit_log(run_id)      # Full traceability
```

---

## Immediate Next Steps

1. **Finalize SDK API signatures** (sk.ui, sk.engine, sk.viz, sk.io)
2. **Build 3 reference apps** using the SDK (beam design, batch processing, compliance check)
3. **Create "Hello World" tutorial** (design a beam in 10 lines)
4. **Prototype Excel integration** (xlwings proof-of-concept)
5. **Define StructJSON v0.1** (canonical data contract)

---

## Open Questions for Discussion

1. **Pricing**: Free forever with paid support? Freemium? Open source?
2. **Multi-code support**: Focus on IS456 first or parallel development?
3. **Community**: Open template sharing or firm-private only?
4. **AI integration**: Central to UX or optional enhancement?
5. **Hosting**: Cloud-only, self-hosted option, or both?

---

## Original Vision (Preserved)

### "The OS for Structural Engineering"

**Goal:** Pivot from building *tools* (apps) to building the *platform* that enables engineers to create their own tools.

**Analogy:** We are building Unity/Roblox for Structure, not just one Game.

### Layer 1: The "Lego Blocks" (Core Primitives)
We provide high-level, verified Python blocks that handle the hard stuff.

#### A. Smart Input Widgets (`st_structural.ui`)
*   `ui.section_input()`: Auto-validates b/D ratios, standard sizes.
*   `ui.material_selector()`: Returns verified `Material` objects (fck, fy, E).
*   `ui.load_case_manager()`: Handles DL/LL/WL combinations automatically.

#### B. Logic Engines (`st_structural.engine`)
*   `engine.verify(element, code="IS456")`: Returns pass/fail + Clause references.
*   `engine.optimize(element, constraint="cost")`: Auto-sizes for lowest cost.
*   `engine.detail(element)`: Generates valid rebar layouts (SP34 rules).

#### C. Professional Outputs (`st_structural.viz`)
*   `viz.render_3d(element)`: Instant interactive WebGL view (PyVista).
*   `viz.report(result)`: Generates calculation pad PDF/HTML.
*   `viz.audit_trail(run_id)`: Cryptographic proof of inputs/outputs.

### Layer 2: The Builder Experience
Two ways to build:

#### 1. The "Scripting Engineer" (Pro-Code)
```python
import struct_platform as sp

# 10-Line Beam Tool
def main():
    geom = sp.ui.beam_geometry("Input")
    loads = sp.ui.etabs_import("Select Beam")

    # The Magic Line
    result = sp.engine.design_and_detail(geom, loads, code="IS456")

    if result.passed:
        sp.viz.render_3d(result.geometry)
        sp.io.export_dxf(result)
```

#### 2. The "Visual Architect" (No-Code)
*   Drag `Input` node → Connect to `IS456 Design` node → Connect to `3D Viewer` node → Hit "Publish".

### Layer 3: The Ecosystem (Exchange)
*   **Company Registry:** "My Firm's Standard Tools" (Private).
*   **Global Marketplace:** Experts share niche tools ("Nuclear Wall Design").
*   **Standard Data Format:** All tools speak `StructJSON`.

### Differentiation Summary
| Feature | Excel | Streamlit (Generic) | **Our Platform** |
| :--- | :--- | :--- | :--- |
| **Logic** | Manual Formulas | DIY Python | **Verified Kernels** |
| **Viz** | Charts | Basic Plots | **Engineering 3D** |
| **State** | Files | Session State | **Versioned Data** |
| **Speed** | Fast Calc, Slow Dev | Slow Dev | **Instant Dev** |

---

## References

- [VIKTOR - Streamlining Structural Engineering](https://www.viktor.ai/blog/112/streamlining-structural-engineering-viktor-for-building-and-construction)
- [Speckle - The AEC Data Hub](https://speckle.systems/)
- [PyXLL - Python Excel Add-in](https://www.pyxll.com)
- [xlwings - Python for Excel](https://www.xlwings.org/)
- [n8n - AI Workflow Automation](https://n8n.io/)
- [n8n vs Zapier Comparison](https://n8n.io/vs/zapier/)
