# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Adapters for converting various input formats to canonical models.

This module provides adapter classes that convert external data formats
(ETABS CSV, SAFE CSV, manual input) to the canonical Pydantic models
defined in models.py.

The adapter pattern allows:
- Easy addition of new input formats
- Format-specific validation and normalization
- Clean separation between parsing and business logic

Example:
    >>> from structural_lib.adapters import ETABSAdapter
    >>> adapter = ETABSAdapter()
    >>>
    >>> # Check if adapter can handle the file
    >>> if adapter.can_handle("frames_geometry.csv"):
    ...     beams = adapter.load_geometry("frames_geometry.csv")
    ...     print(f"Loaded {len(beams)} beams")

Architecture:
    See docs/architecture/canonical-data-format.md for full documentation.

Author: Session 40 Agent
Task: TASK-DATA-001
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import (
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    FrameType,
    Point3D,
    SectionProperties,
)


__all__ = [
    "InputAdapter",
    "ETABSAdapter",
    "ManualInputAdapter",
]


# =============================================================================
# Base Adapter Interface
# =============================================================================


class InputAdapter(ABC):
    """Base class for input format adapters.

    Subclasses implement format-specific loading logic while
    returning standardized canonical models.

    Attributes:
        name: Human-readable adapter name (e.g., "ETABS", "SAFE")
        supported_formats: List of file extensions this adapter handles
    """

    name: str = "Base"
    supported_formats: list[str] = []

    @abstractmethod
    def can_handle(self, source: Path | str) -> bool:
        """Check if this adapter can handle the given source.

        Args:
            source: Path to file or identifier

        Returns:
            True if this adapter can process the source
        """
        pass

    @abstractmethod
    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Load beam geometry from source.

        Args:
            source: Path to geometry file
            defaults: Default section properties to apply

        Returns:
            List of BeamGeometry models
        """
        pass

    @abstractmethod
    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Load beam forces from source.

        Args:
            source: Path to forces file

        Returns:
            List of BeamForces models (envelope values)
        """
        pass


# =============================================================================
# ETABS Adapter
# =============================================================================


