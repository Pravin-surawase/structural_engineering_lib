"""
Bar Bending Schedule (BBS) Module — IS 2502:1999 / SP 34:1987

This module generates Bar Bending Schedules (BBS) and Bill of Materials (BOM)
from beam detailing results. Outputs are deterministic and suitable for
fabrication and site use.

References:
- IS 2502:1999 (Steel for Reinforcement)
- SP 34:1987 (Handbook on Concrete Reinforcement and Detailing)
- IS 1786:2008 (High Strength Deformed Steel Bars)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict
import csv
import json
from pathlib import Path
import math
import re

from .detailing import BeamDetailingResult
from .types import CuttingAssignment, CuttingPlan


# =============================================================================
# Constants
# =============================================================================

# Unit weight of steel (kg/m³) — IS 1786
STEEL_DENSITY_KG_M3 = 7850.0

# Standard stock lengths available (mm)
STANDARD_STOCK_LENGTHS_MM = [6000, 7500, 9000, 12000]

# Standard bar shapes per IS 2502 / SP 34
BAR_SHAPES = {
    "A": "Straight bar",
    "B": "Bent-up bar (cranked)",
    "C": "L-shaped (90° hook one end)",
    "D": "U-bar (180° hook both ends)",
    "E": "Stirrup (closed rectangular)",
    "F": "Open stirrup (U-shape)",
    "G": "Helical / spiral",
    "H": "Hairpin (U with extended legs)",
}

# Rounding rules (per SP 34 / site practice)
LENGTH_ROUND_MM = 10  # Round cut lengths to nearest 10mm
WEIGHT_ROUND_KG = 0.01  # Round weights to 2 decimal places
WEIGHT_ROUND_DECIMALS = 2


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class BBSLineItem:
    """Single line item in a Bar Bending Schedule."""

    bar_mark: str  # Unique identifier (e.g., "B1-B-S-D16-01")
    member_id: str  # Beam/element ID
    location: str  # "bottom", "top", "stirrup"
    zone: str  # "start", "mid", "end", or "full"
    shape_code: str  # Shape per IS 2502 (A, B, C, D, E, etc.)
    diameter_mm: float  # Bar diameter
    no_of_bars: int  # Quantity
    cut_length_mm: float  # Total length including hooks/bends
    total_length_mm: float  # no_of_bars × cut_length
    unit_weight_kg: float  # Weight per bar
    total_weight_kg: float  # Total weight

    # Optional bend details
    a_mm: float = 0.0  # Dimension 'a' for shape
    b_mm: float = 0.0  # Dimension 'b' for shape
    c_mm: float = 0.0  # Dimension 'c' for shape
    d_mm: float = 0.0  # Dimension 'd' for shape
    bend_angle: float = 0.0  # Primary bend angle (degrees)
    hook_length_mm: float = 0.0  # Hook length (if applicable)

    remarks: str = ""


@dataclass
class BBSummary:
    """Summary of Bar Bending Schedule for a beam or project."""

    member_id: str
    total_items: int
    total_bars: int
    total_length_m: float  # Total length in meters
    total_weight_kg: float

    # Breakdown by diameter
    weight_by_diameter: Dict[float, float] = field(default_factory=dict)
    length_by_diameter: Dict[float, float] = field(default_factory=dict)
    count_by_diameter: Dict[float, int] = field(default_factory=dict)


@dataclass
class BBSDocument:
    """Complete Bar Bending Schedule document."""

    project_name: str
    member_ids: List[str]
    items: List[BBSLineItem]
    summary: BBSummary
    created_by: str = "structural_engineering_lib"
    version: str = "1.0"


# =============================================================================
# Weight Calculation
# =============================================================================


def calculate_bar_weight(
    diameter_mm: float,
    length_mm: float,
    round_weight: bool = True,
) -> float:
    """
    Calculate weight of a single bar.

    Weight = (π × d² / 4) × length × density

    Args:
        diameter_mm: Bar diameter (mm)
        length_mm: Bar length (mm)

    Returns:
        Weight in kg. Rounded to WEIGHT_ROUND_KG by default.
    """
    # Convert to meters
    d_m = diameter_mm / 1000
    l_m = length_mm / 1000

    # Cross-sectional area (m²)
    area_m2 = math.pi * (d_m / 2) ** 2

    # Weight (kg)
    weight = area_m2 * l_m * STEEL_DENSITY_KG_M3

    return round(weight, WEIGHT_ROUND_DECIMALS) if round_weight else weight


def calculate_unit_weight_per_meter(diameter_mm: float) -> float:
    """
    Calculate unit weight per meter for a bar diameter.

    This is useful for quick calculations.

    Args:
        diameter_mm: Bar diameter (mm)

    Returns:
        Weight in kg/m
    """
    return calculate_bar_weight(diameter_mm, 1000)


# Standard unit weights (kg/m) — pre-calculated for common diameters
UNIT_WEIGHTS_KG_M = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    16: 1.579,
    20: 2.466,
    25: 3.853,
    32: 6.313,
}


# =============================================================================
# Cut Length Calculations
# =============================================================================


def calculate_hook_length(
    diameter_mm: float,
    hook_angle: float = 90.0,
) -> float:
    """
    Calculate hook length per IS 456 Cl 26.2.2.1.

    Standard hooks:
    - 90° hook: 8d minimum
    - 180° hook: 4d beyond bend + 4d radius = 8d equivalent

    Args:
        diameter_mm: Bar diameter (mm)
        hook_angle: Hook angle in degrees

    Returns:
        Hook length (mm)
    """
    if hook_angle == 180:
        return 8 * diameter_mm  # U-bend equivalent
    elif hook_angle == 90:
        return 8 * diameter_mm  # Standard 90° hook
    elif hook_angle == 135:
        return max(10 * diameter_mm, 75)  # Stirrups: 10d (min 75mm)
    else:
        return 4 * diameter_mm  # Minimum


def calculate_bend_deduction(
    diameter_mm: float,
    bend_angle: float = 90.0,
) -> float:
    """
    Calculate length deduction at bends per IS 2502 / SP 34.

    The actual bar length at a bend is less than the sum of the
    two straight segments due to the curved portion.

    Args:
        diameter_mm: Bar diameter (mm)
        bend_angle: Bend angle in degrees

    Returns:
        Length to deduct (mm) — returns 0 or small value
    """
    # Minimum bend radius = 2d for main bars, 4d for stirrups
    # For simplicity, use 2d and approximate deduction
    if bend_angle == 90:
        return 0.5 * diameter_mm  # Approximate deduction
    elif bend_angle == 135:
        return 0.25 * diameter_mm
    elif bend_angle == 180:
        return 1.0 * diameter_mm
    else:
        return 0.0


def calculate_straight_bar_length(
    span_mm: float,
    cover_mm: float,
    ld_mm: float,
    location: str = "bottom",
    zone: str = "full",
) -> float:
    """
    Calculate cut length for straight main bars.

    Args:
        span_mm: Beam span (mm)
        cover_mm: Clear cover (mm)
        ld_mm: Development length (mm)
        location: "bottom" or "top"
        zone: "full", "start", "mid", "end"

    Returns:
        Cut length (mm)
    """
    if zone == "full":
        # Full-span bar: span + 2×Ld (anchorage at both ends)
        cut_length = span_mm + 2 * ld_mm
    elif zone == "start" or zone == "end":
        # Curtailed bar: half span + Ld + extension past support
        cut_length = span_mm / 2 + ld_mm + 100  # 100mm nominal extension
    elif zone == "mid":
        # Mid-span bar (typically bottom): 60% of span + 2×Ld
        cut_length = 0.6 * span_mm + 2 * ld_mm
    else:
        cut_length = span_mm + 2 * ld_mm

    return round(cut_length / LENGTH_ROUND_MM) * LENGTH_ROUND_MM


def calculate_stirrup_cut_length(
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    stirrup_dia_mm: float,
    hook_length_mm: float = 0,
) -> float:
    """
    Calculate cut length for closed stirrups.

    Perimeter = 2×(width + height) + hook lengths
    Internal dimensions account for cover + stirrup radius.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        cover_mm: Clear cover (mm)
        stirrup_dia_mm: Stirrup diameter (mm)
        hook_length_mm: Hook length (if 0, uses default 10d)

    Returns:
        Cut length (mm)
    """
    # Internal dimensions (centerline): cover to stirrup outside + 0.5d
    inner_width = b_mm - 2 * (cover_mm + 0.5 * stirrup_dia_mm)
    inner_height = D_mm - 2 * (cover_mm + 0.5 * stirrup_dia_mm)

    # Perimeter
    perimeter = 2 * (inner_width + inner_height)

    # Add hook lengths (135° hooks for stirrups)
    if hook_length_mm == 0:
        hook_length_mm = calculate_hook_length(stirrup_dia_mm, 135)

    cut_length = perimeter + 2 * hook_length_mm

    return round(cut_length / LENGTH_ROUND_MM) * LENGTH_ROUND_MM


# =============================================================================
# BBS Generation from Detailing Results
# =============================================================================


def _normalize_member_id(member_id: str) -> str:
    """Normalize member IDs for deterministic bar mark formatting."""
    if member_id is None:
        return "UNKNOWN"
    cleaned = []
    for ch in str(member_id).strip().upper():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in (" ", "-", "_"):
            cleaned.append("-")
    result = "".join(cleaned)
    while "--" in result:
        result = result.replace("--", "-")
    result = result.strip("-")
    return result if result else "UNKNOWN"


def _bar_mark_loc_code(location: str) -> str:
    return {
        "bottom": "B",
        "top": "T",
        "stirrup": "S",
    }.get(location, "X")


def _bar_mark_zone_code(zone: str) -> str:
    return {
        "start": "S",
        "mid": "M",
        "end": "E",
        "full": "F",
    }.get(zone, "X")


def _bar_mark_sort_key(item: BBSLineItem) -> tuple:
    return (
        _normalize_member_id(item.member_id),
        _bar_mark_loc_code(item.location),
        _bar_mark_zone_code(item.zone),
        int(round(item.diameter_mm)),
        item.shape_code,
        int(round(item.cut_length_mm)),
    )


BAR_MARK_PATTERN = re.compile(
    r"(?P<beam_id>[A-Z0-9]+(?:-[A-Z0-9]+)*)-"
    r"(?P<loc>[BTS])-(?P<zone>[SMEF])-D(?P<dia>\d+)-(?P<seq>\d{2})",
    flags=re.IGNORECASE,
)


def parse_bar_mark(mark: str) -> dict | None:
    """Parse a bar mark into its components, or return None if invalid."""
    if mark is None:
        return None
    cleaned = mark.strip()
    if not cleaned:
        return None
    match = BAR_MARK_PATTERN.fullmatch(cleaned)
    if not match:
        return None
    data = match.groupdict()
    return {
        "mark": cleaned.upper(),
        "beam_id": data["beam_id"].upper(),
        "loc": data["loc"].upper(),
        "zone": data["zone"].upper(),
        "dia": int(data["dia"]),
        "seq": int(data["seq"]),
    }


def extract_bar_marks_from_text(text: str) -> List[str]:
    """Extract bar marks from a free-text string."""
    if not text:
        return []
    return [match.group(0).upper() for match in BAR_MARK_PATTERN.finditer(text)]


def extract_bar_marks_from_items(
    items: List[BBSLineItem],
) -> Dict[str, set[str]]:
    """Collect bar marks from BBS items, grouped by beam."""
    marks_by_beam: Dict[str, set[str]] = {}
    for item in items:
        parsed = parse_bar_mark(item.bar_mark)
        if not parsed:
            raise ValueError(f"Invalid bar_mark in items: '{item.bar_mark}'")
        beam_id = parsed["beam_id"]
        marks_by_beam.setdefault(beam_id, set()).add(parsed["mark"])
    return marks_by_beam


def extract_bar_marks_from_bbs_csv(path: str | Path) -> Dict[str, set[str]]:
    """Load bar marks from a BBS CSV file, grouped by beam."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"BBS file not found: {p}")

    marks_by_beam: Dict[str, set[str]] = {}
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "bar_mark" not in reader.fieldnames:
            raise ValueError("BBS CSV missing required 'bar_mark' column.")

        for row in reader:
            mark_raw = (row.get("bar_mark") or "").strip()
            if not mark_raw or mark_raw.upper() == "TOTAL":
                continue
            parsed = parse_bar_mark(mark_raw)
            if not parsed:
                raise ValueError(f"Invalid bar_mark in BBS CSV: '{mark_raw}'")
            beam_id = parsed["beam_id"]
            marks_by_beam.setdefault(beam_id, set()).add(parsed["mark"])

    return marks_by_beam


