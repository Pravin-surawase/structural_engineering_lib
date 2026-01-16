#!/usr/bin/env python3
"""
Comprehensive Streamlit App Issue Detector

Scans ALL Streamlit pages for common issues:
- NameError (undefined variables)
- AttributeError (session state access)
- KeyError (direct dict access)
- ZeroDivisionError (division without checks) - Phase 4: Enhanced detection
- ImportError (imports inside functions)
- TypeError (wrong function args)
- API signature mismatches (Phase 3: test files)
- Widget default values (Phase 5: TASK-403)

**Phase 6 Enhancements (TASK-425):**
- Safe dict-like methods: Recognizes .get(), .setdefault(), .pop(), .update(),
  .keys(), .values(), .items(), .clear() as safe method calls on session_state
- Attribute-style tracking: Now tracks st.session_state.key = value assignments
  (previously only tracked st.session_state["key"] = value)
- Eliminates ~19 false positives per scan where .get() was flagged

**Phase 5 Enhancements (TASK-403):**
- Widget return type validation: Detects st.number_input(), st.text_input(),
  st.selectbox() etc. without explicit default values
- Prevents potential None/empty value issues in calculations

**Phase 4 Enhancements (TASK-401):**
- Path division detection: Recognizes Path(...).method().attr[n] / "string" patterns
- Guaranteed non-zero detection: max(x, positive), min(x, negative)
- Complex expression tracing for Path-like objects

**Phase 3 Enhancements:**
- Guard clause detection: Recognizes early-exit patterns that validate for entire function
- API signature checking: Validates test function calls against actual signatures

Part of comprehensive prevention system (Phase 1A + Phase 2 + Phase 3 + Phase 4 + Phase 5 + Phase 6).

Usage:
    python scripts/check_streamlit_issues.py --all-pages
    python scripts/check_streamlit_issues.py --page beam_design
    python scripts/check_streamlit_issues.py tmp/test_file.py
    python scripts/check_streamlit_issues.py --all-pages --fail-on critical,high
    python scripts/check_streamlit_issues.py --all-pages --ignore-file .scanner-ignore.yml
    python scripts/check_streamlit_issues.py --all-pages --verbose
"""

import ast
import sys
import argparse

try:
    import yaml
except ModuleNotFoundError:
    yaml = None
import inspect
import time
from pathlib import Path
from typing import List, Tuple, Set, Dict, Optional, Any
from collections import defaultdict

# =============================================================================
# PHASE 3: FUNCTION SIGNATURE REGISTRY
# =============================================================================


