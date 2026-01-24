"""
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
    shear: Optional[ShearResult] = None
    ast_total: float = 0.0
    asc_total: float = 0.0
    utilization_ratio: float = 0.0
    warnings: list[str] | None = None


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
    ) -> BeamDesignResponse:
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
            BeamDesignResponse with flexure and shear calculations
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
            warnings=data.get("warnings"),
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
