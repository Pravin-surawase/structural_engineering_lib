## Summary

<!-- Brief description of what this PR does and why -->

## Changes

<!-- List the key changes made -->

## Task Reference

<!-- Link to TASKS.md item or issue, e.g. "Resolves TASK-XXX" -->

## Testing

- [ ] Targeted checks for the changed behavior
- [ ] Repository quick gate: `./run.sh check --quick`
- [ ] React validation: `./run.sh frontend check` (if the workbench changed)
- [ ] Full gate: `./run.sh check` (when required by scope/risk)

## Checklist

- [ ] No behavior change without tests
- [ ] Architecture boundaries respected (Core ← IS 456 ← Services ← UI)
- [ ] Units explicit in all parameters (mm, N/mm², kN, kNm)
- [ ] No duplicate hooks/components/routes (searched before coding)
- [ ] Docs updated if public API changed
- [ ] Supported-case, limitation, and professional-review claims remain accurate
