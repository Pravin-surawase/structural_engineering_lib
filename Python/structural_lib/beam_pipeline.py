"""
beam_pipeline — Unified application-layer pipeline for beam design.

This module provides a single, canonical pipeline that:
1. CLI (`__main__.py`) and job_runner share the same design logic
2. Outputs a versioned, documented JSON schema
3. Validates units at the application boundary

Design Goals (from architecture-review-2025-12-27.md):
- Single source of truth for design workflow
- Canonical output schema (v1)
- Units validation at app layer
- Deterministic outputs

Schema Version: 1
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from . import api
from . import detailing


# =============================================================================
# Schema Version
# =============================================================================

SCHEMA_VERSION = 1

# Canonical units for IS456 pipeline
# All inputs/outputs use these units
IS456_UNITS = {
    "length": "mm",
    "stress": "N/mm²",
    "force": "kN",
    "moment": "kN·m",
    "area": "mm²",
}


# =============================================================================
# Units Validation
# =============================================================================

# Normalized forms for case-insensitive matching (uppercase, no spaces)
_VALID_UNIT_NORMALIZED = frozenset(
    {
        "IS456",
        "MM-KN-KNM-NMM2",
        "MM,KN,KN-M,N/MM2",
    }
)


class UnitsValidationError(ValueError):
    """Raised when units parameter is invalid or missing."""

    pass


def validate_units(units: Optional[str]) -> str:
    """
    Validate units string at application boundary.

    Args:
        units: Units specifier string.

    Returns:
        Normalized units string ("IS456").

    Raises:
        UnitsValidationError: If units is invalid or missing.
    """
    if units is None or not isinstance(units, str) or units.strip() == "":
        raise UnitsValidationError(
            "units is required. Use 'IS456' for IS 456 standard units "
            "(mm, N/mm², kN, kN·m)."
        )

    # Case-insensitive comparison: normalize to uppercase, remove spaces
    normalized = units.strip().upper().replace(" ", "")
    if normalized not in _VALID_UNIT_NORMALIZED:
        raise UnitsValidationError(
            f"Invalid units '{units}'. Expected 'IS456', 'IS 456', "
            "'mm-kN-kNm-Nmm2', or 'mm,kN,kN-m,N/mm2' (case-insensitive)."
        )

    return "IS456"  # Always return canonical form


# =============================================================================
# Canonical Output Schema (v1)
# =============================================================================


@dataclass
class BeamGeometry:
    """Beam geometry in canonical units (mm)."""

    b_mm: float  # Width
    D_mm: float  # Overall depth
    d_mm: float  # Effective depth
    span_mm: float  # Span length
    cover_mm: float  # Clear cover
    d_dash_mm: float = 50.0  # Compression steel depth


@dataclass
class BeamMaterials:
    """Material properties in canonical units (N/mm²)."""

    fck_nmm2: float  # Concrete characteristic strength
    fy_nmm2: float  # Steel yield strength


@dataclass
class BeamLoads:
    """Load case in canonical units (kN, kN·m)."""

    case_id: str
    mu_knm: float  # Factored moment
    vu_kn: float  # Factored shear


@dataclass
class FlexureOutput:
    """Flexure design output."""

    ast_required_mm2: float
    asc_required_mm2: float
    xu_mm: float
    xu_max_mm: float
    mu_lim_knm: float
    xu_d_ratio: float
    section_type: str  # "UNDER_REINFORCED", "BALANCED", "OVER_REINFORCED"
    is_safe: bool
    utilization: float
    remarks: str = ""


@dataclass
class ShearOutput:
    """Shear design output."""

    tau_v_nmm2: float
    tau_c_nmm2: float
    tau_c_max_nmm2: float
    vus_kn: float
    sv_required_mm: float
    is_safe: bool
    utilization: float
    remarks: str = ""


@dataclass
class ServiceabilityOutput:
    """Serviceability check output (optional)."""

    deflection_status: str = "not_run"
    deflection_ok: Optional[bool] = None
    deflection_remarks: str = ""
    deflection_utilization: Optional[float] = None
    crack_width_status: str = "not_run"
    crack_width_ok: Optional[bool] = None
    crack_width_remarks: str = ""
    crack_width_utilization: Optional[float] = None


@dataclass
class DetailingOutput:
    """Detailing output (optional)."""

    ld_tension_mm: float = 0.0
    lap_length_mm: float = 0.0
    bottom_bars: List[Dict[str, Any]] = field(default_factory=list)
    top_bars: List[Dict[str, Any]] = field(default_factory=list)
    stirrups: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BeamDesignOutput:
    """
    Canonical output schema for a single beam design.

    This is the unified output format used by CLI, job_runner, and
    any other consumer. Schema version is included for forward compatibility.
    """

    schema_version: int
    code: str  # "IS456"
    units: str  # "IS456" = mm, N/mm², kN, kN·m

    beam_id: str
    story: str

    geometry: BeamGeometry
    materials: BeamMaterials
    loads: BeamLoads

    flexure: FlexureOutput
    shear: ShearOutput
    serviceability: ServiceabilityOutput = field(default_factory=ServiceabilityOutput)
    detailing: Optional[DetailingOutput] = None

    is_ok: bool = False
    governing_utilization: float = 0.0
    governing_check: str = ""
    remarks: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return _dataclass_to_dict(self)


@dataclass
class MultiBeamOutput:
    """Output for multiple beams."""

    schema_version: int
    code: str
    units: str
    beams: List[BeamDesignOutput]
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return _dataclass_to_dict(self)


def _dataclass_to_dict(obj: Any) -> Any:
    """Recursively convert dataclass to dict, handling enums and nested objects."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Enum):
        return obj.value if hasattr(obj, "value") else str(obj)
    else:
        return obj


