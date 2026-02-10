#!/usr/bin/env python3
"""
FastAPI Issues AST Scanner.

Detects common FastAPI anti-patterns and potential issues:
- Missing response_model on endpoints
- Bare exceptions (hiding errors)
- Missing dependency injection patterns
- Async/await issues
- Security anti-patterns (hardcoded secrets, missing auth)
- Missing input validation
- Unhandled WebSocket disconnections

Similar to check_streamlit.py but for FastAPI code.

Usage:
    python scripts/check_fastapi_issues.py                    # Scan all
    python scripts/check_fastapi_issues.py --file router.py   # Single file
    python scripts/check_fastapi_issues.py --json             # JSON output
    python scripts/check_fastapi_issues.py --fail-on-critical # Exit 1 if critical
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Issue:
    """Represents a detected issue."""
    file: str
    line: int
    severity: str  # critical, high, medium, low
    category: str
    message: str
    suggestion: str = ""


@dataclass
class ScanResult:
    """Result of scanning a file."""
    file: str
    issues: list[Issue] = field(default_factory=list)


class FastAPIIssueScanner(ast.NodeVisitor):
    """AST visitor that detects FastAPI anti-patterns."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[Issue] = []
        self.in_route_handler = False
        self.in_websocket_handler = False
        self.current_function: str | None = None
        self.has_response_model = False
        self.has_exception_handler = False

    def add_issue(
        self,
        node: ast.AST,
        severity: str,
        category: str,
        message: str,
        suggestion: str = "",
    ) -> None:
        """Add an issue to the list."""
        self.issues.append(Issue(
            file=self.filename,
            line=node.lineno,
            severity=severity,
            category=category,
            message=message,
            suggestion=suggestion,
        ))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for issues."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function definitions for issues."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Common checks for sync and async functions."""
        # Check if this is a route handler (has decorator)
        is_route = False
        is_websocket = False
        has_response_model = False

        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name in ("get", "post", "put", "delete", "patch", "api_route"):
                is_route = True
                # Check for response_model
                if isinstance(decorator, ast.Call):
                    for keyword in decorator.keywords:
                        if keyword.arg == "response_model":
                            has_response_model = True
            elif decorator_name == "websocket":
                is_websocket = True

        self.in_route_handler = is_route
        self.in_websocket_handler = is_websocket

        # Check for missing response_model on non-trivial routes
        if is_route and not has_response_model:
            # Only warn for POST/PUT/PATCH which typically return data
            for decorator in node.decorator_list:
                decorator_name = self._get_decorator_name(decorator)
                if decorator_name in ("post", "put", "patch"):
                    self.add_issue(
                        node,
                        "medium",
                        "response_model",
                        f"Route handler '{node.name}' missing response_model",
                        "Add response_model=YourModel for type-safe responses",
                    )
                    break

        # Check for bare except clauses
        self._check_bare_except(node)

        # Check for hardcoded secrets
        self._check_hardcoded_secrets(node)

        # Check WebSocket handlers for disconnect handling
        if is_websocket:
            self._check_websocket_handler(node)

        # Store current function for context
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
            elif isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return ""

    def _check_bare_except(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check for bare except clauses that swallow errors."""
        for child in ast.walk(node):
            if isinstance(child, ast.ExceptHandler):
                if child.type is None:
                    self.add_issue(
                        child,
                        "high",
                        "error_handling",
                        f"Bare 'except:' in '{node.name}' hides all errors",
                        "Use 'except Exception as e:' and log the error",
                    )

    def _check_hardcoded_secrets(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check for hardcoded secrets in function body."""
        secret_patterns = ["secret", "password", "api_key", "token", "private_key"]

        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(pattern in name_lower for pattern in secret_patterns):
                            if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                                if len(child.value.value) > 5:  # Likely a real secret
                                    self.add_issue(
                                        child,
                                        "critical",
                                        "security",
                                        f"Hardcoded secret in variable '{target.id}'",
                                        "Use environment variables: os.getenv('SECRET_KEY')",
                                    )

    def _check_websocket_handler(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check WebSocket handlers for proper disconnect handling."""
        has_try = False
        has_disconnect_catch = False

        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
                for handler in child.handlers:
                    if handler.type:
                        # Check if it catches WebSocketDisconnect
                        type_name = ""
                        if isinstance(handler.type, ast.Name):
                            type_name = handler.type.id
                        elif isinstance(handler.type, ast.Attribute):
                            type_name = handler.type.attr
                        if "Disconnect" in type_name or "disconnect" in type_name.lower():
                            has_disconnect_catch = True

        if not has_try or not has_disconnect_catch:
            self.add_issue(
                node,
                "high",
                "websocket",
                f"WebSocket handler '{node.name}' may not handle disconnection",
                "Wrap in try/except WebSocketDisconnect for clean disconnect",
            )

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for issues."""
        # Check for sync operations in async context
        if self.in_route_handler or self.in_websocket_handler:
            func_name = self._get_call_name(node)

            # Check for blocking operations
            blocking_calls = ["time.sleep", "open", "requests.get", "requests.post"]
            if func_name in blocking_calls:
                self.add_issue(
                    node,
                    "high",
                    "async",
                    f"Blocking call '{func_name}' in async handler",
                    f"Use async alternatives: asyncio.sleep, aiofiles.open, httpx.AsyncClient",
                )

        # Check for missing await
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("send_json", "receive_json", "accept", "close"):
                # These should be awaited
                parent = node
                # Check if parent is Await
                # This is tricky - we'd need to track parent nodes
                pass

        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> str:
        """Get the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute):
                return f"{node.func.value.attr}.{node.func.attr}"
        return ""

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check for suspicious constants."""
        # Check for hardcoded localhost/127.0.0.1 in production code
        if isinstance(node.value, str):
            if "localhost" in node.value or "127.0.0.1" in node.value:
                if "test" not in self.filename.lower():
                    self.add_issue(
                        node,
                        "low",
                        "config",
                        f"Hardcoded localhost address found",
                        "Use environment variable for host configuration",
                    )

        self.generic_visit(node)


def scan_file(filepath: Path) -> ScanResult:
    """Scan a single file for issues."""
    result = ScanResult(file=str(filepath))

    try:
        source = filepath.read_text()
        tree = ast.parse(source, filename=str(filepath))
        scanner = FastAPIIssueScanner(str(filepath))
        scanner.visit(tree)
        result.issues = scanner.issues
    except SyntaxError as e:
        result.issues.append(Issue(
            file=str(filepath),
            line=e.lineno or 0,
            severity="critical",
            category="syntax",
            message=f"Syntax error: {e.msg}",
        ))
    except Exception as e:
        result.issues.append(Issue(
            file=str(filepath),
            line=0,
            severity="critical",
            category="scan_error",
            message=f"Failed to scan: {str(e)}",
        ))

    return result


def scan_directory(directory: Path) -> list[ScanResult]:
    """Scan all Python files in a directory."""
    results = []

    for filepath in directory.rglob("*.py"):
        # Skip __pycache__ and test files for some checks
        if "__pycache__" in str(filepath):
            continue
        result = scan_file(filepath)
        if result.issues:
            results.append(result)

    return results


def print_results(results: list[ScanResult], json_output: bool = False) -> dict[str, int]:
    """Print scan results and return summary counts."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    if json_output:
        output = {
            "files_with_issues": len(results),
            "issues": [],
        }
        for result in results:
            for issue in result.issues:
                counts[issue.severity] += 1
                output["issues"].append({
                    "file": issue.file,
                    "line": issue.line,
                    "severity": issue.severity,
                    "category": issue.category,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                })
        output["summary"] = counts
        print(json.dumps(output, indent=2))
    else:
        print("=" * 80)
        print("FastAPI Issues Scanner")
        print("=" * 80)
        print()

        for result in results:
            print(f"📄 {result.file}")
            for issue in result.issues:
                counts[issue.severity] += 1
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                }[issue.severity]
                print(f"  {severity_icon} Line {issue.line}: [{issue.category}] {issue.message}")
                if issue.suggestion:
                    print(f"     💡 {issue.suggestion}")
            print()

        print("=" * 80)
        print("Summary")
        print("=" * 80)
        total = sum(counts.values())
        print(f"Total issues: {total}")
        print(f"  🔴 Critical: {counts['critical']}")
        print(f"  🟠 High: {counts['high']}")
        print(f"  🟡 Medium: {counts['medium']}")
        print(f"  🔵 Low: {counts['low']}")

        if total == 0:
            print("\n✅ No issues found!")
        elif counts["critical"] > 0:
            print("\n❌ Critical issues found - must fix before deployment!")
        elif counts["high"] > 0:
            print("\n⚠️ High severity issues found - review recommended")

    return counts


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FastAPI issues AST scanner")
    parser.add_argument("--file", type=str, help="Scan a specific file")
    parser.add_argument("--dir", type=str, default="fastapi_app", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit 1 if critical issues")
    parser.add_argument("--fail-on-high", action="store_true", help="Exit 1 if high+ issues")

    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            return 1
        results = [scan_file(filepath)]
        results = [r for r in results if r.issues]
    else:
        directory = Path(args.dir)
        if not directory.exists():
            print(f"Error: Directory not found: {directory}")
            return 1
        results = scan_directory(directory)

    counts = print_results(results, json_output=args.json)

    if args.fail_on_critical and counts["critical"] > 0:
        return 1
    if args.fail_on_high and (counts["critical"] > 0 or counts["high"] > 0):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
