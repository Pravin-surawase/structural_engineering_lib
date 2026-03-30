"""
Tests for IS 456:2000 clauses.json schema and content coverage.

Validates that clauses.json:
- Loads correctly and has valid structure
- Contains required fields for every clause
- Uses valid categories
- Covers key clauses for columns, footings, walls, seismic (IS 13920), and Annex D
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

CLAUSES_PATH = (
    Path(__file__).parent.parent.parent
    / "structural_lib"
    / "codes"
    / "is456"
    / "clauses.json"
)

VALID_CATEGORIES = {
    "materials",
    "flexure",
    "shear",
    "columns",
    "footings",
    "slabs",
    "walls",
    "seismic",
    "general",
    "detailing",
    "serviceability",
    "durability",
    "analysis",
    "design_limits",
    "torsion",
}

REQUIRED_FIELDS = {"title", "section", "text", "category", "keywords"}


@pytest.fixture(scope="module")
def clauses_data():
    """Load clauses.json once for all tests in this module."""
    with open(CLAUSES_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def clauses(clauses_data):
    """Return the clauses dict."""
    return clauses_data["clauses"]


# --- Schema & structure tests ---


def test_clauses_json_loads(clauses_data):
    """clauses.json loads without error and has top-level keys."""
    assert "metadata" in clauses_data
    assert "clauses" in clauses_data
    assert isinstance(clauses_data["clauses"], dict)
    assert len(clauses_data["clauses"]) > 0


def test_clauses_metadata_count_matches(clauses_data):
    """metadata.total_clauses matches actual len(clauses)."""
    expected = clauses_data["metadata"]["total_clauses"]
    actual = len(clauses_data["clauses"])
    assert (
        actual == expected
    ), f"metadata.total_clauses={expected} but actual clause count={actual}"


def test_clauses_required_fields(clauses):
    """Every clause has: title, section, text, category, keywords."""
    missing = {}
    for clause_id, clause in clauses.items():
        absent = REQUIRED_FIELDS - set(clause.keys())
        if absent:
            missing[clause_id] = absent
    assert not missing, f"Clauses missing required fields: {missing}"


def test_clauses_categories_valid(clauses):
    """Every clause category is one of the valid categories."""
    invalid = {}
    for clause_id, clause in clauses.items():
        cat = clause.get("category")
        if cat not in VALID_CATEGORIES:
            invalid[clause_id] = cat
    assert not invalid, f"Clauses with invalid category: {invalid}"


# --- Coverage tests: columns ---


COLUMN_CLAUSES = [
    "39.1",
    "39.3",
    "39.4",
    "39.5",
    "39.6",
    "39.7",
    "25.1",
    "25.2",
    "25.3",
    "25.4",
    "26.5.3.1",
]


@pytest.mark.parametrize("clause_id", COLUMN_CLAUSES)
def test_clauses_column_coverage(clauses, clause_id):
    """Key column clause exists in clauses.json."""
    assert clause_id in clauses, f"Missing column clause: {clause_id}"


# --- Coverage tests: footings ---


FOOTING_CLAUSES = ["34.1", "34.2", "34.2.3", "34.2.4", "34.3", "34.4", "31.6"]


@pytest.mark.parametrize("clause_id", FOOTING_CLAUSES)
def test_clauses_footing_coverage(clauses, clause_id):
    """Key footing clause exists in clauses.json."""
    assert clause_id in clauses, f"Missing footing clause: {clause_id}"


# --- Coverage tests: IS 13920 seismic ---


IS13920_CLAUSES = [
    "IS13920_5.1",
    "IS13920_7.1",
    "IS13920_7.2",
    "IS13920_7.3",
    "IS13920_7.4",
    "IS13920_8.1",
]


@pytest.mark.parametrize("clause_id", IS13920_CLAUSES)
def test_clauses_is13920_coverage(clauses, clause_id):
    """IS 13920 clause exists in clauses.json."""
    assert clause_id in clauses, f"Missing IS 13920 clause: {clause_id}"


# --- Coverage tests: Annex D (two-way slabs) ---


ANNEX_D_CLAUSES = ["AnnexD-1", "AnnexD-1.1", "AnnexD-2"]


@pytest.mark.parametrize("clause_id", ANNEX_D_CLAUSES)
def test_clauses_annex_d_coverage(clauses, clause_id):
    """Annex D clause exists in clauses.json."""
    assert clause_id in clauses, f"Missing Annex D clause: {clause_id}"


# --- Coverage tests: walls ---


WALL_CLAUSES = ["32.1", "32.2", "32.3", "32.4", "32.5"]


@pytest.mark.parametrize("clause_id", WALL_CLAUSES)
def test_clauses_walls_section(clauses, clause_id):
    """Wall clause exists in clauses.json."""
    assert clause_id in clauses, f"Missing wall clause: {clause_id}"
