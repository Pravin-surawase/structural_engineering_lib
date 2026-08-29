#!/usr/bin/env python3
"""Select and run the healthy Node.js major pinned by ``.nvmrc``.

This is the repository-owned Node boundary for developer commands. It avoids
assuming that ``nvm`` is installed or that the first ``node``/``npm`` on PATH
matches the project runtime.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def required_node_major(repo_root: Path = REPO_ROOT) -> str | None:
    """Return the Node major pinned by ``.nvmrc``, if present."""
    nvmrc = repo_root / ".nvmrc"
    if not nvmrc.exists():
        return None
    match = re.search(r"\d+", nvmrc.read_text(encoding="utf-8"))
    return match.group(0) if match else None


def node_bin_candidates(required_major: str) -> list[Path]:
    """Return plausible binary directories in deterministic preference order."""
    candidates: list[Path] = []
    brew = shutil.which("brew")
    if brew:
        try:
            result = subprocess.run(
                [brew, "--prefix", f"node@{required_major}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, OSError):
            result = None
        if result is not None and result.returncode == 0 and result.stdout.strip():
            candidates.append(Path(result.stdout.strip()) / "bin")

    candidates.extend(
        [
            Path(f"/opt/homebrew/opt/node@{required_major}/bin"),
            Path(f"/usr/local/opt/node@{required_major}/bin"),
        ]
    )
    current_node = shutil.which("node")
    if current_node:
        candidates.append(Path(current_node).parent)
    candidates.extend(
        path / "bin"
        for path in sorted(
            (Path.home() / ".nvm" / "versions" / "node").glob(f"v{required_major}.*"),
            reverse=True,
        )
    )
    return candidates


def node_runtime_env(
    *,
    repo_root: Path = REPO_ROOT,
    required_major: str | None = None,
    candidate_bins: list[Path] | None = None,
) -> tuple[dict[str, str] | None, str]:
    """Return an environment using the pinned healthy Node/npm pair."""
    pinned_major = required_major or required_node_major(repo_root)
    if not pinned_major:
        return dict(os.environ), "Node version not pinned"

    candidates = (
        node_bin_candidates(pinned_major) if candidate_bins is None else candidate_bins
    )
    seen: set[Path] = set()
    for bin_dir in candidates:
        resolved = bin_dir.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        node_path = shutil.which("node", path=str(resolved))
        npm_path = shutil.which("npm", path=str(resolved))
        if not node_path or not npm_path:
            continue
        try:
            result = subprocess.run(
                [node_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        match = re.search(r"v?(\d+)", result.stdout.strip())
        if result.returncode == 0 and match and match.group(1) == pinned_major:
            env = dict(os.environ)
            env["PATH"] = str(resolved) + os.pathsep + env.get("PATH", "")
            return env, result.stdout.strip()

    return None, f"Node {pinned_major}.x from .nvmrc is not available"


def _resolve_cwd(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise ValueError(f"Working directory does not exist: {resolved}")
    return resolved


def _selected_bin_dir(env: dict[str, str]) -> Path:
    """Return the directory containing the selected Node executable."""
    node = shutil.which("node", path=env.get("PATH", ""))
    if not node:
        raise ValueError("Node executable is missing from the selected environment")
    return Path(node).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a command with the Node.js major pinned by .nvmrc"
    )
    parser.add_argument(
        "--cwd",
        default=str(REPO_ROOT),
        help="Command working directory, relative to the repository root by default",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="show_runtime",
        help="Print the selected Node and npm versions without running a command",
    )
    parser.add_argument(
        "--bin-dir",
        action="store_true",
        help="Print only the selected Node binary directory",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    env, status = node_runtime_env()
    if env is None:
        print(f"ERROR: {status}", file=sys.stderr)
        print("Install the .nvmrc major with nvm or Homebrew.", file=sys.stderr)
        return 1

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]

    try:
        bin_dir = _selected_bin_dir(env)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.bin_dir:
        print(bin_dir)
        return 0

    if args.show_runtime or not command:
        npm = shutil.which("npm", path=env.get("PATH", ""))
        if not npm:
            print("ERROR: npm is missing from the selected Node environment", file=sys.stderr)
            return 1
        npm_result = subprocess.run(
            [npm, "--version"],
            capture_output=True,
            text=True,
            env=env,
            timeout=10,
        )
        npm_version = (
            npm_result.stdout.strip() if npm_result.returncode == 0 else "unavailable"
        )
        print(f"Node runtime: {status}")
        print(f"npm runtime: {npm_version}")
        print(f"Binary directory: {bin_dir}")
        return 0

    try:
        cwd = _resolve_cwd(args.cwd)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        executable = shutil.which(command[0], path=env.get("PATH", ""))
        if executable:
            command[0] = executable
        result = subprocess.run(command, cwd=cwd, env=env)
    except FileNotFoundError:
        print(
            f"ERROR: Command not found in selected Node environment: {command[0]}",
            file=sys.stderr,
        )
        return 127
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
