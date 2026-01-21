"""
Tests for Session State Manager
=================================

Comprehensive unit tests for session management utilities.

Test Coverage:
- Data class creation and serialization
- Session state initialization
- Get/set operations
- History management
- Cache operations
- State export/import
- Helper functions

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-010
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from utils.session_manager import (
    BeamInputs,
    DesignResult,
    StateKeys,
    SessionStateManager,
    load_last_design,
    save_design_to_file,
    load_design_from_file,
    compare_designs,
    format_design_summary,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_inputs():
    """Sample beam inputs"""
    return BeamInputs(
        span_mm=5000,
        b_mm=300,
        d_mm=450,
        D_mm=500,
        fck_mpa=25,
        fy_mpa=500,
        mu_knm=120,
        vu_kn=80,
        cover_mm=30,
    )


@pytest.fixture
def sample_result(sample_inputs):
    """Sample design result"""
    return DesignResult(
        inputs=sample_inputs,
        ast_mm2=603,
        ast_provided_mm2=603,
        num_bars=3,
        bar_diameter_mm=16,
        stirrup_diameter_mm=8,
        stirrup_spacing_mm=175,
        utilization_pct=65.5,
        status="PASS",
        compliance_checks={"min_steel": True, "max_steel": True, "spacing": True},
        cost_per_meter=87.45,
    )


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit session state"""

    # Create a dict-like mock for session_state
    class MockSessionState(dict):
        pass

    mock_st = MockSessionState()

    # Create a mock streamlit module
    import sys
    from unittest.mock import MagicMock

    # Import first to get the module
    try:
        import streamlit as st_original
    except:
        pass

    mock_streamlit = MagicMock()
    mock_streamlit.session_state = mock_st

    # Patch at module level
    monkeypatch.setattr("streamlit.session_state", mock_st)

    # Also patch in the session_manager module
    import utils.session_manager

    monkeypatch.setattr(utils.session_manager, "st", mock_streamlit)

    # Initialize required keys for session manager
    mock_st["user_preferences"] = {}
    mock_st["design_history"] = []
    mock_st["current_inputs"] = None
    mock_st["current_result"] = None
    mock_st["design_cache"] = {}
    mock_st["last_computation_time"] = None

    yield mock_st


# =============================================================================
# Test Data Classes
# =============================================================================


class TestBeamInputs:
    """Test BeamInputs data class"""

    def test_creation(self, sample_inputs):
        """Test creating BeamInputs"""
        assert sample_inputs.span_mm == 5000
        assert sample_inputs.b_mm == 300
        assert sample_inputs.fck_mpa == 25
        assert sample_inputs.fy_mpa == 500
        assert sample_inputs.timestamp != ""

    def test_default_values(self):
        """Test default values"""
        inputs = BeamInputs()
        assert inputs.span_mm == 5000.0
        assert inputs.b_mm == 300.0
        assert inputs.d_mm == 450.0
        assert inputs.D_mm == 500.0
        assert inputs.fck_mpa == 25.0
        assert inputs.fy_mpa == 500.0

    def test_to_dict(self, sample_inputs):
        """Test converting to dictionary"""
        data = sample_inputs.to_dict()
        assert isinstance(data, dict)
        assert data["span_mm"] == 5000
        assert data["b_mm"] == 300
        assert "timestamp" in data

    def test_from_dict(self, sample_inputs):
        """Test creating from dictionary"""
        data = sample_inputs.to_dict()
        inputs = BeamInputs.from_dict(data)

        assert inputs.span_mm == sample_inputs.span_mm
        assert inputs.b_mm == sample_inputs.b_mm
        assert inputs.fck_mpa == sample_inputs.fck_mpa

    def test_timestamp_auto_set(self):
        """Test timestamp is auto-set if not provided"""
        inputs = BeamInputs()
        assert inputs.timestamp != ""

        # Should be recent (within last second)
        ts = datetime.fromisoformat(inputs.timestamp)
        now = datetime.now()
        assert (now - ts).total_seconds() < 1.0


