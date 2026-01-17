# Multi-Code Architecture Design

**Type:** Architecture
**Audience:** All Agents, Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** LIB-IMPROVEMENT, TASK-ACI-01, TASK-EC2-01

---

## Overview

This document defines the architecture for supporting multiple design codes (IS 456, ACI 318, EC2) in a unified, extensible manner.

---

## Design Principles

1. **Single API, Multiple Codes** — Users call `sk.engine.design_beam(code="ACI318")` without learning different APIs
2. **Code as Plugin** — Each code is a self-contained module implementing a standard interface
3. **Shared Infrastructure** — Common utilities (validation, units, geometry) are reused
4. **Test Parity** — Each code has equivalent test coverage

---

## Directory Structure

```
structural_lib/
├── codes/
│   ├── __init__.py           # Code registry and base classes
│   ├── base.py               # Abstract DesignCode class
│   ├── registry.py           # Code registration and discovery
│   │
│   ├── is456/                # IS 456:2000 (Complete)
│   │   ├── __init__.py       # IS456Code class
│   │   ├── flexure.py        # Flexure design
│   │   ├── shear.py          # Shear design
│   │   ├── torsion.py        # Torsion design
│   │   ├── detailing.py      # Bar arrangements
│   │   ├── serviceability.py # Deflection, crack width
│   │   ├── tables.py         # Code tables (xu/d, tc, etc.)
│   │   ├── constants.py      # Gamma factors, limits
│   │   └── tests/            # Code-specific tests
│   │
│   ├── aci318/               # ACI 318-19 (To implement)
│   │   ├── __init__.py       # ACI318Code class
│   │   ├── flexure.py
│   │   ├── shear.py
│   │   ├── torsion.py
│   │   ├── detailing.py
│   │   ├── tables.py
│   │   ├── constants.py
│   │   └── tests/
│   │
│   └── ec2/                  # EN 1992-1-1 (Future)
│       ├── __init__.py       # EC2Code class
│       ├── flexure.py
│       ├── shear.py
│       ├── detailing.py
│       ├── constants.py
│       └── tests/
│
└── core/
    ├── base.py               # DesignCode ABC
    ├── registry.py           # Global registry
    ├── geometry.py           # Shared geometry utils
    ├── materials.py          # Material properties
    └── units.py              # Unit conversion
```

---

## Abstract Base Class

