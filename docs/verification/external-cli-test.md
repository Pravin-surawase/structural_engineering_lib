# External CLI Test (S-007)

Purpose: capture a repeatable, human-run CLI test from a fresh user.

---

## Tester Info
- **Name/Role:**
- **OS + Version:**
- **Python Version:**
- **Shell:**
- **Install method:** `pip install` / `pipx` / other

## Checklist (Run in Order)

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
