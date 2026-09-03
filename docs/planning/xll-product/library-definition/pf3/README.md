---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF3
---

# PF3 — capability scope and library boundaries

PF3 is complete. [baseline.json](baseline.json) maps all 17 capability families
and AO01-AO26 to reusable foundations, IS 456 calculations, reusable services,
application adapters, delivery or quality work.

## D04 and D05 decisions

The dependency direction is core quantities/contracts, then design-code
calculations, then reusable services, then application adapters. Whole-member
design, bounded analysis, reinforcement resolution, BBS data, quantities,
pricing, formwork measurement, calculation records and candidate search remain
normal library services when they operate on explicit data. Excel, ETABS COM,
workbook/model mutation and file rendering stay outside the engineering core.

The first common engineering profiles cover explicit foundations, a bounded
planar beam-line solver, ordinary IS 456 reinforced-concrete sections, and one
or more collinear beam spans with complete strength, serviceability, detailing,
fit and construction data. Seismic detailing and ETABS-connected use follow the
ordinary standalone slice through the same member contract.

Deep, curved, prestressed, hollow, composite and other special beams, global
building analysis, other code families and formwork temporary-works design are
visible extensions rather than silent partial support. Nonzero actions outside
a selected interaction method make that operation inapplicable; they are never
discarded.

## Exit review

- Every capability serves one or more PF1 workflows.
- AO01-AO26 each has a capability and responsibility owner.
- Reusable work contains no workbook, COM, process or rendering dependency.
- Six supported-profile definitions state their limits and order.
- All initial exclusions have a reason and decision owner.

PF4 now owns the exact quantities, units, signs, axes, topology, optional values,
identities and result states shared by every profile.
