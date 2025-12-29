"""
DXF Export Module — Beam Detail Drawing Generation

This module generates DXF drawings from beam detailing data using the ezdxf library.

Output Format:
- DXF R2010 (AC1024) for wide compatibility
- Layers: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP, DIMENSIONS, TEXT
- Scale: 1:1 (mm units)
- Origin: Bottom-left of beam at first support

Dependencies:
- ezdxf (pip install ezdxf)

Usage:
    from structural_lib.dxf_export import generate_beam_dxf
    generate_beam_dxf(detailing_result, "output.dxf")
"""

from typing import Any, List, Optional, Tuple, Dict, Union, Set
from pathlib import Path

ezdxf: Any = None
_units: Any = None
_TextEntityAlignment: Any = None
EZDXF_AVAILABLE = False

try:
    import ezdxf as _ezdxf

    ezdxf = _ezdxf

    try:
        from ezdxf import units as _ezdxf_units

        _units = _ezdxf_units
    except Exception:
        _units = None

    try:
        from ezdxf.enums import TextEntityAlignment as _ezdxf_TextEntityAlignment

        _TextEntityAlignment = _ezdxf_TextEntityAlignment
    except Exception:
        _TextEntityAlignment = None

    EZDXF_AVAILABLE = True
except Exception:
    EZDXF_AVAILABLE = False

# Public aliases so tests/users can monkeypatch or introspect the optional ezdxf
# surface in a stable way.
units = _units
TextEntityAlignment = _TextEntityAlignment

from .api import get_library_version
from .detailing import BeamDetailingResult, BarArrangement, StirrupArrangement
from . import bbs


# =============================================================================
# Constants
# =============================================================================

# Layer definitions (name, color index, linetype)
LAYERS = {
    "BEAM_OUTLINE": (7, "CONTINUOUS"),  # White
    "REBAR_MAIN": (1, "CONTINUOUS"),  # Red
    "REBAR_STIRRUP": (3, "CONTINUOUS"),  # Green
    "DIMENSIONS": (4, "CONTINUOUS"),  # Cyan
    "TEXT": (2, "CONTINUOUS"),  # Yellow
    "CENTERLINE": (6, "CENTER"),  # Magenta
    "HIDDEN": (8, "HIDDEN"),  # Gray
    "BORDER": (7, "CONTINUOUS"),  # White
}

# Drawing parameters
TEXT_HEIGHT = 50  # mm (scaled for drawing)
DIM_OFFSET = 100  # Dimension line offset from beam
REBAR_OFFSET = 30  # Offset from beam edge for rebar line
DEFAULT_SHEET_MARGIN = 200.0  # mm
DEFAULT_TITLE_BLOCK_WIDTH = 900.0  # mm
DEFAULT_TITLE_BLOCK_HEIGHT = 250.0  # mm


# =============================================================================
# Helper Functions
# =============================================================================


def check_ezdxf():
    """Raise error if ezdxf is not available."""
    if not EZDXF_AVAILABLE:
        raise ImportError(
            "ezdxf library not installed. Install with: pip install ezdxf"
        )


def _text_align(name: str) -> Any:
    """Return a text alignment compatible with the installed ezdxf.

    ezdxf's Text.set_placement() accepts either a TextEntityAlignment enum member
    or a string (varies by ezdxf version).
    """
    if TextEntityAlignment is None:
        return name
    return getattr(TextEntityAlignment, name)


def setup_layers(doc):
    """Create standard layers in the DXF document."""
    for layer_name, (color, linetype) in LAYERS.items():
        try:
            doc.layers.add(layer_name, color=color)
        except ezdxf.DXFTableEntryError:
            pass  # Layer already exists


def draw_rectangle(msp, x1: float, y1: float, x2: float, y2: float, layer: str):
    """Draw a rectangle using 4 lines."""
    msp.add_line((x1, y1), (x2, y1), dxfattribs={"layer": layer})
    msp.add_line((x2, y1), (x2, y2), dxfattribs={"layer": layer})
    msp.add_line((x2, y2), (x1, y2), dxfattribs={"layer": layer})
    msp.add_line((x1, y2), (x1, y1), dxfattribs={"layer": layer})


def _annotation_scale(span: float, depth: float) -> float:
    """Scale text and offsets for readability across beam sizes."""
    if span <= 0 or depth <= 0:
        return 1.0
    base = (span / 4000.0 + depth / 500.0) / 2.0
    return max(0.75, min(1.4, base))


def _zone_label(zone: str) -> str:
    return {
        "start": "Start",
        "mid": "Mid",
        "end": "End",
        "full": "Full",
    }.get(zone, zone.capitalize())


def _bar_mark_map(detailing: BeamDetailingResult) -> dict:
    """Map (location, zone) -> bar_mark using BBS generation."""
    marks: dict = {}
    for item in bbs.generate_bbs_from_detailing(detailing):
        key = (item.location, item.zone)
        if key not in marks:
            marks[key] = item.bar_mark
    return marks


def extract_bar_marks_from_dxf(path: Union[str, Path]) -> Dict[str, Set[str]]:
    """Extract bar marks from a DXF file, grouped by beam."""
    check_ezdxf()
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"DXF file not found: {p}")

    doc = ezdxf.readfile(str(p))
    msp = doc.modelspace()

    marks_by_beam: Dict[str, Set[str]] = {}
    for entity in msp.query("TEXT MTEXT"):
        if entity.dxftype() == "TEXT":
            text = entity.dxf.text
        else:
            if hasattr(entity, "plain_text"):
                text = entity.plain_text()
            else:
                text = entity.text

        for mark in bbs.extract_bar_marks_from_text(text):
            parsed = bbs.parse_bar_mark(mark)
            if not parsed:
                continue
            beam_id = parsed["beam_id"]
            marks_by_beam.setdefault(beam_id, set()).add(parsed["mark"])

    return marks_by_beam


