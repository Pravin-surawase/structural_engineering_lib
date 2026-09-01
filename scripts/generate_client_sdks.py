#!/usr/bin/env python3
"""
Generate client SDKs from FastAPI OpenAPI specification.

When to use: After changing FastAPI endpoints. Generates TypeScript/Python client SDKs from OpenAPI spec.

This script uses openapi-python-client and openapi-typescript to generate
type-safe client libraries for consuming the structural design API.

Usage:
    python scripts/generate_client_sdks.py [--output-dir clients] [--languages python,typescript]

Week 3 Implementation - V3 Migration
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent
FASTAPI_DIR = ROOT / "fastapi_app"
OPENAPI_SPEC = FASTAPI_DIR / "openapi_baseline.json"
OUTPUT_DIR = ROOT / "clients"


def check_openapi_spec() -> dict:
    """Load and validate OpenAPI specification."""
    if not OPENAPI_SPEC.exists():
        print(f"❌ OpenAPI spec not found: {OPENAPI_SPEC}")
        print("   Run the FastAPI server first to generate it:")
        print("   uvicorn fastapi_app.main:app --reload")
        print("   Then visit http://localhost:8000/openapi.json and save it")
        sys.exit(1)

    with open(OPENAPI_SPEC) as f:
        spec = json.load(f)

    print(f"✅ OpenAPI spec loaded: {spec.get('info', {}).get('title', 'Unknown')}")
    print(f"   Version: {spec.get('info', {}).get('version', 'Unknown')}")
    print(f"   Paths: {len(spec.get('paths', {}))}")

    return spec


def generate_python_client(output_dir: Path, spec_path: Path) -> bool:
    """Generate Python client using openapi-python-client."""
    print("\n📦 Generating Python Client...")

    # Check if openapi-python-client is installed
    try:
        result = subprocess.run(
            ["openapi-python-client", "--version"],
            capture_output=True,
            text=True,
        )
        has_tool = result.returncode == 0
    except FileNotFoundError:
        has_tool = False

    if not has_tool:
        print("⚠️  openapi-python-client not found. Install with:")
        print("   pip install openapi-python-client")

        # Generate basic Python client manually
        print("   Generating basic client instead...")
        return generate_basic_python_client(output_dir)

    client_dir = output_dir / "python"
    if client_dir.exists():
        shutil.rmtree(client_dir)

    result = subprocess.run(
        [
            "openapi-python-client",
            "generate",
            "--path",
            str(spec_path),
            "--output-path",
            str(client_dir),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✅ Python client generated: {client_dir}")
        return True
    else:
        print(f"❌ Failed to generate Python client: {result.stderr}")
        return generate_basic_python_client(output_dir)


def generate_basic_python_client(output_dir: Path) -> bool:
    """Generate a basic Python client without external tools."""
    client_dir = output_dir / "python" / "structural_client"
    client_dir.mkdir(parents=True, exist_ok=True)

    # __init__.py
    (client_dir / "__init__.py").write_text('''"""
Structural Design API Client.

Auto-generated from OpenAPI specification.
"""

from .client import StructuralDesignClient

__all__ = ["StructuralDesignClient"]
''')

    # client.py
    (client_dir / "client.py").write_text('''"""
Structural Design API Client.

Provides type-safe access to the FastAPI structural design API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class FlexureResult:
    """Flexure design calculation results."""

    ast_required: float
    ast_min: float
    ast_max: float
    xu: float
    xu_max: float
    is_under_reinforced: bool
    moment_capacity: float
    asc_required: float


@dataclass
class ShearResult:
    """Shear design calculation results."""

    tau_v: float
    tau_c: float
    tau_c_max: float
    asv_required: float
    stirrup_spacing: float
    sv_max: float
    shear_capacity: float


@dataclass
class BeamDesignResponse:
    """Complete beam design results."""

    success: bool
    message: str
    flexure: FlexureResult
    result_envelope: dict[str, Any]
    shear: Optional[ShearResult] = None
    ast_total: float = 0.0
    asc_total: float = 0.0
    utilization_ratio: float = 0.0
    effective_depth_basis: dict[str, Any] | None = None
    warnings: list[str] | None = None


