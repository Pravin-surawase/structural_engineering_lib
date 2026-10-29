"""Regression coverage for candidate-version documentation semantics."""

import importlib
import sys
from pathlib import Path

import pytest

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
        'pip install "structural-lib-is456[dxf]==0.23.0a1"\n',
        encoding="utf-8",
    )
    return tasks, brief, readme


def _write_public_candidate_fixture(root: Path) -> tuple[Path, Path]:
    pyproject = root / "Python" / "pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text('[project]\nversion = "0.24.0a1"\n', encoding="utf-8")

    readme = root / "README.md"
    readme.write_text(
        "[Alpha](https://example.invalid/releases/tag/v0.23.1a2)\n"
        "> **v0.24.0a1 is an Alpha development preview.\n"
        'pip install "structural-lib-is456==0.24.0a1"\n'
        "`0.23.1a2` remains the current public Alpha.\n",
        encoding="utf-8",
    )
    checklist = root / "docs" / "planning" / "pre-release-checklist.md"
    checklist.parent.mkdir(parents=True)
    checklist.write_text(
        "Current source metadata: 0.24.0a1 (prepared candidate; unpublished)\n"
        "Current public Alpha: v0.23.1a2\n",
        encoding="utf-8",
    )
    return readme, checklist


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
    assert "structural-lib-is456==0.23.1a1" in readme_content
    assert "structural-lib-is456[dxf]==0.23.1a1" in readme_content

    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--check-docs"])
    assert bump_version.main() == 0


def test_candidate_bump_resets_published_citation_state(
    tmp_path: Path, monkeypatch
) -> None:
    pyproject = tmp_path / "Python" / "pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text('[project]\nversion = "0.24.0a1"\n', encoding="utf-8")
    citation = tmp_path / "CITATION.cff"
    citation.write_text(
        "cff-version: 1.2.0\n"
        "version: 0.24.0a1\n"
        "date-released: 2026-08-24\n"
        'message: "Alpha v0.24.0a1 is owner-authorized for publication."\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(bump_version, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "0.24.0a2"])

    assert bump_version.main() == 0

    content = citation.read_text(encoding="utf-8")
    assert "version: 0.24.0a2" in content
    assert "date-released:" not in content
    assert "Prepared Alpha candidate v0.24.0a2; not tagged or published" in content
    assert "owner-authorized" not in content


def test_alpha_candidate_can_promote_to_normal_software_release(
    tmp_path: Path, monkeypatch
) -> None:
    pyproject = tmp_path / "Python" / "pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text(
        '[project]\nversion = "0.24.0a1"\nclassifiers = [\n'
        '  "Development Status :: 3 - Alpha",\n]\n',
        encoding="utf-8",
    )
    python_readme = tmp_path / "Python" / "README.md"
    python_readme.write_text(
        "**Version:** 0.24.0a1 (Alpha development preview)\n" "## New in v0.24.0a1\n",
        encoding="utf-8",
    )
    root_readme = tmp_path / "README.md"
    root_readme.write_text(
        "> **v0.24.0a1 is an Alpha development preview.** Support is bounded.\n",
        encoding="utf-8",
    )
    citation = tmp_path / "CITATION.cff"
    citation.write_text(
        "version: 0.24.0a1\n"
        "date-released: 2026-08-24\n"
        'message: "Alpha v0.24.0a1 is published."\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(bump_version, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "0.24.0"])

    assert bump_version.main() == 0

    assert 'version = "0.24.0"' in pyproject.read_text(encoding="utf-8")
    assert "Development Status :: 4 - Beta" in pyproject.read_text(encoding="utf-8")
    assert (
        "v0.24.0 is a normal software release of the audited supported scope"
        in root_readme.read_text(encoding="utf-8")
    )
    assert (
        "Version:** 0.24.0 (normal/final version format; publication state is in the release ledger)"
        in python_readme.read_text(encoding="utf-8")
    )
    citation_text = citation.read_text(encoding="utf-8")
    assert "Prepared normal software release candidate v0.24.0" in citation_text
    assert "date-released:" not in citation_text


def test_doc_sync_preserves_public_release_identity(tmp_path: Path, monkeypatch):
    """A prepared source version must not relabel the last public release."""
    readme, checklist = _write_public_candidate_fixture(tmp_path)
    monkeypatch.setattr(bump_version, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--sync-docs"])

    assert bump_version.main() == 0
    readme_content = readme.read_text(encoding="utf-8")
    assert "releases/tag/v0.23.1a2" in readme_content
    assert "v0.24.0a1 is an Alpha development preview" in readme_content
    assert "current public Alpha" in readme_content
    assert "0.23.1a2" in readme_content
    assert "Current source metadata: 0.24.0a1" in checklist.read_text(encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--check-docs"])
    assert bump_version.main() == 0


@pytest.mark.parametrize(
    "guide",
    [
        "docs/getting-started/python-quickstart.md",
        "docs/getting-started/beginners-guide.md",
        "docs/getting-started/colab-workflow.md",
        "Python/examples/README.md",
        "Python/examples/colab_workflow.py",
        "docs/cookbook/cli-reference.md",
    ],
)
def test_active_recipe_check_and_sync_cover_extras_and_tagged_inputs(
    tmp_path: Path, monkeypatch, guide: str
) -> None:
    pyproject = tmp_path / "Python/pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text('[project]\nversion = "0.25.0"\n', encoding="utf-8")
    path = tmp_path / guide
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "**Version:** 0.24.0\n"
        "Runnable examples for `structural-lib-is456` 0.24.0.\n"
        'pip install "structural-lib-is456==0.24.0"\n'
        '%pip install "structural-lib-is456[dxf,render]==0.24.0"\n'
        "https://raw.githubusercontent.com/Pravin-surawase/structural_engineering_lib/v0.24.0/Python/examples/sample_beam_design.csv\n"
        "Expected structural_lib: 0.24.0\n"
        "Historical publication: v0.24.0 on the original date.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bump_version, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--check-docs"])
    assert bump_version.main() == 1
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--sync-docs"])
    assert bump_version.main() == 0
    updated = path.read_text(encoding="utf-8")
    assert "structural-lib-is456==0.25.0" in updated
    assert "structural-lib-is456[dxf,render]==0.25.0" in updated
    assert "/v0.25.0/Python/examples/sample_beam_design.csv" in updated
    assert "Historical publication: v0.24.0 on the original date." in updated
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--check-docs"])
    assert bump_version.main() == 0