class ETABSAdapter(InputAdapter):
    """Adapter for ETABS CSV exports.

    Handles both beam forces (Element Forces - Beams) and
    frame geometry (Connectivity - Frame) exports.

    Column name mappings support ETABS 2019-2024 formats.
    """

    name = "ETABS"
    supported_formats = [".csv"]

    # Column mappings for different ETABS versions
    GEOMETRY_COLUMNS: dict[str, list[str]] = {
        "unique_name": ["UniqueName", "Unique Name", "GUID", "Unique"],
        "label": ["Label", "Frame", "Element", "Name"],
        "story": ["Story", "Level", "Floor", "Storey"],
        "frame_type": ["ObjType", "Type", "ElementType", "FrameType"],
        "section_name": ["AnalSect", "Section", "SectionName", "PropName"],
        "point1_name": ["JointI", "PointI", "Point1", "NodeI"],
        "point2_name": ["JointJ", "PointJ", "Point2", "NodeJ"],
        "point1_x": ["XI", "X1", "Point1X", "XStart"],
        "point1_y": ["YI", "Y1", "Point1Y", "YStart"],
        "point1_z": ["ZI", "Z1", "Point1Z", "ZStart"],
        "point2_x": ["XJ", "X2", "Point2X", "XEnd"],
        "point2_y": ["YJ", "Y2", "Point2Y", "YEnd"],
        "point2_z": ["ZJ", "Z2", "Point2Z", "ZEnd"],
        "angle": ["Angle", "Rotation", "OffsetAngle"],
    }

    FORCES_COLUMNS: dict[str, list[str]] = {
        "story": ["Story", "Level", "Floor"],
        "beam_id": [
            "Label",
            "Frame",
            "Element",
            "Beam",
            "Name",
            "beam_id",
            "BeamID",
        ],
        "unique_name": ["Unique Name", "UniqueName", "Unique", "GUID"],
        "case_id": [
            "Output Case",
            "Load Case/Combo",
            "Load Case",
            "LoadCase",
            "Combo",
            "Case",
        ],
        "station": ["Station", "Location", "Distance", "Loc"],
        "m3": ["M3", "Moment", "M", "Mu", "MomentY", "Myy"],
        "v2": ["V2", "Shear", "V", "Vu", "ShearY", "Vyy"],
        "p": ["P", "Axial", "N", "Pu", "AxialForce"],
        # VBA envelope export format
        "mu_max": ["Mu_max_kNm", "Mu_max", "MuMax", "Mu"],
        "mu_min": ["Mu_min_kNm", "Mu_min", "MuMin"],
        "vu_max": ["Vu_max_kN", "Vu_max", "VuMax", "Vu"],
    }

    def __init__(self):
        """Initialize ETABS adapter."""
        self._column_cache: dict[str, dict[str, str]] = {}

    def can_handle(self, source: Path | str) -> bool:
        """Check if source is a valid ETABS CSV.

        Args:
            source: Path to file

        Returns:
            True if file is CSV and contains ETABS-like headers
        """
        path = Path(source)
        if not path.exists() or path.suffix.lower() != ".csv":
            return False

        try:
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, [])

            # Check for ETABS-specific columns
            header_set = {h.strip() for h in headers}
            geometry_indicators = {"Story", "Label", "XI", "XJ", "JointI", "JointJ"}
            forces_indicators = {"Story", "M3", "V2", "Output Case", "Station"}

            return bool(
                header_set & geometry_indicators or header_set & forces_indicators
            )
        except Exception:
            return False

    def _detect_column(
        self, headers: list[str], field: str, mapping: dict[str, list[str]]
    ) -> str | None:
        """Detect the actual column name for a logical field.

        Args:
            headers: CSV header row
            field: Logical field name (e.g., "story")
            mapping: Column name mapping dict

        Returns:
            Actual column name found, or None
        """
        possible_names = mapping.get(field, [])
        header_lower = {h.lower(): h for h in headers}

        for name in possible_names:
            if name.lower() in header_lower:
                return header_lower[name.lower()]

        return None

    def _build_column_map(
        self,
        headers: list[str],
        mapping: dict[str, list[str]],
    ) -> dict[str, str]:
        """Build a mapping from logical field names to actual column names.

        Args:
            headers: CSV header row
            mapping: Column name mapping dict

        Returns:
            Dict mapping logical names to actual column names
        """
        result = {}
        for field in mapping:
            actual = self._detect_column(headers, field, mapping)
            if actual:
                result[field] = actual
        return result

    def _parse_section_name(
        self,
        section_name: str,
        defaults: DesignDefaults | None,
    ) -> SectionProperties:
        """Parse section properties from ETABS section name.

        Attempts to parse dimensions from naming patterns like:
        - B230X450M20 -> width=230, depth=450, fck=20
        - RC300x500 -> width=300, depth=500
        - W12X26 -> (steel section, use defaults)

        Args:
            section_name: ETABS section name
            defaults: Default properties if parsing fails

        Returns:
            SectionProperties model
        """
        defaults = defaults or DesignDefaults()

        # Try to parse "BwidthXdepthMfck" pattern
        import re

        pattern = r"B(\d+)[Xx](\d+)(?:M(\d+))?"
        match = re.match(pattern, section_name.upper())

        if match:
            width = float(match.group(1))
            depth = float(match.group(2))
            fck = float(match.group(3)) if match.group(3) else defaults.fck_mpa

            return SectionProperties(
                width_mm=width,
                depth_mm=depth,
                fck_mpa=fck,
                fy_mpa=defaults.fy_mpa,
                cover_mm=defaults.cover_mm,
            )

        # Try simpler "widthxdepth" pattern
        simple_pattern = r"(\d+)[Xx](\d+)"
        match = re.search(simple_pattern, section_name)

        if match:
            width = float(match.group(1))
            depth = float(match.group(2))

            return SectionProperties(
                width_mm=width,
                depth_mm=depth,
                fck_mpa=defaults.fck_mpa,
                fy_mpa=defaults.fy_mpa,
                cover_mm=defaults.cover_mm,
            )

        # Use defaults if parsing fails
        return SectionProperties(
            width_mm=300,  # Default width
            depth_mm=500,  # Default depth
            fck_mpa=defaults.fck_mpa,
            fy_mpa=defaults.fy_mpa,
            cover_mm=defaults.cover_mm,
        )

    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Load beam geometry from ETABS frames_geometry CSV.

        Args:
            source: Path to frames_geometry.csv
            defaults: Default section properties

        Returns:
            List of BeamGeometry models for beam elements

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        defaults = defaults or DesignDefaults()
        beams: list[BeamGeometry] = []

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.GEOMETRY_COLUMNS)

            # Check required columns
            required = ["label", "story", "point1_x", "point1_y", "point1_z"]
            missing = [r for r in required if r not in column_map]
            if missing:
                raise ValueError(
                    f"Missing required columns: {missing}. "
                    f"Available: {list(column_map.keys())}"
                )

            for row in reader:
                # Skip non-beam elements
                frame_type_col = column_map.get("frame_type")
                if frame_type_col and row.get(frame_type_col, "").lower() not in (
                    "beam",
                    "",
                ):
                    continue

                # Extract coordinates
                try:
                    point1 = Point3D(
                        x=float(row[column_map["point1_x"]]),
                        y=float(row[column_map["point1_y"]]),
                        z=float(row[column_map["point1_z"]]),
                    )

                    point2_x_col = column_map.get("point2_x")
                    point2_y_col = column_map.get("point2_y")
                    point2_z_col = column_map.get("point2_z")

                    if all([point2_x_col, point2_y_col, point2_z_col]):
                        point2 = Point3D(
                            x=float(row[point2_x_col]),
                            y=float(row[point2_y_col]),
                            z=float(row[point2_z_col]),
                        )
                    else:
                        # Skip if no end point
                        continue

                except (KeyError, ValueError):
                    # Skip rows with invalid coordinates
                    continue

                # Extract section properties
                section_name_col = column_map.get("section_name")
                section_name = row.get(section_name_col, "") if section_name_col else ""
                section = self._parse_section_name(section_name, defaults)

                # Build beam ID
                label = row[column_map["label"]].strip()
                story = row[column_map["story"]].strip()
                beam_id = f"{label}_{story}"

                # Extract source ID
                source_id_col = column_map.get("unique_name")
                source_id = (
                    row.get(source_id_col, "").strip() if source_id_col else None
                )

                # Extract angle
                angle_col = column_map.get("angle")
                angle = float(row.get(angle_col, 0)) if angle_col else 0.0

                try:
                    beam = BeamGeometry(
                        id=beam_id,
                        label=label,
                        story=story,
                        frame_type=FrameType.BEAM,
                        point1=point1,
                        point2=point2,
                        section=section,
                        angle=angle,
                        source_id=source_id or None,
                    )
                    beams.append(beam)
                except Exception:
                    # Skip invalid beams (e.g., too short)
                    continue

        return beams

    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Load beam forces from ETABS beam forces CSV.

        Supports two formats:
        1. Raw ETABS station data (M3, V2, case_id columns)
           - Takes maximum absolute values across all stations
        2. VBA envelope export (Mu_max_kNm, Vu_max_kN columns)
           - Uses pre-computed envelope values directly

        Args:
            source: Path to beam_forces.csv

        Returns:
            List of BeamForces models (one per beam per load case)

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Collect envelope values per beam/case
        envelopes: dict[tuple[str, str, str], dict[str, Any]] = {}

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.FORCES_COLUMNS)

            # Detect format: VBA envelope vs raw ETABS
            is_vba_envelope = "mu_max" in column_map or "vu_max" in column_map
            is_raw_etabs = "m3" in column_map and "v2" in column_map

            if is_vba_envelope:
                # VBA envelope format - pre-computed envelope values
                required = ["beam_id"]
                # mu_max or vu_max must exist (at least one)
                if "mu_max" not in column_map and "vu_max" not in column_map:
                    raise ValueError(
                        "VBA envelope format requires Mu_max_kNm or Vu_max_kN column"
                    )
            elif is_raw_etabs:
                # Raw ETABS format with station data
                required = ["beam_id", "case_id", "m3", "v2"]
            else:
                raise ValueError(
                    "Could not detect format. Need either M3/V2 columns "
                    "(raw ETABS) or Mu_max_kNm/Vu_max_kN columns (VBA envelope). "
                    f"Available: {list(column_map.keys())}"
                )

            missing = [r for r in required if r not in column_map]
            if missing:
                raise ValueError(
                    f"Missing required columns: {missing}. "
                    f"Available: {list(column_map.keys())}"
                )

            for row in reader:
                try:
                    beam_id = row[column_map["beam_id"]].strip()
                    story_col = column_map.get("story")
                    story = row.get(story_col, "").strip() if story_col else ""

                    if is_vba_envelope:
                        # VBA envelope format - values already enveloped
                        case_id = "Envelope"  # Default case name for envelope data

                        # Get Mu - try mu_max first, then use max of mu_max and mu_min
                        mu_max_col = column_map.get("mu_max")
                        mu_min_col = column_map.get("mu_min")

                        mu = 0.0
                        if mu_max_col:
                            mu_max_val = abs(float(row.get(mu_max_col, 0) or 0))
                            mu = mu_max_val
                        if mu_min_col:
                            mu_min_val = abs(float(row.get(mu_min_col, 0) or 0))
                            mu = max(mu, mu_min_val)

                        # Get Vu
                        vu_col = column_map.get("vu_max")
                        vu = abs(float(row.get(vu_col, 0) or 0)) if vu_col else 0.0

                        key = (beam_id, story, case_id)
                        envelopes[key] = {
                            "beam_id": beam_id,
                            "story": story,
                            "case_id": case_id,
                            "mu_max": mu,
                            "vu_max": vu,
                            "pu_max": 0.0,
                            "station_count": 1,
                        }

                    else:
                        # Raw ETABS format - need to compute envelope
                        case_id = row[column_map["case_id"]].strip()

                        m3 = abs(float(row[column_map["m3"]]))
                        v2 = abs(float(row[column_map["v2"]]))

                        p_col = column_map.get("p")
                        p = abs(float(row.get(p_col, 0))) if p_col else 0.0

                        key = (beam_id, story, case_id)

                        if key not in envelopes:
                            envelopes[key] = {
                                "beam_id": beam_id,
                                "story": story,
                                "case_id": case_id,
                                "mu_max": m3,
                                "vu_max": v2,
                                "pu_max": p,
                                "station_count": 1,
                            }
                        else:
                            env = envelopes[key]
                            env["mu_max"] = max(env["mu_max"], m3)
                            env["vu_max"] = max(env["vu_max"], v2)
                            env["pu_max"] = max(env["pu_max"], p)
                            env["station_count"] += 1

                except (KeyError, ValueError):
                    # Skip invalid rows
                    continue

        # Convert to BeamForces models
        forces: list[BeamForces] = []
        for env in envelopes.values():
            # Build ID matching BeamGeometry format
            beam_id = env["beam_id"]
            story = env["story"]
            full_id = f"{beam_id}_{story}" if story else beam_id

            forces.append(
                BeamForces(
                    id=full_id,
                    load_case=env["case_id"],
                    mu_knm=env["mu_max"],
                    vu_kn=env["vu_max"],
                    pu_kn=env["pu_max"],
                    station_count=env["station_count"],
                )
            )

        return forces


