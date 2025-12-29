"""
Tests for Bar Bending Schedule (BBS) module.

Tests cover:
- Weight calculations
- Cut length calculations
- BBS generation from detailing
- CSV/JSON export
- Summary aggregation
"""

import pytest
import tempfile
import csv
import json
from dataclasses import replace
from pathlib import Path

from structural_lib.bbs import (
    # Constants
    UNIT_WEIGHTS_KG_M,
    STANDARD_STOCK_LENGTHS_MM,
    # Weight calculations
    calculate_bar_weight,
    calculate_unit_weight_per_meter,
    # Cut length calculations
    calculate_hook_length,
    calculate_bend_deduction,
    calculate_straight_bar_length,
    calculate_stirrup_cut_length,
    # BBS generation
    generate_bbs_from_detailing,
    calculate_bbs_summary,
    export_bbs_to_csv,
    export_bbs_to_json,
    export_bom_summary_csv,
    # Cutting-stock optimization
    optimize_cutting_stock,
    # Data classes
    BBSLineItem,
    BBSDocument,
)
from structural_lib.detailing import (
    BeamDetailingResult,
    BarArrangement,
    StirrupArrangement,
)


# =============================================================================
# Weight Calculation Tests
# =============================================================================


class TestWeightCalculations:
    """Tests for bar weight calculations."""

    def test_bar_weight_16mm_1m(self):
        """16mm bar, 1m length should be approximately 1.58 kg."""
        weight = calculate_bar_weight(16, 1000)
        # π × (8/1000)² × 1 × 7850 ≈ 1.579 kg
        assert 1.57 <= weight <= 1.59

    def test_bar_weight_matches_unit_weight(self):
        """Weight calculation should match tabulated unit weights."""
        for dia, expected_unit_wt in UNIT_WEIGHTS_KG_M.items():
            calculated = calculate_bar_weight(dia, 1000)
            assert abs(calculated - expected_unit_wt) < 0.01, f"Mismatch for {dia}mm"

    def test_unit_weight_per_meter(self):
        """Unit weight function should match calculate_bar_weight."""
        for dia in [8, 12, 16, 20, 25]:
            unit_wt = calculate_unit_weight_per_meter(dia)
            from_calc = calculate_bar_weight(dia, 1000)
            assert abs(unit_wt - from_calc) < 0.01

    def test_weight_scales_linearly(self):
        """Weight should scale linearly with length."""
        w1 = calculate_bar_weight(16, 1000)
        w2 = calculate_bar_weight(16, 2000)
        assert abs(w2 - 2 * w1) < 0.01

    def test_weight_scales_with_area(self):
        """Weight should scale with diameter squared."""
        w16 = calculate_bar_weight(16, 1000)
        w8 = calculate_bar_weight(8, 1000)
        # Area ratio = (16/8)² = 4
        assert abs(w16 / w8 - 4) < 0.1


# =============================================================================
# Hook and Bend Length Tests
# =============================================================================


class TestHookAndBendLengths:
    """Tests for hook and bend calculations."""

    def test_hook_length_90_degree(self):
        """90° hook should be 8d."""
        hl = calculate_hook_length(16, 90)
        assert hl == 128  # 8 × 16

    def test_hook_length_180_degree(self):
        """180° hook should be 8d."""
        hl = calculate_hook_length(16, 180)
        assert hl == 128

    def test_hook_length_135_degree(self):
        """135° hook (stirrup) should be 10d (min 75mm)."""
        hl = calculate_hook_length(8, 135)
        assert hl == 80  # max(10 × 8, 75)

    def test_bend_deduction_90(self):
        """90° bend deduction should be 0.5d."""
        bd = calculate_bend_deduction(16, 90)
        assert bd == 8  # 0.5 × 16


# =============================================================================
# Cut Length Tests
# =============================================================================


