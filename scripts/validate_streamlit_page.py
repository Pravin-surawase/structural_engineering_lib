#!/usr/bin/env python3
"""
Automated Streamlit Page Validation Script

Tests pages without running Streamlit browser to catch errors fast.

Usage:
    python scripts/validate_streamlit_page.py streamlit_app/pages/01_beam_design.py
"""

import sys
import ast
from pathlib import Path
from typing import List, Dict, Any


class StreamlitPageValidator:
    """Validates Streamlit pages for common issues"""

    def __init__(self, page_path: str):
        self.page_path = Path(page_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Dict[str, Any]:
        """Run all validations"""
        print(f"🔍 Validating: {self.page_path.name}")
        print("=" * 60)

        # 1. Syntax check
        if not self._check_syntax():
            return self._report()

        # 2. Import check
        if not self._check_imports():
            return self._report()

        # 3. AST analysis
        self._analyze_ast()

        # 4. Theme manager check
        self._check_theme_setup()

        return self._report()

    def _check_syntax(self) -> bool:
        """Check Python syntax"""
        print("\n1️⃣  Checking syntax...")
        try:
            with open(self.page_path) as f:
                compile(f.read(), self.page_path, "exec")
            print("   ✅ Syntax OK")
            return True
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            print(f"   ❌ Syntax error: {e.msg}")
            return False

    def _check_imports(self) -> bool:
        """Check if all imports work"""
        print("\n2️⃣  Checking imports...")
        try:
            with open(self.page_path) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name.split(".")[0])
                        except ImportError:
                            self.warnings.append(f"Import may fail: {alias.name}")

            print("   ✅ Imports OK")
            return True
        except Exception as e:
            self.errors.append(f"Import check failed: {e}")
            print(f"   ❌ Import error: {e}")
            return False

    def _analyze_ast(self):
        """Analyze AST for issues"""
        print("\n3️⃣  Analyzing code structure...")
        try:
            with open(self.page_path) as f:
                tree = ast.parse(f.read())

            # Check for unhashable hash calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "hash":
                        if node.args and isinstance(node.args[0], ast.Call):
                            if isinstance(node.args[0].func, ast.Name):
                                if node.args[0].func.id == "frozenset":
                                    self.warnings.append(
                                        f"Line {node.lineno}: Potential unhashable hash() - "
                                        "ensure dict values are hashable"
                                    )

            print("   ✅ AST analysis complete")
        except Exception as e:
            self.warnings.append(f"AST analysis partial: {e}")
            print(f"   ⚠️  AST analysis warning: {e}")

    def _check_theme_setup(self):
        """Check theme manager setup"""
        print("\n4️⃣  Checking theme setup...")
        try:
            with open(self.page_path) as f:
                content = f.read()

            # Check for theme initialization
            if "initialize_theme()" not in content:
                self.warnings.append("Theme not initialized - call initialize_theme()")

            if "apply_dark_mode_theme()" not in content:
                self.warnings.append("Dark mode theme not applied")

            # Check import order
            lines = content.split("\n")
            theme_import_line = None
            theme_init_line = None

            for i, line in enumerate(lines):
                if "from utils.theme_manager import" in line:
                    theme_import_line = i
                if "initialize_theme()" in line:
                    theme_init_line = i
                if "apply_dark_mode_theme()" in line and theme_init_line is None:
                    self.warnings.append(
                        f"Line {i+1}: apply_dark_mode_theme() before initialize_theme()"
                    )

            print("   ✅ Theme setup checked")
        except Exception as e:
            self.warnings.append(f"Theme check error: {e}")
            print(f"   ⚠️  Theme check warning: {e}")

    def _report(self) -> Dict[str, Any]:
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All checks passed!")

        print("\n" + "=" * 60)

        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_streamlit_page.py <page_path>")
        print(
            "Example: python scripts/validate_streamlit_page.py streamlit_app/pages/01_beam_design.py"
        )
        sys.exit(1)

    page_path = sys.argv[1]
    validator = StreamlitPageValidator(page_path)
    result = validator.validate()

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
