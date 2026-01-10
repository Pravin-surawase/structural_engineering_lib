# Contributing

Thanks for helping improve **structural_engineering_lib**.

## Quick Start

### Python
- Install (editable) with dev tools:
  - `cd Python`
  - `python3 -m pip install -e ".[dev]"`
- Run tests:
  - `python3 -m pytest -q`

### VBA
- VBA modules live in `VBA/Modules/`.
- Tests live in `VBA/Tests/` and are currently **manual-run**.

## Workflow

### For AI Agents (CRITICAL)
- ⚠️ **ALWAYS use `./scripts/safe_push.sh "message"` for commits** to avoid git race conditions
- Read the full guide: [docs/contributing/git-workflow-for-ai-agents.md](docs/_archive/contributing/git-workflow-for-ai-agents.md)
- Pre-commit hooks modify files after staging — safe_push.sh handles this automatically
- Never use `git push` directly after `git commit`

### For Repository Maintainer (Pravin)
- **Direct push** to main allowed for routine changes (docs, fixes, tests, minor updates)
- **Use PRs** for significant features, breaking changes, or when you want self-review
- CI runs on every push — watch for failures and fix immediately
- Rule of thumb: <20 lines and low-risk → direct push; >20 lines or risky → use PR

Helper script (optional):
- `./scripts/safe_push.sh "message"` (recommended for all commits — prevents race conditions)
- `./scripts/quick_push.sh "docs: update something"` (runs `./scripts/quick_check.sh`, then commits + pushes)
- `./scripts/quick_push.sh "docs: update docs" docs` (docs-only checks)
- `./scripts/quick_push.sh "test: update" --cov` (runs tests with coverage gate)

### For External Contributors (if any)
- Fork the repository
- Create a feature branch
- Submit PR to main
- Wait for CI to pass
- Maintainer will review and merge

## Guidelines

- Keep changes small and focused.
- Prefer pure functions and deterministic outputs (no UI or worksheet access in core logic).
- Preserve unit conventions (mm, kN, kN·m).
- Update or add tests when changing behavior.
- Update docs when you change public APIs.

## Error Handling Strategy

This library uses a **layered error handling strategy** to balance usability, debuggability, and proper separation of concerns.

### By Layer

#### 1. Core Calculation Modules (flexure, shear, serviceability, etc.)

**Strategy:** Raise `ValueError` for invalid inputs.

**Rationale:**
- Entry-point functions (e.g., `design_beam_flexure_is456`) already validate inputs using validation utilities
- If a low-level helper receives invalid input, it indicates a programming error (contract violation)
- Explicit exceptions make bugs immediately visible rather than silently propagating incorrect results

**Example:**
```python
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    """Calculate limiting moment of resistance per IS 456 Cl. 38.1."""
    if b <= 0:
        raise ValueError("b (width) must be positive for Mu,lim calculation")
    if d <= 0:
        raise ValueError("d (effective depth) must be positive for Mu,lim calculation")
    # ... calculation
```

#### 2. Validation Utilities (validation.py)

**Strategy:** Return `List[DesignError]` for reusable validators.

**Rationale:**
- Validators aggregate multiple errors for better user experience
- Structured errors contain field names, severities, and clause references
- Entry-point functions collect validation errors before attempting calculations

**Example:**
```python
def validate_dimensions(b: float, D: float, d: float = None) -> List[DesignError]:
    """Validate beam dimensions per IS 456 Cl. 23.1."""
    errors = []
    if b <= 0:
        errors.append(DesignError(
            error_message="Beam width must be positive",
            severity=Severity.ERROR,
            field_name="b"
        ))
    # ... more checks
    return errors
```

#### 3. Orchestration/API Layer (api.py, beam_pipeline.py)

**Strategy:** Catch exceptions from lower layers, convert to structured errors, aggregate results.

**Rationale:**
- This layer knows the full context (all inputs, design intent)
- Catches `ValueError` from calculation helpers and converts to `DesignError`
- Returns structured results with `.success`, `.errors`, `.data` fields
- Never lets exceptions escape to I/O layer

**Example:**
```python
def design_beam_flexure_is456(...) -> DesignResult:
    """Design beam for flexure per IS 456."""
    errors = validate_beam_inputs(...)  # Collect validation errors
    if errors:
        return DesignResult(success=False, errors=errors)

    try:
        mu_lim = calculate_mu_lim(b, d, fck, fy)
        # ... design logic
        return DesignResult(success=True, data={...})
    except ValueError as e:
        # Convert calculation exception to structured error
        return DesignResult(
            success=False,
            errors=[DesignError(error_message=str(e), severity=Severity.ERROR)]
        )
```

#### 4. I/O Modules (dxf_export, excel_integration, report)

**Strategy:** Raise exceptions for I/O failures.

**Rationale:**
- I/O errors are environmental (file not found, permission denied, malformed data)
- Should be caught and handled by the calling context (CLI, UI, script)
- Use descriptive exception messages with context

**Example:**
```python
def export_beam_to_dxf(beam_data: Dict, filepath: str) -> None:
    """Export beam design to DXF file."""
    if not os.path.exists(os.path.dirname(filepath)):
        raise FileNotFoundError(f"Directory does not exist: {os.path.dirname(filepath)}")
    # ... export logic
```

#### 5. CLI/Entry Points (job_cli.py, __main__.py)

**Strategy:** Catch all exceptions, log them, print user-friendly messages.

**Rationale:**
- This is the outermost layer — nothing above to catch exceptions
- Convert technical exceptions to human-readable error messages
- Log full traceback for debugging but show brief message to user

**Example:**
```python
def main():
    try:
        result = design_beam_job(...)
        if not result.success:
            for error in result.errors:
                print(f"ERROR: {error.error_message}")
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(2)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}")
        sys.exit(3)
```

### Summary Table

| Layer | Error Handling | Escapes Layer? | Rationale |
|-------|---------------|----------------|-----------|
| Core Calculations | Raise `ValueError` | Yes | Contract violation → fail fast |
| Validation Utilities | Return `List[DesignError]` | No | Aggregate user input errors |
| Orchestration/API | Catch exceptions, return `DesignResult` | No | Convert to structured format |
| I/O Modules | Raise specific exceptions | Yes | Environmental failures |
| CLI/Entry Points | Catch all, log, exit with code | No | User-facing error messages |

### Rules for Contributors

1. **Never return sentinel values** (e.g., `0.0`, `-1`, `None`) to indicate errors in calculation functions
2. **Use validation utilities** before calling calculation helpers (fail early with good messages)
3. **Let exceptions bubble up** from core to orchestration layer (don't catch prematurely)
4. **Always include context** in error messages (which parameter, which clause, expected range)
5. **Test error paths** — every `ValueError` should have a corresponding test with `pytest.raises()`

### Audit Compliance

Run `scripts/audit_error_handling.py` to check compliance:
```bash
.venv/bin/python scripts/audit_error_handling.py
```

This script uses AST analysis to detect:
- Return statements with error sentinel values (0.0, -1, None in error conditions)
- Missing validation before calculation helpers
- Exceptions caught without re-raising or converting to structured errors



## Reporting Issues

When filing a bug, include:
- What you expected vs what happened
- Input parameters (b, D, span, fck, fy, Mu/Vu)
- Whether you used Python or Excel/VBA
- Any files (CSV) you can share

## Code of Conduct

By participating, you agree to the rules in `CODE_OF_CONDUCT.md`.
