#!/usr/bin/env python3
"""Validate the live React/FastAPI contract and Python API documentation.

The contract lane scans production TypeScript/TSX call sites and verifies each
internal fetch/EventSource path and HTTP method against FastAPI's generated
OpenAPI schema. It fails closed when no source files or call sites are found.

Usage:
    .venv/bin/python scripts/check_api.py
    .venv/bin/python scripts/check_api.py --signatures
    .venv/bin/python scripts/check_api.py --docs
    .venv/bin/python scripts/check_api.py --sync
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
SOURCE_SUFFIXES = {".ts", ".tsx"}
CALL_RE = re.compile(
    r"\b(?P<kind>fetch|new\s+EventSource)\s*\(\s*"
    r"(?P<target>`[^`]*`|'[^']*'|\"[^\"]*\"|[A-Za-z_$][\w$]*)",
    re.DOTALL,
)
ENDPOINT_RE = re.compile(
    r"/(?:api/v1|health|stream)(?:/(?:[A-Za-z0-9._~-]+|\$\{[^}]+\}))*"
)


@dataclass(frozen=True)
class CallSite:
    file: Path
    line: int
    method: str
    endpoint: str


def _is_production_source(path: Path) -> bool:
    """Return True for production TypeScript/TSX sources."""
    if path.suffix not in SOURCE_SUFFIXES:
        return False
    if "__tests__" in path.parts:
        return False
    return not any(token in path.name for token in (".test.", ".spec."))


def _resolve_identifier(source: str, name: str, before: int) -> str | None:
    """Resolve the nearest preceding const/let assignment for a fetch target."""
    assignment = re.compile(
        rf"\b(?:const|let)\s+{re.escape(name)}\s*=\s*(?P<expr>.*?);",
        re.DOTALL,
    )
    matches = [match for match in assignment.finditer(source, 0, before)]
    return matches[-1].group("expr") if matches else None


def _extract_endpoint(expression: str) -> str | None:
    """Extract and normalize an internal endpoint from a JS expression."""
    match = ENDPOINT_RE.search(expression)
    if not match:
        return None
    endpoint = match.group(0).rstrip("/") or "/"
    return re.sub(r"\$\{[^}]+\}", "{dynamic}", endpoint)


def _call_expression_end(source: str, open_paren: int) -> int:
    """Return the matching close parenthesis without crossing into the next call."""
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(open_paren, len(source)):
        character = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in "'\"`":
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index
    return len(source)


def _extract_call_sites(path: Path) -> tuple[list[CallSite], list[str]]:
    """Extract internal HTTP/SSE call sites and unresolved internal targets."""
    source = path.read_text(encoding="utf-8")
    calls: list[CallSite] = []
    unresolved: list[str] = []

    for match in CALL_RE.finditer(source):
        kind = match.group("kind")
        target = match.group("target")
        expression = target
        if target[0] not in "`'\"":
            resolved = _resolve_identifier(source, target, match.start())
            if resolved is None:
                line = source.count("\n", 0, match.start()) + 1
                unresolved.append(f"{path.relative_to(REPO_ROOT)}:{line}: {target}")
                continue
            expression = resolved

        endpoint = _extract_endpoint(expression)
        if endpoint is None:
            # Literal external fetches are outside this internal contract. A
            # variable target is ambiguous and therefore fails closed.
            if target[0] not in "`'\"":
                line = source.count("\n", 0, match.start()) + 1
                unresolved.append(f"{path.relative_to(REPO_ROOT)}:{line}: {target}")
            continue

        method = "GET"
        if kind == "fetch":
            open_paren = source.find("(", match.start(), match.end())
            call_end = _call_expression_end(source, open_paren)
            tail = source[match.end() : call_end]
            if tail.lstrip().startswith(","):
                method_match = re.search(
                    r"\bmethod\s*:\s*['\"](?P<method>[A-Za-z]+)['\"]", tail
                )
                if method_match:
                    method = method_match.group("method").upper()

        line = source.count("\n", 0, match.start()) + 1
        calls.append(CallSite(path, line, method, endpoint))

    return calls, unresolved


def _load_openapi_routes() -> dict[str, set[str]]:
    """Load route methods from the live FastAPI application."""
    sys.path.insert(0, str(REPO_ROOT))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi_app.main import app

    schema = app.openapi()
    routes: dict[str, set[str]] = {}
    for path, operations in schema.get("paths", {}).items():
        routes[path.rstrip("/") or "/"] = {
            method.upper() for method in operations if method in HTTP_METHODS
        }
    return routes


def _same_route_shape(client_path: str, server_path: str) -> bool:
    """Match paths while treating client/server template segments as wildcards."""
    client_segments = client_path.strip("/").split("/")
    server_segments = server_path.strip("/").split("/")
    if len(client_segments) != len(server_segments):
        return False
    for client, server in zip(client_segments, server_segments):
        if client.startswith("{") or server.startswith("{"):
            continue
        if client != server:
            return False
    return True


def check_signatures(
    files: list[str] | None = None,
    pages_dir: str = "react_app/src",
    show_fix: bool = False,
) -> int:
    """Validate production React HTTP/SSE calls against FastAPI OpenAPI."""
    source_root = REPO_ROOT / pages_dir
    if not source_root.is_dir():
        print(f"ERROR: Source directory not found: {source_root}")
        return 1

    if files:
        candidates: list[Path] = []
        for value in files:
            path = Path(value)
            if not path.is_absolute():
                direct = REPO_ROOT / path
                path = direct if direct.exists() else source_root / path
            if path.exists() and _is_production_source(path):
                candidates.append(path)
    else:
        candidates = [
            path for path in source_root.rglob("*") if _is_production_source(path)
        ]

    if not candidates:
        print("ERROR: No production TypeScript/TSX files were scanned")
        return 1

    call_sites: list[CallSite] = []
    unresolved: list[str] = []
    for path in sorted(set(candidates)):
        calls, unknown = _extract_call_sites(path)
        call_sites.extend(calls)
        unresolved.extend(unknown)

    if not call_sites:
        print(
            "ERROR: No internal React API call sites were found; refusing vacuous pass"
        )
        return 1

    try:
        routes = _load_openapi_routes()
    except Exception as exc:  # pragma: no cover - environment-specific import failure
        print(f"ERROR: Cannot load FastAPI OpenAPI schema: {exc}")
        return 1

    mismatches: list[tuple[CallSite, list[str]]] = []
    for call in call_sites:
        shaped = [route for route in routes if _same_route_shape(call.endpoint, route)]
        matching = [route for route in shaped if call.method in routes[route]]
        if not matching:
            mismatches.append((call, shaped))

    if unresolved:
        print("ERROR: Internal fetch targets could not be resolved:")
        for item in unresolved:
            print(f"  - {item}")

    if mismatches:
        print("ERROR: React call sites missing from the FastAPI OpenAPI contract:")
        for call, shaped in mismatches:
            relative = call.file.relative_to(REPO_ROOT)
            print(f"  - {relative}:{call.line}: {call.method} {call.endpoint}")
            if show_fix and shaped:
                options = ", ".join(
                    f"{route} [{'/'.join(sorted(routes[route]))}]" for route in shaped
                )
                print(f"    path candidates: {options}")

    if unresolved or mismatches:
        return 1

    files_with_calls = len({call.file for call in call_sites})
    print(
        "✅ React/FastAPI contract: "
        f"{len(call_sites)} call site(s) across {files_with_calls} file(s) "
        f"matched {len(routes)} OpenAPI path(s)"
    )
    return 0


def check_docs() -> int:
    """Ensure public Python API symbols are documented in api.md."""
    doc_path = REPO_ROOT / "docs/reference/api.md"
    if not doc_path.exists():
        print("ERROR: docs/reference/api.md not found")
        return 1
    doc_text = doc_path.read_text(encoding="utf-8")
    documented = set(re.findall(r"\bapi\.([A-Za-z_][A-Za-z0-9_]*)", doc_text))
    documented.update(
        re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", doc_text, re.MULTILINE)
    )

    sys.path.insert(0, str(REPO_ROOT / "Python"))
    try:
        from structural_lib import api  # type: ignore
    except ImportError as exc:
        print(f"ERROR: Cannot import structural_lib.api: {exc}")
        return 1

    exported = [
        name for name in getattr(api, "__all__", []) if not name.startswith("_")
    ]
    missing = [name for name in exported if name not in documented]
    if missing:
        print("ERROR: api.__all__ symbols missing from docs/reference/api.md:")
        for name in missing:
            print(f"  - {name}")
        return 1
    print("✅ All api.__all__ symbols documented in api.md")
    return 0


API_SYMBOL_RE = re.compile(r"\bapi\.[A-Za-z_][A-Za-z0-9_]*")


def _extract_symbols(path: Path) -> set[str]:
    symbols = set(API_SYMBOL_RE.findall(path.read_text(encoding="utf-8")))
    return {symbol for symbol in symbols if symbol not in {"api.py", "api.md"}}


def check_sync() -> int:
    """Validate documented compatibility symbols against the registry."""
    api_doc = REPO_ROOT / "docs/reference/api.md"
    stability_doc = REPO_ROOT / "docs/reference/api-stability.md"
    registry_path = REPO_ROOT / "docs/reference/api-classification.json"
    if not api_doc.exists() or not stability_doc.exists() or not registry_path.exists():
        print("ERROR: API docs or classification registry not found")
        return 1

    stability_text = stability_doc.read_text(encoding="utf-8")
    if "api-classification.json" not in stability_text:
        print("ERROR: api-stability.md does not bind the classification registry")
        return 1

    api_symbols = _extract_symbols(api_doc)
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot load API classification registry: {exc}")
        return 1
    surfaces = registry.get("surfaces")
    compatibility = next(
        (
            surface
            for surface in surfaces or []
            if surface.get("module") == "structural_lib.api"
        ),
        None,
    )
    if not isinstance(compatibility, dict):
        print("ERROR: structural_lib.api classification surface is missing")
        return 1
    classified = {
        f"api.{symbol['name']}"
        for symbol in compatibility.get("symbols", [])
        if isinstance(symbol, dict) and isinstance(symbol.get("name"), str)
    }
    unclassified = sorted(api_symbols - classified)
    if unclassified:
        print("ERROR: api.md symbols missing from API classification registry:")
        for symbol in unclassified:
            print(f"  - {symbol}")
        return 1

    print("✅ api.md symbols are bound to api-classification.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate React/FastAPI contracts and Python API documentation"
    )
    group = parser.add_argument_group("Check selectors (default: --all)")
    group.add_argument(
        "--signatures",
        action="store_true",
        help="Check production React call sites against FastAPI OpenAPI",
    )
    group.add_argument(
        "--docs", action="store_true", help="Check api.__all__ in api.md"
    )
    group.add_argument(
        "--sync", action="store_true", help="Check API doc symbol parity"
    )
    group.add_argument("--all", action="store_true", help="Run all checks")

    contract = parser.add_argument_group("Contract options")
    contract.add_argument(
        "--pages-dir", default="react_app/src", help="React source directory"
    )
    contract.add_argument(
        "--fix", action="store_true", help="Show route candidates for mismatches"
    )
    contract.add_argument("files", nargs="*", help="Specific TS/TSX files to scan")

    args = parser.parse_args()
    run_all = args.all or not any((args.signatures, args.docs, args.sync))
    results: list[int] = []

    if run_all or args.signatures:
        print("⚙️  Checking React/FastAPI contract...")
        results.append(check_signatures(args.files or None, args.pages_dir, args.fix))
    if run_all or args.docs:
        print("📖 Checking api.__all__ documentation...")
        results.append(check_docs())
    if run_all or args.sync:
        print("🔄 Checking api.md ↔ api-stability.md sync...")
        results.append(check_sync())

    failed = sum(result != 0 for result in results)
    print(f"\n{'=' * 40}")
    if failed:
        print(f"❌ {failed}/{len(results)} API check(s) failed")
        return 1
    print(f"✅ All {len(results)} API check(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
