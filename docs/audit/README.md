# Audit Evidence & Readiness

**Type:** Reference
**Audience:** All Agents, Auditors, Compliance
**Status:** Approved
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24

---

## Purpose

This folder contains audit evidence templates, checklists, and generated reports for demonstrating software quality, security posture, and compliance readiness.

**Standards alignment:**
- NIST SSDF (SP 800-218) — Secure Software Development Framework
- SLSA Build Levels — Supply-chain integrity
- CycloneDX/SPDX — Software Bill of Materials (SBOM)
- OpenSSF Scorecard — Automated security checks

---

## Contents

| File | Purpose |
|------|---------|
| [audit-readiness.md](audit-readiness.md) | Master checklist and evidence requirements |
| [evidence-bundle-template.md](evidence-bundle-template.md) | Per-release evidence collection template |
| `reports/` | Generated audit reports (auto-created by `audit_readiness_report.py`) |

---

## Quick Commands

```bash
# Generate audit readiness report
.venv/bin/python scripts/audit_readiness_report.py

# Generate report for specific release
.venv/bin/python scripts/audit_readiness_report.py --release v0.6.0

# Check audit compliance status
.venv/bin/python scripts/audit_readiness_report.py --check-only
```

---

## Automation

| Script | Purpose |
|--------|---------|
| `scripts/audit_readiness_report.py` | Generate audit evidence bundle |
| `scripts/check_governance_compliance.py` | Governance health check |
| `scripts/validate_folder_structure.py` | Structure compliance |

---

## Evidence Collection Workflow

1. **Continuous:** CI pipelines collect test results, coverage, scanner outputs
2. **Per-release:** Run `audit_readiness_report.py` to compile evidence bundle
3. **Review:** Verify all checklist items in `audit-readiness.md` are satisfied
4. **Archive:** Store evidence bundle in `reports/` with release tag

---

## Related Documentation

- [../research/automation-audit-readiness-research.md](../research/automation-audit-readiness-research.md) — Research and standards background
- [../reference/automation-catalog.md](../reference/automation-catalog.md) — Script reference
- [../contributing/testing-strategy.md](../contributing/testing-strategy.md) — Testing requirements

---

## Maintenance

This folder is maintained by automation scripts. Manual edits should only be made to:
- `audit-readiness.md` (checklist updates)
- `evidence-bundle-template.md` (template improvements)

Generated reports in `reports/` are auto-created and should not be manually edited.
