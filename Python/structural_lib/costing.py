"""Cost calculation utilities for structural elements."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CostProfile:
    """Regional cost data for materials and labor.

    Based on CPWD DSR 2023 (India national average).
    Users can override with regional data.
    """

    currency: str = "INR"

    # Material costs per unit
    concrete_costs: Dict[int, float] = field(
        default_factory=lambda: {
            20: 6200,
            25: 6700,
            30: 7200,
            35: 7700,
            40: 8200,
        }
    )
    steel_cost_per_kg: float = 72.0  # Fe500
    formwork_cost_per_m2: float = 500.0

    # Labor modifiers
    congestion_threshold_pt: float = 2.5  # Steel percentage
    congestion_multiplier: float = 1.2

    # Regional adjustment
    location_factor: float = 1.0  # 1.0 = national average


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
    """Calculate concrete volume in m³.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Volume in m³
    """
    # Convert mm to meters
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    return b_m * D_m * span_m


def calculate_steel_weight(ast_mm2: float, span_mm: float) -> float:
    """Calculate steel weight in kg.

    Args:
        ast_mm2: Steel area (mm²)
        span_mm: Beam span (mm)

    Returns:
        Weight in kg
    """
    # Steel density: 7850 kg/m³
    ast_m2 = ast_mm2 / 1_000_000  # mm² to m²
    span_m = span_mm / 1000
    volume_m3 = ast_m2 * span_m
    return volume_m3 * 7850


def calculate_formwork_area(b_mm: float, D_mm: float, span_mm: float) -> float:
    """Calculate formwork surface area in m².

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Surface area in m²
    """
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    # Formwork needed: bottom + 2 sides
    # (Top is open for concrete pouring)
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
        ast_mm2: Tension steel area (mm²)
        fck_nmm2: Concrete grade (N/mm²)
        steel_percentage: pt = 100 * Ast / (b*d)
        cost_profile: Regional cost data

    Returns:
        CostBreakdown with detailed costs
    """
    # Material quantities
    concrete_vol_m3 = calculate_concrete_volume(b_mm, D_mm, span_mm)
    steel_weight_kg = calculate_steel_weight(ast_mm2, span_mm)
    formwork_area_m2 = calculate_formwork_area(b_mm, D_mm, span_mm)

    # Material costs
    concrete_rate = cost_profile.concrete_costs.get(fck_nmm2, 6700)
    concrete_cost = concrete_vol_m3 * concrete_rate

    steel_cost = steel_weight_kg * cost_profile.steel_cost_per_kg

    formwork_cost = formwork_area_m2 * cost_profile.formwork_cost_per_m2

    # Labor adjustment (congestion penalty)
    labor_adjustment = 0.0
    if steel_percentage > cost_profile.congestion_threshold_pt:
        # Apply penalty to steel placement labor
        penalty_rate = cost_profile.congestion_multiplier - 1.0
        labor_adjustment = steel_cost * penalty_rate

    # Total (apply location factor)
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
