---
**Type:** Research
**Audience:** Developers, Product
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Related Tasks:** TASK-CSV-02, TASK-CSV-03
---

# ETABS Automation Integration — UX-First Options

## Executive Summary

Manual export (select table → export → convert → upload) is too slow for first-time
users. The best user experience is **one-click connect** to a local ETABS instance,
auto-run analysis if needed, then pull required tables directly via API.

Because ETABS exposes a **local COM/.NET API**, a **web-hosted Streamlit app cannot
directly access it** without a local bridge or a local app running on the same
Windows machine.

This document expands the option set, evaluates each path in depth, and
recommends a phased plan.

---

## Constraints (Reality Check)

- **ETABS API is local** (COM/.NET). It runs on Windows, on the same machine as ETABS.
- **Streamlit Cloud cannot reach local COM** unless a local bridge exposes data.
- A **non-technical install** must be a 1-click installer with a tray icon and
  auto-start; zero config is the goal.

---

## Evidence + Inputs (Current, Mostly Local)

We cannot access external web sources from this environment. The following inputs
are from prior internal research and archived docs:

- **Anecdotal reliability issues** with ETABS OAPI across versions are cited in
  `docs/publications/findings/00-research-summary-final.md`.
- **Forum threads** with ETABS API reliability reports are referenced in
  `docs/_archive/publications/01-engineer-pain-points.md`.

These are useful signals but should be validated with the official CSI OAPI
documentation and ETABS release notes when available.

---

## Options (Ranked by UX + Reliability)

### Option A — Local ETABS Bridge (Recommended)

**Idea:** Small Windows app/service connects to ETABS via OAPI and exposes a
local REST API for our Streamlit UI.

**Pros:**
- One-click connect, no manual exports.
- Most robust and scalable.
- Can enforce required tables and validation.

**Cons:**
- Requires installing a helper app.
- Windows-only (ETABS is Windows anyway).

**Best for:** Web UI + local ETABS integration.

---

### Option B — Local Streamlit App (Fastest to Ship)

**Idea:** Run Streamlit locally on the same machine as ETABS.

**Pros:**
- Simplest integration (direct COM API).
- No bridge needed.

**Cons:**
- Not a hosted web experience.
- Requires local Python/Streamlit setup.

**Best for:** Power users and internal workflows.

---

### Option C — ETABS In-App Add-In (Strong UX for Non-Technical Users)

**Idea:** A C#/.NET add-in appears inside ETABS (menu button). Users click
"Export to Structural Lib," the add-in runs analysis if needed and sends data to
the local bridge or writes a JSON bundle.

**Pros:**
- Best in-app UX (no separate app to find).
- Clear context: user is already in ETABS.
- Can enforce correct table selection and load combo logic.

**Cons:**
- Requires ETABS add-in deployment knowledge.
- Add-in API surface must be validated across versions.

**Best for:** Engineers who live in ETABS daily.

---

### Option D — Excel/VBA or VSTO Add-In (Fallback)

**Idea:** Excel macro calls ETABS API and exports required tables to CSV/JSON,
then user uploads once.

**Pros:**
- Familiar to many structural engineers.
- No new app installer if Excel is already used.

**Cons:**
- Still file-based, slower than live API.
- Excel dependency.

**Best for:** Low-friction fallback during beta.

---

### Option E — CLI Exporter (Headless Helper)

**Idea:** A tiny `etabs-exporter.exe` runs on the ETABS machine, reads tables
via OAPI, and writes a single JSON/ZIP artifact that Streamlit can ingest.

**Pros:**
- Minimal UI, easy automation.
- Can be invoked by the bridge or scheduled.

**Cons:**
- Still file-based (upload step remains).
- Non-technical users need a small launcher or wrapper.

**Best for:** Early adopters and batch pipelines.

---

### Option F — Cloud ETABS Server (Future)

**Idea:** Run ETABS on a Windows server; user uploads model, app runs analysis.

**Pros:**
- Fully web-native.
- No local install for users.

