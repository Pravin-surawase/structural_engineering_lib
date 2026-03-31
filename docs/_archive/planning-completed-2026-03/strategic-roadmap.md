---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# Strategic Roadmap - VBA/Excel Focus
**Project:** Structural Engineering Library
**Focus Area:** Excel/VBA Platform (User Enablement & Innovation)
**Planning Agent:** Main Coordinator
**Last Updated:** 2026-01-01

---

## Executive Summary

**Current State:**
- ✅ VBA implementation: 95%+ feature parity with Python (~5,755 lines, 20 modules)
- ✅ Documentation foundation: API reference, FAQ, UDT guide, DXF standards complete
- ⚠️ User enablement gap: Discoverability solved, but templates/tutorials incomplete
- 🎯 **Strategic Insight:** Excel/VBA is a "big plus" due to existing user base in structural engineering

**Strategic Direction:**
Focus on **Excel/VBA as primary platform** for next 2-3 months. Rationale:
1. Users already use Excel daily (zero learning curve for UI)
2. VBA is feature-complete (no major dev work needed)
3. Documentation now solid (can focus on UX/enablement)
4. **Differentiation opportunity:** Most RC design tools are desktop apps or web calculators, NOT Excel add-ins

**Goal Hierarchy:**
1. **Phase 1 (Weeks 1-2):** User Enablement - Make existing features easy to discover and use
2. **Phase 2 (Weeks 3-6):** UX Innovation - Add wizards, templates, automation beyond basic UDFs
3. **Phase 3 (Months 2-3):** Ecosystem - Distribution, community, integration with ETABS/STAAD
4. **Phase 4 (Months 3+):** Advanced - Cloud, mobile companion, web calculator

---

## Phase 1: User Enablement (Weeks 1-2)

**Goal:** Reduce time-to-first-design from 30 minutes → 5 minutes for new users

### Metrics
- [ ] Template gallery: 3 ready-to-use workbooks
- [ ] Screenshot tutorial: 10 images captured and integrated
- [ ] Video tutorial: 1 screencast (5-10 minutes)
- [ ] Sample data: 5 realistic beam design examples

### Tasks (Priority Order)

#### Task 1.1: Create Template Gallery
**Deliverable:** 3 pre-configured Excel workbooks in `Excel/Templates/`

**Workbook 1: BeamDesignSchedule.xlsm**
- **Purpose:** Multi-beam batch design (10-50 beams)
- **Features:**
  - Pre-built table with headers (BeamID, b, D, fck, fy, Mu, Vu)
  - Formulas for: Ast, bars, stirrups, Ld, status
  - Conditional formatting (green=safe, red=check)
  - Print-ready format (A4 landscape)
  - Macro button: "Export All to DXF"
- **Sample data:** 10 beams from typical residential building
- **Agent task:** Create workbook, test formulas, verify output

**Workbook 2: QuickDesignSheet.xlsm**
- **Purpose:** Single beam quick design with visual feedback
- **Features:**
  - Input section (geometry, materials, loads)
  - Auto-calculated results (Ast, stirrups, checks)
  - Visual indicators (utilization bars, check icons)
  - Notes section (assumptions, warnings)
  - Macro button: "Export to DXF"
- **Sample data:** B1 from validation pack (300×500, Mu=150kNm)
- **Agent task:** Create workbook with visual elements

**Workbook 3: ComplianceReport.xlsm**
- **Purpose:** IS 456 + IS 13920 compliance checking
- **Features:**
  - Input: beam dimensions, Ast provided
  - Checks: Min steel, max steel, b/D ratio, ductility
  - Output: Pass/fail with clause references
  - Summary: Compliance score (0-100%)
- **Sample data:** 5 beams (2 compliant, 3 non-compliant)
- **Agent task:** Create compliance checklist automation

**File locations:**
```
Excel/Templates/
├── BeamDesignSchedule.xlsm
├── QuickDesignSheet.xlsm
├── ComplianceReport.xlsm
└── README.md  (explains each template)
```

**Acceptance criteria:**
- [ ] All formulas work on fresh Excel install
- [ ] Add-in dependency clearly documented
- [ ] Each template has built-in instructions sheet
- [ ] Tested on Windows Excel 2016 and Excel 365

---

