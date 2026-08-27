# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       inputs
Description:  Professional input dataclasses for beam design

This module provides structured input types for the IS 456 beam design API.
Using dataclasses ensures type safety, validation, and IDE autocompletion.

Usage:
    >>> from structural_lib.core.inputs import BeamGeometryInput, MaterialsInput, LoadsInput
    >>> geometry = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)
    >>> materials = MaterialsInput(fck_nmm2=25, fy_nmm2=500)
    >>> loads = LoadsInput(mu_knm=150, vu_kn=80)

Features:
    - Immutable by default (frozen=True for safety)
    - Post-init validation with clear error messages
    - Helper class methods for common configurations
    - JSON/dict import/export for interoperability
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from structural_lib.core.validation import (
    require_nonblank_string,
    require_nonnegative_real,
    require_positive_real,
    require_strict_bool,
)

__all__ = [
    "BeamGeometryInput",
    "MaterialsInput",
    "LoadsInput",
    "LoadCaseInput",
    "BeamInput",
    "DetailingConfigInput",
    "from_dict",
    "from_json",
    "from_json_file",
]


_MISSING = object()


def _first_present(
    data: dict[str, Any], *keys: str, default: object = _MISSING
) -> object:
    """Return the first present alias without treating explicit zero as absent."""
    for key in keys:
        if key in data:
            return data[key]
    if default is not _MISSING:
        return default
    aliases = " or ".join(keys)
    raise ValueError(f"Missing required field: {aliases}")