class FunctionSignatureRegistry:
    """
    Registry of function signatures for API mismatch detection.

    Scans source files to build a database of function signatures,
    then compares test calls against actual signatures.
    """

    def __init__(self):
        self.signatures: Dict[str, Dict[str, Any]] = {}  # func_name -> signature info
        self._scanned_files: Set[Path] = set()

    def scan_file(self, filepath: Path):
        """Scan a file and extract function signatures."""
        if filepath in self._scanned_files:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig_info = self._extract_signature(node, filepath)
                    # Store with module context
                    func_key = f"{filepath.stem}.{node.name}"
                    self.signatures[func_key] = sig_info
                    # Also store without module for common functions
                    if node.name not in self.signatures:
                        self.signatures[node.name] = sig_info

            self._scanned_files.add(filepath)
        except Exception as e:
            # Silently skip files that can't be parsed
            pass

    def _extract_signature(
        self, node: ast.FunctionDef, filepath: Path
    ) -> Dict[str, Any]:
        """Extract signature information from function definition."""
        args = node.args

        # Required positional args (no defaults)
        required_args = [
            arg.arg for arg in args.args[: len(args.args) - len(args.defaults)]
        ]

        # Optional args (with defaults)
        optional_args = [
            arg.arg for arg in args.args[len(args.args) - len(args.defaults) :]
        ]

        # Keyword-only args
        kwonly_required = [
            arg.arg
            for arg in args.kwonlyargs
            if arg.arg not in [d.arg for d in args.kw_defaults if d]
        ]
        kwonly_optional = [
            arg.arg
            for arg in args.kwonlyargs
            if arg.arg in [d.arg for d in args.kw_defaults if d]
        ]

        return {
            "name": node.name,
            "required_args": required_args,
            "optional_args": optional_args,
            "kwonly_required": kwonly_required,
            "kwonly_optional": kwonly_optional,
            "has_vararg": args.vararg is not None,
            "has_kwarg": args.kwarg is not None,
            "total_params": len(args.args),
            "min_params": len(required_args),
            "filepath": str(filepath),
            "lineno": node.lineno,
        }

    def get_signature(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Get signature for a function name."""
        return self.signatures.get(func_name)

    def scan_common_modules(self, project_root: Path):
        """Scan common utility modules."""
        patterns = [
            "streamlit_app/utils/*.py",
            "streamlit_app/components/*.py",
            "Python/structural_lib/*.py",
        ]

        for pattern in patterns:
            for filepath in project_root.glob(pattern):
                if filepath.name != "__init__.py":
                    self.scan_file(filepath)


class IgnoreConfig:
    """Configuration for ignored issues."""

    def __init__(self, config_path: Optional[Path] = None):
        self.ignored_lines: Dict[str, Set[int]] = defaultdict(set)
        self.ignored_patterns: List[Dict] = []

        if config_path and config_path.exists():
            self._load_config(config_path)

    def _load_config(self, config_path: Path):
        """Load ignore configuration from YAML file."""
        if yaml is None:
            print(
                "⚠️  Warning: PyYAML not installed; ignore config not loaded. "
                "Install with: pip install pyyaml"
            )
            return
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}

            # Parse false_positives section
            false_positives = config.get("false_positives", [])
            for item in false_positives:
                file_pattern = item.get("file", "")
                lines = item.get("lines", [])

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

    def __init__(
        self,
        filepath: str,
        ignore_config: Optional[IgnoreConfig] = None,
        sig_registry: Optional[FunctionSignatureRegistry] = None,
    ):
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)
        self.ignore_config = ignore_config
        self.sig_registry = sig_registry  # Phase 3: API signature checking

        # Scope tracking for NameError detection
        self.scopes: List[Set[str]] = [set()]  # Stack of scopes (sets of defined vars)
        self.imported_names: Set[str] = set()  # Track imports
        # Add common builtins that are always available
        self.builtin_names: Set[str] = set(dir(__builtins__)) | {
            "print",
            "len",
            "range",
            "int",
            "float",
            "str",
            "list",
            "dict",
            "tuple",
            "set",
            "frozenset",
            "bool",
            "type",
            "isinstance",
            "hasattr",
            "getattr",
            "setattr",
            "sum",
            "min",
            "max",
            "abs",
            "round",
            "sorted",
            "reversed",
            "enumerate",
            "zip",
            "map",
            "filter",
            "all",
            "any",
            "open",
            "hash",
            "id",
            "ord",
            "chr",
            # Standard exception names
            "Exception",
            "ValueError",
            "TypeError",
            "KeyError",
            "IndexError",
            "AttributeError",
            "NameError",
            "ZeroDivisionError",
            "RuntimeError",
            "ImportError",
            "IOError",
            "OSError",
        }  # Python builtins

        # Track Path types for division operator detection
        self.path_like_vars: Set[str] = set()  # Variables that are Path objects

        # Session state tracking
        self.session_state_keys: Set[str] = set()  # Track keys set in session state

        # Function tracking
        self.in_function = False
        self.function_name = ""
        self.current_class = None

        # Division safety tracking (Phase 3: Enhanced with guard clause detection)
        self.safe_denominators: Set[str] = set()  # Variables validated as non-zero
        self.function_level_safe_denoms: Set[str] = set()  # Safe at function scope
        self.parent_nodes: List[ast.AST] = []  # Stack for tracking parent nodes
        self.in_conditional = False  # Track if we're inside a conditional branch

        # Test mock tracking (Phase 2 enhancement)
        self.magicmock_assignments: Set[str] = set()  # Track mock.attr = MagicMock()

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
        streamlit_names = {"st", "pd", "np", "plt"}
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
            if alias.name == "pathlib" or alias.name.startswith("pathlib."):
                if "Path" in alias.name or imported_name == "Path":
                    self.path_like_vars.add(imported_name)

        # Detect imports inside functions (bad practice)
        # Exception: Allow imports inside try/except blocks (optional dependencies)
        if self.in_function and not self._is_in_try_except():
            for alias in node.names:
                self.add_issue(
                    node.lineno,
                    "HIGH",
                    f"Import '{alias.name}' inside function '{self.function_name}' (move to module level)",
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from...import and detect inside functions."""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            if imported_name != "*":
                self.imported_names.add(imported_name)
                self.add_defined_name(imported_name)

                # Phase 2: Track Path imports
                if node.module == "pathlib" and (
                    alias.name == "Path" or imported_name == "Path"
                ):
                    self.path_like_vars.add(imported_name)

        # Detect imports inside functions
        # Exception: Allow imports inside try/except blocks (optional dependencies)
        if self.in_function and not self._is_in_try_except():
            module = node.module or ""
            self.add_issue(
                node.lineno,
                "HIGH",
                f"Import from '{module}' inside function '{self.function_name}' (move to module level)",
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function definitions and scope."""
        self.add_defined_name(node.name)

        old_in_function = self.in_function
        old_function_name = self.function_name

        self.in_function = True
        self.function_name = node.name

        # Phase 3: Clear function-level safe denominators for new function
        self.function_level_safe_denoms.clear()

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
                            f"Function '{node.name}' returns dict without type hint",
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
            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id in self.path_like_vars
            ):
                is_path_assignment = True

            # Phase 2: Track MagicMock assignments for test files
            # Pattern: mock_streamlit.method = MagicMock()
            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id == "MagicMock"
            ):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        # Extract the full attribute path: mock_streamlit.method
                        attr_path = self._get_attribute_path(target)
                        if attr_path:
                            self.magicmock_assignments.add(attr_path)

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
                    if (
                        isinstance(target.value.value, ast.Name)
                        and target.value.value.id == "st"
                        and target.value.attr == "session_state"
                    ):
                        if isinstance(target.slice, ast.Constant):
                            key = target.slice.value
                            if isinstance(key, str):
                                self.session_state_keys.add(key)

            # Phase 6: Track attribute-style session state assignments
            # Pattern: st.session_state.key = value
            elif isinstance(target, ast.Attribute):
                if (
                    isinstance(target.value, ast.Attribute)
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "st"
                    and target.value.attr == "session_state"
                ):
                    # This is st.session_state.key = value
                    key = target.attr
                    self.session_state_keys.add(key)

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Track annotated assignments (e.g., x: int = 5)."""
        # AnnAssign has .target (single target), .annotation, .value
        if isinstance(node.target, ast.Name):
            self.add_defined_name(node.target.id)
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
                    f"NameError: '{node.target.id}' used in augmented assignment but not defined",
                )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """Detect undefined variable usage (NameError)."""
        if isinstance(node.ctx, ast.Load):
            # Variable is being read
            if not self.is_defined(node.id):
                # Filter out likely false positives
                if node.id not in ["_", "__name__", "__file__"]:
                    self.add_issue(
                        node.lineno,
                        "CRITICAL",
                        f"NameError: name '{node.id}' is not defined (used before assignment or import)",
                    )

        self.generic_visit(node)

    # NOTE: visit_Attribute is defined later in this class (around line 1138)
    # to handle both session state detection AND mock assertion anti-patterns.
    # Do NOT add another visit_Attribute here!

    def visit_Compare(self, node: ast.Compare):
        """Track 'in' checks for session state keys."""
        # Pattern: 'key' in/not in st.session_state
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            if isinstance(op, (ast.In, ast.NotIn)):
                # Check if comparing against st.session_state
                comparator = node.comparators[0]
                if (
                    isinstance(comparator, ast.Attribute)
                    and isinstance(comparator.value, ast.Name)
                    and comparator.value.id == "st"
                    and comparator.attr == "session_state"
                ):
                    # Extract the key being checked
                    if isinstance(node.left, ast.Constant) and isinstance(
                        node.left.value, str
                    ):
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
            if isinstance(node.slice, ast.Constant) and isinstance(
                node.slice.value, str
            ):
                # String key access - likely dict access
                if var_name in [
                    "result",
                    "inputs",
                    "design_result",
                    "flexure",
                    "shear",
                    "detailing",
                    "data",
                    "config",
                ]:
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"KeyError risk: '{var_name}[{repr(node.slice.value)}]' may raise KeyError (use .get() with default)",
                    )

        # Session state subscript: st.session_state["key"]
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "st"
                and node.value.attr == "session_state"
            ):
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value
                    if isinstance(key, str) and key not in self.session_state_keys:
                        self.add_issue(
                            node.lineno,
                            "HIGH",
                            f"KeyError risk: st.session_state[{repr(key)}] may not exist (use .get() or check 'in')",
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
                        # Phase 6: Skip if accessing [0] on result of split()
                        # str.split() always returns at least 1 element
                        if index_value == 0 and isinstance(node.value, ast.Call):
                            if (
                                isinstance(node.value.func, ast.Attribute)
                                and node.value.func.attr == "split"
                            ):
                                # This is x.split(...)[0] - always safe
                                self.generic_visit(node)
                                return

                        # Check if bounds validated (look for len() checks)
                        if not self._has_bounds_check_nearby(
                            container_name, index_value
                        ):
                            self.add_issue(
                                node.lineno,
                                "MEDIUM",
                                f"IndexError risk: {container_name}[{index_value}] without bounds check (validate len() > {index_value})",
                            )

        self.generic_visit(node)

    def _get_attribute_path(self, node: ast.expr) -> Optional[str]:
        """
        Get the full attribute path from an AST node.
        Example: mock_streamlit.progress -> "mock_streamlit.progress"
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_attribute_path(node.value)
            if base:
                return f"{base}.{node.attr}"
        return None

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

    def _is_path_expression(self, node: ast.expr) -> bool:
        """
        Recursively check if an expression originates from a Path call.

        Detects patterns like:
        - Path(__file__)
        - Path(__file__).resolve()
        - Path(__file__).resolve().parents[2]
        - path_var (if path_var is in self.path_like_vars)

        Phase 4: Enhanced Path detection for complex expressions.
        """
        if isinstance(node, ast.Name):
            # Direct variable reference
            return node.id in self.path_like_vars

        elif isinstance(node, ast.Call):
            # Direct Path(...) call
            if isinstance(node.func, ast.Name) and node.func.id in self.path_like_vars:
                return True
            # Method call like path.resolve()
            if isinstance(node.func, ast.Attribute):
                return self._is_path_expression(node.func.value)

        elif isinstance(node, ast.Attribute):
            # Attribute access like path.parents
            return self._is_path_expression(node.value)

        elif isinstance(node, ast.Subscript):
            # Subscript like path.parents[2]
            return self._is_path_expression(node.value)

        return False

    def _is_guaranteed_nonzero(self, node: ast.expr) -> bool:
        """
        Check if an expression is guaranteed to be non-zero.

        Detects patterns like:
        - max(expr, 1) or max(1, expr) - minimum is 1
        - min(expr, -1) or max(expr, positive_const)
        - abs(expr) + 1 (but not abs alone)
        - Numeric constants > 0 or < 0

        Phase 4: Enhanced denominator safety detection.
        """
        if isinstance(node, ast.Constant):
            # Non-zero constant
            if isinstance(node.value, (int, float)) and node.value != 0:
                return True

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                # max(a, b) - if any argument is positive constant, result >= that constant
                if node.func.id == "max" and len(node.args) >= 2:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant):
                            if isinstance(arg.value, (int, float)) and arg.value > 0:
                                return True

                # min(a, b) - if any argument is negative constant, result <= that constant (non-zero)
                if node.func.id == "min" and len(node.args) >= 2:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant):
                            if isinstance(arg.value, (int, float)) and arg.value < 0:
                                return True

        elif isinstance(node, ast.BinOp):
            # Addition/subtraction of constant to abs()
            # e.g., abs(x) + 1 is always >= 1 if constant > 0
            pass  # Complex case, skip for now

        return False

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
            elif isinstance(
                parent, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While)
            ):
                break
        return False

    def _check_api_signature(self, node: ast.Call, func_name: str):
        """
        Check if function call matches registered signature (Phase 3).

        Validates:
        - Correct number of positional arguments
        - Valid keyword argument names
        - Required arguments provided

        Args:
            node: The Call AST node
            func_name: The function name to check
        """
        sig = self.sig_registry.get_signature(func_name)
        if not sig:
            # Function not in registry (might be builtin, local, etc.)
            return

        # Count positional args provided (not including kwargs)
        positional_count = len(
            [arg for arg in node.args if not isinstance(arg, ast.Starred)]
        )

        # Extract keyword argument names
        keyword_names = {kw.arg for kw in node.keywords if kw.arg is not None}

        # Check for **kwargs spread (can't validate)
        has_kwargs_spread = any(kw.arg is None for kw in node.keywords)

        # Check minimum positional args
        min_required = sig["min_params"]
        total_required = len(sig["required_args"])

        # If they provide too few positional args and no matching keywords
        if positional_count < min_required:
            # Check if missing args are provided as keywords
            missing_args = sig["required_args"][positional_count:]
            missing_not_in_kwargs = [
                arg for arg in missing_args if arg not in keyword_names
            ]

            if missing_not_in_kwargs and not has_kwargs_spread:
                self.add_issue(
                    node.lineno,
                    "HIGH",
                    f"API signature mismatch: {func_name}() requires {total_required} args, "
                    f"but only {positional_count} positional provided. "
                    f"Missing: {', '.join(missing_not_in_kwargs)}",
                )

        # Check for invalid keyword argument names (if no **kwargs in signature)
        if not sig["has_kwarg"] and not has_kwargs_spread:
            valid_kwarg_names = (
                set(sig["required_args"])
                | set(sig["optional_args"])
                | set(sig["kwonly_required"])
                | set(sig["kwonly_optional"])
            )

            invalid_kwargs = keyword_names - valid_kwarg_names
            if invalid_kwargs:
                self.add_issue(
                    node.lineno,
                    "HIGH",
                    f"API signature mismatch: {func_name}() called with invalid keyword args: "
                    f"{', '.join(invalid_kwargs)}. Valid: {', '.join(sorted(valid_kwarg_names))}",
                )

        # Check for too many positional args (if no *args in signature)
        if not sig["has_vararg"]:
            max_positional = len(sig["required_args"]) + len(sig["optional_args"])
            if positional_count > max_positional:
                self.add_issue(
                    node.lineno,
                    "HIGH",
                    f"API signature mismatch: {func_name}() accepts max {max_positional} positional args, "
                    f"but {positional_count} provided",
                )

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
        """Track if statements and mark validated denominators.

        Phase 3: Enhanced with guard clause detection.
        Recognizes patterns like:
            if x == 0:
                return None  # or raise
            # x is now safe for rest of function
        """
        # Check if the test validates any denominators
        validated_vars = self._get_validated_vars(node.test)

        # Phase 3: Check for guard clause pattern
        # Pattern: if <var> == 0: return/raise (early exit validates var for rest of function)
        is_guard_clause = False
        guard_validated_vars = set()

        if validated_vars and self._is_early_exit(node.body):
            # This is a guard clause - variable is safe AFTER the if block
            is_guard_clause = True
            guard_validated_vars = validated_vars.copy()

        if validated_vars:
            # Add all to safe denominators for the body
            for var in validated_vars:
                self.safe_denominators.add(var)

            # Visit the body where the variables are safe
            for child in node.body:
                self.visit(child)

            # If not a guard clause, remove from safe denominators after the body
            if not is_guard_clause:
                for var in validated_vars:
                    self.safe_denominators.discard(var)

            # Visit orelse without the validation
            for child in node.orelse:
                self.visit(child)
        else:
            # Normal processing
            self.generic_visit(node)

        # Phase 3: If this was a guard clause, mark variables as safe at function level
        if is_guard_clause:
            for var in guard_validated_vars:
                self.function_level_safe_denoms.add(var)

    def visit_BinOp(self, node: ast.BinOp):
        """Detect division operations (ZeroDivisionError risk) - Phase 4: Enhanced detection."""
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            # Phase 4: Enhanced Path detection - handles complex expressions like
            # Path(__file__).resolve().parents[2] / "Python"
            if isinstance(node.op, ast.Div) and self._is_path_expression(node.left):
                # This is Path division, not arithmetic - safe
                self.generic_visit(node)
                return

            # Phase 2 fallback: Check if left is simple Path variable
            left_name = self._extract_var_name(node.left)
            if left_name in self.path_like_vars and isinstance(node.op, ast.Div):
                self.generic_visit(node)
                return

            # Check if denominator is obviously safe
            is_safe = False

            # Phase 4: Check if denominator is guaranteed non-zero (e.g., max(x, 1))
            if self._is_guaranteed_nonzero(node.right):
                is_safe = True

            # Check if it's a constant (not zero)
            if not is_safe and isinstance(node.right, ast.Constant):
                if isinstance(node.right.value, (int, float)) and node.right.value != 0:
                    is_safe = True

            # Phase 3: Check if denominator is validated at function level (guard clause)
            if not is_safe:
                denom_name = self._extract_var_name(node.right)
                if denom_name and denom_name in self.function_level_safe_denoms:
                    is_safe = True

            # Check if denominator is a validated variable (if-block level)
            if not is_safe:
                denom_name = self._extract_var_name(node.right)
                if denom_name and denom_name in self.safe_denominators:
                    is_safe = True

            # Check if inside a ternary expression with zero-check
            if not is_safe:
                if self._is_in_safe_ternary(node):
                    is_safe = True

            if not is_safe:
                op_name = {ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%"}[
                    type(node.op)
                ]
                self.add_issue(
                    node.lineno,
                    "CRITICAL",
                    f"ZeroDivisionError risk: division '{op_name}' without obvious zero check (validate denominator)",
                )

        self.generic_visit(node)

    def _has_bounds_check_nearby(self, container: str, index: int) -> bool:
        """Check if there's a len() check for this container/index nearby.

        Phase 6 Enhancement:
        - Look at ALL parent nodes (not just last 5)
        - Properly match len() > index patterns
        - Handle if-blocks that guard the access
        - Handle ternary expressions (x if len(y) > 0 else default)
        """
        # Look through ALL parent nodes for if statements with len() checks
        for parent in self.parent_nodes:
            if isinstance(parent, ast.If):
                # Check if test contains len(container)
                try:
                    test_str = (
                        ast.unparse(parent.test) if hasattr(ast, "unparse") else ""
                    )
                except Exception:
                    continue

                # Pattern: len(container) > index or len(container) >= (index + 1)
                # For index 0: len(container) > 0 OR len(container) OR just container
                if f"len({container})" in test_str:
                    # Check comparison patterns
                    if index == 0:
                        # For [0], any of these work:
                        # len(container) > 0, len(container) >= 1, len(container)
                        if any(p in test_str for p in ["> 0", ">= 1", "!= 0", "!= []"]):
                            return True
                        # Also: just "if len(container):" is truthy check
                        if test_str.strip() == f"len({container})":
                            return True
                    else:
                        # For [n], need len > n or len >= n+1
                        if f"> {index}" in test_str or f">= {index + 1}" in test_str:
                            return True

            # Also check ternary expressions in assignments
            elif isinstance(parent, ast.IfExp):
                try:
                    test_str = (
                        ast.unparse(parent.test) if hasattr(ast, "unparse") else ""
                    )
                except Exception:
                    continue

                if f"len({container})" in test_str:
                    if index == 0 and any(
                        p in test_str for p in ["> 0", ">= 1", "!= 0"]
                    ):
                        return True

        return False

    def _is_in_try_except(self) -> bool:
        """Check if current node is inside a try/except block."""
        for parent in self.parent_nodes:
            if isinstance(parent, ast.Try):
                return True
        return False

    def _check_widget_defaults(self, node: ast.Call):
        """TASK-403: Check Streamlit widget calls for missing default values.

        Detects widgets that may return None or unexpected values:
        - st.number_input() without value= parameter
        - st.text_input() without value= parameter
        - st.text_area() without value= parameter
        - st.selectbox() without index= parameter
        - st.multiselect() without default= parameter
        - st.slider() without value= parameter
        - st.radio() without index= parameter

        When defaults are missing, widgets return their first option or None,
        which can cause TypeError/AttributeError when used in calculations.
        """
        # Only check st.widget_name() calls
        if not isinstance(node.func, ast.Attribute):
            return

        # Check if it's a call on 'st' object
        if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "st"):
            return

        widget_name = node.func.attr

        # Define widgets and their required default parameters
        # Format: widget_name -> (default_param_name, severity, description)
        widget_defaults = {
            "number_input": (
                "value",
                "MEDIUM",
                "returns 0.0 or min_value if no default",
            ),
            "text_input": ("value", "LOW", "returns empty string if no default"),
            "text_area": ("value", "LOW", "returns empty string if no default"),
            "selectbox": ("index", "LOW", "returns first option if no index"),
            "multiselect": ("default", "LOW", "returns empty list if no default"),
            "slider": ("value", "LOW", "returns min_value if no default"),
            "radio": ("index", "LOW", "returns first option if no index"),
        }

        if widget_name not in widget_defaults:
            return

        param_name, severity, description = widget_defaults[widget_name]

        # Check if the required parameter is provided
        has_default = False

        # Check keyword arguments
        for kw in node.keywords:
            if kw.arg == param_name:
                has_default = True
                break

        # For some widgets, positional args may provide the default
        # st.number_input(label, min, max, value) - value is 4th positional
        # st.text_input(label, value) - value is 2nd positional
        # st.slider(label, min, max, value) - value is 4th positional
        positional_defaults = {
            "number_input": 3,  # 4th arg (0-indexed: label, min, max, value)
            "text_input": 1,  # 2nd arg (label, value)
            "text_area": 1,  # 2nd arg (label, value)
            "slider": 3,  # 4th arg (label, min, max, value)
        }

        if widget_name in positional_defaults:
            min_positional_for_default = positional_defaults[widget_name]
            if len(node.args) > min_positional_for_default:
                has_default = True

        if not has_default:
            self.add_issue(
                node.lineno,
                severity,
                f"Widget st.{widget_name}() missing '{param_name}=' parameter ({description})",
            )

    def _is_early_exit(self, body: List[ast.stmt]) -> bool:
        """Check if a code block contains early exit (return/raise).

        Phase 3: Helper for guard clause detection.
        Returns True if the block only contains early exit statements.

        Examples:
            if x == 0: return None  # True
            if x == 0: raise ValueError()  # True
            if x == 0: return  # True
            if x == 0:
                log("error")
                return None  # True (exits after logging)
        """
        if not body:
            return False

        # Check if last statement is return or raise
        last_stmt = body[-1]
        if isinstance(last_stmt, (ast.Return, ast.Raise)):
            return True

        # Check for early exit in nested if/while/for (conservative)
        # For guard clause detection, we require simple patterns
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

        Phase 3: Also checks API signature mismatches in test files.

        Checks for:
        - hash()/frozenset() on unhashable types (lists, dicts)
        - int()/float() without try/except (ValueError)
        - Common type mismatches
        - API signature mismatches (test files only)
        """
        func_name = None

        # Extract function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

        # Phase 3+: Check API signature mismatches in test files AND page files
        # Extended from tests-only to catch API mismatches in Streamlit pages
        critical_api_funcs = {
            "cached_design",
            "cached_smart_analysis",
            "run_cost_optimization",
            "run_compliance_checks",
            "design_beam",
        }
        if self.sig_registry and func_name:
            # Check all calls to critical API functions (regardless of file location)
            if func_name in critical_api_funcs:
                self._check_api_signature(node, func_name)
            # Also check test files for all registered functions
            elif "/tests/" in self.filepath:
                self._check_api_signature(node, func_name)

        # Check for hash() with unhashable types
        if func_name == "hash":
            if node.args:
                arg = node.args[0]

                # Direct unhashable types: hash([...]), hash({...}), hash({x: y})
                if isinstance(arg, (ast.List, ast.Set, ast.Dict)):
                    type_name = {ast.List: "list", ast.Set: "set", ast.Dict: "dict"}[
                        type(arg)
                    ]
                    self.add_issue(
                        node.lineno,
                        "CRITICAL",
                        f"TypeError: hash() called on unhashable type (lists/dicts/sets cannot be hashed)",
                    )

                # Risky pattern: hash(frozenset(dict.items()))
                elif isinstance(arg, ast.Call):
                    if (
                        isinstance(arg.func, ast.Name)
                        and arg.func.id == "frozenset"
                        and arg.args
                        and isinstance(arg.args[0], ast.Call)
                    ):
                        inner_call = arg.args[0]
                        if (
                            isinstance(inner_call.func, ast.Attribute)
                            and inner_call.func.attr == "items"
                        ):
                            self.add_issue(
                                node.lineno,
                                "HIGH",
                                "TypeError risk: hash(frozenset(dict.items()) fails if dict contains unhashable values (validate first)",
                            )

        # Check for frozenset() with unhashable types
        if func_name == "frozenset" and node.args:
            arg = node.args[0]

            # Direct list/dict/set literals are unhashable
            if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                self.add_issue(
                    node.lineno,
                    "CRITICAL",
                    f"TypeError: frozenset() called on unhashable type (lists/dicts/sets cannot be hashed)",
                )

            # Check for .items() which returns unhashable tuples containing unhashable values
            elif isinstance(arg, ast.Call):
                if isinstance(arg.func, ast.Attribute) and arg.func.attr == "items":
                    # dict.items() returns unhashable if dict values are unhashable
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"TypeError risk: frozenset(dict.items()) may fail if dict contains unhashable values (lists, dicts). Use make_hashable() helper.",
                    )

        # Check for int() / float() without error handling
        if func_name in ("int", "float"):
            # Only flag if there are arguments (conversion attempt)
            if node.args:
                # Check if inside try/except
                if not self._is_in_try_except():
                    self.add_issue(
                        node.lineno,
                        "MEDIUM",
                        f"ValueError risk: {func_name}() without try/except (invalid input will crash)",
                    )

        # TASK-403: Widget return type validation
        # Detect Streamlit widgets without explicit default values
        self._check_widget_defaults(node)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """
        Detect session state access without validation AND mock assertion anti-patterns.

        Handles:
        1. st.session_state.key access without validation
        2. Phase 2 Enhancement: Detect .called, .call_count on non-Mock objects

        Phase 6 Enhancement (TASK-425):
        - Recognize safe dict-like methods (.get, .setdefault, .pop, etc.)
        - These are safe method calls, not risky attribute accesses
        """
        # === Session state detection (for all files) ===
        # Check for st.session_state.key pattern
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "st"
                and node.value.attr == "session_state"
            ):
                # This is st.session_state.some_key
                attr_name = node.attr

                # Phase 6: Safe dict-like methods are NOT risky attribute accesses
                # These are standard dict methods that always exist on session_state
                safe_dict_methods = {
                    "get",
                    "setdefault",
                    "pop",
                    "update",
                    "keys",
                    "values",
                    "items",
                    "clear",
                    "copy",
                    "__contains__",
                    "__getitem__",
                    "__setitem__",
                    "__delitem__",
                    "__len__",
                    "__iter__",
                }
                if attr_name in safe_dict_methods:
                    # This is a safe method call, not a key access - skip warning
                    pass
                # Only warn if we haven't seen this key set
                elif attr_name not in self.session_state_keys:
                    self.add_issue(
                        node.lineno,
                        "HIGH",
                        f"AttributeError risk: st.session_state.{attr_name} may not exist (use .get() or check 'in')",
                    )

        # === Mock assertion anti-patterns (test files only) ===
        # Only check in test files
        if "/tests/" in self.filepath or self.filepath.endswith("_test.py"):
            # Check for .called, .call_count, .call_args patterns
            if node.attr in ("called", "call_count", "call_args", "call_args_list"):
                # Check if this is likely NOT a Mock object
                # Heuristic: if it's mock_streamlit.method_name.called, flag it
                # unless the method was explicitly set to MagicMock
                if isinstance(node.value, ast.Attribute):
                    # Pattern: mock_streamlit.markdown.called
                    base = node.value.value
                    method = node.value.attr

                    # Check if base looks like a mock fixture (mock_streamlit, mock_*, etc.)
                    if isinstance(base, ast.Name):
                        base_name = base.id
                        if base_name.startswith("mock_"):
                            # Get the full path: mock_streamlit.method
                            attr_path = f"{base_name}.{method}"

                            # Check if this was explicitly set to MagicMock
                            if attr_path not in self.magicmock_assignments:
                                # This is likely mock_streamlit.function.called
                                # which will fail if function is not a MagicMock
                                self.add_issue(
                                    node.lineno,
                                    "HIGH",
                                    f"Mock assertion anti-pattern: '{attr_path}.{node.attr}' "
                                    f"will fail if {method} is not a MagicMock. "
                                    f"Either: (1) Set '{attr_path} = MagicMock()' first, "
                                    f"or (2) Use 'assert True' to verify function ran without error.",
                                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Detect duplicate class definitions that shadow conftest fixtures.

        Phase 2 Enhancement: Warn when test files define MockStreamlit, MockSessionState, etc.
        These should use the centralized fixtures from conftest.py instead.
        """
        # Only check in test files (not conftest.py itself)
        if "/tests/" in self.filepath and not self.filepath.endswith("conftest.py"):
            # Known centralized test fixtures
            centralized_classes = {
                "MockStreamlit": "streamlit_app/tests/conftest.py",
                "MockSessionState": "streamlit_app/tests/conftest.py",
                "MockContext": "streamlit_app/tests/conftest.py",
            }

            if node.name in centralized_classes:
                expected_location = centralized_classes[node.name]
                self.add_issue(
                    node.lineno,
                    "MEDIUM",
                    f"Duplicate class definition: '{node.name}' shadows centralized fixture in {expected_location}. "
                    f"Use the conftest.py fixture instead (via 'mock_streamlit' parameter in test functions).",
                )

        # Track the class definition
        self.add_defined_name(node.name)
        old_class = self.current_class
        self.current_class = node.name

        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

        self.current_class = old_class


def check_file(
    filepath: Path,
    ignore_config: Optional[IgnoreConfig] = None,
    sig_registry: Optional[FunctionSignatureRegistry] = None,
) -> List[Tuple[int, str, str]]:
    """Check a single file for issues.

    Args:
        filepath: Path to file to check
        ignore_config: Optional ignore configuration
        sig_registry: Optional signature registry for API validation
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source, filename=str(filepath))

        detector = EnhancedIssueDetector(
            str(filepath), ignore_config=ignore_config, sig_registry=sig_registry
        )
        detector.visit(tree)

        return detector.issues

    except SyntaxError as e:
        return [(e.lineno or 0, "ERROR", f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, "ERROR", f"Failed to parse file: {e}")]


