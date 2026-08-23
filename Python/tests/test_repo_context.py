"""Contracts for the small canonical context manifest and live summaries."""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
from pathlib import Path

import pytest

repo_context = importlib.import_module("scripts.repo_context")


def _fixture(tmp_path: Path) -> tuple[dict, dict]:
    for path in (
        "authority.json",
        "docs/index.md",
        "docs/api-reference/index.md",
        "docs/live-policy-index.json",
        "src/README.md",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n" if target.suffix == ".json" else "# File\n")
    manifest = {
        "schema_version": 1,
        "description": "fixture",
        "summary_policy": {
            "source": "live-worktree-files",
            "default_file_limit": 5,
            "generated_folder_indexes": "retired",
        },
        "authorities": {
            "fixture": {"path": "authority.json", "description": "fixture authority"}
        },
        "retained_indexes": {
            "docs/index.md": {
                "kind": "site-entry",
                "owner": "docs",
                "reason": "home",
            },
            "docs/api-reference/index.md": {
                "kind": "site-entry",
                "owner": "api",
                "reason": "API home",
            },
            "docs/live-policy-index.json": {
                "kind": "specialized-manifest",
                "owner": "policy",
                "reason": "not a folder inventory",
            },
        },
        "areas": {
            "source": {
                "description": "source files",
                "roots": ["src"],
                "read_first": ["src/README.md"],
                "operations": ["run tests"],
            }
        },
    }
    registry = {
        "operations": {
            "run tests": {
                "status": "active",
                "command": {"display": "test", "steps": []},
            }
        }
    }
    return manifest, registry


def test_live_context_manifest_is_valid_and_folder_indexes_are_retired() -> None:
    manifest = repo_context.load_manifest()

    assert len(manifest["areas"]) == 10
    assert manifest["summary_policy"]["generated_folder_indexes"] == "retired"
    assert set(manifest["retained_indexes"]) == {
        "docs/api-reference/index.md",
        "docs/git-automation/live-git-guidance-index.json",
        "docs/index.md",
    }


def test_manifest_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text('{"schema_version": 1, "schema_version": 1}\n')

    with pytest.raises(repo_context.ContextManifestError, match="duplicate JSON key"):
        repo_context._read_manifest(path)


def test_manifest_rejects_unknown_operation_and_repository_escape(
    tmp_path: Path,
) -> None:
    manifest, registry = _fixture(tmp_path)
    manifest["areas"]["source"]["operations"] = ["unknown"]

    with pytest.raises(repo_context.ContextManifestError, match="is not active"):
        repo_context.validate_manifest(
            manifest,
            root=tmp_path,
            tracked_paths={"docs/index.md", "docs/api-reference/index.md"},
            registry=registry,
        )

    manifest, registry = _fixture(tmp_path)
    manifest["areas"]["source"]["roots"] = ["../outside"]
    with pytest.raises(
        repo_context.ContextManifestError, match="inside the repository"
    ):
        repo_context.validate_manifest(
            manifest,
            root=tmp_path,
            tracked_paths={"docs/index.md", "docs/api-reference/index.md"},
            registry=registry,
        )


def test_manifest_rejects_unexpected_generic_index(tmp_path: Path) -> None:
    manifest, registry = _fixture(tmp_path)
    unexpected = tmp_path / "src" / "index.json"
    unexpected.write_text("{}\n")

    with pytest.raises(
        repo_context.ContextManifestError, match="generic generated indexes are retired"
    ):
        repo_context.validate_manifest(
            manifest,
            root=tmp_path,
            tracked_paths={
                "docs/index.md",
                "docs/api-reference/index.md",
                "src/index.json",
            },
            registry=registry,
        )


def test_manifest_rejects_an_untracked_regenerated_index(tmp_path: Path) -> None:
    manifest, registry = _fixture(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    (tmp_path / "src" / "index.md").write_text("# Stale projection\n")

    with pytest.raises(
        repo_context.ContextManifestError, match="generic generated indexes are retired"
    ):
        repo_context.validate_manifest(
            manifest,
            root=tmp_path,
            registry=registry,
        )


def test_manifest_shape_is_strict(tmp_path: Path) -> None:
    manifest, registry = _fixture(tmp_path)
    invalid = copy.deepcopy(manifest)
    invalid["areas"]["source"]["extra"] = True

    with pytest.raises(repo_context.ContextManifestError, match="unknown fields"):
        repo_context.validate_manifest(
            invalid,
            root=tmp_path,
            tracked_paths={"docs/index.md", "docs/api-reference/index.md"},
            registry=registry,
        )


def test_live_summary_is_bounded_and_contains_no_timestamp(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "a.py").write_text("VALUE = 1\n")
    (source / "b.md").write_text("# B\n")
    nested = source / "nested"
    nested.mkdir()
    (nested / "c.py").write_text("VALUE = 2\n")

    summaries = repo_context.summarize_roots(["src"], repository_root=tmp_path, limit=2)

    assert summaries == [
        {
            "root": "src",
            "file_count": 3,
            "extensions": {".md": 1, ".py": 2},
            "top_level": {".": 2, "nested": 1},
            "files": ["src/a.py", "src/b.md"],
            "truncated": True,
        }
    ]
    assert "generated" not in json.dumps(summaries)


def test_retired_generator_bridges_are_absent_and_context_stays_canonical() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    for name in (
        "generate_all_indexes.sh",
        "generate_docs_index.py",
        "generate_enhanced_index.py",
    ):
        assert not (repository_root / "scripts" / name).exists()
        assert (repository_root / "scripts" / "_archive" / name).exists()

    result = subprocess.run(
        [str(repository_root / "run.sh"), "context", "validate"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS context manifest" in result.stdout
