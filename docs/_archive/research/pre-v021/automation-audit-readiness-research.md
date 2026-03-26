# Automation Audit Readiness & CI Evidence Research

**Type:** Research
**Audience:** All Agents
**Status:** Implemented ✅
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-AUTOMATION-AUDIT
**Abstract:** Audit readiness and CI evidence practices for automation scripts, plus a concrete roadmap for this repo.

---

## Implementation Status (2026-01-24)

✅ **Phase 1 — Evidence Baseline** (Complete)
- Created `docs/audit/` folder with audit-readiness.md and evidence-bundle-template.md
- Added `audit_readiness_report.py` (25-check evidence collector)
- Added CI evidence bundle job to `python-tests.yml`

✅ **Phase 2 — SBOM + Provenance** (Complete)
- Added `.github/workflows/sbom.yml` (CycloneDX + SPDX generation)

✅ **Phase 3 — CI Efficiency** (Complete)
- Added path-based filtering to `fast-checks.yml` (dorny/paths-filter)
- Python tests skip for docs-only changes
- Docs checks skip for Python-only changes

---

## Executive Summary

This research consolidates audit-readiness practices for automation-heavy repositories and maps them to our current automation system. It also moves the previously misplaced audit block out of the automation catalog and expands it with external standards (SSDF, SLSA, SBOM, Scorecard) and CI evidence patterns.

Key takeaways:
- **Audit readiness** requires consistent evidence: tests, scanners, dependency metadata (SBOM), provenance, and change-control artifacts.
- **SLSA** provides a build-provenance and tamper-resistance roadmap; **SSDF** defines secure SDLC practices; **SBOM standards** (CycloneDX/SPDX) cover component inventories; **OpenSSF Scorecard** gives automated supply-chain risk checks. (Sources below.)
- **CI efficiency** should use path filters and job-level changes to keep PR checks fast while retaining nightly/full validation. (Sources below.)

---

## Scope

**In scope:** audit evidence, CI gating, supply-chain integrity, SBOM/provenance, automation health.
**Out of scope:** implementing new automation scripts (this doc is research + roadmap only).

---

## Current State Snapshot (Repo Reality)

**Automation Coverage (internal):**
- 152 scripts (per `scripts/index.json` updated 2026-01-24).
- Task discovery: `scripts/automation-map.json` + `scripts/find_automation.py`.
- Automation catalog: `docs/reference/automation-catalog.md`.

**Safety Gates (internal):**
- Documentation checks: metadata, similarity, links, versions.
- Streamlit runtime guards: `check_streamlit_issues.py`, `check_fragment_violations.py`.
- Git workflow automation: `ai_commit.sh` + PR helpers.

**CI posture (internal):**
- Fast checks on PRs; full matrix on main merge.
- Lint + typecheck + scanners enabled.

---

## External Standards and Why They Matter

### 1) NIST SSDF (SP 800-218)
SSDF defines secure software development practices across four groups (Prepare, Protect, Produce, Respond). It provides the management + engineering backbone for audit readiness and aligns with procurement requirements. (Sources below.)

**Mapping idea:**
- **Prepare/Protect:** governance scripts, git automation enforcement, dependency management.
- **Produce/Respond:** tests, scanners, post-release checks, incident response documentation.

### 2) SLSA Build Levels + Provenance
SLSA defines build levels and provenance requirements. Build L1 requires attestation that the artifact was built as expected; higher levels add signed attestations and hardened build platforms. (Sources below.)

**Mapping idea:**
- Start with **Build L1**: generate provenance + attestations for release artifacts.
- Target **Build L2** when build service can sign attestations and enforce boundaries.

### 3) SBOM Standards (CycloneDX + SPDX)
- **CycloneDX** is now an Ecma International standard (v1.6) and supports SBOMs across multiple asset types. (Sources below.)
- **SPDX** is an ISO standard (ISO/IEC 5962:2021) and widely recognized for SBOM exchange. (Sources below.)

