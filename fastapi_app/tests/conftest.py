"""
Test Fixtures for FastAPI Tests.

Provides shared test fixtures and configuration.
"""

import os

# Disable global rate limiter during tests to avoid interference with load tests
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app


def unwrap(response):
    """Extract data from APIResponse wrapper.

    All non-health, non-export endpoints now wrap responses in:
        {"success": true, "data": {...}}
    This helper asserts success and returns the inner data dict.
    """
    body = response.json()
    assert body["success"] is True, f"Expected success=True, got {body}"
    return body["data"]


# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="module")
def client():
    """
    Create a test client for the FastAPI application.

    Uses module scope to reuse client across tests for efficiency.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_beam_design_request():
    """Sample beam design request data."""
    return {
        "width": 300.0,
        "depth": 500.0,
        "moment": 150.0,
        "shear": 75.0,
        "fck": 25.0,
        "fy": 500.0,
        "clear_cover": 25.0,
        "stirrup_dia_mm": 8.0,
        "main_bar_dia_mm": 20.0,
    }


@pytest.fixture
def sample_beam_check_request():
    """Sample supplied-beam V2 check request data."""
    return {
        "schema_version": "beam-supplied-check/v2",
        "correlation_id": "REST-B1-ULS-1",
        "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS-1"},
        "section": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "effective_depth_basis": {
                "clear_cover_mm": 40.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 20.0,
            },
        },
        "materials": {
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "fy_transverse_nmm2": 415.0,
        },
        "actions": {
            "mu_knm": 100.0,
            "vu_kn": 60.0,
            "primary_tension_face": "BOTTOM",
        },
        "reinforcement": {
            "clear_cover_mm": 40.0,
            "tension": {"diameter_mm": 20.0, "bars_per_layer": [4]},
            "compression_or_hanger": {
                "diameter_mm": 12.0,
                "bars_per_layer": [2],
            },
            "stirrup_diameter_mm": 8.0,
            "stirrup_legs": 2,
            "stirrup_spacing_mm": 150.0,
            "bar_type": "deformed",
            "has_standard_bend_at_start": True,
            "has_standard_bend_at_end": True,
            "source_reference": "Reviewed schedule B1-R1",
        },
        "selection": {
            "permitted_diameters_mm": [12.0, 16.0, 20.0, 25.0],
            "maximum_layers": 2,
            "maximum_bars_per_layer": 8,
            "nominal_max_aggregate_size_mm": 20.0,
            "effective_depth_tolerance_mm": 1.0,
            "objective": "min_area",
            "source_reference": "Reviewed project bar catalogue P1",
        },
        "support": {
            "start_width_mm": 5000.0,
            "end_width_mm": 5000.0,
            "source_reference": "Reviewed supports C1 and C2",
        },
    }


@pytest.fixture
def sample_detailing_request():
    """Sample beam detailing request data."""
    return {
        "width": 300.0,
        "depth": 500.0,
        "ast_required": 850.0,
        "asc_required": 0.0,
        "asv_required": 0.5,
        "fck": 25.0,
        "fy": 500.0,
        "clear_cover": 25.0,
        "preferred_bar_dia": [16, 20],
        "max_layers": 2,
    }


@pytest.fixture
def sample_optimization_request():
    """Sample cost optimization request data."""
    return {
        "moment": 200.0,
        "shear": 100.0,
        "span_length": 6000.0,
        "fck": 25.0,
        "fy": 500.0,
        "clear_cover": 25.0,
        "main_bar_diameter": 16.0,
        "stirrup_diameter": 8.0,
        "stirrup_legs": 2,
        "cost_params": {
            "currency": "INR",
            "concrete_cost": 6000.0,
            "steel_cost": 60.0,
            "formwork_cost": 400.0,
            "congestion_threshold_pt": 2.5,
            "congestion_multiplier": 1.2,
            "location_factor": 1.0,
        },
        "constraints": {
            "min_width": 200.0,
            "max_width": 500.0,
            "min_depth": 300.0,
            "max_depth": 800.0,
            "width_step": 50.0,
            "depth_step": 50.0,
            "min_utilization": 0.7,
        },
        "optimize_for": "cost",
        "include_alternatives": True,
        "max_alternatives": 3,
    }


@pytest.fixture
def sample_analysis_request():
    """Sample smart analysis request data."""
    return {
        "width": 300.0,
        "depth": 500.0,
        "effective_depth": 450.0,
        "moment": 150.0,
        "shear": 75.0,
        "fck": 25.0,
        "fy": 500.0,
        "span_length": 5000.0,
        "exposure_class": "moderate",
        "seismic_zone": None,
        "include_suggestions": True,
        "include_code_checks": True,
        "analyze_efficiency": True,
    }


@pytest.fixture
def sample_geometry_request():
    """Sample 3D geometry request data."""
    return {
        "width": 300.0,
        "depth": 500.0,
        "length": 3000.0,
        "tension_bars": [{"diameter": 16, "count": 3, "layer": 1}],
        "compression_bars": [{"diameter": 12, "count": 2, "layer": 1}],
        "stirrup_diameter": 8,
        "stirrup_spacing": 150.0,
        "clear_cover": 25.0,
        "include_rebars": True,
        "include_stirrups": True,
        "mesh_resolution": "medium",
        "output_format": "vertices_faces",
    }