# =============================================================================
# Pipeline Functions
# =============================================================================


def design_single_beam(
    *,
    units: str,
    beam_id: str,
    story: str,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    span_mm: float,
    cover_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    mu_knm: float,
    vu_kn: float,
    case_id: str = "CASE-1",
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    include_detailing: bool = True,
    stirrup_dia_mm: float = 8.0,
    stirrup_spacing_start_mm: float = 150.0,
    stirrup_spacing_mid_mm: float = 200.0,
    stirrup_spacing_end_mm: float = 150.0,
    deflection_params: Optional[Dict[str, Any]] = None,
    crack_width_params: Optional[Dict[str, Any]] = None,
) -> BeamDesignOutput:
    """
    Run complete beam design pipeline for a single beam/case.

    This is the canonical entry point that CLI and job_runner should use.

    Args:
        units: Units specifier (must be 'IS456' or equivalent).
        beam_id: Beam identifier.
        story: Story/floor identifier.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        span_mm: Span length (mm).
        cover_mm: Clear cover (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        mu_knm: Factored moment (kN·m).
        vu_kn: Factored shear (kN).
        case_id: Load case identifier.
        d_dash_mm: Compression steel depth (mm).
        asv_mm2: Stirrup area (mm²).
        pt_percent: Tension steel percentage (optional).
        include_detailing: Generate detailing output.
        stirrup_dia_mm: Stirrup diameter for detailing.
        stirrup_spacing_*: Stirrup spacing for zones.
        deflection_params: Deflection check parameters.
        crack_width_params: Crack width check parameters.

    Returns:
        BeamDesignOutput with complete design results.

    Raises:
        UnitsValidationError: If units parameter is invalid.
    """
    # Validate units at boundary
    validated_units = validate_units(units)

    # Run design via existing API
    case_result = api.design_beam_is456(
        units=validated_units,
        case_id=case_id,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        d_dash_mm=d_dash_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        deflection_params=deflection_params,
        crack_width_params=crack_width_params,
    )

    # Build canonical output
    geometry = BeamGeometry(
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        span_mm=span_mm,
        cover_mm=cover_mm,
        d_dash_mm=d_dash_mm,
    )

    materials = BeamMaterials(
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
    )

    loads = BeamLoads(
        case_id=case_id,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
    )

    # Extract flexure output
    flexure = FlexureOutput(
        ast_required_mm2=case_result.flexure.ast_required,
        asc_required_mm2=case_result.flexure.asc_required,
        xu_mm=case_result.flexure.xu,
        xu_max_mm=case_result.flexure.xu_max,
        mu_lim_knm=case_result.flexure.mu_lim,
        xu_d_ratio=case_result.flexure.xu / d_mm if d_mm > 0 else 0.0,
        section_type=_section_type_str(case_result.flexure.section_type),
        is_safe=case_result.flexure.is_safe,
        utilization=case_result.utilizations.get("flexure", 0.0),
        remarks=case_result.flexure.error_message,
    )

    # Extract shear output
    shear = ShearOutput(
        tau_v_nmm2=case_result.shear.tv,
        tau_c_nmm2=case_result.shear.tc,
        tau_c_max_nmm2=case_result.shear.tc_max,
        vus_kn=case_result.shear.vus,
        sv_required_mm=case_result.shear.spacing,
        is_safe=case_result.shear.is_safe,
        utilization=case_result.utilizations.get("shear", 0.0),
        remarks=case_result.shear.remarks,
    )

    # Extract serviceability (if available)
    serviceability = ServiceabilityOutput()
    if case_result.deflection is not None:
        serviceability.deflection_status = (
            "ok" if case_result.deflection.is_ok else "fail"
        )
        serviceability.deflection_ok = case_result.deflection.is_ok
        serviceability.deflection_remarks = case_result.deflection.remarks
        serviceability.deflection_utilization = case_result.utilizations.get(
            "deflection"
        )
    if case_result.crack_width is not None:
        serviceability.crack_width_status = (
            "ok" if case_result.crack_width.is_ok else "fail"
        )
        serviceability.crack_width_ok = case_result.crack_width.is_ok
        serviceability.crack_width_remarks = case_result.crack_width.remarks
        serviceability.crack_width_utilization = case_result.utilizations.get(
            "crack_width"
        )

    # Generate detailing if requested
    detailing_output = None
    if include_detailing:
        try:
            detailing_result = detailing.create_beam_detailing(
                beam_id=beam_id,
                story=story,
                b=b_mm,
                D=D_mm,
                span=span_mm,
                cover=cover_mm,
                fck=fck_nmm2,
                fy=fy_nmm2,
                ast_start=case_result.flexure.ast_required,
                ast_mid=case_result.flexure.ast_required,
                ast_end=case_result.flexure.ast_required,
                asc_start=case_result.flexure.asc_required,
                asc_mid=case_result.flexure.asc_required,
                asc_end=case_result.flexure.asc_required,
                stirrup_dia=stirrup_dia_mm,
                stirrup_spacing_start=stirrup_spacing_start_mm,
                stirrup_spacing_mid=stirrup_spacing_mid_mm,
                stirrup_spacing_end=stirrup_spacing_end_mm,
            )

            detailing_output = DetailingOutput(
                ld_tension_mm=detailing_result.ld_tension,
                lap_length_mm=detailing_result.lap_length,
                bottom_bars=[
                    {
                        "count": bar.count,
                        "diameter": bar.diameter,
                        "callout": bar.callout(),
                    }
                    for bar in detailing_result.bottom_bars
                ],
                top_bars=[
                    {
                        "count": bar.count,
                        "diameter": bar.diameter,
                        "callout": bar.callout(),
                    }
                    for bar in detailing_result.top_bars
                ],
                stirrups=[
                    {
                        "diameter": stir.diameter,
                        "spacing": stir.spacing,
                        "callout": stir.callout(),
                    }
                    for stir in detailing_result.stirrups
                ],
            )
        except Exception:
            # Detailing is optional; don't fail the whole design
            pass

    # Determine governing check
    governing_check = ""
    if case_result.failed_checks:
        governing_check = case_result.failed_checks[0]
    elif case_result.utilizations:
        governing_check = max(
            case_result.utilizations, key=lambda k: case_result.utilizations[k]
        )

    return BeamDesignOutput(
        schema_version=SCHEMA_VERSION,
        code="IS456",
        units=validated_units,
        beam_id=beam_id,
        story=story,
        geometry=geometry,
        materials=materials,
        loads=loads,
        flexure=flexure,
        shear=shear,
        serviceability=serviceability,
        detailing=detailing_output,
        is_ok=case_result.is_ok,
        governing_utilization=case_result.governing_utilization,
        governing_check=governing_check,
        remarks=case_result.remarks,
    )


