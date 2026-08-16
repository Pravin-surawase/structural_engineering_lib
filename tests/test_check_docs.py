"""Focused regressions for the unified documentation checker."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import check_docs


def _write_frontmatter_doc(path: Path, *, status: str) -> None:
    path.write_text(
        "\n".join(
            [
                "---",
                "owner: Main Agent",
                f"status: {status}",
                "last_updated: 2026-08-16",
                "doc_type: reference",
                "---",
                "",
                "# Fixture",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_frontmatter_json_returns_nonzero_with_unchanged_invalid_report(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _write_frontmatter_doc(tmp_path / "invalid.md", status="completed")
    monkeypatch.setattr(check_docs, "DOCS_DIR", tmp_path)

    result = check_docs.check_frontmatter(json_output=True)

    report = json.loads(capsys.readouterr().out)
    assert result == 1
    assert report == {
        "total": 1,
        "with_frontmatter": 1,
        "without_frontmatter": 0,
        "invalid_frontmatter": 1,
        "skipped": 0,
        "files_without": [],
        "files_invalid": [
            {
                "file": "invalid.md",
                "errors": [
                    "Invalid status: 'completed' "
                    "(valid: ['active', 'draft', 'deprecated', 'archived'])"
                ],
            }
        ],
    }


def test_frontmatter_json_returns_zero_with_unchanged_valid_report(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _write_frontmatter_doc(tmp_path / "valid.md", status="active")
    monkeypatch.setattr(check_docs, "DOCS_DIR", tmp_path)

    result = check_docs.check_frontmatter(json_output=True)

    report = json.loads(capsys.readouterr().out)
    assert result == 0
    assert report == {
        "total": 1,
        "with_frontmatter": 1,
        "without_frontmatter": 0,
        "invalid_frontmatter": 0,
        "skipped": 0,
        "files_without": [],
        "files_invalid": [],
    }