class TestDesignResult:
    """Test DesignResult data class"""

    def test_creation(self, sample_result):
        """Test creating DesignResult"""
        assert sample_result.ast_mm2 == 603
        assert sample_result.num_bars == 3
        assert sample_result.bar_diameter_mm == 16
        assert sample_result.status == "PASS"
        assert sample_result.timestamp != ""

    def test_to_dict(self, sample_result):
        """Test converting to dictionary"""
        data = sample_result.to_dict()
        assert isinstance(data, dict)
        assert data["ast_mm2"] == 603
        assert data["status"] == "PASS"
        assert "inputs" in data
        assert isinstance(data["inputs"], dict)

    def test_from_dict(self, sample_result):
        """Test creating from dictionary"""
        data = sample_result.to_dict()
        result = DesignResult.from_dict(data)

        assert result.ast_mm2 == sample_result.ast_mm2
        assert result.num_bars == sample_result.num_bars
        assert result.status == sample_result.status
        assert result.inputs.span_mm == sample_result.inputs.span_mm

    def test_compliance_checks(self, sample_result):
        """Test compliance checks dictionary"""
        assert isinstance(sample_result.compliance_checks, dict)
        assert "min_steel" in sample_result.compliance_checks
        assert sample_result.compliance_checks["min_steel"] == True


# =============================================================================
# Test Session State Manager (without Streamlit)
# =============================================================================


class TestSessionStateManagerBasics:
    """Test SessionStateManager basic operations"""

    def test_input_hash_same_inputs(self, sample_inputs):
        """Test hash is same for identical inputs"""
        hash1 = SessionStateManager._input_hash(sample_inputs)
        hash2 = SessionStateManager._input_hash(sample_inputs)
        assert hash1 == hash2

    def test_input_hash_different_inputs(self, sample_inputs):
        """Test hash is different for different inputs"""
        inputs2 = BeamInputs(
            span_mm=6000,  # Different
            b_mm=300,
            d_mm=450,
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80,
        )

        hash1 = SessionStateManager._input_hash(sample_inputs)
        hash2 = SessionStateManager._input_hash(inputs2)
        assert hash1 != hash2

    def test_input_hash_precision(self):
        """Test hash handles floating point precision"""
        inputs1 = BeamInputs(
            span_mm=5000.0,
            b_mm=300.0,
            d_mm=450.0,
            D_mm=500.0,
            fck_mpa=25.0,
            fy_mpa=500.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )
        inputs2 = BeamInputs(
            span_mm=5000.01,
            b_mm=300.02,
            d_mm=450.0,
            D_mm=500.0,
            fck_mpa=25.0,
            fy_mpa=500.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )

        # Hashes should be same (rounded to 1 decimal place)
        hash1 = SessionStateManager._input_hash(inputs1)
        hash2 = SessionStateManager._input_hash(inputs2)
        assert hash1 == hash2


