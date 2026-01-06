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

*(To be added in Step 2)*

---

## 8. Unit Handling Strategies

*(To be added in Step 2)*

---

## 9. Engineering Notation Conventions

*(To be added in Step 2)*

---

## 10. Recommendations for Our Library

*(To be added in Step 2)*