def compare_bbs_dxf_marks(
    bbs_csv_path: Union[str, Path],
    dxf_path: Union[str, Path],
) -> Dict[str, object]:
    """Compare bar marks in a BBS CSV against a DXF file."""
    bbs_marks = bbs.extract_bar_marks_from_bbs_csv(bbs_csv_path)
    dxf_marks = extract_bar_marks_from_dxf(dxf_path)

    missing_in_dxf: Dict[str, List[str]] = {}
    extra_in_dxf: Dict[str, List[str]] = {}

    all_beams = sorted(set(bbs_marks) | set(dxf_marks))
    for beam_id in all_beams:
        bbs_set = bbs_marks.get(beam_id, set())
        dxf_set = dxf_marks.get(beam_id, set())

        missing = sorted(bbs_set - dxf_set)
        extra = sorted(dxf_set - bbs_set)

        if missing:
            missing_in_dxf[beam_id] = missing
        if extra:
            extra_in_dxf[beam_id] = extra

    summary = {
        "beams_checked": len(all_beams),
        "bbs_marks": sum(len(marks) for marks in bbs_marks.values()),
        "dxf_marks": sum(len(marks) for marks in dxf_marks.values()),
        "missing_in_dxf": sum(len(marks) for marks in missing_in_dxf.values()),
        "extra_in_dxf": sum(len(marks) for marks in extra_in_dxf.values()),
    }

    return {
        "ok": not missing_in_dxf and not extra_in_dxf,
        "missing_in_dxf": missing_in_dxf,
        "extra_in_dxf": extra_in_dxf,
        "summary": summary,
    }


def _annotation_extents(include_annotations: bool) -> Tuple[float, float]:
    """Return (above_extent, below_extent) for annotations."""
    if include_annotations:
        above_extent = 150 + TEXT_HEIGHT * 1.5
        below_extent = DIM_OFFSET + 200 + TEXT_HEIGHT
    else:
        above_extent = 100
        below_extent = DIM_OFFSET + 50
    return above_extent, below_extent


def _estimate_cell_width(
    span_mm: float, b_mm: float, include_section_cuts: bool
) -> float:
    """Estimate cell width for a single beam (mm)."""
    width = span_mm
    if include_section_cuts:
        width += 500 + b_mm + 200 + b_mm
    # Space for right-side dimension + text
    width += DIM_OFFSET + TEXT_HEIGHT + 20
    return width


def _draw_title_block(
    msp,
    origin: Tuple[float, float],
    width: float,
    height: float,
    fields: List[str],
) -> None:
    """Draw a simple title block with a list of text lines."""
    x1, y1 = origin
    x2 = x1 + width
    y2 = y1 + height

    draw_rectangle(msp, x1, y1, x2, y2, "BORDER")

    lines = [line for line in fields if line]
    padding = 15
    if lines:
        max_line_height = (height - 2 * padding) / len(lines)
        line_height = min(TEXT_HEIGHT * 0.6, max_line_height)
    else:
        line_height = TEXT_HEIGHT * 0.6
    spacing = max(2.0, line_height * 0.2)

    x_text = x1 + 20
    y_text = y2 - line_height - padding
    for line in lines:
        msp.add_text(
            line,
            dxfattribs={"layer": "TEXT", "height": line_height},
        ).set_placement((x_text, y_text), align=_text_align("LEFT"))
        y_text -= line_height + spacing


def _format_size_line(b: float, D: float) -> str:
    return f"Size: {int(round(b))}x{int(round(D))} mm"


def _format_cover_line(cover: float) -> str:
    return f"Cover: {int(round(cover))} mm"


def _format_range_line(label: str, values: List[float]) -> str:
    if not values:
        return ""
    v_min = int(round(min(values)))
    v_max = int(round(max(values)))
    if v_min == v_max:
        return f"{label}: {v_min} mm"
    return f"{label}: {v_min}-{v_max} mm"


def _format_size_range_line(b_values: List[float], d_values: List[float]) -> str:
    if not b_values or not d_values:
        return ""
    b_min = int(round(min(b_values)))
    b_max = int(round(max(b_values)))
    d_min = int(round(min(d_values)))
    d_max = int(round(max(d_values)))
    b_part = f"{b_min}" if b_min == b_max else f"{b_min}-{b_max}"
    d_part = f"{d_min}" if d_min == d_max else f"{d_min}-{d_max}"
    return f"Sizes: {b_part} x {d_part} mm"


def draw_stirrup(
    msp,
    x: float,
    y_bottom: float,
    width: float,
    height: float,
    cover: float,
    layer: str,
):
    """Draw a single stirrup (U-shape with hooks)."""
    # Outer points
    x1 = x - width / 2 + cover
    x2 = x + width / 2 - cover
    y1 = y_bottom + cover
    y2 = y_bottom + height - cover

    # Draw U-shape
    msp.add_line((x1, y1), (x1, y2), dxfattribs={"layer": layer})
    msp.add_line((x1, y2), (x2, y2), dxfattribs={"layer": layer})
    msp.add_line((x2, y2), (x2, y1), dxfattribs={"layer": layer})

    # 135° hooks (simplified as small lines)
    hook_len = 30
    msp.add_line(
        (x1, y1),
        (x1 + hook_len * 0.7, y1 - hook_len * 0.7),
        dxfattribs={"layer": layer},
    )
    msp.add_line(
        (x2, y1),
        (x2 - hook_len * 0.7, y1 - hook_len * 0.7),
        dxfattribs={"layer": layer},
    )


