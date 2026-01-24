"""
Test Fixtures for FastAPI Tests.

Provides shared test fixtures and configuration.
"""

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app


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
    }


@pytest.fixture
def sample_beam_check_request():
    """Sample beam check request data."""
    return {
        "width": 300.0,
        "depth": 500.0,
        "moment": 150.0,
        "shear": 75.0,
        "ast_provided": 942.0,  # 3T20
        "asc_provided": 0.0,
        "stirrup_area": 100.5,  # 2L8
        "stirrup_spacing": 150.0,
        "fck": 25.0,
        "fy": 500.0,
        "clear_cover": 25.0,
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
        "cost_params": {
            "concrete_cost": 6000.0,
            "steel_cost": 60.0,
            "formwork_cost": 400.0,
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
