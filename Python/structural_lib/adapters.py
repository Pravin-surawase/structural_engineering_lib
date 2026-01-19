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
from collections.abc import Sequence
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
    "SAFEAdapter",
    "STAADAdapter",
    "GenericCSVAdapter",
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

    def __init__(self) -> None:
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
        self, headers: Sequence[str], field: str, mapping: dict[str, list[str]]
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
        headers: Sequence[str],
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
        defaults = defaults or DesignDefaults()  # type: ignore[call-arg]

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

        defaults = defaults or DesignDefaults()  # type: ignore[call-arg]
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
        defaults = defaults or DesignDefaults()  # type: ignore[call-arg]

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


# =============================================================================
# SAFE Adapter
# =============================================================================


class SAFEAdapter(InputAdapter):
    """Adapter for CSI SAFE slab strip forces CSV exports.

    SAFE exports strip forces via: Display → Show Tables → Strip Forces

    Column Mappings:
    - Strip/SpanName → beam_id (strip/band identifier)
    - LoadCombo → case_id (load combination)
    - M22/Moment22 → m3 (moment about 2 axis, kN·m)
    - V23/Shear23 → v2 (shear in 23 plane, kN)
    - Position → station (location along strip)

    Example CSV:
        Strip,SpanName,LoadCombo,Position,M22,V23
        Strip1-A,Span1,1.5DL+1.5LL,0,0,-85.2
        Strip1-A,Span1,1.5DL+1.5LL,1500,120.5,0
    """

    name = "SAFE"
    supported_formats = [".csv"]

    # Column name mappings (internal name -> possible CSV column names)
    GEOMETRY_COLUMNS: dict[str, list[str]] = {
        "story": ["Story", "Level", "Floor"],
        "beam_id": ["Strip", "SpanName", "StripName", "Label", "Name"],
        "unique_name": ["Unique Name", "UniqueName", "GUID"],
        "point1_x": ["Point1X", "X1", "Start X", "StartX"],
        "point1_y": ["Point1Y", "Y1", "Start Y", "StartY"],
        "point1_z": ["Point1Z", "Z1", "Start Z", "StartZ", "Elevation"],
        "point2_x": ["Point2X", "X2", "End X", "EndX"],
        "point2_y": ["Point2Y", "Y2", "End Y", "EndY"],
        "point2_z": ["Point2Z", "Z2", "End Z", "EndZ"],
        "width_mm": ["Width", "Width_mm", "b", "B_mm", "StripWidth"],
        "depth_mm": ["Depth", "Depth_mm", "t", "D_mm", "SlabThick", "Thickness"],
        "fck_mpa": ["fck", "Fck", "fc", "ConcreteStrength"],
        "fy_mpa": ["fy", "Fy", "SteelStrength"],
    }

    FORCES_COLUMNS: dict[str, list[str]] = {
        "story": ["Story", "Level", "Floor"],
        "beam_id": ["Strip", "SpanName", "StripName", "Label", "Name"],
        "case_id": [
            "LoadCombo",
            "Load Combo",
            "Output Case",
            "Load Case",
            "Combo",
        ],
        "station": ["Position", "Station", "Location", "Distance"],
        "m3": ["M22", "Moment22", "M", "Mu", "Moment"],
        "v2": ["V23", "Shear23", "V", "Vu", "Shear"],
        "p": ["P", "Axial", "N", "AxialForce"],
        # SAFE envelope format (pre-computed)
        "mu_max": ["Mu_max", "MuMax", "M22_max", "MaxMoment"],
        "vu_max": ["Vu_max", "VuMax", "V23_max", "MaxShear"],
    }

    def __init__(self) -> None:
        """Initialize SAFE adapter."""
        self._column_cache: dict[str, dict[str, str]] = {}

    def can_handle(self, source: Path | str) -> bool:
        """Check if source is a valid SAFE CSV.

        Args:
            source: Path to file

        Returns:
            True if file is CSV and contains SAFE-like headers
        """
        path = Path(source)
        if not path.exists() or path.suffix.lower() != ".csv":
            return False

        try:
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, [])

                # Check for SAFE-specific columns
                headers_lower = {h.lower().strip() for h in headers}
                safe_indicators = {"strip", "spanname", "m22", "v23", "loadcombo"}
                return len(headers_lower & safe_indicators) >= 2

        except (UnicodeDecodeError, csv.Error):
            return False

    def _build_column_map(
        self, headers: Sequence[str], mappings: dict[str, list[str]]
    ) -> dict[str, str]:
        """Build mapping from internal names to actual column names.

        Args:
            headers: CSV header row
            mappings: Internal name to possible column names

        Returns:
            Dictionary mapping internal names to actual column names
        """
        headers_lower = {h.lower().strip(): h for h in headers}
        result: dict[str, str] = {}

        for internal_name, possible_names in mappings.items():
            for name in possible_names:
                if name.lower() in headers_lower:
                    result[internal_name] = headers_lower[name.lower()]
                    break

        return result

    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Load strip geometry from SAFE geometry CSV.

        Note: SAFE geometry is typically less detailed than ETABS.
        For slab strips, geometry is often inferred from section properties.

        Args:
            source: Path to geometry CSV
            defaults: Default section properties

        Returns:
            List of BeamGeometry models for strips
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        defaults = defaults or DesignDefaults()  # type: ignore[call-arg]
        beams: list[BeamGeometry] = []

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.GEOMETRY_COLUMNS)

            # Check required columns
            if "beam_id" not in column_map:
                raise ValueError(
                    "Missing strip identifier column. "
                    "Expected: Strip, SpanName, or StripName"
                )

            for row in reader:
                try:
                    beam_id_col = column_map["beam_id"]
                    label = row[beam_id_col].strip()
                    story_col = column_map.get("story")
                    story = row.get(story_col, "").strip() if story_col else "Slab"
                    beam_id = f"{label}_{story}"

                    # Handle coordinates if available
                    # SAFE strips often don't have full 3D geometry
                    has_coords = all(
                        k in column_map
                        for k in ["point1_x", "point1_y", "point2_x", "point2_y"]
                    )

                    if has_coords:
                        point1 = Point3D(
                            x=float(row.get(column_map["point1_x"], 0)),
                            y=float(row.get(column_map["point1_y"], 0)),
                            z=float(row.get(column_map.get("point1_z", ""), 0) or 0),
                        )
                        point2 = Point3D(
                            x=float(row.get(column_map["point2_x"], 0)),
                            y=float(row.get(column_map["point2_y"], 0)),
                            z=float(row.get(column_map.get("point2_z", ""), 0) or 0),
                        )
                    else:
                        # Default to unit length strip if no coordinates
                        point1 = Point3D(x=0.0, y=0.0, z=0.0)
                        point2 = Point3D(x=1.0, y=0.0, z=0.0)

                    # Section properties
                    width_col = column_map.get("width_mm")
                    depth_col = column_map.get("depth_mm")
                    fck_col = column_map.get("fck_mpa")
                    fy_col = column_map.get("fy_mpa")

                    section = SectionProperties(
                        width_mm=(
                            float(row.get(width_col, 1000) or 1000)
                            if width_col
                            else 1000
                        ),  # Default strip width
                        depth_mm=(
                            float(row.get(depth_col, 200) or 200) if depth_col else 200
                        ),  # Default slab depth
                        fck_mpa=(
                            float(
                                row.get(fck_col, defaults.fck_mpa) or defaults.fck_mpa
                            )
                            if fck_col
                            else defaults.fck_mpa
                        ),
                        fy_mpa=(
                            float(row.get(fy_col, defaults.fy_mpa) or defaults.fy_mpa)
                            if fy_col
                            else defaults.fy_mpa
                        ),
                        cover_mm=defaults.cover_mm,
                    )

                    try:
                        beam = BeamGeometry(
                            id=beam_id,
                            label=label,
                            story=story,
                            frame_type=FrameType.BEAM,
                            point1=point1,
                            point2=point2,
                            section=section,
                            angle=0.0,
                            source_id=None,
                        )
                        beams.append(beam)
                    except Exception:
                        # Skip invalid strips (e.g., too short)
                        continue

                except (KeyError, ValueError):
                    continue

        return beams

    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Load strip forces from SAFE forces CSV.

        Processes force envelope - takes maximum absolute values
        across all positions for each strip/load case combination.

        Args:
            source: Path to strip forces CSV

        Returns:
            List of BeamForces models (one per strip per load case)

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        envelopes: dict[tuple[str, str, str], dict[str, Any]] = {}

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.FORCES_COLUMNS)

            # Detect format: envelope vs station data
            is_envelope = "mu_max" in column_map or "vu_max" in column_map
            is_station_data = "m3" in column_map and "v2" in column_map

            if is_envelope:
                required = ["beam_id"]
            elif is_station_data:
                required = ["beam_id", "case_id", "m3", "v2"]
            else:
                raise ValueError(
                    "Missing force columns. Expected M22/V23 or Mu_max/Vu_max. "
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

                    if is_envelope:
                        case_id = "Envelope"

                        mu_col = column_map.get("mu_max")
                        vu_col = column_map.get("vu_max")

                        mu = abs(float(row.get(mu_col, 0) or 0)) if mu_col else 0.0
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
                    continue

        # Convert to BeamForces models
        forces: list[BeamForces] = []
        for env in envelopes.values():
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


class STAADAdapter(InputAdapter):
    """Adapter for STAAD.Pro beam data imports.

    STAAD.Pro uses different column naming conventions than ETABS/SAFE:
    - Member/Beam: Member identifier
    - Node: Node number
    - Dist/Distance: Station location along member
    - Fx: Axial force
    - Fy: Shear force (major axis, corresponds to V2)
    - Fz: Shear force (minor axis)
    - Mx: Torsion
    - My: Bending moment (major axis)
    - Mz: Bending moment (minor axis, corresponds to M3 in ETABS)
    - LC/Load/Case: Load case identifier

    Note: STAAD.Pro's local axis convention may differ from ETABS.
    In STAAD, My is typically the major axis moment for beam bending
    while Mz is for minor axis. This adapter maps appropriately.

    Example:
        >>> adapter = STAADAdapter()
        >>> if adapter.can_handle("staad_forces.csv"):
        ...     forces = adapter.load_forces("staad_forces.csv")
    """

    name = "STAAD.Pro"
    supported_formats = [".csv", ".txt"]

    # Default section dimensions (mm) when not provided in CSV
    DEFAULT_WIDTH_MM = 300.0
    DEFAULT_DEPTH_MM = 500.0

    # Column mappings for geometry
    GEOMETRY_COLUMNS: dict[str, list[str]] = {
        "beam_id": ["Member", "Beam", "Element", "MemberNo", "Memb"],
        "label": ["Label", "Name", "MemberLabel"],
        "story": ["Story", "Level", "Floor", "Group"],
        "node1": ["Node1", "StartNode", "NodeI", "I"],
        "node2": ["Node2", "EndNode", "NodeJ", "J"],
        "point1_x": ["X1", "StartX", "Xi", "Ix"],
        "point1_y": ["Y1", "StartY", "Yi", "Iy"],
        "point1_z": ["Z1", "StartZ", "Zi", "Iz"],
        "point2_x": ["X2", "EndX", "Xj", "Jx"],
        "point2_y": ["Y2", "EndY", "Yj", "Jy"],
        "point2_z": ["Z2", "EndZ", "Zj", "Jz"],
        "section": ["Section", "SecName", "Profile", "Property"],
        "width_mm": ["Width", "B", "b", "Width_mm"],
        "depth_mm": ["Depth", "D", "d", "Depth_mm", "Height", "H"],
        "fck_mpa": ["fck", "Fck", "Fc", "ConcreteStrength"],
        "fy_mpa": ["fy", "Fy", "SteelStrength"],
    }

    # Column mappings for forces
    FORCES_COLUMNS: dict[str, list[str]] = {
        "beam_id": ["Member", "Beam", "Element", "MemberNo", "Memb"],
        "case_id": [
            "LC",
            "Load",
            "Case",
            "LoadCase",
            "Load Case",
            "Combo",
            "LoadCombo",
        ],
        "station": ["Dist", "Distance", "Loc", "Location", "Station", "X"],
        # STAAD uses My for major axis bending (like M3 in ETABS)
        # and Fy for major axis shear (like V2 in ETABS)
        "m3": ["My", "Mz", "Moment", "BendingMoment", "M"],
        "v2": ["Fy", "Fz", "Shear", "ShearForce", "V"],
        "p": ["Fx", "Axial", "AxialForce", "N", "P"],
        # Envelope format columns
        "mu_max": ["My_max", "Mz_max", "Moment_max", "Mu_max", "M_max"],
        "mu_min": ["My_min", "Mz_min", "Moment_min", "Mu_min", "M_min"],
        "vu_max": ["Fy_max", "Fz_max", "Shear_max", "Vu_max", "V_max"],
    }

    def can_handle(self, source: Path | str) -> bool:
        """Check if source is a STAAD.Pro export file.

        Detection strategy:
        1. Check file extension (.csv, .txt)
        2. Look for STAAD-specific column names (Member, My, Fy, etc.)
        3. Differentiate from ETABS (which uses Frame, M3, V2)

        Args:
            source: Path to input file

        Returns:
            True if this looks like a STAAD.Pro export
        """
        path = Path(source)

        # Check extension
        if path.suffix.lower() not in self.supported_formats:
            return False

        if not path.exists():
            return False

        # Check for STAAD-specific columns
        try:
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                headers_lower = [h.lower().strip() for h in headers]

                # STAAD-specific column names
                staad_markers = [
                    "member",
                    "memb",
                    "memberno",
                    "my",
                    "mz",
                    "fy",
                    "fz",
                    "fx",
                    "lc",
                    "dist",
                ]

                # ETABS-specific markers (to exclude)
                etabs_markers = ["frame", "m3", "v2", "uniquename", "story"]

                staad_count = sum(
                    1 for h in headers_lower if any(m == h for m in staad_markers)
                )
                etabs_count = sum(
                    1 for h in headers_lower if any(m == h for m in etabs_markers)
                )

                # Consider STAAD if it has STAAD markers but not ETABS markers
                return staad_count >= 2 and etabs_count < 2

        except Exception:
            return False

    def _build_column_map(
        self, headers: Sequence[str], column_spec: dict[str, list[str]]
    ) -> dict[str, str]:
        """Build mapping from internal names to actual column names.

        Args:
            headers: Column headers from CSV
            column_spec: Specification of column aliases

        Returns:
            Dict mapping internal names to actual header names
        """
        column_map = {}
        headers_lower = {h.lower(): h for h in headers}

        for internal_name, aliases in column_spec.items():
            for alias in aliases:
                if alias.lower() in headers_lower:
                    column_map[internal_name] = headers_lower[alias.lower()]
                    break

        return column_map

    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Load member geometry from STAAD.Pro geometry export.

        STAAD.Pro exports member connectivity with node coordinates.

        Args:
            source: Path to geometry CSV file
            defaults: Default material properties

        Returns:
            List of BeamGeometry models

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        if defaults is None:
            defaults = DesignDefaults()  # type: ignore[call-arg]

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        beams: list[BeamGeometry] = []

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.GEOMETRY_COLUMNS)

            # Must have beam_id at minimum
            if "beam_id" not in column_map:
                raise ValueError(
                    f"Missing beam identifier column. Expected one of: "
                    f"{self.GEOMETRY_COLUMNS['beam_id']}. "
                    f"Available: {headers}"
                )

            for row in reader:
                try:
                    beam_id = row[column_map["beam_id"]].strip()
                    if not beam_id:
                        continue

                    # Label (use beam_id if not provided)
                    label_col = column_map.get("label")
                    label = (
                        row.get(label_col, beam_id).strip() if label_col else beam_id
                    )

                    # Story/group (use "Default" if not provided - BeamGeometry requires non-empty)
                    story_col = column_map.get("story")
                    story_from_csv = row.get(story_col, "").strip() if story_col else ""
                    story = story_from_csv if story_from_csv else "Default"

                    # Coordinates
                    has_coords = all(
                        k in column_map
                        for k in ["point1_x", "point1_y", "point2_x", "point2_y"]
                    )

                    if has_coords:
                        # STAAD typically uses meters or feet - assume meters
                        point1 = Point3D(
                            x=float(row.get(column_map["point1_x"], 0) or 0),
                            y=float(row.get(column_map["point1_y"], 0) or 0),
                            z=float(row.get(column_map.get("point1_z", ""), 0) or 0),
                        )
                        point2 = Point3D(
                            x=float(row.get(column_map["point2_x"], 0) or 0),
                            y=float(row.get(column_map["point2_y"], 0) or 0),
                            z=float(row.get(column_map.get("point2_z", ""), 0) or 0),
                        )
                    else:
                        # Default placeholder coordinates
                        point1 = Point3D(x=0.0, y=0.0, z=0.0)
                        point2 = Point3D(x=1.0, y=0.0, z=0.0)

                    # Section properties - use class constants for default dimensions
                    width_col = column_map.get("width_mm")
                    depth_col = column_map.get("depth_mm")
                    fck_col = column_map.get("fck_mpa")
                    fy_col = column_map.get("fy_mpa")

                    section = SectionProperties(
                        width_mm=(
                            float(
                                row.get(width_col, self.DEFAULT_WIDTH_MM)
                                or self.DEFAULT_WIDTH_MM
                            )
                            if width_col
                            else self.DEFAULT_WIDTH_MM
                        ),
                        depth_mm=(
                            float(
                                row.get(depth_col, self.DEFAULT_DEPTH_MM)
                                or self.DEFAULT_DEPTH_MM
                            )
                            if depth_col
                            else self.DEFAULT_DEPTH_MM
                        ),
                        fck_mpa=(
                            float(
                                row.get(fck_col, defaults.fck_mpa) or defaults.fck_mpa
                            )
                            if fck_col
                            else defaults.fck_mpa
                        ),
                        fy_mpa=(
                            float(row.get(fy_col, defaults.fy_mpa) or defaults.fy_mpa)
                            if fy_col
                            else defaults.fy_mpa
                        ),
                        cover_mm=defaults.cover_mm,
                    )

                    # Build full ID (append story only if explicitly provided in CSV)
                    full_id = f"{beam_id}_{story}" if story_from_csv else beam_id

                    try:
                        beam = BeamGeometry(
                            id=full_id,
                            label=label,
                            story=story,
                            frame_type=FrameType.BEAM,
                            point1=point1,
                            point2=point2,
                            section=section,
                            angle=0.0,
                            source_id=beam_id,
                        )
                        beams.append(beam)
                    except Exception:
                        # Skip invalid members
                        continue

                except (KeyError, ValueError):
                    continue

        return beams

    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Load member forces from STAAD.Pro force export.

        Handles both:
        - Station data: Multiple rows per member with different Dist values
        - Envelope data: Pre-computed max values (My_max, Fy_max columns)

        Args:
            source: Path to forces CSV file

        Returns:
            List of BeamForces models (envelope per member/load case)

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        envelopes: dict[tuple[str, str], dict[str, Any]] = {}

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.FORCES_COLUMNS)

            # Detect format
            is_envelope = "mu_max" in column_map or "vu_max" in column_map
            is_station_data = "m3" in column_map and "v2" in column_map

            if is_envelope:
                required = ["beam_id"]
            elif is_station_data:
                required = ["beam_id", "m3", "v2"]
            else:
                raise ValueError(
                    "Missing force columns. Expected My/Fy or My_max/Fy_max. "
                    f"Available: {list(column_map.keys())}"
                )

            missing = [r for r in required if r not in column_map]
            if missing:
                raise ValueError(
                    f"Missing required columns: {missing}. " f"Available: {headers}"
                )

            for row in reader:
                try:
                    beam_id = row[column_map["beam_id"]].strip()
                    if not beam_id:
                        continue

                    # Load case (default to "Default" if not provided)
                    case_col = column_map.get("case_id")
                    case_id = (
                        row.get(case_col, "Default").strip() if case_col else "Default"
                    )
                    if not case_id:
                        case_id = "Default"

                    if is_envelope:
                        # Pre-computed envelope format
                        mu_col = column_map.get("mu_max")
                        vu_col = column_map.get("vu_max")

                        mu = abs(float(row.get(mu_col, 0) or 0)) if mu_col else 0.0
                        vu = abs(float(row.get(vu_col, 0) or 0)) if vu_col else 0.0

                        key = (beam_id, case_id)
                        envelopes[key] = {
                            "beam_id": beam_id,
                            "case_id": case_id,
                            "mu_max": mu,
                            "vu_max": vu,
                            "pu_max": 0.0,
                            "station_count": 1,
                        }
                    else:
                        # Station data - build envelope
                        m3 = abs(float(row[column_map["m3"]]))
                        v2 = abs(float(row[column_map["v2"]]))

                        p_col = column_map.get("p")
                        p = abs(float(row.get(p_col, 0) or 0)) if p_col else 0.0

                        key = (beam_id, case_id)

                        if key not in envelopes:
                            envelopes[key] = {
                                "beam_id": beam_id,
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
                    continue

        # Convert to BeamForces models
        forces: list[BeamForces] = []
        for env in envelopes.values():
            forces.append(
                BeamForces(
                    id=env["beam_id"],
                    load_case=env["case_id"],
                    mu_knm=env["mu_max"],
                    vu_kn=env["vu_max"],
                    pu_kn=env["pu_max"],
                    station_count=env["station_count"],
                )
            )

        return forces


# =============================================================================
# Generic CSV Adapter (Excel/Manual Entry)
# =============================================================================


class GenericCSVAdapter(InputAdapter):
    """Adapter for generic/manual CSV input (Excel templates, user-created files).

    Handles the simplified "Generic Format" defined in csv-import-schema.md,
    as well as Excel BeamDesignSchedule template format.

    Supports two primary use cases:
    1. Generic format: beam_id, mu_knm, vu_kn, b_mm, D_mm, etc.
    2. Excel template: BeamID, b (mm), D (mm), Mu (kN-m), Vu (kN), etc.

    Column Mappings (case-insensitive, with flexible aliases):
    - BeamID/beam_id → beam_id
    - b (mm)/b_mm/b/Width → width_mm
    - D (mm)/D_mm/D/Depth → depth_mm
    - Mu (kN-m)/mu_knm/Mu → mu_knm
    - Vu (kN)/vu_kn/Vu → vu_kn

    Example Generic CSV:
        beam_id,story,mu_knm,vu_kn,b_mm,D_mm,fck_nmm2
        B1,GF,180.5,125.0,300,500,25
        B2,GF,145.2,98.3,300,450,25

    Example Excel Template CSV:
        BeamID,b (mm),D (mm),d (mm),fck,fy,Mu (kN-m),Vu (kN),Cover (mm)
        B1,300,500,450,25,500,150,100,40
        B2,300,450,400,25,500,120,80,40
    """

    name = "Generic"
    supported_formats = [".csv", ".txt"]

    # Default dimensions for generic input
    DEFAULT_WIDTH_MM = 300.0
    DEFAULT_DEPTH_MM = 500.0

    # Column mappings for geometry/section properties
    GEOMETRY_COLUMNS: dict[str, list[str]] = {
        "beam_id": [
            "BeamID",
            "Beam ID",
            "beam_id",
            "ID",
            "Name",
            "Label",
            "Element",
        ],
        "story": ["Story", "Floor", "Level", "story"],
        "label": ["Label", "Name", "Description"],
        "span_mm": ["Span (mm)", "span_mm", "Span", "Length", "L (mm)"],
        "width_mm": [
            "b (mm)",
            "b_mm",
            "b",
            "Width",
            "Width (mm)",
            "width_mm",
            "B",
        ],
        "depth_mm": [
            "D (mm)",
            "D_mm",
            "D",
            "Depth",
            "Depth (mm)",
            "depth_mm",
            "H",
            "Height",
        ],
        "eff_depth_mm": ["d (mm)", "d_mm", "d", "Effective Depth"],
        "fck_mpa": ["fck", "fck_nmm2", "Fck", "fck (N/mm2)", "Concrete Grade"],
        "fy_mpa": ["fy", "fy_nmm2", "Fy", "fy (N/mm2)", "Steel Grade"],
        "cover_mm": ["Cover (mm)", "cover_mm", "Cover", "c"],
    }

    # Column mappings for forces
    FORCES_COLUMNS: dict[str, list[str]] = {
        "beam_id": [
            "BeamID",
            "Beam ID",
            "beam_id",
            "ID",
            "Name",
            "Label",
            "Element",
        ],
        "story": ["Story", "Floor", "Level", "story"],
        "mu_knm": [
            "Mu (kN-m)",
            "mu_knm",
            "Mu",
            "Moment",
            "Bending Moment",
            "M (kNm)",
        ],
        "vu_kn": ["Vu (kN)", "vu_kn", "Vu", "Shear", "Shear Force", "V (kN)"],
        "pu_kn": ["Pu (kN)", "pu_kn", "Pu", "Axial", "Axial Force", "P (kN)"],
        "load_case": ["Load Case", "Combo", "Case", "LoadCase", "LC"],
        # Section properties may also appear in forces file
        "width_mm": [
            "b (mm)",
            "b_mm",
            "b",
            "Width",
            "Width (mm)",
            "width_mm",
            "B",
        ],
        "depth_mm": [
            "D (mm)",
            "D_mm",
            "D",
            "Depth",
            "Depth (mm)",
            "depth_mm",
            "H",
        ],
        "fck_mpa": ["fck", "fck_nmm2", "Fck", "fck (N/mm2)"],
        "fy_mpa": ["fy", "fy_nmm2", "Fy", "fy (N/mm2)"],
        "cover_mm": ["Cover (mm)", "cover_mm", "Cover"],
    }

    def can_handle(self, source: Path | str) -> bool:
        """Check if source is a generic/Excel CSV file.

        Returns True for CSV files that have beam_id and at least one
        recognizable column (mu_knm, vu_kn, b_mm, D_mm).

        This adapter has the lowest priority - it handles files that
        don't match more specific formats (ETABS, SAFE, STAAD).
        """
        path = Path(source)

        # Basic file checks
        if not path.exists():
            return False
        if path.suffix.lower() not in self.supported_formats:
            return False

        try:
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                headers_lower = [h.lower().strip() for h in headers]

                # Build column map to check recognition
                column_map = self._build_column_map(headers, self.FORCES_COLUMNS)

                # Must have beam_id
                if "beam_id" not in column_map:
                    return False

                # Must have at least one force or geometry column
                recognized = {
                    "mu_knm",
                    "vu_kn",
                    "width_mm",
                    "depth_mm",
                    "fck_mpa",
                    "fy_mpa",
                }
                has_recognized = any(k in column_map for k in recognized)

                if not has_recognized:
                    return False

                # Exclude ETABS-specific patterns
                etabs_markers = ["m3", "v2", "uniquename", "output case"]
                has_etabs = any(m in headers_lower for m in etabs_markers)

                # Exclude STAAD-specific patterns
                staad_markers = ["my", "fy", "fx", "lc", "dist"]
                staad_count = sum(1 for m in staad_markers if m in headers_lower)

                # Accept if not clearly ETABS or STAAD
                return not has_etabs and staad_count < 3

        except Exception:
            return False

    def _build_column_map(
        self, headers: Sequence[str], column_spec: dict[str, list[str]]
    ) -> dict[str, str]:
        """Build mapping from internal names to actual column names.

        Prefers exact case matches over case-insensitive matches to handle
        situations like both 'D (mm)' and 'd (mm)' being present.
        """
        column_map = {}
        headers_set = set(headers)
        headers_lower = {h.lower(): h for h in headers}

        for internal_name, aliases in column_spec.items():
            # First pass: try exact match
            for alias in aliases:
                if alias in headers_set:
                    column_map[internal_name] = alias
                    break
            else:
                # Second pass: case-insensitive match
                for alias in aliases:
                    if alias.lower() in headers_lower:
                        column_map[internal_name] = headers_lower[alias.lower()]
                        break

        return column_map

    def load_geometry(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> list[BeamGeometry]:
        """Load beam geometry from generic CSV.

        Creates BeamGeometry models with section properties from CSV.
        Uses placeholder coordinates since generic format typically
        doesn't include 3D geometry.

        Args:
            source: Path to geometry/beam schedule CSV
            defaults: Default material properties

        Returns:
            List of BeamGeometry models
        """
        if defaults is None:
            defaults = DesignDefaults()  # type: ignore[call-arg]

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        beams: list[BeamGeometry] = []

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.GEOMETRY_COLUMNS)

            if "beam_id" not in column_map:
                raise ValueError(
                    f"Missing beam identifier column. Expected one of: "
                    f"{self.GEOMETRY_COLUMNS['beam_id']}. "
                    f"Available: {headers}"
                )

            for row in reader:
                try:
                    beam_id = row[column_map["beam_id"]].strip()
                    if not beam_id:
                        continue

                    # Label (use beam_id if not provided)
                    label_col = column_map.get("label")
                    label = (
                        row.get(label_col, beam_id).strip() if label_col else beam_id
                    )

                    # Story
                    story_col = column_map.get("story")
                    story_from_csv = row.get(story_col, "").strip() if story_col else ""
                    story = story_from_csv if story_from_csv else "Default"

                    # Span (for calculating placeholder coordinates)
                    span_col = column_map.get("span_mm")
                    span_mm = 5000.0  # Default 5m span
                    if span_col:
                        span_val = row.get(span_col, "")
                        if span_val and str(span_val).strip():
                            try:
                                span_mm = float(span_val)
                            except ValueError:
                                pass

                    # Placeholder coordinates based on span
                    point1 = Point3D(x=0.0, y=0.0, z=0.0)
                    point2 = Point3D(x=span_mm / 1000.0, y=0.0, z=0.0)  # Convert to m

                    # Section properties
                    width_col = column_map.get("width_mm")
                    depth_col = column_map.get("depth_mm")
                    fck_col = column_map.get("fck_mpa")
                    fy_col = column_map.get("fy_mpa")
                    cover_col = column_map.get("cover_mm")

                    section = SectionProperties(
                        width_mm=(
                            float(
                                row.get(width_col, self.DEFAULT_WIDTH_MM)
                                or self.DEFAULT_WIDTH_MM
                            )
                            if width_col
                            else self.DEFAULT_WIDTH_MM
                        ),
                        depth_mm=(
                            float(
                                row.get(depth_col, self.DEFAULT_DEPTH_MM)
                                or self.DEFAULT_DEPTH_MM
                            )
                            if depth_col
                            else self.DEFAULT_DEPTH_MM
                        ),
                        fck_mpa=(
                            float(
                                row.get(fck_col, defaults.fck_mpa) or defaults.fck_mpa
                            )
                            if fck_col
                            else defaults.fck_mpa
                        ),
                        fy_mpa=(
                            float(row.get(fy_col, defaults.fy_mpa) or defaults.fy_mpa)
                            if fy_col
                            else defaults.fy_mpa
                        ),
                        cover_mm=(
                            float(
                                row.get(cover_col, defaults.cover_mm)
                                or defaults.cover_mm
                            )
                            if cover_col
                            else defaults.cover_mm
                        ),
                    )

                    # Build full ID
                    full_id = f"{beam_id}_{story}" if story_from_csv else beam_id

                    try:
                        beam = BeamGeometry(
                            id=full_id,
                            label=label,
                            story=story,
                            frame_type=FrameType.BEAM,
                            point1=point1,
                            point2=point2,
                            section=section,
                            angle=0.0,
                            source_id=beam_id,
                        )
                        beams.append(beam)
                    except Exception:
                        # Skip invalid members
                        continue

                except (KeyError, ValueError):
                    continue

        return beams

    def load_forces(
        self,
        source: Path | str,
    ) -> list[BeamForces]:
        """Load beam forces from generic/Excel CSV.

        Generic format typically has one row per beam with design forces.
        No envelope processing needed.

        Args:
            source: Path to forces/beam schedule CSV

        Returns:
            List of BeamForces models

        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        forces: list[BeamForces] = []

        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            column_map = self._build_column_map(headers, self.FORCES_COLUMNS)

            if "beam_id" not in column_map:
                raise ValueError(
                    f"Missing beam identifier column. Expected one of: "
                    f"{self.FORCES_COLUMNS['beam_id']}. "
                    f"Available: {headers}"
                )

            # Need at least mu or vu
            has_forces = "mu_knm" in column_map or "vu_kn" in column_map
            if not has_forces:
                raise ValueError(
                    "Missing force columns. Expected Mu (kN-m) or Vu (kN). "
                    f"Available: {headers}"
                )

            for row in reader:
                try:
                    beam_id = row[column_map["beam_id"]].strip()
                    if not beam_id:
                        continue

                    # Story for unique ID
                    story_col = column_map.get("story")
                    story = row.get(story_col, "").strip() if story_col else ""

                    # Load case
                    lc_col = column_map.get("load_case")
                    load_case = (
                        row.get(lc_col, "Design").strip() if lc_col else "Design"
                    )
                    if not load_case:
                        load_case = "Design"

                    # Forces
                    mu_col = column_map.get("mu_knm")
                    vu_col = column_map.get("vu_kn")
                    pu_col = column_map.get("pu_kn")

                    mu = 0.0
                    vu = 0.0
                    pu = 0.0

                    if mu_col:
                        mu_val = row.get(mu_col, "0")
                        if mu_val and str(mu_val).strip():
                            try:
                                mu = abs(float(mu_val))
                            except ValueError:
                                pass

                    if vu_col:
                        vu_val = row.get(vu_col, "0")
                        if vu_val and str(vu_val).strip():
                            try:
                                vu = abs(float(vu_val))
                            except ValueError:
                                pass

                    if pu_col:
                        pu_val = row.get(pu_col, "0")
                        if pu_val and str(pu_val).strip():
                            try:
                                pu = abs(float(pu_val))
                            except ValueError:
                                pass

                    # Build unique ID
                    full_id = f"{beam_id}_{story}" if story else beam_id

                    force = BeamForces(
                        id=full_id,
                        load_case=load_case,
                        mu_knm=mu,
                        vu_kn=vu,
                        pu_kn=pu,
                        station_count=1,  # Single row = 1 station
                    )
                    forces.append(force)

                except (KeyError, ValueError):
                    continue

        return forces

    def load_combined(
        self,
        source: Path | str,
        defaults: DesignDefaults | None = None,
    ) -> tuple[list[BeamGeometry], list[BeamForces]]:
        """Load both geometry and forces from a combined CSV.

        Many Excel templates have both section properties and forces
        in the same file. This method loads both in one pass.

        Args:
            source: Path to combined beam schedule CSV
            defaults: Default material properties

        Returns:
            Tuple of (geometry list, forces list)
        """
        geometry = self.load_geometry(source, defaults)
        forces = self.load_forces(source)
        return geometry, forces
