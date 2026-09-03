---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF2
---

# PF2 — evidence and existing-asset audit

PF2 is complete. [baseline.json](baseline.json) classifies current Python, C#,
automation, sourcebook, StructProof and failure evidence before reuse.

## D03 decision

Use selective reuse. Retain bounded pure kernels and traceability controls,
correct engineering meanings and coverage before migration, compatibility-wrap
published paths where meanings can be recovered, replace host/transport
implementations when they are not common semantics, and omit unrelated or
advisory features from the first beam common set. Existing code, tests, schemas
or cross-project agreement never grant migration authority by themselves.

The current Python root exports 489 names, including 466 callables; the services
facade exports 245 callables. The committed
[surface audit](audit_public_surfaces.py) assigns every callable through ordered
module rules and separately covers 15 advertised CLI entries and 13 family
facades. It also lists all five working C# operations, four Excel functions and
the shared contract/validation types.

The 20 historical/current failure families retain their original states and
each has a prevention rule and acceptance test. The evidence scale distinguishes
planning, build, focused software, correlated comparison, independent
engineering, installed application and qualified approval evidence.

## Exit review

- Every current public/de-facto surface has an exact or deterministic-group
  disposition candidate.
- AO01-AO26 remain requirements evidence until PF5 defines their semantic
  contracts.
- Sourcebook cases and StructProof agreement are correlated candidate evidence,
  not independent assurance.
- C# compilation and schemas do not establish full member design or installed
  Excel/ETABS behavior.
- All F01-F20 prevention rules and acceptance evidence remain visible.

PF3 may now use PF1 workflow demand and this asset evidence together; no function
is selected because it merely exists.