**Cons:**
- ETABS licensing + server cost.
- Model IP/privacy concerns.

**Best for:** Enterprise or managed SaaS.

---

### Option G — UI Automation (Not Recommended)

**Idea:** Use UI automation (AutoHotkey/WinAppDriver) to drive ETABS export
dialogs automatically.

**Pros:**
- Zero API integration.
- Fast prototype.

**Cons:**
- Extremely brittle, breaks across versions or UI changes.
- Hard to support at scale.

**Best for:** Short-lived prototype only.

---

## Quick Comparison Matrix

| Option | UX Quality | Install Friction | Reliability | Time to Ship |
| --- | --- | --- | --- | --- |
| A. Local Bridge | High | Medium | High | Medium |
| B. Local Streamlit | Medium | Medium | High | Fast |
| C. ETABS Add-In | High | Medium | Medium | Medium |
| D. Excel Add-In | Medium | Low | Medium | Fast |
| E. CLI Exporter | Medium | Low | Medium | Fast |
| F. Cloud ETABS | High | High | Medium | Slow |
| G. UI Automation | Low | Low | Low | Fast |

---

## What We Must Pull (Minimum Data)

From ETABS API / tables:
- **Element Forces – Beams** (M3, V2, Station, Output Case)
- **Frame Section Assignments**
- **Frame Section Properties (Rectangular concrete)**
- **Joint Coordinates / Frame Connectivity**
- **Story Definitions**
- **Optional Axial (P)** if needed for axial effects

This is sufficient for:
- Batch design (envelopes per beam)
- Governing combo selection per beam
- 3D visualization placement

---

## Data Retrieval Strategy (API vs Export)

**Preferred:** Use ETABS `DatabaseTables` / OAPI to pull table data directly into
memory (no file round-trip).

**Fallback:** Export tables to CSV/Access/Excel and parse.

**Why it matters:** Direct table access avoids user error (wrong tables, missing
combos) and removes the "export/convert/upload" step that kills early adoption.

---

## Suggested API Bridge Endpoints

Minimal REST endpoints for the local ETABS bridge:

```
GET  /status                # ETABS running? model open?
POST /analysis/run           # run analysis (if needed)
GET  /analysis/status        # polling (percent + success)
GET  /tables/beam_forces     # Element Forces – Beams
GET  /tables/sections        # Section assignments + properties
GET  /tables/geometry        # Joints + connectivity + stories
```

---

## Recommended Path (Phased)

**Phase 1 (Now):**
- Keep CSV import (baseline).
- Add “Connect ETABS (beta)” button that detects local bridge.
- If bridge not installed, show “Download Bridge” link.
 - Add a second CTA: “Export via ETABS Add-In” (optional).

**Phase 2 (Next 2-4 weeks):**
- Build local bridge (C# preferred or Python COM).
- Add automated table pulls and validation.
- Add “Run analysis” if not analyzed.
 - Package as MSI with auto-start and tray icon.

**Phase 3 (Later):**
- Optional secure tunnel for hosted Streamlit.
- Push data to cloud for shared visualization.
 - Enterprise controls (auth, audit logs, license checks).

---

## Open Questions

1. Which ETABS versions must be supported (v18/v19/v20)?
2. Can we bundle ETABS API interop DLLs with the bridge installer?
3. UX: should bridge auto-start with ETABS or run independently?
4. Do we need an ETABS in-app add-in to reduce confusion for new users?
5. What is the minimum compatible Windows + .NET version for the installer?

---

## External Validation Checklist (Needs Online CSI Docs)

- Confirm `DatabaseTables` methods cover required result tables and units.
- Verify add-in/plug-in APIs are supported and stable across ETABS versions.
- Validate automation licensing limits (single seat, network, enterprise).

---

## Summary Recommendation

**Primary:** Local ETABS bridge (simple installer + REST).
**Secondary:** ETABS add-in for in-app export (if API supports it).
**Fallback:** CSV pipeline + optional Excel/CLI export.
**Future:** Cloud ETABS server for enterprise.
