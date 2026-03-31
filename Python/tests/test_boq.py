# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the BOQ (Bill of Quantities) aggregation module."""

import pytest

from structural_lib.services.bbs import BBSDocument, BBSummary
from structural_lib.services.boq import (
    DEFAULT_CONCRETE_COSTS,
    ProjectBOQ,
    aggregate_project_boq,
)

# ---------------------------------------------------------------------------
# Helpers: minimal BBS stubs
# ---------------------------------------------------------------------------


def _make_bbs_summary(
    member_id="B1",
    total_weight_kg=25.0,
    weight_by_diameter=None,
    count_by_diameter=None,
):
    return BBSummary(
        member_id=member_id,
        total_items=3,
        total_bars=10,
        total_length_m=50.0,
        total_weight_kg=total_weight_kg,
        weight_by_diameter=weight_by_diameter or {16.0: 15.0, 12.0: 10.0},
        count_by_diameter=count_by_diameter or {16.0: 6, 12.0: 4},
    )


def _make_bbs_doc(
    member_id="B1",
    total_weight_kg=25.0,
    weight_by_diameter=None,
    count_by_diameter=None,
):
    return BBSDocument(
        project_name="Test",
        member_ids=[member_id],
        items=[],
        summary=_make_bbs_summary(
            member_id=member_id,
            total_weight_kg=total_weight_kg,
            weight_by_diameter=weight_by_diameter,
            count_by_diameter=count_by_diameter,
        ),
    )


def _make_meta(
    story="GF",
    b_mm=300.0,
    D_mm=500.0,
    span_mm=5000.0,
    fck=25,
    steel_grade="Fe500",
):
    return {
        "story": story,
        "b_mm": b_mm,
        "D_mm": D_mm,
        "span_mm": span_mm,
        "fck": fck,
        "steel_grade": steel_grade,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAggregateProjectBOQ:
    """Tests for aggregate_project_boq function."""

    def test_single_beam_basic(self):
        """Single beam produces correct totals."""
        bbs_docs = [_make_bbs_doc()]
        metas = [_make_meta()]
        boq = aggregate_project_boq(bbs_docs, metas, project_name="P1")

        assert isinstance(boq, ProjectBOQ)
        assert boq.project_name == "P1"
        assert boq.total_beams == 1
        assert boq.grand_total_steel_kg == 25.0

    def test_concrete_volume_calculation(self):
        """Concrete volume = b * D * span in m3."""
        bbs_docs = [_make_bbs_doc()]
        metas = [_make_meta(b_mm=300.0, D_mm=500.0, span_mm=5000.0)]
        boq = aggregate_project_boq(bbs_docs, metas)

        expected_m3 = 300.0 * 500.0 * 5000.0 / 1e9  # 0.75
        assert boq.grand_total_concrete_m3 == pytest.approx(expected_m3, abs=0.001)

    def test_steel_cost_calculation(self):
        """Steel cost = weight * rate."""
        bbs_docs = [_make_bbs_doc(total_weight_kg=100.0)]
        metas = [_make_meta()]
        boq = aggregate_project_boq(bbs_docs, metas, steel_cost_per_kg=60.0)

        steel_cost = sum(s.cost_inr for s in boq.steel)
        assert steel_cost == pytest.approx(6000.0, abs=0.01)

    def test_multiple_beams_aggregation(self):
        """Multiple beams aggregate steel and concrete correctly."""
        bbs_docs = [
            _make_bbs_doc(member_id="B1", total_weight_kg=20.0),
            _make_bbs_doc(member_id="B2", total_weight_kg=30.0),
        ]
        metas = [_make_meta(story="GF"), _make_meta(story="1F")]
        boq = aggregate_project_boq(bbs_docs, metas)

        assert boq.total_beams == 2
        assert boq.grand_total_steel_kg == pytest.approx(50.0, abs=0.01)

    def test_story_grouping(self):
        """Beams are grouped by story."""
        bbs_docs = [
            _make_bbs_doc(member_id="B1", total_weight_kg=10.0),
            _make_bbs_doc(member_id="B2", total_weight_kg=20.0),
            _make_bbs_doc(member_id="B3", total_weight_kg=15.0),
        ]
        metas = [
            _make_meta(story="GF"),
            _make_meta(story="GF"),
            _make_meta(story="1F"),
        ]
        boq = aggregate_project_boq(bbs_docs, metas)

        assert len(boq.by_story) == 2
        gf = next(s for s in boq.by_story if s.story == "GF")
        assert gf.beam_count == 2
        assert gf.steel_kg == pytest.approx(30.0, abs=0.01)

    def test_empty_input_returns_empty_schedule(self):
        """Empty input produces zeroed BOQ."""
        boq = aggregate_project_boq([], [])

        assert boq.total_beams == 0
        assert boq.grand_total_steel_kg == 0.0
        assert boq.grand_total_concrete_m3 == 0.0
        assert boq.grand_total_cost_inr == 0.0
        assert boq.steel == []
        assert boq.concrete == []
        assert boq.by_story == []

    def test_custom_concrete_costs(self):
        """Custom concrete cost rates are applied."""
        bbs_docs = [_make_bbs_doc()]
        metas = [_make_meta(fck=30)]
        custom_costs = {30: 10000.0}
        boq = aggregate_project_boq(bbs_docs, metas, concrete_costs=custom_costs)

        concrete_m30 = next((c for c in boq.concrete if c.grade == "M30"), None)
        assert concrete_m30 is not None
        expected_vol = 300.0 * 500.0 * 5000.0 / 1e9
        assert concrete_m30.cost_inr == pytest.approx(expected_vol * 10000.0, abs=0.01)

    def test_multiple_steel_grades(self):
        """Beams with different steel grades produce separate SteelSummary entries."""
        bbs_docs = [
            _make_bbs_doc(member_id="B1", total_weight_kg=20.0),
            _make_bbs_doc(member_id="B2", total_weight_kg=15.0),
        ]
        metas = [
            _make_meta(steel_grade="Fe500"),
            _make_meta(steel_grade="Fe415"),
        ]
        boq = aggregate_project_boq(bbs_docs, metas)

        assert len(boq.steel) == 2
        grades = {s.grade for s in boq.steel}
        assert grades == {"Fe500", "Fe415"}

    def test_default_concrete_costs_used(self):
        """DEFAULT_CONCRETE_COSTS has expected grades."""
        assert 25 in DEFAULT_CONCRETE_COSTS
        assert 30 in DEFAULT_CONCRETE_COSTS

    def test_project_name_default(self):
        """Default project name is 'Project'."""
        boq = aggregate_project_boq([], [])
        assert boq.project_name == "Project"
