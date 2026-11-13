---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, serviceability, deflection, cracking, is456]
---

# Check instantaneous beam deflection and flexural cracking

Use `beam.load_instantaneous_service` and `beam.check_instantaneous_service`
with one current service load case. The input includes the physical section,
bar positions, member and reinforcement revisions, and explicit deflection
and crack limits.

## Run the worked example

Use the matching 0.29 candidate, the [example script](../../../Python/examples/beam_instantaneous_service.py)
and the [frozen cases](../../verification/library-029-serv01-beam-service.json).

```bash
python beam_instantaneous_service.py --reference library-029-serv01-beam-service.json \
  --case two_span --output-dir two-span
python beam_instantaneous_service.py --reference library-029-serv01-beam-service.json \
  --case multilayer --output-dir multilayer
python beam_instantaneous_service.py --reference library-029-serv01-beam-service.json \
  --case two_span_tight_limit --output-dir limit-exceeded
python beam_instantaneous_service.py --reference library-029-serv01-beam-service.json \
  --case missing_service_load --output-dir service-held
```

```python
from pathlib import Path

from structural_lib.design.is456 import beam

request = beam.load_instantaneous_service(Path("beam-service-request.json").read_text())
result = beam.check_instantaneous_service(request)
Path("beam-service.html").write_text(beam.render_instantaneous_service_html(result))
```

The two-span case uses two equal 4 m spans, mirrored longitudinal steel
depths, 11.25 kN/m uniform load per span and a 70 kN point load at
each midspan. The support-centre moment is −75 kN·m and the midpoint
moment is +55 kN·m. The resolved maximum instantaneous displacement is
1.7727 mm. The crack checks use the actual top and bottom bars at the
hogging and sagging moment extrema. For the 3 m simply supported
multilayer example, 106.667 kN/m produces a 120 kN·m midpoint moment and
1.5476 mm instantaneous displacement.

The [independent replay](../../verification/check_library_029_serv01_reference.py)
uses the elastic force method and integrates moment divided by stiffness.
The library uses the beam-line stiffness solver and a constant fully
cracked stiffness computed from all actual bar layers. It records the
cracking moment and uses the unmodified elastic tension-surface strain in
the Annex F width expression. The check uses each face’s edges and outer bar-gap midpoints. It requires
equal outer bar diameters and each inner bar to sit behind an outer bar of
equal or greater diameter.
The input's exposure class bounds the supplied crack limit.

The service load case provides the UDL and midpoint point load directly.
The accompanying section or member request supplies geometry and its
revision. The instantaneous check keeps its own calculation identity and
reports separate from the supplied-action strength checks.

A missing load case or limit, a stale revision, or geometry outside the
profile gives HOLD. A calculated limit exceedance gives FAIL. Long-term
deflection stays HOLD and requires the time-dependent load and material
history. The profile excludes torsional and shear cracking, unequal
continuous spans and flanged sections.
