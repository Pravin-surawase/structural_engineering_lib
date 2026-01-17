---
**Type:** Research + Plan
**Audience:** Developers, Product
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Related Tasks:** ETABS-API-05
---

# ETABS Add-In Integration — Detailed Plan (UX-First)

## Executive Summary

An ETABS add-in can deliver the best in-app UX (one button inside ETABS) but
requires confirmation that the ETABS add-in API is supported and stable across
your target versions. If supported, a robust v1 is ~4–6 weeks with ongoing
maintenance per ETABS release. This doc defines the UX, architecture, data flow,
unit handling, error cases, and a phased plan.

This document is intentionally conservative: any OAPI specifics are marked as
"verify" until official CSI documentation is provided.

---

## Evidence Status (External Docs Pending)

I cannot access the internet from this environment. This plan assumes ETABS OAPI
availability and add-in support, but **requires validation** against the latest
CSI ETABS API documentation.

**Please provide official docs** if available. Suggested location:
`docs/reference/vendor/etabs/` (we can create this folder).

---

## Goals

- One-click export inside ETABS: run analysis if needed, pull required data,
  and provide a structured payload for Streamlit.
- Minimize user steps (no manual table selection, no Excel conversions).
- Ensure unit correctness and table completeness with validation.

## Non-Goals (v1)

- Cloud-hosted ETABS analysis.
- Bi-directional model editing from Streamlit.

---

## UX Flow (Inside ETABS)

1. User opens ETABS model.
2. Clicks a new menu item: `Tools > Structural Lib > Export`.
3. Add-in checks:
   - Model open
   - Analysis status (run if needed)
   - Required tables available
4. Add-in exports data to:
   - Local bridge endpoint (preferred), or
   - A single JSON/ZIP file (fallback)
5. Streamlit receives data and runs batch design + 3D visualization.

**UI principle:** single button, zero configuration.

---

## Data Requirements (Minimum v1)

- Element forces (beams): M3, V2, station, output case/combo
- Frame section assignments
- Section properties (rectangular RC)
- Joint coordinates and frame connectivity
- Story definitions
- Units (force, length, moment)

**Optional v1.1:** axial force (P), load combo definitions, design combos.

---

## Architecture Overview

```
ETABS (Add-In)
   |
   |  OAPI calls (verify)
   v
Add-In Collector
   |
   |  normalized JSON (units + schema)
   v
Local Bridge (optional)
   |
   |  REST
   v
Streamlit UI
```

**Two delivery modes:**
- **Mode A (Preferred):** Add-in posts to local bridge REST endpoint.
- **Mode B (Fallback):** Add-in writes a JSON/ZIP file for manual upload.

---

## Add-In Responsibilities

- ETABS process attach + model status check
- Run analysis if not analyzed
- Pull tables via OAPI (verify API names)
- Normalize to a stable JSON schema
- Validate completeness and units
- Report errors with user-friendly messages

---

## Unit Handling Strategy

- Read model units from ETABS (verify API)
- Normalize output to SI base (N, mm) or to our CSV schema units
- Include units metadata in the JSON payload
- Provide unit conversion map in the payload header

**Failure modes:**
- Mixed units or missing unit metadata
- Unexpected unit strings
- Partial conversion errors

---

## Error Handling Matrix

| Condition | User Message | Recovery |
| --- | --- | --- |
| ETABS not running | "Open ETABS and load a model." | Retry |
| No model open | "Open a model first." | Retry |
| Analysis not run | "Running analysis..." | Auto-run |
| Table missing | "Required data missing: [table]" | Fix model or update ETABS |
| API error | "ETABS API error: [code]" | Retry or close/reopen ETABS |
| Export failed | "Unable to export. Please retry." | Retry + log |

---

## Data Schema (Proposed JSON)

```json
{
  "meta": {
    "source": "etabs-addon",
    "etabs_version": "verify",
    "units": {"length": "mm", "force": "N", "moment": "N-mm"}
  },
  "model": {
    "stories": [],
    "joints": [],
    "frames": [],
    "sections": []
  },
  "results": {
    "beam_forces": []
  }
}
```

**Note:** Align fields with `docs/specs/csv-import-schema.md` to reduce mapping.

---

## Security + Privacy

- Local-only data by default
- If posting to bridge, require localhost + token
- Never exfiltrate model data without user intent

---

## Automation Strategy

- **CI packaging**: build the add-in into a versioned artifact.
- **Smoke test**: sample EDB + test harness to confirm table pull and export.
- **Schema validation**: JSON schema check in CI.
- **Version pinning**: detect ETABS version at runtime and warn on mismatch.

---

## Phased Plan

### Phase 0 — Documentation + Feasibility (1 week)
- Obtain latest CSI ETABS OAPI and add-in docs.
- Confirm add-in menu integration is supported.
- Validate access to required tables via OAPI.
- Spike: export one table + units.

**Exit criteria:** proof of add-in menu item and successful table pull.

### Phase 1 — MVP Add-In (2–3 weeks)
- Implement menu entry + single Export button.
- Attach to ETABS, run analysis if needed.
- Pull required tables and output JSON.
- Minimal error handling and progress dialog.

**Exit criteria:** JSON payload usable by Streamlit offline import.

### Phase 2 — Bridge Integration (1–2 weeks)
- POST data to local bridge endpoint.
- Add validation responses (missing tables, units mismatch).
- Improve UX and error dialogs.

**Exit criteria:** One-click export into Streamlit UI (bridge path).

### Phase 3 — Installer + Update (1–2 weeks)
- MSI packaging with simple install/uninstall.
- Auto-update check or version mismatch warning.
- Logs and diagnostics package.

**Exit criteria:** non-technical install flow.

---

## Effort + Maintenance Estimate

- **Total v1:** ~4–6 weeks for one developer
- **Maintenance:** 0.5–2 days per ETABS release for compatibility

---

## Open Questions (Need Official Docs)

1. What ETABS versions must be supported (v18/v19/v20)?
2. Does ETABS expose a supported add-in API for custom menu items?
3. What OAPI table names and units fields are guaranteed stable?
4. Are there licensing or automation restrictions for OAPI?

---

## Required Inputs From You

Please provide the latest ETABS OAPI or add-in documentation (PDF or help files).
Suggested location in repo:
- `docs/reference/vendor/etabs/`

If you provide that, I will update this document with verified API calls,
actual table names, and exact units behavior.