# =============================================================================
# Main Drawing Functions
# =============================================================================


def draw_beam_elevation(
    msp,
    span: float,
    D: float,
    b: float,
    cover: float,
    top_bars: List[BarArrangement],
    bottom_bars: List[BarArrangement],
    stirrups: List[StirrupArrangement],
    origin: Tuple[float, float] = (0, 0),
):
    """
    Draw beam elevation view (longitudinal section).

    Args:
        msp: Modelspace
        span: Beam span length (mm)
        D: Beam depth (mm)
        b: Beam width (mm)
        cover: Clear cover (mm)
        top_bars: Bar arrangements [start, mid, end]
        bottom_bars: Bar arrangements [start, mid, end]
        stirrups: Stirrup arrangements [start, mid, end]
        origin: Drawing origin (x, y)
    """
    x0, y0 = origin

    # 1. Draw beam outline
    draw_rectangle(msp, x0, y0, x0 + span, y0 + D, "BEAM_OUTLINE")

    # 2. Draw centerline
    msp.add_line(
        (x0 - 200, y0 + D / 2),
        (x0 + span + 200, y0 + D / 2),
        dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"},
    )

    # 3. Draw reinforcement lines (simplified as horizontal lines)
    # Bottom bars (continuous line with circles at ends)
    mid_idx = len(bottom_bars) // 2 if bottom_bars else 0
    bot_bar = (
        bottom_bars[mid_idx]
        if bottom_bars
        else BarArrangement(
            count=2, diameter=16, area_provided=402, spacing=100, layers=1
        )
    )
    y_bot = y0 + cover + bot_bar.diameter / 2
    msp.add_line((x0, y_bot), (x0 + span, y_bot), dxfattribs={"layer": "REBAR_MAIN"})

    # Top bars
    top_mid_idx = len(top_bars) // 2 if top_bars else 0
    top_bar = (
        top_bars[top_mid_idx]
        if top_bars
        else BarArrangement(
            count=2, diameter=12, area_provided=226, spacing=100, layers=1
        )
    )
    y_top = y0 + D - cover - top_bar.diameter / 2
    msp.add_line((x0, y_top), (x0 + span, y_top), dxfattribs={"layer": "REBAR_MAIN"})

    # 4. Draw stirrups at intervals
    # Handle varying number of stirrup zones
    if not stirrups:
        return

    n_zones = len(stirrups)
    if n_zones == 1:
        # Single zone - uniform spacing
        x = x0 + stirrups[0].spacing / 2
        while x < x0 + span:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += stirrups[0].spacing
    elif n_zones == 2:
        # Two zones - split at midspan
        zone_1_end = span * 0.5

        x = x0 + stirrups[0].spacing / 2
        while x < x0 + zone_1_end:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += stirrups[0].spacing

        while x < x0 + span:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += stirrups[1].spacing
    else:
        # Three or more zones - standard start/mid/end
        zone_1_end = span * 0.25  # First zone
        zone_2_end = span * 0.75  # Second zone ends

        # Start zone stirrups
        x = x0 + stirrups[0].spacing / 2
        while x < x0 + zone_1_end:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += stirrups[0].spacing

        # Mid zone stirrups
        while x < x0 + zone_2_end:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += stirrups[1].spacing

        # End zone stirrups
        end_spacing = stirrups[2].spacing if n_zones > 2 else stirrups[0].spacing
        while x < x0 + span:
            draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
            x += end_spacing


def draw_dimensions(msp, span: float, D: float, origin: Tuple[float, float] = (0, 0)):
    """
    Add dimension annotations.

    Args:
        msp: Modelspace
        span: Beam span (mm)
        D: Beam depth (mm)
        origin: Drawing origin
    """
    x0, y0 = origin

    # Span dimension (below beam)
    y_dim = y0 - DIM_OFFSET
    msp.add_line((x0, y0), (x0, y_dim - 20), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line(
        (x0 + span, y0), (x0 + span, y_dim - 20), dxfattribs={"layer": "DIMENSIONS"}
    )
    msp.add_line((x0, y_dim), (x0 + span, y_dim), dxfattribs={"layer": "DIMENSIONS"})

    # Span text
    msp.add_text(
        f"{int(span)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
        },
    ).set_placement(
        (x0 + span / 2, y_dim - TEXT_HEIGHT), align=_text_align("TOP_CENTER")
    )

    # Depth dimension (right side)
    x_dim = x0 + span + DIM_OFFSET
    msp.add_line((x0 + span, y0), (x_dim + 20, y0), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line(
        (x0 + span, y0 + D), (x_dim + 20, y0 + D), dxfattribs={"layer": "DIMENSIONS"}
    )
    msp.add_line((x_dim, y0), (x_dim, y0 + D), dxfattribs={"layer": "DIMENSIONS"})

    # Depth text (rotated)
    msp.add_text(
        f"{int(D)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
            "rotation": 90,
        },
    ).set_placement(
        (x_dim + TEXT_HEIGHT, y0 + D / 2), align=_text_align("MIDDLE_CENTER")
    )


