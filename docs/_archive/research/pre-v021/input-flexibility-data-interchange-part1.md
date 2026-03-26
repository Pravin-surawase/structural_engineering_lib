# Input Flexibility & Data Interchange

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** In Progress (Part 1/3)
**Task:** TASK-238
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Current API requires verbose dict construction for every function call, creating poor developer experience (Colab review: C- rating). Users must manually create dictionaries with 6-12 parameters, leading to repetition and errors.

**Goal:** Research flexible input patterns that allow:
1. Multiple input formats (dict, dataclass, spreadsheet, ETABS export)
2. Progressive disclosure (simple → advanced)
3. Type-safe but convenient
4. IDE autocomplete friendly

**Key Finding:** Modern libraries use polymorphic constructors + builder patterns + smart defaults. Combination of typed input objects + convenience functions provides best UX.

**Recommendation:**
- Phase 1: Add typed input classes (BeamInput, SectionInput) - 8-10 hours
- Phase 2: Add convenience constructors (from_dict, from_excel, from_etabs) - 12-15 hours
- Phase 3: Add builder pattern for complex cases - 6-8 hours

---

## Table of Contents

1. [Problem Statement & Current Pain Points](#1-problem-statement--current-pain-points)
2. [Industry Patterns Analysis](#2-industry-patterns-analysis)
3. [Input Pattern Strategies](#3-input-pattern-strategies)
4. [Data Interchange Formats](#4-data-interchange-formats)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Examples & Code Patterns](#6-examples--code-patterns)
7. [Migration Strategy](#7-migration-strategy)
8. [Recommendations](#8-recommendations)

---

## 1. Problem Statement & Current Pain Points

### 1.1 Current API Pain Points

**Issue 1: Verbose Dictionary Construction**

Current approach from Colab review:
```python
# User must create dict manually for EVERY beam
beam_data = {
    'span_mm': 5000,
    'width_mm': 230,
    'depth_mm': 450,
    'fck_mpa': 25,
    'fy_mpa': 415,
    'cover_mm': 25,
    'moment_knm': 120,
    'shear_kn': 85,
}

result = design_beam_is456(beam_data)
```

**Problems:**
- ❌ No IDE autocomplete for dict keys
- ❌ Typos in keys cause runtime errors
- ❌ No type checking until runtime
- ❌ Must remember exact key names
- ❌ Must repeat units in every key
- ❌ No validation until function call

**Issue 2: Repetitive Parameter Passing**

For multiple similar beams:
```python
# Repetitive and error-prone
beam1 = {'span_mm': 5000, 'width_mm': 230, 'depth_mm': 450, ...}
beam2 = {'span_mm': 6000, 'width_mm': 230, 'depth_mm': 450, ...}  # Copy-paste
beam3 = {'span_mm': 7000, 'width_mm': 230, 'depth_mm': 450, ...}  # More copy-paste
```

**Issue 3: No Data Import Helpers**

Real-world data comes from:
- ETABS table exports (Excel)
- Spreadsheet calculations
- CAD schedules
- BIM models

Current workflow:
```python
# User must manually parse Excel → dict
df = pd.read_excel('beams.xlsx')
for row in df.iterrows():
    beam_data = {
        'span_mm': row['Span'],
        'width_mm': row['Width'],
        # ... manual mapping for 10+ fields
    }
```

### 1.2 User Experience Impact

**From Colab Notebook Review:**
- **Rating:** C- (Poor)
- **Feedback:** "Too much boilerplate, feels like assembly language"
- **Improvement Potential:** C- → B+ with better input flexibility

**Desired UX:**
```python
# Simple case: positional args
result = design_beam(span=5000, width=230, depth=450, moment=120)

# Excel import: one-liner
beams = BeamInput.from_excel('schedule.xlsx')
results = [design_beam(b) for b in beams]

# ETABS export: direct import
beams = BeamInput.from_etabs('model.json')
```

---

## 2. Industry Patterns Analysis

### 2.1 NumPy/Pandas Pattern: Multiple Constructors

**NumPy Array Creation:**
```python
# Multiple ways to create arrays
arr1 = np.array([1, 2, 3])              # From list
arr2 = np.zeros((3, 3))                 # Zeros
arr3 = np.arange(0, 10, 2)              # Range
arr4 = np.linspace(0, 1, 100)           # Linear space
arr5 = np.random.randn(5, 5)            # Random
arr6 = np.loadtxt('data.txt')           # From file
```

**Pandas DataFrame Creation:**
```python
# Multiple constructors
df1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})  # From dict
df2 = pd.read_csv('data.csv')                          # From CSV
df3 = pd.read_excel('data.xlsx')                       # From Excel
df4 = pd.read_sql(query, connection)                   # From SQL
df5 = pd.DataFrame(numpy_array)                        # From array
```

**Lesson:** Provide multiple constructors for different data sources.

### 2.2 Requests Pattern: Flexible Arguments

**Requests Library:**
```python
# Simple: positional
response = requests.get('https://api.example.com')

# With params: dict
response = requests.get('https://api.example.com', params={'key': 'value'})

# With headers: dict
response = requests.get(url, headers={'Authorization': 'Bearer token'})

# Combined: kwargs
response = requests.get(
    url,
    params={'key': 'value'},
    headers={'Auth': 'token'},
    timeout=30,
    verify=True
)
```

**Lesson:** Use kwargs for optional parameters, allow dict or explicit args.

### 2.3 PyNite Pattern: Object-Oriented Input

**PyNite (Structural Analysis):**
```python
from PyNite import FEModel3D

# Create model
model = FEModel3D()

# Add nodes (object-based)
model.add_node('N1', 0, 0, 0)
model.add_node('N2', 5000, 0, 0)

# Add members (object-based)
model.add_member('M1', 'N1', 'N2', E=200000, G=80000, Iy=1e8, Iz=1e8, J=1e6, A=5000)

# Or from dict
model.add_member_from_dict({
    'name': 'M1',
    'i_node': 'N1',
    'j_node': 'N2',
    'material': {'E': 200000, 'G': 80000},
    'section': {'A': 5000, 'Iy': 1e8}
})
```

**Lesson:** Support both object-oriented and dict-based input.

### 2.4 ezdxf Pattern: Builder Classes

**ezdxf (CAD Library):**
```python
import ezdxf

# Create drawing
doc = ezdxf.new()
msp = doc.modelspace()

# Builder pattern for complex entities
msp.add_line((0, 0), (100, 0))
msp.add_circle((50, 50), radius=25)

# Or use entity builder
circle = msp.add_circle((50, 50), radius=25)
circle.dxf.color = 1
circle.dxf.layer = 'Dimensions'
```

**Lesson:** Use builder pattern for complex configurations.

### 2.5 Pint Pattern: Unit Handling

**Pint (Units Library):**
```python
from pint import UnitRegistry
ureg = UnitRegistry()

# Explicit units
length = 5 * ureg.meter
force = 100 * ureg.kN

# Conversion
length_mm = length.to(ureg.mm)  # 5000 mm

# Calculations preserve units
stress = force / (length ** 2)  # kN/m²
```

**Lesson:** Consider unit-aware inputs (future enhancement).

---

## 3. Input Pattern Strategies

### 3.1 Strategy 1: Typed Input Classes (Dataclasses)

**Approach:** Define typed input classes using Python dataclasses.

**Benefits:**
- ✅ IDE autocomplete
- ✅ Type checking (mypy)
- ✅ Validation in __post_init__
- ✅ Self-documenting
- ✅ Immutable (frozen=True)

**Example:**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class BeamInput:
    """
    Input parameters for beam design.

    Attributes:
        span_mm: Beam span in millimeters (typical: 3000-10000)
        width_mm: Beam width in millimeters (typical: 200-600)
        depth_mm: Effective depth in millimeters (typical: 300-1200)
        moment_knm: Factored moment in kilonewton-meters
        shear_kn: Factored shear in kilonewtons
        fck_mpa: Concrete grade in N/mm² (20, 25, 30, 35, 40)
        fy_mpa: Steel grade in N/mm² (415, 500, 550)
        cover_mm: Clear cover in millimeters (default: 25)
        exposure: Exposure condition per Table 16
    """
    span_mm: float
    width_mm: float
    depth_mm: float
    moment_knm: float
    shear_kn: float
    fck_mpa: Literal[20, 25, 30, 35, 40] = 25
    fy_mpa: Literal[415, 500, 550] = 415
    cover_mm: float = 25
    exposure: Literal['mild', 'moderate', 'severe', 'very_severe'] = 'moderate'

    def __post_init__(self):
        """Validate inputs."""
        if self.span_mm <= 0:
            raise ValueError("span_mm must be positive")
        if self.width_mm <= 0:
            raise ValueError("width_mm must be positive")
        # ... more validation
```

**Usage:**
```python
# IDE autocomplete works!
beam = BeamInput(
    span_mm=5000,
    width_mm=230,
    depth_mm=450,
    moment_knm=120,
    shear_kn=85,
)

result = design_beam(beam)
```

**Pros:**
- ✅ Type-safe
- ✅ IDE friendly
- ✅ Validation at creation
- ✅ Immutable

**Cons:**
- ❌ More verbose than kwargs
- ❌ Requires import

### 3.2 Strategy 2: Flexible Function Signatures

**Approach:** Accept multiple input formats in function signature.

**Pattern 1: Union Types**
```python
from typing import Union

def design_beam(
    beam: Union[BeamInput, dict]
) -> BeamDesignResult:
    """
    Design beam accepting multiple input formats.

    Args:
        beam: BeamInput object OR dict with keys:
            span_mm, width_mm, depth_mm, moment_knm, etc.
    """
    if isinstance(beam, dict):
        beam = BeamInput(**beam)  # Convert dict → BeamInput

    # Design logic uses beam.span_mm, beam.width_mm, etc.
    ...
```

**Usage:**
```python
# Dict input (backward compatible)
result = design_beam({'span_mm': 5000, 'width_mm': 230, ...})

# Object input (new, type-safe)
beam = BeamInput(span_mm=5000, width_mm=230, ...)
result = design_beam(beam)
```

**Pattern 2: Overloaded Signatures**
```python
from typing import overload

@overload
def design_beam(
    *,
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    moment_knm: float,
    shear_kn: float,
    fck_mpa: float = 25,
    fy_mpa: float = 415,
) -> BeamDesignResult: ...

@overload
def design_beam(beam: BeamInput) -> BeamDesignResult: ...

@overload
def design_beam(beam: dict) -> BeamDesignResult: ...

def design_beam(beam=None, **kwargs) -> BeamDesignResult:
    """Design beam with flexible input."""
    if beam is None:
        # Called with kwargs
        beam = BeamInput(**kwargs)
    elif isinstance(beam, dict):
        beam = BeamInput(**beam)
    elif not isinstance(beam, BeamInput):
        raise TypeError("Expected BeamInput, dict, or kwargs")

    # Design logic
    ...
```

**Usage:**
```python
# Kwargs (most convenient for simple cases)
result = design_beam(
    span_mm=5000,
    width_mm=230,
    depth_mm=450,
    moment_knm=120,
    shear_kn=85
)

# Object (best for complex cases)
beam = BeamInput(...)
result = design_beam(beam)

# Dict (backward compatible)
result = design_beam({'span_mm': 5000, ...})
```

---

## 4. Data Interchange Formats

### 4.1 Excel Import Pattern

**Goal:** Import beam data from Excel spreadsheet.

**Excel Format:**
| Beam ID | Span (mm) | Width (mm) | Depth (mm) | Moment (kN·m) | Shear (kN) | fck | fy |
|---------|-----------|------------|------------|---------------|------------|-----|-----|
| B1      | 5000      | 230        | 450        | 120           | 85         | 25  | 415 |
| B2      | 6000      | 300        | 500        | 180           | 110        | 30  | 415 |

**Implementation:**
```python
@classmethod
def from_excel(
    cls,
    file_path: str,
    sheet_name: str = 'Beams',
    column_mapping: Optional[dict] = None
) -> list[BeamInput]:
    """
    Import beams from Excel file.

    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name (default: 'Beams')
        column_mapping: Custom column mapping (optional)
            If None, uses default mapping:
            {'Span (mm)': 'span_mm', 'Width (mm)': 'width_mm', ...}

    Returns:
        List of BeamInput objects

    Example:
        >>> beams = BeamInput.from_excel('schedule.xlsx')
        >>> for beam in beams:
        ...     result = design_beam(beam)
    """
    import pandas as pd

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Default column mapping
    if column_mapping is None:
        column_mapping = {
            'Span (mm)': 'span_mm',
            'Width (mm)': 'width_mm',
            'Depth (mm)': 'depth_mm',
            'Moment (kN·m)': 'moment_knm',
            'Shear (kN)': 'shear_kn',
            'fck': 'fck_mpa',
            'fy': 'fy_mpa',
        }

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Convert rows to BeamInput objects
    beams = []
    for _, row in df.iterrows():
        beam = cls(**row.to_dict())
        beams.append(beam)

    return beams
```

**Usage:**
```python
# Simple import
beams = BeamInput.from_excel('beam_schedule.xlsx')
results = [design_beam(b) for b in beams]

# Custom column names
beams = BeamInput.from_excel(
    'my_schedule.xlsx',
    column_mapping={
        'L': 'span_mm',
        'b': 'width_mm',
        'd': 'depth_mm',
    }
)
```

### 4.2 ETABS Export Pattern

**Goal:** Import beam data from ETABS table export.

**ETABS JSON Format:**
```json
{
  "model": "Building_01",
  "beams": [
    {
      "Name": "B1",
      "Story": "Story1",
      "Length": 5000,
      "Section": "230x450",
      "Material": "M25",
      "Rebar": "Fe415",
      "Moment22": 120.5,
      "Shear2": 85.2
    }
  ]
}
```

**Implementation:**
```python
@classmethod
def from_etabs_json(
    cls,
    file_path: str,
    unit_conversion: Optional[dict] = None
) -> list[BeamInput]:
    """
    Import beams from ETABS JSON export.

    Args:
        file_path: Path to ETABS JSON file
        unit_conversion: Unit conversion factors (optional)
            Default: assumes ETABS exports in mm, kN

    Returns:
        List of BeamInput objects

    Example:
        >>> beams = BeamInput.from_etabs_json('etabs_export.json')
    """
    import json

    with open(file_path) as f:
        data = json.load(f)

    beams = []
    for beam_data in data['beams']:
        # Parse section "230x450" → width=230, depth=450
        section = beam_data['Section']
        width, depth = map(float, section.split('x'))

        # Parse material "M25" → fck=25
        material = beam_data['Material']
        fck = float(material.replace('M', ''))

        # Parse rebar "Fe415" → fy=415
        rebar = beam_data['Rebar']
        fy = float(rebar.replace('Fe', ''))

        beam = cls(
            span_mm=beam_data['Length'],
            width_mm=width,
            depth_mm=depth,
            moment_knm=beam_data['Moment22'],
            shear_kn=beam_data['Shear2'],
            fck_mpa=fck,
            fy_mpa=fy,
        )
        beams.append(beam)

    return beams
```

---

**(Part 1/3 complete - continuing in next file)**
