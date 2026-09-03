---
owner: Main Agent
last_updated: 2026-09-04
doc_type: spec
phase_id: PF10
---

# PF10 — migration, versioning and documentation

PF10 is complete. [baseline.json](baseline.json) gives every current Python and
C# surface a migration disposition, defines semantic translations and adoption
stages, separates all version axes, and lays out documentation/examples for
ordinary library, Excel and ETABS users.

## D21 and D22 decisions

Existing Python users are not forced into Excel or abandoned. The 489 root
exports, 245 service exports, 15 CLI routes and 13 family facades remain covered
by ordered disposition groups. Beam operations migrate to PF5 semantics;
recoverable callers use visible compatibility wrappers. Existing non-beam
Python facades keep their current supported contracts and are not automatically
ported to C# without a separate scope and assurance decision.

The current C# foundations become compatibility or retained kernels under the
new semantic operations. Vendor-specific force input moves to the ETABS adapter;
ranking gains the profile-derived expected leaf set and reason-coded exclusions.
The four existing XLL functions delegate to the new function families while
workbook users move through a copy-producing migration command.

Compatibility translates span, cover, reinforcement state, bar length, cost,
optional values, results, action bases and required checks. It refuses ambiguity
instead of reproducing a known unsafe result. Introduction, translation,
documentation, deprecation and major removal are separate adoption stages.

Package, semantic operation, schema, profile, code data, assurance corpus,
workbook, adapter and report-template versions remain distinct and travel with
results. Old calculations replay against their exact dependencies or state that
they are not replayable; they never recalculate silently using new rules.

Documentation starts with normal Python/.NET use, then concepts and semantic
operations, followed by Excel/ETABS adapters. Nine curricula progress from bar
area to complete member/construction work, workbook operation, ETABS snapshot,
coupled reanalysis and review.

## Exit review

- Ordered rules cover all audited Python surfaces and exact advertised routes.
- Eleven current C# surface groups have a final target.
- Ten semantic translations and eight consumer paths preserve useful callers.
- Nine independent version axes prevent package numbers hiding engineering change.
- Nine example curricula serve Python, .NET, Excel, ETABS and reviewer journeys.

PF11 now integrates these completed decisions into the bounded implementation
backlog and first independently reviewable work packet.
