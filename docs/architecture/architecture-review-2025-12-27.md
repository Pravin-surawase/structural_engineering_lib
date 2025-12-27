# Architecture Review — 2025-12-27

**Requested by:** main agent  
**Reviewer:** ARCHITECT agent (role doc in `agents/ARCHITECT.md`)  
**Context used:** `docs/architecture/project-overview.md`, `docs/architecture/deep-project-map.md`

---

## Prompt to ARCHITECT

Act as ARCHITECT. Use `docs/architecture/project-overview.md` and
`docs/architecture/deep-project-map.md`. Review the current architecture for:
layer boundaries, dependency direction, and risks to scalability/parity.
Provide findings and concrete recommendations.

---

## ARCHITECT Findings

### 1) Application logic duplicated in multiple entrypoints
**Where:** `Python/structural_lib/__main__.py` (CLI), `excel_integration.py`, and `job_runner.py`.  
**Risk:** Drift between CLI output, batch/job output, and Excel integration.  
**Recommendation:** Introduce a single application-layer pipeline (e.g., `beam_engine.py`)
used by CLI and job runner, with stable JSON output contract.

### 2) Output schema is implicit and inconsistent
**Where:** CLI output dict in `__main__.py`, job runner output, and examples docs.  
**Risk:** Consumers will depend on fields that may diverge; docs can drift.  
**Recommendation:** Document a canonical result schema (JSON), version it,
and have CLI/job runner emit the same structure.

### 3) Units and assumptions are enforced only at API edge
**Where:** Core functions accept raw numbers; `api.py` enforces units string,
but CLI inputs are parsed without unit validation beyond field names.  
**Risk:** Silent unit drift in CSV workflows.  
**Recommendation:** Add explicit units assumptions to CLI help/docs and
centralize unit validation in application layer.

### 4) Optional dependency boundaries are correct but need stronger guardrails
**Where:** `dxf_export.py` requires `ezdxf` but is reachable from multiple paths.  
**Risk:** Users hit runtime errors in batch runs.  
**Recommendation:** Ensure every path that can call DXF checks availability
and surfaces a clear error message; keep DXF out of core.

### 5) Parity risk still central
**Where:** Core math exists in Python and VBA with partial parity guarantees.  
**Risk:** Silent divergence for edge cases.  
**Recommendation:** Track parity-critical functions, add parity vectors,
and require parity checks before 1.0.

---

## Main Agent Decision

**Accept now (document + schedule):**
- Create a single application-layer pipeline for CLI/job outputs (P1).
- Define and version a canonical JSON output schema (P1).
- Strengthen unit assumptions in CLI docs and validate at the app layer (P2).

**Defer (track for v1.0 readiness):**
- Parity harness expansion and parity gates (P1 but larger scope).
- Optional dependency guardrails review across all DXF entrypoints (P2).

---

## Final Actions (this pass)

- Logged this review in `docs/architecture/architecture-review-2025-12-27.md`.
- No code changes made in this pass.
- Next steps: convert accepted items into tasks when ready.

