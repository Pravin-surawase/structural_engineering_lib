#!/usr/bin/env python3
"""Unified API validation — signatures, docs, and sync checks.

Consolidates three former scripts into one with subcommands:
  --signatures   Check Streamlit pages for correct API call signatures
  --docs         Ensure api.__all__ symbols are in docs/reference/api.md
  --sync         Validate api.md ↔ api-stability.md symbol parity
  --all          Run all checks (default)

Replaces:
  - check_api_signatures.py
  - check_api_doc_signatures.py
  - check_api_docs_sync.py

Usage:
    python scripts/check_api.py                 # All checks
    python scripts/check_api.py --signatures    # Streamlit signature checks
    python scripts/check_api.py --docs          # api.__all__ ↔ api.md
    python scripts/check_api.py --sync          # api.md ↔ api-stability.md
    python scripts/check_api.py --fix           # Show suggested fixes (signatures)

Exit Codes:
    0: All checks pass
    1: One or more checks failed
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1: SIGNATURES — Streamlit page API call validation
# ═══════════════════════════════════════════════════════════════════════════

API_SIGNATURES = {
    "cached_design": {
        "required_params": [
            "mu_knm", "vu_kn", "b_mm", "D_mm", "d_mm", "fck_nmm2", "fy_nmm2",
        ],
        "optional_params": ["exposure", "span_mm"],
    },
    "cached_smart_analysis": {
        "required_params": [
            "mu_knm", "vu_kn", "b_mm", "D_mm", "d_mm",
            "fck_nmm2", "fy_nmm2", "span_mm",
        ],
        "optional_params": ["include_cost", "include_suggestions"],
    },
    "build_design_params": {
        "required_params": [
            "mu_knm", "vu_kn", "b_mm", "D_mm", "d_mm",
            "fck_nmm2", "fy_nmm2", "cover_mm",
        ],
        "optional_params": [],
    },
}

RESPONSE_KEY_MAPPINGS = {
    "Ast_req": "ast_required",
    "Ast_prov": "ast_provided",
    "spacing_mm": "spacing",
    "n_bars": "num_bars",
}

PARAM_NAME_MAPPINGS = {
    "fck": "fck_nmm2",
    "fy": "fy_nmm2",
    "cover": "cover_mm",
}


class APISignatureChecker(ast.NodeVisitor):
    """AST visitor to check API function calls."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[dict] = []
        self.local_functions: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.local_functions.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.local_functions.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_func_name(node)
        if func_name in API_SIGNATURES and func_name not in self.local_functions:
            self._check_api_call(node, func_name)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            key = node.slice.value
            if key in RESPONSE_KEY_MAPPINGS:
                if isinstance(node.value, ast.Name):
                    var_name = node.value.id.lower()
                    if any(p in var_name for p in ["df", "data", "result", "row", "record"]):
                        self.generic_visit(node)
                        return
                correct_key = RESPONSE_KEY_MAPPINGS[key]
                self.issues.append({
                    "type": "wrong_key", "line": node.lineno,
                    "key": key, "correct_key": correct_key,
                    "message": f"Use '{correct_key}' instead of '{key}'",
                })
        self.generic_visit(node)

    def _get_func_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def _check_api_call(self, node: ast.Call, func_name: str) -> None:
        spec = API_SIGNATURES[func_name]
        required = set(spec["required_params"])
        used_kwargs = {kw.arg for kw in node.keywords if kw.arg}

        for kwarg in used_kwargs:
            if kwarg in PARAM_NAME_MAPPINGS:
                correct = PARAM_NAME_MAPPINGS[kwarg]
                self.issues.append({
                    "type": "wrong_param", "line": node.lineno,
                    "function": func_name, "param": kwarg,
                    "correct_param": correct,
                    "message": f"Use '{correct}' instead of '{kwarg}' in {func_name}()",
                })

        if used_kwargs:
            missing = required - used_kwargs
            if missing:
                positional_count = len(node.args)
                required_list = spec["required_params"]
                covered_by_positional = set(required_list[:positional_count])
                still_missing = missing - covered_by_positional
                if still_missing:
                    self.issues.append({
                        "type": "missing_params", "line": node.lineno,
                        "function": func_name, "missing": list(still_missing),
                        "message": f"Missing required parameters: {still_missing}",
                    })