class StructuralDesignClient:
    """
    Client for the Structural Design API.

    Usage:
        client = StructuralDesignClient("http://localhost:8000")
        result = client.design_beam(
            width=300,
            depth=500,
            moment=150,
            fck=25,
            fy=500,
            shear=75,
            clear_cover=25,
            stirrup_dia_mm=8,
            main_bar_dia_mm=20,
        )
        print(f"Ast required: {result.flexure.ast_required}")
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def health(self) -> dict:
        """Check API health status."""
        response = self._client.get("/health")
        response.raise_for_status()
        return response.json()

    def design_beam(
        self,
        width: float,
        depth: float,
        moment: float,
        fck: float,
        fy: float,
        shear: float,
        clear_cover: float,
        stirrup_dia_mm: float,
        main_bar_dia_mm: float,
        effective_depth: float | None = None,
    ) -> BeamDesignResponse:
        """
        Design a reinforced concrete beam.

        Args:
            width: Beam width in mm
            depth: Beam depth in mm
            moment: Design moment in kN·m
            fck: Concrete strength in MPa
            fy: Steel yield strength in MPa
            shear: Design shear in kN
            clear_cover: Clear cover in mm for derived effective depth
            stirrup_dia_mm: Stirrup diameter in mm for derived effective depth
            main_bar_dia_mm: Tension bar diameter in mm for derived effective depth
            effective_depth: Explicit effective depth in mm; omit to derive it

        Returns:
            BeamDesignResponse with flexure and shear calculations
        """
        payload = {
            "width": width,
            "depth": depth,
            "moment": moment,
            "fck": fck,
            "fy": fy,
            "clear_cover": clear_cover,
            "stirrup_dia_mm": stirrup_dia_mm,
            "main_bar_dia_mm": main_bar_dia_mm,
        }
        payload["shear"] = shear
        if effective_depth is not None:
            payload["effective_depth"] = effective_depth

        response = self._client.post("/api/v1/design/beam", json=payload)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            problem = response.json().get("error", {})
            code = problem.get("code", response.status_code)
            message = problem.get("message", "Request failed")
            raise RuntimeError(f"Design failed: {code}: {message}") from exc
        envelope = response.json()
        if envelope.get("success") is not True:
            raise RuntimeError(
                f"Design failed: {envelope.get('error', 'unknown error')}"
            )
        data = envelope["data"]

        shear_data = data.get("shear")
        shear_result = (
            ShearResult(
                tau_v=shear_data["tau_v"],
                tau_c=shear_data["tau_c"],
                tau_c_max=shear_data["tau_c_max"],
                asv_required=shear_data["asv_required"],
                stirrup_spacing=shear_data["stirrup_spacing"],
                sv_max=shear_data["sv_max"],
                shear_capacity=shear_data["shear_capacity"],
            )
            if shear_data
            else None
        )

        return BeamDesignResponse(
            success=data["success"],
            message=data["message"],
            result_envelope=data["result_envelope"],
            flexure=FlexureResult(
                ast_required=data["flexure"]["ast_required"],
                ast_min=data["flexure"]["ast_min"],
                ast_max=data["flexure"]["ast_max"],
                xu=data["flexure"]["xu"],
                xu_max=data["flexure"]["xu_max"],
                is_under_reinforced=data["flexure"]["is_under_reinforced"],
                moment_capacity=data["flexure"]["moment_capacity"],
                asc_required=data["flexure"]["asc_required"],
            ),
            shear=shear_result,
            ast_total=data["ast_total"],
            asc_total=data.get("asc_total", 0.0),
            utilization_ratio=data["utilization_ratio"],
            effective_depth_basis=data.get("effective_depth_basis"),
            warnings=data.get("warnings"),
        )

    def design_beam_v2(self, request: dict[str, Any]) -> dict[str, Any]:
        """Run the canonical nested ``beam-design-input/v1`` request.

        This method deliberately returns the versioned canonical dictionary;
        field names and status axes therefore match the Python facade exactly.
        """

        response = self._client.post("/api/v2/design/beam", json=request)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            problem = response.json().get("error", {})
            code = problem.get("code", response.status_code)
            message = problem.get("message", "Request failed")
            raise RuntimeError(f"Canonical design failed: {code}: {message}") from exc
        return response.json()

    def calculate_geometry(
        self,
        width: float,
        depth: float,
        length: float,
    ) -> dict:
        """
        Generate beam geometry through the maintained 3D route.

        Args:
            width: Beam width in mm
            depth: Beam depth in mm
            length: Beam length in mm

        Returns:
            Dictionary containing typed geometry components and bounds
        """
        response = self._client.post(
            "/api/v1/geometry/beam/3d",
            json={"width": width, "depth": depth, "length": length},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            problem = response.json().get("error", {})
            code = problem.get("code", response.status_code)
            message = problem.get("message", "Request failed")
            raise RuntimeError(
                f"Geometry generation failed: {code}: {message}"
            ) from exc
        envelope = response.json()
        if envelope.get("success") is not True:
            raise RuntimeError(
                f"Geometry generation failed: {envelope.get('error', 'unknown error')}"
            )
        return envelope["data"]
''')

    print(f"✅ Basic Python client generated: {client_dir}")
    return True


def generate_typescript_client(output_dir: Path, spec_path: Path) -> bool:
    """Generate TypeScript client using openapi-typescript."""
    print("\n📦 Generating TypeScript Client...")

    # Generate basic TypeScript client (skip npx which may hang)
    # Full openapi-typescript generation can be done manually with:
    #   npx openapi-typescript openapi.json -o api-types.ts
    return generate_basic_typescript_client(output_dir)


def generate_basic_typescript_client(output_dir: Path) -> bool:
    """Generate a basic TypeScript client."""
    client_dir = output_dir / "typescript"
    client_dir.mkdir(parents=True, exist_ok=True)

    # package.json
    (client_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "@structural-lib/api-client",
                "version": "0.1.0",
                "description": "TypeScript client for Structural Design API",
                "main": "dist/index.js",
                "types": "dist/index.d.ts",
                "scripts": {"build": "tsc", "test": "jest"},
                "dependencies": {},
                "devDependencies": {"typescript": "^5.0.0"},
                "peerDependencies": {"typescript": ">=4.7"},
            },
            indent=2,
        )
        + "\n"
    )

    # tsconfig.json
    (client_dir / "tsconfig.json").write_text(
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "declaration": True,
                    "outDir": "./dist",
                    "strict": True,
                    "esModuleInterop": True,
                },
                "include": ["src/**/*"],
            },
            indent=2,
        )
        + "\n"
    )

    # src/index.ts
    src_dir = client_dir / "src"
    src_dir.mkdir(exist_ok=True)

    (src_dir / "index.ts").write_text("""/**
 * Structural Design API Client
 *
 * Auto-generated TypeScript client for the FastAPI structural design API.
 */

