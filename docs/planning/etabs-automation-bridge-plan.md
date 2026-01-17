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

## Goal

Replace manual table export with a one-click ETABS connection:
auto-run analysis if needed, pull required tables, and feed batch design + 3D.

---

## Phase 0 — Feasibility + Option Gate (1 week)

- Validate ETABS OAPI connection via COM/.NET on Windows.
- Confirm required tables exist and can be pulled programmatically.
- Confirm analysis status check and run-analysis call.
- Validate whether ETABS supports a menu add-in workflow.

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
- If bridge not detected, show “Install Bridge” CTA.

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
