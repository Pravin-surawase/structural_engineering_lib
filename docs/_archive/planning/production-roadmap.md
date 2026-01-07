# Production Readiness Roadmap (12-Month Weekly Plan)

Purpose: reach a professional-grade beam library with pandas-like reliability.

---

## Roadmap Baseline (v0.10.4)

**Current state:** v0.10.4 published on PyPI
**Next milestone:** v0.20.0 (Contract Lock checkpoint — includes S-007 by W06)
**Target:** v1.0.0 in 52 weeks

Note: For live version/test counts, see `docs/ai-context-pack.md`.

### Already Done (freeze these)
- Core design functions: flexure (singly/doubly/flanged), shear, ductile
- Detailing: Ld, lap length, spacing, bar callouts
- Serviceability: Level A (deflection + crack width), Level B
- CLI: `design`, `bbs`, `dxf`, `job` commands
- DXF export, BBS generation, cutting-stock optimizer
- Test suite: 1810 passed, 92% branch coverage
- Docs discipline: TASKS.md, ai-context-pack.md, copilot-instructions.md

### Core Gaps (must close for v1.0)
- S-007: External engineer CLI test
- Error schema with structured codes/hints
- 10-15 verified benchmark cases with clause references
- 10-15 Python↔VBA parity vectors passing
- Schema versioning for job/results/schedule
- Security scan in CI

### Near-Term Release Milestones (v0.13–v0.17)
Beam-only focus with added visualization and UX polish.

**v0.13 — Verification + Visual Trust**
- 5–10 verified benchmark cases with clause references.
- Report visuals: utilization bars, governing case highlight, quick pass/fail tiles.
- Short “explain this result” blocks in reports (beam-safe, deterministic).

**v0.14 — Detailing Completeness + Friendlier Errors**
- Side-face reinforcement check (Cl. 26.5.1.3).
- Anchorage space check (Cl. 26.2).
- Top error hints tightened with actionable suggestions.

**v0.15 — Serviceability Level C**
- Long-term deflection (creep + shrinkage) with explicit assumptions.
- Serviceability outputs show assumptions in report payloads.

**v0.16 — Torsion Phase 1 + Reporting Flags**
- Basic torsion checks (Cl. 41) with opt-in inputs.
- Report flags for torsion-governed cases.

**v0.17 — Parity Automation + UX Cleanup**
- VBA parity harness (10–15 vectors).
- UX polish pass (CLI summaries, report readability, stable layouts).

### NO Until v1.1 (explicit scope boundary)
| Deferred | Reason |
|----------|--------|
| PDF report generation | Nice-to-have, not core |
| Multi-beam schema redesign | Keep current batch outputs; do not redesign contracts until post-v1.0 |
| Serviceability Level C (creep/shrinkage) | Specialized |
| Full VBA automation (beyond 15 vectors) | Diminishing returns |
| Website / docs site | Post-v1.0 adoption effort |
| Performance regression CI guards | Basic benchmark is enough |
| 30+ verified examples | 10-15 is sufficient for v1.0 |

Note: Batch execution already exists (CSV/job runner). v1.0 will *stabilize* the current multi-beam output shape under schema v1; it will not introduce a new “multi-beam schema v2”.

---

Assumptions:
- 5 to 10 hours per week, solo owner.
- WIP limit = 1 (only one active task at a time).
- Every week ends with tests passing and docs updated.

Definition of "professional-grade":
- Stable public API with versioned schemas (JSON/CSV/DXF).
- Deterministic outputs (same inputs -> same outputs).
- Verified example pack with clause references.
- Security scan in CI and dependency policy.
- Python <-> VBA parity harness with tolerances.
- Cold-start onboarding: install -> first result in < 5 minutes.
- Traceability: every result ties to clause + governing case.
- Reproducibility: outputs are versioned and schema-stable across releases.

Non-negotiables:
- No new feature unless it advances the current week.
- Clear "done" criteria for every task.
- If a week is missed, roll it forward; do not add parallel tasks.
- S-007 is a human-dependent gate: if it is waiting on a tester, continue to the next roadmap week (WIP=1 still applies). When the tester is available, S-007 preempts the current week.

---

## INBOX + Interruption Rules

