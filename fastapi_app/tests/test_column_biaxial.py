"""
Tests for POST /api/v1/design/column/biaxial-check endpoint.
"""

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap

client = TestClient(app)
ENDPOINT = "/api/v1/design/column/biaxial-check"

SAFE_PAYLOAD = {
    "Pu_kN": 1500.0,
    "Mux_kNm": 120.0,
    "Muy_kNm": 80.0,
    "b_mm": 400.0,
    "D_mm": 500.0,
    "le_mm": 3000.0,
    "fck": 25.0,
    "fy": 415.0,
    "Asc_mm2": 2400.0,
    "d_prime_mm": 50.0,
}


class TestBiaxialCheckHappyPath:
    """Tests for successful biaxial bending checks."""

    def test_safe_case_returns_200(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        assert resp.status_code == 200

    def test_safe_case_is_safe(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        assert data["is_safe"] is True
        assert data["interaction_ratio"] < 1.0

    def test_safe_case_response_fields(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        expected_keys = {
            "Pu_kN",
            "Mux_kNm",
            "Muy_kNm",
            "Mux1_kNm",
            "Muy1_kNm",
            "Puz_kN",
            "alpha_n",
            "interaction_ratio",
            "is_safe",
            "classification",
            "clause_ref",
            "warnings",
        }
        assert expected_keys == set(data.keys())

    def test_safe_case_clause_ref(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        assert data["clause_ref"] == "Cl. 39.6"

    def test_safe_case_capacities_positive(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        assert data["Mux1_kNm"] > 0
        assert data["Muy1_kNm"] > 0
        assert data["Puz_kN"] > 0

    def test_alpha_n_range(self):
        """alpha_n should be between 1.0 and 2.0 per IS 456 Cl 39.6."""
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        assert 1.0 <= data["alpha_n"] <= 2.0

    def test_echoes_input_loads(self):
        resp = client.post(ENDPOINT, json=SAFE_PAYLOAD)
        data = unwrap(resp)
        assert data["Pu_kN"] == 1500.0
        assert data["Mux_kNm"] == 120.0
        assert data["Muy_kNm"] == 80.0


class TestBiaxialCheckUnsafe:
    """Tests for unsafe biaxial cases (interaction_ratio > 1.0)."""

    def test_overloaded_column_unsafe(self):
        payload = {
            "Pu_kN": 2500.0,
            "Mux_kNm": 300.0,
            "Muy_kNm": 200.0,
            "b_mm": 300.0,
            "D_mm": 400.0,
            "le_mm": 3000.0,
            "fck": 25.0,
            "fy": 415.0,
            "Asc_mm2": 1600.0,
            "d_prime_mm": 50.0,
        }
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["is_safe"] is False
        assert data["interaction_ratio"] > 1.0


class TestBiaxialCheckEdgeCases:
    """Edge cases: zero moments, slender column, optional params."""

    def test_zero_moments(self):
        """Pure axial load - both moments zero."""
        payload = {**SAFE_PAYLOAD, "Mux_kNm": 0.0, "Muy_kNm": 0.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["interaction_ratio"] == 0.0
        assert data["is_safe"] is True

    def test_slender_column_warnings(self):
        """le/D >= 12 should produce slender classification and warnings."""
        payload = {**SAFE_PAYLOAD, "le_mm": 8000.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["classification"] == 2
        assert len(data["warnings"]) > 0

    def test_with_l_unsupported(self):
        """Providing optional l_unsupported_mm should still work."""
        payload = {**SAFE_PAYLOAD, "l_unsupported_mm": 3500.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert "is_safe" in data

    def test_without_l_unsupported(self):
        """Omitting l_unsupported_mm is valid (None default)."""
        payload = {**SAFE_PAYLOAD}
        assert "l_unsupported_mm" not in payload
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 200


class TestBiaxialCheckValidation:
    """Tests for input validation (422 responses)."""

    def test_missing_required_field(self):
        payload = {**SAFE_PAYLOAD}
        del payload["Pu_kN"]
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_negative_dimension(self):
        payload = {**SAFE_PAYLOAD, "b_mm": -100.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_zero_dimension(self):
        payload = {**SAFE_PAYLOAD, "D_mm": 0.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_fck_below_minimum(self):
        payload = {**SAFE_PAYLOAD, "fck": 5.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_fy_above_maximum(self):
        payload = {**SAFE_PAYLOAD, "fy": 700.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_negative_Pu(self):
        payload = {**SAFE_PAYLOAD, "Pu_kN": -10.0}
        resp = client.post(ENDPOINT, json=payload)
        assert resp.status_code == 422

    def test_empty_body(self):
        resp = client.post(ENDPOINT, json={})
        assert resp.status_code == 422
