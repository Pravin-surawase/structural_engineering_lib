# IS 456 RC Beam Design Library — API Reference

**Document Version:** 0.7.1  
**Last Updated:** December 15, 2025  
**Scope:** Public APIs for Python/VBA implementations (flexure, shear, ductile detailing, integration, reporting, detailing, DXF export).

---

## 1. Conventions
- **Units:**
  - Moments (`Mu`, `Mu_Lim`): **kN·m**
  - Shear Forces (`Vu`, `Vus`): **kN**
  - Dimensions (`b`, `d`, `D`): **mm**
  - Areas (`Ast`, `Asv`): **mm²**
  - Stresses (`fck`, `fy`, `Tv`, `Tc`): **N/mm²** (MPa)
  - Percentages (`pt`): **%** (e.g., 1.2 for 1.2%)
- **Sign Conventions:**
  - Inputs are generally treated as absolute values for design checks.
  - UI/Application layer is responsible for handling signs before calling these libraries.
- **Return Values:**
  - VBA (planned): User Defined Types (UDTs) for complex results, or simple types (`Double`) for helpers.
  - Python: `dataclasses` or simple types (`float`).
  - Excel UDFs: wrapper functions (VBA) to expose selected helpers (TBD).

---

## 2. Flexure Module (`M06_Flexure` / `flexure.py`)

### 2.1 Calculate Limiting Moment (`Mu_Lim`)
Calculates the maximum moment a singly reinforced section can resist.

