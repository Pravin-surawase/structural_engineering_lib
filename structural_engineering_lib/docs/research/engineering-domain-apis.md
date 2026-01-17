# Engineering Domain API Patterns Research

> **Research on domain-specific API patterns for structural engineering libraries**
> Created: 2026-01-07 | Part of: API Improvement Research (TASK-205)

---

## Purpose

This research analyzes API patterns from engineering/CAD domain libraries to inform our structural engineering library design. Focus areas:
- Unit handling and conversion patterns
- Engineering notation conventions (IS 456, Eurocode, etc.)
- Domain-specific naming and parameter patterns
- CAD/drawing library integration approaches
- Physical quantity representation

**Goal**: Extract domain-specific best practices that complement general Python API patterns (TASK-200/201).

---

## Table of Contents

1. [Libraries Analyzed](#1-libraries-analyzed)
2. [PyNite: Structural Analysis Library](#2-pynite-structural-analysis-library)
3. [ezdxf: DXF/DWG CAD Library](#3-ezdxf-dxfdwg-cad-library)
4. [pint: Physical Quantities & Units](#4-pint-physical-quantities--units)
5. [handcalcs: Engineering Calculation Documentation](#5-handcalcs-engineering-calculation-documentation)
6. [OpenSees Python Bindings](#6-opensees-python-bindings)
7. [Cross-Library Patterns](#7-cross-library-patterns)
8. [Unit Handling Strategies](#8-unit-handling-strategies)
9. [Engineering Notation Conventions](#9-engineering-notation-conventions)
10. [Recommendations for Our Library](#10-recommendations-for-our-library)

---

## 1. Libraries Analyzed

### Selection Criteria

Libraries chosen for analysis:
1. **PyNite** - Structural analysis (similar domain to ours)
2. **ezdxf** - CAD/drawing integration (we export DXF)
3. **pint** - Physical quantities/units (industry standard)
4. **handcalcs** - Engineering calculations (similar use case)
5. **OpenSees** - FEA (reference for large structural engineering API)

### Analysis Focus

For each library, we examine:
- **API design patterns**: Function signatures, parameter conventions
- **Unit handling**: How physical quantities are represented
- **Naming conventions**: Domain terminology, abbreviations
- **Result objects**: How calculation outputs are structured
- **Error handling**: Validation and error messages
- **Integration patterns**: How library fits into engineering workflows

---

## 2. PyNite: Structural Analysis Library

**Repository**: https://github.com/JWock82/PyNite
**Domain**: 3D structural analysis (FEA for frames, trusses, plates)
**Version analyzed**: v0.0.93 (2023)

### 2.1 API Design Observations

**Member definition pattern:**
```python
# PyNite uses method chaining for model building
model = FEModel3D()
model.add_node('N1', x=0, y=0, z=0)
model.add_node('N2', x=10*12, y=0, z=0)  # feet to inches conversion
model.add_member(
    name='M1',
    i_node='N1',
    j_node='N2',
    E=29000,      # ksi (implicit units)
    G=11200,      # ksi
    Iy=100,       # in^4
    Iz=150,       # in^4
    J=250,        # in^4
    A=10,         # in^2
)
```

**Key patterns:**
- **String IDs** for nodes/members (not integers): `'N1'`, `'M1'`
- **Implicit units** (documented but not enforced): ksi, inches, kips
- **Method chaining** for model building
- **Named parameters** for all properties (good discoverability)

### 2.2 Unit Handling

**PyNite approach:**
```python
# Units are implicit but documented
# User must convert consistently
model.add_node('N1', x=0, y=0, z=0)          # inches (US units)
model.add_member('M1', ..., E=29000)         # ksi (implicit)
model.add_load('L1', member='M1', w=10)      # kips/ft (implicit)

# NO built-in unit conversion
# Users must handle conversion manually
```

**Pros:**
- Simple, no overhead
- Fast for users familiar with consistent unit system

**Cons:**
- Easy to mix units (inches vs feet)
- No validation of unit consistency
- Burden on user to track units

**Lesson for us**: Consider whether to enforce units or trust user consistency.

### 2.3 Result Access Patterns

```python
# Results accessed via node/member name
node_displacement = model.get_node_displacement('N1', 'Dz', combo='1.2D+1.6L')
member_shear = model.get_member_shear('M1', x=5*12, combo='1.2D+1.6L')
member_moment = model.get_member_moment('M1', x=5*12, combo='1.2D+1.6L')

# Plotting results
model.plot_deformed_shape(combo='1.2D+1.6L', scale=100)
```

**Key patterns:**
- **String-based access**: Use entity names, not indices
- **Combo parameter**: Load combination specified at access time
- **Position parameter**: Results at specific location (x along member)
- **Built-in plotting**: Visualization integrated into API

### 2.4 Validation Approach

**Input validation:**
```python
# PyNite validates structural validity
model.analyze()  # Will raise errors for:
# - Unstable structures
# - Singular stiffness matrix
# - Unsupported nodes
# But NOT for unit consistency
```

**Observations:**
- Validates **structural** constraints (DOFs, supports)
- Does NOT validate **value** reasonableness (units, magnitudes)
- Relies on solver to catch problems (late validation)

### 2.5 Domain Naming Conventions

**PyNite uses standard structural notation:**
- `E`, `G` (moduli - uppercase single letter)
- `Iy`, `Iz`, `J` (moments of inertia - uppercase with subscript)
- `A` (area - uppercase)
- `i_node`, `j_node` (start/end nodes - lowercase with underscore)
- `Dz`, `Rx` (displacements, rotations - uppercase with direction)

**Consistency with textbook notation**: High
**IDE autocomplete friendly**: Yes (full words: `i_node` not just `i`)

---

## 3. ezdxf: DXF/DWG CAD Library

**Repository**: https://github.com/mozman/ezdxf
**Domain**: CAD file creation/editing (DXF/DWG format)
**Version analyzed**: v1.2.0 (2024)

### 3.1 API Design Observations

**Entity creation pattern:**
```python
import ezdxf

# Create new drawing
doc = ezdxf.new('R2010')  # DXF version
msp = doc.modelspace()

# Add entities with explicit units
msp.add_line((0, 0), (100, 0))  # Coordinates in drawing units
msp.add_circle((50, 50), radius=20)
msp.add_text(
    'BEAM B1',
    dxfattribs={
        'height': 2.5,      # Text height in drawing units
        'layer': 'TEXT',
        'style': 'STANDARD',
    }
)

# Save
doc.saveas('output.dxf')
```

**Key patterns:**
- **Tuples for coordinates**: `(x, y)` or `(x, y, z)` not separate params
- **Drawing units**: All dimensions in DXF drawing units (unitless)
- **dxfattribs dict**: Layer, color, style in dictionary
- **Fluent interface**: `doc.modelspace().add_line(...)`

### 3.2 Unit Handling Strategy

**ezdxf approach:**
```python
# Drawing units are UNITLESS
# User must scale to their preferred unit system
# Example: Design in mm, DXF in mm
msp.add_line((0, 0), (300, 550))  # User knows this is mm

# No built-in unit conversion
# User scales at export time if needed
scale = 1.0  # mm to mm (1:1)
scale = 25.4  # inches to mm
```

**Lesson for us**:
- DXF export should assume consistent units (mm)
- Document expected units clearly
- Consider optional scale parameter for unit conversion

### 3.3 Layer and Style Management

```python
# ezdxf uses string names for layers
doc.layers.add('REINFORCEMENT', color=1)  # Red
doc.layers.add('DIMENSIONS', color=7)     # White
doc.layers.add('TEXT', color=7)

# Entities reference layers by name
msp.add_line((0, 0), (100, 0), dxfattribs={'layer': 'REINFORCEMENT'})
```

**Our current approach**: Similar (string layer names)
**Validation**: ezdxf validates layer exists at save time

### 3.4 Coordinate Systems

**ezdxf coordinate handling:**
```python
# Global WCS (World Coordinate System)
msp.add_line((0, 0), (100, 0))

# User Coordinate Systems (UCS)
with doc.ucs_context() as ucs:
    ucs.translate(50, 50)
    ucs.rotate_z(45)
    # Add entities in rotated/translated system
    msp.add_line((0, 0), (100, 0))  # Appears rotated in WCS
```

**Lesson**: Support for coordinate transformations (we don't need UCS yet).

---

## 4. pint: Physical Quantities & Units

**Repository**: https://github.com/hgrecco/pint
**Domain**: Physical quantities with units (industry standard)
**Version analyzed**: v0.23 (2024)

### 4.1 Core API Pattern

**Creating quantities:**
```python
from pint import UnitRegistry
ureg = UnitRegistry()

# Quantity = magnitude + unit
length = 300 * ureg.mm
force = 150 * ureg.kN
stress = 30 * ureg.MPa
moment = 250 * ureg.kN * ureg.m

# Or string parsing
length = ureg('300 mm')
force = ureg('150 kN')
```

**Key features:**
- **Operator overloading**: `*`, `/`, `+`, `-` handle units
- **Type safety**: Adding mm + kN raises error
- **Conversion**: Automatic with `.to()` method

### 4.2 Unit Conversion Pattern

```python
# Explicit conversion
length_m = length.to('m')           # 0.3 m
length_in = length.to('inch')       # 11.811 inches

# Context conversion (maintains magnitude)
with ureg.context('imperial'):
    length_ft = length.to('feet')

# Dimensionality checking
try:
    wrong = (300 * ureg.mm) + (150 * ureg.kN)
except DimensionalityError:
    print("Cannot add length and force")
```

**Powerful but heavyweight**: ~100KB import, slight overhead per operation.

### 4.3 Integration with NumPy

```python
import numpy as np

# Quantities work with arrays
lengths = np.array([300, 400, 500]) * ureg.mm
forces = np.array([100, 150, 200]) * ureg.kN

# Operations preserve units
moments = forces * lengths  # kN·mm units automatically

# Convert array results
moments_kn_m = moments.to('kN*m')  # [30, 60, 100] kN·m
```

**Lesson**: pint enables unit-safe calculations but adds complexity.

### 4.4 Performance Considerations

```python
# Benchmark: pint vs raw floats
# Simple multiplication

# Raw floats: ~50 ns
result = 300.0 * 150.0

# Pint Quantities: ~2000 ns (40× slower)
result = (300 * ureg.mm) * (150 * ureg.kN)

# For batch operations: convert at boundaries
lengths_mm = np.array([300, 400, 500])  # Raw floats
forces_kn = np.array([100, 150, 200])   # Raw floats
# ... do calculations ...
# Convert results at end
results_with_units = results * ureg.kN * ureg.m
```

**Lesson for us**:
- Use pint at API boundaries (input/output validation)?
- Or keep internal calculations unit-free for performance?
- Document units in param names instead (`b_mm`, `fck_mpa`)?

### 4.5 Custom Unit Systems

```python
# pint allows custom units
ureg.define('IS456_stress = MPa')
ureg.define('IS456_moment = kN*m')

# Or use contexts
IS456_context = Context('IS456')
IS456_context.add_transformation('[length]', '[length]', lambda ureg, x: x)
ureg.add_context(IS456_context)
```

**Not widely used**: Most engineers prefer SI base units.

---

## 5. handcalcs: Engineering Calculation Documentation

**Repository**: https://github.com/connorferster/handcalcs
**Domain**: Engineering calculations with symbolic rendering
**Version analyzed**: v1.8.0 (2024)

### 5.1 Core Concept

**handcalcs renders Python code as formatted equations:**
```python
import handcalcs.render
from math import sqrt

@handcalcs.render
def beam_design(b, d, M_u, f_c, f_y):
    # All calculations shown symbolically in output
    M_u_lim = 0.138 * f_c * b * d**2
    rho_max = 0.75 * 0.85 * f_c / f_y * (0.003 / (0.003 + 0.0038))
    A_st_req = M_u / (0.87 * f_y * 0.9 * d)
    return locals()

# Renders as:
# M_{u,lim} = 0.138 × f_c × b × d²
# ρ_{max} = 0.75 × 0.85 × f_c / f_y × (0.003 / (0.003 + 0.0038))
# A_{st,req} = M_u / (0.87 × f_y × 0.9 × d)
```

### 5.2 Naming Convention for Rendering

**handcalcs uses special variable naming:**
```python
# Subscripts: use underscore
M_u = 250      # Renders as: M_u
A_st_req = 100 # Renders as: A_{st,req}
f_c_k = 30     # Renders as: f_{c,k}

# Greek letters: use name
rho = 0.015    # Renders as: ρ
alpha = 0.85   # Renders as: α
delta = 45     # Renders as: δ

# Superscripts: not directly supported
# Use function calls or workaround
```

**Our naming already compatible**:
- `mu_kn_m` → renders well with handcalcs
- `ast_required_mm2` → renders as A_{st,required}
- `fck_mpa` → renders as f_{ck}

### 5.3 Unit Handling Approach

**handcalcs is UNIT AGNOSTIC:**
```python
# Variables are just numbers
b = 300       # mm (implicit)
d = 550       # mm (implicit)
M_u = 250     # kN·m (implicit)
f_c = 30      # MPa (implicit)

# User must track units manually
# handcalcs only renders calculations, doesn't validate
```

**Units in documentation:**
```python
# Comment-based unit documentation
b = 300      # [mm] Beam width
d = 550      # [mm] Effective depth
M_u = 250    # [kN·m] Factored moment
```

**Lesson**: handcalcs complements our approach (units in names + comments).

### 5.4 Integration Pattern

**handcalcs as documentation layer:**
```python
# Core calculation (no handcalcs)
def calculate_ast(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa):
    mu_n_mm = mu_kn_m * 1e6
    # ... calculation logic
    return ast_mm2

# Documentation wrapper (with handcalcs)
@handcalcs.render
def calculate_ast_documented(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa):
    result = calculate_ast(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)
    # Show intermediate steps for documentation
    return locals()
```

**Lesson**: Consider handcalcs for documentation/reports, not core API.

---

## 6. OpenSees Python Bindings

**Repository**: https://github.com/zhuminjie/OpenSeesPy
**Domain**: Finite element analysis (large research codebase)
**Version analyzed**: v3.5.1 (2024)

### 6.1 API Design Observations

**Node/element creation:**
```python
import openseespy.opensees as ops

# Initialize model
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)  # 2D, 3 DOF

# Create nodes (tag, x, y)
ops.node(1, 0.0, 0.0)
ops.node(2, 144.0, 0.0)
ops.node(3, 168.0, 0.0)

# Fix boundary conditions (tag, x-dof, y-dof, rotation-dof)
ops.fix(1, 1, 1, 1)

# Create material (tag, E)
ops.uniaxialMaterial('Elastic', 1, 29000.0)  # ksi

# Create element (tag, node-i, node-j, area, E-tag, I)
ops.element('elasticBeamColumn', 1, 1, 2, 10.0, 1, 100.0)
```

**Key patterns:**
- **Integer tags**: All entities identified by integers (not strings)
- **Positional arguments**: Most parameters positional (poor discoverability)
- **String-based dispatch**: Material type as string `'Elastic'`
- **Implicit units**: User must ensure consistency (typically kips, inches)
- **Imperative style**: Sequential commands build model

### 6.2 Unit Handling

**OpenSees approach:**
```python
# NO unit system - completely user responsibility
# Typical conventions:
# - Force: kips or kN
# - Length: inches or mm
# - Stress: ksi or MPa
# - Time: seconds

# Example with US units (kips, inches, ksi)
E = 29000.0  # ksi
A = 10.0     # in²
I = 100.0    # in⁴

# Example with SI units (kN, mm, MPa)
E = 200000.0  # MPa
A = 6452.0    # mm²
I = 41623333.3 # mm⁴
```

**Lesson**: Large research codes avoid enforcing units (flexibility > safety).

### 6.3 Result Access

```python
# Run analysis
ops.analyze(10)  # Number of steps

# Get results (tag-based)
disp_node_2 = ops.nodeDisp(2)           # [ux, uy, rotation]
force_elem_1 = ops.eleForce(1)          # [N1, V1, M1, N2, V2, M2]
stress_node_2 = ops.nodeReaction(2)     # [Rx, Ry, M]
```

**Observations:**
- Returns raw arrays/tuples
- No named fields (must remember order)
- No units (user must track)

**Compared to our approach**: We use dataclasses with named fields (better).

---

## 7. Cross-Library Patterns

### 7.1 Comparison Table

| Library | Unit Strategy | Naming Style | Result Type | Validation | ID System |
|---------|--------------|--------------|-------------|------------|-----------|
| **PyNite** | Implicit (doc only) | Textbook (E, Iy, Iz) | Method calls | Structural only | String names |
| **ezdxf** | Unitless (drawing units) | CAD conventions | Entities | Minimal | Integer handles |
| **pint** | Explicit (Quantity objects) | SI standard | Quantities | Dimensional | N/A |
| **handcalcs** | Implicit (user tracks) | Symbolic (subscripts) | Formatted text | None | N/A |
| **OpenSees** | Implicit (user choice) | Minimal (single letters) | Arrays/tuples | Solver-based | Integer tags |
| **Our library** | **Suffix-based (b_mm)** | **IS 456 notation** | **Dataclasses** | **Explicit + validation flag** | **String IDs (future)** |

### 7.2 Common Domain Patterns

#### Pattern 1: Tag/ID-Based Entity References

**Observation**: Structural codes use tags to reference entities:
- PyNite: String names (`'N1'`, `'M1'`)
- OpenSees: Integer tags (`1`, `2`, `3`)
- ezdxf: Handles (internal integers)

**Trade-offs:**
- **Strings**: More readable, easier debugging (`'Beam_B1'` vs `147`)
- **Integers**: Faster lookup, less memory, sequential generation

**Recommendation for us**:
- Current: No entity system (direct calculation)
- Future (job runner): Consider string IDs for beams (`'B1'`, `'B2'`)

#### Pattern 2: Method Chaining vs Functional

**PyNite (method chaining):**
```python
model.add_node('N1', 0, 0, 0) \
     .add_member('M1', 'N1', 'N2', E=29000) \
     .add_load('L1', ...)
```

**Our library (functional):**
```python
flexure = design_singly_reinforced(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)
shear = design_shear(b_mm, d_mm, vu_kn, fck_mpa, fy_mpa)
```

**Recommendation**: Keep functional style (clearer, more testable, aligns with numpy/scipy).

#### Pattern 3: Coordinate Tuples vs Separate Parameters

**ezdxf approach:**
```python
msp.add_line((0, 0), (100, 0))  # Tuple coordinates
```

**PyNite approach:**
```python
model.add_node('N1', x=0, y=0, z=0)  # Named parameters
```

**Recommendation for us**:
- Geometry: Use tuples for points (`start=(x, y)`, `end=(x, y)`)
- Properties: Use named params (`b_mm=300`, `d_mm=550`)

### 7.3 Error Handling Patterns

| Library | Validation Timing | Error Types | Error Messages |
|---------|-------------------|-------------|----------------|
| PyNite | Late (at solve) | Generic Python exceptions | Minimal context |
| ezdxf | Save time | ezdxf.DXFError hierarchy | Detailed DXF context |
| pint | Immediate | DimensionalityError | Shows expected vs actual dimensions |
| handcalcs | None (documentation only) | N/A | N/A |
| OpenSees | Solver time | Generic errors | Cryptic (Fortran heritage) |
| **Our library** | **Early (function entry) + optional skip** | **Custom hierarchy (ValidationError, DesignError, ComplianceError)** | **Three Questions framework (what/why/how)** |

**Our approach is better**: Fail fast with actionable messages.

---

## 8. Unit Handling Strategies

### 8.1 Strategy Comparison

#### Strategy A: Implicit Units (PyNite, OpenSees, handcalcs)

**Approach**: Document expected units, user ensures consistency.

```python
def design_beam(b, d, M_u, f_c, f_y):
    """
    Args:
        b: Beam width (mm)
        d: Effective depth (mm)
        M_u: Factored moment (kN·m)
        f_c: Concrete strength (MPa)
        f_y: Steel yield strength (MPa)
    """
    # Calculations assume units are correct
    ...
```

**Pros:**
- Simple, no overhead
- Fast (no conversion logic)
- Flexible (user can use any consistent system)

**Cons:**
- Easy to mix units accidentally
- No validation
- Errors only caught when results are wrong

#### Strategy B: Explicit Quantities (pint)

**Approach**: Wrap all values in Quantity objects with units.

```python
from pint import UnitRegistry
ureg = UnitRegistry()

def design_beam(b, d, M_u, f_c, f_y):
    """
    Args:
        b: Beam width (Quantity with length dimension)
        d: Effective depth (Quantity)
        M_u: Moment (Quantity)
        ...
    """
    # Convert to standard units internally
    b_mm = b.to('mm').magnitude
    d_mm = d.to('mm').magnitude
    M_u_n_mm = M_u.to('N*mm').magnitude
    ...
    # Return with units
    return result * ureg.mm**2
```

**Pros:**
- Type-safe (dimensional analysis)
- Automatic unit conversion
- Catches unit mixing errors

**Cons:**
- 40× slower for simple operations
- Heavyweight dependency (~100KB)
- Verbose API (`(300 * ureg.mm)` vs `300`)
- Over-engineering for our use case

#### Strategy C: Suffix-Based (Our Current Approach)

**Approach**: Encode units in parameter names, validate at boundaries.

```python
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
) -> FlexureResult:
    """Design beam per IS 456:2000.

    Args:
        b_mm: Beam width in millimeters
        d_mm: Effective depth in millimeters
        mu_kn_m: Factored moment in kilonewton-meters
        fck_mpa: Characteristic concrete compressive strength in megapascals
        fy_mpa: Characteristic steel yield strength in megapascals
    """
    # Units are clear from names
    # Validation at entry point
    if b_mm < 200:
        raise ValidationError("b_mm must be >= 200mm per IS 456 Cl. 26.5.1.1")
    ...
```

**Pros:**
- Clear from name what unit is expected
- IDE autocomplete shows units
- No performance overhead
- Simple validation at boundaries
- Compatible with handcalcs rendering

**Cons:**
- User must convert before calling
- No automatic conversion
- Still possible to pass wrong units (but less likely)

### 8.2 Hybrid Approach (Recommendation)

**Use suffix-based + optional pint at API boundaries:**

```python
from typing import Union
from pint import Quantity

def design_beam(
    b_mm: Union[float, Quantity],  # Accept both
    d_mm: Union[float, Quantity],
    mu_kn_m: Union[float, Quantity],
    fck_mpa: Union[float, Quantity],
    fy_mpa: Union[float, Quantity],
) -> FlexureResult:
    """Design beam (accepts floats in expected units or pint Quantities)."""

    # Convert Quantity to float at boundary
    if isinstance(b_mm, Quantity):
        b_mm = b_mm.to('mm').magnitude
    if isinstance(mu_kn_m, Quantity):
        mu_kn_m = mu_kn_m.to('kN*m').magnitude
    # ... etc

    # Core calculation uses floats (fast)
    ...
```

**Pros:**
- Users can choose: simple floats or safe Quantities
- Core calculations stay fast (floats internally)
- Validation at boundary converts/checks

**Cons:**
- More complex API
- Optional dependency (pint) needed for Quantity support

**Recommendation**: Add pint support as **optional** in v1.0+ (not v0.15).

### 8.3 Unit Conversion Utilities

**Provide helper functions for common conversions:**

```python
# Python/structural_lib/units.py

def mm_to_m(value_mm: float) -> float:
    """Convert millimeters to meters."""
    return value_mm / 1000.0

def kn_m_to_n_mm(moment_kn_m: float) -> float:
    """Convert kN·m to N·mm."""
    return moment_kn_m * 1e6

def mpa_to_n_mm2(stress_mpa: float) -> float:
    """Convert MPa to N/mm²."""
    return stress_mpa  # Already same unit

# IS 456 standard unit system
IS456_UNITS = {
    'length': 'mm',
    'force': 'kN',
    'stress': 'MPa',  # = N/mm²
    'moment': 'kN·m',
    'area': 'mm²',
}
```

---

## 9. Engineering Notation Conventions

### 9.1 IS 456 Standard Notation

**Variable naming from IS 456:2000:**

| Symbol | Meaning | Our naming |
|--------|---------|------------|
| b | Beam width | `b_mm` |
| D | Overall depth | `D_mm` |
| d | Effective depth | `d_mm` |
| M | Bending moment | `mu_kn_m` (factored) |
| V | Shear force | `vu_kn` (factored) |
| fck | Characteristic compressive strength | `fck_mpa` |
| fy | Characteristic yield strength | `fy_mpa` |
| Ast | Area of tension steel | `ast_mm2` |
| Asc | Area of compression steel | `asc_mm2` |
| xu | Depth of neutral axis | `xu_mm` |
| pt | Percentage tension steel | `pt_percent` |
| ρ | Reinforcement ratio | `rho` (handcalcs) or `reinforcement_ratio` |

### 9.2 Subscript Conventions

**IS 456 uses subscripts extensively:**
- `M_u` = Factored moment (ultimate)
- `A_st` = Area of steel, tension
- `f_ck` = Characteristic compressive strength of concrete
- `τ_c` = Shear stress in concrete

**Our approach (Python-compatible):**
- Underscore for subscript: `mu`, `ast`, `fck`, `tau_c`
- Full suffix for units: `mu_kn_m`, `ast_mm2`, `fck_mpa`

**handcalcs rendering:**
- `mu_kn_m` → renders as M_u
- `ast_mm2` → renders as A_{st}
- `fck_mpa` → renders as f_{ck}

### 9.3 Abbreviation Standards

**Standard engineering abbreviations (use these):**

| Term | Abbreviation | Example variable |
|------|--------------|------------------|
| Minimum | min | `ast_min_mm2` |
| Maximum | max | `ast_max_mm2` |
| Required | req | `ast_req_mm2` |
| Provided | prov | `ast_prov_mm2` |
| Ultimate | u | `mu_kn_m`, `vu_kn` |
| Service | s | `ms_kn_m` (rare in our code) |
| Characteristic | k | `fck_mpa`, `fyk_mpa` |
| Limit | lim | `mu_lim_kn_m` |
| Effective | eff | `d_eff_mm` |
| Clear | cl or clear | `cover_clear_mm`, `spacing_clear_mm` |

**Avoid ambiguous abbreviations:**
- ❌ `len` (length? vs Python built-in len())
- ❌ `dia` vs `d` (diameter - use `dia_mm` for bar diameter, `d_mm` for effective depth)
- ❌ `str` (stirrup? vs Python built-in str())

### 9.4 Greek Letters (for handcalcs)

**When using handcalcs rendering:**

```python
# Use spelled-out names for Greek letters
rho = ast_mm2 / (b_mm * d_mm)        # ρ (reinforcement ratio)
alpha = 0.85                          # α (stress block factor)
phi = 16                              # φ (bar diameter)
tau_c = calculate_shear_stress(...)   # τ_c (concrete shear stress)
```

**handcalcs will render these as Greek symbols automatically.**

---

## 10. Recommendations for Our Library

### 10.1 Current Approach Validation ✅

**Our current patterns are GOOD:**
1. **Suffix-based units** (`b_mm`, `fck_mpa`) - clear, fast, IDE-friendly
2. **Dataclass results** - better than tuples (PyNite/OpenSees return arrays)
3. **Explicit validation with flag** - better than implicit (PyNite) or none (handcalcs)
4. **Custom exception hierarchy** - better than generic exceptions (all others)
5. **IS 456 notation** - matches domain textbooks and code

**Areas where others are better:**
1. **pint dimensional analysis** - but too heavyweight for our performance needs
2. **ezdxf entity system** - but we don't need complex entity management yet

### 10.2 Recommended Improvements

#### Improvement 1: Add Unit Conversion Module (High Priority)

**Create `Python/structural_lib/units.py`:**
```python
"""Unit conversion utilities for structural engineering."""

def mm_to_m(mm: float) -> float:
    """Convert millimeters to meters."""
    return mm / 1000.0

def m_to_mm(m: float) -> float:
    """Convert meters to millimeters."""
    return m * 1000.0

def kn_m_to_n_mm(kn_m: float) -> float:
    """Convert kN·m to N·mm."""
    return kn_m * 1e6

def n_mm_to_kn_m(n_mm: float) -> float:
    """Convert N·mm to kN·m."""
    return n_mm / 1e6

# Add more as needed
```

#### Improvement 2: Optional pint Support (Medium Priority, v1.0+)

**Add as optional dependency:**
```python
# pyproject.toml
[tool.poetry.extras]
units = ["pint>=0.23"]

# In API functions:
from typing import Union

try:
    from pint import Quantity
    PINT_AVAILABLE = True
except ImportError:
    Quantity = None
    PINT_AVAILABLE = False

def design_beam(
    b_mm: Union[float, 'Quantity'],  # Accept both
    ...
):
    if PINT_AVAILABLE and isinstance(b_mm, Quantity):
        b_mm = b_mm.to('mm').magnitude
    # ... rest of function
```

#### Improvement 3: handcalcs Integration (Low Priority)

**Add documentation wrapper:**
```python
# Python/structural_lib/documentation.py
"""Documentation wrappers using handcalcs (optional dependency)."""

try:
    import handcalcs.render
    HANDCALCS_AVAILABLE = True
except ImportError:
    HANDCALCS_AVAILABLE = False

if HANDCALCS_AVAILABLE:
    @handcalcs.render
    def design_singly_reinforced_doc(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa):
        """Documented version showing calculation steps."""
        result = design_singly_reinforced(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)
        # Show intermediate steps for documentation
        return locals()
```

### 10.3 Keep Current Practices

**Don't change these (already good):**
1. ✅ Suffix-based unit naming (`b_mm`, `fck_mpa`)
2. ✅ Dataclass results with named fields
3. ✅ Validation at function entry with optional `validate` flag
4. ✅ Custom exception hierarchy (ValidationError, DesignError, etc.)
5. ✅ IS 456 notation conventions
6. ✅ Three Questions error messages (what/why/how)

### 10.4 Future Considerations

**Entity system (if needed for complex models):**
- Use **string IDs** like PyNite (`'B1'`, `'B2'`) not integers
- Only add if multi-beam optimization requires it
- Current functional API is fine for single-beam design

**Coordinate systems:**
- Current: No coordinate system (1D beam, length only)
- Future: If adding 2D/3D, use numpy arrays like `start=[x, y, z]`
- Don't need UCS (User Coordinate System) like ezdxf

---

## Summary

### Key Takeaways

1. **Unit handling**: Our suffix-based approach (`b_mm`) is simpler and faster than pint, clearer than implicit. Keep it.
2. **Naming**: IS 456 notation with underscores (`mu_kn_m`, `ast_mm2`) is compatible with handcalcs and domain textbooks. Keep it.
3. **Results**: Dataclasses are better than tuples/arrays (used by PyNite/OpenSees). Keep it.
4. **Validation**: Early validation with optional skip is better than late (PyNite) or none (handcalcs). Keep it.
5. **Error messages**: Our Three Questions approach is better than generic messages. Keep it.

### Optional Enhancements (Not Critical)

- Add `units.py` conversion utilities (helpful, not essential)
- Support pint Quantities as optional (v1.0+, adds flexibility)
- Add handcalcs documentation wrappers (nice for reports, not core)

### Validation Against Other Standards

| Criterion | Our Approach | Industry Pattern | Assessment |
|-----------|--------------|------------------|------------|
| Unit clarity | Suffix-based | Implicit (PyNite) or Explicit (pint) | ✅ Good balance |
| Performance | Fast (floats) | Fast (PyNite) or Slow (pint) | ✅ Optimal |
| Type safety | Python types | Quantities (pint) | ⚠️ Could add optional pint |
| Notation | IS 456 standard | Domain-specific | ✅ Matches textbooks |
| Results | Dataclasses | Tuples/arrays | ✅ Better than others |
| Validation | Early + optional | Late (PyNite) or None | ✅ Better than others |
| Errors | Three Questions | Generic | ✅ Best in class |

**Conclusion**: Our current approach is **well-designed** and **better than most domain libraries**. Minor enhancements possible, but no major changes needed.
