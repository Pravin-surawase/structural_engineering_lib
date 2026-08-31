"""Bounded service-load inputs; no inferred stresses or reinforcement design."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel


class BeamServiceabilityBasisV1(StrictPublicModel):
    """Caller-owned service analysis bound to a section, station and bar revision."""

    member_id: str = Field(min_length=1, max_length=80)
    service_case_id: str = Field(min_length=1, max_length=80)
    station_mm: float = Field(ge=0)
    tension_face: Literal["TOP", "BOTTOM"]
    b_mm: float = Field(gt=0)
    h_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    reinforcement_reference: str = Field(min_length=1)
    service_load_reference: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class BeamSpanDepthCheckV1(StrictPublicModel):
    """Cl 23.2.1, rectangular member <=10 m; externally justified Fig 4/5 factors."""

    method: Literal["IS456_SPAN_DEPTH"]
    effective_span_mm: float = Field(gt=0, le=10000)
    support_condition: Literal["CANTILEVER", "SIMPLY_SUPPORTED", "CONTINUOUS"]
    mf_tension_steel: float = Field(gt=0, le=2)
    mf_compression_steel: float = Field(ge=1, le=1.5)
    span_support_reference: str = Field(min_length=1)
    modification_factors_reference: str = Field(min_length=1)


class BeamAnnexFCrackCheckV1(StrictPublicModel):
    """Supplied mean strain at the tension surface; not fs/Es by substitution."""

    method: Literal["IS456_ANNEX_F_TENSION_SURFACE"]
    exposure_class: Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE", "EXTREME"]
    cracking_harmful: bool
    limit_mm: float = Field(gt=0, le=0.3)
    limit_reference: str = Field(min_length=1)
    acr_mm: float = Field(gt=0)
    cmin_mm: float = Field(gt=0)
    x_mm: float = Field(gt=0)
    epsilon_m: float = Field(ge=0)
    fs_service_nmm2: float = Field(ge=0)
    es_nmm2: float = Field(gt=0)
    strain_geometry_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_limit_and_cover(self) -> Self:
        # Cl 35.3.2 with Amendment 4: particularly aggressive categories 0.1 mm.
        ceiling = (
            0.1
            if self.exposure_class in ("VERY_SEVERE", "EXTREME")
            else 0.2 if self.cracking_harmful or self.exposure_class != "MILD" else 0.3
        )
        if self.limit_mm > ceiling:
            raise ValueError(
                f"limit_mm exceeds the supported Cl 35.3.2 ceiling {ceiling}"
            )
        if self.acr_mm < self.cmin_mm:
            raise ValueError(
                "acr_mm must be at least cmin_mm (longitudinal-bar surface cover)"
            )
        return self


class BeamServiceabilityChecksV1(StrictPublicModel):
    """Both bounded checks are mandatory; opaque/partial method inputs stay held."""

    schema_version: Literal["beam-serviceability-checks/v1"]
    basis: BeamServiceabilityBasisV1
    deflection: BeamSpanDepthCheckV1
    crack_width: BeamAnnexFCrackCheckV1