def assign_bar_marks(items: List[BBSLineItem]) -> List[BBSLineItem]:
    """Assign deterministic, project-unique bar marks in-place."""
    items_sorted = sorted(items, key=_bar_mark_sort_key)
    seq_by_beam: Dict[str, int] = {}

    for item in items_sorted:
        beam_id = _normalize_member_id(item.member_id)
        seq = seq_by_beam.get(beam_id, 0) + 1
        seq_by_beam[beam_id] = seq

        loc_code = _bar_mark_loc_code(item.location)
        zone_code = _bar_mark_zone_code(item.zone)
        dia = int(round(item.diameter_mm))

        item.bar_mark = f"{beam_id}-{loc_code}-{zone_code}-D{dia}-{seq:02d}"

    return items


def generate_bbs_from_detailing(
    detailing: BeamDetailingResult,
    include_hooks: bool = True,
) -> List[BBSLineItem]:
    """
    Generate BBS line items from a BeamDetailingResult.

    Args:
        detailing: Beam detailing result
        include_hooks: Whether to include hook lengths in calculations

    Returns:
        List of BBS line items
    """
    items = []

    # Process bottom bars
    zones = ["start", "mid", "end"]
    for i, (bar_arr, zone) in enumerate(zip(detailing.bottom_bars, zones)):
        if bar_arr.count > 0:
            cut_length = calculate_straight_bar_length(
                span_mm=detailing.span,
                cover_mm=detailing.cover,
                ld_mm=detailing.ld_tension,
                location="bottom",
                zone=zone,
            )

            unit_wt = calculate_bar_weight(bar_arr.diameter, cut_length)
            total_wt = calculate_bar_weight(
                bar_arr.diameter,
                cut_length * bar_arr.count,
                round_weight=False,
            )

            items.append(
                BBSLineItem(
                    bar_mark="",
                    member_id=detailing.beam_id,
                    location="bottom",
                    zone=zone,
                    shape_code="A",  # Straight
                    diameter_mm=bar_arr.diameter,
                    no_of_bars=bar_arr.count,
                    cut_length_mm=cut_length,
                    total_length_mm=cut_length * bar_arr.count,
                    unit_weight_kg=unit_wt,
                    total_weight_kg=round(total_wt, WEIGHT_ROUND_DECIMALS),
                    a_mm=cut_length,
                    remarks=f"Bottom {zone} - {bar_arr.callout()}",
                )
            )

    # Process top bars
    for i, (bar_arr, zone) in enumerate(zip(detailing.top_bars, zones)):
        if bar_arr.count > 0:
            cut_length = calculate_straight_bar_length(
                span_mm=detailing.span,
                cover_mm=detailing.cover,
                ld_mm=detailing.ld_compression,
                location="top",
                zone=zone,
            )

            unit_wt = calculate_bar_weight(bar_arr.diameter, cut_length)
            total_wt = calculate_bar_weight(
                bar_arr.diameter,
                cut_length * bar_arr.count,
                round_weight=False,
            )

            items.append(
                BBSLineItem(
                    bar_mark="",
                    member_id=detailing.beam_id,
                    location="top",
                    zone=zone,
                    shape_code="A",  # Straight
                    diameter_mm=bar_arr.diameter,
                    no_of_bars=bar_arr.count,
                    cut_length_mm=cut_length,
                    total_length_mm=cut_length * bar_arr.count,
                    unit_weight_kg=unit_wt,
                    total_weight_kg=round(total_wt, WEIGHT_ROUND_DECIMALS),
                    a_mm=cut_length,
                    remarks=f"Top {zone} - {bar_arr.callout()}",
                )
            )

    # Process stirrups
    for i, (stirrup, zone) in enumerate(zip(detailing.stirrups, zones)):
        if stirrup.spacing > 0 and stirrup.zone_length > 0:
            # Number of stirrups in zone
            no_of_stirrups = int(stirrup.zone_length / stirrup.spacing) + 1

            cut_length = calculate_stirrup_cut_length(
                b_mm=detailing.b,
                D_mm=detailing.D,
                cover_mm=detailing.cover,
                stirrup_dia_mm=stirrup.diameter,
            )

            unit_wt = calculate_bar_weight(stirrup.diameter, cut_length)
            total_wt = calculate_bar_weight(
                stirrup.diameter,
                cut_length * no_of_stirrups,
                round_weight=False,
            )

            items.append(
                BBSLineItem(
                    bar_mark="",
                    member_id=detailing.beam_id,
                    location="stirrup",
                    zone=zone,
                    shape_code="E",  # Closed stirrup
                    diameter_mm=stirrup.diameter,
                    no_of_bars=no_of_stirrups,
                    cut_length_mm=cut_length,
                    total_length_mm=cut_length * no_of_stirrups,
                    unit_weight_kg=unit_wt,
                    total_weight_kg=round(total_wt, WEIGHT_ROUND_DECIMALS),
                    a_mm=detailing.b - 2 * detailing.cover,  # inner width
                    b_mm=detailing.D - 2 * detailing.cover,  # inner height
                    remarks=f"Stirrup {zone} - {stirrup.callout()}",
                )
            )

    return assign_bar_marks(items)


