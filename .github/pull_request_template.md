## Summary

<!-- Brief description of what this PR does and why -->

## Changes

<!-- List the key changes made -->

## Task Reference

<!-- Link to TASKS.md item or issue, e.g. "Resolves TASK-XXX" -->

## Testing

- [ ] Python: `.venv/bin/pytest Python/tests/ -v`
- [ ] React: `cd react_app && npm run build`
- [ ] Docker: `docker compose up --build` (if FastAPI changed)
- [ ] VBA: ran relevant tests in `VBA/Tests/` (manual, if VBA changed)
- [ ] Streamlit: `.venv/bin/python scripts/check_streamlit.py --all-pages` (if Streamlit changed)

## Checklist

- [ ] No behavior change without tests
- [ ] Architecture boundaries respected (Core ← IS 456 ← Services ← UI)
- [ ] Units explicit in all parameters (mm, N/mm², kN, kNm)
- [ ] No duplicate hooks/components/routes (searched before coding)
- [ ] Docs updated if public API changed
- [ ] Python + VBA parity maintained (if formula changed)
