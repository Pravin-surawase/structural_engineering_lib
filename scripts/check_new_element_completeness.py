#!/usr/bin/env python3
"""Check structural element completeness across all 7 layers.

Verifies types, math, tests, API, endpoint, frontend, and docs for each element.

Usage:
    python scripts/check_new_element_completeness.py                  # Full report
    python scripts/check_new_element_completeness.py --element column # Specific element
    python scripts/check_new_element_completeness.py --json           # Machine-readable
    python scripts/check_new_element_completeness.py --verbose        # Show file paths
"""

import ast
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Auto-detect elements from codes/is456/ subdirectories
# plus known future elements
KNOWN_ELEMENTS = ["beam", "column", "slab", "footing", "staircase", "shear_wall"]


def discover_elements():
    """Auto-detect elements from codes/is456/ subdirectories."""
    is456_dir = REPO_ROOT / "Python" / "structural_lib" / "codes" / "is456"
    discovered = []
    if is456_dir.exists():
        for d in sorted(is456_dir.iterdir()):
            if (
                d.is_dir()
                and not d.name.startswith(("_", "."))
                and d.name != "__pycache__"
                and d.name != "common"
            ):
                discovered.append(d.name)

    # Add known future elements that don't exist yet
    all_elements = list(set(discovered + KNOWN_ELEMENTS))
    return sorted(all_elements)


def check_types(element, verbose=False):
    """Check Layer 1: Type definitions in core/."""
    checks = {"layer": "types", "files": []}

    # Check for result type in data_types.py
    dt_file = REPO_ROOT / "Python" / "structural_lib" / "core" / "data_types.py"
    if dt_file.exists():
        content = dt_file.read_text()
        # Look for class names containing element name (case-insensitive)
        elem_cap = element.capitalize()
        # Handle special cases
        if element == "column":
            checks["result_type"] = "class Column" in content
        elif element == "beam":
            checks["result_type"] = (
                "class Beam" in content or "BeamDesignResult" in content
            )
        else:
            checks["result_type"] = f"class {elem_cap}" in content

        if checks["result_type"] and verbose:
            checks["files"].append(str(dt_file.relative_to(REPO_ROOT)))
    else:
        checks["result_type"] = False

    # Check for error codes in errors.py
    err_file = REPO_ROOT / "Python" / "structural_lib" / "core" / "errors.py"
    if err_file.exists():
        content = err_file.read_text()
        err_prefix = f"E_{element.upper()}_"
        error_count = content.count(err_prefix)
        checks["error_codes"] = error_count
        checks["has_errors"] = error_count >= 3  # Minimum 3 error codes

        if checks["has_errors"] and verbose:
            checks["files"].append(str(err_file.relative_to(REPO_ROOT)))
    else:
        checks["has_errors"] = False
        checks["error_codes"] = 0

    return checks


def check_math(element, verbose=False):
    """Check Layer 2: Math implementation in codes/is456/."""
    checks = {"layer": "math", "files": []}

    # Check for element module directory or file
    is456_dir = REPO_ROOT / "Python" / "structural_lib" / "codes" / "is456"
    element_dir = is456_dir / element
    element_file = is456_dir / f"{element}.py"

    checks["module_exists"] = element_dir.exists() or element_file.exists()

    if element_dir.exists():
        # Count .py files (excluding __init__, __pycache__)
        py_files = [
            f
            for f in element_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("_")
        ]
        checks["module_count"] = len(py_files)

        if verbose:
            checks["files"].extend([str(f.relative_to(REPO_ROOT)) for f in py_files])

        # Count @clause decorated functions
        clause_count = 0
        for py_file in py_files:
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for dec in node.decorator_list:
                            if (
                                isinstance(dec, ast.Call)
                                and hasattr(dec.func, "id")
                                and dec.func.id == "clause"
                            ):
                                clause_count += 1
                            elif (
                                isinstance(dec, ast.Call)
                                and hasattr(dec.func, "attr")
                                and dec.func.attr == "clause"
                            ):
                                clause_count += 1
            except (SyntaxError, UnicodeDecodeError):
                pass
        checks["clause_functions"] = clause_count
    elif element_file.exists():
        checks["module_count"] = 1
        if verbose:
            checks["files"].append(str(element_file.relative_to(REPO_ROOT)))

        # Count @clause decorated functions in single file
        try:
            tree = ast.parse(element_file.read_text())
            clause_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        if (
                            isinstance(dec, ast.Call)
                            and hasattr(dec.func, "id")
                            and dec.func.id == "clause"
                        ):
                            clause_count += 1
            checks["clause_functions"] = clause_count
        except (SyntaxError, UnicodeDecodeError):
            checks["clause_functions"] = 0
    else:
        checks["module_count"] = 0
        checks["clause_functions"] = 0

    return checks


