# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
IS 456 Traceability Module
==========================

Provides the @clause decorator and traceability API for IS 456:2000 compliance.

This module enables:
- Marking functions with IS 456 clause references via @clause decorator
- Querying clause references by function name
- Generating traceability reports
- CLI lookups for clause information

Example:
    >>> from structural_lib.codes.is456.traceability import clause, get_clause_refs
    >>> @clause("38.1", "40.1")
    ... def my_design_function(b, d, fck):
    ...     pass
    >>> get_clause_refs(my_design_function)
    ['38.1', '40.1']

Author: ARCHITECT Agent
Version: 1.0.0
"""

from __future__ import annotations

import functools
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

_logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])

# Module-level registry for clause references
_CLAUSE_REGISTRY: dict[str, list[str]] = {}

# Cached clause database
_CLAUSE_DB: dict[str, Any] | None = None


def _load_clause_database() -> dict[str, Any]:
    """Load the IS 456 clause database from JSON file.

    Returns:
        dict: The clause database containing all IS 456 clauses.

    Raises:
        FileNotFoundError: If clauses.json is not found.
        json.JSONDecodeError: If clauses.json is invalid.
    """
    global _CLAUSE_DB

    if _CLAUSE_DB is not None:
        return _CLAUSE_DB

    db_path = Path(__file__).parent / "clauses.json"
    if not db_path.exists():
        raise FileNotFoundError(
            f"Clause database not found: {db_path}. "
            "Ensure clauses.json exists in the is456 module directory."
        )

    with open(db_path, encoding="utf-8") as f:
        _CLAUSE_DB = json.load(f)

    _logger.debug("Loaded %d clauses from database", len(_CLAUSE_DB.get("clauses", {})))
    return _CLAUSE_DB


def clause(*clause_refs: str) -> Callable[[F], F]:
    """Decorator to mark a function with IS 456 clause references.

    This decorator adds traceability metadata to functions, linking them
    to specific IS 456:2000 clauses. The clause references are stored
    in a registry and can be queried via get_clause_refs().

    Args:
        *clause_refs: One or more clause reference strings (e.g., "38.1", "40.1").

    Returns:
        A decorator function that adds clause metadata.

    Example:
        >>> @clause("38.1", "38.2")
        ... def calculate_flexure(b, d, fck, fy, Mu):
        ...     '''Calculate flexural reinforcement per IS 456 Cl. 38.'''
        ...     pass

    Note:
        Clause references should match keys in clauses.json for validation.
        Invalid references will log a warning but won't raise an error.
    """

    def decorator(func: F) -> F:
        # Store clause references in function attribute
        existing = getattr(func, "_is456_clauses", [])
        all_clauses = list(existing) + list(clause_refs)
        func._is456_clauses = all_clauses  # type: ignore[attr-defined]

        # Register in module-level registry using qualified name
        func_key = f"{func.__module__}.{func.__qualname__}"
        _CLAUSE_REGISTRY[func_key] = all_clauses

        # Validate clause references exist in database (warn only)
        try:
            db = _load_clause_database()
            # Combine clauses and annexure keys for validation
            known_clauses = set(db.get("clauses", {}).keys())
            known_clauses.update(db.get("annexures", {}).keys())
            for ref in clause_refs:
                if ref not in known_clauses:
                    _logger.warning(
                        "Unknown clause reference '%s' in function '%s'. "
                        "Clause not found in IS 456 database.",
                        ref,
                        func_key,
                    )
        except FileNotFoundError:
            _logger.debug("Clause database not available for validation")

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Preserve clause metadata on wrapper
        wrapper._is456_clauses = all_clauses  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def get_clause_refs(func: Callable[..., Any] | str) -> list[str]:
    """Get IS 456 clause references for a function.

    Args:
        func: Either a function object or a fully qualified function name
              (e.g., "structural_lib.codes.is456.flexure.calculate_mu_lim").

    Returns:
        List of clause reference strings, or empty list if none found.

    Example:
        >>> from structural_lib.codes.is456 import flexure
        >>> get_clause_refs(flexure.calculate_mu_lim)
        ['38.1']
        >>> get_clause_refs("structural_lib.codes.is456.flexure.calculate_mu_lim")
        ['38.1']
    """
    if callable(func):
        # First try function attribute
        refs = getattr(func, "_is456_clauses", None)
        if refs is not None:
            return list(refs)

        # Fall back to registry
        func_key = f"{func.__module__}.{func.__qualname__}"
        return _CLAUSE_REGISTRY.get(func_key, [])

    # String lookup in registry
    return _CLAUSE_REGISTRY.get(func, [])


def get_clause_info(clause_ref: str) -> dict[str, Any] | None:
    """Get detailed information about a specific IS 456 clause.

    Args:
        clause_ref: Clause reference string (e.g., "38.1", "40.1", "G-1.1").

    Returns:
        Dictionary with clause information, or None if not found.

    Example:
        >>> info = get_clause_info("38.1")
        >>> print(info["title"])
        'Assumptions in Design'
        >>> print(info["category"])
        'flexure'
    """
    db = _load_clause_database()

    # First check in clauses
    clauses: dict[str, Any] = db.get("clauses", {})
    if clause_ref in clauses:
        result: dict[str, Any] = clauses[clause_ref]
        return result

    # Then check in annexures (for G-x.x references)
    annexures: dict[str, Any] = db.get("annexures", {})
    if clause_ref in annexures:
        result = annexures[clause_ref]
        return result

    return None


def list_clauses_by_category(category: str) -> list[dict[str, Any]]:
    """List all clauses in a specific category.

    Args:
        category: Category name (e.g., "flexure", "shear", "detailing").

    Returns:
        List of clause dictionaries matching the category.

    Example:
        >>> flexure_clauses = list_clauses_by_category("flexure")
        >>> len(flexure_clauses)
        8
    """
    db = _load_clause_database()
    clauses = db.get("clauses", {})
    result = []
    for ref, info in clauses.items():
        if info.get("category") == category:
            result.append({"clause_ref": ref, **info})
    return result


def get_all_registered_functions() -> dict[str, list[str]]:
    """Get all functions registered with clause decorators.

    Returns:
        Dictionary mapping function names to their clause references.

    Example:
        >>> funcs = get_all_registered_functions()
        >>> for name, clauses in funcs.items():
        ...     print(f"{name}: {clauses}")
    """
    return dict(_CLAUSE_REGISTRY)


def search_clauses(keyword: str) -> list[dict[str, Any]]:
    """Search clauses by keyword in title, text, or keywords.

    Args:
        keyword: Search term (case-insensitive).

    Returns:
        List of matching clause dictionaries with clause_ref added.

    Example:
        >>> results = search_clauses("shear")
        >>> len(results)
        10
    """
    db = _load_clause_database()
    clauses = db.get("clauses", {})
    keyword_lower = keyword.lower()
    results = []

    for ref, info in clauses.items():
        # Search in title
        if keyword_lower in info.get("title", "").lower():
            results.append({"clause_ref": ref, **info})
            continue
        # Search in text
        if keyword_lower in info.get("text", "").lower():
            results.append({"clause_ref": ref, **info})
            continue
        # Search in keywords
        for kw in info.get("keywords", []):
            if keyword_lower in kw.lower():
                results.append({"clause_ref": ref, **info})
                break

    return results


def generate_traceability_report() -> dict[str, Any]:
    """Generate a traceability report for all registered functions.

    Returns:
        Dictionary containing:
        - functions: List of function info with their clause references
        - clauses_used: Set of all clause references used
        - coverage: Statistics on clause coverage

    Example:
        >>> report = generate_traceability_report()
        >>> print(f"Functions: {len(report['functions'])}")
        >>> print(f"Clauses used: {len(report['clauses_used'])}")
    """
    db = _load_clause_database()
    all_clauses = set(db.get("clauses", {}).keys())
    used_clauses: set[str] = set()
    functions = []

    for func_name, refs in _CLAUSE_REGISTRY.items():
        used_clauses.update(refs)
        functions.append(
            {
                "function": func_name,
                "clauses": refs,
                "module": func_name.rsplit(".", 1)[0] if "." in func_name else "",
            }
        )

    return {
        "functions": functions,
        "clauses_used": sorted(used_clauses),
        "total_clauses_in_db": len(all_clauses),
        "total_clauses_used": len(used_clauses),
        "coverage_percent": (
            round(len(used_clauses) / len(all_clauses) * 100, 1) if all_clauses else 0.0
        ),
    }


def get_database_metadata() -> dict[str, Any]:
    """Get metadata about the clause database.

    Returns:
        Dictionary with database metadata (standard, version, etc.).
    """
    db = _load_clause_database()
    metadata: dict[str, Any] = db.get("metadata", {})
    return metadata


# CLI entry point function
def cli_lookup(clause_ref: str) -> None:
    """CLI function to lookup clause information.

    Args:
        clause_ref: Clause reference to look up.
    """
    info = get_clause_info(clause_ref)
    if info is None:
        print(f"Clause '{clause_ref}' not found in IS 456 database.")
        return

    print(f"\n{'=' * 60}")
    print(f"IS 456:2000 - Clause {clause_ref}")
    print(f"{'=' * 60}")
    print(f"Title:    {info.get('title', 'N/A')}")
    print(f"Section:  {info.get('section', 'N/A')}")
    print(f"Category: {info.get('category', 'N/A')}")
    print("\nText:")
    print(f"  {info.get('text', 'N/A')}")

    if "formula" in info:
        print("\nFormula:")
        print(f"  {info['formula']}")

    if "formulas" in info:
        print("\nFormulas:")
        for name, formula in info["formulas"].items():
            print(f"  {name}: {formula}")

    if "tables" in info:
        print("\nRelated Tables:")
        for table in info["tables"]:
            print(f"  - {table}")

    if "keywords" in info:
        print(f"\nKeywords: {', '.join(info['keywords'])}")

    print(f"{'=' * 60}\n")