def draw_annotations(
    msp,
    span: float,
    D: float,
    beam_id: str,
    story: str,
    b: float,
    top_bars: List[BarArrangement],
    bottom_bars: List[BarArrangement],
    stirrups: List[StirrupArrangement],
    ld: float,
    lap: float,
    detailing: Optional[BeamDetailingResult] = None,
    origin: Tuple[float, float] = (0, 0),
):
    """
    Add text annotations for reinforcement callouts.
    """
    x0, y0 = origin

    scale = _annotation_scale(span, D)
    text_height = TEXT_HEIGHT * scale
    dim_offset = DIM_OFFSET * scale

    mark_map = _bar_mark_map(detailing) if detailing else {}

    # Title
    title_y = y0 + D + 150 * scale
    msp.add_text(
        f"BEAM {beam_id} (Story: {story}) — {int(b)}x{int(D)}",
        dxfattribs={
            "layer": "TEXT",
            "height": text_height * 1.5,
        },
    ).set_placement((x0, title_y), align=_text_align("LEFT"))

    # Bottom bar callouts (zone-specific)
    if bottom_bars:
        zone_x = [x0 + span * 0.125, x0 + span * 0.5, x0 + span * 0.875]
        for bar_arr, zone, x in zip(bottom_bars, ["start", "mid", "end"], zone_x):
            if bar_arr.count <= 0:
                continue
            mark = mark_map.get(("bottom", zone), "")
            mark_text = f"{mark} " if mark else ""
            bot_callout = f"Bottom {_zone_label(zone)}: {mark_text}{bar_arr.callout()}"
            msp.add_text(
                bot_callout,
                dxfattribs={
                    "layer": "TEXT",
                    "height": text_height,
                },
            ).set_placement(
                (x, y0 - dim_offset - 100 * scale),
                align=_text_align("TOP_CENTER"),
            )

    # Top bar callouts (zone-specific)
    if top_bars:
        zone_x = [x0 + span * 0.125, x0 + span * 0.5, x0 + span * 0.875]
        for bar_arr, zone, x in zip(top_bars, ["start", "mid", "end"], zone_x):
            if bar_arr.count <= 0:
                continue
            mark = mark_map.get(("top", zone), "")
            mark_text = f"{mark} " if mark else ""
            top_callout = f"Top {_zone_label(zone)}: {mark_text}{bar_arr.callout()}"
            msp.add_text(
                top_callout,
                dxfattribs={
                    "layer": "TEXT",
                    "height": text_height,
                },
            ).set_placement(
                (x, y0 + D + 50 * scale),
                align=_text_align("BOTTOM_CENTER"),
            )

    # Stirrup callouts for each zone (handle varying zone counts)
    if stirrups:
        n_stir = len(stirrups)
        if n_stir == 1:
            zone_names = ["start"]
            zone_x = [x0 + span * 0.5]
        elif n_stir == 2:
            zone_names = ["start", "mid"]
            zone_x = [x0 + span * 0.25, x0 + span * 0.75]
        else:
            zone_names = ["start", "mid", "end"]
            zone_x = [x0 + span * 0.125, x0 + span * 0.5, x0 + span * 0.875]

        for stir, zone, x in zip(stirrups, zone_names, zone_x):
            mark = mark_map.get(("stirrup", zone), "")
            mark_text = f"{mark} " if mark else ""
            msp.add_text(
                f"Stirrup {_zone_label(zone)}: {mark_text}{stir.callout()}",
                dxfattribs={
                    "layer": "TEXT",
                    "height": text_height * 0.8,
                },
            ).set_placement((x, y0 + D / 2), align=_text_align("MIDDLE_CENTER"))

    # Development length note
    note_y = y0 - dim_offset - 200 * scale
    msp.add_text(
        f"Ld = {int(ld)} mm, Lap = {int(lap)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": text_height * 0.8,
        },
    ).set_placement((x0, note_y), align=_text_align("LEFT"))


# =============================================================================
# Section Cut Drawing
# =============================================================================


