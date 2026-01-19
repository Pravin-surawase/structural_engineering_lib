# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""JSON serialization utilities for canonical data models.

This module provides functions for:
- Saving/loading canonical models to/from JSON files
- Batch serialization for caching processed data
- JSON Schema generation for documentation

The serialization layer enables:
- Caching validated data to avoid re-parsing CSVs
- Sharing data between sessions
- Generating API schemas for AI agents

Example:
    >>> from structural_lib.serialization import save_geometry, load_geometry
    >>>
    >>> # Save to cache
    >>> save_geometry(beams, "cache/beams.json")
    >>>
    >>> # Load from cache (much faster than CSV parsing)
    >>> beams = load_geometry("cache/beams.json")

Author: Session 40 Agent
Task: TASK-DATA-001
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
)

__all__ = [
    "save_geometry",
    "load_geometry",
    "save_forces",
    "load_forces",
    "save_batch_input",
    "load_batch_input",
    "save_batch_result",
    "load_batch_result",
    "generate_schema",
    "generate_all_schemas",
]


# Type variable for generic save/load
T = TypeVar("T", bound=BaseModel)


# =============================================================================
# File Metadata
# =============================================================================


def _create_metadata(model_type: str, count: int) -> dict:
    """Create metadata for JSON file.

    Args:
        model_type: Type of model being saved
        count: Number of items

    Returns:
        Metadata dictionary
    """
    return {
        "version": "1.0",
        "model_type": model_type,
        "count": count,
        "created_at": datetime.now().isoformat(),
        "library": "structural_lib",
    }


def _validate_metadata(
    data: dict,
    expected_type: str,
    filepath: Path,
) -> None:
    """Validate metadata from loaded JSON.

    Args:
        data: Loaded JSON data
        expected_type: Expected model type
        filepath: File path (for error message)

    Raises:
        ValueError: If metadata is invalid or wrong type
    """
    metadata = data.get("metadata", {})

    if metadata.get("model_type") != expected_type:
        raise ValueError(
            f"Expected {expected_type} but got {metadata.get('model_type')} "
            f"in {filepath}"
        )


# =============================================================================
# Geometry Serialization
# =============================================================================


def save_geometry(
    beams: list[BeamGeometry],
    filepath: Path | str,
    *,
    pretty: bool = True,
) -> None:
    """Save beam geometry to JSON file.

    Args:
        beams: List of BeamGeometry models
        filepath: Output file path
        pretty: Use indented JSON (default True)
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Exclude computed fields to avoid rejection on load (extra="forbid")
    # Use dict format for nested exclusions
    exclude_fields = {
        "length_m": True,
        "is_vertical": True,
        "section": {"effective_depth_mm"},
    }
    data = {
        "metadata": _create_metadata("BeamGeometry", len(beams)),
        "beams": [b.model_dump(mode="json", exclude=exclude_fields) for b in beams],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None)


def load_geometry(filepath: Path | str) -> list[BeamGeometry]:
    """Load beam geometry from JSON file.

    Args:
        filepath: Input file path

    Returns:
        List of validated BeamGeometry models

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong model type
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _validate_metadata(data, "BeamGeometry", path)

    return [BeamGeometry.model_validate(b) for b in data["beams"]]


# =============================================================================
# Forces Serialization
# =============================================================================


def save_forces(
    forces: list[BeamForces],
    filepath: Path | str,
    *,
    pretty: bool = True,
) -> None:
    """Save beam forces to JSON file.

    Args:
        forces: List of BeamForces models
        filepath: Output file path
        pretty: Use indented JSON (default True)
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "metadata": _create_metadata("BeamForces", len(forces)),
        "forces": [f.model_dump(mode="json") for f in forces],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None)


def load_forces(filepath: Path | str) -> list[BeamForces]:
    """Load beam forces from JSON file.

    Args:
        filepath: Input file path

    Returns:
        List of validated BeamForces models

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong model type
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _validate_metadata(data, "BeamForces", path)

    return [BeamForces.model_validate(f) for f in data["forces"]]