def design_multiple_beams(
    *,
    units: str,
    beams: Sequence[Dict[str, Any]],
    include_detailing: bool = True,
) -> MultiBeamOutput:
    """
    Design multiple beams and return unified output.

    Args:
        units: Units specifier.
        beams: List of beam parameter dicts.
        include_detailing: Generate detailing for each beam.

    Returns:
        MultiBeamOutput with all beam results.
    """
    validated_units = validate_units(units)

    results = []
    pass_count = 0
    fail_count = 0

    for beam_params in beams:
        result = design_single_beam(
            units=validated_units,
            beam_id=beam_params.get("beam_id", "BEAM"),
            story=beam_params.get("story", "STORY"),
            b_mm=float(beam_params["b_mm"]),
            D_mm=float(beam_params["D_mm"]),
            d_mm=float(beam_params["d_mm"]),
            span_mm=float(beam_params.get("span_mm", 4000)),
            cover_mm=float(beam_params.get("cover_mm", 40)),
            fck_nmm2=float(beam_params["fck_nmm2"]),
            fy_nmm2=float(beam_params["fy_nmm2"]),
            mu_knm=float(beam_params["mu_knm"]),
            vu_kn=float(beam_params["vu_kn"]),
            case_id=beam_params.get("case_id", "CASE-1"),
            d_dash_mm=float(beam_params.get("d_dash_mm", 50)),
            asv_mm2=float(beam_params.get("asv_mm2", 100)),
            include_detailing=include_detailing,
            stirrup_dia_mm=float(beam_params.get("stirrup_dia_mm", 8)),
        )
        results.append(result)

        if result.is_ok:
            pass_count += 1
        else:
            fail_count += 1

    return MultiBeamOutput(
        schema_version=SCHEMA_VERSION,
        code="IS456",
        units=validated_units,
        beams=results,
        summary={
            "total_beams": len(results),
            "passed": pass_count,
            "failed": fail_count,
            "pass_rate": pass_count / len(results) if results else 0.0,
        },
    )


def _section_type_str(section_type) -> str:
    """Convert section type enum to string."""
    if hasattr(section_type, "name"):
        return section_type.name
    elif hasattr(section_type, "value"):
        return str(section_type.value)
    else:
        return str(section_type)
