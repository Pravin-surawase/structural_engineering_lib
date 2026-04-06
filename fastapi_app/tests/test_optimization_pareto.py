"""
Tests for Pareto multi-objective beam optimization endpoint.

Covers POST /api/v1/optimization/beam/pareto
"""

from fastapi import status

from fastapi_app.tests.conftest import unwrap


class TestParetoOptimization:
    """Tests for the Pareto beam optimization endpoint."""

    def test_pareto_valid_request(self, client):
        """Valid Pareto request returns 200 with pareto_front and all expected fields."""
        payload = {
            "span_mm": 5000.0,
            "mu_knm": 150.0,
            "vu_kn": 80.0,
            "cover_mm": 40,
            "max_candidates": 20,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = unwrap(response)
        # Response structure matches ParetoResponse model
        assert "pareto_front" in data
        assert "pareto_count" in data
        assert "total_candidates" in data
        assert "objectives_used" in data
        assert "computation_time_sec" in data

        assert isinstance(data["pareto_front"], list)
        assert data["pareto_count"] >= 0
        assert data["total_candidates"] >= 0
        assert isinstance(data["objectives_used"], list)
        assert data["computation_time_sec"] >= 0

    def test_pareto_invalid_negative_span(self, client):
        """Negative span_mm should be rejected with 422."""
        payload = {
            "span_mm": -1000.0,
            "mu_knm": 150.0,
            "vu_kn": 80.0,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_pareto_invalid_zero_moment(self, client):
        """Zero mu_knm should be rejected (gt=0 constraint)."""
        payload = {
            "span_mm": 5000.0,
            "mu_knm": 0.0,
            "vu_kn": 80.0,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_pareto_small_moment(self, client):
        """Very small (but valid) moment returns a valid result."""
        payload = {
            "span_mm": 3000.0,
            "mu_knm": 5.0,
            "vu_kn": 10.0,
            "max_candidates": 10,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = unwrap(response)
        assert isinstance(data["pareto_front"], list)

    def test_pareto_response_candidate_structure(self, client):
        """Each candidate in pareto_front has all ParetoCandidateResponse fields."""
        payload = {
            "span_mm": 6000.0,
            "mu_knm": 200.0,
            "vu_kn": 100.0,
            "max_candidates": 15,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = unwrap(response)
        if data["pareto_count"] > 0:
            candidate = data["pareto_front"][0]
            expected_fields = [
                "b_mm",
                "D_mm",
                "d_mm",
                "fck_nmm2",
                "fy_nmm2",
                "ast_required",
                "ast_provided",
                "bar_config",
                "cost",
                "steel_weight_kg",
                "utilization",
                "is_safe",
                "governing_clauses",
                "rank",
                "crowding_distance",
            ]
            for field in expected_fields:
                assert field in candidate, f"Missing field: {field}"

            # Sanity checks on values
            assert candidate["b_mm"] > 0
            assert candidate["D_mm"] > 0
            assert candidate["d_mm"] > 0
            assert 0 <= candidate["utilization"] <= 2.0
            assert isinstance(candidate["is_safe"], bool)
            assert isinstance(candidate["governing_clauses"], list)

    def test_pareto_custom_objectives(self, client):
        """Passing custom objectives list is accepted."""
        payload = {
            "span_mm": 5000.0,
            "mu_knm": 120.0,
            "vu_kn": 60.0,
            "objectives": ["cost", "utilization"],
            "max_candidates": 10,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = unwrap(response)
        assert "cost" in data["objectives_used"]

    def test_pareto_best_by_fields(self, client):
        """best_by_cost, best_by_utilization, best_by_weight are present (may be null)."""
        payload = {
            "span_mm": 5000.0,
            "mu_knm": 150.0,
            "vu_kn": 80.0,
            "max_candidates": 30,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = unwrap(response)
        # These fields should exist in the response (can be null)
        assert "best_by_cost" in data
        assert "best_by_utilization" in data
        assert "best_by_weight" in data

    def test_pareto_span_exceeds_max(self, client):
        """span_mm > 30000 should be rejected (le=30000 constraint)."""
        payload = {
            "span_mm": 50000.0,
            "mu_knm": 150.0,
            "vu_kn": 80.0,
        }
        response = client.post("/api/v1/optimization/beam/pareto", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
