---
owner: Main Agent
last_updated: 2026-09-03
doc_type: phase-record
---

# PF0 — product and library charter

PF0 is complete. It fixes the product purpose, first and later workflows,
reusable-library direction, decision ownership and measurable success before
the programme defines features or signatures.

## Decision

D01 is resolved as follows:

> The project will maintain native Python and native .NET libraries for a
> deliberately selected common semantic capability set. Standalone
> reinforced-concrete beam design in Windows Excel is the first product
> workflow. Normal Python and .NET use must remain first-class. ETABS
> acquisition, checking, candidate search, controlled reanalysis, detailing,
> BBS, quantities, pricing, formwork measurement and reports form the later
> automation workflow around the same reusable services.

This choice avoids two earlier failure paths: treating a language port as a
design, and allowing an application contract to become the engineering API.
Excel and ETABS remain adapters. Substantial workflows can still belong in a
library when they operate only on explicit data.

## Evidence reviewed

| Evidence | Consequence for PF0 |
| --- | --- |
| [Current Python package](../../../../../Python/structural_lib/README.md) and its broad public facade | The old library contains useful engineering math, services and compatibility obligations, but its large re-export surface, mixed defaults and application helpers require PF2 disposition and PF4/PF5 semantic review. |
| [C# foundation](../../../../../CSharp/README.md) | Native .NET and Excel-DNA boundaries are buildable. Current force normalization, geometry, quantities, beam-line analysis and ranking are evidence, not the complete member design or normative shared contract. |
| [Automation requirements](../../automation/README.md) | The user journey requires strength, serviceability, detailing, constructability, bar paths, BBS, quantities, costs, formwork measurement, solver/search, ETABS identity and reviewable outputs. |
| [Reusable-library research](../../reusable-library-research.md) | Python and .NET should share semantic operations and conformance evidence while keeping idiomatic APIs and host-specific adapters. |
| [Requirements-first audit](../../requirements-first/README.md) | The three-project inventory covers 197 issue records, 20 failure families and 180 sourcebook case records. It identifies incomplete aggregation, hidden engineering defaults, stale result identity, contract drift, ambiguous quantities, limited construction estimates and evidence-category mistakes that later phases must prevent. |
| Owner directions recorded on 3 September 2026 | Standalone Excel beam design is first; normal library use and later ETABS-to-design-to-solver automation are required; the work must cover complete beam and construction needs and avoid repeating old-library mistakes. |

The evidence supports the charter but does not qualify any formula, completed
XLL or live ETABS workflow. Those claims require later operation-level,
engineering and installed-application evidence.

## Deliverables

| ID | Artefact | Result |
| --- | --- | --- |
| PF0-D1-charter | [charter.md](charter.md) | Purpose, users, workflows, scope, boundaries and decision are stated in a concise charter. |
| PF0-D2-owner-map | [owner-map.json](owner-map.json) | Six user groups, six journeys, nine accountable roles and consequential decision ownership are defined. |
| PF0-D3-success-measures | [success-measures.json](success-measures.json) | Fourteen measurable outcomes name a target, accountable owner and later definition-owner phase. |
| PF0-D4-glossary | [glossary.json](glossary.json) | Shared programme vocabulary prevents early ambiguity around capacity, checks, completeness, approval, optional values, adapters and evidence. |
| PF0-D5-scope-authority | [scope-authority.json](scope-authority.json) | PF0-PF11 decision boundaries, exclusions, standing authority and the absence of implementation deliverables are explicit. |

Run the phase audit from the repository root:

    bash scripts/python_runtime.sh \
      docs/planning/xll-product/library-definition/pf0/validate_pf0.py

The audit checks cross-file identifiers, owners, measures, glossary terms,
decision resolution, phase authority and completion evidence. It does not run a
calculation or application.

## Exit review

| Exit condition | Evidence | Result |
| --- | --- | --- |
| Each desired outcome has a measure and owner. | Fourteen records in success-measures.json reference roles in owner-map.json and name the later phase that defines its detailed evidence. | Satisfied |
| The standalone Excel workflow and reusable-library purpose are stated. | Charter decision, purpose, users and product sequence; WF-STANDALONE-EXCEL, WF-PYTHON-LIBRARY and WF-DOTNET-LIBRARY. | Satisfied |
| Application delivery and library capability remain distinct. | Charter boundaries, reusable-library definition and phase-authority restrictions. | Satisfied |
| Initial product and code direction are visible without pretending all detailed scope is settled. | IS 456 reinforced-concrete beams are the first common focus; PF3 owns exact profiles and exclusions. | Satisfied |
| No implementation deliverable is included. | scope-authority.json has an empty implementation_deliverables list; all PF0 artefacts are definition records. | Satisfied |
| D01 has the required evidence. | Owner charter, user/journey map and measurable outcome definitions are linked in the decision register. | Satisfied |

PF1 and PF2 are next and may proceed in parallel. PF1 converts the six journeys
into detailed information flows and scenarios. PF2 audits the old Python/C#
surface, callers, examples and failure evidence operation by operation. PF3
waits for both so capability boundaries reflect real workflows and real asset
evidence.