class TestCutLengths:
    """Tests for cut length calculations."""

    def test_straight_bar_full_span(self):
        """Full span bar should include 2×Ld."""
        cut = calculate_straight_bar_length(
            span_mm=4000,
            cover_mm=40,
            ld_mm=500,
            location="bottom",
            zone="full",
        )
        # 4000 + 2×500 = 5000, rounded to nearest 10
        assert cut == 5000

    def test_straight_bar_start_zone(self):
        """Start zone bar should be curtailed."""
        cut = calculate_straight_bar_length(
            span_mm=4000,
            cover_mm=40,
            ld_mm=500,
            location="bottom",
            zone="start",
        )
        # 4000/2 + 500 + 100 = 2600
        assert cut == 2600

    def test_straight_bar_mid_zone(self):
        """Mid zone bar should be 60% of span + 2×Ld."""
        cut = calculate_straight_bar_length(
            span_mm=4000,
            cover_mm=40,
            ld_mm=500,
            location="bottom",
            zone="mid",
        )
        # 0.6×4000 + 2×500 = 2400 + 1000 = 3400
        assert cut == 3400

    def test_stirrup_cut_length(self):
        """Stirrup cut length should include perimeter + hooks."""
        cut = calculate_stirrup_cut_length(
            b_mm=300,
            D_mm=500,
            cover_mm=40,
            stirrup_dia_mm=8,
            hook_length_mm=0,  # Will use default 10d = 80mm
        )
        # Inner width = 300 - 2×(40 + 4) = 212
        # Inner height = 500 - 2×(40 + 4) = 412
        # Perimeter = 2×(212 + 412) = 1248
        # Hooks = 2 × 80 = 160
        # Total = 1248 + 160 = 1408 -> rounded to 1410
        assert cut == 1410

    def test_cut_length_rounded(self):
        """Cut lengths should be rounded to nearest 10mm."""
        cut = calculate_straight_bar_length(
            span_mm=4005,
            cover_mm=40,
            ld_mm=502,
            location="bottom",
            zone="full",
        )
        # 4005 + 1004 = 5009, rounds to 5010
        assert cut % 10 == 0


# =============================================================================
# BBS Generation Tests
# =============================================================================


class TestBBSGeneration:
    """Tests for BBS generation from detailing results."""

    @pytest.fixture
    def sample_detailing(self) -> BeamDetailingResult:
        """Create a sample beam detailing result for testing."""
        return BeamDetailingResult(
            beam_id="B1",
            story="Story1",
            b=300,
            D=500,
            span=4000,
            cover=40,
            top_bars=[
                BarArrangement(
                    count=2, diameter=16, area_provided=402, spacing=180, layers=1
                ),
                BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=180, layers=1
                ),
                BarArrangement(
                    count=2, diameter=16, area_provided=402, spacing=180, layers=1
                ),
            ],
            bottom_bars=[
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=90, layers=1
                ),
                BarArrangement(
                    count=4, diameter=16, area_provided=804, spacing=60, layers=1
                ),
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=90, layers=1
                ),
            ],
            stirrups=[
                StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
                StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
                StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            ],
            ld_tension=600,
            ld_compression=450,
            lap_length=750,
            is_valid=True,
            remarks="",
        )

    def test_bbs_generates_items(self, sample_detailing):
        """BBS should generate line items from detailing."""
        items = generate_bbs_from_detailing(sample_detailing)
        assert len(items) > 0

    def test_bbs_includes_all_zones(self, sample_detailing):
        """BBS should include items for all zones."""
        items = generate_bbs_from_detailing(sample_detailing)
        zones = {item.zone for item in items}
        assert "start" in zones
        assert "mid" in zones
        assert "end" in zones

    def test_bbs_includes_all_locations(self, sample_detailing):
        """BBS should include bottom, top, and stirrups."""
        items = generate_bbs_from_detailing(sample_detailing)
        locations = {item.location for item in items}
        assert "bottom" in locations
        assert "top" in locations
        assert "stirrup" in locations

    def test_bbs_weights_positive(self, sample_detailing):
        """All weights should be positive."""
        items = generate_bbs_from_detailing(sample_detailing)
        for item in items:
            assert item.unit_weight_kg > 0
            assert item.total_weight_kg > 0

    def test_bbs_total_weight_consistent(self, sample_detailing):
        """Total weight should equal sum of individual weights."""
        items = generate_bbs_from_detailing(sample_detailing)
        for item in items:
            expected = round(
                calculate_bar_weight(
                    item.diameter_mm,
                    item.total_length_mm,
                    round_weight=False,
                ),
                2,
            )
            assert abs(item.total_weight_kg - expected) < 0.1

    def test_bbs_unique_marks(self, sample_detailing):
        """All bar marks should be unique."""
        items = generate_bbs_from_detailing(sample_detailing)
        marks = [item.bar_mark for item in items]
        assert len(marks) == len(set(marks))

    def test_bbs_unique_marks_across_beams(self, sample_detailing):
        """Marks should be unique across multiple beams."""
        detailing_b2 = replace(sample_detailing, beam_id="B2", story="Story2")
        items = generate_bbs_from_detailing(sample_detailing)
        items += generate_bbs_from_detailing(detailing_b2)
        marks = [item.bar_mark for item in items]
        assert len(marks) == len(set(marks))
        assert all(mark.startswith(("B1-", "B2-")) for mark in marks)


