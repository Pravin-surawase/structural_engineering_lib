# Input Flexibility & Data Interchange - Part 2/3

**(Continued from part1.md)**

## 4. Data Interchange Formats (Continued)

### 4.3 CSV Import Pattern

**Goal:** Import from simple CSV file (common for spreadsheet exports).

**CSV Format:**
```csv
span_mm,width_mm,depth_mm,moment_knm,shear_kn,fck_mpa,fy_mpa
5000,230,450,120,85,25,415
6000,300,500,180,110,30,415
```

**Implementation:**
```python
@classmethod
def from_csv(
    cls,
    file_path: str,
    **kwargs
) -> list[BeamInput]:
    """
    Import beams from CSV file.

    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments passed to pandas.read_csv

    Returns:
        List of BeamInput objects

    Example:
        >>> beams = BeamInput.from_csv('beams.csv')
    """
    import pandas as pd

    df = pd.read_csv(file_path, **kwargs)
    return [cls(**row.to_dict()) for _, row in df.iterrows()]
```

### 4.4 JSON Import/Export Pattern

**Goal:** Full serialization for API integration or storage.

**JSON Format:**
```json
{
  "beams": [
    {
      "span_mm": 5000,
      "width_mm": 230,
      "depth_mm": 450,
      "moment_knm": 120,
      "shear_kn": 85,
      "fck_mpa": 25,
      "fy_mpa": 415,
      "cover_mm": 25,
      "exposure": "moderate"
    }
  ]
}
```

**Implementation:**
```python
@classmethod
def from_json(cls, file_path: str) -> list[BeamInput]:
    """Import beams from JSON file."""
    import json
    with open(file_path) as f:
        data = json.load(f)
    return [cls(**beam_data) for beam_data in data['beams']]

def to_json(self) -> dict:
    """Export to JSON-serializable dict."""
    from dataclasses import asdict
    return asdict(self)
```

---

## 5. Builder Pattern for Complex Cases

### 5.1 Builder Pattern Motivation

**Problem:** Some beams have complex configurations that require many optional parameters.

**Example Complex Case:**
```python
# Too many parameters!
beam = BeamInput(
    span_mm=8000,
    width_mm=300,
    depth_mm=600,
    moment_knm=250,
    shear_kn=150,
    fck_mpa=30,
    fy_mpa=500,
    cover_mm=40,
    exposure='severe',
    # Optional detailing params
    top_bars=[25, 25, 20],
    bottom_bars=[25, 25, 25, 20],
    stirrup_dia=10,
    stirrup_spacing=150,
    # Optional loading
    distributed_load_kn_per_m=15,
    point_loads=[(2000, 50), (6000, 50)],
    # Optional support conditions
    left_support='fixed',
    right_support='pinned',
)
```

### 5.2 Builder Implementation

**Pattern:**
```python
class BeamBuilder:
    """
    Builder for complex beam configurations.

    Example:
        >>> beam = (BeamBuilder()
        ...     .span(8000)
        ...     .section(width=300, depth=600)
        ...     .concrete('M30')
        ...     .steel('Fe500')
        ...     .loading(moment=250, shear=150)
        ...     .cover(40, exposure='severe')
        ...     .build())
    """

    def __init__(self):
        self._data = {}

    def span(self, span_mm: float) -> 'BeamBuilder':
        """Set span in mm."""
        self._data['span_mm'] = span_mm
        return self

    def section(self, width: float, depth: float) -> 'BeamBuilder':
        """Set cross-section dimensions."""
        self._data['width_mm'] = width
        self._data['depth_mm'] = depth
        return self

    def concrete(self, grade: str) -> 'BeamBuilder':
        """Set concrete grade (e.g., 'M25', 'M30')."""
        self._data['fck_mpa'] = float(grade.replace('M', ''))
        return self

    def steel(self, grade: str) -> 'BeamBuilder':
        """Set steel grade (e.g., 'Fe415', 'Fe500')."""
        self._data['fy_mpa'] = float(grade.replace('Fe', ''))
        return self

    def loading(self, moment: float, shear: float) -> 'BeamBuilder':
        """Set factored loads."""
        self._data['moment_knm'] = moment
        self._data['shear_kn'] = shear
        return self

    def cover(
        self,
        cover_mm: float,
        exposure: str = 'moderate'
    ) -> 'BeamBuilder':
        """Set cover and exposure."""
        self._data['cover_mm'] = cover_mm
        self._data['exposure'] = exposure
        return self

    def build(self) -> BeamInput:
        """Build BeamInput object."""
        return BeamInput(**self._data)
```