@dataclass(frozen=True)
class BeamGeometryInput:
    """Beam geometry parameters.

    All dimensions in mm. Immutable after creation.

    Attributes:
        b_mm: Beam width (mm). Must be positive.
        D_mm: Overall depth (mm). Must be positive and > d_mm.
        span_mm: Clear span (mm). Must be positive.
        d_mm: Effective depth (mm). If None, computed from D, cover, stirrup, bar.
        cover_mm: Clear cover to reinforcement (mm). Default 40mm per IS 456.
        stirrup_dia_mm: Stirrup diameter (mm). Default 8mm.
        bar_dia_mm: Main bar diameter (mm). Default 20mm.

    Examples:
        >>> geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)
        >>> geom.effective_depth  # Auto-calculated: 500 - 40 - 8 - 10
        442.0

        >>> # With explicit effective depth
        >>> geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, d_mm=450)

    Raises:
        ValueError: If dimensions are non-positive or inconsistent.
    """

    b_mm: float
    D_mm: float
    span_mm: float
    d_mm: float | None = None
    cover_mm: float = 40.0
    stirrup_dia_mm: float = 8.0
    bar_dia_mm: float = 20.0

    def __post_init__(self) -> None:
        """Validate geometry parameters."""
        require_positive_real(self.b_mm, "b_mm")
        require_positive_real(self.D_mm, "D_mm")
        require_positive_real(self.span_mm, "span_mm")
        require_positive_real(self.cover_mm, "cover_mm")
        require_positive_real(self.stirrup_dia_mm, "stirrup_dia_mm")
        require_positive_real(self.bar_dia_mm, "bar_dia_mm")
        if self.cover_mm >= self.D_mm:
            raise ValueError("cover_mm must be less than D_mm.")
        if self.b_mm <= 2 * (self.cover_mm + self.stirrup_dia_mm):
            raise ValueError(
                "b_mm must leave positive clear width inside cover and stirrups."
            )

        # Effective depth validation
        if self.d_mm is not None:
            d_eff = require_positive_real(self.d_mm, "d_mm")
        else:
            d_eff = (
                self.D_mm - self.cover_mm - self.stirrup_dia_mm - self.bar_dia_mm / 2
            )
        if d_eff <= 0:
            raise ValueError(f"Effective depth must be positive, got {d_eff}")
        if d_eff >= self.D_mm:
            raise ValueError(
                f"Effective depth ({d_eff}mm) must be less than overall depth ({self.D_mm}mm)"
            )

        # Practical limits check (warnings would be nice, but we raise for now)
        if self.b_mm < 200:
            pass  # Could warn: "Beam width < 200mm may be impractical"
        if self.D_mm / self.b_mm > 4:
            pass  # Could warn: "D/b > 4 may cause stability issues"

    @property
    def effective_depth(self) -> float:
        """Return effective depth (d_mm or computed from D, cover, stirrup, bar)."""
        if self.d_mm is not None:
            return self.d_mm
        from structural_lib.core.geometry import compute_effective_depth

        return compute_effective_depth(
            self.D_mm, self.cover_mm, self.stirrup_dia_mm, self.bar_dia_mm
        )

    @property
    def span_depth_ratio(self) -> float:
        """Return L/d ratio for serviceability checks."""
        return self.span_mm / self.effective_depth

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BeamGeometryInput:
        """Create from dictionary.

        Handles both canonical (b_mm, D_mm) and legacy (b, D) key formats.
        """
        # Normalize keys
        b = _first_present(data, "b_mm", "b")
        D = _first_present(data, "D_mm", "D")
        span = _first_present(data, "span_mm", "span")
        d = _first_present(data, "d_mm", "d", default=None)
        cover = _first_present(data, "cover_mm", "cover", default=40.0)
        stirrup = _first_present(data, "stirrup_dia_mm", default=8.0)
        bar = _first_present(data, "bar_dia_mm", default=20.0)

        return cls(
            b_mm=b,  # type: ignore[arg-type]
            D_mm=D,  # type: ignore[arg-type]
            span_mm=span,  # type: ignore[arg-type]
            d_mm=d,  # type: ignore[arg-type]
            cover_mm=cover,  # type: ignore[arg-type]
            stirrup_dia_mm=stirrup,  # type: ignore[arg-type]
            bar_dia_mm=bar,  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class MaterialsInput:
    """Material properties for beam design.

    Attributes:
        fck_nmm2: Characteristic compressive strength of concrete (N/mm²).
                  Typical values: 20, 25, 30, 35, 40 for IS 456.
        fy_nmm2: Characteristic yield strength of steel (N/mm²).
                 Typical values: 415 (Fe 415), 500 (Fe 500), 550 (Fe 550).
        es_nmm2: Modulus of elasticity of steel (N/mm²). Default 2×10⁵.

    Examples:
        >>> mat = MaterialsInput(fck_nmm2=25, fy_nmm2=500)
        >>> mat.concrete_grade  # "M25"

        >>> # Using class methods for common grades
        >>> mat = MaterialsInput.m25_fe500()

    Raises:
        ValueError: If material strengths are non-positive or out of range.
    """

    fck_nmm2: float
    fy_nmm2: float
    es_nmm2: float = 200000.0

    # Valid ranges per IS 456
    VALID_FCK_RANGE = (15.0, 80.0)  # M15 to M80
    VALID_FY_RANGE = (250.0, 550.0)  # Maintained IS 456 service domain

    def __post_init__(self) -> None:
        """Validate material properties."""
        require_positive_real(self.fck_nmm2, "fck_nmm2")
        require_positive_real(self.fy_nmm2, "fy_nmm2")
        require_positive_real(self.es_nmm2, "es_nmm2")

        if not (self.VALID_FCK_RANGE[0] <= self.fck_nmm2 <= self.VALID_FCK_RANGE[1]):
            raise ValueError("fck_nmm2 must be within the supported range 15-80 N/mm².")
        if not (self.VALID_FY_RANGE[0] <= self.fy_nmm2 <= self.VALID_FY_RANGE[1]):
            raise ValueError(
                "fy_nmm2 must be within the supported range 250-550 N/mm²."
            )

    @property
    def concrete_grade(self) -> str:
        """Return concrete grade string (e.g., 'M25')."""
        return f"M{int(self.fck_nmm2)}"

    @property
    def steel_grade(self) -> str:
        """Return steel grade string (e.g., 'Fe 500')."""
        return f"Fe {int(self.fy_nmm2)}"

    @classmethod
    def m25_fe500(cls) -> MaterialsInput:
        """Create M25 concrete with Fe 500 steel (most common combination)."""
        return cls(fck_nmm2=25.0, fy_nmm2=500.0)

    @classmethod
    def m30_fe500(cls) -> MaterialsInput:
        """Create M30 concrete with Fe 500 steel."""
        return cls(fck_nmm2=30.0, fy_nmm2=500.0)

    @classmethod
    def m20_fe415(cls) -> MaterialsInput:
        """Create M20 concrete with Fe 415 steel (legacy/economy)."""
        return cls(fck_nmm2=20.0, fy_nmm2=415.0)

    @classmethod
    def m35_fe500(cls) -> MaterialsInput:
        """Create M35 concrete with Fe 500 steel (higher strength)."""
        return cls(fck_nmm2=35.0, fy_nmm2=500.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MaterialsInput:
        """Create from dictionary.

        Handles both canonical (fck_nmm2) and legacy (fck) key formats.
        """
        fck = _first_present(data, "fck_nmm2", "fck")
        fy = _first_present(data, "fy_nmm2", "fy")
        es = _first_present(data, "es_nmm2", "Es", default=200000.0)

        return cls(
            fck_nmm2=fck,  # type: ignore[arg-type]
            fy_nmm2=fy,  # type: ignore[arg-type]
            es_nmm2=es,  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class LoadsInput:
    """Simple loads input for single-case design.

    For multiple load cases, use LoadCaseInput with BeamInput.

    Attributes:
        mu_knm: Factored bending moment (kN·m). Must be non-negative.
        vu_kn: Factored shear force (kN). Must be non-negative.
        case_id: Optional load case identifier.

    Examples:
        >>> loads = LoadsInput(mu_knm=150, vu_kn=80)

        >>> # With case identifier
        >>> loads = LoadsInput(mu_knm=150, vu_kn=80, case_id="1.5(DL+LL)")

    Raises:
        ValueError: If loads are negative.
    """

    mu_knm: float
    vu_kn: float
    case_id: str = "CASE-1"

    def __post_init__(self) -> None:
        """Validate load values."""
        require_nonnegative_real(self.mu_knm, "mu_knm")
        require_nonnegative_real(self.vu_kn, "vu_kn")
        require_nonblank_string(self.case_id, "case_id")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoadsInput:
        """Create from dictionary.

        Handles both canonical (mu_knm) and legacy (Mu, mu) key formats.
        """
        mu = _first_present(data, "mu_knm", "Mu", "mu")
        vu = _first_present(data, "vu_kn", "Vu", "vu")
        case_id = _first_present(data, "case_id", default="CASE-1")

        return cls(
            mu_knm=mu,  # type: ignore[arg-type]
            vu_kn=vu,  # type: ignore[arg-type]
            case_id=case_id,  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class LoadCaseInput:
    """Single load case for multi-case analysis.

    Attributes:
        case_id: Unique load case identifier.
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear force (kN).
        description: Optional description of load combination.

    Examples:
        >>> case1 = LoadCaseInput("1.5DL+1.5LL", mu_knm=120, vu_kn=85)
        >>> case2 = LoadCaseInput("1.2DL+1.6LL", mu_knm=135, vu_kn=92)
    """

    case_id: str
    mu_knm: float
    vu_kn: float
    description: str = ""

    def __post_init__(self) -> None:
        """Validate load case."""
        require_nonblank_string(self.case_id, "case_id")
        require_nonnegative_real(self.mu_knm, "mu_knm")
        require_nonnegative_real(self.vu_kn, "vu_kn")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoadCaseInput:
        """Create from dictionary."""
        case_id = _first_present(data, "case_id")
        mu = _first_present(data, "mu_knm", "Mu", "mu")
        vu = _first_present(data, "vu_kn", "Vu", "vu")
        description = _first_present(data, "description", default="")

        return cls(
            case_id=case_id,  # type: ignore[arg-type]
            mu_knm=mu,  # type: ignore[arg-type]
            vu_kn=vu,  # type: ignore[arg-type]
            description=description,  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class DetailingConfigInput:
    """Configuration for beam detailing.

    Attributes:
        stirrup_dia_mm: Stirrup diameter (mm). Default 8mm.
        stirrup_spacing_start_mm: Spacing at supports (mm). Default 150mm.
        stirrup_spacing_mid_mm: Spacing at midspan (mm). Default 200mm.
        stirrup_spacing_end_mm: Spacing at other end (mm). Default same as start.
        is_seismic: Apply IS 13920 seismic detailing. Default False.
        preferred_bar_dias: Preferred main bar diameters (mm).
        max_bar_layers: Maximum bar layers allowed.

    Examples:
        >>> config = DetailingConfigInput(stirrup_dia_mm=10, is_seismic=True)

        >>> # For seismic zone, use class method
        >>> config = DetailingConfigInput.seismic()
    """

    stirrup_dia_mm: float = 8.0
    stirrup_spacing_start_mm: float = 150.0
    stirrup_spacing_mid_mm: float = 200.0
    stirrup_spacing_end_mm: float | None = None  # Defaults to start
    is_seismic: bool = False
    preferred_bar_dias: tuple[float, ...] = (12.0, 16.0, 20.0, 25.0)
    max_bar_layers: int = 2
    d_dash_mm: float = 50.0  # Cover to compression steel
    asv_mm2: float = 100.0  # Area of stirrup legs (for 2-legged 8mm: ~100mm²)

    def __post_init__(self) -> None:
        """Reject unusable detailing configuration at construction."""
        require_positive_real(self.stirrup_dia_mm, "stirrup_dia_mm")
        require_positive_real(self.stirrup_spacing_start_mm, "stirrup_spacing_start_mm")
        require_positive_real(self.stirrup_spacing_mid_mm, "stirrup_spacing_mid_mm")
        if self.stirrup_spacing_end_mm is not None:
            require_positive_real(self.stirrup_spacing_end_mm, "stirrup_spacing_end_mm")
        require_strict_bool(self.is_seismic, "is_seismic")
        require_positive_real(self.d_dash_mm, "d_dash_mm")
        require_positive_real(self.asv_mm2, "asv_mm2")
        if isinstance(self.max_bar_layers, bool) or not isinstance(
            self.max_bar_layers, int
        ):
            raise ValueError("max_bar_layers must be an integer.")
        if self.max_bar_layers <= 0:
            raise ValueError("max_bar_layers must be > 0.")
        if (
            not isinstance(self.preferred_bar_dias, (tuple, list))
            or not self.preferred_bar_dias
        ):
            raise ValueError("preferred_bar_dias must contain at least one diameter.")
        normalized = tuple(
            require_positive_real(value, "preferred_bar_dias")
            for value in self.preferred_bar_dias
        )
        if len(set(normalized)) != len(normalized):
            raise ValueError("preferred_bar_dias must not contain duplicates.")

    @property
    def stirrup_spacing_end(self) -> float:
        """Return end spacing (defaults to start spacing if not specified)."""
        return (
            self.stirrup_spacing_end_mm
            if self.stirrup_spacing_end_mm is not None
            else self.stirrup_spacing_start_mm
        )

    @classmethod
    def seismic(cls, zone: int = 3) -> DetailingConfigInput:
        """Create seismic detailing configuration.

        Args:
            zone: Seismic zone (1-5). Zones 4-5 use stricter requirements.
        """
        if zone >= 4:
            return cls(
                stirrup_dia_mm=10.0,
                stirrup_spacing_start_mm=100.0,
                stirrup_spacing_mid_mm=150.0,
                is_seismic=True,
            )
        return cls(
            stirrup_dia_mm=8.0,
            stirrup_spacing_start_mm=125.0,
            stirrup_spacing_mid_mm=175.0,
            is_seismic=True,
        )

    @classmethod
    def gravity_only(cls) -> DetailingConfigInput:
        """Create configuration for gravity-only design (non-seismic)."""
        return cls(is_seismic=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DetailingConfigInput:
        """Create from dictionary."""
        return cls(
            stirrup_dia_mm=_first_present(data, "stirrup_dia_mm", default=8.0),  # type: ignore[arg-type]
            stirrup_spacing_start_mm=_first_present(
                data, "stirrup_spacing_start_mm", default=150.0
            ),  # type: ignore[arg-type]
            stirrup_spacing_mid_mm=_first_present(
                data, "stirrup_spacing_mid_mm", default=200.0
            ),  # type: ignore[arg-type]
            stirrup_spacing_end_mm=(
                data["stirrup_spacing_end_mm"]
                if "stirrup_spacing_end_mm" in data
                and data["stirrup_spacing_end_mm"] is not None
                else None
            ),
            is_seismic=_first_present(data, "is_seismic", default=False),  # type: ignore[arg-type]
            preferred_bar_dias=tuple(
                _first_present(data, "preferred_bar_dias", default=(12, 16, 20, 25))  # type: ignore[arg-type]
            ),
            max_bar_layers=_first_present(data, "max_bar_layers", default=2),  # type: ignore[arg-type]
            d_dash_mm=_first_present(data, "d_dash_mm", default=50.0),  # type: ignore[arg-type]
            asv_mm2=_first_present(data, "asv_mm2", default=100.0),  # type: ignore[arg-type]
        )


@dataclass
class BeamInput:
    """Complete beam input for design and detailing.

    This is the primary input dataclass combining geometry, materials,
    loads, and optional detailing configuration. Not frozen to allow
    mutation during input building.

    Attributes:
        beam_id: Unique beam identifier.
        story: Story/level name.
        geometry: Beam geometry (dimensions).
        materials: Material properties (concrete, steel grades).
        loads: Simple load input for single-case design.
        load_cases: Multiple load cases for envelope design.
        detailing_config: Optional detailing configuration.
        units: Units system label. Default "IS456".

    Examples:
        >>> # Simple single-case input
        >>> beam = BeamInput(
        ...     beam_id="B1",
        ...     story="GF",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
        ...     materials=MaterialsInput.m25_fe500(),
        ...     loads=LoadsInput(mu_knm=150, vu_kn=80),
        ... )

        >>> # Multi-case input
        >>> beam = BeamInput(
        ...     beam_id="B2",
        ...     story="1F",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000),
        ...     materials=MaterialsInput.m30_fe500(),
        ...     load_cases=[
        ...         LoadCaseInput("1.5DL+1.5LL", mu_knm=200, vu_kn=100),
        ...         LoadCaseInput("1.2DL+1.6LL+EQX", mu_knm=220, vu_kn=110),
        ...     ],
        ...     detailing_config=DetailingConfigInput.seismic(zone=4),
        ... )

        >>> # From JSON file
        >>> beam = BeamInput.from_json_file("inputs/B1.json")
    """

    beam_id: str
    story: str
    geometry: BeamGeometryInput
    materials: MaterialsInput
    loads: LoadsInput | None = None
    load_cases: list[LoadCaseInput] = field(default_factory=list)
    detailing_config: DetailingConfigInput = field(default_factory=DetailingConfigInput)
    units: str = "IS456"

    def __post_init__(self) -> None:
        """Validate beam input."""
        self.beam_id = require_nonblank_string(self.beam_id, "beam_id")
        self.story = require_nonblank_string(self.story, "story")
        require_nonblank_string(self.units, "units")
        if not isinstance(self.geometry, BeamGeometryInput):
            raise ValueError("geometry must be a BeamGeometryInput.")
        if not isinstance(self.materials, MaterialsInput):
            raise ValueError("materials must be a MaterialsInput.")
        if not isinstance(self.detailing_config, DetailingConfigInput):
            raise ValueError("detailing_config must be a DetailingConfigInput.")
        if self.loads is not None and not isinstance(self.loads, LoadsInput):
            raise ValueError("loads must be a LoadsInput.")
        if not isinstance(self.load_cases, list) or any(
            not isinstance(case, LoadCaseInput) for case in self.load_cases
        ):
            raise ValueError("load_cases must be a list of LoadCaseInput values.")
        if self.loads is not None and self.load_cases:
            raise ValueError("Specify 'loads' or 'load_cases', not both.")
        if self.loads is None and not self.load_cases:
            raise ValueError("Either 'loads' or 'load_cases' must be provided")
        case_ids = [case.case_id.strip() for case in self.load_cases]
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("load_cases must have unique case_id values.")

    @property
    def has_multiple_cases(self) -> bool:
        """Return True if multiple load cases are defined."""
        return len(self.load_cases) > 1

    @property
    def governing_moment(self) -> float:
        """Return maximum moment from all load cases."""
        if self.loads is not None:
            return self.loads.mu_knm
        return max(case.mu_knm for case in self.load_cases) if self.load_cases else 0.0

    @property
    def governing_shear(self) -> float:
        """Return maximum shear from all load cases."""
        if self.loads is not None:
            return self.loads.vu_kn
        return max(case.vu_kn for case in self.load_cases) if self.load_cases else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        result: dict[str, Any] = {
            "beam_id": self.beam_id,
            "story": self.story,
            "geometry": self.geometry.to_dict(),
            "materials": self.materials.to_dict(),
            "detailing_config": self.detailing_config.to_dict(),
            "units": self.units,
        }

        if self.loads is not None:
            result["loads"] = self.loads.to_dict()

        if self.load_cases:
            result["load_cases"] = [case.to_dict() for case in self.load_cases]

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_json_file(self, path: str | Path) -> Path:
        """Write to JSON file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.to_json(), encoding="utf-8")
        return file_path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BeamInput:
        """Create from dictionary.

        Handles nested structures and various key formats.
        """
        geometry = BeamGeometryInput.from_dict(data.get("geometry", data))
        materials = MaterialsInput.from_dict(data.get("materials", data))

        loads = None
        if "loads" in data:
            loads = LoadsInput.from_dict(data["loads"])
        elif "mu_knm" in data or "Mu" in data:
            # Flat format with loads at top level
            loads = LoadsInput.from_dict(data)

        load_cases: list[LoadCaseInput] = []
        if "load_cases" in data:
            load_cases = [LoadCaseInput.from_dict(c) for c in data["load_cases"]]
        elif "cases" in data:
            load_cases = [LoadCaseInput.from_dict(c) for c in data["cases"]]

        detailing_config = DetailingConfigInput()
        if "detailing_config" in data:
            detailing_config = DetailingConfigInput.from_dict(data["detailing_config"])
        elif "detailing" in data:
            detailing_config = DetailingConfigInput.from_dict(data["detailing"])

        return cls(
            beam_id=_first_present(data, "beam_id"),  # type: ignore[arg-type]
            story=_first_present(data, "story"),  # type: ignore[arg-type]
            geometry=geometry,
            materials=materials,
            loads=loads,
            load_cases=load_cases,
            detailing_config=detailing_config,
            units=_first_present(data, "units", default="IS456"),  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, json_string: str) -> BeamInput:
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_string))

    @classmethod
    def from_json_file(cls, path: str | Path) -> BeamInput:
        """Create from JSON file."""
        content = Path(path).read_text(encoding="utf-8")
        return cls.from_json(content)


# =============================================================================
# Module-level convenience functions
# =============================================================================


def from_dict(data: dict[str, Any]) -> BeamInput:
    """Create BeamInput from dictionary (convenience function)."""
    return BeamInput.from_dict(data)


def from_json(json_string: str) -> BeamInput:
    """Create BeamInput from JSON string (convenience function)."""
    return BeamInput.from_json(json_string)


def from_json_file(path: str | Path) -> BeamInput:
    """Create BeamInput from JSON file (convenience function)."""
    return BeamInput.from_json_file(path)
