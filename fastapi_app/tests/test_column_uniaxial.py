"""
Tests for POST /api/v1/design/column/uniaxial endpoint.

Tests cover:
- Happy path: safe design returns ok=True
- Unsafe design: overloaded column returns ok=False
- Pure bending: Pu=0 is valid
- Validation: Pydantic rejects invalid inputs (422)
"""

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap

client = TestClient(app)

ENDPOINT = "/api/v1/design/column/uniaxial"

# A safe design — values from the docstring example
SAFE_REQUEST = {
    "Pu_kN": 1200.0,
    "Mu_kNm": 150.0,
    "b_mm": 300.0,
    "D_mm": 450.0,
    "le_mm": 3000.0,
    "fck": 25.0,
    "fy": 415.0,
    "Asc_mm2": 2700.0,
    "d_prime_mm": 50.0,
    "l_unsupported_mm": 3000.0,
}


class TestColumnUniaxialHappyPath:
    """Tests for successful design calculations."""

    def test_safe_design_returns_200(self):
        """Safe design returns 200 with ok=True."""
        resp = client.post(ENDPOINT, json=SAFE_REQUEST)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["ok"] is True
        assert data["utilization"] < 1.0
        assert data["classification"] == "SHORT"
        assert data["Pu_cap_kN"] > 0
        assert data["Mu_cap_kNm"] > 0

    def test_response_contains_all_fields(self):
        """Response includes all expected fields."""
        resp = client.post(ENDPOINT, json=SAFE_REQUEST)
        data = unwrap(resp)
        expected_fields = {
            "ok",
            "utilization",
            "Pu_cap_kN",
            "Mu_cap_kNm",
            "classification",
            "eccentricity_mm",
            "e_min_mm",
            "warnings",
        }
        assert expected_fields.issubset(data.keys())

    def test_eccentricity_values(self):
        """Eccentricity is computed correctly."""
        resp = client.post(ENDPOINT, json=SAFE_REQUEST)
        data = unwrap(resp)
        assert data["eccentricity_mm"] > 0
        # e_min should be present when l_unsupported_mm is provided
        assert data["e_min_mm"] is not None
        assert data["e_min_mm"] > 0

    def test_without_l_unsupported(self):
        """Omitting l_unsupported_mm still works (e_min check skipped)."""
        req = {**SAFE_REQUEST}
        del req["l_unsupported_mm"]
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["ok"] is True

    def test_pure_bending_pu_zero(self):
        """Pu=0 (pure bending) is a valid case."""
        req = {**SAFE_REQUEST, "Pu_kN": 0.0, "Mu_kNm": 100.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 200


class TestColumnUniaxialUnsafe:
    """Tests for designs that exceed capacity."""

    def test_overloaded_column_returns_ok_false(self):
        """Heavily overloaded column should return ok=False."""
        req = {**SAFE_REQUEST, "Pu_kN": 50000.0, "Mu_kNm": 5000.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["ok"] is False
        assert data["utilization"] > 1.0


class TestColumnUniaxialValidation:
    """Tests for Pydantic input validation (422 errors)."""

    def test_negative_moment_rejected(self):
        """Negative moment should be rejected."""
        req = {**SAFE_REQUEST, "Mu_kNm": -50.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_width_too_small_rejected(self):
        """b_mm < 100 is rejected by Pydantic."""
        req = {**SAFE_REQUEST, "b_mm": 50.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_width_too_large_rejected(self):
        """b_mm > 2000 is rejected by Pydantic."""
        req = {**SAFE_REQUEST, "b_mm": 3000.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_fck_out_of_range_rejected(self):
        """fck < 15 is rejected."""
        req = {**SAFE_REQUEST, "fck": 5.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_missing_required_field(self):
        """Omitting a required field returns 422."""
        req = {**SAFE_REQUEST}
        del req["Pu_kN"]
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_zero_effective_length_rejected(self):
        """le_mm=0 is rejected (gt=0)."""
        req = {**SAFE_REQUEST, "le_mm": 0.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422
