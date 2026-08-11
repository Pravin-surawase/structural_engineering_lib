"""Regression coverage for candidate-version documentation semantics."""

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

bump_version = importlib.import_module("scripts.bump_version")


def _write_candidate_bump_fixture(root: Path) -> tuple[Path, Path, Path]:
    pyproject = root / "Python" / "pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text('[project]\nversion = "0.23.0a1"\n', encoding="utf-8")

    tasks = root / "docs" / "TASKS.md"
    tasks.parent.mkdir()
    tasks.write_text(
        "| **Current** | v0.23.0 | ✅ ALPHA RELEASED — public artifact evidence |\n",
        encoding="utf-8",
    )
    brief = root / "docs" / "planning" / "next-session-brief.md"
    brief.parent.mkdir()
    brief.write_text(
        "| **Current** | v0.23.0 | ✅ ALPHA RELEASED — public artifact evidence |\n",
        encoding="utf-8",
    )
    readme = root / "Python" / "README.md"
    readme.write_text(
        "**Version:** 0.23.0a1 (Alpha development preview)\n"
        "## New in v0.23.0a1\n"
        "pip install structural-lib-is456==0.23.0a1\n"
        'pip install "structural-lib-is456[dxf]===0.23.0a1"\n',
        encoding="utf-8",
    )
    return tasks, brief, readme


def test_candidate_bump_preserves_published_release_evidence(
    tmp_path: Path, monkeypatch
):
    """Candidate metadata changes must not relabel published-release history."""
    tasks, brief, readme = _write_candidate_bump_fixture(tmp_path)
    monkeypatch.setattr(bump_version, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "0.23.1a1"])

    assert bump_version.main() == 0
    assert 'version = "0.23.1a1"' in (tmp_path / "Python" / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    for path in (tasks, brief):
        content = path.read_text(encoding="utf-8")
        assert "v0.23.0 | ✅ ALPHA RELEASED" in content
        assert "v0.23.1a1" not in content
    readme_content = readme.read_text(encoding="utf-8")
    assert "**Version:** 0.23.1a1" in readme_content
    assert "## New in v0.23.1a1" in readme_content
    assert "structural-lib-is456===0.23.1a1" in readme_content
    assert "structural-lib-is456[dxf]===0.23.1a1" in readme_content

    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--check-docs"])
    assert bump_version.main() == 0
