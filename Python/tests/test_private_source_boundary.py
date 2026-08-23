"""Protected engineering-source material stays local and outside distributions."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_private_sources_directory_is_ignored_and_untracked() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/private_sources/" in gitignore

    tracked = subprocess.run(
        ["git", "ls-files", "private_sources"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert tracked.stdout == ""

    ignored_paths = (
        "private_sources/is456_library_first/manifest.json",
        "private_sources/is_code_library/library.sqlite3",
        "private_sources/is_code_library/source_pdfs/is13920/example.pdf",
    )
    for ignored_path in ignored_paths:
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", ignored_path],
            cwd=ROOT,
            check=False,
        )
        assert ignored.returncode == 0, ignored_path


def test_package_configuration_has_no_private_source_data() -> None:
    pyproject = (ROOT / "Python" / "pyproject.toml").read_text(encoding="utf-8")
    assert "private_sources" not in pyproject