**Python:**
```python
def calculate_mu_lim(
    b: float, 
    d: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.2 Calculate Required Steel (`Ast_Required`)
Calculates tension steel area for a given moment. Returns `-1` if `Mu > Mu_Lim`.

**Python:**
```python
def calculate_ast_required(
    b: float, 
    d: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.3 Design Singly Reinforced Beam
Performs full design check including under/over-reinforced status and min/max steel checks; flags when Mu exceeds Mu_lim.

**Python:**
```python
def design_singly_reinforced(
    b: float, 
    d: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> FlexureResult
```

### 2.4 Design Doubly Reinforced Beam
Designs a beam that can be singly or doubly reinforced. If `Mu > Mu_lim`, calculates compression steel (`Asc`) and additional tension steel.

**Python:**
```python
def design_doubly_reinforced(
    b: float, 
    d: float, 
    d_dash: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> FlexureResult
```

**Return Type (`FlexureResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `mu_lim` | float | Limiting moment capacity (kN·m) |
| `ast_required` | float | Required tension steel area (mm²) |
| `asc_required` | float | Required compression steel area (mm²) |
| `pt_provided` | float | Percentage of tension steel provided |
| `section_type` | Enum | `UNDER_REINFORCED`, `BALANCED`, `OVER_REINFORCED` |
| `xu` | float | Actual neutral axis depth (mm) |
| `xu_max` | float | Max neutral axis depth (mm) |
| `is_safe` | bool | True if design is valid |
| `error_message` | str | Details if unsafe |

---

## 3. Shear Module (`M07_Shear` / `shear.py`)

*(See existing documentation)*

---

## 4. Ductile Detailing Module (`M10_Ductile` / `ductile.py`)

### 4.1 Check Beam Ductility
Performs comprehensive checks for IS 13920:2016 compliance (geometry, min/max steel, confinement spacing).

**Python:**
```python
def check_beam_ductility(
    b: float, 
    D: float, 
    d: float, 
    fck: float, 
    fy: float, 
    min_long_bar_dia: float
) -> DuctileBeamResult
```

**Return Type (`DuctileBeamResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `is_geometry_valid` | bool | True if b >= 200 and b/D >= 0.3 |
| `min_pt` | float | Min tension steel % (Cl 6.2.1) |
| `max_pt` | float | Max tension steel % (2.5%) |
| `confinement_spacing` | float | Max hoop spacing in plastic hinge zone (mm) |
| `remarks` | str | Compliance status or error details |

### 4.2 Helper Functions
- `check_geometry(b, D)`
- `get_min_tension_steel_percentage(fck, fy)`
- `calculate_confinement_spacing(d, min_long_bar_dia)`

---

## 5. Serviceability Module (`serviceability.py`) (v0.8 Level A)

**Status:** New in v0.8 (Python-first; VBA parity planned).

### 5.1 Deflection Check (Span/Depth Method)

**Units:**
- `span_mm`, `d_mm`: **mm**

**Python:**
```python
def check_deflection_span_depth(
        *,
        span_mm: float,
        d_mm: float,
        support_condition: SupportCondition | str = "simply_supported",
        base_allowable_ld: float | None = None,
        mf_tension_steel: float | None = None,
        mf_compression_steel: float | None = None,
        mf_flanged: float | None = None,
) -> DeflectionResult
```

**Behavior (Level A):**
- Computes `L/d` and compares to `allowable L/d`.
- `allowable L/d` is computed as:
    $$\text{allowable} = \text{base} \times mf_{tension} \times mf_{compression} \times mf_{flanged}$$
- If base/modifiers are not provided, the result records explicit assumptions.

### 5.2 Crack Width Check (Annex-F-style Estimate)

**Units:**
- Geometry inputs: **mm**
- `fs_service_nmm2`: **N/mm²**
- Result crack width: **mm**

**Python:**
```python
def check_crack_width(
        *,
        exposure_class: ExposureClass | str = "moderate",
        limit_mm: float | None = None,
        acr_mm: float | None = None,
        cmin_mm: float | None = None,
        h_mm: float | None = None,
        x_mm: float | None = None,
        epsilon_m: float | None = None,
        fs_service_nmm2: float | None = None,
        es_nmm2: float = 200000.0,
) -> CrackWidthResult
```

**Behavior (Level A):**
- Computes an Annex-F-style crack width estimate using the configured inputs.
- If `epsilon_m` is not provided, it can be estimated as `fs_service_nmm2 / es_nmm2` and recorded as an assumption.
- If required parameters are missing, returns `is_ok=False` with a clear remark (no guessing).

**Return Types:**
- `DeflectionResult`: contains `is_ok`, `remarks`, `support_condition`, and `inputs/computed/assumptions` payloads.
- `CrackWidthResult`: contains `is_ok`, `remarks`, `exposure_class`, and `inputs/computed/assumptions` payloads.

---
## 6. Compliance Checker (`compliance.py`) (v0.8+)
**Goal:** One-click verdict across checks with clear “why fail” remarks.

### 6.1 Multi-Case Compliance Report

**Inputs:** already-factored per-case actions.

**Units:**
- `mu_knm`: **kN·m**
- `vu_kn`: **kN**
- `b_mm`, `D_mm`, `d_mm`, `d_dash_mm`: **mm**
- `fck_nmm2`, `fy_nmm2`: **N/mm²**

**Python:**
```python
def check_compliance_report(
        *,
        cases: Sequence[dict],
        b_mm: float,
        D_mm: float,
        d_mm: float,
        fck_nmm2: float,
        fy_nmm2: float,
        d_dash_mm: float = 50.0,
        asv_mm2: float = 100.0,
        pt_percent: float | None = None,
        deflection_defaults: dict | None = None,
        crack_width_defaults: dict | None = None,
) -> ComplianceReport
```

**Behavior (MVP):**
- Runs flexure + shear for each case.
- Optionally runs deflection/crack checks when the corresponding defaults/params are provided.
- Determines a deterministic governing case using utilization ratios (demand/limit):
    - flexure: $|Mu|/Mu_{lim}$
    - shear: $\tau_v/\tau_{c,max}$
    - deflection: $(L/d)/(allowable\ L/d)$
    - crack width: $w_{cr}/w_{lim}$
- Governing case is the case with the highest utilization vector (sorted descending). Exact ties are broken by input order.

**Outputs:**
- `ComplianceReport.summary`: compact, Excel-friendly dict containing `num_cases`, `num_failed_cases`, governing identifiers, and per-check max utilizations.

---
<<<<<<< HEAD
=======

>>>>>>> feat/task-042-compliance-checker
### 2.5 Calculate Limiting Moment (Flanged)
Calculates the limiting moment of resistance for a T-beam section.

**Python:**
```python
def calculate_mu_lim_flanged(
    bw: float, 
    bf: float, 
    d: float, 
    Df: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.6 Design Flanged Beam
Designs a flanged beam (T-beam). Handles neutral axis in flange (rectangular behavior), neutral axis in web (singly reinforced T), and doubly reinforced T-beams.

**Python:**
```python
def design_flanged_beam(
    bw: float, 
    bf: float, 
    d: float, 
    Df: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float,
    d_dash: float = 50.0
) -> FlexureResult
```

---

## 3. Shear Module (`M07_Shear` / `shear.py`)

### 3.1 Calculate Nominal Shear Stress (`Tv`)
Calculates $\tau_v = \frac{V_u}{bd}$.

**Python:**
```python
def calculate_tv(
    vu_kn: float, 
    b: float, 
    d: float
) -> float
```

### 3.2 Design Shear Reinforcement
Performs shear design: checks $\tau_v$ vs $\tau_{c,max}$, gets $\tau_c$ (Table 19), computes $V_{us}$ and stirrup spacing with code limits.
- Table 19 policy: clamp pt to 0.15–3.0%; use nearest lower concrete grade column (no fck interpolation).
- Table 20: if $\tau_v > \tau_{c,max}$, section is inadequate.

**Python:**
```python
def design_shear(
    vu_kn: float, 
    b: float, 
    d: float, 
    fck: float, 
    fy: float, 
    asv: float, 
    pt: float
) -> ShearResult
```

**Return Type (`ShearResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `tv` | float | Nominal shear stress (N/mm²) |
| `tc` | float | Design shear strength of concrete (N/mm²) |
| `tc_max` | float | Max shear stress limit (N/mm²) |
| `vus` | float | Shear to be resisted by stirrups (kN) |
| `spacing` | float | Governing stirrup spacing (mm) |
| `is_safe` | bool | True if $\tau_v \le \tau_{c,max}$ |
| `remarks` | str | Design status (e.g., "Shear reinforcement required") |

---

## 4. Excel User Defined Functions (UDFs)
Implemented in `M09_UDFs.bas` for direct worksheet use.

| Function | Description | Returns |
|----------|-------------|---------|
| `IS456_MuLim(b, d, fck, fy)` | Limiting Moment of Resistance | kN·m |
| `IS456_AstRequired(b, d, Mu, fck, fy)` | Required Tension Steel | mm² or "Over-Reinforced" |
| `IS456_ShearSpacing(Vu, b, d, fck, fy, Asv, pt)` | Stirrup Spacing | mm or "Unsafe..." |
| `IS456_MuLim_Flanged(bw, bf, d, Df, fck, fy)` | Limiting Moment (T-Beam) | kN·m |
| `IS456_Design_Rectangular(...)` | Full Design (Singly/Doubly) | Array [Ast, Asc, Xu, Status] |
| `IS456_Design_Flanged(...)` | Full Design (T-Beam) | Array [Ast, Asc, Xu, Status] |
| `IS456_Check_Ductility(b, D, d, fck, fy, db)` | IS 13920 Compliance Check | "Compliant" or Error Msg |
| `IS456_Tc(fck, pt)` | Table 19 Shear Strength | N/mm² |
| `IS456_TcMax(fck)` | Table 20 Max Shear Stress | N/mm² |

---

## 5. Integration Module (`M13_Integration.bas`)

This module handles data import from external analysis software (ETABS) into the BEAM_INPUT table.

### 5.1 Import ETABS Data
**VBA:**
```vba
Public Sub Import_ETABS_Data()
```
- Opens file picker (Mac/Windows compatible) or falls back to InputBox.
- Parses CSV with robust handling of quoted values and header aliases.
- Groups data by beam (Story|Label) and aggregates forces into Start/Mid/End buckets.
- Falls back to sample data if no file is selected.

### 5.2 Generate Sample ETABS CSV
**VBA:**
```vba
Public Sub Generate_Sample_ETABS_CSV()
```
- Creates a sample ETABS-style CSV file for testing.
- Outputs: Story, Label, Station, M3, V2, Output Case columns.

### 5.3 Header Normalization
The module recognizes these header aliases:
| Standard | Aliases Recognized |
|----------|-------------------|
| `Story` | `Story`, `Story Name` |
| `Label` | `Label`, `Beam` |
| `Station` | `Station`, `Dist` |
| `M3` | `M3`, `Moment` |
| `V2` | `V2`, `Shear` |
| `Output Case` | `Case`, `Combo` |

### 5.4 Bucket Aggregation Logic
Forces are aggregated into three zones based on station position:
| Zone | Station Range | Use Case |
|------|--------------|----------|
| Start | 0% – 20% of span | Support hogging moment |
| Mid | 20% – 80% of span | Midspan sagging moment |
| End | 80% – 100% of span | Support hogging moment |

Within each bucket, the value with maximum absolute magnitude is selected (preserving sign).

---

## 6. Reporting Module (`M14_Reporting.bas`)

This module generates the Beam Schedule from design output.

### 6.1 Generate Beam Schedule
**VBA:**
```vba
Public Sub Generate_Beam_Schedule()
```
- Reads from `tbl_BeamDesign` on BEAM_DESIGN sheet.
- Writes to `tbl_BeamSchedule` on BEAM_SCHEDULE sheet.
- Auto-sorts input by Story/ID before grouping.
- Uses dynamic column lookup for robustness.

### 6.2 Schedule Output Format
| Column | Description |
|--------|-------------|
| Story | Story identifier |
| ID | Beam identifier |
| Size | `bxD` (e.g., "230x450") |
| Bot-Start, Bot-Mid, Bot-End | Bottom steel pattern |
| Top-Start, Top-Mid, Top-End | Top steel pattern |
| Stir-Start, Stir-Mid, Stir-End | Stirrup specification |

### 6.3 Bar Pattern Conversion
`Get_Bar_Pattern(area)` converts steel area to practical notation:
| Area Range | Bar Diameter | Example Output |
|------------|--------------|----------------|
| < 300 mm² | 12 mm | "3-12 (#280)" |
| 300–800 mm² | 16 mm | "3-16 (#600)" |
| 800–1500 mm² | 20 mm | "3-20 (#942)" |
| > 1500 mm² | 25 mm | "4-25 (#1963)" |

### 6.4 Steel Placement Logic
Based on moment sign:
- **Negative Mu (Hogging):** Tension at top → `Ast` placed in Top row.
- **Positive Mu (Sagging):** Tension at bottom → `Ast` placed in Bottom row.

---

## 7. Usage Examples

### 7.1 Python Example
```python
from structural_lib.flexure import design_singly_reinforced

# Design a beam for 150 kNm moment
result = design_singly_reinforced(
    b=230,
    d=450,
    d_total=500,
    mu_knm=150.0,
    fck=25,
    fy=500
)

if result.is_safe:
    print(f"Ast Required: {result.ast_required:.2f} mm²")
    print(f"Pt Provided: {result.pt_provided:.2f}%")
else:
    print(f"Design Failed: {result.error_message}")
```

---

## 8. Ductile Detailing (IS 13920:2016) — `ductile.py` / `M10_Ductile.bas`

### 8.1 Geometry Check
**Python:**
```python
check_geometry(b: float, D: float) -> Tuple[bool, str]
```
- Valid if b ≥ 200 mm and b/D ≥ 0.3.

**VBA:**
```vba
Public Function Check_Geometry(b As Double, D As Double, ByRef ErrorMsg As String) As Boolean
```

### 8.2 Minimum/Maximum Tension Steel
**Python:**
```python
get_min_tension_steel_percentage(fck: float, fy: float) -> float  # returns %
get_max_tension_steel_percentage() -> float  # 2.5%
```

**VBA:**
```vba
Public Function Get_Min_Tension_Steel_Percentage(fck As Double, fy As Double) As Double
Public Function Get_Max_Tension_Steel_Percentage() As Double
```

### 8.3 Confinement Spacing (Plastic Hinge Zones)
**Python:**
```python
calculate_confinement_spacing(d: float, min_long_bar_dia: float) -> float  # mm
```
Spacing = min(d/4, 8*db_min, 100 mm).

**VBA:**
```vba
Public Function Calculate_Confinement_Spacing(d As Double, min_long_bar_dia As Double) As Double
```

### 8.4 Aggregate Check
**Python:**
```python
check_beam_ductility(
    b: float, D: float, d: float,
    fck: float, fy: float,
    min_long_bar_dia: float
) -> DuctileBeamResult
```

**VBA:**
```vba
Public Function Check_Beam_Ductility( _
    b As Double, D As Double, d As Double, _
    fck As Double, fy As Double, _
    min_long_bar_dia As Double _
) As DuctileBeamResult
```

**DuctileBeamResult Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `is_geometry_valid` | bool | Geometry check result |
| `min_pt` | float | Minimum tension steel (%) |
| `max_pt` | float | Maximum tension steel (%) |
| `confinement_spacing` | float | Max hoop spacing in hinge zone (mm) |
| `remarks` | str | "Compliant" or reason for failure |

### 7.2 VBA Example
```vba
Sub TestBeam()
    Dim res As FlexureResult
    ' Design for 150 kNm
    res = Design_Singly_Reinforced(230, 450, 500, 150, 25, 500)
    
    If res.IsSafe Then
        Debug.Print "Ast Required: " & res.Ast_Required
    Else
        Debug.Print "Design Failed: " & res.ErrorMessage
    End If
End Sub
```

### 7.3 Worked Examples (Reference Values)

Use these to sanity-check outputs (within typical rounding tolerance: ±0.5 kN·m for moments, ±1% for areas/stresses, spacing capped to code limits).

1) **Flexure — singly reinforced**
- Inputs: b=230 mm, d=450 mm, D=500 mm, Mu=150 kN·m, fck=25, fy=500.
- Expected: Mu_lim ≈ 163 kN·m; Ast_required ≈ 1040–1100 mm²; Pt ≈ 1.0–1.1%; xu_max = 0.46d.

2) **Shear — stirrups required**
- Inputs: b=230 mm, d=450 mm, Vu=100 kN, fck=20, fy_stirrup=415, pt=1.0%, 2-legged 8 mm stirrups (Asv≈100.5 mm²).
- Expected: τv ≈ 0.97 N/mm²; τc (M20, pt=1.0%) = 0.62 N/mm²; τv < τc,max=2.8; Vus ≈ 35–36 kN; spacing governed by max limits → 300 mm.

