# Copilot Instructions — structural_engineering_lib

## What this project is
IS 456 RC beam design library with **Python + VBA parity**.

## Non-negotiables
- Deterministic calculations (no hidden defaults).
- Units must be explicit and consistent.
- Keep Python/VBA behavior aligned.
- Prefer minimal, surgical changes.

## Always load this context first
- docs/AI_CONTEXT_PACK.md
- docs/PROJECT_OVERVIEW.md
- docs/API_REFERENCE.md
- docs/KNOWN_PITFALLS.md
- docs/TASKS.md

## Coding rules
- Don’t mix UI/I-O code into core calculation modules.
- Add/extend tests with every behavior change (Python at minimum).
- If you move files, keep redirect stubs to avoid breaking links.

## Definition of done
- Tests pass (at least Python).
- Docs updated where contracts/examples changed.
- No unrelated refactors.
