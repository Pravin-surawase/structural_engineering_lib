---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, serviceability, creep, shrinkage, is456]
---

# Check a finite-age beam service history

Use `beam.load_finite_service_history` and `beam.check_finite_service_history`
for a simply supported rectangular beam under a sustained gravity UDL and
an additional transient UDL at assessment. Supply the actual bar layers,
both current service cases, and cumulative creep and shrinkage inputs for
the finish and assessment dates.

```bash
python beam_finite_service_history.py --reference library-029-serv02-beam-history.json \
  --case multilayer_history --output-dir history
python beam_finite_service_history.py --reference library-029-serv02-beam-history.json \
  --case missing_sustained --output-dir held-history
```

Use the [example script](../../../Python/examples/beam_finite_service_history.py)
and the [frozen cases](../../verification/library-029-serv02-beam-history.json)
with the matching 0.29 candidate. For application code, pass a complete
request to the loader and send the checked result to
`beam.render_finite_service_history_html`. The HTML and JSON carry the same
input hash and retain qualified review status.

The 3 m example applies 64 kN/m on day 28. The finish measurement is day 90,
with zero added finish load. At day 365 the total load is 106.667 kN/m,
including the transient share. The sample assumes cumulative creep
coefficients 0.6 and 1.2, and shrinkage strains 0.00010 and 0.00022 for
the two dates. Use project-specific finite-age evidence for these inputs.
The humidity and notional size fields record the context of that evidence.

The calculation recomputes the neutral axis and inertia at each effective
concrete modulus with all actual bar layers. It uses the actual tension
steel centroid and both face areas in the Annex C-3 shrinkage expression.
The [independent replay](../../verification/check_library_029_serv02_reference.py)
gives 1.20189 mm on day 90 and 2.09958 mm on day 365. The resulting
after-finishes deflection is 0.89769 mm. The calculated flexural crack
width at assessment is 0.16474 mm using the sustained and transient strain
planes, with zero tension-stiffening credit.

The history treats shrinkage through the Annex C deflection component.
The crack width covers flexural strain. The profile holds reverse bending,
added finish loads, continuous spans and histories outside the declared
basis. It requires separate checks for torsional and shear cracking.
