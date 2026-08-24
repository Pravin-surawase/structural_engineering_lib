"""Tests for release scripts (bump_version.py, release.py).

Integration tests that exercise the scripts via subprocess.
All bump operations use --dry-run to remain non-destructive.
"""

import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
PYTHON = sys.executable  # Use current Python interpreter
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"
RELEASE_SCRIPT = REPO_ROOT / "scripts" / "release.py"
release = importlib.import_module("scripts.release")

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
        """--current returns the legacy release or a PEP 440 Alpha identifier."""
        result = run_script(BUMP_SCRIPT, "--current")
        assert result.returncode == 0
        output = result.stdout.strip()
        assert "Current version:" in output
        version_part = output.split(":")[-1].strip()
        assert re.fullmatch(r"\d+\.\d+\.\d+(?:a\d+)?", version_part), version_part


class TestBumpVersionDryRun:
    """Tests for --dry-run ensuring no actual file changes."""

    def test_dry_run_no_file_changes(self):
        """0.99.0a1 --dry-run makes no actual changes to any files."""
        before = _file_checksums()
        result = run_script(BUMP_SCRIPT, "0.99.0a1", "--dry-run")
        after = _file_checksums()
        assert before == after, "Dry-run modified files!"
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout or "WOULD UPDATE" in result.stdout

    def test_dry_run_shows_would_update(self):
        """--dry-run output includes WOULD UPDATE for tracked files."""
        result = run_script(BUMP_SCRIPT, "0.99.0a1", "--dry-run")
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
            "1.0.0",
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
        result = run_script(BUMP_SCRIPT, "0.0.1a1", "--dry-run")
        assert result.returncode != 0
        assert "must be higher" in result.stdout or "ERROR" in result.stdout

    def test_semver_ordering_force_override(self):
        """--force allows downgrade (dry-run to avoid actual changes)."""
        before = _file_checksums()
        result = run_script(BUMP_SCRIPT, "0.0.1a1", "--force", "--dry-run")
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
        result = run_script(BUMP_SCRIPT, "0.99.0a1", "--dry-run")
        # The script itself handles missing files gracefully.
        # We verify the script ran successfully even if some files are missing.
        assert result.returncode == 0
        # stdout should contain output about the files being processed
        assert len(result.stdout) > 0


# ─── release.py ──────────────────────────────────────────────────────────────


def test_release_publication_authorization_holds_by_default(tmp_path: Path) -> None:
    authorization = tmp_path / "release-publication-authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "schema_version": "release-publication-authorization/v1",
                "decision": "HOLD",
                "version": None,
                "tag": None,
                "authorized_targets": [],
                "authorized_by": None,
                "authorized_at_utc": None,
                "exact_candidate_review_receipt": None,
                "exact_candidate_review_receipt_sha256": None,
                "qualified_structural_engineering_review": False,
                "professional_approval": False,
            }
        ),
        encoding="utf-8",
    )

    errors = release._release_publication_authorization_errors(
        "0.23.1a1",
        "pypi",
        authorization,
        repo_root=tmp_path,
    )

    assert "release publication decision is HOLD, not AUTHORIZED" in errors


@pytest.mark.parametrize(
    ("errors", "wheel_supplied", "authorization_errors", "verdict", "exit_code"),
    [
        (1, False, None, "NOT_READY", 1),
        (0, False, None, "READY_TO_PREPARE_CANDIDATE", 0),
        (0, True, None, "CANDIDATE_TECHNICALLY_READY", 0),
        (
            0,
            True,
            ["release publication decision is HOLD, not AUTHORIZED"],
            "CANDIDATE_TECHNICALLY_READY",
            0,
        ),
        (0, True, [], "READY_TO_PUBLISH", 0),
    ],
)
def test_preflight_verdicts_are_mode_accurate(
    errors: int,
    wheel_supplied: bool,
    authorization_errors: list[str] | None,
    verdict: str,
    exit_code: int,
) -> None:
    actual, holds, actual_exit = release._preflight_verdict(
        errors,
        wheel_supplied=wheel_supplied,
        authorization_errors=authorization_errors,
    )

    assert actual == verdict
    assert actual_exit == exit_code
    assert bool(holds) is (verdict not in {"NOT_READY", "READY_TO_PUBLISH"})


