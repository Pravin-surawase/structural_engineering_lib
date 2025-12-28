# Production Readiness Roadmap (12-Month Weekly Plan)

Purpose: reach a professional-grade beam library with pandas-like reliability.

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

Non-negotiables:
- No new feature unless it advances the current week.
- Clear "done" criteria for every task.
- If a week is missed, roll it forward; do not add parallel tasks.

---

## Milestone Gates

Phase 1 (Weeks 1-13): Foundation and API freeze
- Gate: API list frozen, error schema defined, core tests >= 90% branch.

Phase 2 (Weeks 14-26): Trust and verification
- Gate: 20 to 30 verified examples run in CI with published outputs.

Phase 3 (Weeks 27-39): Stability, security, parity
- Gate: parity harness passing on 10+ vectors; security scan clean.

Phase 4 (Weeks 40-52): Professional UX and v1.0
- Gate: cold-start user test passes; CLI schema v1; v1.0 released.

---

## Weekly Plan (W01 to W52)

### Weeks 1-13: Foundation and API Freeze
- W01: Scope lock and WIP rule
  - Deliverable: add WIP=1 rule to docs/TASKS.md and docs/AI_CONTEXT_PACK.md.
  - Done when: rule visible and agreed.
- W02: External CLI test (S-007)
  - Deliverable: cold-start test log in docs/SESSION_LOG.md.
  - Done when: results recorded + issues captured.
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
- W08: Schema v1 draft (job + results)
  - Deliverable: schema files in docs/specs/.
  - Done when: sample JSON validates.
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
  - Done when: recorded in docs/RELEASES.md.
- W13: Foundation release
  - Deliverable: v0.11.x (or internal) checkpoint release.
  - Done when: CHANGELOG and RELEASES updated.

### Weeks 14-26: Trust and Verification
- W14: Golden vector selection
  - Deliverable: list of 20 to 30 verified problems + sources.
  - Done when: list published in docs/verification/.
- W15: Implement 5 golden vectors
  - Deliverable: tests + expected outputs for 5 cases.
  - Done when: CI passes and outputs stored.
- W16: Implement 5 more vectors
  - Deliverable: total 10 verified cases.
  - Done when: tests pass in CI.
- W17: Implement 10 more vectors
  - Deliverable: total 20 verified cases.
  - Done when: tests pass in CI.
- W18: Clause tagging in outputs
  - Deliverable: clause references in result payload.
  - Done when: schema updated and example output shows tags.
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
- W26: Verification milestone
  - Deliverable: verification pack v1.
  - Done when: pack runs in CI and docs updated.

### Weeks 27-39: Stability, Security, Parity
- W27: Parity harness design
  - Deliverable: design doc + harness stub.
  - Done when: Python and VBA can run same vector set.
- W28: Parity vectors x5
  - Deliverable: 5 parity vectors passing within tolerance.
  - Done when: harness reports pass.
- W29: Parity vectors x10
  - Deliverable: 10 parity vectors passing.
  - Done when: nightly parity job added.
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
  - Deliverable: v0.12.x-rc checkpoint.
  - Done when: CI clean across all checks.
- W39: Stabilization buffer
  - Deliverable: fix any regressions discovered in W27-W38.
  - Done when: zero open regressions.

### Weeks 40-52: Professional UX and v1.0
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
  - Done when: logged in docs/SESSION_LOG.md.
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

Last updated: 2025-12-28