def _check_file_signatures(filepath: Path) -> list[dict]:
    """Check a single Python file for API signature issues."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        return [{"type": "syntax_error", "line": e.lineno or 0, "message": f"Syntax error: {e.msg}"}]
    checker = APISignatureChecker(str(filepath))
    checker.visit(tree)
    return checker.issues


def check_signatures(
    files: list[str] | None = None,
    pages_dir: str = "streamlit_app/pages",
    show_fix: bool = False,
) -> int:
    """Check Streamlit pages for API signature issues."""
    pdir = REPO_ROOT / pages_dir
    if not pdir.exists():
        print(f"❌ Pages directory not found: {pdir}")
        return 1

    results: dict[str, list[dict]] = {}
    if files:
        for fp in files:
            path = Path(fp)
            if not path.exists():
                path = pdir / fp
            if path.exists():
                issues = _check_file_signatures(path)
                if issues:
                    results[path.name] = issues
    else:
        for page_file in pdir.glob("*.py"):
            if page_file.name.startswith("_"):
                continue
            issues = _check_file_signatures(page_file)
            if issues:
                results[page_file.name] = issues

    if results:
        total = 0
        for filename, issues in sorted(results.items()):
            print(f"\n📄 {filename}:")
            for issue in issues:
                total += 1
                icon = {"wrong_key": "🔑", "wrong_param": "⚙️", "missing_params": "❓"}.get(
                    issue.get("type", ""), "⚠️"
                )
                print(f"   {icon} Line {issue.get('line', 0)}: {issue.get('message', '')}")
                if show_fix and issue["type"] in ("wrong_key", "wrong_param"):
                    correct = issue.get("correct_key") or issue.get("correct_param")
                    wrong = issue.get("key") or issue.get("param")
                    print(f"      Fix: Replace '{wrong}' with '{correct}'")
        print(f"\n❌ {total} issue(s) in {len(results)} file(s)")
        return 1

    print("✅ No API signature issues found!")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2: DOCS — api.__all__ symbols documented in api.md
# ═══════════════════════════════════════════════════════════════════════════

def check_docs() -> int:
    """Ensure api.__all__ functions are documented in docs/reference/api.md."""
    doc_path = REPO_ROOT / "docs" / "reference" / "api.md"
    if not doc_path.exists():
        print("ERROR: docs/reference/api.md not found")
        return 1

    doc_text = doc_path.read_text(encoding="utf-8")

    # Extract documented names
    documented: set[str] = set()
    for match in re.finditer(r"\bapi\.([a-zA-Z_][a-zA-Z0-9_]*)", doc_text):
        documented.add(match.group(1))
    for match in re.finditer(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", doc_text, re.M):
        documented.add(match.group(1))

    # Load API module
    sys.path.insert(0, str(REPO_ROOT / "Python"))
    try:
        from structural_lib import api  # type: ignore
    except ImportError as e:
        print(f"ERROR: Cannot import structural_lib.api: {e}")
        return 1

    exported = [name for name in getattr(api, "__all__", []) if not name.startswith("_")]
    missing = [name for name in exported if name not in documented]

    if missing:
        print("ERROR: api.__all__ symbols missing from docs/reference/api.md:")
        for name in missing:
            print(f"  - {name}")
        return 1

    print("✅ All api.__all__ symbols documented in api.md")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3: SYNC — api.md ↔ api-stability.md symbol parity
# ═══════════════════════════════════════════════════════════════════════════

_API_SYMBOL_RE = re.compile(r"\bapi\.[a-zA-Z_][a-zA-Z0-9_]*")


def _extract_symbols(path: Path) -> set[str]:
    """Extract api.* symbols from a markdown file."""
    symbols = set(_API_SYMBOL_RE.findall(path.read_text(encoding="utf-8")))
    return {s for s in symbols if s != "api.py"}


def check_sync() -> int:
    """Validate api.md and api-stability.md mention same symbols."""
    api_doc = REPO_ROOT / "docs" / "reference" / "api.md"
    stability_doc = REPO_ROOT / "docs" / "reference" / "api-stability.md"

    if not api_doc.exists():
        print("ERROR: docs/reference/api.md not found")
        return 1
    if not stability_doc.exists():
        print("ERROR: docs/reference/api-stability.md not found")
        return 1

    api_doc_text = api_doc.read_text(encoding="utf-8")
    api_doc_symbols = _extract_symbols(api_doc)
    stability_symbols = _extract_symbols(stability_doc)

    if not stability_symbols:
        print("ERROR: No api.* symbols found in api-stability.md")
        return 1

    # Check symbols in stability doc are in api doc
    missing_in_api_doc = []
    for symbol in sorted(stability_symbols):
        name = symbol.split(".", 1)[1]
        if symbol not in api_doc_text and not re.search(rf"\b{name}\b", api_doc_text):
            missing_in_api_doc.append(symbol)

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

    print("✅ api.md ↔ api-stability.md symbols in sync")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified API validation (signatures, docs, sync)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/check_api.py                 # All checks\n"
            "  python scripts/check_api.py --signatures    # Streamlit signatures\n"
            "  python scripts/check_api.py --docs          # api.__all__ in api.md\n"
            "  python scripts/check_api.py --sync          # api.md ↔ stability\n"
            "  python scripts/check_api.py --fix           # Show suggested fixes\n"
        ),
    )

    group = parser.add_argument_group("Check selectors (default: --all)")
    group.add_argument("--signatures", action="store_true", help="Check Streamlit API signatures")
    group.add_argument("--docs", action="store_true", help="Check api.__all__ in api.md")
    group.add_argument("--sync", action="store_true", help="Check api.md ↔ api-stability.md sync")
    group.add_argument("--all", action="store_true", help="Run all checks (default)")

    sig_group = parser.add_argument_group("Signature options")
    sig_group.add_argument("--fix", action="store_true", help="Show suggested fixes")
    sig_group.add_argument("--pages-dir", default="streamlit_app/pages", help="Pages directory")
    sig_group.add_argument("files", nargs="*", help="Specific files to check (signatures)")

    args = parser.parse_args()
    run_all = args.all or not any([args.signatures, args.docs, args.sync])

    results: list[int] = []

    if run_all or args.signatures:
        print("⚙️  Checking API signatures...")
        rc = check_signatures(files=args.files or None, pages_dir=args.pages_dir, show_fix=args.fix)
        results.append(rc)

    if run_all or args.docs:
        print("📖 Checking api.__all__ documentation...")
        rc = check_docs()
        results.append(rc)

    if run_all or args.sync:
        print("🔄 Checking api.md ↔ api-stability.md sync...")
        rc = check_sync()
        results.append(rc)

    if any(rc != 0 for rc in results):
        print(f"\n{'='*40}")
        print(f"❌ {sum(1 for rc in results if rc != 0)}/{len(results)} check(s) failed")
        return 1
    else:
        print(f"\n{'='*40}")
        print(f"✅ All {len(results)} API check(s) passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
