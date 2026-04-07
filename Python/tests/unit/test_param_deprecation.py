# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for deprecated parameter aliases in service-layer functions.

Verifies four patterns for every function with deprecated params:
1. New param names work without warnings
2. Old param names emit DeprecationWarning
3. Both old and new raises ValueError
4. Neither param raises TypeError

Covers:
- column_api: design_column_axial_is456, design_column_is456,
              check_column_ductility_is13920
- beam_api:   check_beam_ductility (5 deprecated params),
              check_anchorage_at_simple_support (2 deprecated params)

References:
    TASK-743
"""

from __future__ import annotations

import warnings

import pytest

from structural_lib import (
    check_beam_ductility,
    check_column_ductility_is13920,
    design_column_axial_is456,
    design_column_is456,
)
from structural_lib.services.beam_api import check_anchorage_at_simple_support

# ============================================================================
# Helpers — common kwargs for each function (using new param names)
# ============================================================================

_AXIAL_KWARGS = {
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
    "Ag_mm2": 90_000.0,
    "Asc_mm2": 1_800.0,
}

_COLUMN_IS456_KWARGS = {
    "Pu_kN": 800.0,
    "Mux_kNm": 120.0,
    "b_mm": 300.0,
    "D_mm": 450.0,
    "l_mm": 3000.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
    "Asc_mm2": 2400.0,
    "d_prime_mm": 50.0,
}

_DUCTILITY_COL_KWARGS = {
    "b_mm": 400.0,
    "D_mm": 500.0,
    "clear_height_mm": 3000.0,
    "bar_dia_mm": 16.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
}

_BEAM_DUCTILITY_KWARGS = {
    "b_mm": 230.0,
    "D_mm": 450.0,
    "d_mm": 410.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
}

_ANCHORAGE_KWARGS = {
    "bar_dia_mm": 12.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
    "vu_kn": 50.0,
    "support_width_mm": 300.0,
}


# ============================================================================
# 1. design_column_axial_is456
# ============================================================================


class TestDesignColumnAxialDeprecation:
    """Deprecation tests for design_column_axial_is456."""

    def test_new_params_no_warning(self):
        """New param names (fck_nmm2, fy_nmm2) emit no warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = design_column_axial_is456(**_AXIAL_KWARGS)
            assert result is not None

    def test_old_fck_emits_warning(self):
        """Old 'fck' emits DeprecationWarning."""
        with pytest.warns(DeprecationWarning, match="'fck' is deprecated"):
            design_column_axial_is456(fck=25, fy_nmm2=415, Ag_mm2=90_000, Asc_mm2=1_800)

    def test_old_fy_emits_warning(self):
        """Old 'fy' emits DeprecationWarning."""
        with pytest.warns(DeprecationWarning, match="'fy' is deprecated"):
            design_column_axial_is456(fck_nmm2=25, fy=415, Ag_mm2=90_000, Asc_mm2=1_800)

    def test_both_fck_raises(self):
        """Passing both fck_nmm2 and fck raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fck_nmm2' or 'fck', not both"):
            design_column_axial_is456(
                fck_nmm2=25, fck=25, fy_nmm2=415, Ag_mm2=90_000, Asc_mm2=1_800
            )

    def test_both_fy_raises(self):
        """Passing both fy_nmm2 and fy raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fy_nmm2' or 'fy', not both"):
            design_column_axial_is456(
                fck_nmm2=25, fy_nmm2=415, fy=415, Ag_mm2=90_000, Asc_mm2=1_800
            )

    def test_missing_fck_raises(self):
        """Omitting both fck_nmm2 and fck raises TypeError."""
        with pytest.raises(TypeError, match="requires 'fck_nmm2'"):
            design_column_axial_is456(fy_nmm2=415, Ag_mm2=90_000, Asc_mm2=1_800)

    def test_missing_fy_raises(self):
        """Omitting both fy_nmm2 and fy raises TypeError."""
        with pytest.raises(TypeError, match="requires 'fy_nmm2'"):
            design_column_axial_is456(fck_nmm2=25, Ag_mm2=90_000, Asc_mm2=1_800)


# ============================================================================
# 2. design_column_is456 (has defaults: fck=25, fy=415)
# ============================================================================


