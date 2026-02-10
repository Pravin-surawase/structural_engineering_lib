"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.bbs

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.bbs is deprecated. "
    "Use structural_lib.services.bbs instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.bbs import (  # noqa: F401, E402
    BAR_MARK_PATTERN,
    BAR_SHAPES,
    LENGTH_ROUND_MM,
    STANDARD_STOCK_LENGTHS_MM,
    STEEL_DENSITY_KG_M3,
    UNIT_WEIGHTS_KG_M,
    WEIGHT_ROUND_DECIMALS,
    WEIGHT_ROUND_KG,
    BBSDocument,
    BBSLineItem,
    BBSummary,
    assign_bar_marks,
    calculate_bar_weight,
    calculate_bbs_summary,
    calculate_bend_deduction,
    calculate_hook_length,
    calculate_stirrup_cut_length,
    calculate_straight_bar_length,
    calculate_unit_weight_per_meter,
    export_bbs_to_csv,
    export_bbs_to_json,
    export_bom_summary_csv,
    extract_bar_marks_from_bbs_csv,
    extract_bar_marks_from_items,
    extract_bar_marks_from_text,
    generate_bbs_document,
    generate_bbs_from_detailing,
    generate_summary_table,
    optimize_cutting_stock,
    parse_bar_mark,
)