**Usage:**
```python
# Fluent API - readable and self-documenting
beam = (BeamBuilder()
    .span(8000)
    .section(width=300, depth=600)
    .concrete('M30')
    .steel('Fe500')
    .loading(moment=250, shear=150)
    .cover(40, exposure='severe')
    .build())

result = design_beam(beam)
```

---

## 6. Smart Defaults & Progressive Disclosure

### 6.1 Smart Defaults Strategy

**Goal:** Reduce required inputs for common cases.

**Principle:** 80% of beams use standard values for many parameters.

**Common Defaults:**
```python
@dataclass(frozen=True)
class BeamInput:
    # Required (no good defaults)
    span_mm: float
    width_mm: float
    depth_mm: float
    moment_knm: float
    shear_kn: float

    # Common defaults (can be omitted)
    fck_mpa: Literal[20, 25, 30, 35, 40] = 25  # M25 most common
    fy_mpa: Literal[415, 500, 550] = 415      # Fe415 most common
    cover_mm: float = 25                       # Default per Table 16
    exposure: Literal['mild', 'moderate', 'severe', 'very_severe'] = 'moderate'
```

**Usage:**
```python
# Minimal input for simple case (5 required params)
beam = BeamInput(
    span_mm=5000,
    width_mm=230,
    depth_mm=450,
    moment_knm=120,
    shear_kn=85,
    # Uses defaults: M25, Fe415, 25mm cover, moderate exposure
)

# Override defaults when needed
beam_severe = BeamInput(
    span_mm=5000,
    width_mm=230,
    depth_mm=450,
    moment_knm=120,
    shear_kn=85,
    fck_mpa=30,              # Override: M30
    cover_mm=40,             # Override: 40mm
    exposure='severe',       # Override: severe
)
```

### 6.2 Progressive Disclosure Pattern

**Goal:** Show only relevant parameters based on context.

**Example: Singly vs Doubly Reinforced**

```python
class SinglelyReinforcedBeamInput(BeamInput):
    """Input for singly reinforced beam (no compression steel)."""
    pass  # Same as base

class DoublyReinforcedBeamInput(BeamInput):
    """Input for doubly reinforced beam."""
    asc_provided_mm2: Optional[float] = None  # Compression steel
    d_dash_mm: Optional[float] = None         # Cover to compression steel
```

**Usage:**
```python
# Simple case: no need to think about compression steel
beam = SinglelyReinforcedBeamInput(...)

# Complex case: explicitly provide compression steel params
beam = DoublyReinforcedBeamInput(
    ...,
    asc_provided_mm2=628,
    d_dash_mm=50,
)
```

---

## 7. Validation & Error Messages

### 7.1 Input Validation Strategy

**Goal:** Catch errors early with helpful messages.

**Implementation:**
```python
@dataclass(frozen=True)
class BeamInput:
    span_mm: float
    width_mm: float
    depth_mm: float
    moment_knm: float
    shear_kn: float
    fck_mpa: Literal[20, 25, 30, 35, 40] = 25
    fy_mpa: Literal[415, 500, 550] = 415
    cover_mm: float = 25

    def __post_init__(self):
        """Validate inputs with helpful error messages."""
        # Validation following Three Questions Framework

        # Check 1: Physical constraints
        if self.span_mm <= 0:
            raise ValueError(
                "Invalid span. "
                f"Reason: span_mm={self.span_mm} (must be positive). "
                "Solution: Provide positive span in millimeters (typical: 3000-10000)."
            )

        if self.width_mm <= 0:
            raise ValueError(
                "Invalid width. "
                f"Reason: width_mm={self.width_mm} (must be positive). "
                "Solution: Provide positive width in millimeters (typical: 200-600)."
            )

        # Check 2: Realistic ranges (warnings)
        if self.span_mm > 12000:
            import warnings
            warnings.warn(
                f"Large span detected: {self.span_mm} mm. "
                "Typical beams: 3000-10000 mm. "
                "Verify this is intentional.",
                UserWarning
            )

        # Check 3: Unit consistency
        if self.span_mm < 100:
            raise ValueError(
                "Span too small. "
                f"Reason: span_mm={self.span_mm} (unrealistic). "
                "Solution: Check units. Did you mean {self.span_mm * 1000} mm?"
            )
```