def draw_section_cut(
    msp,
    b: float,
    D: float,
    cover: float,
    top_bars: BarArrangement,
    bottom_bars: BarArrangement,
    stirrup: StirrupArrangement,
    origin: Tuple[float, float] = (0, 0),
    scale: float = 1.0,
    title: str = "SECTION A-A",
):
    """
    Draw a cross-section view of the beam.

    Args:
        msp: Modelspace to draw on
        b: Beam width (mm)
        D: Beam total depth (mm)
        cover: Clear cover (mm)
        top_bars: Top bar arrangement at this section
        bottom_bars: Bottom bar arrangement at this section
        stirrup: Stirrup arrangement at this section
        origin: Bottom-left corner of section
        scale: Drawing scale (1.0 = 1:1)
        title: Section title text
    """
    x0, y0 = origin
    b_scaled = b * scale
    D_scaled = D * scale
    cover_scaled = cover * scale

    # Beam outline
    draw_rectangle(msp, x0, y0, x0 + b_scaled, y0 + D_scaled, "BEAM_OUTLINE")

    # Stirrup (inner rectangle with rounded corners represented as rectangle)
    stirrup_dia = stirrup.diameter * scale
    inner_x1 = x0 + cover_scaled
    inner_y1 = y0 + cover_scaled
    inner_x2 = x0 + b_scaled - cover_scaled
    inner_y2 = y0 + D_scaled - cover_scaled

    msp.add_lwpolyline(
        [
            (inner_x1, inner_y1),
            (inner_x2, inner_y1),
            (inner_x2, inner_y2),
            (inner_x1, inner_y2),
            (inner_x1, inner_y1),
        ],
        dxfattribs={"layer": "REBAR_STIRRUP"},
    )

    # Bottom bars (circles)
    n_bottom = bottom_bars.count
    dia_bottom = bottom_bars.diameter * scale
    if n_bottom > 0:
        # Calculate spacing (clamp to avoid negative values for tight sections)
        available_width = b_scaled - 2 * cover_scaled - 2 * stirrup_dia - dia_bottom
        available_width = max(available_width, 0)  # Clamp to prevent negative
        if n_bottom > 1 and available_width > 0:
            spacing = available_width / (n_bottom - 1)
        else:
            spacing = 0  # Stack bars at center if no room

        bar_y = y0 + cover_scaled + stirrup_dia + dia_bottom / 2
        # Center the bar group if spacing is zero
        if spacing == 0 and n_bottom > 1:
            start_x = x0 + b_scaled / 2  # Center single stack
        else:
            start_x = x0 + cover_scaled + stirrup_dia + dia_bottom / 2

        for i in range(n_bottom):
            cx = start_x + i * spacing
            msp.add_circle(
                (cx, bar_y),
                dia_bottom / 2,
                dxfattribs={"layer": "REBAR_MAIN"},
            )

    # Top bars (circles)
    n_top = top_bars.count
    dia_top = top_bars.diameter * scale
    if n_top > 0:
        available_width = b_scaled - 2 * cover_scaled - 2 * stirrup_dia - dia_top
        available_width = max(available_width, 0)  # Clamp to prevent negative
        if n_top > 1 and available_width > 0:
            spacing = available_width / (n_top - 1)
        else:
            spacing = 0  # Stack bars at center if no room

        bar_y = y0 + D_scaled - cover_scaled - stirrup_dia - dia_top / 2
        # Center the bar group if spacing is zero
        if spacing == 0 and n_top > 1:
            start_x = x0 + b_scaled / 2  # Center single stack
        else:
            start_x = x0 + cover_scaled + stirrup_dia + dia_top / 2

        for i in range(n_top):
            cx = start_x + i * spacing
            msp.add_circle(
                (cx, bar_y),
                dia_top / 2,
                dxfattribs={"layer": "REBAR_MAIN"},
            )

    # Section title
    msp.add_text(
        title,
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT * 0.8 * scale,
        },
    ).set_placement(
        (x0 + b_scaled / 2, y0 - 50 * scale), align=_text_align("TOP_CENTER")
    )

    # Dimension: width
    msp.add_text(
        f"{int(b)}",
        dxfattribs={
            "layer": "DIMENSIONS",
            "height": TEXT_HEIGHT * 0.6 * scale,
        },
    ).set_placement(
        (x0 + b_scaled / 2, y0 - 20 * scale), align=_text_align("TOP_CENTER")
    )

    # Dimension: depth
    msp.add_text(
        f"{int(D)}",
        dxfattribs={
            "layer": "DIMENSIONS",
            "height": TEXT_HEIGHT * 0.6 * scale,
            "rotation": 90,
        },
    ).set_placement(
        (x0 + b_scaled + 20 * scale, y0 + D_scaled / 2),
        align=_text_align("MIDDLE_CENTER"),
    )

    # Bar callouts
    bot_text = f"{n_bottom}-T{int(bottom_bars.diameter)}"
    top_text = f"{n_top}-T{int(top_bars.diameter)}"

    msp.add_text(
        bot_text,
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT * 0.5 * scale,
        },
    ).set_placement(
        (x0 + b_scaled / 2, y0 + cover_scaled + stirrup_dia + dia_bottom + 10 * scale),
        align=_text_align("BOTTOM_CENTER"),
    )

    msp.add_text(
        top_text,
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT * 0.5 * scale,
        },
    ).set_placement(
        (
            x0 + b_scaled / 2,
            y0 + D_scaled - cover_scaled - stirrup_dia - dia_top - 10 * scale,
        ),
        align=_text_align("TOP_CENTER"),
    )


# =============================================================================
# Main Export Function
# =============================================================================