# =============================================================================
# Summary Tests
# =============================================================================


class TestBBSSummary:
    """Tests for BBS summary calculations."""

    def test_summary_totals(self):
        """Summary should correctly total bars and weights."""
        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=4,
                cut_length_mm=5000,
                total_length_mm=20000,
                unit_weight_kg=7.9,
                total_weight_kg=31.6,
            ),
            BBSLineItem(
                bar_mark="S1",
                member_id="B1",
                location="stirrup",
                zone="full",
                shape_code="E",
                diameter_mm=8,
                no_of_bars=20,
                cut_length_mm=1440,
                total_length_mm=28800,
                unit_weight_kg=0.57,
                total_weight_kg=11.4,
            ),
        ]
        summary = calculate_bbs_summary(items, "B1")

        assert summary.total_bars == 24
        assert summary.total_items == 2
        assert abs(summary.total_weight_kg - 43.0) < 0.1

    def test_summary_by_diameter(self):
        """Summary should break down by diameter."""
        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=4,
                cut_length_mm=5000,
                total_length_mm=20000,
                unit_weight_kg=7.9,
                total_weight_kg=31.6,
            ),
            BBSLineItem(
                bar_mark="B2",
                member_id="B1",
                location="top",
                zone="full",
                shape_code="A",
                diameter_mm=12,
                no_of_bars=2,
                cut_length_mm=4000,
                total_length_mm=8000,
                unit_weight_kg=3.55,
                total_weight_kg=7.1,
            ),
        ]
        summary = calculate_bbs_summary(items, "B1")

        assert 16 in summary.weight_by_diameter
        assert 12 in summary.weight_by_diameter
        assert summary.count_by_diameter[16] == 4
        assert summary.count_by_diameter[12] == 2


# =============================================================================
# Export Tests
# =============================================================================


class TestBBSExport:
    """Tests for BBS export functions."""

    @pytest.fixture
    def sample_items(self) -> list:
        """Sample BBS items for export testing."""
        return [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=4,
                cut_length_mm=5000,
                total_length_mm=20000,
                unit_weight_kg=7.9,
                total_weight_kg=31.6,
                remarks="Bottom main bars",
            ),
            BBSLineItem(
                bar_mark="S1",
                member_id="B1",
                location="stirrup",
                zone="start",
                shape_code="E",
                diameter_mm=8,
                no_of_bars=10,
                cut_length_mm=1440,
                total_length_mm=14400,
                unit_weight_kg=0.57,
                total_weight_kg=5.7,
                a_mm=220,
                b_mm=420,
                remarks="Start zone stirrups",
            ),
        ]

    def test_csv_export_creates_file(self, sample_items):
        """CSV export should create a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bbs.csv"
            result = export_bbs_to_csv(sample_items, str(path))

            assert Path(result).exists()

    def test_csv_export_content(self, sample_items):
        """CSV export should contain all items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bbs.csv"
            export_bbs_to_csv(sample_items, str(path))

            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            # Should have 2 items + blank + TOTAL row
            data_rows = [r for r in rows if r["bar_mark"] and r["bar_mark"] != "TOTAL"]
            assert len(data_rows) == 2

    def test_csv_export_with_summary(self, sample_items):
        """CSV export with summary should include TOTAL row."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bbs.csv"
            export_bbs_to_csv(sample_items, str(path), include_summary=True)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "TOTAL" in content

    def test_json_export_creates_file(self, sample_items):
        """JSON export should create a valid file."""
        doc = BBSDocument(
            project_name="Test Project",
            member_ids=["B1"],
            items=sample_items,
            summary=calculate_bbs_summary(sample_items, "B1"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bbs.json"
            result = export_bbs_to_json(doc, str(path))

            assert Path(result).exists()

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["project_name"] == "Test Project"
            assert len(data["items"]) == 2

    def test_bom_summary_export(self, sample_items):
        """BOM summary should export correctly."""
        summary = calculate_bbs_summary(sample_items, "B1")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bom.csv"
            result = export_bom_summary_csv(summary, str(path))

            assert Path(result).exists()

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "BILL OF MATERIALS" in content
            assert "TOTAL" in content


# =============================================================================
# Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests to ensure deterministic outputs."""

    def test_same_input_same_output(self):
        """Same detailing input should produce identical BBS."""
        detailing = BeamDetailingResult(
            beam_id="B1",
            story="Story1",
            b=300,
            D=500,
            span=4000,
            cover=40,
            top_bars=[
                BarArrangement(
                    count=2, diameter=16, area_provided=402, spacing=180, layers=1
                ),
                BarArrangement(
                    count=2, diameter=16, area_provided=402, spacing=180, layers=1
                ),
                BarArrangement(
                    count=2, diameter=16, area_provided=402, spacing=180, layers=1
                ),
            ],
            bottom_bars=[
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=90, layers=1
                ),
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=90, layers=1
                ),
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=90, layers=1
                ),
            ],
            stirrups=[
                StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
                StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
                StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            ],
            ld_tension=600,
            ld_compression=450,
            lap_length=750,
            is_valid=True,
            remarks="",
        )

        items1 = generate_bbs_from_detailing(detailing)
        items2 = generate_bbs_from_detailing(detailing)

        assert len(items1) == len(items2)
        for i1, i2 in zip(items1, items2):
            assert i1.bar_mark == i2.bar_mark
            assert i1.cut_length_mm == i2.cut_length_mm
            assert i1.total_weight_kg == i2.total_weight_kg

    def test_weight_calculation_deterministic(self):
        """Weight calculations should be deterministic."""
        results = [calculate_bar_weight(16, 5000) for _ in range(10)]
        assert len(set(results)) == 1  # All results identical