**Rule: Incoming work goes to INBOX, not today.**

New issues/features go to `docs/TASKS.md` (Backlog section) with:
- Severity: P0 (blocker) / P1 (important) / P2 (nice-to-have)
- Impact area: design / schema / CLI / DXF / docs / parity
- Reproducible: yes / no
- Link to failing case (if bug)

**Only 2 things can interrupt the roadmap:**
1. **P0 correctness:** Wrong design result, unsafe output, wrong clause reference
2. **P0 usability blocker:** Fresh install fails, CLI broken, outputs invalid JSON/CSV

Everything else waits for the next stabilization week or backlog review.

---

## Predictable Issue Buckets

These are expected issues for this domain — plan for them, don't be surprised:

| Bucket | Examples | When to address |
|--------|----------|----------------|
| Units + signs | ETABS kN vs N, moment sign conventions | W06 (Units boundary spec) |
| Edge geometry | b very small, D ≈ d, cover weirdness | W22 (Edge-case coverage) |
| T-beam flanges | NA location transitions, bf edge cases | W22 (Edge-case coverage) |
| Table boundaries | Table 19/20 interpolation at edges | W22 (Edge-case coverage) |
| Serviceability params | Global vs per-beam flags | W05 (Input validation) |
| DXF determinism | Font differences, entity ordering | W36 (DXF determinism) |
| CSV dirtiness | Blank rows, TOTAL rows, non-numeric | W05 (Input validation) |
| Path issues | Windows/Mac/Colab path handling | W43 (Colab workflow) |

---

## Risk Analysis

**Phase 2 (Trust & Verification) is the biggest time sink:**
- Each verified problem needs: source reference, input extraction, expected output, tolerance, test.
- Estimate: 2-4 hours per problem. At 20-30 problems = 60-120 hours = 6-12 weeks at solo pace.
- Mitigation: Start with 10-15 core cases, expand only if time allows.

**Phase 3 (Parity) is second-risk:**
- VBA automation is brittle and tooling-limited.
- Mitigation: Stage parity in batches (5 → 10 → 15 vectors), don't block on full automation.

**API Freeze means:**
- Freeze: core design functions (`design_singly_reinforced`, `design_shear`, etc.), result dataclass shapes, error schema.
- Keep flexible: CLI flags, output formats, convenience wrappers, report templates.

---

## Milestone Gates

**Phase A — Contract Lock (Weeks 1-13)**
- Goal: Stop breaking yourself later
- Gate: API list frozen, error schema v1, schema versioning, core tests ≥ 90% branch
- Stabilization: W13 is buffer week

**Phase B — Trust Pack (Weeks 14-26)**
- Goal: Engineers trust it
- Gate: 10-15 verified examples in CI with published outputs and clause references
- Stabilization: W26 is buffer week

**Phase C — Stability, Security, Parity (Weeks 27-39)**
- Goal: Enterprise-ish confidence
- Gate: 10-15 parity vectors passing (Python↔VBA), security scan clean
- Parity scope: 10-15 vectors for v1.0; full automation grows post-v1.0
- Stabilization: W39 is buffer week

**Phase D — Professional UX and v1.0 (Weeks 40-52)**
- Goal: Strangers succeed without you
- Gate: Cold-start < 5 min, CLI schema v1 enforced, v1.0.0 released
- Stabilization: W49 is buffer week

---

## Weekly Plan (W01 to W52)

### Weeks 1-13: Foundation and API Freeze
- W01: Scope lock and WIP rule
  - Deliverable: add WIP=1 rule to docs/TASKS.md and docs/ai-context-pack.md.
  - Done when: rule visible and agreed.
- W02: External CLI test (S-007)
  - Deliverable: cold-start test log in docs/SESSION_log.md (fresh install, run CLI, verify outputs).
  - Done when: results recorded + issues captured + at least 3 “stranger” pain points converted to backlog items.
  - If blocked: mark as Waiting and proceed to W03 (WIP=1 rule still applies; S-007 resumes when tester is available).
- W03: Error schema draft
  - Deliverable: error schema doc (code, field, hint, severity).
  - Done when: schema published in docs/reference/.
