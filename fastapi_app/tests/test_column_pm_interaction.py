"""
Tests for POST /api/v1/design/column/interaction-curve endpoint.

Tests cover:
- Happy path: valid request returns 200 with points, key values
- Custom n_points
- Validation: Pydantic rejects invalid inputs (422)
"""

from fastapi.testclient import TestClient

from fastapi_app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/design/column/interaction-curve"

VALID_REQUEST = {
    "b_mm": 300.0,
    "D_mm": 450.0,
    "fck": 25.0,
    "fy": 415.0,
    "Asc_mm2": 2400.0,
    "d_prime_mm": 50.0,
}


class TestPMInteractionCurveHappyPath:
    """Tests for successful P-M interaction curve generation."""

    def test_pm_interaction_curve_valid(self):
        """Valid request returns 200 with curve data."""
        resp = client.post(ENDPOINT, json=VALID_REQUEST)
        assert resp.status_code == 200
        data = resp.json()

        # Points array present and non-empty
        assert "points" in data
        assert len(data["points"]) > 0

        # Each point has Pu_kN and Mu_kNm
        for pt in data["points"]:
            assert "Pu_kN" in pt
            assert "Mu_kNm" in pt

        # Key capacities present and positive
        assert data["Pu_0_kN"] > 0
        assert data["Mu_0_kNm"] >= 0
        assert data["Pu_bal_kN"] > 0
        assert data["Mu_bal_kNm"] > 0

        # Echo-back fields
        assert data["fck"] == 25.0
        assert data["fy"] == 415.0
        assert data["b_mm"] == 300.0
        assert data["D_mm"] == 450.0
        assert data["Asc_mm2"] == 2400.0
        assert data["d_prime_mm"] == 50.0
        assert data["clause_ref"] == "Cl. 39.5"

    def test_pm_interaction_curve_custom_n_points(self):
        """n_points=100 returns n_points+1 sweep points + pure axial cap point."""
        req = {**VALID_REQUEST, "n_points": 100}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 200
        data = resp.json()
        # Sweep generates n_points+1 points; pure axial cap (Pu_0, 0) may be
        # appended if the last sweep point doesn't already match it.
        assert len(data["points"]) >= 101


class TestPMInteractionCurveValidation:
    """Tests for Pydantic input validation (422 errors)."""

    def test_pm_interaction_curve_invalid_dimensions(self):
        """b_mm=0 is rejected (gt=0)."""
        req = {**VALID_REQUEST, "b_mm": 0.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_pm_interaction_curve_invalid_fck(self):
        """fck=0 is rejected (ge=15)."""
        req = {**VALID_REQUEST, "fck": 0.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_pm_interaction_curve_invalid_n_points(self):
        """n_points=5 is rejected (ge=10)."""
        req = {**VALID_REQUEST, "n_points": 5}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_pm_interaction_curve_missing_required_field(self):
        """Omitting Asc_mm2 returns 422."""
        req = {**VALID_REQUEST}
        del req["Asc_mm2"]
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422

    def test_pm_interaction_curve_d_prime_too_large(self):
        """d_prime_mm > 200 is rejected."""
        req = {**VALID_REQUEST, "d_prime_mm": 250.0}
        resp = client.post(ENDPOINT, json=req)
        assert resp.status_code == 422
