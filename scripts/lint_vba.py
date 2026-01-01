#!/usr/bin/env python3
"""
VBA Syntax Linter - Pre-import validation
Catches common errors before Excel import
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class VBALinter:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []

    def lint(self) -> bool:
        """Run all checks. Returns True if no errors."""
        self.check_option_explicit()
        self.check_procedure_pairing()
        self.check_undeclared_variables()
        self.check_common_typos()
        self.check_line_continuations()

        self.print_results()
        return len(self.errors) == 0

    def check_option_explicit(self):
        """Ensure Option Explicit is present."""
        if not re.search(r'^\s*Option\s+Explicit', self.content, re.MULTILINE | re.IGNORECASE):
            self.warnings.append((1, "Missing 'Option Explicit' - add at top of file"))

    def check_procedure_pairing(self):
        """Check Sub/Function have matching End statements."""
        proc_stack = []

        for i, line in enumerate(self.lines, start=1):
            line_clean = line.strip()

            # Ignore comments
            if line_clean.startswith("'"):
                continue

            # Sub/Function start
            if re.match(r'^(Public|Private|Friend)?\s*(Sub|Function)', line_clean, re.IGNORECASE):
                proc_type = re.search(r'(Sub|Function)', line_clean, re.IGNORECASE).group(1)
                proc_stack.append((i, proc_type))

            # End Sub/Function
            if re.match(r'^End\s+(Sub|Function)', line_clean, re.IGNORECASE):
                end_type = re.search(r'End\s+(Sub|Function)', line_clean, re.IGNORECASE).group(1)
                if not proc_stack:
                    self.errors.append((i, f"'End {end_type}' without matching '{end_type}'"))
                else:
                    start_line, start_type = proc_stack.pop()
                    if start_type.lower() != end_type.lower():
                        self.errors.append((i, f"'End {end_type}' does not match '{start_type}' at line {start_line}"))

        # Check for unclosed procedures
        for start_line, proc_type in proc_stack:
            self.errors.append((start_line, f"'{proc_type}' not closed with 'End {proc_type}'"))

    def check_undeclared_variables(self):
        """Check for common undeclared variable patterns (basic check)."""
        # Extract declared variables
        declared = set()
        for line in self.lines:
            # Dim, As, Const declarations
            if re.search(r'\b(Dim|Const|Public|Private)\s+(\w+)', line, re.IGNORECASE):
                var_name = re.search(r'\b(Dim|Const|Public|Private)\s+(\w+)', line, re.IGNORECASE).group(2)
                declared.add(var_name.lower())

        # Check for assignments to undeclared variables (basic heuristic)
        for i, line in enumerate(self.lines, start=1):
            # Skip comments and declarations
            if line.strip().startswith("'") or re.search(r'\b(Dim|Const|Public|Private)\s+', line, re.IGNORECASE):
                continue

            # Look for assignment (var = ...)
            match = re.search(r'\b(\w+)\s*=', line)
            if match:
                var_name = match.group(1).lower()
                # Exclude common VBA keywords/properties
                if var_name not in declared and var_name not in {'set', 'let', 'get', 'call', 'if', 'end', 'for', 'next', 'do', 'loop', 'while'}:
                    self.warnings.append((i, f"Possible undeclared variable: '{match.group(1)}'"))

    def check_common_typos(self):
        """Check for common VBA typos."""
        for i, line in enumerate(self.lines, start=1):
            if re.search(r'\bElse\s+If\b', line, re.IGNORECASE):
                self.warnings.append((i, "Use 'ElseIf' (one word) instead of 'Else If'"))
            if re.search(r'\bEndSub\b', line, re.IGNORECASE):
                self.errors.append((i, "Use 'End Sub' (two words) instead of 'EndSub'"))
            if re.search(r'\bEndFunction\b', line, re.IGNORECASE):
                self.errors.append((i, "Use 'End Function' (two words) instead of 'EndFunction'"))

    def check_line_continuations(self):
        """Check for broken line continuations."""
        for i, line in enumerate(self.lines, start=1):
            # Line continuation must have space before underscore
            if re.search(r'\S_\s*$', line):
                self.warnings.append((i, "Line continuation: add space before '_'"))

    def print_results(self):
        """Print errors and warnings."""
        if not self.errors and not self.warnings:
            print(f"✅ {self.filepath.name}: No issues found")
            return

        print(f"\n{'='*60}")
        print(f"File: {self.filepath}")
        print(f"{'='*60}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for line_num, msg in sorted(self.errors):
                print(f"  Line {line_num}: {msg}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for line_num, msg in sorted(self.warnings):
                print(f"  Line {line_num}: {msg}")

        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/lint_vba.py <file.bas>")
        print("   or: python scripts/lint_vba.py Excel/Templates/*.bas")
        sys.exit(1)

    files = [Path(arg) for arg in sys.argv[1:]]
    all_pass = True

    for filepath in files:
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            all_pass = False
            continue

        linter = VBALinter(filepath)
        if not linter.lint():
            all_pass = False

    if all_pass:
        print("\n✅ All files passed validation")
        sys.exit(0)
    else:
        print("\n❌ Some files have errors - fix before importing to Excel")
        sys.exit(1)

if __name__ == '__main__':
    main()
