"""Regression tests for deterministic docs-index file output."""

from __future__ import annotations

import json
import sys

import pytest

from scripts import generate_docs_index

pytestmark = pytest.mark.repo_only


def test_write_ends_with_newline_and_remains_valid_json(tmp_path, monkeypatch) -> None:
    output = tmp_path / "docs-index.json"
    index = {
        "version": "1.0.0",
        "generated": "frozen",
        "total_docs": 1,
        "docs": {"example.md": {"type": "reference"}},
        "navigation": {},
    }
    monkeypatch.setattr(generate_docs_index, "OUTPUT_FILE", output)
    monkeypatch.setattr(generate_docs_index, "scan_docs", lambda: index)
    monkeypatch.setattr(sys, "argv", ["generate_docs_index.py", "--write"])

    assert generate_docs_index.main() == 0
    raw = output.read_bytes()
    assert raw.endswith(b"\n")
    assert json.loads(raw) == index
