# Data Model Compatibility Checklist (BeamGeometry/RebarLayout)

**Type:** Checklist
**Audience:** Developers
**Status:** Active
**Importance:** Medium
**Created:** 2026-01-08
**Last Updated:** 2026-01-13

---

**Purpose:** Ensure new data models align with existing `structural_lib` outputs.
**Scope:** BeamGeometry, RebarLayout, PreviewPayload, and related planned types.

---

## Checklist (Use Before Adding/Updating Fields)

### BeamGeometry
- [ ] `span_mm` aligns with `design_beam_is456(span_mm=...)` semantics.
- [ ] `b_mm`, `D_mm`, `d_mm` match `BeamDesignOutput.geometry` fields (if present).
- [ ] `cover_mm` aligns with detailing inputs and defaults (no hidden offsets).
- [ ] `effective_span_mm` uses the same rule as beam pipeline (document formula).
- [ ] Units are explicit in field names (mm, kN, kN·m).

### RebarLayout
- [ ] `bars` matches `BeamDetailingResult`/`BarArrangement` structure.
- [ ] `positions_mm` coordinate system documented (origin, axes, sign).
- [ ] `clear_spacing_mm` computed with code-conformant rule (IS 456/IS 13920).
- [ ] `cover_mm` uses the same definition as detailing (clear cover).
- [ ] Bar dia and count correspond to `detail_beam_is456()` output fields.

### LoadDiagramResult
- [ ] `positions_mm` range matches span and support locations.
- [ ] `bmd_knm` and `sfd_kn` align with design sign conventions.
- [ ] `critical_points` map to existing `BeamDesignOutput` critical sections.

### PreviewPayload
- [ ] `geometry` field is always present (even for partial inputs).
- [ ] `rebar` and `bmd` are optional and omitted safely before full analysis.
- [ ] `status` aligns with result status strings used elsewhere ("PASS", "FAIL").
- [ ] `checks` uses the same clause identifiers as compliance results.

### General
- [ ] All new models map cleanly to `BeamDesignOutput` or `BeamDetailingResult`.
- [ ] No duplicate or renamed fields without an explicit migration note.
- [ ] Any derived field has a documented calculation or source.
- [ ] Tests include at least one round-trip check (API → model → preview).

---

## Notes
- Keep new models deterministic and side-effect free.
- Prefer adding models in `structural_lib/types.py` for shared use.
- Update `docs/reference/api.md` glossary when fields change.