3) **Shear — unsafe section**
- Inputs: b=230 mm, d=450 mm, Vu=300 kN, fck=20, fy_stirrup=415, pt=1.0%, Asv=100.5 mm².
- Expected: τv ≈ 2.9 N/mm² > τc,max=2.8 → DesignStatus/remarks indicate section inadequate (increase b or d).

4) **Flexure — minimum steel governed**
- Inputs: b=230 mm, d=450 mm, D=500 mm, Mu=5 kN·m, fck=20, fy=415.
- Expected: Ast_min = 0.85*b*d/fy ≈ 212 mm²; result should return Ast = Ast_min with a “Minimum steel” note.
---

## 9. Detailing Module (`detailing.py`) — v0.7+

Calculates reinforcement detailing parameters per IS 456:2000 and SP 34:1987.

### 9.1 Development Length
**Python:**
```python
def calculate_development_length(
    bar_dia: float,           # mm
    fy: float,                # N/mm² (250, 415, 500, 550)
    fck: float,               # N/mm² (15-50)
    bar_type: str = "deformed", # "deformed" or "plain"
    is_compression: bool = False
) -> float  # Returns Ld in mm
```

**Formula:** `Ld = (φ × σs) / (4 × τbd)`
- σs = 0.87 × fy (tension) or 0.67 × fy (compression)
- τbd from bond stress table with 60% increase for deformed bars

