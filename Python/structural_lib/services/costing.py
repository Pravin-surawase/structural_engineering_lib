# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Cost calculation utilities for structural elements."""

from __future__ import annotations

from dataclasses import dataclass, field

STEEL_DENSITY_KG_PER_M3 = 7850.0
DEFAULT_CONCRETE_GRADE = 25


@dataclass
class CostProfile:
    """Regional cost data for materials and labor.

    Based on CPWD DSR 2023 (India national average).
    Users can override with regional data.
    """

    currency: str = "INR"

    # Material costs per unit
    concrete_costs: dict[int, float] = field(
        default_factory=lambda: {
            20: 6200,
            25: 6700,
            30: 7200,
            35: 7700,
            40: 8200,
        }
    )
    steel_cost_per_kg: float = 72.0  # Fe500 baseline
    formwork_cost_per_m2: float = 500.0

    # Labor modifiers
    congestion_threshold_pt: float = 2.5  # Steel percentage
    congestion_multiplier: float = 1.2

    # Regional adjustment
    location_factor: float = 1.0  # 1.0 = national average

    # Wastage and labor rates (used by detailed cost breakdowns)
    wastage_factor: float = 1.05  # 5% wastage default
    base_labor_rate_per_day: float = 800.0
    labor_productivity_m3_per_day: float = 5.0


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a beam design."""

    concrete_cost: float
    steel_cost: float
    formwork_cost: float
    labor_adjustment: float
    total_cost: float
    currency: str = "INR"

    def to_dict(self) -> dict:
        return {
            "concrete": self.concrete_cost,
            "steel": self.steel_cost,
            "formwork": self.formwork_cost,
            "labor_adjustment": self.labor_adjustment,
            "total": self.total_cost,
            "currency": self.currency,
        }


def calculate_concrete_volume(b_mm: float, D_mm: float, span_mm: float) -> float:
    """Calculate concrete volume in m^3.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Volume in m^3
    """
    # Convert mm to meters
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    return b_m * D_m * span_m


def calculate_steel_weight(ast_mm2: float, span_mm: float) -> float:
    """Calculate steel weight in kg.

    Args:
        ast_mm2: Steel area (mm^2)
        span_mm: Beam span (mm)

    Returns:
        Weight in kg
    """
    ast_m2 = ast_mm2 / 1_000_000  # mm^2 to m^2
    span_m = span_mm / 1000
    volume_m3 = ast_m2 * span_m
    return volume_m3 * STEEL_DENSITY_KG_PER_M3


def calculate_formwork_area(b_mm: float, D_mm: float, span_mm: float) -> float:
    """Calculate formwork surface area in m^2.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Surface area in m^2
    """
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    # Formwork needed: bottom + 2 sides (top open for pouring)
    bottom = b_m * span_m
    sides = 2 * D_m * span_m

    return bottom + sides


def calculate_beam_cost(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    ast_mm2: float,
    fck_nmm2: int,
    steel_percentage: float,
    cost_profile: CostProfile,
) -> CostBreakdown:
    """Calculate total cost for a beam design.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)
        ast_mm2: Tension steel area (mm^2)
        fck_nmm2: Concrete grade (N/mm^2)
        steel_percentage: pt = 100 * Ast / (b*d)
        cost_profile: Regional cost data

    Returns:
        CostBreakdown with detailed costs
    """
    concrete_vol_m3 = calculate_concrete_volume(b_mm, D_mm, span_mm)
    steel_weight_kg = calculate_steel_weight(ast_mm2, span_mm)
    formwork_area_m2 = calculate_formwork_area(b_mm, D_mm, span_mm)

    concrete_rate = cost_profile.concrete_costs.get(fck_nmm2, 6700)
    concrete_cost = concrete_vol_m3 * concrete_rate

    steel_cost = steel_weight_kg * cost_profile.steel_cost_per_kg

    formwork_cost = formwork_area_m2 * cost_profile.formwork_cost_per_m2

    # Labor adjustment (congestion penalty)
    labor_adjustment = 0.0
    if steel_percentage > cost_profile.congestion_threshold_pt:
        penalty_rate = cost_profile.congestion_multiplier - 1.0
        labor_adjustment = steel_cost * penalty_rate

    subtotal = concrete_cost + steel_cost + formwork_cost + labor_adjustment
    total = subtotal * cost_profile.location_factor

    return CostBreakdown(
        concrete_cost=round(concrete_cost, 2),
        steel_cost=round(steel_cost, 2),
        formwork_cost=round(formwork_cost, 2),
        labor_adjustment=round(labor_adjustment, 2),
        total_cost=round(total, 2),
        currency=cost_profile.currency,
    )


def _parse_concrete_grade(grade: str | None) -> int | None:
    if not grade:
        return None
    normalized = grade.strip().upper()
    if normalized.startswith("M"):
        normalized = normalized[1:]
    try:
        return int(float(normalized))
    except ValueError:
        return None


def calculate_concrete_cost(
    volume_m3: float, grade: str, cost_profile: CostProfile
) -> float:
    """Calculate concrete cost including wastage.

    Args:
        volume_m3: Concrete volume in cubic meters (m^3)
        grade: Concrete grade (e.g., "M20", "M25", "M30")
        cost_profile: Cost profile with rates

    Returns:
        Total concrete cost in INR
    """
    if volume_m3 < 0:
        raise ValueError("Volume cannot be negative")

    if volume_m3 == 0:
        return 0.0

    grade_key = _parse_concrete_grade(grade)
    rate = None
    if grade_key is not None:
        rate = cost_profile.concrete_costs.get(grade_key)
    if rate is None:
        rate = cost_profile.concrete_costs.get(DEFAULT_CONCRETE_GRADE, 6700.0)

    volume_with_wastage = volume_m3 * cost_profile.wastage_factor

    return volume_with_wastage * rate


def calculate_steel_cost(
    weight_kg: float, grade: str, cost_profile: CostProfile
) -> float:
    """Calculate steel reinforcement cost including wastage.

    Args:
        weight_kg: Total steel weight in kilograms (kg)
        grade: Steel grade (e.g., "Fe415", "Fe500")
        cost_profile: Cost profile with rates

    Returns:
        Total steel cost in INR
    """
    if weight_kg < 0:
        raise ValueError("Weight cannot be negative")

    if weight_kg == 0:
        return 0.0

    weight_with_wastage = weight_kg * cost_profile.wastage_factor

    return weight_with_wastage * cost_profile.steel_cost_per_kg


def calculate_formwork_cost(area_m2: float, cost_profile: CostProfile) -> float:
    """Calculate formwork cost.

    Args:
        area_m2: Formwork contact area in square meters (m^2)
        cost_profile: Cost profile with rates

    Returns:
        Total formwork cost in INR
    """
    if area_m2 < 0:
        raise ValueError("Area cannot be negative")

    if area_m2 == 0:
        return 0.0

    return area_m2 * cost_profile.formwork_cost_per_m2


def calculate_total_beam_cost(beam_data: dict, cost_profile: CostProfile) -> dict:
    """Calculate total cost for an RC beam with congestion penalty.

    Args:
        beam_data: Dictionary with beam dimensions and reinforcement:
            - b_mm: Width in mm (required)
            - d_mm: Effective depth in mm (required)
            - h_mm: Total depth in mm (required if D_mm not provided)
            - D_mm: Total depth in mm (optional alias for h_mm)
            - length_m: Beam length in meters (required)
            - ast_mm2: Tension steel area in mm^2 (required)
            - asc_mm2: Compression steel area in mm^2 (optional, default 0)
            - fck: Concrete grade strength in N/mm^2 (e.g., 20, 25, 30) (required)
            - fy: Steel grade strength in N/mm^2 (e.g., 415, 500) (required)

    Returns:
        Dictionary with cost breakdown:
            - concrete_cost: INR
            - steel_cost: INR
            - formwork_cost: INR
            - labor_cost: INR
            - congestion_penalty: INR
            - total_cost: INR (location factor applied)
            - reinforcement_percentage: % (for reference)

    Raises:
        ValueError: If required keys are missing or values are invalid

    Notes:
        - Units: Internal calculations use mm, converts to SI (m^3, kg, m^2)
        - Congestion penalty: cost_profile.congestion_multiplier if pt exceeds threshold
        - Steel density: 7850 kg/m^3
    """
    required_keys = ["b_mm", "d_mm", "length_m", "ast_mm2", "fck", "fy"]
    for key in required_keys:
        if key not in beam_data:
            raise ValueError(f"Missing required key: {key}")

    if "h_mm" in beam_data:
        h_mm = beam_data["h_mm"]
    elif "D_mm" in beam_data:
        h_mm = beam_data["D_mm"]
    else:
        raise ValueError("Missing required key: h_mm")

    b_mm = beam_data["b_mm"]
    d_mm = beam_data["d_mm"]
    length_m = beam_data["length_m"]
    ast_mm2 = beam_data["ast_mm2"]
    asc_mm2 = beam_data.get("asc_mm2", 0.0)
    fck = beam_data["fck"]
    fy = beam_data["fy"]

    if b_mm <= 0 or d_mm <= 0 or h_mm <= 0 or length_m <= 0:
        raise ValueError("All dimensions must be positive")
    if ast_mm2 < 0 or asc_mm2 < 0:
        raise ValueError("Steel areas cannot be negative")
    if fck <= 0 or fy <= 0:
        raise ValueError("Material grades must be positive")
    if cost_profile.labor_productivity_m3_per_day <= 0:
        raise ValueError("Labor productivity must be positive")

    length_mm = length_m * 1000.0

    volume_mm3 = b_mm * h_mm * length_mm
    volume_m3 = volume_mm3 / 1e9

    grade_str = f"M{int(fck)}"
    concrete_cost = calculate_concrete_cost(volume_m3, grade_str, cost_profile)

    total_steel_area_mm2 = ast_mm2 + asc_mm2
    steel_volume_mm3 = total_steel_area_mm2 * length_mm
    steel_volume_m3 = steel_volume_mm3 / 1e9
    steel_weight_kg = steel_volume_m3 * STEEL_DENSITY_KG_PER_M3

    grade_str_steel = f"Fe{int(fy)}"
    steel_cost = calculate_steel_cost(steel_weight_kg, grade_str_steel, cost_profile)

    perimeter_mm = b_mm + 2 * h_mm
    formwork_area_mm2 = perimeter_mm * length_mm
    formwork_area_m2 = formwork_area_mm2 / 1e6

    formwork_cost = calculate_formwork_cost(formwork_area_m2, cost_profile)

    labor_days = volume_m3 / cost_profile.labor_productivity_m3_per_day
    base_labor_cost = labor_days * cost_profile.base_labor_rate_per_day

    pt = (ast_mm2 / (b_mm * d_mm)) * 100.0

    if pt > cost_profile.congestion_threshold_pt:
        labor_multiplier = cost_profile.congestion_multiplier
        labor_cost = base_labor_cost * labor_multiplier
        congestion_penalty = labor_cost - base_labor_cost
    else:
        labor_cost = base_labor_cost
        congestion_penalty = 0.0

    subtotal = concrete_cost + steel_cost + formwork_cost + labor_cost
    total_cost = subtotal * cost_profile.location_factor

    return {
        "concrete_cost": concrete_cost,
        "steel_cost": steel_cost,
        "formwork_cost": formwork_cost,
        "labor_cost": labor_cost,
        "congestion_penalty": congestion_penalty,
        "total_cost": total_cost,
        "reinforcement_percentage": pt,
    }
