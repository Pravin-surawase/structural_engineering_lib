"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.dxf_export

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.dxf_export is deprecated. "
    "Use structural_lib.services.dxf_export instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.dxf_export import (  # noqa: F401, E402
    DEFAULT_SHEET_MARGIN,
    DEFAULT_TITLE_BLOCK_HEIGHT,
    DEFAULT_TITLE_BLOCK_WIDTH,
    DIM_OFFSET,
    EZDXF_AVAILABLE,
    LAYERS,
    REBAR_OFFSET,
    REBAR_UNIT_WEIGHT,
    TEXT_HEIGHT,
    TextEntityAlignment,
    check_ezdxf,
    compare_bbs_dxf_marks,
    draw_annotations,
    draw_beam_elevation,
    draw_beam_schedule_table,
    draw_dimensions,
    draw_rectangle,
    draw_section_cut,
    draw_stirrup,
    extract_bar_marks_from_dxf,
    ezdxf,
    generate_beam_dxf,
    generate_beam_schedule_table,
    generate_multi_beam_dxf,
    group_similar_beams,
    main,
    quick_dxf,
    quick_dxf_bytes,
    setup_layers,
    units,
)

if __name__ == "__main__":
    main()
