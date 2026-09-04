---
owner: Product owner
status: active
last_updated: 2026-09-03
doc_type: spec
phase_id: PF0
deliverable_id: PF0-D1-charter
---

# Product and library charter

**Decision D01.** Build a reusable structural-engineering platform with native
Python and native .NET libraries for a deliberately maintained common
capability set. The first product journey is standalone reinforced-concrete beam
design in Windows Excel. The later automation journey acquires traceable ETABS
actions, designs and checks members, searches alternatives, reanalyses changes
that affect the structural model, and produces resolved reinforcement,
construction quantities and reviewable records.

## Purpose

The libraries exist to make engineering calculations and substantial member
workflows usable from normal Python and .NET programs as well as from the Excel
product. They provide explicit engineering meaning, reusable calculation and
design services, deterministic data contracts, and evidence that a reviewer can
follow. Excel and ETABS translate host data and commands; they do not become
owners of duplicate formulas.

The present Python package is a substantial source of calculations, workflows
and compatibility obligations. The C# solution proves useful Windows and .NET
boundaries. Neither public surface becomes the new standard merely because it
already exists. PF2 classifies every useful asset, PF4 settles shared meaning,
and PF5 designs professional public signatures before further migration.

## Users and journeys

The primary product user is a structural engineer completing a standalone beam
design and review in Excel. Primary library users are Python engineers and .NET
developers who need small calculations, checks, complete member services or
candidate evaluation without launching Excel or ETABS. The later product user
is an ETABS analyst who needs current, source-identified actions and controlled
redesign. Checkers, detailers and estimators need reproducible calculations,
actual bar arrangements, BBS, bar lengths, concrete and steel quantities,
formwork measurements, priced scope and reports that trace to the checked
member.

The product sequence is:

1. enter project, geometry, materials, actions, reinforcement and design basis
   directly in the Excel workflow;
2. evaluate flexure, shear, torsion, serviceability, detailing,
   constructability and the required combined member outcome;
3. resolve bars, layers, links, anchorage, laps, cutoffs and physical lengths,
   then produce drawings, BBS, quantities, prices, formwork measurements and a
   calculation record;
4. add ETABS acquisition through an immutable normalized snapshot; and
5. search alternatives, apply model-changing candidates only to an identified
   copy, reanalyse when demand dependencies change, and compare current complete
   results.

## Initial direction and boundaries

IS 456 reinforced-concrete beams are the first common engineering focus. The
definition programme covers foundations, action data, bounded analysis,
strength, serviceability, detailing, construction, fabrication, quantities,
pricing, formwork measurement, optimization and reporting needed for that
journey. PF3 decides the exact initially supported beam and topology profiles.
Existing Python slab, column, wall, staircase and footing capabilities continue
under their current supported boundaries; adding them to the native common set
requires a later explicit decision.

The Windows product uses an Excel-DNA adapter. Pure worksheet functions consume
supplied validated data and perform no live COM call, workbook mutation, ETABS
operation or file creation. Explicit commands own import, model access,
analysis, mutation and export. Pure Python and .NET packages install and run
without Excel or CSI dependencies. PF9 selects exact runtime support and
numeric performance budgets from representative environments.

Capacity, demand check, required reinforcement, selected reinforcement,
whole-member completeness and human approval remain different outcomes.
Missing, blank, zero, defaulted and derived values remain different states.
Required checks cannot disappear from an aggregate result. Construction outputs
derive from actual resolved details rather than required steel area alone.
Engineering results preserve effective inputs, applicability, source/code-data
identity and freshness where those facts affect use.

## Success and authority

Success is measured across product fitness, engineering correctness and
completeness, API quality, direct library reuse, Python/.NET parity,
auditability, Excel usability, ETABS integrity, construction reconciliation,
performance, maintainability, migration and candidate-bound delivery evidence.
The measurable targets and definition-owner phases are in
[success-measures.json](success-measures.json).

The product owner is accountable for purpose, priorities, product acceptance
and release authorization. A qualified structural engineering authority is
accountable for code interpretation, applicability and engineering assurance.
The architecture owner is accountable for shared semantics and package
boundaries. Python, .NET, Excel, ETABS, assurance and release roles own their
defined execution evidence. The complete assignment is in
[owner-map.json](owner-map.json).

PF0 authorizes definition work only. PF1-PF11 may decide the areas assigned in
[scope-authority.json](scope-authority.json). They do not implement formulas or
applications, publish packages, create engineering approval, or bypass the
repository's separate release authorization. PF11 converts the completed
definition into bounded implementation packets and reconciles it with the
existing beam programme and the original XLL delivery phases.
No implementation deliverable is authorized by this charter.
