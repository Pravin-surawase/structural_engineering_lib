---
owner: Main Agent
status: planned
last_updated: 2026-11-12
doc_type: spec
---

# Beam–column programme: delivery and usability

## Decision and reading map

The owner wants ordinary beam and column variations to be inputs to a dependable
workflow, not new implementation tasks. A capability is complete only when an
engineer or AI caller can discover it, supply valid inputs, understand its limits,
and reproduce checked results and physical outputs. This is a planning update,
not implementation, release authorization or a claim of completed engineering.

- **What and why:** this concise delivery guide.
- **Exact engineering scope and evidence:** [0.29 S0–S5 plan](library-usability-improvement.md#029-beam-column-and-slab-parity-plan), including BEAM, COL, SERV, SL, FLOW, DUCT and PROJECT case IDs.
- **Caller/API rules:** [beam facade](../reference/beam-facade.md), [API levels](../reference/api-levels.md), [API stability](../reference/api-stability.md), and the existing LIB-PRO-015 quality obligations in the parent plan.
- **Available now:** the installed package's capability contract and its exact release documentation, not this future plan.

Keep one engineering case authority, one capability registry, one public contract
ledger and one example inventory. Do not duplicate them in this guide. Earlier
historical sections of the parent plan do not override this current programme.

## Milestones, dependencies and versioning

Use stable **M0–M8 planning IDs**. The repository's
[versioning policy](../guidelines/api-evolution-standard.md#2-semantic-versioning-semver)
assigns bug fixes to patches and new features to minor releases, including 0.x.
The expanded S0–S5 plan remains the 0.29 target. Milestones are internal delivery
units and may share one candidate. Assign versions to any later feature
candidates when their scope is frozen. A narrower 0.29 candidate requires an
explicit scope decision and qualification of that exact candidate. Release
authorization is separate.

| ID | Deliverable | Dependency and closure rule |
|---|---|---|
| M0 — baseline and shared contracts | Preserve the current COL02/03 and slab-contract evidence. Freeze shared units, signs, coordinates, action rows, analysis revision, bar identity and status/error semantics. Reconcile discovery for the qualified profiles. | S0/S1 before each dependent slice. Add the pinned source schema when the first FLOW04 adapter is selected. Start public APIs, runnable examples and guides with each slice. |
| M1 — routine beam actions and sections | Simply supported, continuous and cantilever rectangular/T/L members; signed span/support actions and multilayer steel. | BEAM01–BEAM04 and FLOW01. Validate effective-flange assumptions, end orientation, support-face stations and admitted load patterns. Reuse existing qualified paths. |
| M2 — combined beam response and serviceability | Concurrent flexure/shear/torsion, including bounded equilibrium torsion; cracking and short-/long-term deflection. | BEAM06/07 and SERV01/02; distinguish ULS from SLS actions and retain creep/shrinkage/loading-history limits. Missing required sustained-load information holds the applicable service check. |
| M3 — slender rectangular columns | Actual cages, signed end moments, unequal effective lengths, minimum eccentricity and declared second-order basis. | [COL04 on COL02/03](library-usability-improvement.md#next-implementation-packet-col04). Start with the normalized member-action contract and direct Python intake. This is the next engineering packet. |
| M4 — circular columns and selection | Tied/spiral cages and explicit finite-catalogue sizing, bars and ties. | COL05/06; catalogue feasibility is not global optimum or engineering acceptance after a stiffness change. Independent references before implementation. |
| M5 — complete member detailing | Beam/column shear and transverse zones, anchorage, curtailment, laps, congestion, drawings and BBS tied to the checked bars. | BEAM05 and COL07. Earlier slices ship their local physical checks. M5 closes member-wide continuity and fabrication, with ductile joints in M7. |
| M6 — complete imported-project workflow | Batch/storey summaries and governing-combination provenance across both elements; replay revised models. | Builds on FLOW04's pinned member-row adapter and revision checks. Reconcile every supplied row and preserve axes, case identity and freshness. |
| M7 — bounded ductile frame/joints | IS 13920 interior/exterior joints, capacity shear, confinement, SCWB, joint shear and anchorage in admitted directions. | DUCT01/02, M3/M5 and compatible actions. Existing SCWB is not whole-joint PASS. Full seismic-system qualification remains outside scope. |
| M8 — programme closeout | Three reference projects, independent review and exact installed wheel/sdist evidence. | PROJECT01–03, all promised cases and advertised surfaces; distinguish gravity-only closure if ductile evidence remains held. |

Slab commitments and all previously qualified regression families remain in the
matrix. Foundation/stair extensions remain separately tracked, not quietly
counted as completed by this beam–column programme. No new calendar commitment
is implied. An unresolved mandatory family cannot be hidden by a completion
percentage or by relabeling a milestone.

## Cross-cutting gaps to close explicitly

- **Action completeness:** checking all supplied rows is not proof that the
  engineer supplied every required combination. Record the declared combination
  inventory and external completeness responsibility; distinguish ULS, SLS and
  sustained actions. No completed member claim from an incomplete required set.
- **Import admission:** test unit conversion and rounding, gaps in required
  stations, duplicate IDs, conflicting revisions, axis transforms, lost concurrent
  rows and modal/response-spectrum outputs that cannot be interpreted as signed
  concurrent actions. Reject or HOLD incompatible evidence; never manufacture
  concurrency from separate envelopes.
- **Physical assumptions:** effective flange width, lateral/restraint basis,
  cover/exposure, support-face geometry and admitted construction tolerances
  belong in the input/evidence contract, not undocumented example constants.
- **Constructibility and quantities:** check bar bends/fit, interference, splice
  zones and feasible transverse reinforcement. Reconcile BBS centreline/bend
  conventions independently; do not accept agreement between two outputs that
  merely share the same erroneous source.
- **Batch and boundary behavior:** mix PASS, FAIL, HOLD and malformed rows; verify
  documented per-row/whole-job behavior and totals without silently dropping
  members. Test both sides of unrounded limits and only round presentation.
- **Joint eligibility:** explicitly exclude or separately qualify corner, offset,
  eccentric and other unadmitted joint geometry. A passed interior/exterior
  fixture cannot silently admit them.

Use the parent plan's [station, import and project controls](library-usability-improvement.md#station-import-and-project-controls)
to test discontinuities, unsupported action components, incomplete combination
inventories and mixed batch results.

Exercise the three project fixtures progressively as their slices become
available, retaining expected HOLDs. In S3, qualify FLOW04's member-row import
and revision mapping against one pinned export with a beam and a column
before claiming imported-member support. M6 adds project-scale execution on
that adapter. SERV03 and SL04–SL07 remain in the parent plan's slab track.

## Code additions and function design

For each packet, name affected existing functions, call sites and typed request /
result owners before proposing new ones. Exact public symbols are selected only
after discovery; illustrative planning names must never appear as callable APIs.

1. Keep geometry, units, identity and action records in existing shared core
   owners; code-specific material laws, factors, limits and detailing stay in
   their code modules. Services orchestrate; UI/HTTP/CLI adapt. Do not place
   engineering formulas in serializers or UI, or introduce a second formula
   implementation for a new facade.
2. Extend the canonical beam/family facade rather than advertising another
   parallel entry point. Preserve supported single-row calls with documented
   compatibility adapters; use typed, keyword-oriented requests for larger
   member workflows. Separate **check supplied reinforcement**, **select from a
   finite catalogue**, and **project approval**. Never infer the last from either.
3. Validate units, finite numbers, domains, mutually exclusive fields, bar fit,
   coordinates, action compatibility and analysis basis at the appropriate shared
   boundary. Publish field-level issue paths and corrective guidance. Missing
   evidence is HOLD; valid but inadequate design is FAIL; invalid input is an
   intake error, not an engineering PASS/FAIL.
4. Carry source model/revision, member/storey/station, local axes, combination
   type/ID, physical bar revision and check-level governing case through results.
   Distinguish strength, serviceability, freshness and independent-review axes.
   Quantity/drawing exports must refuse a misleading accepted label for held or
   stale designs while allowing explicitly marked diagnostic output.
5. Characterize numerical conditioning, convergence bounds, tolerances and
   deterministic catalogue tie-breaking. Use representative batch performance,
   not only a small kernel benchmark; retain correctness before optimization.
6. Update affected tests, schema/contract evidence, examples and capability
   metadata in the same feature packet. Do not postpone usability to M8 or
   rewrite unrelated modules to create a speculative general framework.

### Where to make changes

| Responsibility | Starting point and expected change |
|---|---|
| Request and source actions | Inspect the [six-component action normalizer](../../Python/structural_lib/beam/analysis.py) before extending unit, axis or revision mapping. Adapt existing records where their semantics match. Keep source units, station side and combination evidence traceable after normalization. |
| Engineering checks | Reuse the relevant IS 456 owners and the frozen fixture. For COL04, the [column packet](library-usability-improvement.md#next-implementation-packet-col04) identifies the axis math, positioned-bar strength and cage checks. The service composes their results. |
| Caller API | Start at the [beam facade](../../Python/structural_lib/design/is456/beam.py) or [column facade](../../Python/structural_lib/design/is456/column.py). Show one recommended load/check or design path for each admitted profile and preserve compatible entry points. Add a new public operation when its request or result contract is materially different. |
| Reports, drawings and schedules | Start at the [calculation-package owner](../../Python/structural_lib/reporting/calculation_package.py) and the member's checked result. Carry input, analysis and reinforcement identity into each projection. Read calculation values and governing IDs from the result. |
| Examples, reference and installed checks | Keep one maintained case payload and driver. Update the existing [family guide generator](../../scripts/generate_family_facade_docs.py) and applicable [beam/column archive replay](../../scripts/_lib/release_beam_column.py) when promoting a workflow. Regenerate owned reference pages and retain the independent replay with the case. |

## One discoverable capability contract for people and AI

Extend [the existing capabilities owner](../../Python/structural_lib/services/capabilities.py)
and maintained API/schema registries; do not create a competing support JSON.
Its installed Python/CLI/HTTP views should identify the operation, canonical
entry point, schema/version, explicit units, admissible profiles, limitations,
required inputs, possible dispositions and runnable example/evidence links.
New fields are a reviewed schema change, not an unannounced rewrite of schema 2.0.

Publish planned, implemented, independently qualified and released states
separately. A source-tree feature must not be advertised as installed-release
support. Make unsupported operations discoverable with a reason and safe next
step; an AI must not guess omitted engineering inputs or invent an API.

Regenerate maintained OpenAPI/JSON schemas, signature ledger and documentation
from their owners where supported. Review semantic meaning as well as generated
diffs. Route README, quickstarts, agent bootstrap and `llms.txt` to the same
canonical surface and version. The current short AI guide's legacy API routing
must be reconciled when the new workflow is promoted; retain compatibility
imports but do not present them as the preferred new workflow.

### Test the route a new caller actually takes

1. Run `python -m structural_lib install-preflight --json` and record the
   package version and origin. Use documentation and example assets for that
   release or exact candidate. The same version string can appear on a draft
   checkout and on an installed artifact.
2. Run `python -m structural_lib capabilities --json`. Choose by element,
   geometry, reinforcement model, action basis and operation. Show the
   recommended callable, request schema and example beside the applicability
   boundary. Keep ordinary section checks, physical member checks and
   reinforcement selection distinct. A plan row remains a future case until
   its operation is present and qualified in the tested artifact.
3. From a clean consumer directory, follow the matching example with an
   explicit path or versioned download for every required input. Read
   governing station, combination, strength, restraint and the applicable
   HOLD/error fields from the structured result. Follow the documented remedy
   and rerun after changing the input. Confirm a change invalidates the old
   outputs where required.

The COL02/03 candidate has public tied and positioned column checks, while
the column capability entry still describes the older two-face and four-corner
paths. Reconcile that entry and its limitations in the COL04 slice. Preserve
the legacy operation's narrower scope. In the family index, give readers a
short profile chooser with the recommended Python operation, compatibility
names and actual availability of CLI or HTTP routes. Generate or validate
that view against the existing capability and recipe owners using the same
workflow identity. Catch a missing recipe, fixture, schema or advertised
entry point during candidate replay. Verify advertised names resolve and
run from the artifact, the same profile has the same meaning across discovery
surfaces, and an earlier install does not advertise the candidate's additions.

## Documentation and in-depth examples

Organize each admitted workflow into four linked layers:

1. **Quickstart:** tested install/extras, a minimal executable example, expected
   disposition, where outputs go and one explicit scope warning.
2. **Worked engineering example:** problem sketch, geometry and coordinate/sign
   conventions, code edition, assumptions, source actions and independent values,
   step-by-step calculation rationale, governing cases and physical detailing.
3. **Task guide:** checking versus selection, batch/storey execution, import,
   modifying a design, reanalysis rules and how to resolve FAIL/HOLD/errors.
4. **Reference:** exact signatures/schema fields, units, defaults, conditional
   requirements, return fields, limitations, provenance and migration notes.

For every newly advertised workflow, ship a tested Python example with inputs,
expected outcomes and the checked outputs included in that slice. Provide an
invocation or request/response for each other advertised surface. Link every
example to the shared fixture and mark unsupported surfaces in the capability
description.

Examples must include a nominal PASS, a valid design FAIL, missing-evidence HOLD,
and invalid-input error, plus the case's relevant boundary and revision controls.
Add ordinary variations in geometry, reinforcement and actions to prove the
workflow is parameterized rather than a hard-coded demo. Show how to read every
important result, not only how to call the function. Do not fill unknown facts
with plausible defaults. Validate calculation values and quantities; visually
inspect representative drawings/reports for legibility, units, bar marks and
consistency with the checked geometry. A file existing is not output acceptance.

Start each worked guide with **when to use it**, the verified install and
one command that works outside a checkout. Link the input JSON and example
script for the same version and name the output files and expected result.
Use the worked calculation to explain the governing check and give one
concrete input edit with the expected recheck outcome. Keep equations and
reference derivation in the evidence record. Keep requests, field meanings
and diagnostic codes in the generated API reference. Reuse the same driver
in the quickstart and project example where the workflow matches.

## Per-milestone definition of done

Use the existing LIB-PRO-015 and S0–S5 gates, not a new parallel bureaucracy:

- Named engineering cases, supported population and independent references frozen.
- Relevant numerical and physical checks pass; deliberate failure/hold controls
  produce their expected outcomes, and no required check is silently absent.
- Canonical function/contract, every advertised adapter, schema and capability
  description agree on field meaning, status, units and limitations.
- Executable examples and active guides work on the exact candidate artifact.
- A fresh reader and a fresh AI context can discover support, run the documented
  workflow, inspect governing checks and resolve the supplied FAIL/HOLD example
  without private notes or guessed parameters. Retain task/result evidence,
  not a subjective “AI-friendly” label.
- Affected regressions, link/contract/example checks and required hosted checks
  pass on the frozen candidate; final release qualification retains exact wheel
  and sdist provenance and the existing approval gates.
- Changelog lists admitted cases, migrations, limits and evidence. Dashboard
  separates evaluated coverage, passing designs, independently verified cases
  and usable output completion. Documentation completion alone earns no
  engineering-capability percentage.

Work in cohesive vertical slices: reference → kernel → service/facade → adapters
→ output → executable guide → focused evidence. Use bounded internal units,
then batch final checks once per frozen milestone. Do not repeat unchanged broad
suites after every small edit or weaken required verification to save time.

## Open decisions at candidate freeze

Pin the first external import/product version, comparator availability, code
editions/amendments, independent reviewers and any publication approvals.
Assign real release versions according to the unchanged versioning policy.
Unresolved reference or licensed comparator access stays a declared limitation,
not fabricated parity. These are gate items for the implementing owner, not
reasons to stop documenting the programme now.
