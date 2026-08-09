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

    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "private_sources/is456_library_first/manifest.json",
        ],
        cwd=ROOT,
        check=False,
    )
    assert ignored.returncode == 0


def test_package_configuration_has_no_private_source_data() -> None:
    pyproject = (ROOT / "Python" / "pyproject.toml").read_text(encoding="utf-8")
    assert "private_sources" not in pyproject