- W04: Implement error schema (core)
  - Deliverable: apply schema to 3 core functions + tests.
  - Done when: tests pass and errors are structured.
- W05: Input validation pass
  - Deliverable: validation coverage on geometry/material inputs.
  - Done when: invalid inputs return is_safe=False with clear errors.
- W06: Units boundary spec
  - Deliverable: unit conversion rules documented and enforced.
  - Done when: docs/reference/known-pitfalls.md updated + tests.
- W07: API freeze v1
  - Deliverable: stable signatures in docs/reference/api.md.
  - Done when: API list labeled "frozen".
- W08: Schema v1 draft (job + results + schedule) + clause tagging
  - Deliverable: schema files in docs/specs/ (job/results/schedule) including a stable place for clause references.
  - Done when: sample JSON validates and one example output contains clause tags.
- W09: Determinism audit
  - Deliverable: tests for deterministic outputs on core pipeline.
  - Done when: repeat runs match hashes.
- W10: Coverage gap closure
  - Deliverable: add tests to reach >= 90% branch on core modules.
  - Done when: coverage report confirms target.
- W11: Deprecation policy
  - Deliverable: policy doc for breaking changes and timelines.
  - Done when: policy referenced in docs/README.md.
- W12: API freeze checkpoint tag
  - Deliverable: internal tag or release note marking API freeze.
  - Done when: recorded in docs/releases.md.
- W13: Foundation release + stabilization buffer
  - Deliverable: v0.20.x checkpoint release + fix any Phase A regressions.
  - Done when: CHANGELOG updated, zero open Phase A issues.

### Weeks 14-26: Trust and Verification (Phase B)
- W14: Golden vector selection
  - Deliverable: list of 10-15 verified problems + sources (scope reduced from 20-30).
  - Done when: list published in docs/verification/.
- W15: Implement 5 golden vectors
  - Deliverable: tests + expected outputs for 5 cases.
  - Done when: CI passes and outputs stored.
- W16: Implement 5 more vectors
  - Deliverable: total 10 verified cases.
  - Done when: tests pass in CI.
- W17: Implement 5 more vectors + edge cases
  - Deliverable: total 15 verified cases (v1.0 target met).
  - Done when: tests pass in CI.
- W18: Verification case documentation
  - Deliverable: each verified case has source reference (SP:16, textbook, hand calc) and tolerance rationale.
  - Done when: docs/verification/README.md lists all 15 cases with citations.
- W19: Verification runner
  - Deliverable: one command to run full verification pack.
  - Done when: CI uses the runner.
- W20: Published outputs
  - Deliverable: sample JSON/CSV/DXF outputs in docs/verification/.
  - Done when: linked from docs/README.md.
- W21: Error message audit
  - Deliverable: top 10 errors clarified with hints.
  - Done when: tests updated with expected messages.
- W22: Edge-case coverage
  - Deliverable: tests for min/max/zero boundary cases.
  - Done when: edge cases pass with clear errors.
- W23: Trust summary page
  - Deliverable: concise "How to trust results" page.
  - Done when: referenced in README.md.
- W24: Doc drift guard
  - Deliverable: check_doc_versions.py covers all version markers.
  - Done when: CI clean with no drift.
- W25: External review
  - Deliverable: 1 engineer review feedback captured.
  - Done when: issues triaged in docs/TASKS.md.
- W26: Verification milestone + stabilization buffer
  - Deliverable: verification pack v1 + fix any Phase B regressions.
  - Done when: pack runs in CI, docs updated, zero open Phase B issues.

### Weeks 27-39: Stability, Security, Parity (Phase C)
- W27: Parity harness design
  - Deliverable: design doc + harness stub.
  - Done when: Python and VBA can run same vector set.
  - Note: VBA tests run manually via `Run_All_Parity_Tests` in Excel; results compared to Python outputs. Full CI automation is post-v1.0.
- W28: Parity vectors x5
  - Deliverable: 5 parity vectors passing within tolerance.
  - Done when: harness reports pass.
- W29: Parity vectors x10-15 (v1.0 target)
  - Deliverable: 10-15 parity vectors passing (v1.0 scope complete).
  - Done when: parity test in CI, full automation deferred to post-v1.0.
