"""
Integration Tests for FastAPI Endpoints.

Tests all API endpoints using FastAPI TestClient.
"""

from fastapi import status


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        assert "documentation" in data
        assert data["documentation"]["swagger_ui"] == "/docs"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "ready" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_system_info(self, client):
        """Test system info endpoint."""
        response = client.get("/health/info")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "python_version" in data
        assert "platform" in data
        assert "api_version" in data


class TestDesignEndpoints:
    """Tests for beam design endpoints."""

    def test_design_beam_basic(self, client, sample_beam_design_request):
        """Test basic beam design calculation."""
        response = client.post("/api/v1/design/beam", json=sample_beam_design_request)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "flexure" in data
        assert "ast_total" in data
        assert data["ast_total"] > 0

    def test_design_beam_validation_error(self, client):
        """Test validation error for invalid request."""
        invalid_request = {
            "width": -100,  # Invalid: negative width
            "depth": 500,
            "moment": 150,
        }

        response = client.post("/api/v1/design/beam", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_design_beam_depth_ratio_validation(self, client):
        """Test depth/width ratio validation."""
        request = {
            "width": 100,
            "depth": 1000,  # Ratio = 10, exceeds limit of 6
            "moment": 50,
        }

        response = client.post("/api/v1/design/beam", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_check_beam(self, client, sample_beam_check_request):
        """Test beam adequacy check."""
        response = client.post(
            "/api/v1/design/beam/check", json=sample_beam_check_request
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "is_adequate" in data
        assert "moment_capacity" in data
        assert "shear_capacity" in data
        assert "moment_utilization" in data
        assert "shear_utilization" in data

    def test_get_design_limits(self, client):
        """Test get design limits endpoint."""
        response = client.get("/api/v1/design/limits")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "concrete" in data
        assert "steel" in data
        assert "reinforcement" in data
        assert "clear_cover" in data


class TestDetailingEndpoints:
    """Tests for beam detailing endpoints."""

    def test_detail_beam(self, client, sample_detailing_request):
        """Test beam detailing calculation."""
        response = client.post("/api/v1/detailing/beam", json=sample_detailing_request)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "tension_bars" in data
        assert "ast_provided" in data

    def test_get_bar_areas(self, client):
        """Test get bar areas endpoint."""
        response = client.get("/api/v1/detailing/bar-areas")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "bars" in data
        assert "T16" in data["bars"]
        assert data["bars"]["T16"]["diameter_mm"] == 16

    def test_development_length(self, client):
        """Test development length calculation."""
        response = client.get(
            "/api/v1/detailing/development-length/16",
            params={"fck": 25.0, "fy": 500.0, "bar_type": "deformed"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["bar_diameter"] == 16
        assert "ld" in data
        assert data["ld"] > 0


class TestImportEndpoints:
    """Tests for CSV import endpoints."""

    def test_dual_csv_import(self, client):
        """Test dual CSV import endpoint."""
        geometry_csv = (
            "BeamID,Story,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)\n"
            "B1,GF,300,500,5000,25,500,40\n"
        )
        forces_csv = "BeamID,Story,Mu (kN-m),Vu (kN)\nB1,GF,150,80\n"

        files = {
            "geometry_file": (
                "geometry.csv",
                geometry_csv.encode("utf-8"),
                "text/csv",
            ),
            "forces_file": (
                "forces.csv",
                forces_csv.encode("utf-8"),
                "text/csv",
            ),
        }
        response = client.post(
            "/api/v1/import/dual-csv?format_hint=generic",
            files=files,
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["beam_count"] == 1
        assert data["beams"][0]["point1"] is not None


class TestOptimizationEndpoints:
    """Tests for cost optimization endpoints."""

    def test_optimize_beam_cost(self, client, sample_optimization_request):
        """Test beam cost optimization."""
        response = client.post(
            "/api/v1/optimization/beam/cost",
            json=sample_optimization_request,
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "optimal" in data
        assert data["optimal"]["width"] > 0
        assert data["optimal"]["depth"] > 0
        assert "cost_breakdown" in data["optimal"]

    def test_get_cost_rates(self, client):
        """Test get cost rates endpoint."""
        response = client.get("/api/v1/optimization/cost-rates")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "materials" in data
        assert "concrete" in data["materials"]
        assert "steel" in data["materials"]


class TestAnalysisEndpoints:
    """Tests for smart analysis endpoints."""

    def test_smart_analyze_beam(self, client, sample_analysis_request):
        """Test smart beam analysis."""
        response = client.post(
            "/api/v1/analysis/beam/smart",
            json=sample_analysis_request,
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "design_summary" in data
        assert "all_checks_passed" in data

    def test_get_code_clauses(self, client):
        """Test get code clauses endpoint."""
        response = client.get("/api/v1/analysis/code-clauses")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "flexure" in data
        assert "shear" in data
        assert "detailing" in data


class TestGeometryEndpoints:
    """Tests for 3D geometry endpoints."""

    def test_generate_beam_geometry(self, client, sample_geometry_request):
        """Test beam geometry generation."""
        response = client.post(
            "/api/v1/geometry/beam/3d",
            json=sample_geometry_request,
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "components" in data
        assert "bounding_box" in data
        assert "center" in data
        assert len(data["center"]) == 3
        assert "total_vertices" in data
        assert "total_faces" in data

    def test_generate_beam_geometry_minimal(self, client):
        """Test minimal geometry request (no reinforcement)."""
        minimal_request = {
            "width": 300.0,
            "depth": 500.0,
            "length": 2000.0,
            "include_rebars": False,
            "include_stirrups": False,
        }

        response = client.post("/api/v1/geometry/beam/3d", json=minimal_request)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert len(data["components"]) >= 1  # At least beam body

    def test_get_materials(self, client):
        """Test get materials endpoint."""
        response = client.get("/api/v1/geometry/materials")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "concrete" in data
        assert "steel" in data
        assert "color" in data["concrete"]


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation endpoints."""

    def test_openapi_json(self, client):
        """Test OpenAPI JSON endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Structural Engineering API"

    def test_swagger_ui(self, client):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

    def test_redoc(self, client):
        """Test ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/api/v1/design/beam",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        # FastAPI handles OPTIONS automatically with CORS middleware
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_cors_response_headers(self, client):
        """Test CORS headers in response."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Check CORS headers are present
        assert "access-control-allow-origin" in response.headers