#### Task 1.2: Capture Tutorial Screenshots
**Deliverable:** 10 PNG images in `docs/images/`

**Using:** [docs/_internal/screenshot-guide.md](screenshot-guide.md) (already created)

**Screenshots needed:**
1. `excel-tutorial-01-addin-install.png` - Add-in installation dialog
2. `excel-tutorial-02-input-table.png` - Input data table (Part 2.1)
3. `excel-tutorial-03-formula-result.png` - Formula result (882 mm²)
4. `excel-tutorial-04-complete-table.png` - Complete design table (Part 6)
5. `excel-tutorial-05-callouts.png` - Bar callouts (3-16φ)
6. `excel-tutorial-06-udf-autocomplete.png` - UDF autocomplete dropdown
7. `excel-tutorial-07-array-formula.png` - Array formula (curly braces)
8. `excel-tutorial-08-macro-dialog.png` - Macro dialog (Alt+F8)
9. `excel-tutorial-09-insert-button.png` - Insert button for macro
10. `excel-tutorial-10-output-report.png` - Formatted beam schedule

**Tools:**
- Windows: Snipping Tool (Win+Shift+S)
- Annotations: Paint 3D or Greenshot
- Compression: TinyPNG (<500KB per image)

**Agent task:**
1. Open BeamDesignSchedule.xlsm (from Task 1.1)
2. Follow screenshot-guide.md step-by-step
3. Capture, annotate, save to docs/images/
4. Verify images render correctly in excel-tutorial.md

**Acceptance criteria:**
- [ ] All 10 images captured
- [ ] File size <500KB each
- [ ] Clear, readable text (1280×720px minimum)
- [ ] Annotations/arrows where specified

---

#### Task 1.3: Create Video Tutorial (Screencast)
**Deliverable:** 1 video (5-10 minutes) showing end-to-end workflow

**Title:** "Designing 10 Beams in 5 Minutes with StructEngLib"

