#!/usr/bin/env python3
"""
Comprehensive Streamlit App Issue Detector

Scans ALL Streamlit pages for common issues:
- NameError (undefined variables)
- AttributeError (session state access)
- KeyError (direct dict access)
- ZeroDivisionError (division without checks)
- ImportError (imports inside functions)
- TypeError (wrong function args)

Part of comprehensive prevention system (Phase 1A + Phase 2).

Usage:
    python scripts/check_streamlit_issues.py --all-pages
    python scripts/check_streamlit_issues.py --page beam_design
    python scripts/check_streamlit_issues.py --all-pages --fail-on critical,high
    python scripts/check_streamlit_issues.py --all-pages --ignore-file .scanner-ignore.yml
"""

import ast
import sys
import argparse
import yaml
from pathlib import Path
from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict


class IgnoreConfig:
    """Configuration for ignored issues."""

    def __init__(self, config_path: Optional[Path] = None):
        self.ignored_lines: Dict[str, Set[int]] = defaultdict(set)
        self.ignored_patterns: List[Dict] = []

        if config_path and config_path.exists():
            self._load_config(config_path)

    def _load_config(self, config_path: Path):
        """Load ignore configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}

            # Parse false_positives section
            false_positives = config.get('false_positives', [])
            for item in false_positives:
                file_pattern = item.get('file', '')
                lines = item.get('lines', [])

                # Store ignored lines per file
                for line in lines:
                    self.ignored_lines[file_pattern].add(line)

            # Parse known_issues section (for documentation, not ignored)
            # These are real issues that are acknowledged but not yet fixed

        except Exception as e:
            print(f"⚠️  Warning: Failed to load ignore config: {e}")

    def should_ignore(self, filepath: str, line: int) -> bool:
        """Check if an issue at this location should be ignored."""
        filename = Path(filepath).name

        # Check exact filename match
        if line in self.ignored_lines.get(filename, set()):
            return True

        # Check pattern matches
        for pattern_file, ignored_lines in self.ignored_lines.items():
            if pattern_file in filepath and line in ignored_lines:
                return True

        return False


class EnhancedIssueDetector(ast.NodeVisitor):
    """Enhanced AST visitor with scope tracking for NameError detection."""

    def __init__(self, filepath: str, ignore_config: Optional[IgnoreConfig] = None):
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)
        self.ignore_config = ignore_config

        # Scope tracking for NameError detection
        self.scopes: List[Set[str]] = [set()]  # Stack of scopes (sets of defined vars)
        self.imported_names: Set[str] = set()  # Track imports
        # Add common builtins that are always available
        self.builtin_names: Set[str] = set(dir(__builtins__)) | {
            'print', 'len', 'range', 'int', 'float', 'str', 'list', 'dict',
            'tuple', 'set', 'frozenset', 'bool', 'type', 'isinstance',
            'hasattr', 'getattr', 'setattr', 'sum', 'min', 'max', 'abs',
            'round', 'sorted', 'reversed', 'enumerate', 'zip', 'map',
            'filter', 'all', 'any', 'open', 'hash', 'id', 'ord', 'chr',
            # Standard exception names
            'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
            'AttributeError', 'NameError', 'ZeroDivisionError', 'RuntimeError',
            'ImportError', 'IOError', 'OSError',
        }  # Python builtins

        # Track Path types for division operator detection
        self.path_like_vars: Set[str] = set()  # Variables that are Path objects

        # Session state tracking
        self.session_state_keys: Set[str] = set()  # Track keys set in session state

        # Function tracking
        self.in_function = False
        self.function_name = ""
        self.current_class = None

        # Division safety tracking
        self.safe_denominators: Set[str] = set()  # Variables validated as non-zero
        self.parent_nodes: List[ast.AST] = []  # Stack for tracking parent nodes
        self.in_conditional = False  # Track if we're inside a conditional branch

    def add_issue(self, line: int, severity: str, message: str):
        """Add an issue, respecting ignore configuration."""
        if self.ignore_config and self.ignore_config.should_ignore(self.filepath, line):
            return  # Issue is ignored
        self.issues.append((line, severity, message))

    def visit(self, node: ast.AST):
        """Override visit to track parent nodes."""
        self.parent_nodes.append(node)
        result = super().visit(node)
        self.parent_nodes.pop()
        return result

    def enter_scope(self):
        """Enter a new scope."""
        self.scopes.append(set())

    def exit_scope(self):
        """Exit current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def add_defined_name(self, name: str):
        """Add a name to current scope."""
        if self.scopes:
            self.scopes[-1].add(name)

    def is_defined(self, name: str) -> bool:
        """Check if name is defined in any visible scope."""
        # Check all scopes (from innermost to outermost)
        for scope in reversed(self.scopes):
            if name in scope:
                return True

        # Check imports
        if name in self.imported_names:
            return True

        # Check builtins
        if name in self.builtin_names:
            return True

        # Special Streamlit names
        streamlit_names = {'st', 'pd', 'np', 'plt'}
        if name in streamlit_names:
            return True

        return False

    def visit_Import(self, node: ast.Import):
        """Track imports and detect imports inside functions."""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            self.imported_names.add(imported_name)
            self.add_defined_name(imported_name)

            # Phase 2: Track Path imports
            if alias.name == 'pathlib' or alias.name.startswith('pathlib.'):
                if 'Path' in alias.name or imported_name == 'Path':
                    self.path_like_vars.add(imported_name)

        # Detect imports inside functions (bad practice)
        if self.in_function:
            for alias in node.names:
                self.add_issue(
                    node.lineno,
                    "HIGH",
                    f"Import '{alias.name}' inside function '{self.function_name}' (move to module level)"
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from...import and detect inside functions."""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            if imported_name != '*':
                self.imported_names.add(imported_name)
                self.add_defined_name(imported_name)

                # Phase 2: Track Path imports
                if node.module == 'pathlib' and (alias.name == 'Path' or imported_name == 'Path'):
                    self.path_like_vars.add(imported_name)

        # Detect imports inside functions
        if self.in_function:
            module = node.module or ""
            self.add_issue(
                node.lineno,
                "HIGH",
                f"Import from '{module}' inside function '{self.function_name}' (move to module level)"
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function definitions and scope."""
        self.add_defined_name(node.name)

        old_in_function = self.in_function
        old_function_name = self.function_name

        self.in_function = True
        self.function_name = node.name

        # Enter function scope
        self.enter_scope()

        # Add function parameters to scope
        for arg in node.args.args:
            self.add_defined_name(arg.arg)

        # Phase 2: Add *args and **kwargs to scope
        if node.args.vararg:
            self.add_defined_name(node.args.vararg.arg)
        if node.args.kwarg:
            self.add_defined_name(node.args.kwarg.arg)

        # Check for missing type hints on functions returning dict
        if node.returns is None:
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value:
                    if isinstance(child.value, ast.Dict):
                        self.add_issue(
                            node.lineno,
                            "MEDIUM",
                            f"Function '{node.name}' returns dict without type hint"
                        )
                        break

        self.generic_visit(node)

        # Exit function scope
        self.exit_scope()

        self.in_function = old_in_function
        self.function_name = old_function_name

    def visit_Assign(self, node: ast.Assign):
        """Track variable assignments (Phase 2: improved)."""
        # Check if assigning a Path object
        is_path_assignment = False
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id in self.path_like_vars:
                is_path_assignment = True
        elif isinstance(node.value, ast.BinOp):
            # Path / "string" creates new Path
            if isinstance(node.value.op, ast.Div):
                left_name = self._extract_var_name(node.value.left)
                if left_name in self.path_like_vars:
                    is_path_assignment = True

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.add_defined_name(target.id)
                if is_path_assignment:
                    self.path_like_vars.add(target.id)
            elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                # Unpack tuple/list assignment
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)
            elif isinstance(target, ast.Subscript):
                # Session state assignment: st.session_state["key"] = value
                if isinstance(target.value, ast.Attribute):
                    if (isinstance(target.value.value, ast.Name) and
                        target.value.value.id == 'st' and
                        target.value.attr == 'session_state'):
                        if isinstance(target.slice, ast.Constant):
                            key = target.slice.value
                            if isinstance(key, str):
                                self.session_state_keys.add(key)

        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        """Track lambda parameters as defined names in lambda scope."""
        # Create new scope for lambda
        self.enter_scope()

        # Add lambda parameters to scope
        for arg in node.args.args:
            self.add_defined_name(arg.arg)

        # Visit lambda body
        self.generic_visit(node)

        # Pop lambda scope
        self.exit_scope()

    def visit_ListComp(self, node: ast.ListComp):
        """Track list comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_DictComp(self, node: ast.DictComp):
        """Track dict comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_SetComp(self, node: ast.SetComp):
        """Track set comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        """Track generator expression variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_AugAssign(self, node: ast.AugAssign):
        """Track augmented assignments (+=, -=, etc.)."""
        if isinstance(node.target, ast.Name):
            # For +=, the variable must already exist
            if not self.is_defined(node.target.id):
                self.add_issue(
                    node.lineno,
                    "CRITICAL",
                    f"NameError: '{node.target.id}' used in augmented assignment but not defined"
                )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """Detect undefined variable usage (NameError)."""
        if isinstance(node.ctx, ast.Load):
            # Variable is being read
            if not self.is_defined(node.id):
                # Filter out likely false positives
                if node.id not in ['_', '__name__', '__file__']:
                    self.add_issue(
                        node.lineno,
                        "CRITICAL",
                        f"NameError: name '{node.id}' is not defined (used before assignment or import)"
                    )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """Detect session state access without validation."""
        # Check for st.session_state.key pattern
        if isinstance(node.value, ast.Attribute):
            if (isinstance(node.value.value, ast.Name) and
                node.value.value.id == 'st' and
                node.value.attr == 'session_state'):
                # This is st.session_state.some_key
                attr_name = node.attr
                # Only warn if we haven't seen this key set
                if attr_name not in self.session_state_keys:
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"AttributeError risk: st.session_state.{attr_name} may not exist (use .get() or check 'in')"
                    )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        """Track 'in' checks for session state keys."""
        # Pattern: 'key' in/not in st.session_state
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            if isinstance(op, (ast.In, ast.NotIn)):
                # Check if comparing against st.session_state
                comparator = node.comparators[0]
                if (isinstance(comparator, ast.Attribute) and
                    isinstance(comparator.value, ast.Name) and
                    comparator.value.id == 'st' and
                    comparator.attr == 'session_state'):
                    # Extract the key being checked
                    if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                        key = node.left.value
                        # Mark this key as validated
                        self.session_state_keys.add(key)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        """Detect IndexError and KeyError risks."""
        # KeyError: dict access with string keys
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            # Skip safe patterns (list indexing with int)
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                # String key access - likely dict access
                if var_name in ['result', 'inputs', 'design_result', 'flexure',
                                'shear', 'detailing', 'data', 'config']:
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"KeyError risk: '{var_name}[{repr(node.slice.value)}]' may raise KeyError (use .get() with default)"
                    )

        # Session state subscript: st.session_state["key"]
        if isinstance(node.value, ast.Attribute):
            if (isinstance(node.value.value, ast.Name) and
                node.value.value.id == 'st' and
                node.value.attr == 'session_state'):
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value
                    if isinstance(key, str) and key not in self.session_state_keys:
                        self.add_issue(
                            node.lineno,
                            "HIGH",
                            f"KeyError risk: st.session_state[{repr(key)}] may not exist (use .get() or check 'in')"
                        )

        # IndexError: list/tuple access
        if isinstance(node.ctx, ast.Load):
            # Extract container name
            container_name = self._extract_var_name(node.value)

            if container_name:
                # Check for constant index (e.g., items[0], items[5])
                if isinstance(node.slice, ast.Constant):
                    index_value = node.slice.value
                    if isinstance(index_value, int):
                        # Check if bounds validated (look for len() checks)
                        if not self._has_bounds_check_nearby(container_name, index_value):
                            self.add_issue(
                                node.lineno,
                                "MEDIUM",
                                f"IndexError risk: {container_name}[{index_value}] without bounds check (validate len() > {index_value})"
                            )

        self.generic_visit(node)

    def _extract_var_name(self, node: ast.expr) -> Optional[str]:
        """Extract variable name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            # Handle max(x, 1) or dict.get("key", default)
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                # For dict.get(), extract the object name
                return self._extract_var_name(node.func.value)
        elif isinstance(node, ast.BinOp):
            # Handle expressions like: x * 1000, x + 1, etc.
            # Extract the variable (if present)
            left_var = self._extract_var_name(node.left)
            right_var = self._extract_var_name(node.right)
            # Return the first non-None variable
            return left_var if left_var else right_var
        elif isinstance(node, ast.Subscript):
            # Handle dict/list access like: steel["fy"], data[0]
            return self._extract_var_name(node.value)
        return None

    def _is_in_safe_ternary(self, binop_node: ast.BinOp) -> bool:
        """
        Check if the BinOp is inside a ternary expression (IfExp) with zero-check.
        Pattern: expr / denom if denom > 0 else default
        """
        # Look for IfExp parent
        for parent in reversed(self.parent_nodes):
            if isinstance(parent, ast.IfExp):
                # Check if the test validates the denominator
                validated_vars = self._get_validated_vars(parent.test)
                denom_name = self._extract_var_name(binop_node.right)

                # If the denominator matches any validated variable, it's safe
                if denom_name and denom_name in validated_vars:
                    return True
            # Stop at statement boundaries
            elif isinstance(parent, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While)):
                break
        return False

    def _is_zero_check(self, test: ast.expr) -> Optional[str]:
        """
        Check if a comparison is validating a variable against zero.
        Returns the variable name if it's a zero check, None otherwise.
        For compound conditions (AND/OR), returns None (handled by _get_validated_vars).
        """
        if isinstance(test, ast.Compare):
            # Check for patterns like: x > 0, x != 0, 0 < x
            if len(test.ops) == 1 and len(test.comparators) == 1:
                op = test.ops[0]
                left = test.left
                right = test.comparators[0]

                # Check if comparing against zero
                is_zero_left = isinstance(left, ast.Constant) and left.value == 0
                is_zero_right = isinstance(right, ast.Constant) and right.value == 0

                # Pattern: var > 0, var != 0
                if is_zero_right and isinstance(op, (ast.Gt, ast.GtE, ast.NotEq)):
                    return self._extract_var_name(left)

                # Pattern: 0 < var, 0 != var
                if is_zero_left and isinstance(op, (ast.Lt, ast.LtE, ast.NotEq)):
                    return self._extract_var_name(right)

        return None

    def _get_validated_vars(self, test: ast.expr) -> Set[str]:
        """
        Get all variables validated against zero in a test expression.
        Handles compound conditions like: x > 0 and y > 0
        """
        validated_vars = set()

        # Handle BoolOp (and/or)
        if isinstance(test, ast.BoolOp):
            for value in test.values:
                var = self._is_zero_check(value)
                if var:
                    validated_vars.add(var)
        else:
            # Single comparison
            var = self._is_zero_check(test)
            if var:
                validated_vars.add(var)

        return validated_vars

    def visit_If(self, node: ast.If):
        """Track if statements and mark validated denominators."""
        # Check if the test validates any denominators
        validated_vars = self._get_validated_vars(node.test)

        if validated_vars:
            # Add all to safe denominators for the body
            for var in validated_vars:
                self.safe_denominators.add(var)

            # Visit the body where the variables are safe
            for child in node.body:
                self.visit(child)

            # Remove from safe denominators after the body
            for var in validated_vars:
                self.safe_denominators.discard(var)

            # Visit orelse without the validation
            for child in node.orelse:
                self.visit(child)
        else:
            # Normal processing
            self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Detect division operations (ZeroDivisionError risk) - Phase 2: Path-aware."""
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            # Phase 2: Check if this is Path division (Path / "string")
            left_name = self._extract_var_name(node.left)
            if left_name in self.path_like_vars and isinstance(node.op, ast.Div):
                # This is Path division, not arithmetic - safe
                self.generic_visit(node)
                return

            # Check if left operand is a Path call: Path(...) / "string"
            if isinstance(node.left, ast.Call):
                if isinstance(node.left.func, ast.Name) and node.left.func.id in self.path_like_vars:
                    self.generic_visit(node)
                    return

            # Check if denominator is obviously safe
            is_safe = False

            # Check if it's a constant (not zero)
            if isinstance(node.right, ast.Constant):
                if isinstance(node.right.value, (int, float)) and node.right.value != 0:
                    is_safe = True

            # Check if denominator is a validated variable
            if not is_safe:
                denom_name = self._extract_var_name(node.right)
                if denom_name and denom_name in self.safe_denominators:
                    is_safe = True

            # Check if inside a ternary expression with zero-check
            if not is_safe:
                if self._is_in_safe_ternary(node):
                    is_safe = True

            if not is_safe:
                op_name = {ast.Div: '/', ast.FloorDiv: '//', ast.Mod: '%'}[type(node.op)]
                self.add_issue(
                    node.lineno,
                    "CRITICAL",
                    f"ZeroDivisionError risk: division '{op_name}' without obvious zero check (validate denominator)"
                )

        self.generic_visit(node)

    def _has_bounds_check_nearby(self, container: str, index: int) -> bool:
        """Check if there's a len() check for this container/index nearby."""
        # Look through parent nodes for if statements with len() checks
        for parent in self.parent_nodes[-5:]:  # Check last 5 parent nodes
            if isinstance(parent, ast.If):
                # Check if test contains len(container)
                test_str = ast.unparse(parent.test) if hasattr(ast, 'unparse') else ""
                if f"len({container})" in test_str and str(index) in test_str:
                    return True
        return False

    def _is_in_try_except(self) -> bool:
        """Check if current node is inside a try/except block."""
        for parent in self.parent_nodes:
            if isinstance(parent, ast.Try):
                return True
        return False

    def visit_For(self, node: ast.For):
        """Track for loop variables (Phase 2: improved tuple unpacking)."""
        self._add_target_names(node.target)
        self.generic_visit(node)

    def _add_target_names(self, target):
        """Recursively add names from assignment targets (handles nested unpacking)."""
        if isinstance(target, ast.Name):
            self.add_defined_name(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._add_target_names(elt)  # Recursive for nested unpacking
        elif isinstance(target, ast.Starred):
            self._add_target_names(target.value)

    def visit_With(self, node: ast.With):
        """Track with statement variables."""
        for item in node.items:
            if item.optional_vars:
                if isinstance(item.optional_vars, ast.Name):
                    self.add_defined_name(item.optional_vars.id)

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Track exception variable."""
        if node.name:
            self.add_defined_name(node.name)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """
        Detect TypeError and ValueError risks in function calls.

        Checks for:
        - hash()/frozenset() on unhashable types (lists, dicts)
        - int()/float() without try/except (ValueError)
        - Common type mismatches
        """
        func_name = None

        # Extract function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

        # Check for hash() with unhashable types
        if func_name == 'hash':
            if node.args:
                arg = node.args[0]

                # Direct unhashable types: hash([...]), hash({...}), hash({x: y})
                if isinstance(arg, (ast.List, ast.Set, ast.Dict)):
                    type_name = {ast.List: "list", ast.Set: "set", ast.Dict: "dict"}[type(arg)]
                    self.add_issue(
                        node.lineno,
                        "CRITICAL",
                        f"TypeError: hash() called on unhashable type (lists/dicts/sets cannot be hashed)"
                    )

                # Risky pattern: hash(frozenset(dict.items()))
                elif isinstance(arg, ast.Call):
                    if (isinstance(arg.func, ast.Name) and arg.func.id == 'frozenset' and
                        arg.args and isinstance(arg.args[0], ast.Call)):
                        inner_call = arg.args[0]
                        if (isinstance(inner_call.func, ast.Attribute) and
                            inner_call.func.attr == 'items'):
                            self.add_issue(
                                node.lineno,
                                "HIGH",
                                "TypeError risk: hash(frozenset(dict.items()) fails if dict contains unhashable values (validate first)"
                            )

        # Check for frozenset() with unhashable types
        if func_name == 'frozenset' and node.args:
            arg = node.args[0]

            # Direct list/dict/set literals are unhashable
            if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                self.add_issue(
                    node.lineno,
                    "CRITICAL",
                    f"TypeError: frozenset() called on unhashable type (lists/dicts/sets cannot be hashed)"
                )

            # Check for .items() which returns unhashable tuples containing unhashable values
            elif isinstance(arg, ast.Call):
                if isinstance(arg.func, ast.Attribute) and arg.func.attr == 'items':
                    # dict.items() returns unhashable if dict values are unhashable
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"TypeError risk: frozenset(dict.items()) may fail if dict contains unhashable values (lists, dicts). Use make_hashable() helper."
                    )

        # Check for int() / float() without error handling
        if func_name in ('int', 'float'):
            # Only flag if there are arguments (conversion attempt)
            if node.args:
                # Check if inside try/except
                if not self._is_in_try_except():
                    self.add_issue(
                        node.lineno,
                        "MEDIUM",
                        f"ValueError risk: {func_name}() without try/except (invalid input will crash)"
                    )

        self.generic_visit(node)


def check_file(filepath: Path, ignore_config: Optional[IgnoreConfig] = None) -> List[Tuple[int, str, str]]:
    """Check a single file for issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source, filename=str(filepath))

        detector = EnhancedIssueDetector(str(filepath), ignore_config=ignore_config)
        detector.visit(tree)

        return detector.issues

    except SyntaxError as e:
        return [(e.lineno or 0, "ERROR", f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, "ERROR", f"Failed to parse file: {e}")]