### 7.2 Cross-Parameter Validation

**Goal:** Validate relationships between parameters.

```python
def __post_init__(self):
    # ... individual validations

    # Cross-parameter checks
    if self.depth_mm < self.cover_mm + 25:
        raise ValueError(
            "Depth insufficient for cover. "
            f"Reason: depth={self.depth_mm} mm, cover={self.cover_mm} mm. "
            f"Solution: Increase depth to at least {self.cover_mm + 50} mm."
        )

    # Span/depth ratio check
    ratio = self.span_mm / self.depth_mm
    if ratio > 20:
        import warnings
        warnings.warn(
            f"Slender beam (L/d = {ratio:.1f}). "
            "Consider deflection carefully (IS 456 Cl. 23.2). "
            f"Suggestion: Increase depth to {self.span_mm / 15:.0f} mm.",
            UserWarning
        )
```

---

## 8. Implementation Roadmap

### 8.1 Phase 1: Core Input Classes (Week 1) - 8-10 hours

**Deliverables:**
- [ ] Create BeamInput dataclass
- [ ] Add validation in __post_init__
- [ ] Create SectionInput, MaterialInput classes
- [ ] Write unit tests
- [ ] Document with examples

**Success Criteria:**
- All common beam cases covered
- IDE autocomplete works
- Type checking passes (mypy)
- 95%+ test coverage

### 8.2 Phase 2: Import Helpers (Week 2) - 12-15 hours

**Deliverables:**
- [ ] Implement from_excel() classmethod
- [ ] Implement from_csv() classmethod
- [ ] Implement from_json() classmethod
- [ ] Implement from_etabs_json() classmethod
- [ ] Add column mapping support
- [ ] Write integration tests

**Success Criteria:**
- Can import from Excel/CSV/JSON
- Column mapping works
- Validation errors helpful
- Examples in docs

### 8.3 Phase 3: Builder Pattern (Week 3) - 6-8 hours

**Deliverables:**
- [ ] Create BeamBuilder class
- [ ] Implement fluent API methods
- [ ] Add builder examples to docs
- [ ] Write tests

**Success Criteria:**
- Builder pattern works for complex cases
- Fluent API is readable
- Examples show real-world usage

### 8.4 Phase 4: Migration (Ongoing) - 4-6 hours

**Deliverables:**
- [ ] Update existing code to accept both old and new input
- [ ] Add deprecation warnings for dict input
- [ ] Update all examples in docs
- [ ] Update Colab notebooks

---

## 9. Backward Compatibility Strategy

### 9.1 Dual Input Support

**Goal:** Support both old dict and new typed input without breaking changes.

**Implementation:**
```python
from typing import Union, TypedDict

# For backward compatibility, define dict structure
class BeamDict(TypedDict):
    span_mm: float
    width_mm: float
    depth_mm: float
    moment_knm: float
    shear_kn: float
    fck_mpa: float
    fy_mpa: float
    cover_mm: float

# Accept both formats
def design_beam(
    beam: Union[BeamInput, BeamDict, dict]
) -> BeamDesignResult:
    """
    Design beam accepting multiple input formats.

    Args:
        beam: Input as BeamInput object, BeamDict, or plain dict

    Returns:
        BeamDesignResult

    Example:
        >>> # New way (recommended)
        >>> beam = BeamInput(span_mm=5000, ...)
        >>> result = design_beam(beam)
        >>>
        >>> # Old way (still supported)
        >>> result = design_beam({'span_mm': 5000, ...})
    """
    if isinstance(beam, dict):
        # Convert dict to BeamInput
        beam = BeamInput(**beam)

    # Design logic uses beam.span_mm, beam.width_mm, etc.
    ...
```

### 9.2 Deprecation Path

**Timeline:**
- **v0.16:** Add BeamInput, support both formats (6 months)
- **v0.17:** Add deprecation warning for dict input (6 months)
- **v1.0:** Dict input removed (breaking change)

**Deprecation Warning:**
```python
def design_beam(beam: Union[BeamInput, dict]) -> BeamDesignResult:
    if isinstance(beam, dict):
        warnings.warn(
            "Dict input is deprecated and will be removed in v1.0. "
            "Use BeamInput instead: "
            "beam = BeamInput(**your_dict)",
            DeprecationWarning,
            stacklevel=2
        )
        beam = BeamInput(**beam)
    ...
```

---

**(Part 2/3 complete - continuing in next file)**
