"""Portable WP07 construction request and output records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from structural_lib.beam.bar_paths import BarPathOutput, BarPathRole


class SpliceKind(StrEnum):
    LAP = "lap"
    COUPLER = "coupler"


class FormworkFaceCategory(StrEnum):
    SOFFIT = "soffit"
    SIDE_LEFT = "side_left"
    SIDE_RIGHT = "side_right"
    END_BULKHEAD = "end_bulkhead"
    SLAB_INTERFACE = "slab_interface"
    SUPPORT_INTERFACE = "support_interface"
    OTHER_DECLARED = "other_declared"


class FormworkMeasurementState(StrEnum):
    INCLUDED = "included"
    EXCLUDED = "excluded"


class CostCategory(StrEnum):
    MATERIAL = "material"
    FORMWORK = "formwork"
    COUPLER = "coupler"
    LABOUR = "labour"
    PLANT = "plant"


class CostBasis(StrEnum):
    STEEL_SCHEDULED_MASS_KG = "steel_scheduled_mass_kg"
    STEEL_STOCK_MASS_KG = "steel_stock_mass_kg"
    CONCRETE_VOLUME_M3 = "concrete_volume_m3"
    FORMWORK_AREA_M2 = "formwork_area_m2"
    COUPLER_COUNT = "coupler_count"


class WastePricingBasis(StrEnum):
    SCHEDULED_STEEL = "scheduled_steel"
    PURCHASED_STOCK = "purchased_stock"


@dataclass(frozen=True)
class ShapeConvention:
    convention_id: str
    revision_id: str
    length_basis: str = "resolved_centreline_v1"


@dataclass(frozen=True)
class CuttingStockPolicy:
    policy_id: str
    revision_id: str
    stock_lengths_mm: tuple[float, ...]
    kerf_mm: float
    reusable_offcut_min_mm: float
    allocation_method: str = "first_fit_decreasing_v1"


@dataclass(frozen=True)
class SpliceRecord:
    splice_id: str
    kind: SpliceKind
    station_x_mm: float
    qualification_reference: str
    coupler_count: int = 0


@dataclass(frozen=True)
class LinkPlacementZone:
    zone_id: str
    bar_mark: str
    start_station_x_mm: float
    end_station_x_mm: float
    spacing_mm: float
    include_start: bool
    include_end: bool


@dataclass(frozen=True)
class BbsRequest:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    schedule_result_id: str
    schedule_output_payload_id: str
    schedule: BarPathOutput
    shape_convention: ShapeConvention
    stock_policy: CuttingStockPolicy
    steel_density_kg_per_m3: float
    splice_records: tuple[SpliceRecord, ...] = ()
    link_zones: tuple[LinkPlacementZone, ...] = ()
    station_tolerance_mm: float = 1e-6


@dataclass(frozen=True)
class ShapeDimension:
    dimension_id: str
    segment_kind: str
    centreline_length_mm: float
    bend_radius_mm: float | None
    bend_angle_degrees: float | None


@dataclass(frozen=True)
class BbsRow:
    bar_mark: str
    role: BarPathRole
    diameter_mm: float
    steel_grade_n_per_mm2: float
    bundle_size: int
    placement_count: int
    scheduled_bar_count: int
    shape_code: str
    dimensions: tuple[ShapeDimension, ...]
    centreline_developed_length_each_mm: float
    fabrication_cut_length_each_mm: float
    scheduled_cut_length_mm: float
    theoretical_mass_kg: float
    source_path_ids: tuple[str, ...]
    splice_ids: tuple[str, ...]


@dataclass(frozen=True)
class PlacedLinkZone:
    zone_id: str
    bar_mark: str
    stations_x_mm: tuple[float, ...]
    count: int


@dataclass(frozen=True)
class StockCut:
    cut_id: str
    bar_mark: str
    length_mm: float


@dataclass(frozen=True)
class StockPiece:
    stock_piece_id: str
    diameter_mm: float
    steel_grade_n_per_mm2: float
    stock_length_mm: float
    cuts: tuple[StockCut, ...]
    kerf_length_mm: float
    reusable_offcut_length_mm: float
    waste_length_mm: float


@dataclass(frozen=True)
class CouplerItem:
    splice_id: str
    station_x_mm: float
    count: int
    qualification_reference: str


@dataclass(frozen=True)
class BbsOutput:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    schedule_result_id: str
    shape_convention_revision_id: str
    cutting_policy_revision_id: str
    rows: tuple[BbsRow, ...]
    link_zones: tuple[PlacedLinkZone, ...]
    stock_pieces: tuple[StockPiece, ...]
    couplers: tuple[CouplerItem, ...]
    scheduled_cut_length_mm: float
    stock_length_mm: float
    kerf_length_mm: float
    reusable_offcut_length_mm: float
    waste_length_mm: float
    scheduled_steel_mass_kg: float
    purchased_stock_mass_kg: float
    allocation_optimality: str
    passed: bool


@dataclass(frozen=True)
class VolumeDeduction:
    deduction_id: str
    volume_m3: float
    ownership_id: str
    reason: str


@dataclass(frozen=True)
class AreaDeduction:
    deduction_id: str
    area_mm2: float
    ownership_id: str
    reason: str


@dataclass(frozen=True)
class ConcreteNetSegment:
    segment_id: str
    member_id: str
    material_id: str
    ownership_id: str
    cross_section_area_mm2: float
    physical_length_mm: float
    owns_monolithic_interface: bool
    deductions: tuple[VolumeDeduction, ...] = ()


@dataclass(frozen=True)
class FormworkContactFace:
    face_id: str
    member_id: str
    category: FormworkFaceCategory
    ownership_id: str
    gross_area_mm2: float
    measurement_state: FormworkMeasurementState
    exclusion_reason: str | None = None
    deductions: tuple[AreaDeduction, ...] = ()


@dataclass(frozen=True)
class ConstructionQuantityRequest:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    bbs_result_id: str
    bbs_output_payload_id: str
    bbs: BbsOutput
    concrete_overlap_policy_id: str
    formwork_measurement_policy_id: str
    concrete_segments: tuple[ConcreteNetSegment, ...]
    formwork_faces: tuple[FormworkContactFace, ...]


@dataclass(frozen=True)
class QuantitySteelItem:
    bar_mark: str
    diameter_mm: float
    steel_grade_n_per_mm2: float
    scheduled_bar_count: int
    scheduled_cut_length_mm: float
    scheduled_mass_kg: float


@dataclass(frozen=True)
class ConcreteQuantity:
    segment_id: str
    material_id: str
    ownership_id: str
    gross_volume_m3: float
    deduction_volume_m3: float
    net_volume_m3: float
    owns_monolithic_interface: bool


@dataclass(frozen=True)
class FormworkQuantity:
    face_id: str
    category: FormworkFaceCategory
    ownership_id: str
    measurement_state: FormworkMeasurementState
    gross_area_m2: float
    deduction_area_m2: float
    net_area_m2: float
    exclusion_reason: str | None


@dataclass(frozen=True)
class WasteLedger:
    kerf_length_mm: float
    reusable_offcut_length_mm: float
    unreusable_waste_length_mm: float


@dataclass(frozen=True)
class ConstructionQuantityOutput:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    bbs_result_id: str
    concrete_overlap_policy_id: str
    formwork_measurement_policy_id: str
    steel_items: tuple[QuantitySteelItem, ...]
    concrete_items: tuple[ConcreteQuantity, ...]
    formwork_items: tuple[FormworkQuantity, ...]
    waste: WasteLedger
    steel_scheduled_mass_kg: float
    steel_stock_mass_kg: float
    concrete_volume_m3: float
    formwork_area_m2: float
    coupler_count: int
    direct_cost: None = None


@dataclass(frozen=True)
class CostRate:
    rate_id: str
    category: CostCategory
    basis: CostBasis
    description: str
    unit_rate_decimal: str
    source_reference: str


@dataclass(frozen=True)
class HumanCostScope:
    included_categories: tuple[CostCategory, ...]
    excluded_categories: tuple[CostCategory, ...]


@dataclass(frozen=True)
class MeasuredRateProfile:
    profile_id: str
    revision_id: str
    currency: str
    valuation_date: str
    time_zone: str
    geography: str
    source: str
    scope: HumanCostScope
    rates: tuple[CostRate, ...]
    waste_pricing_basis: WastePricingBasis
    overhead_percent_decimal: str
    tax_percent_decimal: str


@dataclass(frozen=True)
class ConstructionCostRequest:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    quantity_result_id: str
    quantity_output_payload_id: str
    quantities: ConstructionQuantityOutput
    rate_profile: MeasuredRateProfile


@dataclass(frozen=True)
class CostLine:
    rate_id: str
    category: CostCategory
    basis: CostBasis
    description: str
    source_quantity_result_id: str
    quantity_decimal: str
    unit: str
    unit_rate_decimal: str
    amount_decimal: str


@dataclass(frozen=True)
class ConstructionCostOutput:
    profile_id: str
    project_basis_id: str
    member_id: str
    detail_revision_id: str
    quantity_result_id: str
    rate_profile_id: str
    rate_profile_revision_id: str
    currency: str
    valuation_date: str
    geography: str
    source: str
    lines: tuple[CostLine, ...]
    included_categories: tuple[CostCategory, ...]
    excluded_categories: tuple[CostCategory, ...]
    direct_subtotal_decimal: str
    overhead_decimal: str
    pre_tax_total_decimal: str
    tax_decimal: str
    total_decimal: str