### 9.2 Lap Length
**Python:**
```python
def calculate_lap_length(
    bar_dia: float,
    fy: float,
    fck: float,
    bar_type: str = "deformed",
    lap_zone: str = "tension"  # "tension" or "compression"
) -> float  # Returns lap length in mm
```

**Multiplier:** 1.5× for tension zones, 1.0× for compression zones.

### 9.3 Bar Spacing Check
**Python:**
```python
def calculate_bar_spacing(
    b: float,                 # Beam width (mm)
    cover: float,             # Clear cover (mm)
    stirrup_dia: float,       # Stirrup diameter (mm)
    bar_dia: float,           # Main bar diameter (mm)
    bar_count: int            # Number of bars
) -> float  # Returns c/c spacing (mm)

def check_min_spacing(
    spacing: float,
    bar_dia: float,
    agg_size: float = 20.0
) -> Tuple[bool, str]  # (is_valid, message)
```

**Minimum Spacing:** max(bar_dia, agg_size + 5mm, 25mm) per IS 456 Cl 26.3.2.

### 9.4 Bar Arrangement Selection
**Python:**
```python
def select_bar_arrangement(
    ast_required: float,      # Required area (mm²)
    b: float,                 # Beam width (mm)
    cover: float,             # Clear cover (mm)
    stirrup_dia: float = 8.0, # Stirrup diameter (mm)
    preferred_dia: float = None,
    max_layers: int = 2
) -> BarArrangement
```

