---
owner: Main Agent
status: active
last_updated: 2026-09-30
doc_type: spec
---

# Library usability and implementation quality

**28 September update:** [LIB-MEMBER-WORKFLOW-002](multilayer-member-workflow.md)
adds the complete multilayer case and supersedes the physical centroid-capacity
method with per-bar equilibrium. Its independent source/reference evidence and
limits are recorded separately. Earlier values below remain historical results
for their stated method revisions; do not interpret them as current v3 values.

Caller-usability milestone: complete through PR #1010. This is not a claim that
every function has received a deep implementation or independent engineering
review. The [function review below](#function-review-lib-deep-review-001) records
the subsequent source inspection, comparisons, repairs and remaining scope.

The owner's goal is a usable library, including improvement of the code already
written. Signatures, examples, and API documentation are part of that goal, not
its limit. Assess the full caller journey and fix confirmed main-process
defects in the current supported workflows. Keep calculation owners, explicit
units, compatibility, and the distinction between software results and
engineering approval intact.

## Work and completion evidence

| Area | Required outcome | Evidence |
|---|---|---|
| Public Python API | Discoverable typed inputs/results, coherent operations, useful IDE help | Public signatures, type-checked callers, generated reference |
| Implementation | Correct data flow and calculations; no duplicated formula owners or misleading status | Trace each supported workflow through its owner; focused regressions and existing independent benchmarks |
| Intake and results | Consistent structured errors, explicit units/bases, finite reproducible output | Invalid and valid caller journeys, status and serialization evidence |
| Examples and documentation | One recommended entry path; executable recipes for every promoted workflow | Source and installed-wheel replay, documentation build |
| Packaging and interoperability | Clean installation and usable Python/CLI/HTTP boundaries | Installed-wheel and maintained transport journeys |
| Performance and maintainability | Remove confirmed duplication or measured bottlenecks affecting callers | Before/after evidence where a performance claim is made |

Completion requires evidence for the whole table. A facade cleanup or green
test suite alone is insufficient. Existing supported engineering scope is the
starting boundary; adding unsupported structural systems or publishing a new
release is a separate decision.

## Completed implementation batches

- Baseline: `244a2dae76b253e6c8abd99e5af5329d5b1e0bef`.
- Confirmed: nine family builders expose `Any` groups, ten family modules have
  undocumented operations, and the API-level guide still recommends a different
  namespace from the package README. Slab routes lack equivalent typed builders.
- Batch 1 implemented: typed group imports for all family facades, three slab
  builders, specific calculation result types, complete operation documentation,
  a typed beam/column/slab example, and a purpose-based API chooser. Engineering
  formulas and wire schemas remain unchanged.
- Verification: 70 focused tests pass; 15 implementation/example files pass
  type checking; the strict documentation build passes and rendered family API
  content was inspected. All 13 family recipes and the new typed example pass
  from the built wheel with installed origin verified. Eight additional
  advertised examples execute successfully in isolated scratch directories.
- Remaining canonical operation documentation debt is zero in the generated
  classification. Batch 1 merged as PR #1006 after required validation passed.
- Batch 2 addresses implementation behavior: optional DXF/report imports no
  longer run during calculation or CLI discovery startup. Output functions and
  their missing-dependency behavior retain their existing owners.
- Local timing: seven fresh interpreter processes per entry point on this Mac,
  same Python environment and warmed filesystem. Median package import dropped
  from 588.2 ms to 462.0 ms (21.4%); column import dropped from 576.6 ms to
  460.2 ms (20.2%). These are startup measurements, not calculation-throughput
  or cold-machine claims. The regression checks assert dependency isolation,
  rather than a timing threshold that varies by machine.
- A concrete data-loss defect was reproduced in the Excel bridge's JSON
  round-trip: exported `D=550, d=492, cover=40` reloaded with `d=510`. The
  exporter now includes the loader's explicit `eff_d` field and retains `d`
  for existing JSON consumers. Legacy lowercase overall-depth input remains
  supported. The file round-trip regression uses a supplied depth that differs
  from the default and compares the complete restored record.
- Batch 2 verification: 272 focused import/API compatibility, CLI, Excel bridge,
  DXF, and report checks pass; the three changed library modules pass type
  checking. Regenerated API inventories have no changes. PR #1007 merged after
  required hosted checks passed.
- Clean-install replay at `eae98738`: a fresh virtual environment containing only
  the wheel and declared Pydantic dependencies runs all 13 positive/negative
  family recipes and the typed workflow example. Imported origin was inside
  that environment; NumPy, ezdxf, Jinja2, and pytest were absent.
- Batch 3 fixes an outcome-changing JSON intake defect: duplicate `vu_kn`
  members silently discarded the first action. A request containing 500 kN
  followed by 75 kN returned PASS even though 500 kN alone fails. One common
  JSON boundary now rejects duplicates with the complete field path, rejects
  non-finite numbers, and exposes syntax/encoding failures as library issues.
- Every supported family has a typed JSON loader, including slab variants and
  supplied beam checks. The canonical CLI and V2 HTTP beam route use the same
  ambiguity check. Cookbooks and the typed example show direct JSON loading.
- Final verification reason: this batch changes the shared input boundary and
  public loader inventory across all supported families. After content freezes,
  run one cumulative Python suite (including the maintained independent family
  benchmarks), strict docs, and installed Python/CLI/API replay. Do not repeat
  those gates for documentation-only evidence updates; repair only affected
  evidence if a confirmed failure changes the candidate.

## Cumulative family and transport evidence

The family JSON batch merged as PR #1008 and the physical composition batch as
PR #1009 after their required hosted checks passed. The table below records
the cumulative family/transport baseline; the later sections record the
affected evidence for physical composition and the final caller batch. Exact
candidate, hosted-run and merge identities remain in GitHub.

| Outcome | Verified evidence |
|---|---|
| Public API and signatures | Typed groups/results across 11 family modules; 14 typed JSON loaders; 15 changed implementation/example files pass mypy; canonical documentation debt is zero |
| Calculation and result flow | Runtime traces of all 13 family journeys reach their registered calculation owners and preserve expected PASS/FAIL/HOLD states; the cumulative Python suite includes existing independent arithmetic, golden-vector, physical-beam, and workflow regressions |
| Intake and errors | JSON request round-trips preserve all 13 request models plus supplied beam bar arrays; duplicate actions, non-finite values, syntax and encoding failures produce structured issues; CLI and HTTP reject ambiguous action values |
| Examples and reference | All 11 advertised examples execute against the installed wheel with only declared dependencies; all 13 family recipes pass; strict documentation build succeeds and rendered JSON-loader references were inspected |
| Packaging and transports | Fresh virtual environment, installed origin verified, no NumPy/ezdxf/Jinja2/pytest; installed CLI PASS, FAIL, and rejected-input cases pass; V1 preserves engineering FAIL and V2 exactly matches Python while rejecting duplicate JSON |
| Performance and maintenance | Measured import improvement and the lossless Excel-bridge JSON fix are integrated in PR #1007; JSON parsing has one shared owner across the family loaders, canonical CLI, and V2 ambiguity check |

Cumulative command:
`./run.sh test --python -q -m 'not slow and not performance' --disable-warnings --durations=5`.
Result: 8,002 passed and 4 skipped. Slow/performance tests were excluded; this is
software evidence for the supported library scope, not installed Windows-host
acceptance. The affected HTTP checks pass (10 tests), and changed-path formatting
and generated API/cookbook checks pass.

The verified wheel has SHA-256
`1f08ab62d54bb36b792de5afaa738109650b5367e3d6e0a66e8dff2b8dcf9af7`.
It is a local source build; no package publication or release was performed.

## Physical-member composition batch

The family JSON batch merged as PR #1008. The next batch addresses a confirmed
composition obstacle in the promoted physical-beam API: operation results have
JSON-shaped outputs, while downstream requests need nested dataclasses and
enums. Passing AO18's output directly to AO19 raises an `AttributeError`; each
caller otherwise rebuilds the record tree and evidence fields manually.

- Add `OperationResult.output_as` to recover typed output records while checking
  canonical payload equality. Preserve existing serialized output and states.
- Add `MemberLeafEvidence.from_result` to copy genuine result identities,
  provenance, diagnostics and states into a profile-derived leaf.
- Provide one executable physical-bar → member → BBS → quantity → cost → package
  example and update the existing guides. Its teaching profile is explicitly
  limited to geometry, positive flexure and ordinary seismic applicability;
  it must not be represented as a complete building-design profile. The native
  WP11 automatic ETABS baseline is .NET-only and is not part of this Python API.
- Accept only after the installed wheel runs the entire example and preserves
  missing/stale evidence as partial/draft, with no invented human approval.
  Check affected WP01-WP08 result consumers, the typed caller, and strict docs.
  The unchanged cumulative suite above does not need another run.

Verification: 67 focused WP01/WP06/WP07/WP08 checks passed; the two changed
library modules and the example pass mypy. Changed-path formatting, generated
API inventories (no inventory changes), and strict documentation build passed.
The complete example runs in isolated Python mode from a fresh wheel-only
environment with declared dependencies, with NumPy, ezdxf, Jinja2 and pytest
absent. It reports 59.187606 kg steel, 0.9 m³ concrete, 7.8 m² formwork, a
complete teaching-profile member, a partial missing-leaf member, and a stale
draft package without human approval. Wheel SHA-256:
`64190f506ff231f5958170f993c3c567c8d11a3a65bdd04451787e890e185000`.

## Candidate evidence and remaining caller recipes

The final batch closes the remaining Python caller categories and fixes an
outcome-changing implementation defect found while constructing the real chain:

- `candidate_result_binding` accepted a detached quantity payload while keeping
  the original operation's result identity. Replacing a candidate's calculated
  steel mass with 1 kg changed the selected optimum. It now requires canonical
  equality with an actual output of that operation and rejects a mismatch.
- `bind_candidate_evaluation` composes typed member, quantity and optional cost
  results without rebuilding nested records. The ranker retains its existing
  identity, profile, freshness, completeness and coupling qualification rules.
- `candidate_ranking_workflow.py` calculates all three physical arrangements,
  including four longitudinal bars and 40 actual link paths. The 12 mm case
  fails; 20 mm and 25 mm pass the declared teaching profile. The eligible
  20 mm case has 80.345690 kg steel versus 113.638719 kg for 25 mm. A budget
  stop or stale selected member prevents a selection and optimum claim.
- `beam_checks_workflow.py` runs 21 explicit WP02–WP05 operations, including
  topology, analysis, real action-row normalization, capacity, serviceability,
  anchorage, a lap and reinforcement arrangement. Missing load history, strain
  or seismic context remains unevaluated. The successful elastic analysis is
  also unevaluated as an engineering check. Service components and strain are
  declared teaching inputs, not inferred from that analysis.
- `analysis_snapshot_replay.py` validates portable WP10 JSON and a canonical
  round-trip. It runs offline with the synthetic fixture or a supplied file;
  a changed evidence hash is rejected without exposing an accepted snapshot.
  The native ETABS acquisition/normalization route remains distinct.
- The API chooser and existing references link these executable callers and
  use the actual public construction, reporting, optimization and snapshot
  namespaces.

Verification: 21 focused WP08 checks and three executable-caller integration
checks pass. Six affected library/example files pass mypy. The five
current-source examples and all 13 positive/negative family recipes run from a
fresh installed wheel, with the package origin verified and NumPy, ezdxf,
Jinja2 and pytest absent. The final local wheel SHA-256 is
`b352f150c235af7d23b156e7c569b06b84e077b6506e55a221525815f4d22fee`.
The 10 retained compatibility examples were already replayed at the cumulative
baseline; their owners are unchanged by the physical/candidate batches.

## Completion and boundaries

All six acceptance areas have source, caller and installed-package evidence:
typed APIs and discoverable signatures, registered calculation-owner traces,
structured intake and explicit result states, executable recipes across the
promoted Python workflow categories, clean installation and transport replay,
and measured startup improvement. The final source candidate also passes
changed-path formatting, generated API checks and the strict documentation
build. Required hosted checks apply to the reviewed candidate before merge.

The cumulative 8,002-test run is retained as the shared-boundary baseline;
only affected physical/candidate behavior was retested afterwards. The final
batch changes no family arithmetic or CLI/HTTP owner. Several cohesive commits
share one PR and one required hosted-check cycle per integrated batch.

This completed the bounded caller-usability milestone. Teaching profiles
do not establish complete-building design or construction approval. Public
package publication, installed Windows Excel/ETABS qualification, native-only
WP11 baseline design and new structural-system scope remain separate work.

## Function review: LIB-DEEP-REVIEW-001

**Date:** 27 September 2026. **Starting source:** `3580a8ed` (after PR #1011).
**Scope:** ordinary rectangular-beam request → strength → generated detailing
→ BBS, including retained serialized and pipeline callers. The work includes
reading function bodies and their consuming branches, resolving signatures,
reproducing outcome-changing faults, and comparing relevant library contracts.
The generated [function inventory](../reference/api-classification.json) is a
discovery index; presence in that inventory is not evidence of a source review.

### Public functions inspected

The facade is [design/is456/beam.py](../../Python/structural_lib/design/is456/beam.py).
Its operation owner is
[services/canonical_beam.py](../../Python/structural_lib/services/canonical_beam.py).
Exact current signatures are generated in the [beam reference](../reference/beam-facade.md).
The table distinguishes a full inspected caller path from a boundary-only read.

| Function | Body, signature and options assessment | Decision / evidence |
|---|---|---|
| `input` | Keyword-only, unit-bearing scalar builder delegates to the strict nested request; both effective-depth variants and both shear-steel options traced | Fix contradictory shear-steel descriptions. Retain the compatible scalar signature; grouped callers can already construct `BeamDesignInputV1` with exported identity/section/material/action/basis types |
| `load` | Mapping or typed request → the same model; translated error paths traced | Retain; correct the docstring's obsolete `Any` parameter description |
| `load_json` | Shared duplicate-preserving decoder → mapping validation; finite values, UTF-8 and error paths read | Retain one decoder; existing duplicate-action/CLI evidence applies |
| `design` | Request → effective depth, separate transverse grade, optional service/torsion adapters → compliance owner → typed envelope | Retain calculation ownership; contradictory shear basis now fails at intake before calculation |
| `check` | Direct alias to required-design evaluation | Retain and explicitly distinguish it from supplied-bar acceptance; it does not check an installed arrangement |
| `detail` | Flexural areas drive generated bars; depth, stirrup area and spacing previously checked, longitudinal shear basis omitted | Repair the shared basis check. Make repeated `detailing_standard` optional because the request already requires that explicit choice |
| `design_and_detail` | Sequential composition; aggregate result requires both stages to pass | Same optional keyword; no accepted joint result when generated tension steel cannot support the shear basis |
| `bbs` | Delegates to `generate_bbs`; all supplied results admitted before generation; rejected design/detailing cannot become an artifact | Retain; positive repaired journey yields nine items. This pass reads admission/aggregation, not every cutting-length formula |
| `load_supplied_check` | Mapping/type boundary inspected | Retain; correct obsolete `Any` documentation. Full V2 contract/engineering review remains a separate packet |
| `load_supplied_check_json` | Same shared JSON decoder and V2 model | Retain; no second parser |
| `check_supplied` | Type guard → `check_supplied_beam_v2`; actual bar area and transverse grade reach shear evaluation, support evidence controls HOLD | Boundary and shear flow read. The complete longitudinal evaluator, anchorage and V2 field model are not claimed deeply reviewed here |

### Calculation and downstream owners inspected

The following are source-level findings, not conclusions inferred from a test
count. Unchanged formulas retain their existing code/source qualification.

| Function / owner | What was read or compared | Outcome |
|---|---|---|
| `BeamDesignInputV1.validate_calculation_depth_relation` | Resolved depth vs compression depth and supplied shear basis | Reuse one consistency predicate for percentage/area, including requests loaded from mappings/JSON |
| `_design_beam_is456_calculation` in [beam_api.py](../../Python/structural_lib/services/beam_api.py) | Unit/depth resolution, material domain, delegated parameters and persisted `design_inputs` | Original optional shear inputs survive; consume them downstream rather than replacing them with flexure demand |
| `check_compliance_case` in [compliance.py](../../Python/structural_lib/codes/is456/compliance.py) | Required flexure, percentage precedence, Table 19 input, transverse grade, combined status/utilization | Reject conflicting percentage/area in retained callers too; consistent dual descriptions remain valid |
| `calculate_mu_lim` in [beam/flexure.py](../../Python/structural_lib/codes/is456/beam/flexure.py) | Neutral-axis limit, stress-block coefficients, N·mm → kN·m conversion | Retain; limiting depth used to bracket the independent numerical comparison |
| `calculate_ast_required` | Capacity sentinel, magnitude convention and delegated physical root | 36 cases compared with SciPy's independent root solver; retain |
| `calculate_ast_from_rectangular_stress_block` in [common/stress_blocks.py](../../Python/structural_lib/codes/is456/common/stress_blocks.py) | Discriminant, smaller root, equilibrium area and units | Same 36-case numerical comparison; no iterative-solver dependency added |
| `design_singly_reinforced` | Minimum/maximum steel, calculated neutral axis and structured unsafe result | Retain; existing independent/golden cases cover the maintained branch |
| `design_doubly_reinforced` | Singly/doubly dispatch, compression strain/stress, lever arm, steel limits and unsafe branches | Body read and existing golden case retained; this is not a fresh qualification of every material/strain interpretation |
| `get_xu_max_d`, `get_steel_stress` in [materials.py](../../Python/structural_lib/codes/is456/materials.py) | Grade-specific neutral-axis ratios and Fe415/Fe500 interpolation used by flexure | Retain; no material model rewritten |
| `calculate_tv`, `design_shear` in [beam/shear.py](../../Python/structural_lib/codes/is456/beam/shear.py) | kN conversion, Table 19/20 domains, 415 N/mm² stirrup design cap, strength/minimum/max-spacing bounds | Retain arithmetic; independent interpolation and spacing calculation added for the reproduced failure |
| `get_tc_value`, `_get_tc_for_grade`, `get_tc_max_value` in [tables.py](../../Python/structural_lib/codes/is456/tables.py) | Percentage interpolation, grade-column selection and concrete stress limit | The calculation correctly depends on longitudinal steel; the defect was losing that dependency during detailing |
| `round_to_practical_spacing` | Supported spacing list and conservative selection; `design_shear` rejects unsupported sub-75 mm spacing | Retain; do not add numerical tolerances or arbitrary spacing options to this bounded route |
| `select_bar_arrangement`, `create_beam_detailing` in [beam/detailing.py](../../Python/structural_lib/codes/is456/beam/detailing.py) | Preferred diameter search, layer/count selection, display-area rounding, physical tension face and three zones | Use count × π × diameter² / 4 when checking actual area, rather than the rounded display area |
| `_require_generated_detailing_depth`, `_require_generated_detailing_shear` in [beam_detailing_binding.py](../../Python/structural_lib/services/beam_detailing_binding.py) | Actual geometry vs strength basis, including TOP and BOTTOM tension faces | Add missing longitudinal-area comparison to the existing shared guard; retain separate geometry and stirrup checks |
| `detail`, `compute_detailing`, `_design_and_detail_beam_is456_calculation`, `design_single_beam` | All four callers of that shared guard, including JSON reload and optional pipeline drafting | Each supplies its actual consumed basis; pipeline guard stays outside the optional drafting exception handler |
| `_accepted_detailing`, `generate_bbs` | Source status, empty/mixed input rejection and all-or-nothing admission | Unchanged; repaired producers cannot pass an unsupported reinforcement arrangement into BBS |
| `check_supplied_beam_v2`, `_evaluate_shear` in [supplied_beam_check.py](../../Python/structural_lib/services/supplied_beam_check.py) | Supplied tension area, stirrup capacity and spacing checked against the same request | Separate supplied-steel journey already consumes actual area; no inferred equivalence with generated detailing |

### Confirmed failure, cause and repair

The original valid public request used b = 300 mm, D = 500 mm, d = 442 mm,
M25, Fe500, Mu = 100 kN·m, Vu = 180 kN, two-legged 8 mm links and a caller
shear basis `pt_percent=3.0`. Detailing selected two 20 mm tension bars and
200 mm link spacing. `design_and_detail` returned PASS and `bbs` succeeded.

Actual tension area is 628.318531 mm², so its percentage is 0.473845%, not
3%. The assumed basis permits 275 mm links; the actual bars permit only
125 mm using the maintained Table 19/Cl. 40.4 route. The independent arithmetic
uses M25 table points (0.25%, 0.36 N/mm²) and (0.50%, 0.49 N/mm²), linear
interpolation, `Vus = Vu - tau_c*b*d`, and
`s = 0.87*415*Asv*d/Vus`. Before practical rounding, s lies between 125 and
150 mm. These are the accepted repository source constants; this packet does
not introduce a new standard interpretation.

The prior guard proved only stirrup area/spacing and section depth. It never
compared the generated longitudinal bars with the steel assumed by Table 19.
Its previous regression requests used flexure-derived steel. That is the
specific missed branch; another broad green suite would not explain it.

Now each generated tension face and zone must provide at least the consumed
longitudinal area. Failure raises
`DETAILING_SHEAR_LONGITUDINAL_AREA_MISMATCH` with the exact face/zone and a
repair suggestion. The caller reruns with actual steel (or the existing
flexure-derived basis), then selects spacing within the revised limit. The
library does not silently change reinforcement choices. The coherent two-20 mm,
125 mm-link request succeeds and produces its nine-item schedule.

A second reproduced conflict supplied both 3% and 628.318531 mm². The old
code ignored the area and retained the 275 mm limit; area alone yielded
125 mm. One shared predicate now rejects inconsistent descriptions. Matching
dual inputs remain accepted within relative 1e-9 / absolute 1e-6 mm² tolerance.
No public parameter was removed.

### Comparison with established libraries

Primary documentation was consulted on 27 September 2026. These are specific
API/algorithm comparisons, not claims that different design standards give
interchangeable design capacities.

| Library and source | Concrete comparison | Decision for this packet |
|---|---|---|
| [concreteproperties: analysis](https://concrete-properties.readthedocs.io/en/stable/user_guide/analysis.html#ultimate-bending-capacity) | `ConcreteSection` carries actual geometry/materials; `ultimate_bending_capacity(theta=0, n=0)` returns `UltimateBendingResults`. Nominal analysis is distinguished from design-code factors | Keep typed request/results and bind downstream checks to actual generated bars. Preserve the distinction between required design and supplied reinforcement |
| [StructuralCodes: section calculator](https://fib-international.github.io/structuralcodes/api/sections/section_calculator.html) | `calculate_bending_strength(theta=0, n=0, max_iter=100, tol=0.01)` names numerical controls and returns a result object | Document option meaning and input context. Our closed-form rectangular design needs no artificial iteration options. Further nonlinear/physical-section comparisons remain open |
| [SciPy: brentq](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html) | Bracket, absolute/relative tolerance and returned convergence evidence are explicit | Use an independent numerical solver to check the existing closed-form calculation, without adding SciPy as a runtime dependency |

The numerical comparison actually ran with installed **SciPy 1.17.1**, rather
than inferring agreement from documentation. It solved
`0.36*fck*b*x*(d - 0.42*x) - Mu*1e6 = 0` for x, then obtained
`Ast = 0.36*fck*b*x/(0.87*fy)`. The 36 vectors combine `(b,d,fck)` =
`(230,450,20)`, `(300,442,25)`, `(350,600,35)`, fy = 415/500, and moment
fractions 0, 0.01, 0.25, 0.5, 0.9, 0.99 of the limiting moment. Brackets are
0 to 0.48d/0.46d respectively; `xtol=1e-10`, `rtol=1e-12` and convergence
was checked. Maximum absolute area difference was **5.55e-11 mm²**, against
an acceptance tolerance of 1e-7 mm². This checks two algorithms for the same
equilibrium equation; it does not independently validate IS 456 coefficients,
minimum steel, doubly reinforced sections or whole-member acceptance.

The simpler caller is now `beam.design_and_detail(request)`. Its request still
requires a selected detailing standard; an optional explicit keyword remains
a checked assertion. Updated examples and generated references show the actual
signature and explain the shear options. No runtime dependency, package release
or calculation-speed claim is introduced.

### Verification and remaining review

The focused implementation checks cover wrong longitudinal basis via percentage
and area, both physical tension faces, JSON reload, the pipeline, conflicting
versus matching inputs, revised spacing, and BBS output. Existing depth,
stirrup, FAIL/HOLD and compatibility checks remain in the affected evidence.
Final command results are recorded with this packet's PR.

Local results: **155 focused checks passed** across the changed regressions,
canonical facade, compliance validation, existing depth/golden/supplied-bar/
torsion/pipeline checks and canonical HTTP V2 route. The nine changed
library/example files pass mypy; affected Ruff/Black, generated API/reference,
session-reader and strict MkDocs checks pass. The essential changed-area run
passed 11 checks and identified the expected changed OpenAPI field description;
the snapshot was regenerated and that remaining check passed. No arithmetic or
wire field was changed by the snapshot update.

A fresh isolated environment with the local wheel and its declared dependencies
runs `canonical_workflows.py`: beam BBS 145.98 kg, column/slab PASS, review still
required, and invalid width rejected. Installed origin and both new optional
signatures were verified. Wheel SHA-256:
`f6a5065d50343db658620376204d60d69414a2781d48becde007e9f8bd275277`.
This is local installation evidence, not a published release.

**Still open:** a function-by-function engineering review of supplied-bar
anchorage and serviceability, the physical beam numerical owners, and the
remaining column/slab/wall/stair/footing families. Their earlier usable API and
caller evidence is not substituted for this review. Continue in bounded family
batches with the same table: exact function, body/owner read, signature/options,
reproducer or independent benchmark, decision, change and verified outcome.
Prioritize consequential calculation/data-flow defects over cosmetic rewrites;
measure a representative batch before changing performance-sensitive code.

## Function review: LIB-DEEP-REVIEW-002

**Date:** 27 September 2026. **Starting source:** `3aae2c0e` (PR #1012).
**Scope:** supplied rectangular-beam contracts, longitudinal-layer evaluation,
support anchorage, and the canonical span/depth and Annex F serviceability path.

### Calculation change intake

The controlled source is IS 456:2000 through Amendment 5, SHA-256
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
Printed pages 43, 44 and 47 (PDF pages 44, 45 and 48) were read and visually
checked locally. Only normalized values, clause identifiers and derived
benchmarks belong in this record; protected text and page images stay private.

| Confirmed outcome to repair | Source / independent target | Public consumers and acceptance |
|---|---|---|
| Supplied compression bars can pass above the maximum area; the shared evaluator checks only the lower demand | Cl 26.5.1.1(b)/26.5.1.2: each longitudinal group is limited to `0.04*b*D`. A 500 × 500 mm section has a 10,000 mm² limit; eight 40 mm bars provide 10,053.096491 mm² | Shared evaluator, canonical supplied check, and gravity caller must report the excessive group and its limit; adequate existing cases retain PASS |
| M45/M50 bond values exceed the source's M40-and-above row | Cl 26.2.1.1: 1.9 N/mm² for plain tension bars, 3.04 N/mm² for deformed bars. For 20 mm Fe500, `Ld=20*0.87*500/(4*3.04)=715.4605263157895 mm`; 680 mm is insufficient | Fix the shared lookup so exact anchorage and all development-length consumers use the same source value; retain public signatures and grade keys |
| Simple-support acceptance consumes rounded Ld | Cl 26.2.1: 8 mm Fe415/M25 requires 322.36607142857144 mm; a straight 322 mm length must fail | Reuse the existing unrounded compliance owner; display/scheduling rounding remains separate |
| The documented zero-enhancement support check rejects an otherwise accepted zero-shear action | The implemented conservative check compares full Ld with its support allowance and performs no division by shear | Admit zero shear without an automatic PASS; sufficient and insufficient anchorage must still be distinguished |

Area benchmark tolerance is 1e-6 mm²; development-length arithmetic tolerance
is 1e-9 mm. The code limit itself is not relaxed by those test tolerances.
No new bending, bond, strain or support model is inferred. Full bend geometry,
M1/V credit, negative-moment curtailment, lap qualification, service-load
analysis, Level B/C deflection and the physical-member numerical owners remain
outside this packet. Missing support evidence retains the documented HOLD
policy, with individual completed checks still visible.

### Function bodies, signatures and options inspected

| Function / owner | What was read and traced | Decision |
|---|---|---|
| `BeamBarLayersV2.validate_layers`, `count`, `area_provided_mm2`, `to_service` | Immutable layer arrays, exact circular area, one spacing per layer gap and conversion to the service carrier | Retain exact geometry; no new area override |
| `BeamSuppliedCheckSectionV2.validate_depth_basis` / `resolve_effective_depth` | Exactly one explicit depth or complete depth basis, shared resolver and section proportions | Retain; compare the result with the actual weighted bar centroid downstream |
| `BeamSuppliedReinforcementV2.asv_mm2` / `to_service` | Separate transverse diameter/legs/spacing and declared bend flags; no generated replacement bars | Retain; flags declare bends, not verified bend geometry |
| `BeamReinforcementSelectionV2.to_service` and `BeamSuppliedCheckRequestV2.validate_consumability` | Permitted diameters, layer limits, depth-basis consistency; selection objective is for the preliminary recommendation | Retain the explicit selection object and compatibility; no new options are needed for the fixes |
| `check_supplied_beam_v2` / `_evaluate_shear` | Actual tension area feeds Table 19; actual stirrup area, spacing and grade feed capacity; longitudinal/shear outcomes form the envelope | Retain the existing HOLD policy for missing support evidence. Fixes belong in shared owners and must reach this aggregate |
| `LongitudinalBarLayersV1`, `BeamReinforcementSelectionConstraintsV1`, `SuppliedBeamReinforcementV1` | Immutable dataclass validation, permitted diameter ordering and source references | Retain existing V1 signatures and V2 translation |
| `_recommendation`, `_spacing_checks` | Recommendation remains separate from supplied evidence; actual horizontal/vertical clearances use declared bars and aggregate size | Retain; no speculative optimizer rewrite or speed claim |
| `_layer_centres_from_face_mm`, `_weighted_centroid_from_face_mm`, `_layer_centroid_from_face_mm` | Each layer's physical centre and count-weighted centroid; independent design-depth comparison | Retain; exact physical dimensions are already consumed |
| `evaluate_supplied_beam_reinforcement_v1` | Full body, every area/spacing/depth/support branch and resulting issue/status payload | Add maximum-area checks for both groups, including compression/hanger steel when required Asc is zero |
| `_maximum_longitudinal_area_mm2`, `design_singly_reinforced`, `design_doubly_reinforced` | Extract the existing rectangular maximum-area formula into one pure owner consumed by required-design and supplied-bar checks | Same `0.04*b*D` calculation; no design formula or public signature change |
| `get_bond_stress` | Entire lookup, grade selection, normalized table and plain/deformed factor; source row visually verified | Correct M45/M50 to the M40-and-above value; preserve exported dictionary keys |
| `calculate_development_length_unrounded`, `calculate_development_length`, `evaluate_tension_bar_anchorage_v1` | Exact formula, scheduling rounding and straight-plus-bend equivalent value | Retain separation; corrected shared bond source reaches all three |
| `check_anchorage_at_simple_support` and `beam_api` wrapper | Entire support calculation, zero M1/V assumption, rounding, zero shear and public aliases/defaults | Use exact Ld; accept zero shear while checking full anchorage; correct examples and explain the actual conservative allowance |
| `BeamServiceabilityChecksV1` and its basis/span-depth/crack models | Separate service case, explicit factors and mean surface strain, references/hash, exposure limit and geometric domain | Retain explicit service-analysis ownership; do not infer SLS from ULS actions |
| `BeamDesignInputV1.hold_unfrozen_serviceability`, `canonical_beam.design` service branch | Section/station/material consistency, elastic-strain ceiling, typed mapping into both pure checks | Retain; opaque/partial input stays rejected and generated-bar detailing cannot inherit unrelated SLS evidence |
| `check_deflection_span_depth`, `check_crack_width` | Full Level A bodies, assumptions, formula, defaults, result and pass/fail calculation | Canonical typed caller supplies the required controls. Retain formulas; run independent decimal arithmetic below. Legacy direct-helper defaults are not the canonical service contract |
| `gravity_workflow.run_gravity_workflow_v1` reinforcement branch | Shared evaluator call and reinforcement-result envelope propagation | New excessive-steel failure must reach the real component result; other gravity calculations were not re-reviewed |
| `beam_audit` service-result branches / `derive_overall_status` | Explicit SLS result, service-case identity, provenance and incomplete-evidence aggregation | Retain; status precedence is an existing contract, not a new defect finding |

### Reproducers and impact

Before this packet, a valid 500 × 500 mm V2 request with four 20 mm tension bars,
two layers of four 40 mm compression bars (80 mm vertical centre spacing),
M25/Fe500, 100 kNm, 60 kN and complete support evidence returned **PASS**. The
compression group exceeds its 10,000 mm² maximum. It now returns **FAIL**, with
`BEAM_COMPRESSION_REINFORCEMENT_AREA_EXCESSIVE` in the canonical envelope.
Both area payloads expose `maximum_mm2` and `is_within_maximum`; `is_adequate`
requires both lower and upper limits. The same shared fix reaches gravity
component checks. Missing support evidence still produces the documented HOLD.

For 20 mm Fe500 deformed bars with 680 mm straight anchorage, the old M45/M50
lookup returned **679.6875 / 647.321429 mm** required length and accepted both.
The controlled source requires **715.460526 mm** for either grade; both now
fail with a **35.460526 mm** shortfall. The correction also reaches existing
footing/load-transfer and detailing consumers of the shared bond lookup.
Their use of this owner is covered by focused regression checks, without
claiming a new full review of those element families. The canonical V2 beam
material contract remains M20–M40; the higher-grade correction is exercised
through the expert anchorage APIs, not by widening the canonical domain.

The support check previously accepted 322 mm when the exact required length
was 322.366071 mm. It now fails. Its zero-shear branch previously returned an
input failure with zero required length; it now performs the same conservative
full-length check as a positive-shear case. Public call signatures remain intact.

### Comparison with established library interfaces

| Primary reference checked on 27 September 2026 | Comparison | Consequence here |
|---|---|---|
| [concreteproperties cracked/service stress APIs](https://concrete-properties.readthedocs.io/en/stable/user_guide/analysis.html#stress-analysis) | `calculate_cracked_stress(cracked_results, n, m)` consumes section analysis; `calculate_service_stress(moment_curvature_results, m, kappa=None)` consumes a moment-curvature result | Keep service-analysis and strength inputs separate. Our canonical service check consumes externally established mean strain and modifiers; it is not a replacement section-analysis engine |
| [StructuralCodes EC2 crack functions](https://fib-international.github.io/structuralcodes/api/codes/ec2_2004/cracks.html#calculated-crack-width) | `wk(sr_max, eps_sm_eps_cm)` separates spacing and mean-strain difference; exposure/load-combination limits are separate functions | Preserve explicit geometry/strain/limit inputs and returned evidence. EC2 and IS 456 numerical formulas are not interchangeable |

These are API/documentation comparisons, not executed cross-code benchmarks or
proof of engineering equivalence. No additional runtime dependency is introduced.

### Independent arithmetic and verification scope

An **81-vector** run used Python's `decimal` at 50-digit precision through
`beam.load` → `beam.check`, with separate expected arithmetic. It combines:

- cantilever/simply-supported/continuous bases 7/20/26;
- tension modification factors 0.5/1.0/1.2, compression factor 1.1;
- `acr=40/60/90 mm` and mean strain `0/0.0005/0.001`;
- `L=5000, d=500, h=550, x=150, cmin=40 mm`, with a 0.2 mm crack limit.

The independently rearranged crack expression was
`3*acr*epsilon_m*(h-x)/((h-x)+2*(acr-cmin))`; the L/d limit was
`base*mf_tension*1.1`. Numeric values and both PASS/FAIL results were compared.
Maximum crack-width error was **2.78e-17 mm** and maximum L/d-limit error
**3.55e-15**, against a 1e-12 arithmetic tolerance. This tests the existing
bounded formulas, not the derivation of service strain, Fig 4/5 factors, or
the correctness of a caller's source analysis.

Implementation regressions cover both maximum-area groups, a passing normal
arrangement, source bond values, the unrounded support decision, zero shear,
canonical FAIL propagation and the gravity consumer. The affected evidence
also includes serviceability, public wrappers, generated detailing, footing
load transfer and shared-owner consumers. Exact command results and required
hosted checks belong in this packet's PR; no broad local suite is mandated.

**Next deep review:** physical beam section/strain and reinforcement-layout
owners, complete support/bend-fit and member/profile composition, followed by
Level B/C serviceability and the remaining element families. This packet does
not turn the simplified support-width screen into a complete anchorage or
construction-acceptance model.

## Function review: LIB-DEEP-REVIEW-003

**Scope and intake (2026-09-27, LIB-DEEP-REVIEW-003).** Correct three reproduced
main-process decisions in the physical WP01/WP05 Python operations and their
maintained C# counterparts. The public request signatures, explicit mm/mm²/kNm
units, operation IDs and independent result states remain compatible.

| Calculation owner | Confirmed cause and independent expected outcome |
|---|---|
| `beam.flexure.check_flexure` / `BeamOperations.CheckFlexure` | The check sums tension and compression steel before applying `0.04*b*D`. IS 456:2000 clauses 26.5.1.1(b) and 26.5.1.2 apply this limit separately. In a 500 × 500 mm section, seven 32 mm bars per face give 5,629.734035 mm² per group, each below 10,000 mm²; ±200 kNm demand must not fail the maximum-area criterion. |
| `beam.reinforcement.evaluate_geometry` / `ReinforcementOperations.EvaluateGeometry` | Pair checking skips different face labels. Two 20 mm bars at (150,245) and (150,255) mm have −10 mm clear spacing regardless of their top/bottom labels; the operation must FAIL. |
| `beam.detailing.check_reinforcement_arrangement` / `Detailing.CheckReinforcementArrangement` | Enclosure uses only a sharp inner rectangle and ignores the declared link bend. For an 8 mm link at x/y=29 mm with internal radius 16 mm, the inner corner centre is (49,49) mm. A 16 mm bar at (41,41) mm has `16 - sqrt(8²+8²) - 8 = -3.313708499 mm` clearance to the inner bend; it must FAIL. |

The controlled source identity and printed page 47 for both steel limits are
recorded in review 002 above. Circle separation and quarter-circle containment
are independent Euclidean geometry, with no new code-table interpretation.
Steel-limit and link-enclosure comparisons retain the existing 1e-9 mm²/mm
tolerances; the declared uniform gap comparison remains exact. Fixed numerical
benchmarks use explicit absolute tolerances. Enclosure verification includes
all four corners, tangency and a feasible inset, and member aggregation must
retain a real failed arrangement leaf.

Non-goals: new material laws, a general per-bar strain solver, axial/biaxial
interaction, revised flange-width eligibility, seismic/lap design, new UI
wiring, installed Excel/ETABS artifacts or publication of a release. The
existing capacity routine uses area-weighted face centroids, yielded tension
steel and compression stress at one centroid; its numerical comparison must
identify those assumptions rather than imply general strain compatibility.

### Function bodies, signatures and options inspected

| Owner | Read depth and decision |
|---|---|
| `beam.reinforcement._validate_geometry`, `_face_output`, `effective_depth`, `evaluate_geometry` | Read validation, explicit face/layer/coordinate requests, centroid arithmetic and the full pair loop. Keep the declared uniform gap option; remove the face filter from physical pair checks. AO03 still uses a rectangle, not a curved-link fit model. |
| `beam.flexure._depth_from_compression_face`, `_concrete_block`, `_compression_steel`, `flexural_capacity` | Read the complete calculation path, all capacity options, axial exclusion, sagging/hogging flange behavior, stress interpolation caller and 100-step equilibrium solve. Add explicit per-group output names; retain the old output name as an alias and preserve the request constructor. Material/centroid assumptions remain bounded. |
| `beam.flexure.check_flexure` | Read signed-demand intake, both capacity calls, numerical utilization and all reinforcement decisions. Correct the separate group maxima for both moment signs; excessive tension or compression supply still fails. |
| `beam.detailing.check_reinforcement_arrangement` | Read request/role validation, link cover/bend extent, bar enclosure, pair collisions and horizontal/vertical row checks. Add exact circle containment at rounded corners; retain existing gap, obstacle and placement options. Lap/seismic owners and the remainder of obstacle processing are not certified by this read. |
| `beam.detailing.check_anchorage`, `_anchorage_bend_value` | Trace physical support face/centre, path direction, bend credit, unrounded Ld and M1/V + Lo composition. These are declared evidence and path-length checks; they do not prove that a scheduled bend physically fits a support. No anchorage formula change in this packet. |
| `beam.bar_paths._bend_at`, `_resolve_seed` | Read tangent setbacks, corner centres, arc length and adjacent-bend overlap. These resolve path geometry; they do not qualify support reinforcement or source actions. The whole `resolve_bar_paths` validator was not deeply reviewed here. |
| `beam.member._expected_leaves`, `_qualify_leaf`, `design_member` | Trace profile-derived expected leaves, current code-data/state qualification, exact final-depth result IDs and FAIL propagation. Use an actual failed AO26 result in the regression; a complete failed leaf remains a failed member, never an accepted one. The selected test profile is deliberately bounded, not whole-member acceptance evidence. |
| C# `Flexure.Capacity`, `BeamOperations.CheckFlexure`, `ReinforcementOperations.EvaluateGeometry`, `Detailing.CheckReinforcementArrangement` and output records | Inspect corresponding formulas, face filtering, enclosure and typed output consumers; apply the same three corrections and independent expected decisions. Do not change request constructors or claim installed-host qualification. |

The corrected methods carry new method revision IDs; operation IDs and source
revisions remain unchanged. No optional dependency or new facade is introduced.

### Independent arithmetic and established-library comparison

An executed **36-vector** comparison used installed SciPy 1.17.1
[`brentq`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html)
with an independently written force residual and moment calculation, rather
than the library's 100-step bisection. Inputs were `b=300, D=500, d=450,
d'=50 mm`, Fe250, concrete strengths 20/30/40 N/mm², three tension bars of
16/20/25 mm diameter, zero or two same-diameter compression bars, and both
physical bending faces. The reference used elastic-perfectly-plastic Fe250
stress, `0.0035*(1-d'/x)` compression strain, displaced-concrete deduction and
the existing rectangular design block. All cases were below the limiting axis.
Maximum neutral-axis error was **1.28e-13 mm** and moment error **7.68e-13 kNm**,
against explicit 1e-9 absolute tolerances. This checks the bounded calculation,
not all steel grades or a general distributed-strain formulation.

[`concreteproperties.ultimate_bending_capacity(theta=0, n=0)`](https://concrete-properties.readthedocs.io/en/stable/user_guide/analysis.html#ultimate-bending-capacity)
uses declared material stress/strain profiles and equilibrates axial forces;
its general result is code agnostic, without design reduction factors. This
documentation comparison supports keeping our explicit IS 456/profile result
separate from general section analysis. No concreteproperties execution or
numerical equivalence is claimed. Per-bar strain and multilayer compression
need a separate matched-material benchmark before broadening our capacity
claim.

The implementation regressions cover the separate steel maxima, cross-face
gap outcomes, four mirrored link corners, exact corner tangency, an accepted
inset, a smaller bend radius, and actual arrangement-to-member FAIL propagation.
The three misses arose in the calculation owners themselves: face labels were
used to skip physical pairs, a link's straight bounding rectangle stood in for
its curved steel boundary, and two separately limited steel groups were summed.
Python/C# agreement before the fixes could not detect those shared assumptions.

**Next deep review:** matched-material per-bar strain and multilayer section
benchmarks, then support/path-to-arrangement composition and a representative
complete-profile replay. Level B/C serviceability and other element families
remain open. Exact local/hosted verification and delivery belong in the packet
PR; no broad local suite or release is required by this scope.

## Progress assessment and next acceptance milestone

**Assessment and owner-requested handoff — 27 September 2026.** The recent
work is worthwhile because it corrected reproduced engineering decisions and
made existing public workflows easier to call. Reviews 001–003 changed both
false acceptance (insufficient anchorage, excessive steel and physical clashes)
and false rejection (separately permissible tension/compression groups).
The earlier usability milestone delivered typed inputs/results, executable
examples and installed-package replay. These are concrete improvements;
commit counts, documentation volume and passing suites alone are not measures
of engineering completeness.

The review also exposed a process limitation: the same mistaken assumptions
could survive passing tests and matching Python/C# implementations. Source
reads, independent calculations and complete caller paths are therefore the
valuable parts to retain. Further maintenance should address confirmed
blockers rather than create another general cleanup campaign. Keep cohesive
commits, one PR per bounded milestone and affected verification after the batch.

Progress is strongest in **correctness and usability**. Whole-library deep
review, general per-bar strain/multilayer behavior and complete support geometry
remain open. The measured approximately 20% speed gain concerns imports;
representative end-to-end throughput and manual effort have not been measured.
The source improvements have not been published as a new package release.

### Proposed milestone: LIB-MEMBER-WORKFLOW-001

Deliver one representative ordinary rectangular IS 456 beam through the normal
public Python workflow, from explicit source inputs to checked reinforcement,
BBS and report. Select a case within existing supported scope; enumerate its
complete required check profile before implementation. Teaching examples are
starting points for callers, not the acceptance profile. This is a recommended
next packet, not work already started or a release authorization.

| Acceptance area | Required evidence |
|---|---|
| Frozen case | Named section, materials/code revision, units, supports, separate ULS/SLS actions and actual reinforcement; safe retained inputs and expected outcomes |
| Calculation correctness | Independent source-based benchmarks for governing calculations; matched-material per-bar/multilayer comparison wherever the selected case requires it |
| Complete composition | Every required leaf is accounted for; missing or unsupported evidence remains HOLD/unevaluated and cannot be relabelled as acceptance |
| Caller and artifacts | A reproducible public-API journey preserves inputs, geometry, identities and result states through BBS/report; rejected engineering cannot produce an accepted artifact |
| Measured usability | Record environment, complete elapsed time, manual steps and any baseline comparison; do not substitute import timing for workflow speed |
| Delivery | Update the existing evidence record, run the union of affected checks once after content freezes, then use one hosted PR cycle; publication remains separate |

Start by replaying the selected case and identifying the first confirmed gap.
If a required check cannot be completed within the implemented profile, retain
the incomplete result and repair the gap before calling the milestone complete.
Any scope revision must be explicit; removing a governing check merely to
obtain PASS is not acceptance. Avoid expanding simultaneously into new element
families, a general solver, GUI redesign or installed ETABS work. Level B/C
serviceability and the remaining families follow the governing needs and
subsequent agreed packets.

The [next-session brief](next-session-brief.md) owns resumption and device
boundaries; GitHub owns exact PR/check/merge facts. The function tables above
remain the source-review evidence rather than being copied into each handoff.

### LIB-MEMBER-WORKFLOW-001 frozen acceptance case

**Activated 27 September 2026.** The owner selected this packet from the handoff.
Mac source baseline is PR #1015 (`90da5107`); the writer branch is
`codex/lib-member-workflow-001`. The separate solver candidate remains held
and must be rebound before future integration. Windows work remains retained.

The case is an ordinary, non-seismic rectangular beam on two 400 mm bearing
supports, centred at stations 0 and 5000 mm. The concrete member runs from
-200 to 5200 mm; clear support faces are 200 and 4800 mm. It is 300 by 500 mm,
M25, Fe415 deformed longitudinal steel, with 25 mm nominal cover, 20 mm
aggregate, two 20 mm bottom bars at (50,450)/(250,450) mm and two 12 mm top
bars at (50,50)/(250,50) mm. Every longitudinal bar runs continuously from
-175 to 5175 mm. Two-leg 8 mm Fe415 stirrups at 150 mm have explicit bent
centreline paths and end hooks. No lap, cutoff, axial load, torsion, weak-axis
load, support rotation restraint, primary lateral-system role, or special
fire/watertightness criterion is selected. Lateral restraint exists at both
bearings. Mild exposure and the material/mix specification are explicit case
admission conditions, not inferred from a passing flexure calculation.

Separate uniform actions are ULS 12 N/mm and SLS 8 N/mm, including self-weight.
The public beam-line solver supplies the action rows; independent statics must
recover 30/20 kN support reactions and 37.5/25 kNm midspan moments. The selected
serviceability route is IS 456 clause 23.2.1 span/depth screening with a
conservative source-checked factor, plus Annex F crack width using a retained
cracked-section service calculation. It does not claim calculated long-term
deflection, general multilayer strain compatibility, or new installed evidence.

The frozen required profile includes physical geometry/effective depth,
positive flexure and steel limits, shear/minimum links/spacing, concurrent
zero torsion, span/depth serviceability, crack width, anchorage at both ends,
continuous-bar/lap/curtailment evidence, arrangement and link fit, and explicit
ordinary seismic non-applicability. Fixed-case admission also accounts for
durability cover/material, lateral stability, support steel extension and
fraction, link anchorage, and the absence of side-face-steel requirements.
All these conditions remain in the retained inputs and evidence; none may be
removed to obtain PASS. Geometry and identities must survive paths → BBS →
quantities → report. A failed or missing required check must produce a failed
or draft artifact. No human approval is synthesized.

Initial public-call reproductions exposed: AO11 accepted 5 mm embedment by
checking only M1/V+Lo; AO12 held a completely unspliced/uncurtailed member;
AO24 accepted a schedule from a different reinforcement revision. Repair these
owners and their Python/.NET counterparts, then replay this complete case.
Use source clauses 26.2.3.3(a,c), 26.2.2.4, 26.3, 26.4, 26.5, 23.2/23.3,
38/40 and Annex F. Keep protected prose and page images outside Git.

Verification is the union of affected WP02/WP05/WP07, public-workflow and
independent numerical checks, the matching .NET tests, documentation/contract
checks, an installed-current-wheel replay and one required hosted PR cycle.
Measure a fresh-process input-to-artifact run including imports, calculation,
serialization and file writes; report manual inputs and review steps separately.
No broad local suite, package publication, GUI or installed ETABS work is in scope.

### Complete beam implementation and independent evidence

The [standalone public example](../../Python/examples/complete_member_workflow.py)
freezes 11 member leaves and eight actual bar-end anchorage leaves. Every leaf
comes from the public operation and retains its state, inputs and result identity.
The report carries all 19 leaves, physical bars, quantities and the source
assumptions. Geometry → paths → BBS → package preserves the reinforcement and
topology revisions. The optional renderer writes `calculation.json`, `bbs.csv`
and `report.html`; it cannot promote the semantic package's issue state.

| Confirmed main-process defect | Root cause and repair in Python/.NET |
|---|---|
| A bar ending 5 mm inside its support passed AO11. | Only clause 26.2.3.3(c) was enforced. Compare `Ld` against the minimum of `M1/V+Lo` and three times the actual extension required by (a); expose the combined criterion. |
| A member with continuous bars and no laps/cutoffs remained incomplete. | AO12 treated empty detail lists as missing evidence before inspecting actual paths. Admit only full interval coverage with adequate role-specific station steel; retain interior-end holds and steel-deficit failure. |
| Small top hanger bars failed zero-torsion interaction. | AO08 checked opposite-face tension even when its equivalent moment was zero. Clause 41.4.2 activates that check only when `Mt > |Mu|`; both signs and positive opposite demand are retained. |
| A report could issue against another checked reinforcement revision. | AO24 validated payload hashes and downstream revisions without joining schedule revision/topology to the member. Reject either mismatch as `PACKAGE.IDENTITY_CONFLICT`. The workbook sample generator now gives its checked bars and physical detail one revision. |

The maintained owners read and changed are `check_anchorage`,
`check_laps_and_curtailment`, `check_torsion`, and `create_calculation_package`,
with matching .NET owners. The caller also traces topology, beam-line solve,
action normalization, geometry/depth, flexure, shear, serviceability, arrangement,
ordinary seismic applicability, physical path resolution, member aggregation,
BBS and quantities. No second calculation engine was embedded in the example.

Controlled source identity is IS 456 through Amendment 5, reaffirmed 2021,
SHA256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`,
plus Amendment 6:2024,
SHA256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
Visual reads checked Fig 4 (printed page 38), support clauses 26.2.3.3(a,c)
(page 44), ordinary link anchorage 26.2.2.4 and Table 19 (page 73). Other
admission bases are clauses 22.2, 23.3, 26.3–26.5, 38, 40, 41.4.2,
Tables 5/16/20 and Annex F. The normalized constants and source references are
retained; protected text and images remain outside Git.

| Independent calculation | Result and comparison |
|---|---|
| Simply supported uniform-load statics, at every solver station | ULS reactions 30 kN, maximum moment 37.5 kNm; SLS 20 kN and 25 kNm. |
| Single-layer compression steel, equilibrium reduced independently to a quadratic | `x=68.8801197058 mm`, `Mu=94.6603483765 kNm`; matches the declared centroid profile within `1e-10`. Each top bar remains below Fe415's first inelastic strain point, so this case does not depend on an unqualified multilayer average. |
| Separate SciPy bracketed equilibrium using local parabolic concrete stress deducted at top bars | `x=68.7222003519 mm`, `Mu=94.6636711625 kNm`. The library's uniform `0.446 fck` displaced-concrete deduction is conservative by 0.003323 kNm (0.00351%) for this case. |
| Cracked elastic SLS section, `n=Es/Ec=8`, including displaced concrete at compression steel | `x=104.824706682 mm`, `Icr=718835907.155 mm4`, `fs=96.0372986052 N/mm2`; Annex F surface strain without tension-stiffening reduction gives `w=0.127893467743 mm < 0.3 mm`. |
| Clause 23.2.1 screening and Fig 4 | `L/d=11.1111 < 20`, using conservative tension factor 1.0 and no compression enhancement; this is screening, not a displacement calculation. |
| M25 Table 19 interpolation, actual two-leg 8 mm links at 150 mm | `pt=0.465421%`; interpolate `(0.25%,0.36)`–`(0.50%,0.49)`; resistance `172.612678245 kN > 30 kN`. Minimum links and maximum spacing also pass. |
| Development length and support extension | Bottom `Ld=805.915178571 mm`; physical extension 375 mm at both ends; combined equivalent available length 1125 mm. All bottom bars, exceeding the required one-third fraction, continue into each support. |
| Physical path lengths and steel mass | Four 5350 mm longitudinal bars and 35 hooked links, 39 bars in three marks, `56.9522931244 kg`; concrete `0.81 m3`, formwork `7.08 m2` under the named measurement policy. |

For the independent ultimate calculation, let `Ast=200 pi`, `Asc=72 pi`,
`A=0.36*25*300` and `B=Asc*(700-0.446*25)-0.87*415*Ast`.
The positive root of `A*x²+B*x-Asc*700*50=0` gives the profile equilibrium.
The separate SciPy residual replaces the uniform concrete deduction with
`fcc=0.446*fck*(2r-r²)` for `r=0.0035*(1-50/x)/0.002 < 1`; the bracket
is 50–100 mm. This comparison is limited to these actual single-layer bars.

Each link has two 90-degree hooks around top bars larger than the link itself
and 80 mm tangent tails, exceeding `8*8=64 mm`. Five 20 mm centreline-radius
bends join an open seven-vertex fabrication path. The overlapping closure
parts occupy member planes 10 mm apart. Independently summed length is
`2*100+2*442+242+hypot(242,10)+5*20*(pi/2-2)` mm. The JSON retains actual
segments, not an invented welded loop. The report is not a fabrication drawing.

The [workflow tests](../../Python/tests/integration/test_complete_member_workflow.py)
cover the complete journey, each of 19 missing leaves, actual ULS overload,
actual 5 mm embedment failure, independent statics/section/service calculations,
and path-derived quantities. Every missing case remains visible and draft;
both engineering failures export draft CSV/report data. Professional approval
is absent even for the passing case. This is acceptance of one frozen profile,
not whole-library review, a general design facade or release authorization.

#### Validation, installation and complete-process measurement

- 86 affected Python tests passed: WP02, WP05, WP07, the 25 new complete-case
  checks and the maintained beam/candidate callers. The unrelated snapshot
  replay test was deselected.
- .NET SDK 10.0.400 Release build passed with zero warnings/errors. The affected
  WP02/WP05/WP07 and maintained baseline caller classes ran 78 cases: 77 passed,
  one existing external proprietary-snapshot test skipped. This is portable
  Mac evidence; required hosted Windows checks remain owned by the PR.
- Changed-path Python/C# formatting, semantic manifests/code-data/conformance,
  token-efficiency validation and all 12 selected essential check owners passed.
  API classification was checked after staging the two new intended callers,
  as its tracked-caller inventory requires; no generated registry changed.
- Current-source wheel SHA256
  `11d16d60ced8d6d79b464b8aebcfac724b8f74b7d79829a7347c2fa2215ca3bb`
  installed in an isolated temporary environment. The copied standalone example
  ran outside the checkout with `PYTHONPATH` removed and its library import
  resolved to that environment's `site-packages`. All 19 checks qualified;
  39 bars and `56.9522931244 kg` reached `issue_ready`, with approval false.
  The HTML was also inspected in a browser. This local wheel is not a release.

One installed-wheel command, `python complete_member_workflow.py --output-dir
artifacts`, includes fresh process startup, imports, every operation,
serialization and JSON/CSV/HTML writes. Seven consecutive runs on macOS
26.6.2 arm64, Python 3.11.15, with a warmed filesystem measured
**1.0471, 1.0856, 1.2399, 1.2452, 1.1742, 1.3935 and 1.3686 seconds**;
median **1.2399 seconds**. Outputs were 2,744,277-byte JSON, 10,920-byte CSV
and 664,868-byte HTML. SciPy 1.17.1 was used only for the independent comparison,
not by the caller or installed workflow. No equivalent complete earlier case
was available for a speedup comparison.

Manual work is: prepare/review the fixed inputs, admission and SLS source;
invoke one command; inspect the resulting calculations and physical detailing.
There are **zero intermediate values copied manually during execution**.
Human preparation, checking/approval and fabrication drawing production are
outside the timed run and were not assigned an invented duration. A future
case must retain those obligations and its own supported-check profile.

The first hosted run exposed an additional caller of the stricter report
identity join: `SampleWorkbookData.Member` assigned different reinforcement
and detail IDs to its same source bars. Eight Windows workbook tests rejected
the package. A temporary Mac harness linking the actual host-free workbook
sources and existing tests reproduced the failure. The generator now shares
one revision. Its former 200 mm sample embedment also failed the repaired
engineering criterion; the right bearing is now explicitly 800 mm wide, centred
at 6000 mm with its near face at 5600 mm. The unchanged scheduled bar ends at
6000 mm and has 400 mm actual extension; topology and anchorage use the same
face/centre. The 5 mm failure probes remain failures. No acceptance check is
removed or relaxed to preserve the workbook's passing teaching case.
This is a source-level caller correction, not fresh installed Excel evidence.
The unchanged Python artifact/timing evidence remains applicable; only affected
workbook checks, formatting/documentation and required hosted checks rerun.
The linked-source harness then passed all 18 existing workbook engine/reader
tests with no skips; it is an offline portability check and does not emulate
Excel. [PR #1016](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1016)
owns the final hosted Windows result and integration state.

## Bounded parallel work: LIB-SUPPORT-EVIDENCE-001

**30 September 2026 — recommendation and local planning packet.** Keep
Project_Manager completion first in its separate checkout. The replacement
solver is the main product; this library supplies bounded reusable engineering
operations. Start with current-source consumer evidence and a small reuse map.
This contributes to the intake/evidence work proposed in
[draft PR #1019](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1019)
without accepting its 21-package schedule, 168 hours plus 48 reserve, capacity,
reviewer or proposed serviceability expansion.

### Baseline and writer boundary

- GitHub `main`, explicitly fetched on this Mac on 30 September, is
  `96170d81cd94d323b56f0914ed0214d1bff967b8`. The initially clean planning
  checkout was `codex/library-50-day-plan` at `d8ca7ff99491237bbed34c0e5b6900575b5b5bed`,
  matching draft #1019. Accepted beam milestones
  [#1016](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1016)
  and [#1018](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1018)
  remain complete; their engineering work is not reopened.
- This packet uses the new local branch `codex/library-next-evidence-20260930`,
  based on that fetched main. The Mac task is its writer. No source or installed
  evidence ownership is transferred from Windows. The original planning branch
  and held/dirty sibling worktrees are preserved; two historical temporary
  worktree entries remain unavailable and are not treated as clean candidates.
- #1019 edits this same canonical document. Before any later publication,
  explicitly reconcile its final disposition and this appendix against the
  then-current main. Independent checkouts do not remove that overlap.
  Held solver/XLL candidates still need their own replan/rebind; this packet
  does not reactivate them.
- No `.agents/skills` directory exists here. Use the maintained
  [API Discovery skill](../../.github/skills/api-discovery/SKILL.md),
  [documentation rules](../../.github/instructions/docs.instructions.md) and
  [single-writer procedure](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device).
  No push, merge, dependency upgrade, installation, external post or
  installed-application run is selected.

### Revision-specific evidence

| Observation | Meaning for this packet |
|---|---|
| [PR #1017](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1017) is open; [run 36374778128](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/36374778128) succeeded on `2b2fac77dcbb49d54e38fcca1f59df58a0058c47`. | Dependency/code-owner review remains separate. Successful validation is not a predecessor to these source diagnostics. |
| The commit-filtered Actions read returned one run for main `96170d81`: [documentation run 36419537597](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/36419537597), successful. | Documentation passed; current dependency, installed-wheel, CLI and full-stack qualification are not established by that run. |
| Parent intake identified [older weekly run 36371114483](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/36371114483) as failed on `0793a34f`. | This does not establish that current main is broken. Select a maintenance repair only after a current reproducible failure. |

The [family contracts](../reference/api-classification.json) and
[cookbook](../cookbook/python/family-facades.md) retain 13 journey IDs, 25 advanced
exports and zero stable exports. These differ from the cross-standard
capability-family inventory. The existing
[`recipe_specs`/`run_recipes` owner](../../scripts/verify_lib_pro_013_f0_family_artifact.py)
expects two-way slab `FAIL`, stair `HOLD` and 11 other `PASS` results. Preserving
those outcomes is acceptance. Source recipe replay establishes wrapper and
serialization behavior; it is not a new independent engineering benchmark or
qualified review of all helpers.

### Small executable plan

Allow **1–3 focused hours**: intake 15–30 minutes, mapping 30–90 minutes and
verification/closeout 15–60 minutes. This uncalibrated estimate depends mainly
on source/caller ambiguity. It commits no daily capacity, date or reviewer and
yields to Project_Manager. Report any numerical repair's exact owner,
reproducer and proposed scope to the parent before implementation.

| Step | Measurable exit | Actual dependency |
|---|---|---|
| 1. Bind the current baseline. | Exact source, PR states, local writer and artifact limits recorded; completed beam work stays complete. | Clean Git state, repository identity and fresh fetch/readback; complete at intake. |
| 2. Map the two accepted beam journeys. | Source owners, input obligations, retained acceptance and limits in the table below. Full G1 review of advanced exports remains separate. | Existing contracts/worked cases; neither #1017 nor approval of #1019 is required. |
| 3. Replay lightweight source evidence once. | Generated docs match; classification/convergence and selected CLI checks pass; all 13 recipe statuses and invalid-input rejection match their owner. | Existing worktree-bound Python; no new tests, installation, wheel build, host run or broad suite. |
| 4. Return the next boundary. | Planning-only result and any confirmed failure reported to the parent; broader features and artifact qualification remain explicit decisions. | Steps 1–3; optional owner direction handled by the parent. |

| Reusable boundary | Source/caller and retained evidence | Consumer obligation and limit |
|---|---|---|
| Typed beam design and supplied-steel check | [`design.is456.beam`](../../Python/structural_lib/design/is456/beam.py), [facade contract](../reference/beam-facade.md), [supplied-check recipe](../cookbook/python/beam-supplied-check.md). The compatibility `design_beam_is456` signature was checked through API Discovery. | Supply admitted geometry, materials, unit-explicit actions, depth basis, reinforcement and source identity; preserve separate intake/calculation/engineering/review statuses. No project-load generation or professional approval is implied. |
| Single-layer physical member | [`complete_member_workflow.py`](../../Python/examples/complete_member_workflow.py) uses public `structural_lib.beam`, `construction`, `reporting`; [accepted case](#lib-member-workflow-001-frozen-acceptance-case), [workflow checks](../../Python/tests/integration/test_complete_member_workflow.py). | Retain 19 required leaves and 39 bars through BBS/report. Historical centroid-method numbers are superseded by current v3 case/reference values. |
| Multilayer physical member | Same example with `--case multilayer`; [source, independent references and acceptance](multilayer-member-workflow.md). | Retain 27 leaves, 43 bars, signed per-bar equilibrium and draft outcomes for missing/failed evidence. Supplied cracked SLS basis and span/depth screening stay explicit; calculated long-term displacement, general support fit and axial/biaxial sections remain outside this case. |

The full-member example is a frozen worked case, not a general beam input
builder. Source success does not qualify an older published wheel for
later merged changes. Reuse the existing independent references; do not rerun
the already-passed per-bar packet merely for this planning change. No
engineering requirement or tolerance changes.

Focused commands for step 3:

```bash
./scripts/python_runtime.sh scripts/generate_family_facade_docs.py --check
./scripts/python_runtime.sh -m pytest --no-cov -q \
  Python/tests/test_api_classification.py \
  Python/tests/integration/test_family_facade_convergence.py \
  Python/tests/integration/test_cli.py::test_cli_help \
  Python/tests/integration/test_cli.py::test_capabilities_json_matches_python_contract
./scripts/python_runtime.sh -c 'import runpy; checks = runpy.run_path("scripts/verify_lib_pro_013_f0_family_artifact.py"); rows = checks["run_recipes"](); print([(row["journey_id"], row["engineering_status"]) for row in rows])'
./run.sh efficiency check
```

The smallest useful follow-on is exact-artifact consumer qualification with the
existing wheel verifier: identify the candidate/source/hash, replay the recipes
against that artifact, and retain its result and identity. Allow a provisional
**1–3 additional focused hours** if the existing verifier/runtime are usable;
packaging or runtime failures require a fresh bounded estimate. This needs
explicit authorization for an isolated installation, outside this task.
Proposed code scope is currently **none**: no current main-process failure has
been established. If solver needs expose missing library behavior, select one
explicit contract/case before numerical work. Full-stack, live ETABS, broader
family review, serviceability expansion and publication remain separate packets.

### Local verification — 30 September

The single focused batch passed on source `96170d81` with only this planning
document edited: **39 existing classification/convergence/CLI tests**, generated
facade docs current across **17 files**, and **13 source recipes** matching
their expected statuses with invalid-input rejection and finite JSON. The
existing link scanner, limited to this document, resolved **30 local targets**
with zero broken links. `./run.sh efficiency check` passed. No tests were added.

This closes the bounded local source-evidence packet. It establishes no new
numerical benchmark, installed-wheel qualification, general helper review,
current full-stack verdict or release authority. The broader proposed G1
matrix still needs row-level advanced/native evidence and scope decisions.
There is no confirmed code repair to queue from these checks. The parent owns
the optional solver-supporting versus broader-library direction decision.
