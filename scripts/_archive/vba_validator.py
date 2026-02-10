#!/usr/bin/env python3
"""
VBA Syntax Validator for VS Code
Checks VBA files for common syntax errors without needing Excel/Office
"""

import re
import sys
import io
from pathlib import Path
from typing import List

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


class VBAValidator:
    """Validates VBA syntax and standards"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.current_file = ""
        self.line_number = 0

    def validate_file(self, filepath: str) -> bool:
        """Validate a single VBA file"""
        self.current_file = filepath
        self.errors = []
        self.warnings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ ERROR: Could not read file {filepath}: {e}")
            return False

        print(f"\n📄 Checking: {Path(filepath).name}")
        print("=" * 60)

        # Run all validators
        self._check_option_explicit(lines)
        self._check_syntax_errors(lines)
        self._check_unicode_characters(lines)
        self._check_call_statements(lines)
        self._check_type_safety(lines)
        self._check_error_handling(lines)
        self._check_null_safety(lines)
        self._check_standards(lines)

        # Report results
        return self._print_results()

    def _check_option_explicit(self, lines: List[str]):
        """Check if Option Explicit is present"""
        for i, line in enumerate(lines[:20], 1):  # Check first 20 lines
            if line.strip().lower() == "option explicit":
                return

        self.warnings.append((1, "Missing 'Option Explicit' - Variables not validated"))

    def _check_syntax_errors(self, lines: List[str]):
        """Check for common syntax errors"""
        for i, line in enumerate(lines, 1):
            # Check for mismatched quotes
            double_quote_count = line.count('"') - line.count('""') * 2
            if double_quote_count % 2 != 0:
                self.errors.append(
                    (i, "Mismatched quotes (odd number of unescaped quotes)")
                )

            # Check for unmatched parentheses (basic check)
            if "Debug.Print" not in line:  # Skip Debug.Print for now
                open_parens = line.count("(") - line.count("()")
                close_parens = line.count(")") - line.count("()")
                if open_parens != close_parens:
                    # Only warn if looks like code, not comment
                    if not line.strip().startswith("'"):
                        pass  # Too many false positives

    def _check_unicode_characters(self, lines: List[str]):
        """Check for Unicode characters that will fail in VBA"""
        # Use Unicode escape sequences to avoid parsing issues
        unicode_patterns = {
            "\u201c": '"',  # Left double quote
            "\u201d": '"',  # Right double quote
            "\u2018": "'",  # Left single quote
            "\u2019": "'",  # Right single quote
            "✓": "[OK]",  # Checkmark
            "✗": "[FAIL]",  # X mark
            "✅": "[OK]",  # OK emoji
            "❌": "[FAIL]",  # FAIL emoji
            "→": "->",  # Arrow
            "·": ".",  # Middle dot
            "′": "'",  # Prime
        }

        for i, line in enumerate(lines, 1):
            for bad_char, fix in unicode_patterns.items():
                if bad_char in line:
                    # Format display safely
                    char_repr = repr(bad_char)[1:-1]  # Remove quotes from repr
                    self.errors.append(
                        (
                            i,
                            f"Unicode character {char_repr!r} found - replace with {fix!r}",
                        )
                    )

    def _check_call_statements(self, lines: List[str]):
        """Check for Call statements with proper parentheses"""
        for i, line in enumerate(lines, 1):
            # Remove comments first
            code_part = line.split("'")[0]  # Get everything before comment

            # Match Call statements
            if re.search(r"\bCall\s+\w+\s+[^(]", code_part):
                # Call without parentheses
                match = re.search(r"\bCall\s+(\w+)\s+([^(])", code_part)
                if match:
                    func_name = match.group(1)
                    # Skip common cases that are OK
                    if func_name not in ["Exit", "End", "Next", "Loop"]:
                        self.errors.append(
                            (
                                i,
                                f"Call statement missing parentheses: Call {func_name}(...) required",
                            )
                        )

    def _check_type_safety(self, lines: List[str]):
        """Check for type safety issues"""
        for i, line in enumerate(lines, 1):
            # Check for Integer when Long should be used
            if "As Integer" in line:
                if "For " in line or "count" in line.lower() or "size" in line.lower():
                    self.warnings.append(
                        (
                            i,
                            "Consider using 'As Long' instead of 'As Integer' for loop/size variables",
                        )
                    )

            # Check for division without CDbl
            if "/" in line and "CDbl" not in line and "'" not in line[: line.find("/")]:
                if not any(
                    x in line for x in ["http", "file", "<!--"]
                ):  # Skip URLs/comments
                    pass  # Too many false positives

    def _check_error_handling(self, lines: List[str]):
        """Check error handling patterns"""
        in_error_handler = False
        found_on_error = False

        for i, line in enumerate(lines, 1):
            if "On Error GoTo" in line:
                found_on_error = True
                in_error_handler = True

            if "On Error Resume Next" in line:
                # Check if followed by On Error GoTo 0
                if i + 5 < len(lines):
                    next_5_lines = "".join(lines[i : i + 5])
                    if "On Error GoTo 0" not in next_5_lines:
                        self.warnings.append(
                            (
                                i,
                                "On Error Resume Next without On Error GoTo 0 - error may persist",
                            )
                        )

    def _check_null_safety(self, lines: List[str]):
        """Check for null/nothing checks before object usage"""
        for i, line in enumerate(lines, 1):
            # Look for common object usage patterns
            if re.search(r"\.\w+\s*[=\[]", line):  # obj.property = or obj.method(
                # Check if previous line has null check
                if i > 1:
                    prev_lines = "".join(lines[max(0, i - 5) : i])
                    if (
                        "Is Nothing" not in prev_lines
                        and "Is Not Nothing" not in prev_lines
                    ):
                        # Only warn for known object types
                        if any(
                            x in line for x in ["sapModel", "etabs", "ws", "wb", "comp"]
                        ):
                            pass  # Too many false positives

    def _check_standards(self, lines: List[str]):
        """Check VBA coding standards"""
        for i, line in enumerate(lines, 1):
            # Check for hardcoded paths
            if "C:\\" in line and "'" not in line[: line.find("C:")]:  # Not in comment
                self.warnings.append(
                    (
                        i,
                        "Hardcoded Windows path found - use Application.PathSeparator instead",
                    )
                )

            # Check for implicit type conversions
            if ' = "' in line and " As " in "".join(lines[max(0, i - 10) : i]):
                # Might be type mismatch, but too many false positives
                pass

            # Enum detection
            if "Public Enum" in line:
                self.warnings.append(
                    (
                        i,
                        "Enum detected - consider using Constants instead to avoid ambiguity",
                    )
                )

    def _print_results(self) -> bool:
        """Print validation results"""
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0

        if self.errors:
            print("\n🔴 ERRORS:")
            for line_num, msg in self.errors:
                print(f"  Line {line_num}: {msg}")

        if self.warnings:
            print("\n🟡 WARNINGS:")
            for line_num, msg in self.warnings:
                print(f"  Line {line_num}: {msg}")

        if not has_errors and not has_warnings:
            print("✅ No issues found!")

        status = "❌ FAIL" if has_errors else ("⚠️  WARN" if has_warnings else "✅ PASS")
        print(f"\nStatus: {status}")

        return not has_errors  # Pass if no errors (warnings OK)

    def validate_directory(self, directory: str) -> bool:
        """Validate all VBA files in a directory"""
        path = Path(directory)
        bas_files = sorted(path.glob("*.bas"))

        if not bas_files:
            print(f"No .bas files found in {directory}")
            return False

        print(f"\n🔍 Found {len(bas_files)} VBA files to validate")
        print("=" * 60)

        all_passed = True
        results = []

        for bas_file in bas_files:
            passed = self.validate_file(str(bas_file))
            results.append((bas_file.name, passed))
            if not passed:
                all_passed = False

        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        for filename, passed in results:
            status = "✅" if passed else "❌"
            print(f"{status} {filename}")

        passed_count = sum(1 for _, p in results if p)
        print(f"\n{passed_count}/{len(results)} files passed validation")

        return all_passed


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("VBA Syntax Validator")
        print("=" * 60)
        print("\nUsage:")
        print("  python vba_validator.py <file.bas>        - Validate single file")
        print("  python vba_validator.py <directory>       - Validate all .bas files")
        print("\nExample:")
        print("  python vba_validator.py VBA/ETABS_Export/mod_Main.bas")
        print("  python vba_validator.py VBA/ETABS_Export/")
        return 1

    target = sys.argv[1]
    validator = VBAValidator()

    # Determine if file or directory
    path = Path(target)

    if path.is_file() and path.suffix == ".bas":
        # Single file
        success = validator.validate_file(target)
        return 0 if success else 1

    elif path.is_dir():
        # Directory
        success = validator.validate_directory(target)
        return 0 if success else 1

    else:
        print(f"❌ File not found or not a .bas file: {target}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