export interface BeamDesignRequest {
  width: number;
  depth: number;
  moment: number;
  shear: number;
  fck: number;
  fy: number;
  clear_cover: number;
  stirrup_dia_mm: number;
  main_bar_dia_mm: number;
  effective_depth?: number;
}

export interface CanonicalBeamDesignRequestV1 {
  schema_version?: 'beam-design-input/v1';
  identity: { member_id: string; story: string; case_id: string };
  section: {
    span_mm?: number;
    b_mm: number;
    D_mm: number;
    d_mm?: number;
    effective_depth_basis?: {
      clear_cover_mm: number;
      stirrup_diameter_mm: number;
      tension_bar_diameter_mm: number;
    };
  };
  materials: { fck_nmm2: number; fy_nmm2: number };
  actions: { mu_knm: number; vu_kn: number; tu_knm?: number; primary_tension_face?: "TOP" | "BOTTOM" };
  calculation_basis: {
    d_dash_mm: number;
    asv_mm2: number;
    pt_percent?: number;
    ast_mm2_for_shear?: number;
  };
  detailing?: CanonicalBeamDetailingOptionsV1;
  serviceability?: Record<string, unknown>;
  source_provenance?: string;
}

export interface CanonicalBeamDetailingOptionsV1 {
  standard: 'IS456' | 'IS13920';
  clear_cover_mm: number;
  tension_bar_diameter_mm: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  compression_bar_diameter_mm: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  side_face_bar_diameter_mm?: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  nominal_top_steel_ratio: number;
  stirrup_diameter_mm: number;
  stirrup_legs: number;
  stirrup_spacing_support_mm: number;
  stirrup_spacing_mid_mm: number;
}

export interface CanonicalBeamDesignResponseV1 {
  schema_version: 'beam-design-result/v1';
  identity: CanonicalBeamDesignRequestV1['identity'];
  request: CanonicalBeamDesignRequestV1;
  envelope: BeamDesignResponse['result_envelope'];
  calculation: Record<string, unknown>;
  limitations: string[];
  assumptions: string[];
  provenance: string[];
}

export interface APIResponse<T> {
  success: true;
  data: T;
  clause_refs?: Record<string, string>;
}