# =============================================================================
# Manual Input Adapter
# =============================================================================


class ManualInputAdapter(InputAdapter):
    """Adapter for manual/programmatic input.

    Converts raw dictionaries to canonical models with validation.
    Useful for Streamlit UI or API input.
    """

    name = "Manual"
    supported_formats = []

    def can_handle(self, source: Path | str) -> bool:
        """Manual adapter doesn't handle files."""
        return False

    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Not applicable for manual input."""
        raise NotImplementedError("Use from_dict() for manual input")

    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Not applicable for manual input."""
        raise NotImplementedError("Use from_dict() for manual input")

    @staticmethod
    def geometry_from_dict(
        data: dict[str, Any],
        defaults: DesignDefaults | None = None,
    ) -> BeamGeometry:
        """Create BeamGeometry from dictionary.

        Args:
            data: Dictionary with geometry fields
            defaults: Default section properties

        Returns:
            Validated BeamGeometry model

        Example:
            >>> beam = ManualInputAdapter.geometry_from_dict({
            ...     "id": "B1",
            ...     "label": "B1",
            ...     "story": "Ground",
            ...     "point1": {"x": 0, "y": 0, "z": 0},
            ...     "point2": {"x": 5, "y": 0, "z": 0},
            ...     "width_mm": 300,
            ...     "depth_mm": 500,
            ... })
        """
        defaults = defaults or DesignDefaults()

        # Handle nested point data
        point1 = Point3D.model_validate(data["point1"])
        point2 = Point3D.model_validate(data["point2"])

        # Handle section properties (either nested or flat)
        if "section" in data:
            section = SectionProperties.model_validate(data["section"])
        else:
            section = SectionProperties(
                width_mm=data.get("width_mm", 300),
                depth_mm=data.get("depth_mm", 500),
                fck_mpa=data.get("fck_mpa", defaults.fck_mpa),
                fy_mpa=data.get("fy_mpa", defaults.fy_mpa),
                cover_mm=data.get("cover_mm", defaults.cover_mm),
            )

        return BeamGeometry(
            id=data["id"],
            label=data.get("label", data["id"]),
            story=data.get("story", "Ground"),
            frame_type=FrameType(data.get("frame_type", "beam")),
            point1=point1,
            point2=point2,
            section=section,
            angle=data.get("angle", 0.0),
            source_id=data.get("source_id"),
        )

    @staticmethod
    def forces_from_dict(data: dict[str, Any]) -> BeamForces:
        """Create BeamForces from dictionary.

        Args:
            data: Dictionary with force fields

        Returns:
            Validated BeamForces model
        """
        return BeamForces.model_validate(data)
