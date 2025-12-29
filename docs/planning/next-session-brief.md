# Next Session Briefing

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.11.0 | Published on PyPI |
| **Next** | v0.20.0 | Blocked by S-007 |

**Date:** 2025-12-29 | **PRs:** through #156

---

## 🎯 Immediate Priority

**Only 1 item blocks v0.20.0 release:**

| Task | Description | Owner |
|------|-------------|-------|
| S-007 | External engineer tries CLI cold | Human (not automatable) |

**After S-007 passes:**
```bash
python scripts/release.py 0.20.0
```

**Stabilization status:** 26/31 complete — see `docs/planning/v0.20-stabilization-checklist.md`

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
- CLI: `python -m structural_lib design|bbs|dxf|job|critical|report`
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

**Performance facts (verified 2025-12-29):**
- Tests: 1917 passed, 91 skipped, 92% branch coverage
- Speed: 0.009ms per beam, 94,000 beams/second
- All edge cases handled gracefully (zero/negative → `is_safe=False`)

---

## ✅ Last Session Summary (2025-12-29)

**Focus:** Visual v0.11 deliverables + report tooling

| PR | Description |
|----|-------------|
| #151 | V04 SVG + V05 input sanity heatmap |
| #153 | V06 stability scorecard |
| #154 | V07 units sentinel |
| #155 | V08 report batch packaging + CLI support |
| #156 | V09 golden report fixtures/tests |

**Outcome:** Visual v0.11 (V03–V09) complete and integrated. ✅

---

## 🎯 What's Next (Priority Order)

### Blocking v0.20.0
1. **S-007** — External engineer CLI test (requires human)

### After v0.20.0 (Nice to Have)
2. **S-050** — VBA parity automation
3. **S-051** — Performance benchmarks (track regression)
4. **S-052** — Fuzz testing
5. **S-053** — Security audit

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