class TestDesignColumnIs456Deprecation:
    """Deprecation tests for design_column_is456 (unified orchestrator)."""

    def test_new_params_no_warning(self):
        """New param names emit no warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = design_column_is456(**_COLUMN_IS456_KWARGS)
            assert result is not None

    def test_no_fck_fy_uses_defaults(self):
        """Calling without fck_nmm2/fck uses default (25); same for fy (415)."""
        kwargs = {
            k: v
            for k, v in _COLUMN_IS456_KWARGS.items()
            if k not in ("fck_nmm2", "fy_nmm2")
        }
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # No warning expected
            result = design_column_is456(**kwargs)
            assert result is not None

    def test_old_fck_emits_warning(self):
        """Old 'fck' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _COLUMN_IS456_KWARGS.items() if k != "fck_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fck' is deprecated"):
            design_column_is456(**kwargs, fck=25)

    def test_old_fy_emits_warning(self):
        """Old 'fy' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _COLUMN_IS456_KWARGS.items() if k != "fy_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fy' is deprecated"):
            design_column_is456(**kwargs, fy=415)

    def test_both_fck_raises(self):
        """Passing both fck_nmm2 and fck raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fck_nmm2' or 'fck', not both"):
            design_column_is456(**_COLUMN_IS456_KWARGS, fck=25)

    def test_both_fy_raises(self):
        """Passing both fy_nmm2 and fy raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fy_nmm2' or 'fy', not both"):
            design_column_is456(**_COLUMN_IS456_KWARGS, fy=415)


# ============================================================================
# 3. check_column_ductility_is13920
# ============================================================================


class TestCheckColumnDuctilityDeprecation:
    """Deprecation tests for check_column_ductility_is13920."""

    def test_new_params_no_warning(self):
        """New param names emit no warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = check_column_ductility_is13920(**_DUCTILITY_COL_KWARGS)
            assert result is not None

    def test_old_fck_emits_warning(self):
        """Old 'fck' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _DUCTILITY_COL_KWARGS.items() if k != "fck_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fck' is deprecated"):
            check_column_ductility_is13920(**kwargs, fck=25)

    def test_old_fy_emits_warning(self):
        """Old 'fy' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _DUCTILITY_COL_KWARGS.items() if k != "fy_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fy' is deprecated"):
            check_column_ductility_is13920(**kwargs, fy=415)

    def test_both_fck_raises(self):
        """Passing both fck_nmm2 and fck raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fck_nmm2' or 'fck', not both"):
            check_column_ductility_is13920(**_DUCTILITY_COL_KWARGS, fck=25)

    def test_both_fy_raises(self):
        """Passing both fy_nmm2 and fy raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fy_nmm2' or 'fy', not both"):
            check_column_ductility_is13920(**_DUCTILITY_COL_KWARGS, fy=415)

    def test_missing_fck_raises(self):
        """Omitting both fck_nmm2 and fck raises TypeError."""
        kwargs = {k: v for k, v in _DUCTILITY_COL_KWARGS.items() if k != "fck_nmm2"}
        with pytest.raises(TypeError, match="requires 'fck_nmm2'"):
            check_column_ductility_is13920(**kwargs)

    def test_missing_fy_raises(self):
        """Omitting both fy_nmm2 and fy raises TypeError."""
        kwargs = {k: v for k, v in _DUCTILITY_COL_KWARGS.items() if k != "fy_nmm2"}
        with pytest.raises(TypeError, match="requires 'fy_nmm2'"):
            check_column_ductility_is13920(**kwargs)


# ============================================================================
# 4. check_beam_ductility (5 deprecated params: b, D, d, fck, fy)
# ============================================================================


