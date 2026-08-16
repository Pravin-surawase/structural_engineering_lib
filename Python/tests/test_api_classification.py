"""Executable truth checks for the Alpha API classification registry."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "generate_api_classification.py"
)
_SPEC = importlib.util.spec_from_file_location("generate_api_classification", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
classification = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = classification
_SPEC.loader.exec_module(classification)


def test_every_facade_symbol_has_exactly_one_classification() -> None:
    registry = classification.build_registry()

    for surface in registry["surfaces"]:
        names = [record["name"] for record in surface["symbols"]]
        assert len(names) == len(set(names))
        assert surface["classified_symbol_count"] == len(names)
        assert all(
            record["classification"]
            in {"stable", "preview", "compatibility", "internal"}
            for record in surface["symbols"]
        )


def test_alpha_registry_makes_no_stable_export_promise() -> None:
    registry = classification.build_registry()

    assert registry["release_channel"] == "alpha"
    assert registry["stable_exports"] == []
    for surface in registry["surfaces"]:
        assert all(
            record["classification"] != "stable" for record in surface["symbols"]
        )


def test_public_looking_callable_leakage_is_explicitly_internal() -> None:
    registry = classification.build_registry()

    for surface in registry["surfaces"]:
        for record in surface["symbols"]:
            if not record["declared_export"]:
                assert record["classification"] == "internal"