def scan_all_pages(pages_dir: Path, ignore_config: Optional[IgnoreConfig] = None) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan all Streamlit pages."""
    results = {}

    # Find all Python files in pages directory
    page_files = sorted(pages_dir.glob("*.py"))

    if not page_files:
        print(f"⚠️  No Python files found in {pages_dir}")
        return results

    for page_file in page_files:
        issues = check_file(page_file, ignore_config=ignore_config)
        results[page_file.name] = issues

    return results


def print_results(results: Dict[str, List[Tuple[int, str, str]]],
                  fail_on: List[str] = None) -> int:
    """Print scan results and return exit code."""
    all_issues = []
    total_files = len(results)
    files_with_issues = 0

    print("=" * 80)
    print("🔍 STREAMLIT APP COMPREHENSIVE SCAN RESULTS")
    print("=" * 80)
    print()

    for filename, issues in sorted(results.items()):
        if not issues:
            print(f"✅ {filename}: No issues found")
            continue

        files_with_issues += 1
        all_issues.extend(issues)

        # Group by severity
        critical = [i for i in issues if i[1] == "CRITICAL"]
        high = [i for i in issues if i[1] == "HIGH"]
        medium = [i for i in issues if i[1] == "MEDIUM"]
        errors = [i for i in issues if i[1] == "ERROR"]

        print(f"📄 {filename}:")
        print(f"   Issues: {len(issues)} (Critical: {len(critical)}, High: {len(high)}, Medium: {len(medium)})")

        if errors:
            print("   ❌ ERRORS:")
            for line, severity, message in errors:
                print(f"      Line {line}: {message}")

        if critical:
            print("   🔴 CRITICAL:")
            for line, severity, message in critical:
                print(f"      Line {line}: {message}")

        if high:
            print("   🟠 HIGH:")
            for line, severity, message in high:
                print(f"      Line {line}: {message}")

        if medium:
            print("   🟡 MEDIUM:")
            for line, severity, message in medium:
                print(f"      Line {line}: {message}")

        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    total_issues = len(all_issues)
    critical_count = len([i for i in all_issues if i[1] == "CRITICAL"])
    high_count = len([i for i in all_issues if i[1] == "HIGH"])
    medium_count = len([i for i in all_issues if i[1] == "MEDIUM"])
    error_count = len([i for i in all_issues if i[1] == "ERROR"])

    print(f"Files scanned: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues: {total_issues}")
    print(f"  - Errors: {error_count}")
    print(f"  - Critical: {critical_count}")
    print(f"  - High: {high_count}")
    print(f"  - Medium: {medium_count}")
    print()

    # Determine exit code
    if fail_on:
        should_fail = False
        for severity in fail_on:
            severity_upper = severity.upper()
            count = len([i for i in all_issues if i[1] == severity_upper])
            if count > 0:
                should_fail = True
                print(f"⚠️  Failing due to {count} {severity_upper} issue(s)")

        if should_fail:
            return 1

    if error_count > 0:
        return 1

    if total_issues == 0:
        print("✅ All pages look good!")
    else:
        print("⚠️  Issues found. Review and fix before merging.")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Streamlit app issue detector"
    )
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Scan all pages in streamlit_app/pages/"
    )
    parser.add_argument(
        "--page",
        type=str,
        help="Scan specific page (e.g., 'beam_design' for 01_beam_design.py)"
    )
    parser.add_argument(
        "--fail-on",
        type=str,
        help="Comma-separated list of severities to fail on (e.g., 'critical,high')"
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Shortcut for --fail-on critical (exit 1 if any critical issues found)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--ignore-file",
        type=str,
        default=".scanner-ignore.yml",
        help="Path to ignore configuration file (default: .scanner-ignore.yml)"
    )

    args = parser.parse_args()

    # Parse fail-on severities
    fail_on_severities = None
    if args.fail_on_critical:
        fail_on_severities = ['critical']
    elif args.fail_on:
        fail_on_severities = [s.strip() for s in args.fail_on.split(',')]

    # Determine project root
    project_root = Path(__file__).parent.parent
    pages_dir = project_root / "streamlit_app" / "pages"

    # Load ignore configuration
    ignore_file_path = project_root / args.ignore_file
    ignore_config = IgnoreConfig(ignore_file_path) if ignore_file_path.exists() else None

    if ignore_config and args.verbose:
        print(f"📋 Loaded ignore config from {ignore_file_path}")

    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return 1

    # Scan pages
    if args.all_pages:
        results = scan_all_pages(pages_dir, ignore_config=ignore_config)
        return print_results(results, fail_on_severities)

    elif args.page:
        # Find page file matching pattern
        matching_files = list(pages_dir.glob(f"*{args.page}*.py"))
        if not matching_files:
            print(f"❌ No page found matching '{args.page}'")
            return 1

        page_file = matching_files[0]
        print(f"🔍 Checking {page_file.name}...\n")

        issues = check_file(page_file, ignore_config=ignore_config)
        results = {page_file.name: issues}
        return print_results(results, fail_on_severities)

    else:
        print("❌ Please specify --all-pages or --page <name>")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
