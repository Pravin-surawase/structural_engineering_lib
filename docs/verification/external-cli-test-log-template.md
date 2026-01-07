# External CLI Test Log (S-007) — Template

> Purpose: capture a repeatable, human-run CLI test from a fresh user.
>
> Fill this out and paste into `docs/SESSION_log.md` (or attach it to the PR).

---

## Tester Info

- Name / Role:
- Date:
- OS + Version:
- Python Version (`python --version`):
- Shell / Terminal:
- Install method: `pip install` / `pipx` / other
- Package version (`python -c "from structural_lib import api; print(api.get_library_version())"`):

---

## Setup Notes

- Fresh environment? (yes/no)
- Network restrictions / proxy issues? (yes/no)
- Any optional extras installed? (e.g. `structural-lib-is456[dxf]`)

---

## Run Results

### 1) Install

- Result: PASS / FAIL
- Notes:

### 2) CLI help

- Result: PASS / FAIL
- Notes:

### 3) `job`

- Command run:
- Result: PASS / FAIL
- Notes:

### 4) `critical`

- Command run:
- Result: PASS / FAIL
- Notes:

### 5) `report` (HTML)

- Command run:
- Result: PASS / FAIL
- Notes:

### 6) Optional pipeline (`design` → `bbs` → `dxf`)

- Result: PASS / FAIL / SKIPPED
- Notes:

---

## Friction Points (Most Important)

List 3–10 items a new user would struggle with.

1.
2.
3.

---

## Verdict

- [ ] PASS — all required steps worked
- [ ] FAIL — blocked (explain below)

### Blocker Details

- What blocked you?
- Exact error text / traceback:
- What did you expect instead?

---

## Attachments

- Log file path (if any):
- Output folder (zip) (if any):
