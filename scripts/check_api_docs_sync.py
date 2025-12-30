#!/usr/bin/env python3
"""Validate api-stability.md and api.md mention the same api.* symbols."""

from __future__ import annotations

from pathlib import Path
import re

API_DOC = Path("docs/reference/api.md")
STABILITY_DOC = Path("docs/reference/api-stability.md")

API_RE = re.compile(r"\bapi\.[a-zA-Z_][a-zA-Z0-9_]*")


def _extract(path: Path) -> set[str]:
    symbols = set(API_RE.findall(path.read_text(encoding="utf-8")))
    # Ignore file references like api.py
    return {s for s in symbols if s != "api.py"}


def _is_documented(api_doc_text: str, symbol: str) -> bool:
    name = symbol.split(".", 1)[1]
    if symbol in api_doc_text:
        return True
    # Allow headings or signatures that mention the function name without api.
    pattern = re.compile(rf"\b{name}\b")
    return pattern.search(api_doc_text) is not None


def main() -> int:
    if not API_DOC.exists():
        print("ERROR: docs/reference/api.md not found")
        return 1
    if not STABILITY_DOC.exists():
        print("ERROR: docs/reference/api-stability.md not found")
        return 1

    api_doc_text = API_DOC.read_text(encoding="utf-8")
    api_doc_symbols = _extract(API_DOC)
    stability_symbols = _extract(STABILITY_DOC)

    if not stability_symbols:
        print("ERROR: No api.* symbols found in api-stability.md")
        return 1

    missing_in_api_doc = [
        symbol for symbol in sorted(stability_symbols)
        if not _is_documented(api_doc_text, symbol)
    ]

    missing_in_stability = sorted(api_doc_symbols - stability_symbols)

    if missing_in_api_doc:
        print("ERROR: Symbols in api-stability.md missing from api.md:")
        for symbol in missing_in_api_doc:
            print(f"  - {symbol}")
        return 1

    if missing_in_stability:
        print("ERROR: Symbols in api.md missing from api-stability.md:")
        for symbol in missing_in_stability:
            print(f"  - {symbol}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
