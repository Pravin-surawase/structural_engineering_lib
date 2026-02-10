"""Shared AST parsing helpers for scripts/.

Eliminates repeated ast.parse/try-except boilerplate and import-extraction
logic across 16+ scripts. Provides safe file parsing, import extraction,
function/class discovery, and docstring helpers.

Usage from any script in scripts/:
    from _lib.ast_helpers import parse_python_file, extract_imports, find_functions

    tree = parse_python_file(Path("some_module.py"))
    if tree is not None:
        for imp in extract_imports(tree):
            print(f"  imports {imp.module}")
        for fn in find_functions(tree):
            print(f"  def {fn.name}({', '.join(fn.params)})")
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Safe parsing
# ---------------------------------------------------------------------------


def parse_python_file(
    filepath: Path,
    *,
    quiet: bool = False,
) -> ast.Module | None:
    """Parse a Python file into an AST, returning None on failure.

    Handles the common try/except SyntaxError + UnicodeDecodeError pattern
    that every AST-using script duplicates.

    Args:
        filepath: Path to the .py file.
        quiet: If True, suppress warning messages on parse failure.

    Returns:
        Parsed ast.Module or None if the file cannot be parsed.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        return ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        if not quiet:
            print(f"  ⚠️  Skipping {filepath}: SyntaxError: {e}", file=sys.stderr)
    except UnicodeDecodeError as e:
        if not quiet:
            print(f"  ⚠️  Skipping {filepath}: UnicodeDecodeError: {e}", file=sys.stderr)
    except OSError as e:
        if not quiet:
            print(f"  ⚠️  Cannot read {filepath}: {e}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Import extraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImportInfo:
    """Information about a single import statement.

    Attributes:
        module: The module being imported (e.g., "os.path").
        names: List of imported names (e.g., ["join", "exists"]).
        line: Line number of the import statement.
        is_from_import: True for ``from X import Y``, False for ``import X``.
    """

    module: str
    names: list[str] = field(default_factory=list)
    line: int = 0
    is_from_import: bool = False


def extract_imports(tree: ast.Module) -> Iterator[ImportInfo]:
    """Extract all import statements from an AST.

    Walks the full tree and yields one ImportInfo per import/from-import.
    This is the pattern duplicated in check_architecture_boundaries,
    check_circular_imports, validate_imports, etc.

    Args:
        tree: Parsed AST module (from parse_python_file).

    Yields:
        ImportInfo for each import found.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield ImportInfo(
                    module=alias.name,
                    names=[alias.asname or alias.name],
                    line=node.lineno,
                    is_from_import=False,
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            yield ImportInfo(
                module=module,
                names=names,
                line=node.lineno,
                is_from_import=True,
            )


def extract_imports_from_file(filepath: Path, *, quiet: bool = False) -> list[ImportInfo]:
    """Convenience: parse a file and extract its imports in one call.

    Args:
        filepath: Path to .py file.
        quiet: If True, suppress parse warnings.

    Returns:
        List of ImportInfo (empty list if file cannot be parsed).
    """
    tree = parse_python_file(filepath, quiet=quiet)
    if tree is None:
        return []
    return list(extract_imports(tree))


# ---------------------------------------------------------------------------
# Function / class discovery
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FunctionInfo:
    """Information about a function or method definition.

    Attributes:
        name: Function name.
        line: Line number of the ``def`` statement.
        params: Parameter names (excluding ``self`` and ``cls``).
        docstring: First line of docstring, or empty string.
        is_async: True for ``async def``.
        is_method: True if nested inside a class.
        decorators: List of decorator names (simple names only).
    """

    name: str
    line: int = 0
    params: list[str] = field(default_factory=list)
    docstring: str = ""
    is_async: bool = False
    is_method: bool = False
    decorators: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ClassInfo:
    """Information about a class definition.

    Attributes:
        name: Class name.
        line: Line number of the ``class`` statement.
        docstring: First line of docstring, or empty string.
        methods: Public method names (non-underscore-prefixed).
        bases: Base class names.
    """

    name: str
    line: int = 0
    docstring: str = ""
    methods: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)


def _get_decorator_names(decorator_list: list[ast.expr]) -> list[str]:
    """Extract simple decorator names from a decorator list."""
    names = []
    for dec in decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(dec.attr)
        elif isinstance(dec, ast.Call):
            # e.g., @router.get("/path")
            if isinstance(dec.func, ast.Name):
                names.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                names.append(dec.func.attr)
    return names


def _first_docstring_line(node: ast.AST) -> str:
    """Get the first line of a node's docstring, or empty string."""
    doc = ast.get_docstring(node)
    if doc:
        return doc.split("\n")[0].strip()[:200]
    return ""


def find_functions(
    tree: ast.Module,
    *,
    include_private: bool = False,
    include_methods: bool = False,
) -> list[FunctionInfo]:
    """Find top-level function definitions in an AST.

    Args:
        tree: Parsed AST module.
        include_private: Include functions starting with ``_``.
        include_methods: Include methods inside classes.

    Returns:
        List of FunctionInfo for matching functions.
    """
    results: list[FunctionInfo] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not include_private and node.name.startswith("_"):
                continue
            params = [
                arg.arg
                for arg in node.args.args
                if arg.arg not in ("self", "cls")
            ]
            results.append(
                FunctionInfo(
                    name=node.name,
                    line=node.lineno,
                    params=params,
                    docstring=_first_docstring_line(node),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    is_method=False,
                    decorators=_get_decorator_names(node.decorator_list),
                )
            )

        elif include_methods and isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not include_private and child.name.startswith("_"):
                        continue
                    params = [
                        arg.arg
                        for arg in child.args.args
                        if arg.arg not in ("self", "cls")
                    ]
                    results.append(
                        FunctionInfo(
                            name=child.name,
                            line=child.lineno,
                            params=params,
                            docstring=_first_docstring_line(child),
                            is_async=isinstance(child, ast.AsyncFunctionDef),
                            is_method=True,
                            decorators=_get_decorator_names(child.decorator_list),
                        )
                    )

    return results


def find_classes(
    tree: ast.Module,
    *,
    include_private: bool = False,
) -> list[ClassInfo]:
    """Find top-level class definitions in an AST.

    Args:
        tree: Parsed AST module.
        include_private: Include classes starting with ``_``.

    Returns:
        List of ClassInfo for matching classes.
    """
    results: list[ClassInfo] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            if not include_private and node.name.startswith("_"):
                continue
            methods = [
                child.name
                for child in ast.iter_child_nodes(node)
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not child.name.startswith("_")
            ]
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)

            results.append(
                ClassInfo(
                    name=node.name,
                    line=node.lineno,
                    docstring=_first_docstring_line(node),
                    methods=methods,
                    bases=bases,
                )
            )

    return results


def find_constants(tree: ast.Module) -> list[tuple[str, int]]:
    """Find top-level UPPER_CASE constant assignments.

    Args:
        tree: Parsed AST module.

    Returns:
        List of (name, line_number) tuples for constants.
    """
    constants = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append((target.id, node.lineno))
    return constants
