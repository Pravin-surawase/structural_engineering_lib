---
**Type:** Plan
**Audience:** Developers, Product
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Related Tasks:** TASK-CSV-02, TASK-CSV-03
---

# ETABS Automation Bridge — Implementation Plan

# Documentation Reference (CSI API CHM)

- The CSI API ETABS CHM has been extracted under `docs/reference/vendor/etabs/etabs-chm/`.
- Use it as the canonical source for `cOAPI`, `cSapModel`, `Results`, `FrameObj`, and the
  load combo enums (`eNamedSetType`). Link to specific HTML topics when you cite a method
  in the add-in doc so we keep traceable proof.
- Treat the HTML tree as a vendor snapshot and consider pulling the original CHM if disk usage
  becomes a concern. The README in the folder explains how to rerun `extract_chmLib`.

## Goal

Replace manual table export with a one-click ETABS connection:
auto-run analysis if needed, pull required tables, and feed batch design + 3D.

---

- ## Phase 0 — Feasibility + Option Gate (1 week)

- Validate ETABS OAPI connection via COM/.NET on Windows.
- Confirm required tables exist and can be pulled programmatically.
- Confirm analysis status check and run-analysis call.
- Validate whether ETABS supports a menu add-in workflow.
- Record target ETABS versions (v18/v19/v20) so the installer plan can check compatibility.

**Exit Criteria:**
- Able to open model, run analysis, and fetch “Element Forces – Beams”.
- Decision: Bridge-only vs Bridge + ETABS Add-In.

---

## Phase 1 — Local Bridge MVP (2 weeks)

### Build the bridge
- Windows tray app or service (C# preferred).
- Local REST API with token auth (localhost only).

### Endpoints (MVP)
- `/status` (ETABS running? model open?)
- `/analysis/run`, `/analysis/status`
- `/tables/beam_forces`
- `/tables/sections`
- `/tables/geometry`

### Streamlit UX
- “Connect ETABS” button.
- “Export via add-in” callout when the bridge is present.
- If bridge not detected, show “Install Bridge” CTA and link to the manual export.

**Exit Criteria:**
- Single-click connect + table pull.
- Batch design runs from pulled data.

---

## Phase 2 — UX Polish + Installer (2 weeks)

- Create signed installer (MSI).
- Auto-start on login.
- Clear error messages (ETABS not open, license issues, model not analyzed).
- Cache last pull (fast re-open).
- Add auto-update or version check.

---

## Phase 3 — Optional ETABS Add-In (Parallel Track)

- Build minimal ETABS add-in button: “Export to Structural Lib”.
- Trigger analysis, then call bridge or write a JSON bundle.
- Keep add-in optional (bridge remains primary).

### Add-In Timeline & Installer Process

- **Estimated effort:** 4–6 weeks for a developer to deliver a signed installer,
  plus 1–2 days per ETABS release for regression maintenance.
- **Week 1–2:** MVP menu entry, `cOAPI` bootstrap, `Analyze.RunAnalysis`, `Results.FrameForce`.
- **Week 3–4:** JSON normalization, unit metadata, error dialogs, and bridge handoff.
- **Week 5–6:** Installer packaging (MSI or similar), version checks (`cHelper.GetOAPIVersionNumber`), auto-update paths, and release notes.
- Publish installer artifacts to GitHub Releases and document install/uninstall steps
  (create `docs/reference/installer.md` if needed). Include release automation that verifies
  the installer self-updates and logs the version for nightly health checks.

---

## Phase 4 — Hosted Streamlit Support (Future)
---

## Phase 4 — Hosted Streamlit Support (Future)

- Optional secure tunnel (Tailscale/Cloudflare).
- Push model results to cloud for visualization.
- Enterprise deployment patterns.

---

## Open Risks

- ETABS licensing constraints for automation.
- COM instability if ETABS is busy.
- Security of local API (must be localhost-only + token).
- Version drift between ETABS releases and add-in API.

---

## Suggested Tasks (Backlog)

- **ETABS-API-01:** OAPI connection proof (COM/.NET)
- **ETABS-API-02:** Local bridge MVP (REST + table pull)
- **ETABS-API-03:** Streamlit “Connect ETABS” UX
- **ETABS-API-04:** Installer + auto-update
- **ETABS-API-05:** ETABS add-in feasibility spike

---

# Nightly Validation + Strategic Fit

- **Nightly runs:** Automate a nightly check that:
  1. Starts the bridge (or mocks the COM API) and calls `/status`.
  2. Runs `Analyze.RunAnalysis` and fetches `Results.FrameForce`.
  3. Verifies the JSON schema against our exported contract (`docs/specs/csv-import-schema.md`).
- **Strategic comparison:**
  - The bridge + add-in combo beats CSV exports in UX and accuracy because it eliminates manual table selection and exposes units/envelopes directly.
  - CLI exporter or Excel macros can stay as fallback options for unsupported ETABS versions but should defer to the bridge storytelling.
  - Once the local paths are stable, consider a nightly push to a cloud host for shared visualization; the nightly validation ensures we’re ready for that lift.