# =============================================================================
# Batch Input/Result Serialization
# =============================================================================


def save_batch_input(
    batch: BeamBatchInput,
    filepath: Path | str,
    *,
    pretty: bool = True,
) -> None:
    """Save batch input to JSON file.

    Args:
        batch: BeamBatchInput model
        filepath: Output file path
        pretty: Use indented JSON (default True)
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Manually build beams list to exclude computed fields
    exclude_fields = {
        "length_m": True,
        "is_vertical": True,
        "section": {"effective_depth_mm"},
    }
    beams_data = [
        b.model_dump(mode="json", exclude=exclude_fields) for b in batch.beams
    ]

    forces_data = [f.model_dump(mode="json") for f in batch.forces]
    defaults_data = batch.defaults.model_dump(mode="json") if batch.defaults else None

    data = {
        "metadata": _create_metadata("BeamBatchInput", len(batch.beams)),
        "batch": {
            "beams": beams_data,
            "forces": forces_data,
            "defaults": defaults_data,
            "metadata": batch.metadata,
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None)


def load_batch_input(filepath: Path | str) -> BeamBatchInput:
    """Load batch input from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Validated BeamBatchInput model

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong model type
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _validate_metadata(data, "BeamBatchInput", path)

    return BeamBatchInput.model_validate(data["batch"])


def save_batch_result(
    result: BeamBatchResult,
    filepath: Path | str,
    *,
    pretty: bool = True,
) -> None:
    """Save batch result to JSON file.

    Args:
        result: BeamBatchResult model
        filepath: Output file path
        pretty: Use indented JSON (default True)
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Exclude computed fields (pass_rate, and is_acceptable in each result)
    results_data = [
        r.model_dump(mode="json", exclude={"is_acceptable"}) for r in result.results
    ]
    data = {
        "metadata": _create_metadata("BeamBatchResult", result.total_beams),
        "result": {
            "results": results_data,
            "total_beams": result.total_beams,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "metadata": result.metadata,
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None)


def load_batch_result(filepath: Path | str) -> BeamBatchResult:
    """Load batch result from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Validated BeamBatchResult model

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong model type
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _validate_metadata(data, "BeamBatchResult", path)

    return BeamBatchResult.model_validate(data["result"])


# =============================================================================
# JSON Schema Generation
# =============================================================================


def generate_schema(model_class: type[BaseModel]) -> dict:
    """Generate JSON Schema for a model class.

    Args:
        model_class: Pydantic model class

    Returns:
        JSON Schema dictionary
    """
    return model_class.model_json_schema()


def generate_all_schemas(output_dir: Path | str) -> dict[str, Path]:
    """Generate JSON Schemas for all canonical models.

    Args:
        output_dir: Directory to save schema files

    Returns:
        Dictionary mapping model names to output file paths
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    models = [
        BeamGeometry,
        BeamForces,
        BeamDesignResult,
        DesignDefaults,
        BeamBatchInput,
        BeamBatchResult,
    ]

    output_files = {}

    for model_class in models:
        schema = generate_schema(model_class)
        schema_file = path / f"{model_class.__name__}.schema.json"

        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

        output_files[model_class.__name__] = schema_file

    return output_files


# =============================================================================
# Convenience Functions
# =============================================================================


def cache_exists(filepath: Path | str) -> bool:
    """Check if a cache file exists.

    Args:
        filepath: Cache file path

    Returns:
        True if file exists
    """
    return Path(filepath).exists()


def get_cache_metadata(filepath: Path | str) -> dict | None:
    """Get metadata from a cache file without loading all data.

    Args:
        filepath: Cache file path

    Returns:
        Metadata dictionary or None if file doesn't exist
    """
    path = Path(filepath)
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data.get("metadata")
