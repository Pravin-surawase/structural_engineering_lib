# Task Board

> **How to use:** Start each session here. Pick from "Up Next", move to "Active", then "Done".

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.10.4 | Published on PyPI |
| **Next** | v0.20.0 | Blocked by S-007 |

---

## 🔴 Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **S-007** | External engineer CLI test | CLIENT | ⏳ Waiting (requires human) |

**Context:** This is the last blocker before v0.20.0 release.

**S-007 Test Instructions (design required, full CLI optional):**
```bash
# Fresh environment (simulate external user)
mkdir ~/test_structural && cd ~/test_structural
python3 -m venv .venv && source .venv/bin/activate
pip install structural-lib-is456

# Test CLI
python -m structural_lib --help

# Use correct CSV schema (all required fields)
cat > beams.csv << 'EOF'
BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,Story1,300,500,4000,40,25,500,150,100,942.5,0,8,150,OK
EOF

python -m structural_lib design beams.csv -o results.json
cat results.json

# Optional: full CLI smoke test (requires DXF extras)
pip install "structural-lib-is456[dxf]"
python -m structural_lib bbs results.json -o schedule.csv
python -m structural_lib dxf results.json -o drawings.dxf
python -m structural_lib job job.json -o job_out
```

---

## � INBOX (Triage Required)

> New issues go here with severity/impact/reproducible. Review at phase gates (W13, W26, W39, W52).
> Only P0 items can interrupt the roadmap. See `docs/planning/production-roadmap.md` for rules.

| ID | Issue | Severity | Impact | Reproducible | Link |
|----|-------|----------|--------|--------------|------|
| *empty* | *No new issues* | — | — | — | — |

**Severity guide:**
- **P0:** Blocker (wrong result, unsafe output, install broken)
- **P1:** Important (usability issue, missing validation, doc gap)
- **P2:** Nice-to-have (polish, optimization, edge case)

---

## �📋 Up Next

### Roadmap (Next 5 Weeks, WIP=1)

| Week | ID | Task | Agent | Status | Notes |
|------|----|------|-------|--------|-------|
| W01 | — | Scope lock + WIP rule | — | ✅ Done | Completed in docs discipline |
| W02 | S-007 | External engineer CLI test | CLIENT | ⏳ Waiting | Resume when tester available; proceed to W03 if blocked |
| W03 | RM-W03 | Error schema draft (code/field/hint/severity) | DOCS/DEV | ✅ Done | Published in docs/reference/error-schema.md |
| W04 | RM-W04 | Implement error schema (core + tests) | DEV | ⏳ Not started | Apply to 3 core functions |
| W05 | RM-W05 | Input validation pass (geometry/materials) | DEV | ⏳ Not started | Ensure is_safe=False with errors |
| W06 | RM-W06 | Units boundary spec | DEV/DOCS | ⏳ Not started | Update known-pitfalls.md |

### Post-v0.20.0 Polish

| ID | Task | Agent | Est. | Notes |
|----|------|-------|------|-------|
| S-053 | Security audit (dependency scan) | DEVOPS | 30 min | Nice to have |
| POLISH-001 | README badges (coverage, version) | DOCS | 15 min | Nice to have |

### New IS 456 Feature

| ID | Task | Agent | Est. |
|----|------|-------|------|
| TASK-088 | Slenderness Check (L > 60b warning) | DEV | 1 hr |

### v0.20.0 Release (after S-007 passes)

| Step | ID | Task | Agent | Est. |
|------|-----|------|-------|------|
| 1 | S-007 | External CLI test | CLIENT (owner) | 15 min |
| 2 | REL-001 | Update CHANGELOG | PM | 15 min |
| 3 | REL-002 | Bump version to 0.20.0 | DEVOPS | 10 min |
| 4 | REL-003 | Tag and release | DEVOPS | 15 min |

### v1.0 Gates

| Gate | Status | Notes |
|------|--------|-------|
| External CLI test | ⏳ | = S-007 (owner will do) |
| All tests pass | ✅ | 1810 pass, 91 skip |
| VBA parity verified | ✅ | Spot-checked |
| 5 beam validations | ✅ | Documented |

---

## 📦 Backlog (Post-v1.0)

| ID | Task | Agent | Severity | Impact | Description |
|----|------|-------|----------|--------|-------------|
| TASK-081 | Level C Serviceability | DEV | P2 | design | Shrinkage + creep (Annex C) |
| TASK-082 | VBA Parity Automation | DEVOPS | P2 | parity | Python vs VBA harness (= S-050) |
| TASK-085 | Torsion Design | DEV | P2 | design | Cl. 41 + closed stirrups |
| TASK-086 | Side-Face Reinforcement | DEV | P2 | design | D > 750mm check (Cl. 26.5.1.3) |
| TASK-087 | Anchorage Check | DEV | P2 | design | Ld at supports (Cl. 26.2) |
| TASK-089 | Flanged Width Helper | INTEGRATION | P2 | design | bf from slab geometry |
| TASK-090 | Publish JSON Schemas | INTEGRATION | P1 | schema | Add `schemas/job.schema.json` + `schemas/result.schema.json` |
| TASK-091 | CLI console script alias | DEVOPS | P2 | CLI | Add `structural-lib` console script in pyproject |
| TASK-092 | Structured error payloads | DEV | P1 | schema | Machine-readable error shape (code/field/hint) |
| S-051 | Performance benchmarks | DEV | P2 | stability | Track regression |
| S-052 | Fuzz testing | TESTER | P2 | stability | Random input testing |

---

## ✅ Recently Completed

### v0.20.0 Stabilization (PRs #89-98)

- **S-015:** Fixed 4 broken doc links + created `scripts/check_links.py`
- **S-014:** Fixed expected output in beginners-guide (942→882)
- **S-009:** Fixed D1 expected Ld value (752→777)
- **S-006:** Improved job_runner error messages
- **S-020–S-032:** Verified all High Priority items (edge cases, performance)

### Earlier Sprints

| Sprint | Key Deliverables |
|--------|-----------------|
| Level B Serviceability (PR #62) | 7 functions, `DeflectionLevelBResult`, 16 tests |
| Release Automation (PR #59) | `release.py`, `check_doc_versions.py`, pre-commit hooks |
| Multi-Agent Review | CODEOWNERS, API docs, `__all__` exports |
| DXF Polish | Title blocks, PDF/PNG workflow |

> Full history: `docs/_archive/`

---

## 🛠️ Agent Roles

| Role | Use For |
|------|---------|
| **DEV** | Implementation, refactoring |
| **TESTER** | Test design, edge cases |
| **DEVOPS** | Automation, releases |
| **PM** | Scope, changelog |
| **DOCS** | API docs, guides |
| **CLIENT** | Requirements, validation |
| **SUPPORT** | Troubleshooting |

> Full list: `agents/README.md`

---

## 📊 Status

| Metric | Value |
|--------|-------|
| **Version** | v0.10.4 |
| **Tests** | 1810 passed, 91 skipped |
| **Coverage** | 92% branch |
| **Next Release** | v0.20.0 (awaiting S-007) |
| **Updated** | 2025-12-28 |

---

*Checklist: `docs/planning/v0.20-stabilization-checklist.md`*
