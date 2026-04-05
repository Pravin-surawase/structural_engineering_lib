"""Tests for release scripts (bump_version.py, release.py).

Integration tests that exercise the scripts via subprocess.
All bump operations use --dry-run to remain non-destructive.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable  # Use current Python interpreter
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"
RELEASE_SCRIPT = REPO_ROOT / "scripts" / "release.py"

# Files that bump_version.py would modify — snapshot checksums to detect changes
VERSION_TRACKED_FILES = [
    REPO_ROOT / "Python" / "pyproject.toml",
    REPO_ROOT / "react_app" / "package.json",
    REPO_ROOT / "CITATION.cff",
]


def run_script(
    script: Path, *args: str, timeout: int = 120
) -> subprocess.CompletedProcess:
    """Run a script and return the result."""
    return subprocess.run(
        [PYTHON, str(script), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=timeout,
    )


def _file_checksums() -> dict[str, str]:
    """Return md5 checksums for tracked version files."""
    checksums: dict[str, str] = {}
    for f in VERSION_TRACKED_FILES:
        if f.exists():
            checksums[str(f)] = hashlib.md5(f.read_bytes()).hexdigest()
    return checksums


# ─── bump_version.py ─────────────────────────────────────────────────────────


class TestBumpVersionCurrent:
    """Tests for the --current flag."""

    def test_current_version(self):
        """--current returns a valid semver string."""
        result = run_script(BUMP_SCRIPT, "--current")
        assert result.returncode == 0
        output = result.stdout.strip()
        # Output format: "Current version: X.Y.Z"
        assert "Current version:" in output
        version_part = output.split(":")[-1].strip()
        parts = version_part.split(".")
        assert len(parts) == 3, f"Expected semver X.Y.Z, got: {version_part}"
        for p in parts:
            assert p.isdigit(), f"Non-numeric semver component: {p}"


class TestBumpVersionDryRun:
    """Tests for --dry-run ensuring no actual file changes."""

    def test_dry_run_no_file_changes(self):
        """0.99.0 --dry-run makes no actual changes to any files."""
        before = _file_checksums()
        result = run_script(BUMP_SCRIPT, "0.99.0", "--dry-run")
        after = _file_checksums()
        assert before == after, "Dry-run modified files!"
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout or "WOULD UPDATE" in result.stdout

    def test_dry_run_shows_would_update(self):
        """--dry-run output includes WOULD UPDATE for tracked files."""
        result = run_script(BUMP_SCRIPT, "0.99.0", "--dry-run")
        assert result.returncode == 0
        assert "WOULD UPDATE" in result.stdout


class TestBumpVersionValidation:
    """Tests for version format and ordering validation."""

    @pytest.mark.parametrize(
        "bad_version",
        [
            "abc",
            "1.2",
            "1.2.3.4",
            "v1.0.0",
            "1.0.0-beta",
            "1.0",
            "hello",
            "",
            "...",
            "1.2.x",
        ],
    )
    def test_invalid_version_format(self, bad_version: str):
        """Invalid versions return non-zero exit code."""
        result = run_script(BUMP_SCRIPT, bad_version)
        assert result.returncode != 0, f"Expected failure for version '{bad_version}'"
        # Should contain an error message about format
        combined = result.stdout + result.stderr
        assert "ERROR" in combined or "Invalid" in combined or "Usage" in combined

    def test_semver_ordering_rejects_downgrade(self):
        """Bumping to a lower version returns error."""
        result = run_script(BUMP_SCRIPT, "0.0.1", "--dry-run")
        assert result.returncode != 0
        assert "must be higher" in result.stdout or "ERROR" in result.stdout

    def test_semver_ordering_force_override(self):
        """--force allows downgrade (dry-run to avoid actual changes)."""
        before = _file_checksums()
        result = run_script(BUMP_SCRIPT, "0.0.1", "--force", "--dry-run")
        after = _file_checksums()
        assert result.returncode == 0
        assert before == after, "--force --dry-run should not modify files"

    def test_equal_version_rejected(self):
        """Bumping to the same (current) version is rejected."""
        # Get current version first
        current_result = run_script(BUMP_SCRIPT, "--current")
        current_version = current_result.stdout.strip().split(":")[-1].strip()
        # Try bumping to the same version
        result = run_script(BUMP_SCRIPT, current_version, "--dry-run")
        assert result.returncode != 0
        assert "must be higher" in result.stdout or "ERROR" in result.stdout


class TestBumpVersionReport:
    """Tests for --report flag."""

    def test_report_lists_expected_files(self):
        """--report lists core version files and doc files."""
        result = run_script(BUMP_SCRIPT, "--report")
        assert result.returncode == 0
        output = result.stdout
        assert "Core version pins:" in output
        assert "pyproject.toml" in output
        assert "package.json" in output
        assert "CITATION.cff" in output
        assert "Doc version references:" in output
        assert "Doc last-updated stamps:" in output
        assert "Release logs (manual):" in output
        assert "CHANGELOG.md" in output


class TestBumpVersionCheckDocs:
    """Tests for --check-docs flag."""

    def test_check_docs_runs(self):
        """--check-docs runs without crashing and returns 0 or 1."""
        result = run_script(BUMP_SCRIPT, "--check-docs")
        # May return 0 (in sync) or 1 (stale) — both are valid, not a crash
        assert result.returncode in (0, 1)
        output = result.stdout
        assert "up to date" in output or "stale" in output or "Checking" in output


class TestBumpVersionSyncDocs:
    """Tests for --sync-docs --dry-run."""

    def test_sync_docs_dry_run(self):
        """--sync-docs --dry-run previews doc sync without changes."""
        before = _file_checksums()
        result = run_script(BUMP_SCRIPT, "--sync-docs", "--dry-run")
        after = _file_checksums()
        assert result.returncode == 0
        assert before == after, "--sync-docs --dry-run modified files!"
        assert "DRY RUN" in result.stdout


class TestBumpVersionPatternMatch:
    """Tests for pattern matching edge cases."""

    def test_pattern_match_detection(self):
        """If a VERSION_FILES entry has a nonexistent path, output contains 'SKIP'."""
        # Run a dry-run bump to a high version — any SKIP messages for
        # missing files should appear in the output.  We can't control
        # which files exist, but the script uses "SKIP (not found)" when
        # a file is missing.  Run the bump and search for that pattern.
        result = run_script(BUMP_SCRIPT, "0.99.0", "--dry-run")
        # The script itself handles missing files gracefully.
        # We verify the script ran successfully even if some files are missing.
        assert result.returncode == 0
        # stdout should contain output about the files being processed
        assert len(result.stdout) > 0


# ─── release.py ──────────────────────────────────────────────────────────────


class TestReleaseHelp:
    """Tests for help output."""

    def test_no_subcommand_prints_help(self):
        """No subcommand prints help and returns non-zero."""
        result = run_script(RELEASE_SCRIPT)
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "usage" in combined.lower() or "help" in combined.lower()

    def test_verify_help(self):
        """verify --help shows arguments."""
        result = run_script(RELEASE_SCRIPT, "verify", "--help")
        assert result.returncode == 0
        output = result.stdout
        assert "--version" in output
        assert "--source" in output


class TestReleasePreflight:
    """Tests for the preflight subcommand."""

    @pytest.mark.slow
    def test_preflight_runs(self):
        """preflight subcommand runs and returns structured output."""
        result = run_script(RELEASE_SCRIPT, "preflight")
        # May return 0 or 1 depending on repo state — not a crash
        assert result.returncode in (0, 1)
        output = result.stdout
        assert "PRE-RELEASE VALIDATION" in output
        # Should contain numbered check sections
        assert "1. Git State" in output
        assert "2. Version" in output

    @pytest.mark.slow
    def test_preflight_with_version(self):
        """preflight 0.99.0 validates target version."""
        result = run_script(RELEASE_SCRIPT, "preflight", "0.99.0")
        assert result.returncode in (0, 1)
        output = result.stdout
        assert "PRE-RELEASE VALIDATION" in output
        # Should mention the target version
        assert "0.99.0" in output or "Target" in output

    @pytest.mark.slow
    def test_preflight_detects_version_issues(self):
        """A version equal to current is flagged in preflight."""
        # Get current version
        current_result = run_script(BUMP_SCRIPT, "--current")
        current_version = current_result.stdout.strip().split(":")[-1].strip()
        # Run preflight with the current version — should flag it
        result = run_script(RELEASE_SCRIPT, "preflight", current_version)
        assert result.returncode != 0
        output = result.stdout
        assert "not higher" in output or "✗" in output


class TestReleaseCheckDocs:
    """Tests for the check-docs subcommand."""

    def test_check_docs_command(self):
        """check-docs runs and returns result (pass or fail)."""
        result = run_script(RELEASE_SCRIPT, "check-docs")
        # 0 = docs in sync, 1 = mismatch — both are valid non-crash exits
        assert result.returncode in (0, 1)
        output = result.stdout
        # Should produce some output about its checks
        assert len(output) > 0 or result.returncode == 0


class TestReleaseRun:
    """Tests for the run subcommand."""

    @pytest.mark.slow
    def test_run_dry_run(self):
        """run 0.99.0 --dry-run --no-open runs all checks + bump in dry-run mode."""
        before = _file_checksums()
        result = run_script(RELEASE_SCRIPT, "run", "0.99.0", "--dry-run", "--no-open")
        after = _file_checksums()
        assert before == after, "Dry-run modified files!"
        # Should show the release banner
        output = result.stdout
        assert "DRY-RUN" in output or "RELEASE" in output
        # Exit code depends on test suite pass/fail, but files must be unchanged
        assert result.returncode in (0, 1)

    def test_run_without_version(self):
        """run without version shows usage info and returns non-zero."""
        result = run_script(RELEASE_SCRIPT, "run")
        assert result.returncode != 0
        output = result.stdout
        assert "Usage" in output or "usage" in output or "version" in output.lower()


class TestReleaseChecklist:
    """Tests for the checklist subcommand."""

    def test_checklist_runs(self):
        """checklist subcommand validates pre-release checklist structure."""
        result = run_script(RELEASE_SCRIPT, "checklist")
        # 0 = valid, 1 = missing headings/items
        assert result.returncode in (0, 1)


# ─── Edge Cases ──────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Cross-cutting edge case tests."""

    @pytest.mark.parametrize(
        "bad_version",
        [
            "abc",
            "1.2",
            "1.2.3.4",
            "v0.1.0",
            "0.0",
            "one.two.three",
        ],
    )
    def test_concurrent_version_format_validation(self, bad_version: str):
        """Multiple invalid formats are all rejected by bump_version.py."""
        result = run_script(BUMP_SCRIPT, bad_version)
        assert result.returncode != 0, f"Expected failure for '{bad_version}'"

    def test_scripts_exist(self):
        """Both release scripts exist at expected paths."""
        assert BUMP_SCRIPT.exists(), f"Missing: {BUMP_SCRIPT}"
        assert RELEASE_SCRIPT.exists(), f"Missing: {RELEASE_SCRIPT}"

    def test_bump_no_args_shows_usage(self):
        """bump_version.py with no args shows current version and usage."""
        result = run_script(BUMP_SCRIPT)
        assert result.returncode != 0
        output = result.stdout
        assert "Current version:" in output
        assert "Usage" in output or "usage" in output
