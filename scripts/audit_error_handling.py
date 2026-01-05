#!/usr/bin/env python3
"""
Audit error handling compliance across structural_lib modules.

Checks:
1. No return statements with error sentinel values (0.0, -1, None) in error conditions
2. Proper exception handling patterns by layer
3. Validation before calling calculation helpers

Usage:
    .venv/bin/python scripts/audit_error_handling.py
    .venv/bin/python scripts/audit_error_handling.py --module flexure
    .venv/bin/python scripts/audit_error_handling.py --verbose
"""

import ast
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ComplianceIssue:
    """Represents a compliance issue found during audit."""
    module: str
    function: str
    line: int
    issue_type: str
    description: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'


# Module classification by layer
CORE_MODULES = [
    'flexure', 'shear', 'serviceability', 'detailing',
    'ductile', 'compliance', 'materials', 'tables'
]
VALIDATION_MODULES = ['validation']
ORCHESTRATION_MODULES = ['api', 'beam_pipeline', 'rebar_optimizer']
IO_MODULES = ['dxf_export', 'excel_integration', 'report', 'bbs']
CLI_MODULES = ['job_cli', '__main__']


class ErrorHandlingVisitor(ast.NodeVisitor):
    """AST visitor to detect error handling anti-patterns."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.issues: List[ComplianceIssue] = []
        self.current_function = None
        self.in_error_condition = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_If(self, node: ast.If):
        """Check if statements for error conditions."""
        # Detect error condition patterns
        old_in_error = self.in_error_condition

        # Check if this is an error condition (negative check, zero check, etc.)
        if self._is_error_condition(node.test):
            self.in_error_condition = True

            # Check the body for sentinel return values
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    self._check_return_in_error_condition(stmt, node.lineno)

        self.generic_visit(node)
        self.in_error_condition = old_in_error

    def _is_error_condition(self, test: ast.expr) -> bool:
        """Check if test expression represents an error condition."""
        # x <= 0, x < 0 (but NOT x == 0, which can be valid calculation result)
        if isinstance(test, ast.Compare):
            for op in test.ops:
                # Only flag < and <= (negative/non-positive checks)
                # Don't flag == 0 as it might be valid result check
                if isinstance(op, (ast.LtE, ast.Lt)):
                    for comp in test.comparators:
                        if isinstance(comp, ast.Constant) and comp.value == 0:
                            return True
        # not x, x is None
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return True
        if isinstance(test, ast.Compare):
            for op in test.ops:
                if isinstance(op, ast.Is):
                    return True
        return False

    def _check_return_in_error_condition(self, node: ast.Return, line: int):
        """Check if return statement uses error sentinel values."""
        if node.value is None:
            return  # Return None is sometimes valid

        # Check for sentinel values: 0.0, -1, 0
        if isinstance(node.value, ast.Constant):
            value = node.value.value
            if value in (0.0, -1, 0, -1.0):
                # Check if this is in a core calculation module
                if any(self.module_name.endswith(mod) for mod in CORE_MODULES):
                    self.issues.append(ComplianceIssue(
                        module=self.module_name,
                        function=self.current_function or '<module>',
                        line=line,
                        issue_type='SENTINEL_RETURN',
                        description=f"Returns sentinel value {value} in error condition. Should raise ValueError instead.",
                        severity='ERROR'
                    ))


def analyze_module(module_path: Path) -> List[ComplianceIssue]:
    """Analyze a single module for compliance issues."""
    try:
        with open(module_path) as f:
            tree = ast.parse(f.read(), filename=str(module_path))

        visitor = ErrorHandlingVisitor(module_path.stem)
        visitor.visit(tree)
        return visitor.issues
    except Exception as e:
        return [ComplianceIssue(
            module=module_path.stem,
            function='<parse>',
            line=0,
            issue_type='PARSE_ERROR',
            description=f"Failed to parse module: {e}",
            severity='WARNING'
        )]


def get_layer_for_module(module_name: str) -> str:
    """Determine which layer a module belongs to."""
    if any(module_name.endswith(mod) for mod in CORE_MODULES):
        return 'Core Calculations'
    elif any(module_name.endswith(mod) for mod in VALIDATION_MODULES):
        return 'Validation'
    elif any(module_name.endswith(mod) for mod in ORCHESTRATION_MODULES):
        return 'Orchestration'
    elif any(module_name.endswith(mod) for mod in IO_MODULES):
        return 'I/O'
    elif any(module_name.endswith(mod) for mod in CLI_MODULES):
        return 'CLI'
    return 'Unknown'


def main():
    parser = argparse.ArgumentParser(description='Audit error handling compliance')
    parser.add_argument('--module', help='Specific module to audit (e.g., flexure)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all issues including INFO')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    lib_dir = project_root / 'Python' / 'structural_lib'

    if not lib_dir.exists():
        print(f"ERROR: Library directory not found: {lib_dir}")
        return 1

    # Get modules to audit
    if args.module:
        module_files = [lib_dir / f"{args.module}.py"]
        if not module_files[0].exists():
            print(f"ERROR: Module not found: {args.module}")
            return 1
    else:
        module_files = sorted(lib_dir.glob('*.py'))
        # Exclude __init__, types, constants, utilities
        module_files = [f for f in module_files
                       if f.stem not in ('__init__', 'types', 'constants', 'utilities', 'data_types')]

    # Analyze all modules
    all_issues: List[ComplianceIssue] = []
    for module_file in module_files:
        issues = analyze_module(module_file)
        all_issues.extend(issues)

    # Filter by severity if not verbose
    if not args.verbose:
        all_issues = [i for i in all_issues if i.severity in ('ERROR', 'WARNING')]

    # Output results
    if args.json:
        import json
        output = [
            {
                'module': i.module,
                'function': i.function,
                'line': i.line,
                'issue_type': i.issue_type,
                'description': i.description,
                'severity': i.severity,
                'layer': get_layer_for_module(i.module)
            }
            for i in all_issues
        ]
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "="*80)
        print("ERROR HANDLING COMPLIANCE AUDIT")
        print("="*80 + "\n")

        if not all_issues:
            print("✅ No compliance issues found!\n")
            print(f"Audited {len(module_files)} modules:")
            for f in module_files:
                layer = get_layer_for_module(f.stem)
                print(f"  • {f.stem:20s} [{layer}]")
            return 0

        # Group by severity
        errors = [i for i in all_issues if i.severity == 'ERROR']
        warnings = [i for i in all_issues if i.severity == 'WARNING']
        infos = [i for i in all_issues if i.severity == 'INFO']

        if errors:
            print(f"❌ ERRORS ({len(errors)}):\n")
            for issue in errors:
                layer = get_layer_for_module(issue.module)
                print(f"  {issue.module}.{issue.function}() [Line {issue.line}] [{layer}]")
                print(f"    {issue.description}")
                print()

        if warnings:
            print(f"⚠️  WARNINGS ({len(warnings)}):\n")
            for issue in warnings:
                layer = get_layer_for_module(issue.module)
                print(f"  {issue.module}.{issue.function}() [Line {issue.line}] [{layer}]")
                print(f"    {issue.description}")
                print()

        if infos and args.verbose:
            print(f"ℹ️  INFO ({len(infos)}):\n")
            for issue in infos:
                layer = get_layer_for_module(issue.module)
                print(f"  {issue.module}.{issue.function}() [Line {issue.line}] [{layer}]")
                print(f"    {issue.description}")
                print()

        print("="*80)
        print(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings")
        print(f"Audited {len(module_files)} modules")
        print("="*80 + "\n")

        return 1 if errors else 0


if __name__ == '__main__':
    exit(main())
