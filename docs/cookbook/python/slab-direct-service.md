---
owner: Main Agent
status: active
last_updated: 2026-11-16
doc_type: guide
complexity: intermediate
tags: [slab, serviceability, canonical-api, library-030]
---

# Direct One-Way Slab Serviceability

Use `structural_lib.design.is456.slab.load_direct_service` and
`check_direct_service` for a one-metre tributary strip between two simple
support lines with two free transverse edges. Supply the actual bottom main
bar axes, the crossing distribution layer, the aggregate and nominal cover.
The main bars occupy one centred periodic row without laps in the checked
strip. The result retains the bar axes and uses their actual depth in the
calculation.

Supply the total and sustained unfactored UDL rows for the same analysis and
reinforcement revisions. The check reconciles the concurrent midspan moment
and end shear against the declared span and UDL. Supply the loading age, the
finishes and assessment ages, and the creep coefficients and free shrinkage
strains at those ages. Those coefficients and strains are project inputs.
The transient load enters only at assessment. The result reports the
increment from the actual deflection at finishes.

The scope covers elastic gravity flexure, mild exposure and one way action.
It uses IS 456 Clause 23.2 limits, Annex C deflection and Annex F flexural
crack width with no tension-stiffening reduction. The separate strength,
support anchorage, fire cover and construction tolerance checks still apply.
[IS 456 Clauses 23.2, 24 and Annexes C and F](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf)

## Replay the reference

From the repository root, select a case from the
[frozen B01 fixture](../../verification/library-030-serv03-b01-service.json).

```bash
./scripts/python_runtime.sh Python/examples/slab_direct_service_reference.py \
  --fixture docs/verification/library-030-serv03-b01-service.json \
  --case b01_service_history
```

| Case | Expected result |
| --- | --- |
| `b01_service_history` | PASS with 2.574 mm final and 1.230 mm after-finishes deflection, and zero calculated flexural crack width. |
| `cracked_width_control` | PASS with 0.281 mm crack width against 0.30 mm. |
| `longer_span` | Deflection FAIL, with 19.991 mm at the elastic 5.25 kN/m² witness against an 18 mm final limit. Full-load deflection has no reported value and crack width is HOLD. |
| `longer_span_without_witness` | Both direct checks HOLD outside the elastic ranges. |
| `missing_history`, `stale_reinforcement`, `missing_support_evidence` | HOLD with the missing or stale basis identified. |