# =============================================================================
# Cutting-Stock Optimization Tests
# =============================================================================


class TestCuttingStockOptimization:
    """Tests for cutting-stock optimization function."""

    def test_simple_case_all_bars_fit_one_stock(self):
        """Simple case: all bars fit in one stock length."""

        # Create line items that should fit in a single 6000mm stock
        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=2,
                cut_length_mm=2000,
                total_length_mm=4000,
                unit_weight_kg=3.16,
                total_weight_kg=6.32,
            ),
            BBSLineItem(
                bar_mark="B2",
                member_id="B1",
                location="bottom",
                zone="mid",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=1,
                cut_length_mm=1500,
                total_length_mm=1500,
                unit_weight_kg=2.37,
                total_weight_kg=2.37,
            ),
        ]

        plan = optimize_cutting_stock(items, stock_lengths=[6000], kerf=3.0)

        # Should use only 1 stock bar
        assert plan.total_stock_used == 1
        assert len(plan.assignments) == 1

        # Check assignment details
        assignment = plan.assignments[0]
        assert assignment.stock_length == 6000
        assert len(assignment.cuts) == 3  # 2 × 2000mm + 1 × 1500mm

        # Verify cuts are present
        cut_lengths = [c[1] for c in assignment.cuts]
        assert cut_lengths.count(2000) == 2
        assert cut_lengths.count(1500) == 1

        # Calculate expected waste
        # Total cut length = 2×2000 + 1×1500 = 5500
        # Kerf loss = 3 cuts × 3mm = 9mm
        # Waste = 6000 - 5500 - 9 = 491mm
        expected_waste = 6000 - 5500 - 9
        assert abs(assignment.waste - expected_waste) < 1

    def test_multiple_stock_lengths_needed(self):
        """Multiple stock lengths needed when bars don't fit in one."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=20,
                no_of_bars=5,
                cut_length_mm=5000,
                total_length_mm=25000,
                unit_weight_kg=12.33,
                total_weight_kg=61.65,
            ),
        ]

        plan = optimize_cutting_stock(items, stock_lengths=[6000], kerf=3.0)

        # Each 5000mm bar needs its own 6000mm stock (5000 + 3 kerf = 5003)
        assert plan.total_stock_used == 5
        assert len(plan.assignments) == 5

        # Each assignment should have 1 cut
        for assignment in plan.assignments:
            assert len(assignment.cuts) == 1
            assert assignment.cuts[0][1] == 5000

    def test_bar_longer_than_stock_raises_error(self):
        """Bar longer than any stock length should raise ValueError."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=25,
                no_of_bars=1,
                cut_length_mm=13000,  # Longer than max stock (12000)
                total_length_mm=13000,
                unit_weight_kg=50.09,
                total_weight_kg=50.09,
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            optimize_cutting_stock(items, stock_lengths=[6000, 9000, 12000], kerf=3.0)

        assert "exceeds maximum stock length" in str(exc_info.value)
        assert "13000" in str(exc_info.value)

    def test_waste_calculation_accuracy(self):
        """Waste calculation should be accurate."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=3,
                cut_length_mm=3000,
                total_length_mm=9000,
                unit_weight_kg=4.74,
                total_weight_kg=14.22,
            ),
        ]

        plan = optimize_cutting_stock(items, stock_lengths=[6000, 9000], kerf=3.0)

        # Algorithm uses first-fit-decreasing:
        # - 2 cuts fit in 9000mm stock (2×3000 + 2×3 kerf = 6006mm used, 2994mm waste)
        # - 1 remaining cut requires separate stock bar

        # Total waste should be calculated correctly
        total_cuts_length = 3 * 3000
        total_kerf = 3 * 3.0
        total_stock_length = sum(a.stock_length for a in plan.assignments)
        expected_waste = total_stock_length - total_cuts_length - total_kerf

        assert abs(plan.total_waste - expected_waste) < 1

        # Waste percentage
        expected_pct = expected_waste / total_stock_length * 100
        assert abs(plan.waste_percentage - expected_pct) < 0.1

    def test_first_fit_decreasing_order(self):
        """Algorithm should process cuts in descending order (largest first)."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=2,
                cut_length_mm=1000,  # Smaller
                total_length_mm=2000,
                unit_weight_kg=1.58,
                total_weight_kg=3.16,
            ),
            BBSLineItem(
                bar_mark="B2",
                member_id="B1",
                location="top",
                zone="full",
                shape_code="A",
                diameter_mm=20,
                no_of_bars=2,
                cut_length_mm=4000,  # Larger
                total_length_mm=8000,
                unit_weight_kg=9.86,
                total_weight_kg=19.72,
            ),
        ]

        plan = optimize_cutting_stock(items, stock_lengths=[6000], kerf=3.0)

        # First-fit-decreasing should place 4000mm cuts first
        # Then try to fit 1000mm cuts in remaining space
        # 6000mm stock: 4000 + 3 (kerf) + 1000 + 3 (kerf) = 5006, leaving 994
        # So can fit 1×4000 + 1×1000 per stock
        # Total: 2×4000 + 2×1000 = need 2 stocks

        assert plan.total_stock_used == 2

    def test_kerf_handling(self):
        """Kerf (saw cut loss) should be properly accounted for."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=12,
                no_of_bars=10,
                cut_length_mm=500,
                total_length_mm=5000,
                unit_weight_kg=0.44,
                total_weight_kg=4.4,
            ),
        ]

        # Test with different kerf values
        plan_no_kerf = optimize_cutting_stock(items, stock_lengths=[6000], kerf=0.0)
        plan_with_kerf = optimize_cutting_stock(items, stock_lengths=[6000], kerf=5.0)

        # With no kerf: 10×500 = 5000, fits in 1 stock (6000mm)
        assert plan_no_kerf.total_stock_used == 1

        # With 5mm kerf per cut: need to account for 10×5 = 50mm kerf
        # 10×500 + 10×5 = 5050, still fits in 1 stock
        assert plan_with_kerf.total_stock_used == 1

        # Waste should differ by kerf amount
        waste_diff = plan_no_kerf.total_waste - plan_with_kerf.total_waste
        assert abs(waste_diff - 50) < 1  # 10 cuts × 5mm kerf

    def test_optimal_stock_selection(self):
        """Algorithm should prefer smallest stock that fits."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=1,
                cut_length_mm=5500,
                total_length_mm=5500,
                unit_weight_kg=8.69,
                total_weight_kg=8.69,
            ),
        ]

        plan = optimize_cutting_stock(
            items, stock_lengths=[6000, 7500, 9000, 12000], kerf=3.0
        )

        # 5500mm cut needs 5503mm with kerf
        # Should select 6000mm stock (smallest that fits)
        assert plan.assignments[0].stock_length == 6000

    def test_empty_items_list(self):
        """Empty items list should return empty plan."""

        plan = optimize_cutting_stock([], stock_lengths=[6000], kerf=3.0)

        assert plan.total_stock_used == 0
        assert len(plan.assignments) == 0
        assert plan.total_waste == 0
        assert plan.waste_percentage == 0

    def test_default_stock_lengths(self):
        """Should use default stock lengths when not specified."""

        items = [
            BBSLineItem(
                bar_mark="B1",
                member_id="B1",
                location="bottom",
                zone="full",
                shape_code="A",
                diameter_mm=16,
                no_of_bars=1,
                cut_length_mm=5000,
                total_length_mm=5000,
                unit_weight_kg=7.9,
                total_weight_kg=7.9,
            ),
        ]

        # Call without stock_lengths parameter
        plan = optimize_cutting_stock(items, kerf=3.0)

        # Should use default stock lengths
        # 5000 + 3 kerf = 5003, so should select 6000mm
        assert plan.assignments[0].stock_length in STANDARD_STOCK_LENGTHS_MM