- W30: Security scan in CI
  - Deliverable: dependency scan step (pip-audit or safety).
  - Done when: CI passes and report stored.
- W31: Dependency policy
  - Deliverable: pinning and upgrade policy doc.
  - Done when: policy referenced in docs/contributing/.
- W32: Backward-compat tests
  - Deliverable: fixtures for stable APIs and schema fields.
  - Done when: tests pass.
- W33: Performance baseline
  - Deliverable: benchmark script (500/5000 beams).
  - Done when: baseline recorded in docs/planning/.
- W34: Perf regression guard
  - Deliverable: CI check for regression threshold.
  - Done when: CI fails on regression.
- W35: Batch reliability
  - Deliverable: partial failure handling in job runner.
  - Done when: tests cover mixed pass/fail cases.
- W36: DXF determinism
  - Deliverable: deterministic DXF output test.
  - Done when: output hash stable.
- W37: Release hardening
  - Deliverable: release checklist updated with parity + security steps.
  - Done when: scripts/release.py docs updated.
- W38: Stability release candidate
  - Deliverable: v0.30.x-rc checkpoint.
  - Done when: CI clean across all checks.
- W39: Stabilization buffer
  - Deliverable: fix any Phase C regressions.
  - Done when: zero open Phase C issues.

### Weeks 40-52: Professional UX and v1.0 (Phase D)
- W40: CLI schema v1 enforcement
  - Deliverable: CLI validates job/result schemas.
  - Done when: invalid inputs yield structured errors.
- W41: CLI UX polish
  - Deliverable: examples and help text updates.
  - Done when: docs/getting-started updated.
- W42: Quick-start examples
  - Deliverable: 5 copy/paste examples for common tasks.
  - Done when: examples validated in CI.
- W43: Colab workflow verification
  - Deliverable: colab workflow tested end-to-end.
  - Done when: outputs match expected.
- W44: Cold-start onboarding test
  - Deliverable: install -> result in < 5 minutes.
  - Done when: logged in docs/SESSION_log.md.
- W45: Docs information architecture
  - Deliverable: quick summary vs deep-dive split.
  - Done when: docs/README.md updated.
- W46: API stability review
  - Deliverable: confirm no breaking changes since freeze.
  - Done when: review entry logged.
- W47: External CLI test (second run)
  - Deliverable: second cold-start test log.
  - Done when: pass recorded and issues triaged.
- W48: v1.0 release candidate
  - Deliverable: v1.0.0-rc1.
  - Done when: CI clean and release notes drafted.
- W49: RC fixes
  - Deliverable: close all RC issues.
  - Done when: no open RC tasks.
- W50: Final security and parity pass
  - Deliverable: security scan and parity harness green.
  - Done when: CI passes all required checks.
- W51: Release prep
  - Deliverable: final CHANGELOG and RELEASES entries.
  - Done when: notes approved.
- W52: v1.0.0 release
  - Deliverable: release tag, publish, announcement.
  - Done when: release verified from fresh install.

---

## Notes
- If actual weekly time is lower, extend the plan by adding buffer weeks between phases.
- If actual weekly time is higher, keep WIP=1 but shorten each phase by merging low-risk weeks.
- **Backlog review cadence:** Once per phase (W13, W26, W39, W52) — triage P1/P2 items, close stale issues, reprioritize if needed.
- **Release mechanics (W52):** PyPI via `twine upload`, GitHub Release with `.xlam` asset, README badge update.

## Current Progress (as of 2025-12-28)

**Position:** Week 2 (S-007 is the gate)

**Pre-completed (out of order):**
| Week | Task | Status |
|------|------|--------|
| W01 | Scope lock + WIP rule | ✅ Done |
| W27 | Parity harness stub | ✅ 10 vectors in Python |
| W45 | Docs info architecture | ✅ project-status.md split |

**Current gate:**
- **W02 / S-007:** External engineer CLI test (requires human tester)
- Required by W06 for the v0.20.0 checkpoint; if waiting on a tester, proceed with W03 while keeping WIP=1.

**Next after S-007:**
1. W03: Error schema draft
2. W08: Schema v1 (job + results + schedule + clause tags)
3. W14-W17: 10-15 verified examples

Last updated: 2025-12-28
