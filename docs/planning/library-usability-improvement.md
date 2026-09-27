---
owner: Main Agent
status: active
last_updated: 2026-09-27
doc_type: spec
---

# Library usability and implementation quality

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
