# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Runtime package-version identity without source/installation ambiguity."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, distributions, version
from pathlib import Path
from typing import Any

__all__ = [
    "RUNTIME_VERSION_IDENTITY_SCHEMA_VERSION",
    "RuntimeVersionIdentityV1",
    "get_runtime_version",
    "get_runtime_version_identity",
]


RUNTIME_VERSION_IDENTITY_SCHEMA_VERSION = "runtime-version-identity/v1"
_DISTRIBUTION_NAME = "structural-lib-is456"


@dataclass(frozen=True)
class RuntimeVersionIdentityV1:
    """Identity of the code imported by the current interpreter.

    A source checkout and an installed wheel are deliberately different modes.
    In source mode the adjacent ``Python/pyproject.toml`` is authoritative and
    installed metadata is reported only as a comparison. In installed mode the
    metadata is authoritative when the distribution owns the imported file.
    """

    execution_mode: str
    package_version: str
    package_origin: str
    source_version: str | None
    distribution_version: str | None
    metadata_matches_runtime: bool
    schema_version: str = RUNTIME_VERSION_IDENTITY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_mode": self.execution_mode,
            "package_version": self.package_version,
            "package_origin": self.package_origin,
            "source_version": self.source_version,
            "distribution_version": self.distribution_version,
            "metadata_matches_runtime": self.metadata_matches_runtime,
        }


def _source_version(package_origin: Path) -> str | None:
    """Return the adjacent checkout version, if this import is from source."""

    package_root = package_origin.parent
    candidates = (
        package_root / "pyproject.toml",
        package_root.parent / "pyproject.toml",
        package_root.parent.parent / "pyproject.toml",
    )
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            project = tomllib.loads(candidate.read_text(encoding="utf-8")).get(
                "project", {}
            )
        except (OSError, tomllib.TOMLDecodeError):
            continue
        if project.get("name") != _DISTRIBUTION_NAME:
            continue
        project_version = project.get("version")
        if isinstance(project_version, str) and project_version:
            return project_version
    return None


def _installed_version(origin: Path) -> str | None:
    """Match recorded package ownership to the file selected by the importer."""
    matching_versions = {
        distribution.version
        for distribution in distributions(name=_DISTRIBUTION_NAME)
        if any(
            entry.name == "__init__.py"
            and entry.parent.name == "structural_lib"
            and Path(str(distribution.locate_file(entry))).resolve() == origin
            for entry in distribution.files or ()
        )
    }
    if len(matching_versions) != 1:
        return None
    return matching_versions.pop()


def _resolve_identity(origin: Path) -> RuntimeVersionIdentityV1:
    source_version = _source_version(origin)
    if source_version is not None:
        try:
            distribution_version = version(_DISTRIBUTION_NAME)
        except PackageNotFoundError:
            distribution_version = None
        execution_mode = "SOURCE_CHECKOUT"
        package_version = source_version
        metadata_matches = (
            distribution_version is None or distribution_version == source_version
        )
    else:
        distribution_version = _installed_version(origin)
        if distribution_version is not None:
            execution_mode = "INSTALLED_DISTRIBUTION"
            package_version = distribution_version
            metadata_matches = True
        else:
            execution_mode = "UNINSTALLED_SOURCE"
            package_version = "0.0.0-dev"
            metadata_matches = False

    return RuntimeVersionIdentityV1(
        execution_mode=execution_mode,
        package_version=package_version,
        package_origin=str(origin),
        source_version=source_version,
        distribution_version=distribution_version,
        metadata_matches_runtime=metadata_matches,
    )


@lru_cache(maxsize=1)
def _imported_package_identity() -> RuntimeVersionIdentityV1:
    origin = Path(__file__).resolve().parents[1] / "__init__.py"
    return _resolve_identity(origin.resolve())


def get_runtime_version_identity(
    package_origin: str | Path | None = None,
) -> RuntimeVersionIdentityV1:
    """Return the version identity for this import or inspect an explicit origin.

    The active package identity is fixed at import for the process lifetime.
    Explicit origin probes inspect the current checkout and metadata.
    """
    if not package_origin:
        return _imported_package_identity()
    return _resolve_identity(Path(package_origin).resolve())


def get_runtime_version(package_origin: str | Path | None = None) -> str:
    """Return the version authoritative for the imported code."""

    return get_runtime_version_identity(package_origin).package_version