export interface ProblemResponse {
  success: false;
  data: null;
  error: {
    schema_version: 'structural-problem/v1';
    code: string;
    message: string;
    details?: unknown;
    request_id?: string;
  };
}

export interface FlexureResult {
  ast_required: number;
  ast_min: number;
  ast_max: number;
  xu: number;
  xu_max: number;
  is_under_reinforced: boolean;
  moment_capacity: number;
  asc_required: number;
}

export interface ShearResult {
  tau_v: number;
  tau_c: number;
  tau_c_max: number;
  asv_required: number;
  stirrup_spacing: number;
  sv_max: number;
  shear_capacity: number;
}

export interface BeamDesignResponse {
  success: boolean;
  message: string;
  flexure: FlexureResult;
  shear?: ShearResult;
  ast_total: number;
  asc_total: number;
  utilization_ratio: number;
  effective_depth_used?: number;
  effective_depth_basis: {
    contract_version: 'effective-depth-basis/v1';
    source: 'EXPLICIT' | 'DERIVED';
    D_mm: number;
    d_mm: number;
    effective_depth_basis: Record<string, number> | null;
  };
  result_envelope: {
    schema_version: 'structural-result-envelope/v2';
    intake_status: 'VALID' | 'PARTIAL' | 'BLOCKED';
    calculation_status: 'NOT_EVALUATED' | 'COMPLETED' | 'ERROR';
    engineering_status: 'NOT_EVALUATED' | 'PASS' | 'FAIL' | 'HOLD';
    review_status: 'QUALIFIED_REVIEW_REQUIRED' | 'REVIEWED_ACCEPTED' | 'REVIEWED_REJECTED';
    qualified_review_required: boolean;
    freshness_status: 'CURRENT' | 'STALE';
    serviceability_escalation: string | null;
    overall_status: 'BLOCKED' | 'ERROR' | 'NOT_EVALUATED' | 'STALE' | 'PASS' | 'FAIL' | 'HOLD';
    result_identity: Record<string, string | null> | null;
    issues: Array<{ code: string; path: string; message: string }>;
  };
  warnings?: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface GeometryResult {
  success: boolean;
  message: string;
  components: Array<Record<string, unknown>>;
  bounding_box: Record<string, number>;
  center: number[];
  suggested_camera_distance: number;
  total_vertices: number;
  total_faces: number;
  stl_base64?: string | null;
  gltf_json?: Record<string, unknown> | null;
  warnings?: string[];
}

export class StructuralDesignClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\\/$/, '');
  }

  /**
   * Check API health status.
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Design a reinforced concrete beam.
   */
  async designBeam(params: BeamDesignRequest): Promise<BeamDesignResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Design failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }

    const envelope = await response.json() as APIResponse<BeamDesignResponse>;
    return envelope.data;
  }

  /** Run the canonical v2 nested beam contract. */
  async designBeamV2(
    request: CanonicalBeamDesignRequestV1,
  ): Promise<CanonicalBeamDesignResponseV1> {
    const response = await fetch(`${this.baseUrl}/api/v2/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Canonical design failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }
    return response.json() as Promise<CanonicalBeamDesignResponseV1>;
  }

  /**
   * Calculate beam geometry metrics.
   */
  async calculateGeometry(
    width: number,
    depth: number,
    length: number,
  ): Promise<GeometryResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/geometry/beam/3d`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width, depth, length }),
    });

    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Geometry calculation failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }

    const envelope = await response.json() as APIResponse<GeometryResult>;
    return envelope.data;
  }
}

export default StructuralDesignClient;
""")

    print(f"✅ TypeScript client generated: {client_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate client SDKs from OpenAPI specification"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for generated clients",
    )
    parser.add_argument(
        "--languages",
        type=str,
        default="python,typescript",
        help="Comma-separated list of languages to generate",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔧 Client SDK Generator")
    print("=" * 60)

    # Check OpenAPI spec
    check_openapi_spec()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate clients
    languages = [lang.strip().lower() for lang in args.languages.split(",")]
    results = {}

    if "python" in languages:
        results["python"] = generate_python_client(args.output_dir, OPENAPI_SPEC)

    if "typescript" in languages:
        results["typescript"] = generate_typescript_client(
            args.output_dir, OPENAPI_SPEC
        )

    # Summary
    print("\n" + "=" * 60)
    print("📊 Generation Summary")
    print("=" * 60)
    for lang, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {lang.capitalize()}")

    print(f"\n📁 Output: {args.output_dir}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