**BarArrangement Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `count` | int | Number of bars |
| `diameter` | float | Bar diameter (mm) |
| `area_provided` | float | Total area (mm²) |
| `spacing` | float | C/C spacing (mm) |
| `layers` | int | Number of layers |
| `callout()` | method | Returns "3-16φ" format |

### 9.5 Complete Beam Detailing
**Python:**
```python
def create_beam_detailing(
    beam_id: str,
    story: str,
    b: float, D: float, span: float, cover: float,
    fck: float, fy: float,
    ast_start: float, ast_mid: float, ast_end: float,
    asc_start: float = 0, asc_mid: float = 0, asc_end: float = 0,
    stirrup_dia: float = 8,
    stirrup_spacing_start: float = 150,
    stirrup_spacing_mid: float = 200,
    stirrup_spacing_end: float = 150,
    is_seismic: bool = False
) -> BeamDetailingResult
```

**BeamDetailingResult Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `beam_id` | str | Beam identifier |
| `story` | str | Story identifier |
| `b`, `D`, `span`, `cover` | float | Geometry (mm) |
| `top_bars` | List[BarArrangement] | [start, mid, end] |
| `bottom_bars` | List[BarArrangement] | [start, mid, end] |
| `stirrups` | List[StirrupArrangement] | [start, mid, end] |
| `ld_tension` | float | Development length (mm) |
| `ld_compression` | float | Compression Ld (mm) |
| `lap_length` | float | Lap splice length (mm) |
| `is_valid` | bool | Validity status |
| `remarks` | str | Notes/warnings |

