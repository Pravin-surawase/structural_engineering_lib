# IS 456 RC Beam Design Library — Project Status

*Quick summary for agents and contributors*

**Last updated:** 2025-07-11
**Current release:** v0.10.4 (PyPI)
**Next milestone:** v0.20.0 (blocked by S-007)

---

## What This Library Does

Professional-grade RC beam design library for IS 456:2000:
- **Strength design:** Flexure, shear, ductile detailing
- **Serviceability:** Deflection and crack width (Levels A & B)
- **Outputs:** DXF drawings, BBS schedules, compliance reports
- **Dual implementation:** Python + VBA with parity intent

## Current Stats

| Metric | Value |
|--------|-------|
| Python tests | 1810 passed, 91 skipped |
| Branch coverage | 92% |
| VBA parity | Manual (automation planned) |
| CLI commands | `design`, `bbs`, `dxf`, `job` |

## Success Criteria

- New user → first result in **< 5 min** (Python) or **< 10 min** (Excel)
- Every check surfaces **governing case + utilization + reason**
- Same input → same output (deterministic)
- Batch: 50–500 beams with clear error summaries

## Where to Go Next

| Need | Document |
|------|----------|
| Tasks & blockers | [TASKS.md](../TASKS.md) |
| Architecture | [project-overview.md](../architecture/project-overview.md) |
| API reference | [api.md](../reference/api.md) |
| Module details | [project-status-deep-dive.md](project-status-deep-dive.md) |
| Known issues | [known-pitfalls.md](../reference/known-pitfalls.md) |

## Quick Layer Reference

| Layer | Purpose | Python | VBA |
|-------|---------|--------|-----|
| **Core** | Pure math | `flexure.py`, `shear.py`, etc. | M03–M07 |
| **App** | Orchestration | `api.py`, `job_runner.py` | M11 |
| **I/O** | UI & files | `__main__.py`, `dxf_export.py` | M12–M14 |

## Known Gaps

- [ ] VBA automated testing (TASK-039/040)
- [ ] PDF report generation
- [ ] Serviceability Level C (shrinkage/creep)
- [ ] Multi-beam batch schema

---

*For detailed module maps, research directions, and release artifacts, see [project-status-deep-dive.md](project-status-deep-dive.md).*
