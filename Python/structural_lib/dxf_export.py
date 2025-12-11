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

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    import ezdxf
    from ezdxf import units
    from ezdxf.enums import TextEntityAlignment
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

from .detailing import BeamDetailingResult, BarArrangement, StirrupArrangement


# =============================================================================
# Constants
# =============================================================================

# Layer definitions (name, color index, linetype)
LAYERS = {
    "BEAM_OUTLINE": (7, "CONTINUOUS"),      # White
    "REBAR_MAIN": (1, "CONTINUOUS"),        # Red
    "REBAR_STIRRUP": (3, "CONTINUOUS"),     # Green
    "DIMENSIONS": (4, "CONTINUOUS"),        # Cyan
    "TEXT": (2, "CONTINUOUS"),              # Yellow
    "CENTERLINE": (6, "CENTER"),            # Magenta
    "HIDDEN": (8, "HIDDEN"),                # Gray
}

# Drawing parameters
TEXT_HEIGHT = 50  # mm (scaled for drawing)
DIM_OFFSET = 100  # Dimension line offset from beam
REBAR_OFFSET = 30  # Offset from beam edge for rebar line


# =============================================================================
# Helper Functions
# =============================================================================

def check_ezdxf():
    """Raise error if ezdxf is not available."""
    if not EZDXF_AVAILABLE:
        raise ImportError(
            "ezdxf library not installed. Install with: pip install ezdxf"
        )


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


def draw_stirrup(msp, x: float, y_bottom: float, width: float, height: float, 
                 cover: float, layer: str):
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
    msp.add_line((x1, y1), (x1 + hook_len * 0.7, y1 - hook_len * 0.7), 
                 dxfattribs={"layer": layer})
    msp.add_line((x2, y1), (x2 - hook_len * 0.7, y1 - hook_len * 0.7), 
                 dxfattribs={"layer": layer})


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
    origin: Tuple[float, float] = (0, 0)
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
        dxfattribs={"layer": "CENTERLINE", "linetype": "CENTER"}
    )
    
    # 3. Draw reinforcement lines (simplified as horizontal lines)
    # Bottom bars (continuous line with circles at ends)
    y_bot = y0 + cover + bottom_bars[1].diameter / 2
    msp.add_line((x0, y_bot), (x0 + span, y_bot), dxfattribs={"layer": "REBAR_MAIN"})
    
    # Top bars
    y_top = y0 + D - cover - top_bars[1].diameter / 2
    msp.add_line((x0, y_top), (x0 + span, y_top), dxfattribs={"layer": "REBAR_MAIN"})
    
    # 4. Draw stirrups at intervals
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
    while x < x0 + span:
        draw_stirrup(msp, x, y0, b, D, cover, "REBAR_STIRRUP")
        x += stirrups[2].spacing


def draw_dimensions(
    msp,
    span: float,
    D: float,
    origin: Tuple[float, float] = (0, 0)
):
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
    msp.add_line((x0 + span, y0), (x0 + span, y_dim - 20), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x0, y_dim), (x0 + span, y_dim), dxfattribs={"layer": "DIMENSIONS"})
    
    # Span text
    msp.add_text(
        f"{int(span)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
        }
    ).set_placement((x0 + span / 2, y_dim - TEXT_HEIGHT), align=TextEntityAlignment.TOP_CENTER)
    
    # Depth dimension (right side)
    x_dim = x0 + span + DIM_OFFSET
    msp.add_line((x0 + span, y0), (x_dim + 20, y0), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x0 + span, y0 + D), (x_dim + 20, y0 + D), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x_dim, y0), (x_dim, y0 + D), dxfattribs={"layer": "DIMENSIONS"})
    
    # Depth text (rotated)
    msp.add_text(
        f"{int(D)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
            "rotation": 90,
        }
    ).set_placement((x_dim + TEXT_HEIGHT, y0 + D / 2), align=TextEntityAlignment.MIDDLE_CENTER)


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
    origin: Tuple[float, float] = (0, 0)
):
    """
    Add text annotations for reinforcement callouts.
    """
    x0, y0 = origin
    
    # Title
    title_y = y0 + D + 150
    msp.add_text(
        f"BEAM {beam_id} (Story: {story}) — {int(b)}x{int(D)}",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT * 1.5,
        }
    ).set_placement((x0, title_y), align=TextEntityAlignment.LEFT)
    
    # Bottom bar callout
    bot_callout = bottom_bars[1].callout()  # Mid span (typically governs)
    msp.add_text(
        f"Bottom: {bot_callout}",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
        }
    ).set_placement((x0 + span / 2, y0 - DIM_OFFSET - 100), align=TextEntityAlignment.TOP_CENTER)
    
    # Top bar callout
    top_callout = top_bars[1].callout()
    msp.add_text(
        f"Top: {top_callout}",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT,
        }
    ).set_placement((x0 + span / 2, y0 + D + 50), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # Stirrup callouts for each zone
    zone_x = [x0 + span * 0.125, x0 + span * 0.5, x0 + span * 0.875]
    zone_labels = ["Start", "Mid", "End"]
    
    for i, (stir, x, label) in enumerate(zip(stirrups, zone_x, zone_labels)):
        msp.add_text(
            stir.callout(),
            dxfattribs={
                "layer": "TEXT",
                "height": TEXT_HEIGHT * 0.8,
            }
        ).set_placement((x, y0 + D / 2), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Development length note
    note_y = y0 - DIM_OFFSET - 200
    msp.add_text(
        f"Ld = {int(ld)} mm, Lap = {int(lap)} mm",
        dxfattribs={
            "layer": "TEXT",
            "height": TEXT_HEIGHT * 0.8,
        }
    ).set_placement((x0, note_y), align=TextEntityAlignment.LEFT)


# =============================================================================
# Main Export Function
# =============================================================================

def generate_beam_dxf(
    detailing: BeamDetailingResult,
    output_path: str,
    include_dimensions: bool = True,
    include_annotations: bool = True
) -> str:
    """
    Generate a DXF file from beam detailing result.
    
    Args:
        detailing: BeamDetailingResult from detailing module
        output_path: Path to save DXF file
        include_dimensions: Add dimension lines
        include_annotations: Add text annotations
    
    Returns:
        Path to generated DXF file
    """
    check_ezdxf()
    
    # Create new DXF document (R2010 for compatibility)
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    
    # Setup layers
    setup_layers(doc)
    
    # Get modelspace
    msp = doc.modelspace()
    
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
        origin=(0, 0)
    )
    
    # Add dimensions
    if include_dimensions:
        draw_dimensions(msp, detailing.span, detailing.D, origin=(0, 0))
    
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
            origin=(0, 0)
        )
    
    # Save file
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
    parser.add_argument("-o", "--output", default="beam_detail.dxf", help="Output DXF path")
    
    args = parser.parse_args()
    
    # Load detailing data from JSON
    with open(args.input, "r") as f:
        data = json.load(f)
    
    # TODO: Convert JSON to BeamDetailingResult
    # For now, create a sample
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