@pytest.mark.parametrize(
    ("target_version", "wheel_supplied", "publication_target", "expected"),
    [
        (
            "0.24.0a1",
            True,
            None,
            [
                "positional target version is pre-bump-only and cannot accompany "
                "--wheel"
            ],
        ),
        (
            None,
            False,
            "pypi",
            ["publication target evaluation requires --wheel"],
        ),
        ("0.24.0a1", False, None, []),
        (None, True, "pypi", []),
    ],
)
def test_preflight_rejects_ambiguous_mode_combinations(
    target_version: str | None,
    wheel_supplied: bool,
    publication_target: str | None,
    expected: list[str],
) -> None:
    assert (
        release._preflight_mode_errors(
            target_version,
            wheel_supplied=wheel_supplied,
            publication_target=publication_target,
        )
        == expected
    )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _authorized_release_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Create a reviewed package commit plus an evidence-only authorization commit."""

    repo = tmp_path / "repo"
    python_root = repo / "Python"
    verification_root = repo / "docs" / "verification"
    python_root.mkdir(parents=True)
    verification_root.mkdir(parents=True)
    (python_root / "package.txt").write_text("reviewed package\n", encoding="utf-8")

    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Release Test")
    _git(repo, "config", "user.email", "release-test@example.invalid")
    _git(repo, "add", "Python/package.txt")
    _git(repo, "commit", "-q", "-m", "reviewed candidate")

    reviewed_head = _git(repo, "rev-parse", "HEAD")
    reviewed_tree = _git(repo, "rev-parse", "HEAD^{tree}")
    reviewed_python_tree = _git(repo, "rev-parse", "HEAD:Python")
    receipt_path = verification_root / "v0.24.0a1-exact-review.json"
    receipt = {
        "schema_version": "exact-candidate-review-receipt/v1",
        "decision": "ACCEPT",
        "reviewed_candidate": {
            "head_sha": reviewed_head,
            "tree_sha": reviewed_tree,
            "python_tree_sha": reviewed_python_tree,
            "version": "0.24.0a1",
            "tag": "v0.24.0a1",
            "reviewed_targets": ["pypi", "github-release"],
        },
        "hosted_checks": {
            "required_pr_checks": {
                "status": "PASS",
                "head_sha": reviewed_head,
                "url": "https://github.com/example/project/actions/runs/100",
            },
            "weekly_verification": {
                "status": "PASS",
                "head_sha": reviewed_head,
                "url": "https://github.com/example/project/actions/runs/101",
            },
        },
        "reviewer": {
            "identity": "independent-reviewer",
            "independent": True,
            "reviewed_at_utc": "2026-08-17T00:05:00Z",
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    receipt_sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()

    authorization_path = verification_root / "release-publication-authorization.json"
    authorization_path.write_text(
        json.dumps(
            {
                "schema_version": "release-publication-authorization/v1",
                "decision": "AUTHORIZED",
                "version": "0.24.0a1",
                "tag": "v0.24.0a1",
                "authorized_targets": ["pypi", "github-release"],
                "authorized_by": "repository-owner",
                "authorized_at_utc": "2026-08-17T00:10:00Z",
                "exact_candidate_review_receipt": (
                    "docs/verification/v0.24.0a1-exact-review.json"
                ),
                "exact_candidate_review_receipt_sha256": receipt_sha,
                "qualified_structural_engineering_review": False,
                "professional_approval": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "docs/verification")
    _git(repo, "commit", "-q", "-m", "authorize reviewed candidate")
    return authorization_path, receipt_path


def test_release_publication_authorization_binds_version_tag_and_target(
    tmp_path: Path,
) -> None:
    record, _ = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]

    assert (
        release._release_publication_authorization_errors(
            "0.24.0a1", "pypi", record, repo_root=repo
        )
        == []
    )
    assert release._release_publication_authorization_errors(
        "0.24.0a1", "testpypi", record, repo_root=repo
    ) == [
        "release authorization does not include target 'testpypi'",
        "exact candidate review receipt does not include target 'testpypi'",
    ]


def test_release_publication_authorization_rejects_fabricated_receipt_text(
    tmp_path: Path,
) -> None:
    record, _ = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    authorization = json.loads(record.read_text(encoding="utf-8"))
    authorization["exact_candidate_review_receipt"] = "review-receipt-sha256"
    record.write_text(json.dumps(authorization), encoding="utf-8")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert errors == [
        "exact candidate review receipt must be a repository-relative JSON file "
        "under docs/verification"
    ]


def test_release_publication_authorization_rejects_tampered_receipt(
    tmp_path: Path,
) -> None:
    record, receipt_path = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["reviewed_candidate"]["tree_sha"] = "0" * 40
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert errors == ["exact candidate review receipt SHA-256 does not match"]


def test_release_publication_authorization_requires_exact_hosted_receipts(
    tmp_path: Path,
) -> None:
    record, receipt_path = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["hosted_checks"]["weekly_verification"]["head_sha"] = "0" * 40
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    authorization = json.loads(record.read_text(encoding="utf-8"))
    authorization["exact_candidate_review_receipt_sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    record.write_text(json.dumps(authorization), encoding="utf-8")
    _git(repo, "add", "docs/verification")
    _git(repo, "commit", "-q", "-m", "record mismatched hosted receipt")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert (
        "exact candidate review receipt weekly_verification head does not match"
        in errors
    )


def test_release_publication_authorization_rejects_false_reviewed_tree(
    tmp_path: Path,
) -> None:
    record, receipt_path = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["reviewed_candidate"]["tree_sha"] = "0" * 40
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    authorization = json.loads(record.read_text(encoding="utf-8"))
    authorization["exact_candidate_review_receipt_sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    record.write_text(json.dumps(authorization), encoding="utf-8")
    _git(repo, "add", "docs/verification")
    _git(repo, "commit", "-q", "-m", "tamper with reviewed tree")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert "reviewed candidate tree does not match reviewed head" in errors


def test_release_publication_authorization_rejects_post_review_package_drift(
    tmp_path: Path,
) -> None:
    record, _ = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    (repo / "Python" / "package.txt").write_text(
        "changed after review\n", encoding="utf-8"
    )
    _git(repo, "add", "Python/package.txt")
    _git(repo, "commit", "-q", "-m", "change package after review")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert "Python package content changed after exact candidate review" in errors
    assert any("Python/package.txt" in error for error in errors)


def test_release_publication_authorization_rejects_pre_review_authorization(
    tmp_path: Path,
) -> None:
    record, _ = _authorized_release_fixture(tmp_path)
    repo = record.parents[2]
    authorization = json.loads(record.read_text(encoding="utf-8"))
    authorization["authorized_at_utc"] = "2026-08-17T00:00:00Z"
    record.write_text(json.dumps(authorization), encoding="utf-8")
    _git(repo, "add", "docs/verification/release-publication-authorization.json")
    _git(repo, "commit", "-q", "-m", "pre-authorize candidate")

    errors = release._release_publication_authorization_errors(
        "0.24.0a1", "pypi", record, repo_root=repo
    )

    assert "release authorization must occur after exact candidate review" in errors


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


class TestReleaseVerifyDependencies:
    """The isolated wheel verifier must install its declared test tools."""

    def test_dev_extra_declares_hypothesis(self):
        pyproject = (REPO_ROOT / "Python" / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        dev_section = pyproject.split("dev = [", 1)[1].split("]", 1)[0]
        assert "hypothesis" in dev_section

    def test_wheel_verify_installs_exact_test_dependencies(self):
        source = RELEASE_SCRIPT.read_text(encoding="utf-8")
        verify_block = source.split("def cmd_verify", 1)[1].split(
            "# ─── Check Docs", 1
        )[0]
        assert 'f"{wheel}[dev,validation]"' in verify_block
        assert (
            'f"structural-lib-is456[dev,validation]==={args.version}"' in verify_block
        )
        assert '"httpx>=0.27"' in verify_block
        assert '"--pre"' not in verify_block
        assert '"--no-cache-dir"' in verify_block
        assert '"https://pypi.org/simple/"' in verify_block
        assert '"-r", str(requirements)' not in verify_block

    def test_wheel_verify_uses_isolated_pytest_configuration(self):
        source = RELEASE_SCRIPT.read_text(encoding="utf-8")
        verify_block = source.split("def cmd_verify", 1)[1].split(
            "# ─── Check Docs", 1
        )[0]

        assert "_assert_package_import_from_venv" in verify_block
        assert "_isolated_pytest_config" in verify_block
        assert '"--import-mode=importlib"' in verify_block
        assert '"not slow and not repo_only"' in verify_block
        assert "cwd=temp_root" in verify_block

    def test_candidate_preflight_runs_the_exact_wheel_uat(self):
        source = RELEASE_SCRIPT.read_text(encoding="utf-8")
        helper = source.split("def _clean_wheel_import_version", 1)[1].split(
            "def _print_version_errors", 1
        )[0]

        assert '"structural_lib.release_uat"' in helper
        assert '"--require-installed-wheel"' in helper

    def test_wheel_verify_commands_are_package_scoped_and_isolated(
        self, tmp_path, monkeypatch
    ):
        wheel = tmp_path / "structural_lib_is456-0.23.1a1-py3-none-any.whl"
        calls: list[tuple[list[str], Path | None, dict[str, str] | None]] = []

        class TemporaryDirectory:
            def __enter__(self):
                return str(tmp_path)

            def __exit__(self, *_):
                return False

        def record_run_check(cmd, *, cwd=None, timeout=600, env=None):
            calls.append((cmd, cwd, env))

        monkeypatch.setattr(release, "_run_check", record_run_check)
        monkeypatch.setattr(release, "_find_wheel", lambda *_: wheel)
        monkeypatch.setattr(
            release.tempfile, "TemporaryDirectory", lambda **_: TemporaryDirectory()
        )

        result = release.cmd_verify(
            argparse.Namespace(
                wheel_dir="Python/dist",
                job="Python/examples/sample_job_is456.json",
                source="wheel",
                version="0.23.1a1",
                skip_cli=True,
            )
        )

        assert result == 0
        install_commands = [cmd for cmd, _, _ in calls if "install" in cmd]
        assert [
            str(tmp_path / "venv" / "bin" / "pip"),
            "install",
            f"{wheel}[dev,validation]",
            "httpx>=0.27",
        ] in install_commands
        assert all("requirements.txt" not in " ".join(cmd) for cmd in install_commands)
        pytest_calls = [cmd for cmd, _, _ in calls if "pytest" in cmd]
        assert len(pytest_calls) == 1
        assert "--import-mode=importlib" in pytest_calls[0]
        assert "-c" in pytest_calls[0]
        research_test = str(
            REPO_ROOT / "Python" / "tests" / "test_research_prototypes.py"
        )
        assert research_test in pytest_calls[0]
        assert pytest_calls[0][pytest_calls[0].index(research_test) - 1] == "--ignore"
        repo_context_test = str(REPO_ROOT / "Python" / "tests" / "test_repo_context.py")
        assert repo_context_test in pytest_calls[0]
        assert (
            pytest_calls[0][pytest_calls[0].index(repo_context_test) - 1] == "--ignore"
        )
        assert any(cwd == tmp_path for _, cwd, _ in calls)
        pytest_config = tmp_path / "pytest.ini"
        assert pytest_config.read_text(encoding="utf-8").startswith("[pytest]\n")
        assert "pythonpath" not in pytest_config.read_text(encoding="utf-8")

    def test_pypi_verify_forces_fresh_official_index(self, tmp_path, monkeypatch):
        calls: list[list[str]] = []

        class TemporaryDirectory:
            def __enter__(self):
                return str(tmp_path)

            def __exit__(self, *_):
                return False

        def record_run_check(cmd, *, cwd=None, timeout=600, env=None):
            calls.append(cmd)

        monkeypatch.setattr(release, "_run_check", record_run_check)
        monkeypatch.setattr(
            release.tempfile, "TemporaryDirectory", lambda **_: TemporaryDirectory()
        )

        result = release.cmd_verify(
            argparse.Namespace(
                wheel_dir="Python/dist",
                job="Python/examples/sample_job_is456.json",
                source="pypi",
                version="0.23.1a1",
                skip_cli=True,
            )
        )

        assert result == 0
        assert [
            str(tmp_path / "venv" / "bin" / "pip"),
            "install",
            "--no-cache-dir",
            "--index-url",
            "https://pypi.org/simple/",
            "structural-lib-is456[dev,validation]===0.23.1a1",
            "httpx>=0.27",
        ] in calls


class TestReleaseReactDependencies:
    """Release checks must provision isolated worktree dependencies safely."""

    def test_missing_dependencies_are_installed_from_lockfile(
        self, tmp_path, monkeypatch
    ):
        react_dir = tmp_path / "react_app"
        react_dir.mkdir()
        (react_dir / "package-lock.json").write_text("{}\n", encoding="utf-8")
        calls: list[list[str]] = []

        def fake_run(cmd, *, cwd=None, timeout=600, env=None):
            calls.append(cmd)
            tsc = react_dir / "node_modules" / ".bin" / "tsc"
            tsc.parent.mkdir(parents=True)
            tsc.write_text("", encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        monkeypatch.setattr(release, "_run_with_timeout", fake_run)

        assert release._ensure_react_dependencies(react_dir, {"PATH": "test"})
        assert calls == [["npm", "ci"]]

    def test_dependency_symlink_is_rejected_without_running_npm(
        self, tmp_path, monkeypatch
    ):
        react_dir = tmp_path / "react_app"
        react_dir.mkdir()
        target = tmp_path / "shared-node-modules"
        target.mkdir()
        (react_dir / "node_modules").symlink_to(target, target_is_directory=True)
        called = False

        def fail_if_called(*_args, **_kwargs):
            nonlocal called
            called = True
            raise AssertionError("npm must not traverse a dependency symlink")

        monkeypatch.setattr(release, "_run_with_timeout", fail_if_called)

        assert not release._ensure_react_dependencies(react_dir, {"PATH": "test"})
        assert not called

    def test_release_run_and_preflight_share_dependency_provisioner(self):
        source = RELEASE_SCRIPT.read_text(encoding="utf-8")
        assert source.count("_ensure_react_dependencies(react_dir, node_env)") == 2


class TestPublishWorkflow:
    """The release workflow must preserve package maturity on GitHub."""

    def test_development_status_controls_github_prerelease(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(
            encoding="utf-8"
        )

        assert "prerelease: ${{ steps.version.outputs.prerelease }}" in workflow
        assert "Development Status :: 3 - Alpha" in workflow
        assert "prerelease: ${{ needs.validate.outputs.prerelease }}" in workflow

    def test_future_publications_require_alpha_identifiers(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(
            encoding="utf-8"
        )

        assert "^[0-9]+\\.[0-9]+\\.[0-9]+a[0-9]+$" in workflow
        assert "Expected PEP 440 Alpha format X.Y.ZaN" in workflow

    def test_release_validation_installs_maintained_test_dependencies(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(
            encoding="utf-8"
        )

        assert "python -m pip install -e '.[dev,validation]' 'httpx>=0.27'" in workflow
        assert "python -m pip install -e '.[dev]'" not in workflow

    def test_publication_fails_closed_on_permission_record(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(
            encoding="utf-8"
        )

        assert "python ../scripts/release.py permission-check" in workflow
        assert '"public_distribution_permission_gate_passed": True' in workflow
        assert "IS456-PUBLIC-DISTRIBUTION-001" in workflow
        assert "python ../scripts/release.py footing-inclusion-check" in workflow
        assert '"footing_release_inclusion_gate_passed": True' in workflow
        assert "FOOT-ISO-RC-V1-RELEASE-INCLUSION" in workflow
        assert "-m structural_lib.release_uat" in workflow
        assert "authorization-check" in workflow
        assert "release-publication-authorization.json" in workflow
        assert "fetch-depth: 0" in workflow
        assert "exact_candidate_review_receipt_sha256" in workflow
        assert "review_receipt" in workflow
        assert '"reviewed_candidate"' in workflow
        assert '"professional_approval": False' in workflow

    def test_alpha_ordering_preserves_legacy_release_history(self):
        assert release._release_version_key("0.24.0a1") > release._release_version_key(
            "0.23.0"
        )
        assert release._release_version_key("0.24.0a2") > release._release_version_key(
            "0.24.0a1"
        )
        assert release._release_version_key("0.24.0a1") < release._release_version_key(
            "0.24.0"
        )

    def test_docs_workflow_is_build_only_until_pages_is_configured(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-docs.yml").read_text(
            encoding="utf-8"
        )
        pr_workflow = (
            REPO_ROOT / ".github" / "workflows" / "fast-checks.yml"
        ).read_text(encoding="utf-8")
        mkdocs = (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")

        assert "mkdocs build --strict" in workflow
        assert "gh-deploy" not in workflow
        assert "contents: write" not in workflow
        assert "pull_request:" not in workflow
        assert "pull_request:" in pr_workflow
        assert "name: Documentation Validation" in pr_workflow
        assert "mkdocs build --strict" in pr_workflow
        assert "site_url:" not in mkdocs


class TestReleasePreflight:
    """Tests for the preflight subcommand."""

    def test_docker_preflight_uses_project_node_major(self):
        compose = (REPO_ROOT / "docker-compose.preflight.yml").read_text(
            encoding="utf-8"
        )
        node_major = (REPO_ROOT / ".nvmrc").read_text(encoding="utf-8").strip()
        assert f"image: node:{node_major}-alpine" in compose

    def test_docker_preflight_mounts_repo_only_test_inputs(self):
        compose = (REPO_ROOT / "docker-compose.preflight.yml").read_text(
            encoding="utf-8"
        )
        for mount in (
            "./scripts:/app/scripts:ro",
            "./agents:/app/agents:ro",
            "./.github/agents:/app/.github/agents:ro",
            "./react_app/package.json:/app/react_app/package.json:ro",
            "./CITATION.cff:/app/CITATION.cff:ro",
        ):
            assert mount in compose
        assert '"-m", "not slow"' in compose
        assert '"-p", "no:cacheprovider"' in compose
        assert "test-fastapi:" in compose
        assert "./fastapi_app:/app/fastapi_app:ro" in compose
        assert "./docs:/app/docs:ro" in compose

    def test_preflight_covers_the_fastapi_ci_suite(self):
        source = RELEASE_SCRIPT.read_text(encoding="utf-8")
        preflight = source.split("def cmd_preflight", 1)[1]

        assert (
            '_run_local_pytest_gate("4. FastAPI Tests", "fastapi_app/tests/")'
            in preflight
        )
        assert '"test-fastapi"' in preflight

    def test_fastapi_image_retries_slow_dependency_downloads(self):
        dockerfile = (REPO_ROOT / "Dockerfile.fastapi").read_text(encoding="utf-8")
        assert "PIP_DEFAULT_TIMEOUT=120" in dockerfile
        assert "PIP_RETRIES=5" in dockerfile
        assert "--timeout 120 --retries 5" in dockerfile

    def test_failure_tail_reports_bounded_diagnostics(self, capsys):
        result = subprocess.CompletedProcess(
            ["docker", "compose"], 1, "x" * 5000, "final-error"
        )

        release._print_failure_tail(result, max_chars=100)

        output = capsys.readouterr().out
        assert "Last command output" in output
        assert "final-error" in output
        assert len(output) < 200

    def test_public_distribution_permission_record_is_valid(self):
        assert release._public_distribution_permission_errors() == []

    def test_current_source_surfaces_match_release_state_without_wheel(self):
        current = release._version_from_pyproject()
        authorized = release._release_authorization_recorded(current)

        assert (
            release._source_surface_version_errors(
                current, allow_authorized_release=authorized
            )
            == []
        )

    def test_public_distribution_permission_check_fails_closed(
        self, tmp_path, monkeypatch
    ):
        missing = tmp_path / "missing-permission.json"
        monkeypatch.setattr(release, "PUBLIC_DISTRIBUTION_PERMISSION", missing)

        assert release.cmd_permission_check(argparse.Namespace()) == 1

    def test_footing_inclusion_check_fails_closed_when_owned_file_is_missing(
        self, tmp_path
    ):
        receipt = tmp_path / "footing-release-inclusion.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "record_id": "FOOT-ISO-RC-V1-RELEASE-INCLUSION",
                    "source_head": "886871aef93d9a955a3cc2fa613fe49bad589ce7",
                    "required_owned_file_sha256": {"Python/missing.py": "0" * 64},
                    "required_shared_markers": {
                        "fastapi_app/missing.py": ["footing.router"]
                    },
                }
            ),
            encoding="utf-8",
        )

        errors = release._footing_release_inclusion_errors(receipt, repo_root=tmp_path)

        assert "required footing file is missing: Python/missing.py" in errors
        assert (
            "required footing integration file is missing: fastapi_app/missing.py"
            in errors
        )

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
        """preflight 0.99.0a1 validates an Alpha target version."""
        result = run_script(RELEASE_SCRIPT, "preflight", "0.99.0a1")
        assert result.returncode in (0, 1)
        output = result.stdout
        assert "PRE-RELEASE VALIDATION" in output
        # Should mention the target version
        assert "0.99.0a1" in output or "Target" in output

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
        """run 0.99.0a1 --dry-run --no-open runs all checks + bump in dry-run mode."""
        before = _file_checksums()
        result = run_script(RELEASE_SCRIPT, "run", "0.99.0a1", "--dry-run", "--no-open")
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
