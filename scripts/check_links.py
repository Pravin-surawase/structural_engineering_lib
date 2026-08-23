#!/usr/bin/env python3
"""Validate local Markdown links and images; repair only explicit or unique targets."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import PRESERVED_REFERENCE_FILES, iter_repository_files
from _lib.utils import REPO_ROOT

SKIP_LINK_PATTERNS = [
    r"^text$",
    r"^Link \d+$",
    r"^\$\w+$",
    r"^\.\*",
    r"^\'.*\'$",
    r"^path/to/",
    r"^target\.md$",
    r"^old-file\.md",
    r"^Old_File\.md",
    r"^file\.md",
]
HISTORICAL_DIRECTORIES = ("docs/_archive", "agents/agent-9")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")


def _is_placeholder(text: str, target: str) -> bool:
    return any(
        re.search(pattern, text, re.IGNORECASE)
        or re.search(pattern, target, re.IGNORECASE)
        for pattern in SKIP_LINK_PATTERNS
    )


def _is_historical(file: Path, root: Path) -> bool:
    relative = file.relative_to(root).as_posix()
    return relative in PRESERVED_REFERENCE_FILES or any(
        relative == prefix or relative.startswith(f"{prefix}/")
        for prefix in HISTORICAL_DIRECTORIES
    )


def _find_links(content: str) -> list[tuple[str, str, str, int]]:
    """Return (kind, label, target, position) for links and images."""
    content = re.sub(
        r"```.*?```",
        lambda match: "\n" * match.group(0).count("\n"),
        content,
        flags=re.DOTALL,
    )
    content = re.sub(r"`[^`\n]*`", "", content)
    return [
        (
            "image" if match.group(1) else "link",
            match.group(2),
            match.group(3),
            match.start(),
        )
        for match in LINK_RE.finditer(content)
    ]


def _target_path(target: str) -> str:
    stripped = target.strip()
    if stripped.startswith("<"):
        close = stripped.find(">")
        return stripped[1:close] if close > 0 else stripped
    return stripped.split(maxsplit=1)[0]


def _is_external(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(
        ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")
    )


def _resolve_local_target(source_file: Path, target_path: str, root: Path) -> Path:
    decoded = unquote(target_path.split("#", 1)[0])
    if decoded.startswith("/"):
        return (root / decoded.lstrip("/")).resolve(strict=False)
    return (source_file.parent / decoded).resolve(strict=False)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _build_file_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for file in iter_repository_files(root):
        index[file.name.lower()].append(file)
    return index


def _normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def _find_unique_match(
    target_path: str, file_index: dict[str, list[Path]]
) -> Path | None:
    """Return a suggestion only when all matching strategies identify one file."""
    target = Path(unquote(target_path))
    filename = target.name.lower()
    candidates: set[Path] = set(file_index.get(filename, []))
    if not candidates:
        normalized = _normalize(filename)
        for indexed_name, paths in file_index.items():
            if _normalize(indexed_name) == normalized:
                candidates.update(paths)
    if not candidates:
        stem = _normalize(target.stem)
        for indexed_name, paths in file_index.items():
            if _normalize(Path(indexed_name).stem) == stem:
                candidates.update(paths)
    return next(iter(candidates)) if len(candidates) == 1 else None


def _relative_path(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file, start=from_file.parent)).as_posix()


def _mapped_suggestion(
    *,
    link_map: dict[str, str],
    source_file: Path,
    target_path: str,
    root: Path,
) -> str | None:
    file_key = f"{source_file.relative_to(root).as_posix()}::{target_path}"
    mapped = link_map.get(file_key, link_map.get(target_path))
    if mapped is None:
        return None
    literal = _resolve_local_target(source_file, mapped, root)
    if _inside(literal, root) and literal.exists():
        return mapped
    repo_candidate = (root / mapped.lstrip("/")).resolve(strict=False)
    if _inside(repo_candidate, root) and repo_candidate.exists():
        return (
            f"/{repo_candidate.relative_to(root).as_posix()}"
            if mapped.startswith("/")
            else _relative_path(source_file, repo_candidate)
        )
    raise ValueError(f"Mapping target does not exist for {file_key}: {mapped}")


def _markdown_files(
    root: Path, *, include_historical: bool, exclude_archive: bool
) -> list[Path]:
    files = iter_repository_files(root, {".md"})
    if not include_historical or exclude_archive:
        files = [file for file in files if not _is_historical(file, root)]
    return files


def scan_links(
    *,
    root: Path = REPO_ROOT,
    suggest: bool = False,
    link_map: dict[str, str] | None = None,
    include_historical: bool = False,
    exclude_archive: bool = False,
) -> dict[str, object]:
    file_index = _build_file_index(root) if suggest else {}
    broken_links: list[dict[str, object]] = []
    file_count = 0
    link_count = 0
    image_count = 0

    for markdown_file in _markdown_files(
        root,
        include_historical=include_historical,
        exclude_archive=exclude_archive,
    ):
        file_count += 1
        content = markdown_file.read_text(encoding="utf-8")
        for kind, label, raw_target, _position in _find_links(content):
            target = _target_path(raw_target)
            if _is_external(target) or _is_placeholder(label, target):
                continue
            if kind == "image":
                image_count += 1
            else:
                link_count += 1
            path_part, marker, fragment = target.partition("#")
            if not path_part:
                continue
            resolved = _resolve_local_target(markdown_file, target, root)
            reason = None
            if not _inside(resolved, root):
                reason = "outside_repository"
            elif not resolved.exists():
                reason = "missing"
            if reason is None:
                continue

            suggestion = None
            if link_map:
                suggestion = _mapped_suggestion(
                    link_map=link_map,
                    source_file=markdown_file,
                    target_path=path_part,
                    root=root,
                )
            if suggestion is None and suggest:
                match = _find_unique_match(path_part, file_index)
                if match is not None:
                    suggestion = _relative_path(markdown_file, match)
            if suggestion and marker:
                suggestion = f"{suggestion}#{fragment}"
            broken_links.append(
                {
                    "file": markdown_file.relative_to(root).as_posix(),
                    "kind": kind,
                    "label": label,
                    "target": raw_target,
                    "target_path": path_part,
                    "reason": reason,
                    "suggestion": suggestion,
                }
            )

    return {
        "tool": "check_links",
        "schema_version": 1,
        "files_checked": file_count,
        "links_checked": link_count,
        "images_checked": image_count,
        "broken_count": len(broken_links),
        "broken_links": broken_links,
        "success": not broken_links,
    }


def _apply_fixes(payload: dict[str, object], root: Path) -> int:
    broken_links = payload["broken_links"]
    assert isinstance(broken_links, list)
    by_file: dict[Path, list[dict[str, object]]] = defaultdict(list)
    for item in broken_links:
        if isinstance(item, dict) and item.get("suggestion"):
            by_file[root / str(item["file"])].append(item)
    for file, items in by_file.items():
        content = file.read_text(encoding="utf-8")
        for item in items:
            old = str(item["target"])
            new = str(item["suggestion"])
            content = content.replace(f"]({old})", f"]({new})")
        file.write_text(content, encoding="utf-8")
    return sum(len(items) for items in by_file.values())


def check_and_fix(
    *,
    fix: bool = False,
    verbose: bool = False,
    link_map: dict[str, str] | None = None,
    exclude_archive: bool = False,
    include_historical: bool = False,
    root: Path = REPO_ROOT,
) -> tuple[int, dict[str, object]]:
    payload = scan_links(
        root=root,
        suggest=fix,
        link_map=link_map,
        include_historical=include_historical,
        exclude_archive=exclude_archive,
    )
    if fix and payload["broken_count"]:
        payload["fixed_count"] = _apply_fixes(payload, root)
        verified = scan_links(
            root=root,
            suggest=False,
            link_map=None,
            include_historical=include_historical,
            exclude_archive=exclude_archive,
        )
        payload["remaining_broken_count"] = verified["broken_count"]
        payload["broken_links"] = verified["broken_links"]
        payload["broken_count"] = verified["broken_count"]
        payload["success"] = verified["success"]
    else:
        payload["fixed_count"] = 0

    print(f"\n🔍 Checked {payload['files_checked']} Markdown files")
    print(f"   Local links: {payload['links_checked']}")
    print(f"   Local images: {payload['images_checked']}")
    print(f"   Broken links: {payload['broken_count']}\n")
    broken = payload["broken_links"]
    assert isinstance(broken, list)
    for item in broken:
        if not isinstance(item, dict):
            continue
        print(f"❌ {item['file']} [{item['kind']}]")
        print(f"   {item['target']} ({item['reason']})")
        if item.get("suggestion"):
            print(f"   💡 {item['suggestion']}")
        if not verbose and len(broken) > 20 and broken.index(item) >= 19:
            print(f"   ... and {len(broken) - 20} more")
            break
    if payload["success"]:
        print("✅ All maintained local links and images are valid.")
        return 0, payload
    if fix:
        print(f"⚠️  {payload['broken_count']} broken references remain unresolved.")
    return 1, payload


def _load_map(path_text: str | None) -> dict[str, str] | None:
    if path_text is None:
        return None
    path = Path(path_text)
    if not path.is_file():
        raise ValueError(f"Mapping file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in data.items()
    ):
        raise ValueError("Mapping JSON must be an object of string paths")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local Markdown links and images"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Repair explicit mappings or uniquely matched targets",
    )
    parser.add_argument("--map", help="Explicit old-to-new target mapping JSON")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--include-historical",
        action="store_true",
        help="Also scan archived and legacy-agent evidence",
    )
    parser.add_argument(
        "--exclude-archive",
        action="store_true",
        help="Compatibility option: exclude historical archive surfaces",
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    try:
        link_map = _load_map(args.map)
        if link_map is not None and not args.fix:
            raise ValueError("--map requires --fix")
        if args.json:
            with contextlib.redirect_stdout(sys.stderr):
                exit_code, payload = check_and_fix(
                    fix=args.fix,
                    verbose=args.verbose,
                    link_map=link_map,
                    exclude_archive=args.exclude_archive,
                    include_historical=args.include_historical,
                )
            print(json.dumps(payload, indent=2))
            return exit_code
        exit_code, _payload = check_and_fix(
            fix=args.fix,
            verbose=args.verbose,
            link_map=link_map,
            exclude_archive=args.exclude_archive,
            include_historical=args.include_historical,
        )
        return exit_code
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if args.json:
            print(
                json.dumps(
                    {
                        "tool": "check_links",
                        "schema_version": 1,
                        "success": False,
                        "broken_links": [],
                        "error": str(exc),
                    },
                    indent=2,
                )
            )
        else:
            print(f"❌ {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