**Mapping idea:**
- Generate CycloneDX SBOMs for security tooling.
- Provide SPDX SBOMs for compliance/enterprise requests.

### 4) OpenSSF Scorecard
OpenSSF Scorecard provides automated checks for supply-chain security risks and is installable via GitHub Actions. (Sources below.)

**Mapping idea:**
- Use Scorecard as an external audit signal (security posture check).

### 5) CI Path Filters (GitHub Actions)
GitHub Actions supports `paths` / `paths-ignore` for push/PR triggers to avoid running irrelevant workflows. (Sources below.)

**Mapping idea:**
- Keep PR checks under 5-7 minutes by routing heavy checks to nightly or path-specific workflows.

---

## Gaps (Audit & Engineering)

**Evidence Gaps**
- No unified audit evidence bundle (tests + scanners + dependency SBOM + provenance).
- No automated SBOM generation in CI.
- No provenance attestations for build artifacts.

**Testing Gaps**
- Limited API contract tests.
- Limited negative-case coverage for import adapters and error messages.
- Performance baselines not enforced in CI.

**Process Gaps**
- Heavy validators run on PRs even when unchanged.
- Lack of a single audit-readiness report in docs.

---

## Recommended Evidence Bundle

**Goal:** produce an audit-ready artifact set for each release.

| Evidence Type | Tool/Source | Why It Matters | Standard Alignment |
|---|---|---|---|
| Test results + coverage | pytest + CI artifacts | Demonstrates verification | SSDF (PW/RV) |
| Static analysis + scanners | check_streamlit_issues, fragment checks | Prevent runtime failures | SSDF (PW) |
| SBOM | CycloneDX + SPDX | Supply-chain visibility | SBOM standards |
| Build provenance | SLSA provenance attestation | Integrity + tamper resistance | SLSA |
| Supply-chain risk score | OpenSSF Scorecard | External posture signal | Scorecard |
| Change control | PR links + release notes | Traceability | SSDF (PO/RV) |

---

## Roadmap (Practical)

### Phase 1 — Evidence Baseline
- Add `docs/audit/` folder with a single audit checklist template.
- Add CI job to publish test + scanner summaries as artifacts.
- Document minimum evidence requirements per release.

### Phase 2 — SBOM + Provenance
- Add CycloneDX SBOM generation (CI artifact).
- Add SPDX SBOM generation (CI artifact) for compliance needs.
- Prototype SLSA provenance attestation for release builds.

### Phase 3 — CI Efficiency & Risk Posture
- Path-based workflow triggers for docs vs code changes.
- Nightly-only heavy validators + merge-only full matrix.
- Add OpenSSF Scorecard workflow for ongoing risk assessment.

---

## Actionable Next Steps (Repo-Specific)

1. Create `docs/audit/audit-readiness.md` and evidence checklist template.
2. Add a minimal SBOM CI step (CycloneDX first; SPDX optional).
3. Add `audit_readiness_report.py` to compile evidence in one command.
4. Add path filters for heavy workflows to keep PR checks fast.

---

## Related Files (Internal)

- `docs/reference/automation-catalog.md`
- `scripts/index.json`
- `scripts/automation-map.json`
- `docs/research/ai-agent-effectiveness-research.md`

---

## Sources (External)

- NIST SSDF (SP 800-218): https://csrc.nist.gov/publications/detail/sp/800-218/final
- SLSA v1.0 provenance spec: https://slsa.dev/spec/v1.0/provenance
- SLSA levels spec: https://slsa.dev/spec/v1.0/levels
- CycloneDX 1.6 standard (Ecma): https://cyclonedx.org/news/cyclonedx-v1.6-is-now-an-ecma-international-standard
- SPDX ISO/IEC 5962:2021: https://spdx.dev/learn/about-spdx/
- OpenSSF Scorecard (Action + project): https://securityscorecards.dev/ and https://github.com/ossf/scorecard
- GitHub Actions workflow path filters: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onpushpull_requestpaths