```python
# codes/base.py

from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass

@dataclass
class CodeInfo:
    """Metadata about a design code."""
    code_id: str          # "IS456", "ACI318", "EC2"
    name: str             # "IS 456:2000"
    version: str          # "2000"
    region: str           # "India", "USA", "Europe"
    status: str           # "stable", "beta", "stub"


class DesignCode(ABC):
    """
    Abstract base class for all design codes.

    Each code implementation must provide:
    - Flexure design
    - Shear design
    - Detailing rules
    - Material tables

    Optionally:
    - Torsion design
    - Serviceability checks
    """

    @property
    @abstractmethod
    def info(self) -> CodeInfo:
        """Return code metadata."""
        ...

    # =========================================================================
    # FLEXURE
    # =========================================================================

    @abstractmethod
    def design_flexure_singly(
        self,
        mu_knm: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> FlexureResult:
        """
        Design singly reinforced section.

        Args:
            mu_knm: Factored bending moment (kN·m)
            b_mm: Beam width (mm)
            d_mm: Effective depth (mm)
            fck: Concrete strength (N/mm² or MPa)
            fy: Steel yield strength (N/mm² or MPa)

        Returns:
            FlexureResult with required steel area
        """
        ...

    @abstractmethod
    def design_flexure_doubly(
        self,
        mu_knm: float,
        b_mm: float,
        d_mm: float,
        d_dash_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> FlexureResult:
        """Design doubly reinforced section."""
        ...

    @abstractmethod
    def check_flexure(
        self,
        mu_knm: float,
        ast_mm2: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> VerificationResult:
        """Verify flexure capacity with provided reinforcement."""
        ...

    # =========================================================================
    # SHEAR
    # =========================================================================

    @abstractmethod
    def design_shear(
        self,
        vu_kn: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        pt: float,
        **kwargs
    ) -> ShearResult:
        """
        Design shear reinforcement.

        Args:
            vu_kn: Factored shear force (kN)
            b_mm: Beam width (mm)
            d_mm: Effective depth (mm)
            fck: Concrete strength
            pt: Percentage of tension steel

        Returns:
            ShearResult with required stirrup area and spacing
        """
        ...

    @abstractmethod
    def get_concrete_shear_capacity(
        self,
        fck: float,
        pt: float,
        **kwargs
    ) -> float:
        """
        Get design shear strength of concrete (τc).

        This is code-specific (IS456 Table 19, ACI Vc formula, etc.)
        """
        ...

    # =========================================================================
    # DETAILING
    # =========================================================================

    @abstractmethod
    def compute_development_length(
        self,
        bar_dia_mm: float,
        fck: float,
        fy: float,
        bar_type: str = "tension",
        **kwargs
    ) -> float:
        """
        Compute development length (Ld).

        Args:
            bar_dia_mm: Bar diameter (mm)
            fck: Concrete strength
            fy: Steel yield strength
            bar_type: "tension" or "compression"

        Returns:
            Development length in mm
        """
        ...

    @abstractmethod
    def compute_lap_length(
        self,
        bar_dia_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> float:
        """Compute lap splice length."""
        ...

    @abstractmethod
    def get_minimum_cover(
        self,
        exposure_class: str,
        member_type: str = "beam",
        **kwargs
    ) -> float:
        """Get minimum concrete cover for exposure class."""
        ...

    @abstractmethod
    def get_bar_spacing_limits(
        self,
        bar_dia_mm: float,
        aggregate_size_mm: float = 20.0,
        **kwargs
    ) -> tuple[float, float]:
        """Get (min_spacing, max_spacing) for bars."""
        ...

    # =========================================================================
    # TABLES AND CONSTANTS
    # =========================================================================

    @abstractmethod
    def get_xu_max_ratio(self, fy: float) -> float:
        """Get maximum neutral axis depth ratio (xu_max/d)."""
        ...

    @abstractmethod
    def get_gamma_c(self) -> float:
        """Partial safety factor for concrete."""
        ...

    @abstractmethod
    def get_gamma_s(self) -> float:
        """Partial safety factor for steel."""
        ...

    # =========================================================================
    # OPTIONAL: TORSION
    # =========================================================================

    def design_torsion(
        self,
        tu_knm: float,
        vu_kn: float,
        mu_knm: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> TorsionResult | None:
        """Design for torsion (optional, not all codes implemented)."""
        return None  # Default: not implemented

    # =========================================================================
    # OPTIONAL: SERVICEABILITY
    # =========================================================================

    def check_deflection(
        self,
        span_mm: float,
        d_mm: float,
        support_condition: str,
        pt: float,
        pc: float = 0.0,
        **kwargs
    ) -> DeflectionResult | None:
        """Check deflection (optional)."""
        return None

    def check_crack_width(
        self,
        exposure_class: str,
        steel_stress: float,
        cover_mm: float,
        bar_dia_mm: float,
        spacing_mm: float,
        **kwargs
    ) -> CrackWidthResult | None:
        """Check crack width (optional)."""
        return None
```

---

## Code Registry

```python
# codes/registry.py

from typing import Type
from .base import DesignCode, CodeInfo

_REGISTRY: dict[str, Type[DesignCode]] = {}


def register_code(code_id: str):
    """Decorator to register a design code."""
    def decorator(cls: Type[DesignCode]):
        _REGISTRY[code_id.upper()] = cls
        return cls
    return decorator


def get_code(code_id: str) -> DesignCode:
    """Get an instance of a design code."""
    code_id = code_id.upper()
    if code_id not in _REGISTRY:
        available = list(_REGISTRY.keys())
        raise CodeNotFoundError(
            f"Code '{code_id}' not found. Available: {available}"
        )
    return _REGISTRY[code_id]()


def list_codes() -> list[CodeInfo]:
    """List all available codes."""
    return [cls().info for cls in _REGISTRY.values()]


def is_code_available(code_id: str) -> bool:
    """Check if a code is available."""
    return code_id.upper() in _REGISTRY
```

---

## IS 456 Implementation

