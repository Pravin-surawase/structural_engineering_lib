# External CLI Test (S-007)

Purpose: capture a repeatable, human-run CLI test from a fresh user.

Preferred: use the automated smoke script so the output is consistent and easy to share.

Automated option (recommended):

1) Install (clean venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install "structural-lib-is456[dxf]"
```

2) Download the script (pick one)

- From this repo: `scripts/external_cli_test.py`
- Or copy the file contents into `external_cli_test.py`

3) Run it
```bash
python external_cli_test.py
```

Outputs:
- A shareable log file: `external_cli_test_run/external_cli_test.log`
- A small outputs folder: `external_cli_test_run/outputs/`

Fill this template and attach it with the log:
- `docs/verification/external-cli-test-log-template.md`

---

## Tester Info
- **Name/Role:**
- **OS + Version:**
- **Python Version:**
- **Shell:**
- **Install method:** `pip install` / `pipx` / other

## Checklist (Run in Order)

If you used the automated script above, you can skip this manual checklist.

1) **Install (clean venv)**
```bash
python -m venv .venv
source .venv/bin/activate
pip install "structural-lib-is456[dxf]"
```

2) **Version check**
```bash
python -c "from structural_lib import api; print(api.get_library_version())"
```

3) **Run job**
```bash
python -m structural_lib job Python/examples/sample_job_is456.json -o ./job_out
```

4) **Critical set**
```bash
python -m structural_lib critical ./job_out --top 5 --format=csv
```

5) **Report HTML**
```bash
python -m structural_lib report ./job_out --format=html -o report.html
```

6) **Optional: design pipeline**
```bash
python -m structural_lib design Python/examples/sample_beam_design.csv -o results.json
python -m structural_lib bbs results.json -o schedule.csv
python -m structural_lib dxf results.json -o drawings.dxf
```

## What Happened (Notes)
- **Any errors?** (copy full traceback/output)
- **Anything unclear?**
- **Anything slow?** (approx timings)
- **Missing docs?** (which link would help)

## Verdict
- [ ] PASS — all steps worked
- [ ] FAIL — blocked (list why)
