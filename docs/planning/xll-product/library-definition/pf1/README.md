---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF1
---

# PF1 — users, workflows and information flow

PF1 is complete. [baseline.json](baseline.json) expands the PF0 charter into six
end-to-end workflows, an actor matrix, an information inventory and eight
reference scenarios.

## D02 decision

The authoritative workflow baseline is standalone Excel, direct Python, direct
.NET, ETABS automation, construction output and review/correction. The same
semantic engineering capabilities serve the first three. Excel owns workbook
interaction; ETABS owns live acquisition and controlled transactions.
Engineering services consume explicit immutable data.

The standalone route accepts declared manual/supplied actions or a bounded
analysis model and therefore has no ETABS dependency. The ETABS route supplies
geometry and analysis facts but cannot choose the design basis, actual
reinforcement, long-term serviceability assumptions, fabrication/measurement
policies or human approval.

Construction output starts only after the member has current complete checks and
resolved bars. Bar marks, lengths, BBS, quantities, prices and formwork
measurements remain bound to the same detail identity. A correction creates new
calculation/detail/report evidence rather than editing historical evidence.

## Exit review

- Every PF0 user group has a workflow and accountable handoff.
- Ordinary, continuous, redistributed, torsion-affected, seismic-detailing and
  serviceability-controlled beams have reference scenarios.
- Standalone calculation and normal library use do not require ETABS or Excel.
- Live COM, workbook effects and model mutations remain application commands.
- The information ETABS cannot supply is explicit.
- Review, engineering approval, software state and release acceptance remain
  separate.

PF2 supplies the corresponding asset and failure evidence. PF3 uses both
baselines to decide exact capability and supported-profile boundaries.
