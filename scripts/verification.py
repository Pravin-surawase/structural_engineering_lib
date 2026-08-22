#!/usr/bin/env python3
"""Plan validation work and reuse only content-bound PASS evidence.

When to use: Classify a candidate into explicit verification domains, inspect
an exact evidence identity, or validate the canonical verification manifest.
Unknown paths and Git-query failures expand to every domain.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = SCRIPT_DIR / "verification-manifest.json"
SCHEMA_PATH = SCRIPT_DIR / "verification-manifest.schema.json"
EVIDENCE_SCHEMA_VERSION = 1
EVIDENCE_DIRECTORY = Path("structural-lib") / "verification-evidence" / "v1"
REQUIRED_DOMAINS = (
    "python",
    "fastapi",
    "react",
    "excel",
    "control_plane",
    "docs",
    "repository",
)

sys.path.insert(0, str(SCRIPT_DIR))
from control_plane import (  # noqa: E402
    ControlPlaneError,
    read_strict_json,
    schema_errors,
)


class VerificationError(ValueError):
    """Raised when verification scheduling or evidence cannot be trusted."""


def _git_bytes(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError(f"Git query failed: git {' '.join(args)}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise VerificationError(
            f"Git query failed: git {' '.join(args)}"
            + (f": {detail}" if detail else "")
        )
    return result.stdout


def _nul_paths(payload: bytes) -> list[str]:
    return [os.fsdecode(item) for item in payload.split(b"\0") if item]


def repository_paths(root: Path = REPO_ROOT) -> tuple[str, ...]:
    """Return tracked and untracked non-ignored paths, including deletions."""
    payload = _git_bytes(
        root, "ls-files", "--cached", "--others", "--exclude-standard", "-z"
    )
    return tuple(sorted(set(_nul_paths(payload))))


def _valid_pattern(value: str) -> bool:
    path = Path(value)
    return (
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
    )


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate_manifest(
    manifest: dict[str, Any],
    *,
    root: Path = REPO_ROOT,
    inventory: Sequence[str] | None = None,
    require_coverage: bool = True,
) -> None:
    """Validate schema, domain ownership, patterns, and live path coverage."""
    errors = schema_errors(manifest, SCHEMA_PATH)
    if errors:
        raise VerificationError("\n".join(errors))

    domains = manifest["domains"]
    domain_names = set(domains)
    if tuple(domains) != REQUIRED_DOMAINS:
        raise VerificationError(
            "domains must use the canonical order: " + ", ".join(REQUIRED_DOMAINS)
        )
    hosted_jobs: set[str] = set()
    for name, info in domains.items():
        hosted_job = info["hosted_job"]
        if hosted_job in hosted_jobs:
            raise VerificationError(f"duplicate hosted job owner: {hosted_job}")
        hosted_jobs.add(hosted_job)

    rule_patterns: set[str] = set()
    for index, rule in enumerate(manifest["rules"]):
        unknown = sorted(set(rule["domains"]) - domain_names)
        if unknown:
            raise VerificationError(
                f"rule:{index} references unknown domains: {', '.join(unknown)}"
            )
        for pattern in rule["paths"]:
            if pattern in rule_patterns:
                raise VerificationError(f"duplicate change-path pattern: {pattern}")
            rule_patterns.add(pattern)

    invalid = sorted(
        pattern for pattern in rule_patterns if not _valid_pattern(pattern)
    )
    if invalid:
        raise VerificationError(f"invalid repository patterns: {', '.join(invalid)}")

    paths = tuple(inventory) if inventory is not None else repository_paths(root)
    unmatched = sorted(
        path
        for path in paths
        if not any(_matches(path, rule["paths"]) for rule in manifest["rules"])
    )
    if unmatched and require_coverage:
        raise VerificationError(
            "tracked/untracked paths lack an impact rule: " + ", ".join(unmatched)
        )


def load_manifest(
    path: Path = MANIFEST_PATH,
    *,
    root: Path = REPO_ROOT,
    inventory: Sequence[str] | None = None,
    require_coverage: bool = True,
) -> dict[str, Any]:
    try:
        manifest = read_strict_json(path)
    except ControlPlaneError as exc:
        raise VerificationError(str(exc)) from exc
    validate_manifest(
        manifest,
        root=root,
        inventory=inventory,
        require_coverage=require_coverage,
    )
    return manifest


@dataclass(frozen=True)
class ImpactPlan:
    """Deterministic validation schedule for a set of changed paths."""

    domains: tuple[str, ...]
    changed_paths: tuple[str, ...]
    unknown_paths: tuple[str, ...]
    failure_reasons: tuple[str, ...] = ()

    @property
    def fail_closed(self) -> bool:
        return bool(self.unknown_paths or self.failure_reasons)

    def as_dict(self, all_domains: Iterable[str]) -> dict[str, Any]:
        selected = set(self.domains)
        return {
            "schema_version": 1,
            "status": "all-domains" if self.fail_closed else "planned",
            "fail_closed": self.fail_closed,
            "domains": list(self.domains),
            "domain_flags": {name: name in selected for name in all_domains},
            "changed_paths": list(self.changed_paths),
            "unknown_paths": list(self.unknown_paths),
            "failure_reasons": list(self.failure_reasons),
        }


def classify_paths(
    paths: Iterable[str],
    manifest: dict[str, Any],
    *,
    failure_reasons: Iterable[str] = (),
) -> ImpactPlan:
    """Classify paths; any unknown path or upstream failure selects all domains."""
    normalized = tuple(sorted(set(path for path in paths if path)))
    selected: set[str] = set()
    unknown: list[str] = []
    for path in normalized:
        if not _valid_pattern(path):
            unknown.append(path)
            continue
        matched = False
        for rule in manifest["rules"]:
            if _matches(path, rule["paths"]):
                selected.update(rule["domains"])
                matched = True
        if not matched:
            unknown.append(path)

    failures = tuple(str(reason) for reason in failure_reasons if str(reason))
    if unknown or failures:
        selected = set(manifest["domains"])
    ordered = tuple(name for name in manifest["domains"] if name in selected)
    return ImpactPlan(ordered, normalized, tuple(sorted(unknown)), failures)


def changed_paths(
    *,
    root: Path = REPO_ROOT,
    base: str | None = None,
    head: str = "HEAD",
    include_worktree: bool = True,
) -> tuple[str, ...]:
    """Return the whole candidate delta plus optional staged/unstaged files."""
    resolved_base = base or os.environ.get("STRUCTURAL_LIB_BASE_REF", "origin/main")
    if not resolved_base or set(resolved_base) == {"0"}:
        raise VerificationError("base revision is missing or all-zero")
    changed = set(
        _nul_paths(
            _git_bytes(
                root,
                "diff",
                "--name-only",
                "--no-renames",
                "--diff-filter=ACDMRTUXB",
                "-z",
                f"{resolved_base}...{head}",
            )
        )
    )
    if include_worktree:
        changed.update(
            _nul_paths(
                _git_bytes(
                    root,
                    "diff",
                    "--name-only",
                    "--no-renames",
                    "--diff-filter=ACDMRTUXB",
                    "-z",
                    "HEAD",
                )
            )
        )
        changed.update(
            _nul_paths(
                _git_bytes(root, "ls-files", "--others", "--exclude-standard", "-z")
            )
        )
    return tuple(sorted(changed))


def plan_changes(
    manifest: dict[str, Any],
    *,
    root: Path = REPO_ROOT,
    base: str | None = None,
    head: str = "HEAD",
    include_worktree: bool = True,
    paths: Iterable[str] | None = None,
) -> ImpactPlan:
    if paths is not None:
        return classify_paths(paths, manifest)
    try:
        discovered = changed_paths(
            root=root, base=base, head=head, include_worktree=include_worktree
        )
    except VerificationError as exc:
        return classify_paths((), manifest, failure_reasons=(str(exc),))
    return classify_paths(discovered, manifest)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _runtime_identity(extra: bytes = b"") -> dict[str, Any]:
    distributions = sorted(
        {
            (
                (dist.metadata.get("Name") or "<unknown>").lower(),
                dist.version or "<unknown>",
            )
            for dist in importlib.metadata.distributions()
        }
    )
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "ci": os.environ.get("CI", ""),
        "github_actions": os.environ.get("GITHUB_ACTIONS", ""),
        "runner_os": os.environ.get("RUNNER_OS", ""),
        "runner_arch": os.environ.get("RUNNER_ARCH", ""),
        "runner_image_os": os.environ.get("ImageOS", ""),
        "runner_image_version": os.environ.get("ImageVersion", ""),
        "distributions": distributions,
        "extra_sha256": hashlib.sha256(extra).hexdigest(),
    }


def _normalize_command(command: Sequence[str], root: Path) -> tuple[str, ...]:
    normalized: list[str] = []
    resolved_root = root.resolve()
    for token in command:
        candidate = Path(token)
        if candidate.is_absolute():
            try:
                relative = candidate.resolve().relative_to(resolved_root)
            except (OSError, ValueError):
                normalized.append(token)
            else:
                normalized.append(f"./{relative.as_posix()}")
        else:
            normalized.append(token)
    return tuple(normalized)


@dataclass(frozen=True)
class EvidenceIdentity:
    fingerprint: str
    profile: str
    domains: tuple[str, ...]
    command: tuple[str, ...]
    runtime_digest: str
    input_count: int


class FingerprintContext:
    """Hash repository inputs once and derive many exact evidence identities."""

    def __init__(
        self,
        manifest: dict[str, Any],
        *,
        root: Path = REPO_ROOT,
        runtime_extra: bytes = b"",
        inventory: Sequence[str] | None = None,
    ) -> None:
        self.manifest = manifest
        self.root = root.resolve()
        self.inventory = (
            tuple(inventory) if inventory is not None else repository_paths(root)
        )
        runtime = _runtime_identity(runtime_extra)
        self.runtime_digest = hashlib.sha256(_canonical_bytes(runtime)).hexdigest()
        self._path_digest_cache: dict[str, str] = {}
        self._domain_paths_cache: dict[str, tuple[str, ...]] = {}
        self._unknown_paths = {
            path
            for path in self.inventory
            if not any(_matches(path, rule["paths"]) for rule in manifest["rules"])
        }

    def _path_digest(self, relative: str) -> str:
        cached = self._path_digest_cache.get(relative)
        if cached is not None:
            return cached
        path = self.root / relative
        if path.is_symlink():
            payload = b"symlink\0" + os.fsencode(os.readlink(path))
        elif path.is_file():
            payload = b"file\0" + path.read_bytes()
        elif path.exists():
            payload = b"non-file"
        else:
            payload = b"missing"
        digest = hashlib.sha256(payload).hexdigest()
        self._path_digest_cache[relative] = digest
        return digest

    def _paths_for_domain(self, domain: str) -> tuple[str, ...]:
        cached = self._domain_paths_cache.get(domain)
        if cached is not None:
            return cached
        patterns = [
            pattern
            for rule in self.manifest["rules"]
            if domain in rule["domains"]
            for pattern in rule["paths"]
        ]
        selected = tuple(
            path
            for path in self.inventory
            if path in self._unknown_paths or _matches(path, patterns)
        )
        self._domain_paths_cache[domain] = selected
        return selected

    def identity(
        self,
        *,
        profile: str,
        domains: Iterable[str],
        command: Sequence[str],
    ) -> EvidenceIdentity:
        domain_tuple = tuple(dict.fromkeys(domains))
        unknown = sorted(set(domain_tuple) - set(self.manifest["domains"]))
        if unknown:
            raise VerificationError(f"unknown evidence domains: {', '.join(unknown)}")
        selected_paths = sorted(
            {path for domain in domain_tuple for path in self._paths_for_domain(domain)}
        )
        normalized_command = _normalize_command(command, self.root)
        payload = {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "profile": profile,
            "domains": list(domain_tuple),
            "command": list(normalized_command),
            "runtime_digest": self.runtime_digest,
            "inputs": [[path, self._path_digest(path)] for path in selected_paths],
        }
        fingerprint = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
        return EvidenceIdentity(
            fingerprint=fingerprint,
            profile=profile,
            domains=domain_tuple,
            command=normalized_command,
            runtime_digest=self.runtime_digest,
            input_count=len(selected_paths),
        )


def local_evidence_path(root: Path, fingerprint: str) -> Path:
    if len(fingerprint) != 64 or any(
        char not in "0123456789abcdef" for char in fingerprint
    ):
        raise VerificationError("evidence fingerprint must be lowercase SHA-256")
    common_text = (
        _git_bytes(root, "rev-parse", "--git-common-dir")
        .decode("utf-8", errors="strict")
        .strip()
    )
    common = Path(common_text)
    if not common.is_absolute():
        common = root / common
    return common.resolve() / EVIDENCE_DIRECTORY / f"{fingerprint}.json"


def _receipt_payload(identity: EvidenceIdentity) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "status": "pass",
        "fingerprint": identity.fingerprint,
        "profile": identity.profile,
        "domains": list(identity.domains),
        "command": list(identity.command),
        "runtime_digest": identity.runtime_digest,
        "input_count": identity.input_count,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def probe_receipt(path: Path, identity: EvidenceIdentity) -> tuple[bool, str]:
    if not path.is_file() or path.is_symlink():
        return False, "receipt-missing"
    try:
        receipt = read_strict_json(path)
    except ControlPlaneError:
        return False, "receipt-malformed"
    expected_fields = set(_receipt_payload(identity))
    if set(receipt) != expected_fields:
        return False, "receipt-fields"
    expected = _receipt_payload(identity)
    expected.pop("observed_at_utc")
    actual = dict(receipt)
    observed = actual.pop("observed_at_utc", None)
    if not isinstance(observed, str) or not observed:
        return False, "receipt-time"
    if actual != expected:
        return False, "receipt-identity"
    return True, "exact-pass"


def write_receipt(path: Path, identity: EvidenceIdentity) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(_receipt_payload(identity), indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _cli_receipt_is_allowed(path: Path, identity: EvidenceIdentity) -> bool:
    resolved = path.resolve()
    try:
        if resolved == local_evidence_path(REPO_ROOT, identity.fingerprint):
            return True
    except VerificationError:
        pass
    runner_temp = os.environ.get("RUNNER_TEMP")
    if runner_temp:
        hosted_root = (Path(runner_temp) / "verification-evidence").resolve()
        try:
            resolved.relative_to(hosted_root)
        except ValueError:
            pass
        else:
            return True
    return False


def _write_github_output(path: Path, values: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if isinstance(value, bool):
                rendered = "true" if value else "false"
            elif isinstance(value, (dict, list, tuple)):
                rendered = json.dumps(value, separators=(",", ":"), sort_keys=True)
            else:
                rendered = str(value).replace("\n", " ")
            handle.write(f"{key}={rendered}\n")


def _runtime_extra(path: Path | None) -> bytes:
    if path is None:
        return b""
    try:
        return path.read_bytes()
    except OSError as exc:
        raise VerificationError(f"cannot read runtime identity file: {path}") from exc


def _identity_from_args(
    args: argparse.Namespace, manifest: dict[str, Any]
) -> EvidenceIdentity:
    context = FingerprintContext(
        manifest,
        runtime_extra=_runtime_extra(args.runtime_file),
    )
    return context.identity(
        profile=args.profile,
        domains=args.domain,
        command=args.identity_command or [args.profile],
    )


def _add_identity_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", required=True)
    parser.add_argument("--domain", action="append", required=True)
    parser.add_argument("--identity-command", action="append")
    parser.add_argument("--runtime-file", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser(
        "validate", help="Validate manifest and live path coverage"
    )
    validate.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan", help="Classify changed paths into validation domains")
    plan.add_argument("--base")
    plan.add_argument("--head", default="HEAD")
    plan.add_argument("--no-worktree", action="store_true")
    plan.add_argument("--path", action="append", dest="paths")
    plan.add_argument("--json", action="store_true")
    plan.add_argument("--github-output", type=Path)

    fingerprint = sub.add_parser(
        "fingerprint", help="Compute an exact evidence identity"
    )
    _add_identity_args(fingerprint)
    fingerprint.add_argument("--json", action="store_true")
    fingerprint.add_argument("--github-output", type=Path)

    probe = sub.add_parser(
        "probe", help="Probe an exact PASS receipt without failing on a miss"
    )
    _add_identity_args(probe)
    probe.add_argument("--receipt", type=Path, required=True)
    probe.add_argument("--github-output", type=Path)

    record = sub.add_parser("record", help="Record PASS for the exact current identity")
    _add_identity_args(record)
    record.add_argument("--receipt", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(require_coverage=args.command == "validate")
        if args.command == "validate":
            result = {
                "status": "pass",
                "schema_version": manifest["schema_version"],
                "domains": list(manifest["domains"]),
                "rules": len(manifest["rules"]),
                "unknown_impact": manifest["metadata"]["unknown_impact"],
            }
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(
                    "Verification manifest: PASS "
                    f"({len(manifest['domains'])} domains; {len(manifest['rules'])} rules; unknown -> all)"
                )
            return 0

        if args.command == "plan":
            plan = plan_changes(
                manifest,
                base=args.base,
                head=args.head,
                include_worktree=not args.no_worktree,
                paths=args.paths,
            )
            result = plan.as_dict(manifest["domains"])
            if args.github_output:
                outputs = {**result["domain_flags"]}
                outputs.update(
                    {
                        "fail_closed": plan.fail_closed,
                        "changed_paths": list(plan.changed_paths),
                        "unknown_paths": list(plan.unknown_paths),
                        "failure_reasons": list(plan.failure_reasons),
                    }
                )
                _write_github_output(args.github_output, outputs)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                label = ", ".join(plan.domains) or "none"
                print(f"Verification domains: {label}")
                if plan.fail_closed:
                    print("Fail-closed reason: unknown impact selected every domain")
            return 0

        identity = _identity_from_args(args, manifest)
        identity_result = {
            "fingerprint": identity.fingerprint,
            "profile": identity.profile,
            "domains": list(identity.domains),
            "runtime_digest": identity.runtime_digest,
            "input_count": identity.input_count,
        }
        if args.command == "fingerprint":
            if args.github_output:
                _write_github_output(args.github_output, identity_result)
            if args.json:
                print(json.dumps(identity_result, indent=2))
            else:
                print(identity.fingerprint)
            return 0
        if args.command == "probe":
            valid, reason = probe_receipt(args.receipt, identity)
            result = {**identity_result, "valid": valid, "reason": reason}
            if args.github_output:
                _write_github_output(args.github_output, result)
            print(json.dumps(result, indent=2))
            return 0
        if args.command == "record":
            if not _cli_receipt_is_allowed(args.receipt, identity):
                raise VerificationError(
                    "receipt writes are limited to the Git-common evidence store "
                    "or RUNNER_TEMP/verification-evidence"
                )
            write_receipt(args.receipt, identity)
            print(f"Recorded exact PASS evidence: {args.receipt}")
            return 0
    except VerificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
