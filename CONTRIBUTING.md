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

### For Repository Maintainer (Pravin)
- **Direct push** to main allowed for routine changes (docs, fixes, tests, minor updates)
- **Use PRs** for significant features, breaking changes, or when you want self-review
- CI runs on every push — watch for failures and fix immediately
- Rule of thumb: <20 lines and low-risk → direct push; >20 lines or risky → use PR

Helper script (optional):
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

## Reporting Issues

When filing a bug, include:
- What you expected vs what happened
- Input parameters (b, D, span, fck, fy, Mu/Vu)
- Whether you used Python or Excel/VBA
- Any files (CSV) you can share

## Code of Conduct

By participating, you agree to the rules in `CODE_OF_CONDUCT.md`.