```python
# codes/is456/__init__.py

from ..base import DesignCode, CodeInfo
from ..registry import register_code
from .flexure import design_singly_reinforced, design_doubly_reinforced
from .shear import design_shear_reinforcement, get_tc
from .detailing import compute_ld, compute_lap, get_cover
from .tables import XU_MAX_RATIOS, TC_TABLE
from .constants import GAMMA_C, GAMMA_S


@register_code("IS456")
class IS456Code(DesignCode):
    """
    IS 456:2000 — Indian Standard for Plain and Reinforced Concrete.

    Complete implementation with:
    - Flexure design (singly + doubly reinforced)
    - Shear design (Clause 40)
    - Torsion design (Clause 41)
    - Detailing per SP 34
    - Serviceability (Clause 23-24)
    """

    @property
    def info(self) -> CodeInfo:
        return CodeInfo(
            code_id="IS456",
            name="IS 456:2000",
            version="2000",
            region="India",
            status="stable"
        )

    def design_flexure_singly(self, mu_knm, b_mm, d_mm, fck, fy, **kwargs):
        return design_singly_reinforced(mu_knm, b_mm, d_mm, fck, fy)

    def design_flexure_doubly(self, mu_knm, b_mm, d_mm, d_dash_mm, fck, fy, **kwargs):
        return design_doubly_reinforced(mu_knm, b_mm, d_mm, d_dash_mm, fck, fy)

    def design_shear(self, vu_kn, b_mm, d_mm, fck, pt, **kwargs):
        return design_shear_reinforcement(vu_kn, b_mm, d_mm, fck, pt)

    def get_concrete_shear_capacity(self, fck, pt, **kwargs):
        return get_tc(fck, pt)

    def compute_development_length(self, bar_dia_mm, fck, fy, bar_type="tension", **kwargs):
        return compute_ld(bar_dia_mm, fck, fy, bar_type)

    def compute_lap_length(self, bar_dia_mm, fck, fy, **kwargs):
        return compute_lap(bar_dia_mm, fck, fy)

    def get_minimum_cover(self, exposure_class, member_type="beam", **kwargs):
        return get_cover(exposure_class, member_type)

    def get_bar_spacing_limits(self, bar_dia_mm, aggregate_size_mm=20.0, **kwargs):
        min_spacing = max(bar_dia_mm, aggregate_size_mm + 5, 25)
        max_spacing = 300  # IS 456 Cl 26.3.3
        return (min_spacing, max_spacing)

    def get_xu_max_ratio(self, fy):
        return XU_MAX_RATIOS.get(fy, 0.46)

    def get_gamma_c(self):
        return GAMMA_C  # 1.5

    def get_gamma_s(self):
        return GAMMA_S  # 1.15

    # Torsion and serviceability implemented in full IS456
    def design_torsion(self, tu_knm, vu_kn, mu_knm, b_mm, d_mm, fck, fy, **kwargs):
        from .torsion import design_torsion
        return design_torsion(tu_knm, vu_kn, mu_knm, b_mm, d_mm, fck, fy)

    def check_deflection(self, span_mm, d_mm, support_condition, pt, pc=0.0, **kwargs):
        from .serviceability import check_deflection
        return check_deflection(span_mm, d_mm, support_condition, pt, pc)
```

---

## ACI 318 Implementation Plan

### Key Differences from IS 456

| Aspect | IS 456 | ACI 318-19 |
|--------|--------|------------|
| **Stress block** | Rectangular, 0.36fck | Rectangular, 0.85f'c |
| **Phi factors** | γc=1.5, γs=1.15 | φ varies by check (0.65-0.90) |
| **xu_max/d** | 0.48 (Fe415), 0.46 (Fe500) | c/dt limit for tension-controlled |
| **Shear** | τc from Table 19 | Vc = 2√f'c × bw × d |
| **Development** | Ld = 0.87fy × φ / (4τbd) | Ld per ACI 25.4 tables |
| **Units** | SI (N, mm, kN, kN·m) | US customary (psi, in, kip, kip-ft) |

### Implementation Phases

**Phase 1: Core Flexure + Shear (Priority)**
```python
# codes/aci318/flexure.py

def design_singly_reinforced(
    mu_kipft: float,
    b_in: float,
    d_in: float,
    fc_psi: float,
    fy_psi: float,
) -> FlexureResult:
    """
    ACI 318-19 flexure design.

    Uses rectangular stress block with:
    - a = β1 × c
    - β1 = 0.85 for f'c ≤ 4000 psi
    - Mu = φ × As × fy × (d - a/2)
    """
    # Implementation
    ...
```

**Phase 2: Detailing**
- Development length per ACI 25.4
- Splice lengths per ACI 25.5
- Minimum cover per ACI 20.6

**Phase 3: Torsion + Serviceability**
- Torsion per ACI 22.7
- Deflection per ACI 24.2

### Unit Handling Strategy

```python
# Option A: Internal SI, convert at boundaries
def design_flexure_singly(self, mu_knm, b_mm, d_mm, fc_mpa, fy_mpa, **kwargs):
    # Convert to US customary internally if needed
    mu_kipft = mu_knm * 0.7376
    b_in = b_mm / 25.4
    d_in = d_mm / 25.4
    fc_psi = fc_mpa * 145.038
    fy_psi = fy_mpa * 145.038
    # ... compute
    # Convert back to SI for result
    return FlexureResult(ast_required_mm2=as_in2 * 645.16, ...)

# Option B: Dual unit support via parameter
def design_flexure_singly(self, mu, b, d, fc, fy, units="SI", **kwargs):
    if units == "US":
        # Use US formulas directly
        ...
    else:
        # Convert to US, compute, convert back
        ...
```

**Recommendation:** Option A (internal SI) for consistency across codes.

---

## EC2 Implementation Plan (Future)

### Key Differences