def generate_beam_dxf(
    detailing: BeamDetailingResult,
    output_path: str,
    include_dimensions: bool = True,
    include_annotations: bool = True,
    include_section_cuts: bool = True,
    include_title_block: bool = False,
    title_block: Optional[dict] = None,
    sheet_margin_mm: float = DEFAULT_SHEET_MARGIN,
    title_block_width_mm: float = DEFAULT_TITLE_BLOCK_WIDTH,
    title_block_height_mm: float = DEFAULT_TITLE_BLOCK_HEIGHT,
) -> str:
    """
    Generate a DXF file from beam detailing result.

    Args:
        detailing: BeamDetailingResult from detailing module
        output_path: Path to save DXF file
        include_dimensions: Add dimension lines
        include_annotations: Add text annotations
        include_section_cuts: Add cross-section views (A-A at support, B-B at midspan)
        include_title_block: Draw a deliverable border + title block
        title_block: Optional dict to override title block fields (title, beam_id,
            story, span_line, units, scale, project, date, drawn_by, version)
        sheet_margin_mm: Sheet margin for deliverable layout (mm)
        title_block_width_mm: Title block width (mm)
        title_block_height_mm: Title block height (mm)

    Returns:
        Path to generated DXF file
    """
    check_ezdxf()

    # Create new DXF document (R2010 for compatibility)
    doc = ezdxf.new("R2010")
    if units is not None:
        doc.units = units.MM

    # Setup layers
    setup_layers(doc)

    # Get modelspace
    msp = doc.modelspace()

    origin_x = 0.0
    origin_y = 0.0
    if include_title_block:
        _, below_extent = _annotation_extents(include_annotations)
        origin_x = sheet_margin_mm
        origin_y = sheet_margin_mm + title_block_height_mm + below_extent

    # Draw beam elevation
    draw_beam_elevation(
        msp,
        span=detailing.span,
        D=detailing.D,
        b=detailing.b,
        cover=detailing.cover,
        top_bars=detailing.top_bars,
        bottom_bars=detailing.bottom_bars,
        stirrups=detailing.stirrups,
        origin=(origin_x, origin_y),
    )

    # Add dimensions
    if include_dimensions:
        draw_dimensions(msp, detailing.span, detailing.D, origin=(origin_x, origin_y))

    # Add annotations
    if include_annotations:
        draw_annotations(
            msp,
            span=detailing.span,
            D=detailing.D,
            beam_id=detailing.beam_id,
            story=detailing.story,
            b=detailing.b,
            top_bars=detailing.top_bars,
            bottom_bars=detailing.bottom_bars,
            stirrups=detailing.stirrups,
            ld=detailing.ld_tension,
            lap=detailing.lap_length,
            detailing=detailing,
            origin=(origin_x, origin_y),
        )

    # Add section cuts (positioned to the right of elevation)
    if include_section_cuts:
        # Section A-A at support (uses first zone bars)
        section_x_offset = origin_x + detailing.span + 500  # 500mm gap from elevation

        # Get bar arrangements for support (first zone)
        top_bar_support = (
            detailing.top_bars[0]
            if detailing.top_bars
            else BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        )
        bottom_bar_support = (
            detailing.bottom_bars[0]
            if detailing.bottom_bars
            else BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        )

        draw_section_cut(
            msp,
            b=detailing.b,
            D=detailing.D,
            cover=detailing.cover,
            top_bars=top_bar_support,
            bottom_bars=bottom_bar_support,
            stirrup=(
                detailing.stirrups[0]
                if detailing.stirrups
                else StirrupArrangement(
                    diameter=8, legs=2, spacing=150, zone_length=1000
                )
            ),
            origin=(section_x_offset, origin_y),
            scale=1.0,
            title="SECTION A-A (SUPPORT)",
        )

        # Section B-B at midspan (uses middle zone bars)
        section_b_offset = section_x_offset + detailing.b + 200

        # Get bar arrangements for midspan (middle zone)
        mid_idx = len(detailing.top_bars) // 2 if detailing.top_bars else 0
        top_bar_mid = (
            detailing.top_bars[mid_idx]
            if detailing.top_bars
            else BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        )
        bottom_bar_mid = (
            detailing.bottom_bars[mid_idx]
            if detailing.bottom_bars
            else BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        )
        stirrup_mid_idx = len(detailing.stirrups) // 2 if detailing.stirrups else 0

        draw_section_cut(
            msp,
            b=detailing.b,
            D=detailing.D,
            cover=detailing.cover,
            top_bars=top_bar_mid,
            bottom_bars=bottom_bar_mid,
            stirrup=(
                detailing.stirrups[stirrup_mid_idx]
                if detailing.stirrups
                else StirrupArrangement(
                    diameter=8, legs=2, spacing=200, zone_length=2000
                )
            ),
            origin=(section_b_offset, origin_y),
            scale=1.0,
            title="SECTION B-B (MIDSPAN)",
        )

    if include_title_block:
        above_extent, below_extent = _annotation_extents(include_annotations)
        content_width = _estimate_cell_width(
            detailing.span, detailing.b, include_section_cuts
        )
        content_height = detailing.D + above_extent + below_extent
        sheet_width = content_width + sheet_margin_mm * 2
        sheet_height = content_height + sheet_margin_mm * 2 + title_block_height_mm

        draw_rectangle(msp, 0, 0, sheet_width, sheet_height, "BORDER")

        block_width = min(
            title_block_width_mm, max(100.0, sheet_width - 2 * sheet_margin_mm)
        )
        block_height = min(
            title_block_height_mm, max(80.0, sheet_height - 2 * sheet_margin_mm)
        )
        block_x = sheet_width - sheet_margin_mm - block_width
        block_y = sheet_margin_mm

        title = "RC BEAM DETAIL"
        beam_id = detailing.beam_id
        story = detailing.story
        size_line = _format_size_line(detailing.b, detailing.D)
        cover_line = _format_cover_line(detailing.cover)
        span_line = f"Span: {detailing.span:.0f} mm"
        units_note = "Units: mm, N/mm2, kN, kN-m"
        scale_note = "Scale: 1:1"
        project = ""
        date_line = ""
        drawn_by = ""
        version_line = f"Version: {get_library_version()}"
        if title_block:
            title = title_block.get("title", title)
            beam_id = title_block.get("beam_id", beam_id)
            story = title_block.get("story", story)
            size_line = title_block.get("size_line", size_line)
            cover_line = title_block.get("cover_line", cover_line)
            span_line = title_block.get("span_line", span_line)
            units_note = title_block.get("units", units_note)
            scale_note = title_block.get("scale", scale_note)
            project = title_block.get("project", project)
            date_line = title_block.get("date", date_line)
            drawn_by = title_block.get("drawn_by", drawn_by)
            version_line = title_block.get("version", version_line)

        fields = [
            title,
            project,
            f"Beam: {beam_id}",
            f"Story: {story}",
            size_line,
            cover_line,
            span_line,
            date_line,
            drawn_by,
            version_line,
            scale_note,
            units_note,
        ]
        _draw_title_block(msp, (block_x, block_y), block_width, block_height, fields)

    # Save file
    doc.saveas(output_path)

    return output_path