def calculate_bbs_summary(
    items: List[BBSLineItem],
    member_id: str = "",
) -> BBSummary:
    """
    Calculate summary statistics for BBS items.

    Args:
        items: List of BBS line items
        member_id: Member identifier (or "PROJECT" for aggregate)

    Returns:
        Summary statistics
    """
    total_bars = sum(item.no_of_bars for item in items)
    total_length_mm = sum(item.total_length_mm for item in items)
    weight_by_dia: Dict[float, float] = {}
    length_by_dia: Dict[float, float] = {}
    count_by_dia: Dict[float, int] = {}

    for item in items:
        dia = item.diameter_mm
        length_by_dia[dia] = length_by_dia.get(dia, 0) + item.total_length_mm
        count_by_dia[dia] = count_by_dia.get(dia, 0) + item.no_of_bars

    total_weight_kg = 0.0
    for dia, total_len in length_by_dia.items():
        weight = calculate_bar_weight(dia, total_len, round_weight=False)
        weight_by_dia[dia] = weight
        total_weight_kg += weight

    return BBSummary(
        member_id=member_id,
        total_items=len(items),
        total_bars=total_bars,
        total_length_m=round(total_length_mm / 1000, 2),
        total_weight_kg=round(total_weight_kg, WEIGHT_ROUND_DECIMALS),
        weight_by_diameter={
            k: round(v, WEIGHT_ROUND_DECIMALS) for k, v in sorted(weight_by_dia.items())
        },
        length_by_diameter={
            k: round(v / 1000, 2) for k, v in sorted(length_by_dia.items())
        },
        count_by_diameter=dict(sorted(count_by_dia.items())),
    )


