---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-TRUTH-HYGIENE-38-2
---

# INDIA-2 Clause 38.2 Truth-Hygiene Evidence

## Decision

**REPAIR** the live beam-flexure source identities and arithmetic together.
The controlled IS 456 source has Clause 38.1 and Annex G beam/section cases,
but no Clause 38.2, 38.3, or 38.4. Independently replayed equilibrium also
proved that the legacy rounded `4.6` inverse equation can change a supported
maximum-steel PASS/FAIL result. A metadata-only repair would therefore leave a
false-safe result in the supported beam workflow.

This packet does not expand beam scope, add a structural element, change a
public signature, authorize professional use, or change release state.
Qualified engineering review remains mandatory.

## Controlled-source binding

The controlled consolidated IS 456 source has SHA-256
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
The complete Amendment 6 source has SHA-256
`4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
Their custody and acquisition identities are recorded in
[IS 456 library-first evidence](is456-library-first-evidence.md).

Inspection of the controlled extraction binds rectangular stress-block
assumptions to Clause 38.1, rectangular sections without compression
reinforcement to Annex G-1.1, rectangular sections with compression
reinforcement to Annex G-1.2, and the relevant flanged case to Annex G-2.2.
The extraction contains no Clause 38.2, 38.3, or 38.4 identifier. No source PDF,
scan, page image, watermark, or protected clause prose is added here.

The pre-publication Git boundary is recorded in the
[task-to-Git handoff receipt](india-2-truth-hygiene-38-2-git-handoff-receipt.json).
It is deliberately `HOLD` before remote, review, PR, and integration evidence
exists and grants no cleanup or release authority.

## Consumer and provenance repair

The bounded consumer inventory covered the clause registry, decorators, exact
steel solver, singly and doubly reinforced beam results, both flanged result
paths, decorator examples/tests, parity and regression fixtures, active formula
and architecture documents, the clause maps, and the generated Indian-code
manifest.

- `calculate_ast_required` and singly reinforced design now bind Clause 38.1
  and Annex G-1.1.
- Doubly reinforced design binds Clause 38.1, G-1.1, and G-1.2.
- Flanged design retains Clause 23.1.2 and G-2.2 and reports the applicable
  G-1.1/G-1.2 rectangular-web identities.
- The registry removes unsupported 38.2/38.3/38.4 metadata and adds G-1.2.
- Public result signatures and units remain unchanged. The existing
  `clause_refs` carrier now serializes only supported identifiers.
- The deterministic Indian-code manifest contains 173 known references, 98
  registered known references, and zero registration-only references.

Historical plans and session evidence that describe the discovered stale
identifier remain unchanged as history; they are not implementation authority.

## Independent arithmetic replay

The shared solver uses the smaller physical root of:

`Mu = 0.36 fck b xu (d - 0.42 xu)`

and then:

`Ast = 0.36 fck b xu / (0.87 fy)`.

For `b=230 mm`, `d=450 mm`, `Mu=100 kN m`, `fck=20 N/mm2`, and
`fy=415 N/mm2`, it returns `xu=157.2800401338862 mm` and
`Ast=721.3841475189461 mm2`. Back-substitution returns
`100000000 N mm`, within floating-point tolerance.

The outcome discriminator uses `b=300 mm`, `d=500 mm`, `D=550 mm`,
`Mu=572.05 kN m`, `fck=55 N/mm2`, and `fy=250 N/mm2`:

| Calculation | Required steel | Maximum steel | Disposition |
|---|---:|---:|---|
| Legacy rounded inverse | `6571.474429705084 mm2` | `6600 mm2` | false `PASS` |
| Exact equilibrium | `6600.050311675635 mm2` | `6600 mm2` | `FAIL`, `E_FLEXURE_003` |

The exact root is `xu=241.66850888711292 mm`; back-substitution returns
`572.05 kN m`. This supported-case outcome change is the arithmetic-repair
authority. The canonical exact solver now lives in the common stress-block
module; the slab helper delegates to it while preserving its existing error
contract.

## Validation

- Focused flexure, slab compatibility, traceability, manifest, parity,
  regression, service, property, and unit selection: `190 passed`.
- Focused FastAPI beam, capability, and public-documentation contracts: `17
  passed`.
- The manifest was generated once after executable truth froze, and its
  deterministic-current test passes.
- The new semantic acceptance module rejects reintroduction of nonexistent
  Clause 38.2/38.3/38.4 registry or active clause-map identities.
- Links, indexes, quick `10/10`, normal hooks, hosted checks, immutable-head
  review, and merge-tree equality complete during publication closeout.

## Remaining boundary

This receipt closes only `INDIA-2-TRUTH-HYGIENE-38-2` on merge. Decision-only
`INDIA-2-FOUNDATION-PILE-CAP-G0` is next in a fresh lane. Pile-cap or raft
calculation code, cleanup/deletion, release, React expansion, complete
engineering approval, and professional approval are not authorized here.