# =============================================================================
# Multi-Beam Layout Function
# =============================================================================


def generate_multi_beam_dxf(
    detailings: List[BeamDetailingResult],
    output_path: str,
    columns: int = 2,
    row_spacing: float = 200.0,
    col_spacing: float = 500.0,
    include_dimensions: bool = True,
    include_annotations: bool = True,
    include_section_cuts: bool = True,
    include_title_block: bool = False,
    title_block: Optional[dict] = None,
    sheet_margin_mm: float = DEFAULT_SHEET_MARGIN,
    title_block_width_mm: float = DEFAULT_TITLE_BLOCK_WIDTH,
    title_block_height_mm: float = DEFAULT_TITLE_BLOCK_HEIGHT,
) -> str:
    """
    Generate a single DXF file containing multiple beam details in a grid layout.

    Args:
        detailings: List of BeamDetailingResult objects to draw
        output_path: Path to save DXF file
        columns: Number of columns in the grid layout (must be >= 1)
        row_spacing: Vertical spacing between beam rows (mm)
        col_spacing: Horizontal spacing between beam columns (mm)
        include_dimensions: Add dimension lines
        include_annotations: Add text annotations
        include_section_cuts: Add cross-section views
        include_title_block: Draw a deliverable border + title block
        title_block: Optional dict to override title block fields (title, count_line,
            units, scale, project, date, drawn_by, version)
        sheet_margin_mm: Sheet margin for deliverable layout (mm)
        title_block_width_mm: Title block width (mm)
        title_block_height_mm: Title block height (mm)

    Returns:
        Path to generated DXF file

    Raises:
        ValueError: If detailings is empty or columns < 1
    """
    check_ezdxf()

    if not detailings:
        raise ValueError("At least one beam detailing result is required")

    if columns < 1:
        raise ValueError("columns must be >= 1")

    # Create new DXF document (R2010 for compatibility)
    doc = ezdxf.new("R2010")
    if units is not None:
        doc.units = units.MM

    # Setup layers
    setup_layers(doc)

    # Get modelspace
    msp = doc.modelspace()

    # --- Pre-compute per-column widths and per-row heights ---
    # This ensures beams in the same column/row don't overlap
    n_beams = len(detailings)
    n_rows = (n_beams + columns - 1) // columns  # Ceiling division

    # Calculate cell width for each column (max of all beams in that column)
    col_widths = [0.0] * columns
    row_heights = [0.0] * n_rows

    for idx, detailing in enumerate(detailings):
        col = idx % columns
        row = idx // columns

        # Calculate beam cell width (including section cuts if enabled)
        cell_width = _estimate_cell_width(
            detailing.span, detailing.b, include_section_cuts
        )

        # Update column max width
        col_widths[col] = max(col_widths[col], cell_width)

        # Calculate row height based on annotation extents
        above_extent, below_extent = _annotation_extents(include_annotations)
        cell_height = detailing.D + above_extent + below_extent
        row_heights[row] = max(row_heights[row], cell_height)

    # Compute cumulative X offsets for each column
    col_x_offsets = [0.0] * columns
    for c in range(1, columns):
        col_x_offsets[c] = col_x_offsets[c - 1] + col_widths[c - 1] + col_spacing

    # Compute cumulative Y offsets for each row
    # Account for below_extent so annotations don't overlap
    # (reuse same calculation from loop above)
    _, base_below_extent = _annotation_extents(include_annotations)
    row_y_offsets: List[float] = [
        base_below_extent
    ] * n_rows  # Start with offset for first row's bottom annotations
    for r in range(1, n_rows):
        row_y_offsets[r] = row_y_offsets[r - 1] + row_heights[r - 1] + row_spacing

    # --- Draw each beam at its computed position ---
    for idx, detailing in enumerate(detailings):
        # Calculate row and column
        row = idx // columns
        col = idx % columns

        # Use precomputed cell positions (guarantees no overlap)
        base_x = sheet_margin_mm if include_title_block else 0.0
        base_y = sheet_margin_mm + title_block_height_mm if include_title_block else 0.0
        x_origin = base_x + col_x_offsets[col]
        y_origin = base_y + row_y_offsets[row]

        # Draw beam elevation
        draw_beam_elevation(
            msp,
            span=detailing.span,
            D=detailing.D,
            b=detailing.b,
            cover=detailing.cover,
            top_bars=detailing.top_bars,
            bottom_bars=detailing.bottom_bars,
            stirrups=detailing.stirrups,
            origin=(x_origin, y_origin),
        )

        # Add dimensions
        if include_dimensions:
            draw_dimensions(
                msp, detailing.span, detailing.D, origin=(x_origin, y_origin)
            )

        # Add annotations
        if include_annotations:
            draw_annotations(
                msp,
                span=detailing.span,
                D=detailing.D,
                beam_id=detailing.beam_id,
                story=detailing.story,
                b=detailing.b,
                top_bars=detailing.top_bars,
                bottom_bars=detailing.bottom_bars,
                stirrups=detailing.stirrups,
                ld=detailing.ld_tension,
                lap=detailing.lap_length,
                detailing=detailing,
                origin=(x_origin, y_origin),
            )

        # Add section cuts
        if include_section_cuts:
            section_x_offset = x_origin + detailing.span + 500

            # Get bar arrangements for support (first zone)
            top_bar_support = (
                detailing.top_bars[0]
                if detailing.top_bars
                else BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=100, layers=1
                )
            )
            bottom_bar_support = (
                detailing.bottom_bars[0]
                if detailing.bottom_bars
                else BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=100, layers=1
                )
            )

            draw_section_cut(
                msp,
                b=detailing.b,
                D=detailing.D,
                cover=detailing.cover,
                top_bars=top_bar_support,
                bottom_bars=bottom_bar_support,
                stirrup=(
                    detailing.stirrups[0]
                    if detailing.stirrups
                    else StirrupArrangement(
                        diameter=8, legs=2, spacing=150, zone_length=1000
                    )
                ),
                origin=(section_x_offset, y_origin),
                scale=1.0,
                title="SECTION A-A",
            )

            # Section B-B at midspan
            section_b_offset = section_x_offset + detailing.b + 200
            mid_idx = len(detailing.top_bars) // 2 if detailing.top_bars else 0
            top_bar_mid = (
                detailing.top_bars[mid_idx]
                if detailing.top_bars
                else BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=100, layers=1
                )
            )
            bottom_bar_mid = (
                detailing.bottom_bars[mid_idx]
                if detailing.bottom_bars
                else BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=100, layers=1
                )
            )
            stirrup_mid_idx = len(detailing.stirrups) // 2 if detailing.stirrups else 0

            draw_section_cut(
                msp,
                b=detailing.b,
                D=detailing.D,
                cover=detailing.cover,
                top_bars=top_bar_mid,
                bottom_bars=bottom_bar_mid,
                stirrup=(
                    detailing.stirrups[stirrup_mid_idx]
                    if detailing.stirrups
                    else StirrupArrangement(
                        diameter=8, legs=2, spacing=200, zone_length=2000
                    )
                ),
                origin=(section_b_offset, y_origin),
                scale=1.0,
                title="SECTION B-B",
            )

    # Save file
    if include_title_block:
        total_width = col_x_offsets[-1] + col_widths[-1]
        total_height = row_y_offsets[-1] + row_heights[-1]
        sheet_width = total_width + sheet_margin_mm * 2
        sheet_height = total_height + sheet_margin_mm * 2 + title_block_height_mm

        draw_rectangle(msp, 0, 0, sheet_width, sheet_height, "BORDER")

        block_width = min(
            title_block_width_mm, max(100.0, sheet_width - 2 * sheet_margin_mm)
        )
        block_height = min(
            title_block_height_mm, max(80.0, sheet_height - 2 * sheet_margin_mm)
        )
        block_x = sheet_width - sheet_margin_mm - block_width
        block_y = sheet_margin_mm

        title = "RC BEAM DETAIL SHEET"
        count_line = f"Beams: {len(detailings)}"
        size_range_line = _format_size_range_line(
            [d.b for d in detailings],
            [d.D for d in detailings],
        )
        span_line = _format_range_line("Span", [d.span for d in detailings])
        cover_line = _format_range_line("Cover", [d.cover for d in detailings])
        units_note = "Units: mm, N/mm2, kN, kN-m"
        scale_note = "Scale: 1:1"
        project = ""
        date_line = ""
        drawn_by = ""
        version_line = f"Version: {get_library_version()}"
        if title_block:
            title = title_block.get("title", title)
            count_line = title_block.get("count_line", count_line)
            size_range_line = title_block.get("size_range_line", size_range_line)
            span_line = title_block.get("span_line", span_line)
            cover_line = title_block.get("cover_line", cover_line)
            units_note = title_block.get("units", units_note)
            scale_note = title_block.get("scale", scale_note)
            project = title_block.get("project", project)
            date_line = title_block.get("date", date_line)
            drawn_by = title_block.get("drawn_by", drawn_by)
            version_line = title_block.get("version", version_line)

        fields = [
            title,
            project,
            count_line,
            size_range_line,
            span_line,
            cover_line,
            date_line,
            drawn_by,
            version_line,
            scale_note,
            units_note,
        ]
        _draw_title_block(msp, (block_x, block_y), block_width, block_height, fields)

    doc.saveas(output_path)

    return output_path


# =============================================================================
# CLI Interface
# =============================================================================


def main():
    """Command-line interface for DXF generation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate beam detail DXF")
    parser.add_argument("input", help="JSON file with beam detailing data")
    parser.add_argument(
        "-o", "--output", default="beam_detail.dxf", help="Output DXF path"
    )

    args = parser.parse_args()

    # Load detailing data from JSON
    with open(args.input, "r") as f:
        data = json.load(f)

    # Convert JSON to BeamDetailingResult via create_beam_detailing
    from .detailing import create_beam_detailing

    detailing = create_beam_detailing(
        beam_id=data.get("beam_id", "B1"),
        story=data.get("story", "S1"),
        b=data.get("b", 230),
        D=data.get("D", 450),
        span=data.get("span", 4000),
        cover=data.get("cover", 25),
        fck=data.get("fck", 25),
        fy=data.get("fy", 500),
        ast_start=data.get("ast_start", 800),
        ast_mid=data.get("ast_mid", 1200),
        ast_end=data.get("ast_end", 800),
    )

    output_path = generate_beam_dxf(detailing, args.output)
    print(f"DXF generated: {output_path}")


if __name__ == "__main__":
    main()
