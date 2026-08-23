"""Shared fail-closed primitives for repository file mutations.

The public file-operation scripts use this module for one path contract, one
reference classification, one validator protocol, and byte-exact rollback.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".bas",
    ".bat",
    ".cfg",
    ".cjs",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonc",
    ".jsx",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".pyi",
    ".rst",
    ".scss",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vba",
    ".xml",
    ".yaml",
    ".yml",
    ".zsh",
}

IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "logs",
    "node_modules",
    "tmp",
}

# Historical evidence keeps the path text that was true when recorded.
PRESERVED_REFERENCE_DIRS = (
    "docs/_archive",
    "docs/agents/sessions",
    "docs/audit",
    "docs/migration/learning",
    "docs/research",
    "docs/verification",
    "agents/agent-9",
)
PRESERVED_REFERENCE_FILES = {
    ".github/DEVELOPMENT_TIMELINE.md",
    "docs/SESSION_LOG.md",
    "docs/WORKLOG.md",
    "docs/agents/guides/agent-quick-reference.md",
    "docs/agents/guides/agent-workflow-master-guide.md",
    "docs/migration/12-innovation-ideas-new.md",
    "docs/migration/12-innovation-ideas.md",
    "docs/reference/repo-health-baseline-2026-01-07.md",
    "docs/planning/maint-011-developer-gate-hygiene-follow-up.md",
    "Python/tests/test_agent_governance_automation.py",
    "Python/tests/test_ci_workflow_contract.py",
    "Python/tests/test_session_automation.py",
    "scripts/check_codex_git_workflow.py",
    "scripts/check_links.py",
    "scripts/control-plane.json",
}

MARKDOWN_TARGET_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")


class SafeFileError(RuntimeError):
    """Raised when a file operation cannot prove a safe outcome."""


@dataclass(frozen=True)
class Reference:
    file: Path
    line_number: int
    line_text: str
    classification: str

    def as_dict(self, root: Path) -> dict[str, object]:
        return {
            "file": self.file.relative_to(root).as_posix(),
            "line": self.line_number,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    existed: bool
    data: bytes | None
    mode: int | None


@dataclass(frozen=True)
class LinkCheckResult:
    operational: bool
    broken: frozenset[str]
    payload: dict[str, object]
    error: str | None = None


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _lexical_path(raw: str | Path, root: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    return Path(os.path.abspath(candidate))


def _reject_symlink_components(path: Path, root: Path) -> None:
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise SafeFileError(f"Symlink paths are not allowed: {current}")


def resolve_regular_source(raw: str | Path, root: Path) -> Path:
    """Resolve an existing regular file without following repository symlinks."""
    root = root.resolve()
    path = _lexical_path(raw, root)
    if not _within(path, root):
        raise SafeFileError(f"Source must be inside repository: {raw}")
    _reject_symlink_components(path, root)
    if not path.exists():
        raise SafeFileError(f"Source file not found: {path}")
    if not path.is_file():
        raise SafeFileError(f"Source must be a regular file: {path}")
    return path


def resolve_new_destination(raw: str | Path, root: Path, source: Path) -> Path:
    """Resolve a new in-repository destination and reject overwrite semantics."""
    root = root.resolve()
    path = _lexical_path(raw, root)
    if not _within(path, root):
        raise SafeFileError(f"Destination must be inside repository: {raw}")
    _reject_symlink_components(path.parent, root)
    if path == source:
        raise SafeFileError("Source and destination must differ")
    if path.exists() or path.is_symlink():
        raise SafeFileError(f"Destination already exists: {path}")
    return path


def preserves_reference_text(file: Path, root: Path) -> bool:
    try:
        relative = file.relative_to(root).as_posix()
    except ValueError:
        return True
    return relative in PRESERVED_REFERENCE_FILES or any(
        relative == prefix or relative.startswith(f"{prefix}/")
        for prefix in PRESERVED_REFERENCE_DIRS
    )


def iter_repository_files(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    """Return tracked and unignored untracked files, with a non-Git fallback."""
    excluded_roots = [
        Path(value).resolve()
        for value in os.environ.get("SAFE_FILE_EXCLUDE_ROOTS", "").split(os.pathsep)
        if value
    ]
    files: list[Path] = []
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            for raw in proc.stdout.split(b"\0"):
                if not raw:
                    continue
                path = root / os.fsdecode(raw)
                if path.is_file() and not path.is_symlink():
                    files.append(path)
        else:
            files = [p for p in root.rglob("*") if p.is_file() and not p.is_symlink()]
    except (OSError, subprocess.SubprocessError):
        files = [p for p in root.rglob("*") if p.is_file() and not p.is_symlink()]

    filtered: list[Path] = []
    for path in files:
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(
            _within(path.resolve(strict=False), excluded) for excluded in excluded_roots
        ):
            continue
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if suffixes is not None and path.suffix.lower() not in suffixes:
            continue
        filtered.append(path)
    return sorted(set(filtered))


def _relative_posix_path(target: Path, start: Path) -> str:
    return Path(os.path.relpath(target, start=start)).as_posix()


def _rewrite_markdown_target(
    target: str, *, containing_file: Path, source: Path, destination: Path, root: Path
) -> str:
    stripped = target.strip()
    wrapped = stripped.startswith("<") and stripped.endswith(">")
    value = stripped[1:-1] if wrapped else stripped
    if value.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
        return target
    path_text, marker, fragment = value.partition("#")
    if not path_text or any(ch.isspace() for ch in path_text):
        return target
    candidate = (
        root / path_text.lstrip("/")
        if path_text.startswith("/")
        else containing_file.parent / path_text
    )
    try:
        matches = candidate.resolve(strict=False) == source
    except OSError:
        matches = False
    if not matches:
        return target
    if path_text.startswith("/"):
        replacement = "/" + destination.relative_to(root).as_posix()
    else:
        replacement = _relative_posix_path(destination, containing_file.parent)
    if marker:
        replacement += f"#{fragment}"
    if wrapped:
        replacement = f"<{replacement}>"
    return target.replace(stripped, replacement, 1)


def rewrite_reference_text(
    content: str,
    *,
    containing_file: Path,
    source: Path,
    destination: Path,
    root: Path,
) -> str:
    """Rewrite only deterministic path references to *source*."""

    def replace_markdown(match: re.Match[str]) -> str:
        return "".join(
            (
                match.group(1),
                _rewrite_markdown_target(
                    match.group(2),
                    containing_file=containing_file,
                    source=source,
                    destination=destination,
                    root=root,
                ),
                match.group(3),
            )
        )

    rewritten = MARKDOWN_TARGET_RE.sub(replace_markdown, content)
    old_relative = source.relative_to(root).as_posix()
    new_relative = destination.relative_to(root).as_posix()
    rewritten = rewritten.replace(old_relative, new_relative)
    rewritten = rewritten.replace(
        old_relative.replace("/", "\\"), new_relative.replace("/", "\\")
    )
    return rewritten


def classify_references(
    source: Path, destination: Path | None, root: Path
) -> list[Reference]:
    """Classify every basename/path reference as updateable, preserved, or unresolved."""
    old_relative = source.relative_to(root).as_posix()
    new_relative = (
        destination.relative_to(root).as_posix() if destination is not None else None
    )
    tokens = {source.name, old_relative, old_relative.replace("/", "\\")}
    references: list[Reference] = []
    for file in iter_repository_files(root, TEXT_EXTENSIONS):
        if file == source or file == destination:
            continue
        try:
            content = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(content.splitlines(), 1):
            if not any(token in line for token in tokens):
                continue
            candidate_line = line
            if new_relative is not None:
                candidate_line = candidate_line.replace(new_relative, "")
                candidate_line = candidate_line.replace(
                    new_relative.replace("/", "\\"), ""
                )
                if not any(token in candidate_line for token in tokens):
                    continue
            if preserves_reference_text(file, root):
                classification = "preserved"
            elif (
                destination is not None
                and rewrite_reference_text(
                    line,
                    containing_file=file,
                    source=source,
                    destination=destination,
                    root=root,
                )
                != line
            ):
                classification = "updateable"
            else:
                classification = "unresolved"
            references.append(
                Reference(file, line_number, line.strip()[:160], classification)
            )
    return references


def update_references(
    source: Path, destination: Path, references: Iterable[Reference], root: Path
) -> list[str]:
    """Apply deterministic rewrites to the files classified as updateable."""
    updated: list[str] = []
    files = sorted(
        {ref.file for ref in references if ref.classification == "updateable"}
    )
    for file in files:
        content = file.read_text(encoding="utf-8")
        rewritten = rewrite_reference_text(
            content,
            containing_file=file,
            source=source,
            destination=destination,
            root=root,
        )
        if rewritten == content:
            raise SafeFileError(
                f"Predicted reference update produced no change: {file}"
            )
        file.write_text(rewritten, encoding="utf-8")
        updated.append(file.relative_to(root).as_posix())
    return updated


def capture_snapshots(paths: Iterable[Path], root: Path) -> list[FileSnapshot]:
    snapshots: list[FileSnapshot] = []
    for path in sorted(set(paths)):
        if not _within(_lexical_path(path, root), root):
            raise SafeFileError(f"Snapshot path is outside repository: {path}")
        if path.exists() or path.is_symlink():
            if path.is_symlink() or not path.is_file():
                raise SafeFileError(f"Snapshot target must be a regular file: {path}")
            snapshots.append(
                FileSnapshot(
                    path, True, path.read_bytes(), stat.S_IMODE(path.stat().st_mode)
                )
            )
        else:
            snapshots.append(FileSnapshot(path, False, None, None))
    return snapshots


def restore_snapshots(snapshots: Iterable[FileSnapshot], root: Path) -> None:
    """Restore exact bytes/modes and remove paths created by the operation."""
    created_parents: set[Path] = set()
    for snapshot in snapshots:
        if snapshot.existed:
            snapshot.path.parent.mkdir(parents=True, exist_ok=True)
            snapshot.path.write_bytes(snapshot.data or b"")
            if snapshot.mode is not None:
                snapshot.path.chmod(snapshot.mode)
        elif snapshot.path.exists() or snapshot.path.is_symlink():
            if snapshot.path.is_dir() and not snapshot.path.is_symlink():
                raise SafeFileError(
                    f"Rollback refuses to remove directory: {snapshot.path}"
                )
            snapshot.path.unlink()
            created_parents.add(snapshot.path.parent)
    for parent in sorted(
        created_parents, key=lambda item: len(item.parts), reverse=True
    ):
        current = parent
        while current != root and _within(current, root):
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_link_checker(root: Path) -> LinkCheckResult:
    """Run the canonical checker and require valid structured output."""
    checker = root / "scripts" / "check_links.py"
    if not checker.is_file():
        return LinkCheckResult(False, frozenset(), {}, "check_links.py is missing")
    proc = subprocess.run(
        [sys.executable, str(checker), "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return LinkCheckResult(False, frozenset(), {}, f"invalid checker JSON: {exc}")
    if not isinstance(payload, dict) or payload.get("tool") != "check_links":
        return LinkCheckResult(
            False, frozenset(), payload, "unexpected checker payload"
        )
    broken_raw = payload.get("broken_links")
    if not isinstance(broken_raw, list):
        return LinkCheckResult(
            False, frozenset(), payload, "checker omitted broken_links"
        )
    broken = frozenset(
        f"{item.get('file')}::{item.get('target')}"
        for item in broken_raw
        if isinstance(item, dict)
    )
    if proc.returncode not in (0, 1):
        return LinkCheckResult(
            False, broken, payload, f"checker exited {proc.returncode}"
        )
    return LinkCheckResult(True, broken, payload)


def require_no_link_regression(before: LinkCheckResult, after: LinkCheckResult) -> None:
    if not before.operational:
        raise SafeFileError(f"Link baseline unavailable: {before.error}")
    if not after.operational:
        raise SafeFileError(
            f"Post-operation link validation unavailable: {after.error}"
        )
    added = sorted(after.broken - before.broken)
    if added:
        raise SafeFileError("New broken links: " + ", ".join(added[:10]))


def create_content_hashed_backup(file: Path, root: Path) -> tuple[Path, Path]:
    """Create a collision-safe content-addressed backup plus manifest."""
    relative = file.relative_to(root)
    digest = sha256_file(file)
    backup_root = root / "tmp" / "deleted_backups" / digest
    backup_path = backup_root / "files" / relative
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if backup_path.exists() and sha256_file(backup_path) != digest:
        raise SafeFileError(f"Backup hash collision: {backup_path}")
    if not backup_path.exists():
        backup_path.write_bytes(file.read_bytes())
        backup_path.chmod(stat.S_IMODE(file.stat().st_mode))
    manifest_key = hashlib.sha256(relative.as_posix().encode("utf-8")).hexdigest()[:16]
    manifest_path = backup_root / f"manifest-{manifest_key}.json"
    manifest = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source": relative.as_posix(),
        "source_sha256": digest,
        "size_bytes": file.stat().st_size,
        "mode": stat.S_IMODE(file.stat().st_mode),
        "backup": backup_path.relative_to(root).as_posix(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return backup_path, manifest_path
