# SPDX-License-Identifier: MIT
"""
Insights API Models.

Models for dashboard insights and live code checks.
"""

from pydantic import BaseModel, Field


class DashboardRequest(BaseModel):
    """Request for smart dashboard insights."""

    width: float = Field(gt=0, description="Beam width (mm)")
    depth: float = Field(gt=0, description="Beam depth (mm)")
    span: float = Field(gt=0, description="Beam span (mm)")
    moment: float = Field(ge=0, description="Design moment (kN·m)")
    shear: float = Field(default=0.0, ge=0, description="Design shear (kN)")
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (MPa)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (MPa)")
    cover: float = Field(default=40.0, ge=20.0, description="Clear cover (mm)")
    include_cost: bool = Field(default=True)
    include_suggestions: bool = Field(default=True)
    include_sensitivity: bool = Field(default=True)
    include_constructability: bool = Field(default=True)


class DashboardResponse(BaseModel):
    success: bool
    message: str
    dashboard: dict | None = None
    warnings: list[str] = Field(default_factory=list)


class CodeChecksRequest(BaseModel):
    """Request for live code checks."""

    width: float = Field(gt=0, description="Beam width (mm)")
    depth: float = Field(gt=0, description="Beam depth (mm)")
    span: float = Field(gt=0, description="Beam span (mm)")
    moment: float = Field(ge=0, description="Design moment (kN·m)")
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (MPa)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (MPa)")
    cover: float = Field(default=40.0, ge=20.0, description="Clear cover (mm)")


class CodeChecksResponse(BaseModel):
    success: bool
    message: str
    checks: dict | None = None
    warnings: list[str] = Field(default_factory=list)