| Aspect | IS 456 | EC2 (EN 1992-1-1) |
|--------|--------|-------------------|
| **Stress block** | Rectangular | Parabolic-rectangular or equivalent |
| **Material safety** | γc=1.5, γs=1.15 | γc=1.5, γs=1.15 (same) |
| **Shear** | τc table | Variable strut inclination θ |
| **Detailing** | Different cover and spacing rules |
| **Notation** | Mu, Ast | MEd, As1 |

### Scope (Minimal Viable)
- Flexure with parabolic-rectangular block
- Shear with variable strut (simplified)
- Basic detailing

---

## Engine Integration

```python
# engine/design.py

from structural_lib.codes import get_code, is_code_available

def design_beam(
    beam: BeamInput,
    code: str = "IS456",
    include_detailing: bool = True,
    include_3d: bool = False,
) -> DesignResult:
    """Design beam using specified code."""

    # Get code instance
    if not is_code_available(code):
        raise CodeNotFoundError(code)
    design_code = get_code(code)

    # Extract inputs
    b = beam.geometry.b_mm
    D = beam.geometry.D_mm
    d = beam.geometry.effective_depth
    fck = beam.materials.fck_nmm2
    fy = beam.materials.fy_nmm2
    mu = beam.loads.mu_knm
    vu = beam.loads.vu_kn

    # Design flexure
    flexure_result = design_code.design_flexure_singly(mu, b, d, fck, fy)
    if not flexure_result.is_ok:
        # Try doubly reinforced
        flexure_result = design_code.design_flexure_doubly(
            mu, b, d, beam.geometry.cover_mm, fck, fy
        )

    # Design shear
    pt = flexure_result.pt_provided
    shear_result = design_code.design_shear(vu, b, d, fck, pt)

    # Torsion (if applicable)
    torsion_result = None
    if beam.loads.tu_knm > 0:
        torsion_result = design_code.design_torsion(
            beam.loads.tu_knm, vu, mu, b, d, fck, fy
        )

    # Detailing
    detailing_result = None
    if include_detailing:
        detailing_result = _compute_detailing(design_code, beam, flexure_result, shear_result)

    # 3D geometry
    geometry_3d = None
    if include_3d and detailing_result:
        geometry_3d = beam_to_3d_geometry(detailing_result)

    return DesignResult(
        beam_id=beam.beam_id,
        story=beam.story,
        code=code,
        is_ok=flexure_result.is_ok and shear_result.is_ok,
        flexure=flexure_result,
        shear=shear_result,
        torsion=torsion_result,
        detailing=detailing_result,
        geometry_3d=geometry_3d,
        ...
    )
```

---

## Testing Strategy

### Per-Code Test Suite

```
tests/
├── codes/
│   ├── test_is456_flexure.py
│   ├── test_is456_shear.py
│   ├── test_is456_detailing.py
│   ├── test_aci318_flexure.py
│   ├── test_aci318_shear.py
│   └── test_ec2_flexure.py
└── integration/
    ├── test_multi_code_design.py
    └── test_code_comparison.py
```

### Cross-Code Comparison Tests

```python
# tests/integration/test_code_comparison.py

def test_similar_results_for_similar_inputs():
    """
    Given similar inputs, IS456 and ACI318 should give
    similar (not identical) results.

    This validates the implementations are in the same ballpark.
    """
    beam = BeamInput(
        beam_id="TEST",
        geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
        materials=MaterialsInput(fck_nmm2=25, fy_nmm2=500),
        loads=LoadsInput(mu_knm=200, vu_kn=100)
    )

    is456_result = sk.engine.design_beam(beam, code="IS456")
    aci318_result = sk.engine.design_beam(beam, code="ACI318")

    # Both should pass (basic design)
    assert is456_result.is_ok
    assert aci318_result.is_ok

    # Steel areas should be within 30% of each other
    ratio = is456_result.flexure.ast_required_mm2 / aci318_result.flexure.ast_required_mm2
    assert 0.7 < ratio < 1.3
```

---

## Migration Path

1. **Phase 1 (Week 1-2):** Refactor IS 456 to implement new base class
2. **Phase 2 (Week 3-4):** Implement ACI 318 flexure + shear
3. **Phase 3 (Week 5-6):** Implement ACI 318 detailing
4. **Phase 4 (Week 7-8):** Testing + documentation
5. **Future:** EC2 implementation

---

## Open Questions

1. **Unit handling:** Should we support US customary units natively for ACI?
2. **Material grades:** How to handle different grade naming (M25 vs f'c=3500psi)?
3. **Load factors:** Are load factors code-specific or user-input?
4. **Detailing output:** Should detailing use code-specific callout formats?

---

*This architecture enables clean, maintainable multi-code support.*
