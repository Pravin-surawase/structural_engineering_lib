# Next Session Briefing

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.12.0 | Published on PyPI |
| **Next** | v0.12.1 | Planned (test hardening + verification gates) |

**Date:** 2025-12-30 | **PRs:** through #196

---

## 🎯 Immediate Priority

**v0.12 follow-up (stability + verification):**

| Task | Description | Owner |
|------|-------------|-------|
| S-007 | External engineer CLI cold-start test | CLIENT |
| TASK-126 | Reduce property-invariant skips by tightening generators | TESTER |
| TASK-127 | Add contract tests for units conversion boundaries | TESTER |
| TASK-128 | Add BBS/DXF mark-diff regression fixtures | TESTER |

**Plan doc:** `docs/planning/bbs-dxf-improvement-plan.md`

---

## 📚 Required Reading

> ⚠️ **Do NOT skip this.** These docs contain critical rules that prevent wasted time.

| Order | Document | What You'll Learn |
|-------|----------|-------------------|
| 1 | `.github/copilot-instructions.md` | Layer architecture, units, Mac VBA safety, git workflow |
| 2 | `docs/AI_CONTEXT_PACK.md` | Complete project context for AI agents |
| 3 | `docs/TASKS.md` | Current backlog — what's done, what's pending |
| 4 | `docs/planning/v0.20-stabilization-checklist.md` | Release readiness status |

**Quick project summary:**
- IS 456 RC beam design library (Indian Standard)
- Python + VBA with matching outputs (parity requirement)
- CLI: `python -m structural_lib design|bbs|dxf|job|validate|detail|critical|report|mark-diff`
- PyPI: `pip install structural-lib-is456`

---

## ⚠️ Critical Learnings (Avoid These Mistakes)

| Mistake | Why It Wastes Time | Do This Instead |
|---------|-------------------|-----------------|
| Skipping tests before push | CI fails, need to fix + re-push | `cd Python && .venv/bin/python -m pytest -q` |
| Merging before CI passes | PR gets blocked or reverted | `gh pr checks <num> --watch` first |
| Using `python` directly | May use wrong interpreter | Use `.venv/bin/python` or configure environment |
| Hardcoding expected values in docs | Values drift from actual code | Run code, copy actual output to docs |
| Duplicating content across docs | Creates stale contradictions | Link to canonical source instead |
| Many micro-PRs for tiny changes | Review fatigue, CI waste | Batch related changes into one PR |
| Editing without reading file first | Merge conflicts, overwrites | Always read current state before editing |

**Performance facts (latest CI 2025-12-30):**
- Tests: 1956 passed, 91 skipped, 92% branch coverage
- Speed: 0.009ms per beam, 94,000 beams/second
- All edge cases handled gracefully (zero/negative → `is_safe=False`)

---

## ✅ Last Session Summary (2025-12-30)

**Focus:** v0.12 library-first APIs + release prep

| PR | Description |
|----|-------------|
| #193 | Detail CLI + compute_detailing/compute_bbs/export_bbs wrappers |
| #194 | README + Colab workflow refresh |
| #195 | DXF/report/critical wrappers + DXF import guard |
| #196 | API wrapper tests + stability labels |

**Outcome:** v0.12 API surface finalized; docs refreshed for new CLI usage.

---

## 🎯 What's Next (Priority Order)

### Long-term milestone (v0.20.0)
1. **S-007** — External engineer CLI test (requires human)
2. See `docs/planning/v0.20-stabilization-checklist.md`

### Backlog (v1.0+)
See `docs/TASKS.md` for full backlog including:
- Level C Serviceability (shrinkage + creep)
- Torsion Design (Cl. 41)
- Side-Face Reinforcement (Cl. 26.5.1.3)

---

## 🔍 Quick Verification Commands

```bash
# Check current state
git rev-parse --short HEAD          # Latest commit
python -c "from structural_lib import api; print(api.get_library_version())"

# Run tests
cd Python && ../.venv/bin/python -m pytest -q

# Check for broken links
.venv/bin/python scripts/check_links.py

# Full local CI check
./scripts/ci_local.sh
```

---

## 📜 History

- **Full session log:** `docs/SESSION_LOG.md`
- **Archived docs:** `docs/_archive/`
- **GitHub Actions:** https://github.com/Pravin-surawase/structural_engineering_lib/actions

---

*This briefing should be ~100 lines. If it grows beyond 150, archive old sessions to SESSION_LOG.md.*
