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

    def test_torsion_design_basic(self, client):
        """Test torsion design per IS 456 Cl 41."""
        request = {
            "width": 300,
            "depth": 500,
            "torsion": 10,
            "moment": 120,
            "shear": 80,
            "fck": 25,
            "fy": 500,
        }
        response = client.post("/api/v1/design/beam/torsion", json=request)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["is_safe"] is True
        assert data["ve_kn"] > 0
        assert data["me_knm"] > 0
        assert data["stirrup_spacing"] > 0
        assert data["al_torsion"] > 0
        assert data["requires_closed_stirrups"] is True

    def test_torsion_design_unsafe_section(self, client):
        """Test torsion design with very high torsion → unsafe."""
        request = {
            "width": 150,
            "depth": 300,
            "torsion": 100,
            "moment": 200,
            "shear": 200,
            "fck": 20,
            "fy": 415,
        }
        response = client.post("/api/v1/design/beam/torsion", json=request)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_safe"] is False
        assert data["tv_equiv"] > data["tc_max"]

    def test_torsion_design_validation(self, client):
        """Test torsion validation — torsion must be > 0."""
        request = {
            "width": 300,
            "depth": 500,
            "torsion": -5,
            "moment": 100,
        }
        response = client.post("/api/v1/design/beam/torsion", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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

    def test_dual_csv_response_shape(self, client):
        """Dual CSV response must have exact keys matching TS DualCSVImportResponse."""
        geometry_csv = "BeamID,Story,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)\nB1,GF,300,500,5000,25,500,40\n"
        forces_csv = "BeamID,Story,Mu (kN-m),Vu (kN)\nB1,GF,150,80\n"
        files = {
            "geometry_file": ("g.csv", geometry_csv.encode(), "text/csv"),
            "forces_file": ("f.csv", forces_csv.encode(), "text/csv"),
        }
        response = client.post(
            "/api/v1/import/dual-csv?format_hint=generic", files=files
        )
        data = response.json()
        expected_keys = {
            "success",
            "message",
            "beam_count",
            "beams",
            "format_detected",
            "warnings",
            "unmatched_beams",
            "unmatched_forces",
        }
        assert set(data.keys()) == expected_keys

    def test_single_csv_import(self, client):
        """Test single CSV import endpoint."""
        csv_content = (
            "BeamID,Story,b (mm),D (mm),Span (mm),Mu (kN-m),Vu (kN),fck,fy,Cover (mm)\n"
            "B1,GF,300,500,5000,150,80,25,500,40\n"
            "B2,1F,250,450,4000,100,60,25,500,40\n"
        )
        files = {"file": ("beams.csv", csv_content.encode("utf-8"), "text/csv")}
        response = client.post("/api/v1/import/csv", files=files)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["beam_count"] == 2
        assert len(data["beams"]) == 2

    def test_single_csv_response_shape(self, client):
        """Single CSV response must NOT have column_mapping, must have format_detected."""
        csv_content = "BeamID,Story,b (mm),D (mm),Span (mm),Mu (kN-m),Vu (kN),fck,fy,Cover (mm)\nB1,GF,300,500,5000,150,80,25,500,40\n"
        files = {"file": ("beams.csv", csv_content.encode(), "text/csv")}
        response = client.post("/api/v1/import/csv", files=files)
        data = response.json()
        expected_keys = {
            "success",
            "message",
            "beam_count",
            "beams",
            "format_detected",
            "warnings",
        }
        assert set(data.keys()) == expected_keys
        assert "column_mapping" not in data

    def test_single_csv_beam_fields(self, client):
        """Each beam in CSV response must have all fields for store mapping."""
        csv_content = "BeamID,Story,b (mm),D (mm),Span (mm),Mu (kN-m),Vu (kN),fck,fy,Cover (mm)\nB1,GF,300,500,5000,150,80,25,500,40\n"
        files = {"file": ("beams.csv", csv_content.encode(), "text/csv")}
        response = client.post("/api/v1/import/csv", files=files)
        beam = response.json()["beams"][0]
        required = [
            "id",
            "width_mm",
            "depth_mm",
            "span_mm",
            "mu_knm",
            "vu_kn",
            "fck_mpa",
            "fy_mpa",
            "cover_mm",
        ]
        for field in required:
            assert field in beam, f"Missing field: {field}"

    def test_sample_data_endpoint(self, client):
        """Test sample data endpoint returns beams with 3D positions."""
        response = client.get("/api/v1/import/sample")
        # May be 404 if CSV files not present in test environment
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return  # Skip — sample CSVs not available in CI
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["beam_count"] > 0
        assert len(data["beams"]) == data["beam_count"]

    def test_sample_data_response_shape(self, client):
        """Sample data response must match TS SampleDataResponse interface."""
        response = client.get("/api/v1/import/sample")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return
        data = response.json()
        expected_keys = {
            "success",
            "message",
            "beam_count",
            "beams",
            "format_detected",
            "warnings",
        }
        assert set(data.keys()) == expected_keys

    def test_sample_data_beam_has_3d(self, client):
        """Each sample beam must have point1/point2 for 3D visualization."""
        response = client.get("/api/v1/import/sample")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return
        data = response.json()
        for beam in data["beams"]:
            assert "point1" in beam, f"Beam {beam['id']} missing point1"
            assert "point2" in beam, f"Beam {beam['id']} missing point2"
            assert beam["point1"] is not None
            required = [
                "id",
                "story",
                "width_mm",
                "depth_mm",
                "span_mm",
                "mu_knm",
                "vu_kn",
                "fck_mpa",
                "fy_mpa",
                "cover_mm",
            ]
            for field in required:
                assert field in beam, f"Beam {beam['id']} missing {field}"

    def test_batch_design(self, client):
        """Test batch design endpoint returns correct results."""
        beams = [
            {
                "id": "B1",
                "width_mm": 300,
                "depth_mm": 500,
                "span_mm": 5000,
                "mu_knm": 150,
                "vu_kn": 80,
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
            },
            {
                "id": "B2",
                "width_mm": 250,
                "depth_mm": 450,
                "span_mm": 4000,
                "mu_knm": 100,
                "vu_kn": 60,
                "fck_mpa": 30,
                "fy_mpa": 500,
                "cover_mm": 40,
            },
        ]
        response = client.post("/api/v1/import/batch-design", json=beams)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 2
        assert len(data["results"]) == 2

    def test_batch_design_response_shape(self, client):
        """Batch design response must use 'passed' not 'successful'."""
        beams = [
            {
                "id": "B1",
                "width_mm": 300,
                "depth_mm": 500,
                "span_mm": 5000,
                "mu_knm": 150,
                "vu_kn": 80,
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
            }
        ]
        response = client.post("/api/v1/import/batch-design", json=beams)
        data = response.json()
        expected_keys = {"success", "message", "total", "passed", "failed", "results"}
        assert set(data.keys()) == expected_keys
        assert "successful" not in data, "'successful' should be 'passed'"

    def test_batch_design_result_shape(self, client):
        """Each batch result must be flat BatchDesignResult, not nested DesignedBeam."""
        beams = [
            {
                "id": "B1",
                "width_mm": 300,
                "depth_mm": 500,
                "span_mm": 5000,
                "mu_knm": 150,
                "vu_kn": 80,
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
            }
        ]
        response = client.post("/api/v1/import/batch-design", json=beams)
        result = response.json()["results"][0]
        expected_keys = {
            "beam_id",
            "success",
            "ast_required",
            "asc_required",
            "stirrup_spacing",
            "is_safe",
            "utilization_ratio",
            "error",
        }
        assert set(result.keys()) == expected_keys
        assert result["ast_required"] > 0
        assert 0 < result["utilization_ratio"] < 5

    def test_batch_design_values(self, client):
        """Batch design must return meaningful design values."""
        beams = [
            {
                "id": "B1",
                "width_mm": 300,
                "depth_mm": 500,
                "span_mm": 5000,
                "mu_knm": 150,
                "vu_kn": 80,
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
            }
        ]
        response = client.post("/api/v1/import/batch-design", json=beams)
        r = response.json()["results"][0]
        assert r["success"] is True
        assert r["is_safe"] is True
        assert r["stirrup_spacing"] > 0


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

    def test_load_analysis_udl(self, client):
        """Test simple load analysis with UDL on SS beam."""
        response = client.post(
            "/api/v1/analysis/loads/simple",
            json={
                "span_mm": 6000,
                "support_condition": "simply_supported",
                "loads": [{"load_type": "udl", "magnitude": 20.0}],
                "num_points": 51,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["span_mm"] == 6000
        assert len(data["positions_mm"]) == 51
        assert len(data["bmd_knm"]) == 51
        assert len(data["sfd_kn"]) == 51
        # wL²/8 = 20*(6)²/8 = 90 kN·m
        assert abs(data["max_bm_knm"] - 90.0) < 1.0
        # wL/2 = 20*6/2 = 60 kN
        assert abs(data["max_sf_kn"] - 60.0) < 1.0
        assert len(data["critical_points"]) > 0

    def test_load_analysis_point_load(self, client):
        """Test load analysis with point load at midspan."""
        response = client.post(
            "/api/v1/analysis/loads/simple",
            json={
                "span_mm": 6000,
                "support_condition": "simply_supported",
                "loads": [
                    {"load_type": "point", "magnitude": 50.0, "position_mm": 3000}
                ],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # PL/4 = 50*6/4 = 75 kN·m
        assert abs(data["max_bm_knm"] - 75.0) < 1.0
        # P/2 = 25 kN
        assert abs(data["max_sf_kn"] - 25.0) < 1.0

    def test_load_analysis_cantilever(self, client):
        """Test cantilever beam with UDL."""
        response = client.post(
            "/api/v1/analysis/loads/simple",
            json={
                "span_mm": 3000,
                "support_condition": "cantilever",
                "loads": [{"load_type": "udl", "magnitude": 15.0}],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # wL²/2 = 15*(3)²/2 = 67.5 kN·m (hogging = negative)
        assert data["min_bm_knm"] < -60

    def test_load_analysis_validation(self, client):
        """Test load analysis validation — empty loads."""
        response = client.post(
            "/api/v1/analysis/loads/simple",
            json={
                "span_mm": 6000,
                "support_condition": "simply_supported",
                "loads": [],
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestExportEndpoints:
    """Tests for export endpoints (BBS, DXF, Report)."""

    def _report_payload(self, fmt="html"):
        return {
            "beam_id": "TEST-1",
            "width": 300,
            "depth": 500,
            "fck": 25,
            "fy": 500,
            "moment": 120,
            "shear": 80,
            "ast_required": 900,
            "ast_provided": 942,
            "utilization": 0.85,
            "is_safe": True,
            "format": fmt,
        }

    def test_export_report_html(self, client):
        """Test HTML report export."""
        response = client.post(
            "/api/v1/export/report", json=self._report_payload("html")
        )
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert len(response.content) > 100

    def test_export_report_json(self, client):
        """Test JSON report export."""
        response = client.post(
            "/api/v1/export/report", json=self._report_payload("json")
        )
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]

    def test_export_report_pdf(self, client):
        """Test PDF report export (requires weasyprint)."""
        response = client.post(
            "/api/v1/export/report", json=self._report_payload("pdf")
        )
        # Accepts either 200 (weasyprint installed) or 503 (not installed)
        if response.status_code == status.HTTP_200_OK:
            assert "application/pdf" in response.headers["content-type"]
            # PDF files start with %PDF
            assert response.content[:5] == b"%PDF-"
        else:
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_export_report_invalid_format(self, client):
        """Test invalid format is rejected."""
        response = client.post(
            "/api/v1/export/report", json=self._report_payload("docx")
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
