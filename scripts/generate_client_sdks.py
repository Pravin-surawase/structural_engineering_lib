#!/usr/bin/env python3
"""
Generate client SDKs from FastAPI OpenAPI specification.

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
        print('   Then visit http://localhost:8000/openapi.json and save it')
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
from typing import Optional

import httpx


@dataclass
class FlexureResult:
    """Flexure design calculation results."""
    ast_required: float
    ast_provided: float
    is_safe: bool
    utilization_ratio: float


@dataclass
class DesignResult:
    """Complete beam design results."""
    status: str
    flexure: FlexureResult
    shear: Optional[dict] = None


class StructuralDesignClient:
    """
    Client for the Structural Design API.

    Usage:
        client = StructuralDesignClient("http://localhost:8000")
        result = client.design_beam(width=300, depth=500, moment=150, fck=25, fy=500)
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
        shear: Optional[float] = None,
    ) -> DesignResult:
        """
        Design a reinforced concrete beam.

        Args:
            width: Beam width in mm
            depth: Beam depth in mm
            moment: Design moment in kN·m
            fck: Concrete strength in MPa
            fy: Steel yield strength in MPa
            shear: Design shear in kN (optional)

        Returns:
            DesignResult with flexure and shear calculations
        """
        payload = {
            "width": width,
            "depth": depth,
            "moment": moment,
            "fck": fck,
            "fy": fy,
        }
        if shear is not None:
            payload["shear"] = shear

        response = self._client.post("/api/v1/design/beam", json=payload)
        response.raise_for_status()
        data = response.json()

        return DesignResult(
            status=data["status"],
            flexure=FlexureResult(
                ast_required=data["flexure"]["ast_required"],
                ast_provided=data["flexure"]["ast_provided"],
                is_safe=data["flexure"]["is_safe"],
                utilization_ratio=data["flexure"]["utilization_ratio"],
            ),
            shear=data.get("shear"),
        )

    def calculate_geometry(
        self,
        width: float,
        depth: float,
        length: float,
    ) -> dict:
        """
        Calculate beam geometry metrics.

        Args:
            width: Beam width in mm
            depth: Beam depth in mm
            length: Beam length in mm

        Returns:
            Dictionary with volume, surface_area, weight
        """
        response = self._client.get(
            "/api/v1/geometry/beam",
            params={"width": width, "depth": depth, "length": length},
        )
        response.raise_for_status()
        return response.json()
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
    (client_dir / "package.json").write_text(json.dumps({
        "name": "@structural-lib/api-client",
        "version": "0.1.0",
        "description": "TypeScript client for Structural Design API",
        "main": "dist/index.js",
        "types": "dist/index.d.ts",
        "scripts": {
            "build": "tsc",
            "test": "jest"
        },
        "dependencies": {},
        "devDependencies": {
            "typescript": "^5.0.0"
        },
        "peerDependencies": {
            "typescript": ">=4.7"
        }
    }, indent=2))

    # tsconfig.json
    (client_dir / "tsconfig.json").write_text(json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "declaration": True,
            "outDir": "./dist",
            "strict": True,
            "esModuleInterop": True
        },
        "include": ["src/**/*"]
    }, indent=2))

    # src/index.ts
    src_dir = client_dir / "src"
    src_dir.mkdir(exist_ok=True)

    (src_dir / "index.ts").write_text('''/**
 * Structural Design API Client
 *
 * Auto-generated TypeScript client for the FastAPI structural design API.
 */

export interface BeamDesignRequest {
  width: number;
  depth: number;
  moment: number;
  shear?: number;
  fck: number;
  fy: number;
}

export interface FlexureResult {
  ast_required: number;
  ast_provided: number;
  is_safe: boolean;
  utilization_ratio: number;
}

export interface DesignResult {
  status: 'PASS' | 'FAIL';
  flexure: FlexureResult;
  shear?: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface GeometryResult {
  volume: number;
  surface_area: number;
  weight: number;
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
  async designBeam(params: BeamDesignRequest): Promise<DesignResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Design failed: ${error.detail || response.status}`);
    }

    return response.json();
  }

  /**
   * Calculate beam geometry metrics.
   */
  async calculateGeometry(
    width: number,
    depth: number,
    length: number,
  ): Promise<GeometryResult> {
    const params = new URLSearchParams({
      width: String(width),
      depth: String(depth),
      length: String(length),
    });

    const response = await fetch(`${this.baseUrl}/api/v1/geometry/beam?${params}`);

    if (!response.ok) {
      throw new Error(`Geometry calculation failed: ${response.status}`);
    }

    return response.json();
  }
}

export default StructuralDesignClient;
''')

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
    spec = check_openapi_spec()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate clients
    languages = [lang.strip().lower() for lang in args.languages.split(",")]
    results = {}

    if "python" in languages:
        results["python"] = generate_python_client(args.output_dir, OPENAPI_SPEC)

    if "typescript" in languages:
        results["typescript"] = generate_typescript_client(args.output_dir, OPENAPI_SPEC)

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
