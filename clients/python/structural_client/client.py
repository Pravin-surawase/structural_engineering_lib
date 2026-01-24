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