---

## 10. DXF Export Module (`dxf_export.py`) — v0.7+

Generates CAD-ready DXF drawings from detailing results. **Requires:** `pip install ezdxf`

### 10.1 Generate Beam DXF
**Python:**
```python
def generate_beam_dxf(
    result: BeamDetailingResult,
    output_path: str,
    scale: float = 1.0,
    include_section: bool = True
) -> None  # Creates DXF file at output_path
```

### 10.2 DXF Layers
| Layer Name | Color | Content |
|------------|-------|---------|
| `BEAM_OUTLINE` | White (7) | Beam perimeter |
| `REBAR_MAIN` | Red (1) | Main bars (top/bottom) |
| `REBAR_STIRRUP` | Green (3) | Stirrup outlines |
| `DIMENSIONS` | Cyan (4) | Dimension lines |
| `TEXT` | Yellow (2) | Callouts, labels |
| `CENTERLINE` | Magenta (6) | Center lines |

### 10.3 Output Format
- **DXF Version:** R2010 (AC1024) for wide compatibility
- **Units:** mm (1:1 scale)
- **Views:** Elevation + Cross-section
- **Origin:** Bottom-left of beam at first support

---

## 11. Excel Integration Module (`excel_integration.py`) — v0.7+

Bridges Excel/CSV data with detailing and DXF generation.

### 11.1 Load Beam Data
**Python:**
```python
def load_beam_data_from_csv(filepath: str) -> List[BeamDesignData]
def load_beam_data_from_json(filepath: str) -> List[BeamDesignData]
```

**BeamDesignData Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `beam_id` | str | Beam identifier |
| `story` | str | Story level |
| `b`, `D`, `d`, `span`, `cover` | float | Geometry (mm) |
| `fck`, `fy` | float | Material grades |
| `Mu`, `Vu` | float | Design forces |
| `Ast_req`, `Asc_req` | float | Steel areas (mm²) |
| `stirrup_dia`, `stirrup_spacing` | float | Stirrup details |

### 11.2 Batch Processing
**Python:**
```python
def batch_generate_dxf(
    input_file: str,          # CSV or JSON file path
    output_folder: str,       # DXF output directory
    is_seismic: bool = False  # Apply IS 13920
) -> List[ProcessingResult]

def generate_summary_report(
    results: List[ProcessingResult]
) -> str  # Text summary

def generate_detailing_schedule(
    results: List[ProcessingResult]
) -> List[Dict]  # Schedule rows for CSV export
```

### 11.3 CLI Usage
```bash
# Basic usage
python -m structural_lib.excel_integration beam_design.csv -o ./dxf_output

# With seismic detailing and schedule export
python -m structural_lib.excel_integration beam_design.csv \
    -o ./dxf_output \
    --seismic \
    --schedule detailing_schedule.csv
```

### 11.4 CSV Input Format
```csv
BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,Story1,300,500,4000,40,25,500,150,100,942.5,0,8,150,OK
B2,Story1,300,450,3000,40,25,500,100,80,628.3,0,8,175,OK
```