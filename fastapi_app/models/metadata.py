"""Typed payload models for maintained static JSON metadata routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class APIInfoResponse(BaseModel):
    """Root API discovery payload."""

    name: str
    version: str
    documentation: dict[str, str]
    api_prefix: str
    status: str


class DesignLimitsResponse(BaseModel):
    """Named IS 456 design-limit groups."""

    concrete: dict[str, Any]
    steel: dict[str, Any]
    reinforcement: dict[str, Any]
    clear_cover: dict[str, Any]
    tau_c_max: dict[str, Any]


class CostRatesResponse(BaseModel):
    """Default optimization rate groups and their context."""

    materials: dict[str, dict[str, Any]]
    labor: dict[str, Any]
    location: str
    year: int
    note: str


class CodeClausesResponse(BaseModel):
    """IS 456/IS 13920 references grouped by check type."""

    flexure: dict[str, str]
    shear: dict[str, str]
    detailing: dict[str, str]
    serviceability: dict[str, str]
    seismic: dict[str, str]


class MaterialAppearance(BaseModel):
    """Visualization material metadata."""

    color: list[float]
    roughness: float
    metalness: float
    description: str


class MaterialAppearancesResponse(BaseModel):
    """Named visualization material appearances."""

    concrete: MaterialAppearance
    steel: MaterialAppearance
    formwork: MaterialAppearance
    highlight: MaterialAppearance


class ImportFormatDescription(BaseModel):
    """One supported CSV input shape."""

    name: str
    description: str
    indicators: list[str]
    columns: dict[str, list[str]]
    example: str | None = None


class ImportFormatsResponse(BaseModel):
    """Supported CSV formats and auto-detection metadata."""

    formats: list[ImportFormatDescription]
    auto_detection: bool
    note: str


class DevelopmentLengthResponse(BaseModel):
    """One development-length calculation with explicit inputs and clause."""

    bar_diameter: int
    fck: float
    fy: float
    bar_type: str
    tau_bd: float
    ld: float
    ld_in_diameters: float
    clause: str