def check_tests(element, verbose=False):
    """Check Layer 3: Test files."""
    checks = {"layer": "tests", "files": []}
    tests_dir = REPO_ROOT / "Python" / "tests"

    # Search for test files matching element name
    test_files = list(tests_dir.rglob(f"test_{element}*.py")) + list(
        tests_dir.rglob(f"test_*{element}*.py")
    )
    # Deduplicate
    test_files = list(set(test_files))
    checks["test_files"] = len(test_files)

    if verbose:
        checks["files"] = [str(f.relative_to(REPO_ROOT)) for f in test_files]

    # Count test functions
    test_count = 0
    for tf in test_files:
        try:
            tree = ast.parse(tf.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_count += 1
        except (SyntaxError, UnicodeDecodeError):
            pass
    checks["test_functions"] = test_count
    checks["has_tests"] = test_count >= 15  # Minimum per element

    return checks


def check_api(element, verbose=False):
    """Check Layer 4: API wiring in services/api.py."""
    checks = {"layer": "api", "files": []}
    api_file = REPO_ROOT / "Python" / "structural_lib" / "services" / "api.py"

    if api_file.exists():
        content = api_file.read_text()
        # Look for design_<element>_is456 or <element> related functions
        elem_lower = element.lower()
        # Count public functions related to element
        func_count = 0
        func_names = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    if elem_lower in node.name.lower():
                        func_count += 1
                        func_names.append(node.name)
        except (SyntaxError, UnicodeDecodeError):
            pass
        checks["api_functions"] = func_count
        checks["has_api"] = func_count > 0

        if verbose and checks["has_api"]:
            checks["files"].append(str(api_file.relative_to(REPO_ROOT)))
            checks["function_names"] = func_names
    else:
        checks["api_functions"] = 0
        checks["has_api"] = False

    return checks


def check_endpoint(element, verbose=False):
    """Check Layer 5: FastAPI router."""
    checks = {"layer": "endpoint", "files": []}
    routers_dir = REPO_ROOT / "fastapi_app" / "routers"

    # Check for router file
    router_file = routers_dir / f"{element}.py"
    checks["router_exists"] = router_file.exists()

    if checks["router_exists"] and verbose:
        checks["files"].append(str(router_file.relative_to(REPO_ROOT)))

    # Also check if element is served by another router (e.g., design.py)
    if not router_file.exists():
        for rf in routers_dir.glob("*.py"):
            try:
                content = rf.read_text()
                if element.lower() in content.lower() and "@router" in content:
                    checks["served_by"] = rf.name
                    checks["router_exists"] = True
                    if verbose:
                        checks["files"].append(str(rf.relative_to(REPO_ROOT)))
                    break
            except (OSError, UnicodeDecodeError):
                pass

    # Check for endpoint tests
    tests_dir = REPO_ROOT / "fastapi_app" / "tests"
    if tests_dir.exists():
        test_files = list(tests_dir.rglob(f"*{element}*"))
        checks["endpoint_tests"] = len(test_files)
        if verbose and test_files:
            checks["files"].extend([str(f.relative_to(REPO_ROOT)) for f in test_files])
    else:
        checks["endpoint_tests"] = 0

    return checks


def check_frontend(element, verbose=False):
    """Check Layer 6: React hook + component."""
    checks = {"layer": "frontend", "files": []}
    src_dir = REPO_ROOT / "react_app" / "src"

    # Check for hook
    hooks_dir = src_dir / "hooks"
    elem_cap = element.capitalize()
    hooks = []
    if hooks_dir.exists():
        hooks = list(hooks_dir.glob(f"use{elem_cap}*")) + list(
            hooks_dir.glob(f"*{element.lower()}*")
        )
        hooks = list(set(hooks))  # Deduplicate
    checks["has_hook"] = len(hooks) > 0

    if verbose and hooks:
        checks["files"].extend([str(h.relative_to(REPO_ROOT)) for h in hooks])

    # Check for component directory
    comp_dir = src_dir / "components" / element
    checks["has_component"] = comp_dir.exists()

    if checks["has_component"] and verbose:
        checks["files"].append(str(comp_dir.relative_to(REPO_ROOT)))

    return checks


def check_docs(element, verbose=False):
    """Check Layer 7: Documentation."""
    checks = {"layer": "docs", "files": []}
    docs_dir = REPO_ROOT / "docs"

    # Check for any doc mentioning element
    doc_files = list(docs_dir.rglob(f"*{element}*"))
    checks["doc_files"] = len(doc_files)

    if verbose and doc_files:
        checks["files"] = [
            str(f.relative_to(REPO_ROOT)) for f in doc_files[:5]
        ]  # Limit to 5

    # Check for example script
    examples_dir = REPO_ROOT / "Python" / "examples"
    if examples_dir.exists():
        examples = list(examples_dir.rglob(f"*{element}*"))
        checks["has_example"] = len(examples) > 0
        if verbose and checks["has_example"]:
            checks["files"].extend(
                [str(e.relative_to(REPO_ROOT)) for e in examples[:3]]
            )
    else:
        checks["has_example"] = False

    return checks


def determine_level(results):
    """Determine completeness level L1/L2/L3."""
    types_ok = results["types"].get("has_errors", False) or results["types"].get(
        "result_type", False
    )
    math_ok = (
        results["math"].get("module_exists", False)
        and results["math"].get("clause_functions", 0) > 0
    )
    tests_ok = (
        results["tests"].get("test_functions", 0) >= 5
    )  # Relaxed from 15 — partial credit
    api_ok = results["api"].get("has_api", False)
    endpoint_ok = results["endpoint"].get("router_exists", False)
    frontend_ok = results["frontend"].get("has_hook", False) or results["frontend"].get(
        "has_component", False
    )
    docs_ok = results["docs"].get("doc_files", 0) > 0

    if (
        types_ok
        and math_ok
        and tests_ok
        and api_ok
        and endpoint_ok
        and frontend_ok
        and docs_ok
    ):
        return "L3", "Full Stack"
    elif types_ok and math_ok and tests_ok and api_ok and endpoint_ok:
        return "L2", "API Complete"
    elif types_ok and math_ok and tests_ok:
        return "L1", "Math Complete"
    elif math_ok:
        return "L0", "Partial"
    else:
        return "--", "Not Started"


def check_element(element, verbose=False):
    """Run all checks for a single element."""
    results = {
        "element": element,
        "types": check_types(element, verbose),
        "math": check_math(element, verbose),
        "tests": check_tests(element, verbose),
        "api": check_api(element, verbose),
        "endpoint": check_endpoint(element, verbose),
        "frontend": check_frontend(element, verbose),
        "docs": check_docs(element, verbose),
    }

    level_code, level_name = determine_level(results)
    results["level_code"] = level_code
    results["level_name"] = level_name

    return results


def format_matrix_row(result):
    """Format a single row for the matrix table."""
    elem = result["element"]

    # Types column
    types_ok = result["types"].get("has_errors", False) or result["types"].get(
        "result_type", False
    )
    types_str = "✅" if types_ok else "❌"

    # Math column (show function count)
    math_ok = result["math"].get("module_exists", False)
    clause_count = result["math"].get("clause_functions", 0)
    if math_ok and clause_count > 0:
        math_str = f"{clause_count} fn"
    elif math_ok:
        math_str = "⚠️"
    else:
        math_str = "--"

    # Tests column
    test_count = result["tests"].get("test_functions", 0)
    if test_count >= 15:
        tests_str = f"{test_count} tests"
    elif test_count > 0:
        tests_str = f"⚠️ {test_count}"
    else:
        tests_str = "--"

    # API column
    api_ok = result["api"].get("has_api", False)
    api_str = "✅" if api_ok else "❌"

    # Router column
    router_ok = result["endpoint"].get("router_exists", False)
    router_str = "✅" if router_ok else "❌"

    # UI column
    ui_ok = result["frontend"].get("has_hook", False) or result["frontend"].get(
        "has_component", False
    )
    ui_str = "✅" if ui_ok else "❌"

    # Docs column
    docs_ok = result["docs"].get("doc_files", 0) > 0
    docs_str = "✅" if docs_ok else "❌"

    # Level column
    level = f"{result['level_code']} {result['level_name']}"

    return f"{elem:13}| {types_str:^5} | {math_str:^7}| {tests_str:^10}| {api_str:^3} | {router_str:^6} | {ui_str:^3} | {docs_str:^4} | {level}"


def print_matrix(results):
    """Print the completeness matrix table."""
    print("\nStructural Element Completeness Report")
    print("═" * 120)
    print(
        f"{'Element':13}| Types | Math   | Tests    | API | Router | UI  | Docs | Level"
    )
    print(
        "─" * 13
        + "+"
        + "─" * 7
        + "+"
        + "─" * 8
        + "+"
        + "─" * 10
        + "+"
        + "─" * 5
        + "+"
        + "─" * 8
        + "+"
        + "─" * 5
        + "+"
        + "─" * 6
        + "+"
        + "─" * 30
    )

    for result in results:
        print(format_matrix_row(result))

    # Summary
    total = len(results)
    l1_plus = sum(1 for r in results if r["level_code"] in ["L1", "L2", "L3"])
    l3 = sum(1 for r in results if r["level_code"] == "L3")

    print("\n" + "─" * 120)
    print(f"Summary: {l1_plus}/{total} elements at L1+, {l3}/{total} at L3")
    print()


def print_detailed(result):
    """Print detailed information for a single element."""
    print(f"\n{'=' * 80}")
    print(f"Element: {result['element']}")
    print(f"Level: {result['level_code']} — {result['level_name']}")
    print("=" * 80)

    # Types
    print("\n[Layer 1] Types:")
    print(
        f"  Result type: {'✅' if result['types'].get('result_type', False) else '❌'}"
    )
    print(f"  Error codes: {result['types'].get('error_codes', 0)}")
    if result["types"].get("files"):
        print(f"  Files: {', '.join(result['types']['files'])}")

    # Math
    print("\n[Layer 2] Math:")
    print(
        f"  Module exists: {'✅' if result['math'].get('module_exists', False) else '❌'}"
    )
    print(f"  Module count: {result['math'].get('module_count', 0)}")
    print(f"  @clause functions: {result['math'].get('clause_functions', 0)}")
    if result["math"].get("files"):
        for f in result["math"]["files"]:
            print(f"    - {f}")

    # Tests
    print("\n[Layer 3] Tests:")
    print(f"  Test files: {result['tests'].get('test_files', 0)}")
    print(f"  Test functions: {result['tests'].get('test_functions', 0)}")
    if result["tests"].get("files"):
        for f in result["tests"]["files"]:
            print(f"    - {f}")

    # API
    print("\n[Layer 4] API:")
    print(f"  API functions: {result['api'].get('api_functions', 0)}")
    if result["api"].get("function_names"):
        print(f"  Functions: {', '.join(result['api']['function_names'])}")
    if result["api"].get("files"):
        print(f"  Files: {', '.join(result['api']['files'])}")

    # Endpoint
    print("\n[Layer 5] FastAPI Endpoint:")
    print(
        f"  Router exists: {'✅' if result['endpoint'].get('router_exists', False) else '❌'}"
    )
    if result["endpoint"].get("served_by"):
        print(f"  Served by: {result['endpoint']['served_by']}")
    print(f"  Endpoint tests: {result['endpoint'].get('endpoint_tests', 0)}")
    if result["endpoint"].get("files"):
        for f in result["endpoint"]["files"]:
            print(f"    - {f}")

    # Frontend
    print("\n[Layer 6] Frontend:")
    print(f"  Hook: {'✅' if result['frontend'].get('has_hook', False) else '❌'}")
    print(
        f"  Component: {'✅' if result['frontend'].get('has_component', False) else '❌'}"
    )
    if result["frontend"].get("files"):
        for f in result["frontend"]["files"]:
            print(f"    - {f}")

    # Docs
    print("\n[Layer 7] Documentation:")
    print(f"  Doc files: {result['docs'].get('doc_files', 0)}")
    print(f"  Example: {'✅' if result['docs'].get('has_example', False) else '❌'}")
    if result["docs"].get("files"):
        for f in result["docs"]["files"]:
            print(f"    - {f}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check structural element completeness across all 7 layers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Full matrix report
  %(prog)s --element column    # Detailed report for column
  %(prog)s --json              # Machine-readable JSON
  %(prog)s --verbose           # Include file paths in output
        """,
    )
    parser.add_argument("--element", help="Check specific element (detailed output)")
    parser.add_argument(
        "--json", action="store_true", help="Machine-readable JSON output"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show file paths for each check"
    )

    args = parser.parse_args()

    # Discover elements
    elements = discover_elements()

    if args.element:
        # Single element detailed report
        if args.element not in elements:
            print(
                f"Error: Element '{args.element}' not found. Available: {', '.join(elements)}",
                file=sys.stderr,
            )
            return 1

        result = check_element(args.element, verbose=args.verbose or args.json)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_detailed(result)
    else:
        # All elements matrix
        results = [
            check_element(elem, verbose=args.verbose or args.json) for elem in elements
        ]

        if args.json:
            output = {
                "elements": results,
                "summary": {
                    "total": len(results),
                    "l1_plus": sum(
                        1 for r in results if r["level_code"] in ["L1", "L2", "L3"]
                    ),
                    "l2_plus": sum(
                        1 for r in results if r["level_code"] in ["L2", "L3"]
                    ),
                    "l3": sum(1 for r in results if r["level_code"] == "L3"),
                },
            }
            print(json.dumps(output, indent=2))
        else:
            print_matrix(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