class TestStateExportImport:
    """Test state export/import functionality"""

    def test_export_state_structure(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test exported state has correct structure"""
        # Setup state
        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        # Export
        state = SessionStateManager.export_state()

        # Check structure
        assert "current_inputs" in state
        assert "current_result" in state
        assert "input_history" in state
        assert "result_history" in state
        assert "preferences" in state
        assert "export_timestamp" in state

    def test_export_import_roundtrip(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test export then import preserves data"""
        # Setup original state
        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        # Export
        state = SessionStateManager.export_state()

        # Clear and import
        mock_session_state.clear()
        SessionStateManager.import_state(state)

        # Verify
        imported_inputs = SessionStateManager.get_current_inputs()
        assert imported_inputs.span_mm == sample_inputs.span_mm
        assert imported_inputs.b_mm == sample_inputs.b_mm

        imported_result = SessionStateManager.get_current_result()
        assert imported_result.ast_mm2 == sample_result.ast_mm2
        assert imported_result.status == sample_result.status

    def test_export_json_serializable(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test exported state is JSON serializable"""
        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        state = SessionStateManager.export_state()

        # Should be able to serialize to JSON
        json_str = json.dumps(state)
        assert isinstance(json_str, str)

        # Should be able to deserialize
        restored = json.loads(json_str)
        assert restored["current_inputs"]["span_mm"] == 5000


# =============================================================================
# Test Helper Functions
# =============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    def test_compare_designs_all_metrics(self, sample_result):
        """Test compare_designs calculates all metrics"""
        # Create second result with different values
        inputs2 = BeamInputs(
            span_mm=5000,
            b_mm=350,
            d_mm=450,
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80,
        )
        result2 = DesignResult(
            inputs=inputs2,
            ast_mm2=603,
            ast_provided_mm2=650,
            num_bars=3,
            bar_diameter_mm=18,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=175,
            utilization_pct=75.0,
            status="PASS",
            compliance_checks={"min_steel": True},
            cost_per_meter=95.00,
        )

        comparison = compare_designs(sample_result, result2)

        assert "utilization_diff" in comparison
        assert "cost_diff" in comparison
        assert "cost_savings_pct" in comparison
        assert "steel_area_diff" in comparison
        assert "better_utilization" in comparison
        assert "more_economical" in comparison

    def test_compare_designs_utilization_diff(self, sample_result):
        """Test utilization difference calculation"""
        result2 = DesignResult(
            inputs=sample_result.inputs,
            ast_mm2=603,
            ast_provided_mm2=603,
            num_bars=3,
            bar_diameter_mm=16,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=175,
            utilization_pct=80.0,  # Different
            status="PASS",
            compliance_checks={},
            cost_per_meter=87.45,
        )

        comparison = compare_designs(sample_result, result2)
        assert comparison["utilization_diff"] == pytest.approx(14.5)  # 80 - 65.5

    def test_compare_designs_cost_savings(self, sample_result):
        """Test cost savings percentage calculation"""
        result2 = DesignResult(
            inputs=sample_result.inputs,
            ast_mm2=603,
            ast_provided_mm2=603,
            num_bars=3,
            bar_diameter_mm=16,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=175,
            utilization_pct=65.5,
            status="PASS",
            compliance_checks={},
            cost_per_meter=70.00,  # Cheaper
        )

        comparison = compare_designs(sample_result, result2)
        # Savings = (87.45 - 70) / 87.45 * 100 ≈ 19.97%
        assert comparison["cost_savings_pct"] == pytest.approx(19.97, rel=0.01)
        assert comparison["more_economical"] == True

    def test_format_design_summary_structure(self, sample_result):
        """Test format_design_summary produces valid output"""
        summary = format_design_summary(sample_result)

        assert isinstance(summary, str)
        assert len(summary) > 100
        assert "Design Summary" in summary
        assert "Geometry:" in summary
        assert "Materials:" in summary
        assert "Loading:" in summary
        assert "Design:" in summary
        assert "5,000 mm" in summary or "5000 mm" in summary
        assert "M25" in summary
        assert "Fe500" in summary
        assert "3-16mm bars" in summary

    def test_format_design_summary_contains_key_data(self, sample_result):
        """Test summary contains all key design data"""
        summary = format_design_summary(sample_result)

        # Geometry
        assert "300" in summary  # width
        assert "500" in summary  # depth

        # Materials
        assert "M25" in summary
        assert "Fe500" in summary

        # Loading
        assert "120" in summary  # moment
        assert "80" in summary  # shear

        # Design
        assert "603" in summary  # steel area
        assert "65.5%" in summary  # utilization
        assert "PASS" in summary
        assert "87.45" in summary  # cost


class TestFileOperations:
    """Test file save/load operations"""

    def test_save_and_load_design(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test saving and loading design from file"""
        # Setup state
        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            save_design_to_file(filepath)

            # Verify file exists and has content
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 100

            # Clear state
            mock_session_state.clear()

            # Load
            load_design_from_file(filepath)

            # Verify loaded data
            loaded_inputs = SessionStateManager.get_current_inputs()
            assert loaded_inputs.span_mm == sample_inputs.span_mm

        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_saved_file_is_valid_json(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test saved file is valid JSON"""
        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            save_design_to_file(filepath)

            # Load and parse JSON
            with open(filepath, "r") as f:
                data = json.load(f)

            # Verify structure
            assert "current_inputs" in data
            assert "export_timestamp" in data

        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_load_last_design_empty_history(self, mock_session_state):
        """Test loading last design when history is empty"""
        SessionStateManager.initialize()
        last_design = load_last_design()
        assert last_design is None

    def test_load_last_design_with_history(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test loading last design from history"""
        SessionStateManager.initialize()
        SessionStateManager.add_to_history(sample_inputs, sample_result)

        last_design = load_last_design()
        assert last_design is not None
        assert last_design.span_mm == sample_inputs.span_mm

    def test_history_limit(self, sample_inputs, sample_result, mock_session_state):
        """Test history is limited to 10 entries"""
        SessionStateManager.initialize()

        # Add 15 entries
        for i in range(15):
            inputs = BeamInputs(span_mm=5000 + i * 100)  # Vary span
            result = DesignResult(
                inputs=inputs,
                ast_mm2=600 + i,
                ast_provided_mm2=600 + i,
                num_bars=3,
                bar_diameter_mm=16,
                stirrup_diameter_mm=8,
                stirrup_spacing_mm=175,
                utilization_pct=65.0,
                status="PASS",
                compliance_checks={},
                cost_per_meter=87.0,
            )
            SessionStateManager.add_to_history(inputs, result)

        # Check only last 10 are kept
        history = SessionStateManager.get_history()
        assert len(history) == 10

        # Check it's the last 10 (should have span = 5500 to 5900 + 400)
        assert history[0].inputs.span_mm == 5500  # 6th entry (index 5)
        assert history[-1].inputs.span_mm == 5000 + 14 * 100  # 15th entry

    def test_cache_limit(self, sample_inputs, sample_result, mock_session_state):
        """Test cache is limited to 20 entries"""
        SessionStateManager.initialize()

        # Add 25 cache entries
        for i in range(25):
            inputs = BeamInputs(span_mm=5000 + i * 100)
            result = DesignResult(
                inputs=inputs,
                ast_mm2=600 + i,
                ast_provided_mm2=600 + i,
                num_bars=3,
                bar_diameter_mm=16,
                stirrup_diameter_mm=8,
                stirrup_spacing_mm=175,
                utilization_pct=65.0,
                status="PASS",
                compliance_checks={},
                cost_per_meter=87.0,
            )
            SessionStateManager.cache_design(inputs, result)

        # Check cache size
        cache = mock_session_state[StateKeys.DESIGN_CACHE]
        assert len(cache) <= 20


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for session manager"""

    def test_full_workflow(self, sample_inputs, sample_result, mock_session_state):
        """Test complete workflow"""
        # 1. Initialize
        SessionStateManager.initialize()

        # 2. Set inputs
        SessionStateManager.set_current_inputs(sample_inputs)

        # 3. Cache design
        SessionStateManager.cache_design(sample_inputs, sample_result)

        # 4. Verify cache hit
        cached = SessionStateManager.get_cached_design(sample_inputs)
        assert cached is not None
        assert cached.ast_mm2 == sample_result.ast_mm2

        # 5. Set result
        SessionStateManager.set_current_result(sample_result)

        # 6. Add to history
        SessionStateManager.add_to_history(sample_inputs, sample_result)

        # 7. Verify history
        history = SessionStateManager.get_history()
        assert len(history) == 1

        # 8. Export state
        state = SessionStateManager.export_state()
        assert state["current_result"]["ast_mm2"] == 603

        # 9. Clear and import
        mock_session_state.clear()
        SessionStateManager.import_state(state)

        # 10. Verify restored
        inputs = SessionStateManager.get_current_inputs()
        assert inputs.span_mm == 5000


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Test performance of session manager"""

    def test_cache_lookup_performance(
        self, sample_inputs, sample_result, mock_session_state
    ):
        """Test cache lookup is fast"""
        import time

        SessionStateManager.initialize()
        SessionStateManager.cache_design(sample_inputs, sample_result)

        start = time.time()
        for _ in range(1000):
            SessionStateManager.get_cached_design(sample_inputs)
        elapsed = time.time() - start

        # Should complete 1000 lookups in < 0.1 seconds
        assert elapsed < 0.1

    def test_export_performance(self, sample_inputs, sample_result, mock_session_state):
        """Test state export is fast"""
        import time

        SessionStateManager.initialize()
        SessionStateManager.set_current_inputs(sample_inputs)
        SessionStateManager.set_current_result(sample_result)

        # Add some history
        for _ in range(10):
            SessionStateManager.add_to_history(sample_inputs, sample_result)

        start = time.time()
        for _ in range(100):
            SessionStateManager.export_state()
        elapsed = time.time() - start

        # Should complete 100 exports in < 0.5 seconds
        assert elapsed < 0.5


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