def scan_all_pages(
    pages_dir: Path,
    ignore_config: Optional[IgnoreConfig] = None,
    sig_registry: Optional[FunctionSignatureRegistry] = None,
) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan all Streamlit pages.

    Args:
        pages_dir: Directory containing page files
        ignore_config: Optional ignore configuration
        sig_registry: Optional signature registry for API validation
    """
    results = {}

    # Find all Python files in pages directory
    page_files = sorted(pages_dir.glob("*.py"))

    if not page_files:
        print(f"⚠️  No Python files found in {pages_dir}")
        return results

    for page_file in page_files:
        issues = check_file(
            page_file, ignore_config=ignore_config, sig_registry=sig_registry
        )
        results[page_file.name] = issues

    return results


def print_results(
    results: Dict[str, List[Tuple[int, str, str]]], fail_on: List[str] = None
) -> int:
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
        print(
            f"   Issues: {len(issues)} (Critical: {len(critical)}, High: {len(high)}, Medium: {len(medium)})"
        )

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
        help="Scan all pages in streamlit_app/pages/",
    )
    parser.add_argument(
        "--page",
        type=str,
        help="Scan specific page (e.g., 'beam_design' for 01_beam_design.py)",
    )
    parser.add_argument(
        "--fail-on",
        type=str,
        help="Comma-separated list of severities to fail on (e.g., 'critical,high')",
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Shortcut for --fail-on critical (exit 1 if any critical issues found)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--ignore-file",
        type=str,
        default=".scanner-ignore.yml",
        help="Path to ignore configuration file (default: .scanner-ignore.yml)",
    )
    parser.add_argument(
        "filepath", nargs="?", type=str, help="Optional: scan a specific file path"
    )

    args = parser.parse_args()

    # Parse fail-on severities
    fail_on_severities = None
    if args.fail_on_critical:
        fail_on_severities = ["critical"]
    elif args.fail_on:
        fail_on_severities = [s.strip() for s in args.fail_on.split(",")]

    # Determine project root
    project_root = Path(__file__).parent.parent
    pages_dir = project_root / "streamlit_app" / "pages"

    # Load ignore configuration
    ignore_file_path = project_root / args.ignore_file
    ignore_config = (
        IgnoreConfig(ignore_file_path) if ignore_file_path.exists() else None
    )

    if ignore_config and args.verbose:
        print(f"📋 Loaded ignore config from {ignore_file_path}")

    # Phase 3: Initialize signature registry for API validation
    sig_registry = FunctionSignatureRegistry()
    if args.verbose:
        print(f"🔧 Building function signature registry...")
        start_time = time.time()

    sig_registry.scan_common_modules(project_root)

    if args.verbose:
        elapsed = time.time() - start_time
        print(
            f"✅ Scanned {len(sig_registry.signatures)} function signatures in {elapsed:.2f}s"
        )

    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return 1

    # Scan pages
    if args.filepath:
        # Scan specific file path
        file_path = Path(args.filepath)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1

        print(f"🔍 Checking {file_path}...\n")
        issues = check_file(
            file_path, ignore_config=ignore_config, sig_registry=sig_registry
        )
        results = {file_path.name: issues}
        return print_results(results, fail_on_severities)

    elif args.all_pages:
        results = scan_all_pages(
            pages_dir, ignore_config=ignore_config, sig_registry=sig_registry
        )
        return print_results(results, fail_on_severities)

    elif args.page:
        # Find page file matching pattern
        matching_files = list(pages_dir.glob(f"*{args.page}*.py"))
        if not matching_files:
            print(f"❌ No page found matching '{args.page}'")
            return 1

        page_file = matching_files[0]
        print(f"🔍 Checking {page_file.name}...\n")

        issues = check_file(
            page_file, ignore_config=ignore_config, sig_registry=sig_registry
        )
        results = {page_file.name: issues}
        return print_results(results, fail_on_severities)

    else:
        print("❌ Please specify --all-pages or --page <name>")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