**Script outline:**
- 00:00-00:30 - Intro (what we'll build: 10-beam schedule)
- 00:30-01:00 - Load add-in (show File→Options→Add-ins)
- 01:00-02:00 - Open BeamDesignSchedule.xlsm template
- 02:00-03:00 - Fill input data (copy from ETABS or manual)
- 03:00-04:00 - Formulas auto-calculate (show real-time results)
- 04:00-04:30 - Review status column (2 beams fail, explain why)
- 04:30-05:00 - Export all to DXF (macro button)
- 05:00-05:30 - Open DXF in AutoCAD (show final drawings)
- 05:30-06:00 - Outro (where to get add-in, docs link)

**Recording tools:**
- Windows: OBS Studio (free, open-source)
- Mac: QuickTime Screen Recording
- Editing: DaVinci Resolve (free) or iMovie

**Publishing:**
- Upload to YouTube (public or unlisted)
- Embed in README.md
- Add to docs/getting-started/excel-tutorial.md

**Agent task:**
1. Write detailed script with timestamps
2. Record screen + voiceover (or captions)
3. Edit (cut mistakes, add zoom-ins for formulas)
4. Export to MP4 (1080p, H.264)
5. Upload and get shareable link

**Acceptance criteria:**
- [ ] Video length: 5-10 minutes
- [ ] Audio clear (or captions if no voiceover)
- [ ] Shows real workflow (not just slides)
- [ ] Demonstrates value (speed, accuracy)

---

#### Task 1.4: Create Sample Data Pack
**Deliverable:** 5 CSV files with realistic beam design examples

**File:** `Python/examples/beam_data_samples/`
```
beam_data_samples/
├── residential_typical.csv       (10 beams, 300×450, fck=25)
├── commercial_heavy.csv          (10 beams, 400×600, fck=30)
├── seismic_ductile.csv          (5 beams, IS 13920 compliant)
├── validation_pack_beams.csv    (5 beams from docs/verification/)
└── README.md                    (explains each dataset)
```

**Format (CSV):**
```csv
BeamID,b,D,d,cover,span,fck,fy,Mu,Vu,story,exposure
B1,300,500,450,40,4000,25,500,150,100,GF,Moderate
B2,300,450,400,40,3500,25,500,120,80,1F,Moderate
...
```

**Sources:**
1. SP:16 examples (Table 55-58)
2. Typical residential building (G+3)
3. Validation pack (docs/verification/validation-pack.md)
4. Seismic design examples (IS 13920)

**Agent task:**
1. Research typical beam sizes for Indian construction
2. Create 5 CSV files with headers
3. Validate data (Mu < Mu_lim for most beams)
4. Test: Import each CSV into BeamDesignSchedule.xlsm
5. Verify all formulas work

**Acceptance criteria:**
- [ ] All CSVs load into Excel without errors
- [ ] Data is realistic (typical fck=20-30, fy=500)
- [ ] At least 2 beams fail (to show error handling)
- [ ] README explains each dataset's purpose

---

## Phase 2: UX Innovation (Weeks 3-6)

**Goal:** Go beyond basic UDFs - add features that Python CLI/API cannot easily provide

### Metrics
- [ ] Custom ribbon tab deployed
- [ ] Design wizard (UserForm) functional
- [ ] Real-time validation (on cell change)
- [ ] Insights dashboard auto-generated

### Tasks (Innovation Focus)

#### Task 2.1: Custom Excel Ribbon Tab
**Deliverable:** "Structural Design" ribbon tab in Excel

**Features:**
```
[Structural Design] Tab
├── Design Group
│   ├── Quick Design (opens QuickDesignSheet.xlsm)
│   ├── Batch Design (opens BeamDesignSchedule.xlsm)
│   └── Compliance Check (opens ComplianceReport.xlsm)
├── Export Group
│   ├── Export to DXF
│   ├── Generate BBS
│   └── Create Report
├── Tools Group
│   ├── Bar Calculator (opens helper dialog)
│   ├── Ld Calculator (development length)
│   └── Spacing Checker
└── Help Group
    ├── Documentation (opens docs/README.md)
    ├── FAQ (opens troubleshooting/excel-faq.md)
    └── About (version info)
```

**Implementation:**
- Create CustomUI XML file (RibbonX)
- Package in StructEngLib.xlam
- Callbacks in M12_UI.bas

**Reference:** Office RibbonX documentation

**Agent task:**
1. Design ribbon layout (XML)
2. Create icon set (32×32px PNG)
3. Implement callbacks in VBA
4. Test on Excel 2016 and 365
5. Update installation docs

**Acceptance criteria:**
- [ ] Ribbon tab visible after add-in load
- [ ] All buttons functional
- [ ] Icons clear and professional
- [ ] Works on Windows and Mac Excel

---

#### Task 2.2: Design Wizard (UserForm)
**Deliverable:** Step-by-step beam design wizard

**Workflow:**
```
Step 1: Geometry
┌──────────────────────────┐
│ Beam Width (b):   [300]mm│
│ Total Depth (D):  [500]mm│
│ Clear Cover:      [40]mm │
│ Span:             [4000]mm│
│          [Next >] │
└──────────────────────────┘

Step 2: Materials
┌──────────────────────────┐
│ Concrete (fck): ○ M20    │
│                 ● M25    │
│                 ○ M30    │
│ Steel (fy):     ○ Fe415  │
│                 ● Fe500  │
│   [< Back]  [Next >]│
└──────────────────────────┘

Step 3: Loads
┌──────────────────────────┐
│ Moment (Mu):   [150]kN·m │
│ Shear (Vu):    [100]kN   │
│   [< Back]  [Next >]│
└──────────────────────────┘

Step 4: Detailing
┌──────────────────────────┐
│ Seismic Zone:  ☑ Yes     │
│ Exposure:      [Moderate]│
│   [< Back]  [Design >]│
└──────────────────────────┘

Step 5: Results
┌──────────────────────────┐
│ ✅ Design Complete        │
│ Ast required: 882 mm²    │
│ Bars: 5-16φ (bottom)     │
│ Stirrups: 2L-8φ@150      │
│                          │
│ [Export DXF] [New Design]│
└──────────────────────────┘
```

**Features:**
- Input validation on each step
- Real-time checks (show warnings before "Design" button)
- Results populate worksheet
- Option to save design to catalog

**Agent task:**
1. Design UserForm layout (5 steps)
2. Implement navigation (Next/Back buttons)
3. Add validation (min/max values)
4. Connect to M06_Flexure, M07_Shear, M15_Detailing
5. Test workflow (10 different beams)

**Acceptance criteria:**
- [ ] Wizard completes in <2 minutes
- [ ] Invalid inputs show clear error messages
- [ ] Results match manual UDF calculations
- [ ] "Export DXF" button works from wizard

---

#### Task 2.3: Real-Time Validation
**Deliverable:** Workbook that validates as you type

**Feature:**
- Cell change event triggers validation
- Warning icons appear next to cells
- Status bar shows live checks

**Example:**
```
User types in B2: 150 (beam width)
→ Immediate warning: "⚠️ Width <200mm violates IS 13920 (seismic)"
→ Status bar: "1 warning | 0 errors"

User changes to 230:
→ Warning clears
→ Status bar: "✅ All checks passed"
```

**Checks:**
1. Geometry: b ≥ 200mm, b/D ≥ 0.3
2. Materials: fck in [15-60], fy in [250, 415, 500]
3. Steel %: 0.85/fy ≤ pt ≤ 4%
4. Mu vs Mu_lim: Flag if exceeds

**Implementation:**
- Worksheet_Change event in VBA
- Conditional formatting for icons
- StatusBar API for live updates

**Agent task:**
1. Create validation workbook template
2. Implement Change event handler
3. Add conditional formatting rules
4. Test performance (100 beams)
5. Optimize (avoid recalc loops)

**Acceptance criteria:**
- [ ] Validation runs in <0.5 seconds
- [ ] No circular reference errors
- [ ] Works with undo/redo (Ctrl+Z)
- [ ] Can disable validation (for batch input)

---

#### Task 2.4: Insights Dashboard
**Deliverable:** Auto-generated summary sheet for batch designs

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ DESIGN SUMMARY DASHBOARD                        │
│ Generated: 2026-01-01  |  Project: Sample Bldg  │
├─────────────────────────────────────────────────┤
│ Total Beams: 45                                 │
│ ✅ Safe: 42  |  ⚠️ Check: 3  |  ❌ Failed: 0      │
├─────────────────────────────────────────────────┤
│ MATERIAL SUMMARY                                │
│ • Concrete: 12.5 m³ (fck=25)                    │
│ • Steel: 2,450 kg (fy=500)                      │
│   - Main bars: 1,850 kg                         │
│   - Stirrups: 600 kg                            │
├─────────────────────────────────────────────────┤
│ CRITICAL BEAMS (Highest Utilization)            │
│ 1. B-23: 0.98 (Mu=180kNm, near limit)           │
│ 2. B-12: 0.95 (Shear critical)                  │
│ 3. B-34: 0.92 (Deflection check)                │
├─────────────────────────────────────────────────┤
│ WARNINGS                                        │
│ • B-05: Width 180mm < 200mm (IS 13920)          │
│ • B-17: Steel % = 2.6% > 2.5% (ductile limit)   │
│ • B-29: Stirrup spacing 200mm > max 150mm       │
├─────────────────────────────────────────────────┤
│ [Export Report] [View Details] [Optimize All]   │
└─────────────────────────────────────────────────┘
```

**Charts:**
1. Utilization histogram (0-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0)
2. Steel distribution pie chart (main vs stirrups)
3. Failure mode breakdown (flexure, shear, serviceability)

**Agent task:**
1. Create dashboard template sheet
2. Write VBA macro to populate from design table
3. Add Excel charts (auto-update)
4. Implement drill-down (click beam → jump to row)
5. Test with 50-beam dataset

**Acceptance criteria:**
- [ ] Dashboard updates in <2 seconds
- [ ] Charts update automatically
- [ ] Can export as PDF
- [ ] Highlights top 3 critical beams

---

## Phase 3: Ecosystem & Distribution (Months 2-3)

**Goal:** Make the add-in discoverable and easy to install for 1,000+ users

### Tasks

#### Task 3.1: Create Windows Installer (MSI)
**Deliverable:** One-click installer for Windows

**Features:**
- Copies StructEngLib.xlam to standard location
- Registers add-in in Excel
- Creates Start Menu shortcuts (templates, docs)
- Adds "Uninstall" option

**Tools:** WiX Toolset or Inno Setup

**Agent task:**
1. Research installer tools
2. Create installer script
3. Test on clean Windows 10/11
4. Sign installer (code signing certificate)
5. Host on GitHub Releases

---

#### Task 3.2: ETABS Integration Module
**Deliverable:** Import ETABS beam forces directly into Excel

**Workflow:**
```
ETABS → Export Table → CSV
  ↓
Excel Macro → Import CSV → Populate Design Table
  ↓
Auto-design all beams → Generate DXF for each
```

**Features:**
- Parse ETABS beam forces table
- Map to StructEngLib input format
- Handle moment envelopes (use max)
- Flag discontinuous beams

**Agent task:**
1. Study ETABS export format
2. Create CSV parser in VBA (M13_Integration.bas)
3. Map ETABS units → library units
4. Test with sample ETABS export
5. Document workflow

---

#### Task 3.3: Web Calculator (Parallel to Excel)
**Deliverable:** Simple web interface for quick checks

**Tech stack:**
- Frontend: React/Next.js
- Backend: Python (reuse existing library)
- Deployment: Vercel/Netlify (free tier)

**Features:**
- Single beam quick design
- Results: Ast, bars, stirrups, Ld
- Export: PDF report, no DXF
- Mobile-friendly

**Purpose:** Lead generation for Excel add-in

**Agent task:**
1. Create React form (inputs: b, d, Mu, fck, fy)
2. API endpoint (Python FastAPI)
3. Deploy to web
4. Add "Download Excel Add-in" CTA

---

## Phase 4: Advanced Features (Months 3+)

**Goal:** Features that require significant R&D

#### Task 4.1: AI-Assisted Optimization
- Input: beam span, loads
- Output: optimal b, D, bar arrangement
- Minimize: cost (steel weight)
- Constraints: IS 456 + IS 13920

#### Task 4.2: Cloud Sync (OneDrive/Google Drive)
- Save designs to cloud
- Share with team
- Version control for designs

#### Task 4.3: Mobile Companion App
- iOS/Android app
- View designs on tablet
- Quick calculators (Ld, bar weight)
- Camera scan of hand drawings → Excel

---

## Success Metrics

### Short-Term (Month 1)
- [ ] 3 templates created and tested
- [ ] 10 screenshots captured
- [ ] 1 video tutorial published
- [ ] 5 sample datasets available

### Medium-Term (Month 2-3)
- [ ] Custom ribbon deployed
- [ ] Design wizard functional
- [ ] 100+ downloads of add-in
- [ ] 10+ user testimonials

### Long-Term (Month 4-6)
- [ ] 1,000+ active users
- [ ] Integration with ETABS/STAAD
- [ ] Web calculator live
- [ ] Community forum active

---

## Agent Assignments

### Agent 1: Documentation Agent
- Tasks: 1.2 (screenshots), 1.3 (video), 1.4 (sample data)
- Skills: Technical writing, screen recording
- Timeline: Week 1-2

### Agent 2: Excel Development Agent
- Tasks: 1.1 (templates), 2.1 (ribbon), 2.2 (wizard), 2.3 (validation)
- Skills: VBA, Excel automation, UX design
- Timeline: Week 1-6

### Agent 3: Innovation Agent
- Tasks: 2.4 (dashboard), 3.2 (ETABS integration), 4.1 (AI optimization)
- Skills: Data science, integration, algorithms
- Timeline: Week 3+

### Agent 4: Distribution Agent
- Tasks: 3.1 (installer), 3.3 (web calculator), marketing
- Skills: DevOps, web development, GTM strategy
- Timeline: Month 2+

---

## Next Steps (Immediate)

**For User (Pravin):**
1. **Approve roadmap:** Review phases, adjust priorities
2. **Choose starting point:** Which task to tackle first?
   - Recommendation: Start with Task 1.1 (templates) - highest ROI
3. **Assign agents:** Decide if you'll do manually or use Task tool

**For Agents:**
1. **Task 1.1 can start immediately** (templates) - no blockers
2. **Task 1.2 needs Task 1.1 complete** (screenshots need workbooks)
3. **All Phase 2 tasks need Phase 1 complete** (innovation builds on enablement)

**Risk Mitigation:**
- If templates too time-consuming: Start with screenshots (Task 1.2) using existing BeamDesignApp.xlsm
- If video too complex: Create GIF animations instead (simpler)

---

**Status:** DRAFT - Awaiting approval to proceed
**Created by:** Main Planning Agent
**Next Review:** After Phase 1 completion