def generate_bbs_document(
    detailing_list: List[BeamDetailingResult],
    project_name: str = "Beam BBS",
) -> BBSDocument:
    """
    Generate a complete BBS document from multiple beams.

    Args:
        detailing_list: List of beam detailing results
        project_name: Project name for the document

    Returns:
        Complete BBS document
    """
    all_items = []
    member_ids = []

    for detailing in detailing_list:
        items = generate_bbs_from_detailing(detailing)
        all_items.extend(items)
        member_ids.append(detailing.beam_id)

    summary = calculate_bbs_summary(all_items, "PROJECT")

    return BBSDocument(
        project_name=project_name,
        member_ids=member_ids,
        items=all_items,
        summary=summary,
    )


# =============================================================================
# Cutting-Stock Optimization
# =============================================================================


def optimize_cutting_stock(
    line_items: List[BBSLineItem],
    stock_lengths: List[float] = None,
    kerf: float = 3.0,
) -> CuttingPlan:
    """
    First-fit-decreasing bin packing for rebar cutting optimization.

    This function minimizes steel waste by optimally assigning bar cuts
    to stock lengths. Uses first-fit-decreasing heuristic which typically
    achieves near-optimal results for 1D bin packing problems.

    Algorithm:
    1. Expand line items: repeat each (mark, cut_length) by quantity
    2. Sort by cut_length descending (first-fit-decreasing)
    3. For each cut, try to fit in existing open stock bar
    4. If no fit, open new stock bar (prefer smallest that fits)
    5. Track assignments and waste

    Args:
        line_items: BBS line items with cut lengths and quantities
        stock_lengths: Available stock bar lengths in mm.
                      Defaults to [6000, 7500, 9000, 12000]
        kerf: Saw cut loss per cut in mm (default: 3.0mm)

    Returns:
        CuttingPlan with assignments and waste statistics

    Raises:
        ValueError: If any cut length exceeds all available stock lengths

    Example:
        >>> items = [
        ...     BBSLineItem(bar_mark="B1", ..., cut_length_mm=2500, no_of_bars=4),
        ...     BBSLineItem(bar_mark="S1", ..., cut_length_mm=1200, no_of_bars=10),
        ... ]
        >>> plan = optimize_cutting_stock(items)
        >>> print(f"Stock bars needed: {plan.total_stock_used}")
        >>> print(f"Waste: {plan.waste_percentage:.1f}%")
    """
    # Default stock lengths per module constant
    if stock_lengths is None:
        stock_lengths = [float(x) for x in STANDARD_STOCK_LENGTHS_MM]

    # Sort stock lengths ascending for efficient selection
    stock_lengths_sorted: List[float] = sorted(stock_lengths)

    # Step 1: Expand line items into individual cuts
    cuts = []  # List of (mark, cut_length) tuples
    for item in line_items:
        for _ in range(item.no_of_bars):
            cuts.append((item.bar_mark, item.cut_length_mm))

    # Early return for empty cuts
    if not cuts:
        return CuttingPlan(
            assignments=[],
            total_stock_used=0,
            total_waste=0.0,
            waste_percentage=0.0,
        )

    # Validate all cuts can fit in available stock
    max_stock = max(stock_lengths_sorted)
    for mark, cut_len in cuts:
        if cut_len > max_stock:
            raise ValueError(
                f"Cut length {cut_len:.0f}mm for bar {mark} exceeds "
                f"maximum stock length {max_stock:.0f}mm"
            )

    # Step 2: Sort cuts by length descending (first-fit-decreasing)
    cuts.sort(key=lambda x: x[1], reverse=True)

    # Step 3-4: Bin packing with first-fit-decreasing heuristic
    assignments: List[CuttingAssignment] = []

    for mark, cut_len in cuts:
        placed = False

        # Try to fit in an existing open stock bar
        for assignment in assignments:
            # Calculate remaining space accounting for kerf
            used_length = sum(c[1] for c in assignment.cuts)
            num_cuts = len(assignment.cuts)
            # Space used = sum of cuts + kerf for each cut
            space_used = used_length + (num_cuts * kerf)
            remaining = assignment.stock_length - space_used

            # Check if cut + kerf fits in remaining space
            # (we need kerf after this cut as well)
            if cut_len + kerf <= remaining:
                assignment.cuts.append((mark, cut_len))
                # Update waste
                new_used = used_length + cut_len
                new_num_cuts = num_cuts + 1
                new_space_used = new_used + (new_num_cuts * kerf)
                assignment.waste = assignment.stock_length - new_space_used
                placed = True
                break

        # If not placed, open new stock bar (smallest that fits)
        if not placed:
            # Find smallest stock that can fit this cut + kerf
            selected_stock = None
            for stock_len in stock_lengths_sorted:
                if cut_len + kerf <= stock_len:
                    selected_stock = stock_len
                    break

            # This should not happen as we validated earlier, but check anyway
            if selected_stock is None:
                raise ValueError(
                    f"Cannot fit cut length {cut_len:.0f}mm in any stock length"
                )

            # Create new assignment
            new_assignment = CuttingAssignment(
                stock_length=selected_stock,
                cuts=[(mark, cut_len)],
                waste=selected_stock - cut_len - kerf,
            )
            assignments.append(new_assignment)

    # Calculate statistics
    total_stock_used = len(assignments)
    total_waste = sum(a.waste for a in assignments)
    total_stock_length = sum(a.stock_length for a in assignments)

    # Waste percentage = (total waste / total stock length) × 100
    waste_percentage = (
        (total_waste / total_stock_length * 100) if total_stock_length > 0 else 0.0
    )

    return CuttingPlan(
        assignments=assignments,
        total_stock_used=total_stock_used,
        total_waste=round(total_waste, 2),
        waste_percentage=round(waste_percentage, 2),
    )


