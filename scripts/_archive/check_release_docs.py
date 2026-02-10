#!/usr/bin/env python3
"""Validate CHANGELOG.md and docs/releases.md have matching versions."""

from __future__ import annotations

from pathlib import Path
import re

CHANGELOG = Path("CHANGELOG.md")
RELEASES = Path("docs/getting-started/releases.md")

VERSION_RE = re.compile(r"^##\s*\[?v?(\d+\.\d+\.\d+)\b")


def _parse_versions(path: Path) -> list[str]:
    versions: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = VERSION_RE.match(line.strip())
        if match:
            versions.append(match.group(1))
    return versions


def _semver_key(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def main() -> int:
    if not CHANGELOG.exists():
        print("ERROR: CHANGELOG.md not found")
        return 1
    if not RELEASES.exists():
        print("ERROR: docs/getting-started/releases.md not found")
        return 1

    changelog_versions = _parse_versions(CHANGELOG)
    releases_versions = _parse_versions(RELEASES)

    if not changelog_versions:
        print("ERROR: No versions found in CHANGELOG.md")
        return 1
    if not releases_versions:
        print("ERROR: No versions found in docs/getting-started/releases.md")
        return 1

    missing_in_releases = sorted(
        set(changelog_versions) - set(releases_versions), key=_semver_key
    )
    missing_in_changelog = sorted(
        set(releases_versions) - set(changelog_versions), key=_semver_key
    )

    if missing_in_releases:
        print("ERROR: Versions in CHANGELOG missing from RELEASES:")
        for version in missing_in_releases:
            print(f"  - {version}")
        return 1

    if missing_in_changelog:
        print("ERROR: Versions in RELEASES missing from CHANGELOG:")
        for version in missing_in_changelog:
            print(f"  - {version}")
        return 1

    latest_changelog = max(changelog_versions, key=_semver_key)
    latest_releases = max(releases_versions, key=_semver_key)
    if latest_changelog != latest_releases:
        print(
            "ERROR: Latest versions do not match: "
            f"CHANGELOG={latest_changelog}, RELEASES={latest_releases}"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