class TestCheckBeamDuctilityDeprecation:
    """Deprecation tests for check_beam_ductility (5 deprecated params)."""

    def test_new_params_no_warning(self):
        """New param names emit no warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = check_beam_ductility(**_BEAM_DUCTILITY_KWARGS)
            assert result is not None

    def test_old_b_emits_warning(self):
        """Old 'b' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "b_mm"}
        with pytest.warns(DeprecationWarning, match="'b' is deprecated"):
            check_beam_ductility(**kwargs, b=230)

    def test_old_depth_d_emits_warning(self):  # noqa: N802
        """Old 'D' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "D_mm"}
        with pytest.warns(DeprecationWarning, match="'D' is deprecated"):
            check_beam_ductility(**kwargs, D=450)

    def test_old_d_emits_warning(self):
        """Old 'd' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "d_mm"}
        with pytest.warns(DeprecationWarning, match="'d' is deprecated"):
            check_beam_ductility(**kwargs, d=410)

    def test_old_fck_emits_warning(self):
        """Old 'fck' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "fck_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fck' is deprecated"):
            check_beam_ductility(**kwargs, fck=25)

    def test_old_fy_emits_warning(self):
        """Old 'fy' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "fy_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fy' is deprecated"):
            check_beam_ductility(**kwargs, fy=415)

    def test_both_b_raises(self):
        """Passing both b_mm and b raises ValueError."""
        with pytest.raises(ValueError, match="specify 'b_mm' or 'b', not both"):
            check_beam_ductility(**_BEAM_DUCTILITY_KWARGS, b=230)

    def test_both_depth_d_raises(self):
        """Passing both D_mm and D raises ValueError."""
        with pytest.raises(ValueError, match="specify 'D_mm' or 'D', not both"):
            check_beam_ductility(**_BEAM_DUCTILITY_KWARGS, D=450)

    def test_both_d_raises(self):
        """Passing both d_mm and d raises ValueError."""
        with pytest.raises(ValueError, match="specify 'd_mm' or 'd', not both"):
            check_beam_ductility(**_BEAM_DUCTILITY_KWARGS, d=410)

    def test_both_fck_raises(self):
        """Passing both fck_nmm2 and fck raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fck_nmm2' or 'fck', not both"):
            check_beam_ductility(**_BEAM_DUCTILITY_KWARGS, fck=25)

    def test_both_fy_raises(self):
        """Passing both fy_nmm2 and fy raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fy_nmm2' or 'fy', not both"):
            check_beam_ductility(**_BEAM_DUCTILITY_KWARGS, fy=415)

    def test_missing_b_raises(self):
        """Omitting both b_mm and b raises TypeError."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "b_mm"}
        with pytest.raises(TypeError, match="requires 'b_mm'"):
            check_beam_ductility(**kwargs)

    def test_missing_fck_raises(self):
        """Omitting both fck_nmm2 and fck raises TypeError."""
        kwargs = {k: v for k, v in _BEAM_DUCTILITY_KWARGS.items() if k != "fck_nmm2"}
        with pytest.raises(TypeError, match="requires 'fck_nmm2'"):
            check_beam_ductility(**kwargs)


# ============================================================================
# 5. check_anchorage_at_simple_support (2 deprecated params: fck, fy)
# ============================================================================


class TestCheckAnchorageDeprecation:
    """Deprecation tests for check_anchorage_at_simple_support."""

    def test_new_params_no_warning(self):
        """New param names emit no warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = check_anchorage_at_simple_support(**_ANCHORAGE_KWARGS)
            assert result is not None

    def test_old_fck_emits_warning(self):
        """Old 'fck' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _ANCHORAGE_KWARGS.items() if k != "fck_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fck' is deprecated"):
            check_anchorage_at_simple_support(**kwargs, fck=25)

    def test_old_fy_emits_warning(self):
        """Old 'fy' emits DeprecationWarning."""
        kwargs = {k: v for k, v in _ANCHORAGE_KWARGS.items() if k != "fy_nmm2"}
        with pytest.warns(DeprecationWarning, match="'fy' is deprecated"):
            check_anchorage_at_simple_support(**kwargs, fy=415)

    def test_both_fck_raises(self):
        """Passing both fck_nmm2 and fck raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fck_nmm2' or 'fck', not both"):
            check_anchorage_at_simple_support(**_ANCHORAGE_KWARGS, fck=25)

    def test_both_fy_raises(self):
        """Passing both fy_nmm2 and fy raises ValueError."""
        with pytest.raises(ValueError, match="specify 'fy_nmm2' or 'fy', not both"):
            check_anchorage_at_simple_support(**_ANCHORAGE_KWARGS, fy=415)

    def test_missing_fck_raises(self):
        """Omitting both fck_nmm2 and fck raises TypeError."""
        kwargs = {k: v for k, v in _ANCHORAGE_KWARGS.items() if k != "fck_nmm2"}
        with pytest.raises(TypeError, match="requires 'fck_nmm2'"):
            check_anchorage_at_simple_support(**kwargs)

    def test_missing_fy_raises(self):
        """Omitting both fy_nmm2 and fy raises TypeError."""
        kwargs = {k: v for k, v in _ANCHORAGE_KWARGS.items() if k != "fy_nmm2"}
        with pytest.raises(TypeError, match="requires 'fy_nmm2'"):
            check_anchorage_at_simple_support(**kwargs)