# =============================================================================
# Export Functions
# =============================================================================


def export_bbs_to_csv(
    items: List[BBSLineItem],
    output_path: str,
    include_summary: bool = True,
) -> str:
    """
    Export BBS items to CSV file.

    Args:
        items: List of BBS line items
        output_path: Output file path
        include_summary: Whether to append summary rows

    Returns:
        Path to the created file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "bar_mark",
        "member_id",
        "location",
        "zone",
        "shape_code",
        "diameter_mm",
        "no_of_bars",
        "cut_length_mm",
        "total_length_mm",
        "unit_weight_kg",
        "total_weight_kg",
        "remarks",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            writer.writerow(
                {
                    "bar_mark": item.bar_mark,
                    "member_id": item.member_id,
                    "location": item.location,
                    "zone": item.zone,
                    "shape_code": item.shape_code,
                    "diameter_mm": item.diameter_mm,
                    "no_of_bars": item.no_of_bars,
                    "cut_length_mm": item.cut_length_mm,
                    "total_length_mm": item.total_length_mm,
                    "unit_weight_kg": item.unit_weight_kg,
                    "total_weight_kg": item.total_weight_kg,
                    "remarks": item.remarks,
                }
            )

        if include_summary:
            summary = calculate_bbs_summary(items, "TOTAL")
            # Write blank row
            writer.writerow({fn: "" for fn in fieldnames})
            # Write summary
            writer.writerow(
                {
                    "bar_mark": "TOTAL",
                    "member_id": "",
                    "location": "",
                    "zone": "",
                    "shape_code": "",
                    "diameter_mm": "",
                    "no_of_bars": summary.total_bars,
                    "cut_length_mm": "",
                    "total_length_mm": summary.total_length_m * 1000,
                    "unit_weight_kg": "",
                    "total_weight_kg": summary.total_weight_kg,
                    "remarks": f"{summary.total_items} line items",
                }
            )

    return str(path)


def export_bbs_to_json(
    document: BBSDocument,
    output_path: str,
) -> str:
    """
    Export BBS document to JSON file.

    Args:
        document: BBS document
        output_path: Output file path

    Returns:
        Path to the created file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict
    data = {
        "project_name": document.project_name,
        "created_by": document.created_by,
        "version": document.version,
        "member_ids": document.member_ids,
        "items": [
            {
                "bar_mark": item.bar_mark,
                "member_id": item.member_id,
                "location": item.location,
                "zone": item.zone,
                "shape_code": item.shape_code,
                "diameter_mm": item.diameter_mm,
                "no_of_bars": item.no_of_bars,
                "cut_length_mm": item.cut_length_mm,
                "total_length_mm": item.total_length_mm,
                "unit_weight_kg": item.unit_weight_kg,
                "total_weight_kg": item.total_weight_kg,
                "a_mm": item.a_mm,
                "b_mm": item.b_mm,
                "remarks": item.remarks,
            }
            for item in document.items
        ],
        "summary": {
            "member_id": document.summary.member_id,
            "total_items": document.summary.total_items,
            "total_bars": document.summary.total_bars,
            "total_length_m": document.summary.total_length_m,
            "total_weight_kg": document.summary.total_weight_kg,
            "weight_by_diameter_kg": document.summary.weight_by_diameter,
            "length_by_diameter_m": document.summary.length_by_diameter,
            "count_by_diameter": document.summary.count_by_diameter,
        },
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return str(path)


def export_bom_summary_csv(
    summary: BBSummary,
    output_path: str,
) -> str:
    """
    Export Bill of Materials summary to CSV.

    Args:
        summary: BBS summary
        output_path: Output file path

    Returns:
        Path to the created file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["BILL OF MATERIALS - REINFORCEMENT"])
        writer.writerow(["Member ID:", summary.member_id])
        writer.writerow([])
        writer.writerow(["Diameter (mm)", "Count (nos)", "Length (m)", "Weight (kg)"])

        for dia in sorted(summary.count_by_diameter.keys()):
            writer.writerow(
                [
                    int(dia),
                    summary.count_by_diameter.get(dia, 0),
                    summary.length_by_diameter.get(dia, 0),
                    summary.weight_by_diameter.get(dia, 0),
                ]
            )

        writer.writerow([])
        writer.writerow(
            [
                "TOTAL",
                summary.total_bars,
                summary.total_length_m,
                summary.total_weight_kg,
            ]
        )

    return str(path)
