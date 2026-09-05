# WP01-WP10-04 implementation status

This record captures the review performed after each work packet and any change
to the next packet before implementation continues.

## WP01 review

State: implemented and focused verification passing.

Confirmed outcomes:

- Python and .NET expose FO01-FO04, AO03, and AO06 with the same semantic IDs.
- Canonical input bytes and normalized IDs match for common vectors.
- Effective inputs remain distinct from outputs and retain density, profiles,
  section data, bars, faces, and code-data revisions.
- Actual bars carry physical face, coordinate, diameter, and layer.
- Rectangular singly/doubly and eligible flanged positive/reverse bending cases
  are calculated; unsupported axial interaction cannot qualify.
- The pure packages have no Excel, ETABS, UI, HTTP, or renderer dependency.

Corrections made during review:

- Replaced the initial .NET envelope that stored outputs as effective inputs.
- Replaced one-face inferred reinforcement with explicit face/layer geometry.
- Treated flange-in-tension reverse bending as a supported web-section check.
- Added result identity separately from normalized input and calculation IDs.

WP02 plan update:

- Shear and torsion will accept actual transverse-link geometry, rather than
  required link area alone.
- Torsion interaction will require one concurrent action row containing shear,
  torsion, and bending components; component envelopes will be rejected.
- Axis and link-perimeter identity will be explicit so WP03 normalization can
  bind vendor actions without changing the engineering operation.

## WP02 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO05 evaluates Table 19/20 concrete limits and actual axis-specific link
  capacity, minimum provision, and spacing.
- AO07 checks signed station demands on V2 and V3 without mixing their section
  or active-leg bases.
- AO08 binds shear, torsion, and flexure to one concurrent source row and checks
  actual closed links and identified corner bars.
- Missing actual reinforcement remains `not_evaluated`; invalid input,
  unsupported scope, and completed engineering failure remain distinct.

Corrections made during review:

- Nonzero V3/M2 interaction now returns `not_applicable` for the bounded WP02
  profile instead of preserving and then silently ignoring those components.
- Torsion effective depth now follows the physical primary tension face.
- Link centre dimensions must fit the concrete section, both link directions
  need active legs, and perimeter ids must resolve four physical corners.

WP03 plan update:

- The action normalizer must preserve all six components and mark their
  concurrency basis before any design operation consumes a row.
- Topology must bind physical faces, local axes, support faces, span measures,
  section regions, and analysis elements without deriving them from load sign.
- The beam-line solver remains a bounded planar major-axis solver; unsupported
  minor-axis response stays visible in the normalized snapshot rather than
  being discarded.

## WP03 review

State: implemented and focused verification passing.

Confirmed outcomes:

- AO01 normalizes station, force, and moment units while preserving source,
  model, analysis/result epoch, member/span/object/element/station/case/step,
  local-axis, concurrency, and same-row P/V2/V3/T/M2/M3 identity.
- AO15 binds separate left-face, centre, and right-face support coordinates to
  clear, centreline, and effective design spans. Section regions and analysis
  elements must cover each physical span without gaps or overlap.
- AO02 solves the bounded planar V2/M3 Euler-Bernoulli profile with nodal,
  uniform, point, and prescribed support-movement inputs. It reports physical
  span/analysis element station identity and force/moment equilibrium.
- Python and .NET match the action-row and snapshot canonical identities and
  the closed-form simply supported UDL response.

Corrections made during review:

- Added the omitted WP02 portable request schema discovered by the
  prior-packet review.
- Changed the first .NET normalizer from an interaction-check gate to a source
  snapshot service, so component/design envelope classifications remain
  visible and are not silently converted or rejected during normalization.
- Replaced the first .NET single-face topology model with explicit support
  left/centre/right faces and exact region/mapping coverage.
- Replaced interpolated .NET station results with solved station degrees of
  freedom and calculated action fields, and exposed calculated equilibrium
  residuals instead of placeholder values.
- Kept free-force and free-moment residuals dimensionally separate.

WP04 plan update:

- FO07 and AO09 will distinguish span/depth screening from calculated
  deflection; a screen cannot be presented as a calculated displacement.
- Deflection inputs will bind the service action case, analysis result identity,
  cracked/uncracked stiffness basis, and explicit short-term, creep, shrinkage,
  and sustained-load assumptions.
- FO08 and AO10 will use the actual tension-face bar coordinates, diameters,
  spacing, cover, strain/stress basis, exposure, and declared crack criterion.
- Serviceability operations will preserve missing evidence as `not_evaluated`
  and unsupported methods as `not_applicable`; neither can qualify the later
  complete-member result.

## WP04 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO07 resolves separate total-final and after-finishes limits with an explicit
  code, project, or supplied source. An override can be stricter but cannot
  weaken the applicable code limit.
- FO08 maps harmful cracking and exposure to 0.3, 0.2, or 0.1 mm ceilings and
  applies the same explicit-source rule.
- AO09 keeps the bounded span/depth screen separate from calculated component
  aggregation. The calculated branch retains total and sustained service rows,
  analysis and reinforcement identities, short/long-term components, load and
  finish chronology, environmental values, and named calculation methods.
- AO10 evaluates Annex F flexural crack width from the physical tension face,
  area-weighted effective depth, minimum clear cover, supplied mean strain, and
  distance from the checked surface point to the nearest actual bar surface.
- Python and .NET match the exact component-aggregation and arrangement-sensitive
  Annex F vectors. Missing calculation history, actual bars, or mean strain is
  `not_evaluated`; a valid limit exceedance is an engineering failure.

Corrections made during review:

- Replaced the first .NET-specific bar record with the shared `BarCoordinate`
  contract and restored member, station, service-row, reinforcement-revision,
  and physical-face identity.
- Added the omitted effective depth and actual L/d evaluation to the .NET
  screening branch, and replaced method labels with the required numeric load,
  finish, duration, humidity, and notional-size evidence.
- Corrected effective depth to an area-weighted distance from the compression
  face and corrected `acr` to measure to the nearest bar surface rather than its
  centre.
- Populated every calculated deflection component in the .NET result and added
  validation for source, support, tension-face, and bar-face enum values.
- Rejected branch-specific displacement limits on a screening request and
  rejected invalid bar-face identity instead of retaining ignored inputs.
- Replaced the compact initial .NET draft with readable public contracts,
  operations, and tests.

WP05 plan update:

- AO11 anchorage will check the actual available bar path from a named critical
  section through support faces, bends, hooks, bond conditions, bar stress, and
  diameter. Required development length alone will not qualify a bar.
- AO12 lap and curtailment will retain each bar mark, physical face, start/end
  stations, splice zone, stagger group, continued steel, and shear demand near
  cutoffs. It will not assume that required area exists along the full span.
- AO13 seismic detailing will require an explicit IS 13920 applicability and
  context profile. Ordinary IS 456 members remain visibly not applicable to a
  seismic-only rule rather than silently passing it.
- AO26 arrangement checks will use actual coordinates, layers, cover, clear
  spacing, link/core geometry, bend space, and support-zone congestion. Area
  equivalence alone cannot establish constructability.

## WP05 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO06 calculates development length from the actual bar diameter and stress,
  concrete grade, bar surface, stress state, and bundle size. The normalized
  Amendment 6 epoxy modifier is explicit in the result and code-data revision.
- AO11 checks usable straight bar path and credited scheduled bends from a
  named critical section. Simple supports use the separate near face and
  centreline evidence required for the moment/shear-plus-Lo criterion.
- AO12 checks actual splice zones, lap or qualified-coupler evidence, percentage
  spliced, stagger group, termination extension, continuing steel at the demand
  station, anchorage, shear at cutoff, and any explicitly required extra links.
- AO13 makes the IS 13920 applicability decision visible and requires the full
  member, joint, bar, link-zone, anchorage, dependent-joint, and capacity-shear
  evidence for the supported seismic profile.
- AO26 evaluates the complete physical arrangement: section and link cover,
  cage closure and bend fit, bar enclosure, all bar collisions, aligned-row and
  physical-layer clearances, role centroids, obstacles against bars and each
  numbered cage segment, and the declared placement opening.
- Python and .NET publish matching typed requests and results, operation
  identities, optional inputs, code-data revisions, and conformance examples.

Corrections made during review:

- Replaced the legacy simplified schedule assumptions with actual bar paths,
  faces, station demands, splice and cutoff records, and qualified dependent
  result references.
- Kept the 36 mm restriction specific to lap splices; a larger bar can use a
  qualified coupler with installation evidence.
- Made extra-link evidence conditional on the detail declaring that it is
  required, and made that decision an explicit required field in both language
  contracts.
- Required exact operation identities for anchorage and shear dependencies so
  an unrelated passing result cannot qualify a curtailment or seismic check;
  seismic anchorage and joint results are also bound to their exact face and
  joint so duplicate evidence cannot qualify missing locations.
- Ordered physical layers from actual coordinates instead of trusting user
  layer numbers, and included link segments in obstacle checks.
- Aligned .NET link-segment numbering and optional prohibited-zone input with
  the Python and JSON wire contracts.

WP06 plan update:

- AO14 will create an immutable versioned project and design profile containing
  selected code-data revisions, required operations, criteria, accepted action
  bases, material and detailing rules, and catalogue identities.
- AO17 will compose existing leaf results without repeating their formulas. A
  member qualifies only when every profile-expected leaf is present, current,
  complete, applicable where required, and passing; rejected, partial, stale,
  or unqualified `not_applicable` evidence remains visible and disqualifying.
- AO18 will resolve each selected bar into a mark, count, diameter, physical
  role and layer, tangent straight segments, bend arcs, hooks, and exact start
  and end stations. Those paths feed AO11, AO12, and AO26 rather than assuming
  required steel continues for the full span.

## WP06 review

State: implemented and focused verification passing.

Confirmed outcomes:

- AO14 creates a deterministic immutable project basis from the project and
  profile revisions, canonical units, code-data and catalogue revisions,
  uniquely sourced criteria, required operations, topology scopes, and
  profile-resolved seismic applicability.
- AO17 derives every expected member leaf from the frozen profile and supplied
  design-scope instances. It retains required, selected, supplied, failed,
  missing, not-applicable, incomplete, stale, and unbound evidence separately
  and requires actual-depth convergence against every current applicable leaf.
- AO18 resolves each physical bar or link into ordered tangent straights and
  circular bend arcs with exact endpoints, bend centre, radius, angle, plane
  normal, sweep, developed centreline length, role, layer, detail references,
  and fabrication mark.
- Python and .NET agree on the canonical project-basis fixture, member result
  states, open and closed path geometry, mark grouping, and stock feasibility.
  The portable schema and conformance vectors publish the same semantic ids,
  fields, enums, units, and optional-value rules.

Corrections made during review:

- Removed the application-supplied required-check list from whole-member
  qualification. A caller cannot hide an SLS, detailing, seismic, or fit leaf
  by submitting a shorter list.
- Revalidate the complete project/profile request and its semantic identity at
  the AO17 boundary. Changing criteria, rules, catalogues, units, or revisions
  after AO14 now rejects the member request rather than using the old basis id.
- Bound every topology scope instance to the current design-scope revision and
  reserved the leaf-id separator so two rule/scope pairs cannot collide.
- Excluded stale, unbound, partial, and otherwise unqualified evidence from the
  governing-utilization selection while retaining it in the member output.
- Required the final actual-depth iteration to reference exactly all current
  applicable leaf results; expected not-applicable leaves remain visible but
  do not masquerade as depth-dependent calculations.
- Added the bend plane normal and sweep needed to reconstruct each 3D arc, and
  made mark grouping compare the ordered relative bend planes so distinct 3D
  shapes cannot share a fabrication mark. Stock-length feasibility remains
  separate from the WP07 cutting and offcut plan.

WP07 plan update:

- AO19 will consume one current resolved reinforcement schedule and an explicit
  shape and cutting-stock policy. It will reconcile mark dimensions, cut
  lengths, counts, mass, stock pieces, cuts, reusable offcuts, and waste without
  counting lap or cutting waste twice.
- AO04 will calculate reinforcement, concrete, and formwork quantities from the
  resolved paths, explicit net concrete segments, and named contact faces. It
  will preserve overlap, deduction, waste, interface, and measurement policies
  and will not invent rates when none are supplied.
- AO20 will apply a separately versioned rate profile with currency, effective
  date, geography, source, priced scope, labour, plant, waste, reuse, overhead,
  and tax treatment to the reconciled quantities.
- AO24 will create the reusable calculation-package semantic model containing
  assumptions, revisions, source and calculation identities, every member leaf,
  governing cases, paths, BBS, quantities, cost, drawing data, limitations, and
  real prepared/checked/approved actions. File rendering remains an adapter and
  formwork temporary-works design remains outside this packet.

## WP07 review

State: implemented and focused verification passing.

Confirmed outcomes:

- AO19 accepts only the unchanged passing AO18 payload, reconciles every mark
  summary with all physical paths, requires explicit ownership of each link
  station, and reports centreline dimensions, fabrication cuts, scheduled mass,
  stock, kerf, reusable offcuts, waste, laps, and couplers separately.
- AO04 measures actual scheduled bars, uniquely owned concrete prisms and
  deductions, and uniquely owned included or excluded formwork contact faces.
  Its output retains scheduled and purchased steel bases and never invents cost.
- AO20 binds the unchanged quantity payload and same project/member/detail,
  requires a dated and sourced exhaustive cost scope, prices steel from one
  waste basis, and sums displayed half-even-rounded lines before overhead and tax.
- AO24 binds every supplied dependency payload, enforces one project/member/
  detail/result chain and the complete AO17 leaf set, reproduces leaf values in
  traces, retains renderer-neutral drawing data, and activates only the latest
  real member approval on a current passing chain.
- Python and .NET expose the same required identities, typed records, semantic
  operation IDs, portable enum values, units, numerical fixtures, and result
  states. Rendering, Excel, ETABS, and temporary-works design remain outside the
  pure packages.

Corrections made during review:

- Rejected unzoned transverse-link marks and duplicate ownership of a shared
  link boundary.
- Replaced summary/exemplar trust with exact mark, path, count, material,
  developed-length, segment, and bend reconciliation.
- Defined currency rounding at each displayed line and based subtotal,
  overhead, tax, and total on those rounded amounts.
- Added canonical output-payload identities to every downstream request and
  dependency binding, and expanded the portable schema from opaque objects to
  typed WP07 records.
- Required quantity, cost, and package dependencies to retain one project
  basis; a cost from another project cannot enter an issued package.
- Required passing dependency engineering states for an issue-ready package
  and ordered approval actions by parsed UTC instant so time-zone offsets cannot
  preserve an earlier approval after a later rejection.
- Replaced the initial compact .NET sketch with readable public contracts,
  complete operations, and focused parity facts.

WP08 plan update:

- AO05 will generate a finite, reproducible candidate domain from explicit
  section, material, bar, link, layering, stock, and construction choices. It
  will retain the domain revision, enumeration order, count, exclusions, and
  cancellation state rather than claiming an unbounded search.
- AO21 will evaluate each candidate through the profile-derived AO17 leaf set.
  A candidate is feasible only when every required leaf is current, complete,
  applicable as expected, and passing; required `not_applicable` or unevaluated
  evidence cannot become a feasible winner.
- Ranking will use versioned deterministic objectives and tie-breakers over
  physical steel, concrete, formwork, cost, depth, congestion, and utilization
  values. Every excluded candidate will retain reason codes and result
  identities.
- A finite-domain optimum claim will require complete enumeration of the declared
  finite domain. Cancelled, timed-out, bounded, or heuristic searches will
  report their actual completeness and best-known candidate without upgrading
  it to a proven optimum.

## WP08 review

State: implemented and focused verification passing.

Confirmed outcomes:

- AO21 expands a bounded Cartesian product of section, longitudinal-bar, and
  transverse-link choices and creates canonical candidate, physical-definition,
  and domain identities in deterministic traversal order.
- Physical duplicates remain visible and reason coded, while only one physical
  definition consumes evaluation budget. Every evaluation must follow the
  canonical prefix.
- AO05 freezes the expected leaf set from the profile-bound reference AO17
  result. Required applicable leaves need completed, current, complete, passing
  evidence; a required `not_applicable` result is incomplete, while a
  profile-expected `not_applicable` result can qualify.
- Candidate member, quantity, cost, and optional reanalysis outputs are bound
  by exact operation, result, calculation, normalized-input, and output-payload
  identities. WP07 quantities and cost supply their corresponding objective
  values.
- Changes to section/property, stiffness/material, releases, offsets,
  self-weight/mass, loads/combinations, supports, mesh, or analysis settings
  retain `reanalysis_required`. Fixed-action ranking names its common-force
  assumption; coupled ranking requires fresh candidate-specific evidence from
  an owned model copy.
- Ordered objectives and explicit tie breakers produce deterministic results.
  Candidate ID is always the final tie. Performance uses deterministic work
  counts rather than elapsed time.
- Complete finite enumeration alone may select a candidate and claim optimum
  or infeasibility. Budget, cancellation, unresolved coupling, and incomplete
  evidence retain only a provisional best evaluated candidate and reason-coded
  exclusions.
- Python and .NET expose the same semantic operations, records, enum values,
  identities, units, and adversarial fixtures. Excel integration, ETABS model
  mutation, and search heuristics remain later host concerns.

Corrections made during review:

- Removed the optimization dependency on the reporting layer by defining a
  portable candidate-result binding owned by the WP08 contract.
- Separated physical-definition identity from caller choice labels so duplicate
  physical beams cannot consume budget or appear as distinct design options.
- Bound the domain output back to project, profile, topology, actions, scope,
  baseline analysis, and baseline section, and revalidated its semantic identity
  before ranking.
- Preserved fixed-action section studies as explicitly scoped comparisons while
  requiring fresh analysis evidence for the same section change in coupled mode.
- Replaced scalar application-supplied pass lists with the complete AO17 leaf
  set and retained all feasible, failed, incomplete, unevaluated, and duplicate
  records in the result ledger.

WP09 plan update:

- The canonical add-in references the native `StructuralEngineering.*`
  packages directly; the earlier Excel demo survives only through four
  compatibility delegates.
- Worksheet functions remain pure immutable projections. Workbook reads,
  writes, files, progress, cancellation, and rollback occur only in explicit
  commands.
- Installed acceptance uses one signed AMD64 package, an exact startup
  registration, a 20-member/200-operation sample, and the frozen PF9 budgets.

## WP09 review

State: implemented, independently reviewed, and installed verification passing.

Confirmed outcomes:

- `StructuralEngineering.ExcelDna` exposes the required `STR.INFO`,
  `STR.REBAR`, `STR.IS456.*`, `STR.BEAM.LINE`, and `STR.CONSTRUCTION` families
  over native WP01–WP08 operations.
- Versioned workbook tables and `XL-CMD-01/03/04/06/07` provide validation,
  full calculation, verified current-result reuse, current-candidate evaluation,
  calculation-package export, diagnostics, progress, and cancellation.
- Bulk writes bind preimage, readback, freshness, command receipts, result
  identities, and exact rollback. The shipped workbook saves, reopens, and
  reconstructs its current result identities.
- The signed per-user package passed preflight, install, repair, installed Excel
  workflow, and uninstall. UDF recalculation recorded zero host effects.
- `BENCH-EXCEL-TYPICAL` passed with 356.715 ms warm median, 413.457 ms warm p95,
  2,018.668 ms maximum cold-ready time, and 202.059 MiB working-set growth.
  Its 20 rows repeat one frozen physical beam case for batch and performance
  evidence; broader engineering diversity remains in the operation fixtures.
- Installed migration upgraded the legacy freshness/receipt table shapes and a
  changed runtime fingerprint invalidated saved results before recalculation.

Corrections made during review:

- Replaced the application-specific calculation chain with native operation
  dispatch and strict result projection.
- Fixed transient grouping, oversized Excel cells, result/freshness identities,
  cache content identity, export binding, table readback, COM object lifetime,
  and exact rollback.
- Allowed formatting-only controlled sheets to be reused while still refusing
  sheets containing unrelated values or formulas, and compared legacy
  recalculation with the matching calculation evidence rather than the later
  current-candidate result set.
- Made packaging compatible with Windows PowerShell 5, registered the exact XLL
  for normal Excel startup, and verified install/repair/uninstall against active
  workbook and startup-registration behaviour.
- Corrected cold-ready timing to end at the installed version probe and exclude
  prerequisite, host-configuration, and post-ready lifecycle checks while
  retaining those checks as mandatory evidence; removed the unnecessary blank
  bootstrap workbook from the timed startup path.

WP10 plan update:

- Add AO16 and `XL-CMD-02` through an optional exact-version ETABS adapter and
  bounded STA broker; keep CSI COM outside pure libraries and worksheet UDFs.
- Port the useful getter/ledger/snapshot semantics from the old Python work, but
  exclude its unit and result-selection setters from attached acquisition.
- Require exact pre/post state equality, complete parallel-array validation,
  six-component concurrent rows, offline replay, Excel transactional import,
  and PF8 E5-02 through E5-04 plus `PERF-ETABS-ACQUISITION`.

## WP10-01 review

State: implemented, cross-language parity verified, and host-free focused
verification passing.

Confirmed outcomes:

- AO16 now has strict portable request, raw-capture, call-ledger, normalized
  snapshot, diagnostic, provenance, and result records in Python and .NET.
- Model metadata, explicit optional evidence states, source/runtime/model and
  analysis/result identities, units and one-time conversions, axes and physical
  faces, geometry, material/section assignments, modifiers, offsets, releases,
  cases, combinations, selections, stations, and six-component force rows are
  retained without a host dependency.
- Every normalized fact references raw evidence; every source record has one
  accepted, approved-exclusion, or blocked disposition; accepted force rows
  bind the exact getter signature, call, source-row ordinal, station, selection,
  and canonical row identity.
- PF4 compact canonical JSON freezes call-record, ledger, raw-capture, action-row,
  and snapshot identities. Python and .NET produce the same canonical bytes and
  SHA-256 for the shared valid fixture.
- Invalid schema, stale result epoch, unresolved mapping/axes, blocked rows,
  incomplete ledgers, and raw/snapshot tampering fail closed with distinct
  operation and result states and never expose a partial accepted snapshot.
- The reusable modules reference no CSI, ETABS, COM, Office, or Excel host
  assembly. Offline replay proves portable integrity, not live ETABS
  compatibility, analysis correctness, or engineering approval.

Corrections made during review:

- Added explicit .NET JSON wire names for digit-delimited fields such as
  `inertia_2_mm4`, preventing a serializer-policy ambiguity from breaking the
  shared schema.
- Made Python canonical serialization recursively normalize model values, so
  integer-valued floats produce the same PF4 bytes as JSON and .NET.
- Kept approved exclusions visible in the conserved row ledger and separated
  transport/hash rejection, host-evidence fencing, and uncertain call completion.

WP10-02 remains the first host adapter packet. It must consume these frozen
records and add exact-version CSI/STA acquisition evidence; no such host code,
Excel command, model mutation, copied-model reanalysis, solver, or optimization
is implemented by WP10-01.

WP10-02 readiness update (2026-09-04): its one-session entry card, fixed source
budget, micro-probe order, stop rules, focused freeze matrix, and recurrence
controls are now defined in the WP10 plan. Passive inspection found ETABS
23.3.1.4563, ETABSv1.dll 2.16.0.0, the x64 type library, and .NET SDK 10.0.400
at the expected identities, but no ETABS process was running. Live work remains
held until exactly one intended saved, analysed model is open with its required
output selections already set.

## WP10-02 exact ETABS getter adapter

State: implemented, fake-host focused verification passing, and one bounded
installed getter matrix completed without ETABS state drift.

Confirmed outcomes:

- Added the optional Windows-only `StructuralEngineering.Etabs` project without
  a compile-time CSI reference. The default locked solution restores, builds,
  and runs fake-host tests without ETABS installed.
- The live boundary loads and hashes the exact ETABSv1 assembly, validates all
  48 frozen managed signatures including parameter names, attaches only through
  the exact existing PID,
  and verifies process start, executable version, API version, saved model
  identity, lock, and units before exposing a getter host.
- The runtime read-only whitelist records each allowed member, parameter name,
  order/direction/type,
  direct-value versus CSI-status semantics, output names, counted parallel
  arrays, fixed arrays, and evidence destination. Calls outside the whitelist
  fail closed; setters, unlock, analysis, design, save, close, and exit remain
  denied.
- Strict adapter results discard provider output after a nonzero CSI status,
  unequal array, timeout/cancellation, unknown call, or host identity drift.
  Fake scalar, counted-list, parallel-array, failure, timeout, and drift cases
  prove single-dispatch behavior with no partial accepted call.
- One repaired installed run used frame object `82` (label `B1`, story
  `Ground`) and the
  preselected combination `117.(1.5DL+1.5LL)`. All 48 getter identities were
  exercised through 410 calls; 13 `FrameForce` rows retained the same-row
  object/element/station and P/V2/V3/T/M2/M3 arrays. It also proves every force
  row belongs to object `82` and the exact selected combination, the returned
  analysis-element graph joins both frame endpoints, the two case-type getters
  agree, and the section/material getters agree.
- Protected process, file, lock, present/database units, 15 case statuses, run
  flags, and all 77 output-selection flags have identical preflight/postflight
  SHA-256. Exact raw output remains outside Git under a hash-bound evidence
  manifest; no normalization or partial snapshot is claimed.

Installed finding and bounded replan:

- `FrameObj.GetElm("82")` returned CSI status `1`; its historical evidence was
  static only. It is excluded from the final whitelist. Same-row
  `Results.FrameForce` object/element identities are instead verified with
  `LineElm.GetObj`, `GetPoints`, `GetLocalAxes`, and
  `GetTransformationMatrix`. No failed getter output became accepted evidence.

Candidate review and one bounded repair:

- The first candidate was rejected once because five executable premises were
  incomplete: whitelist immutability, digest-bound nullable-array metadata,
  exact reflected parameter names, cross-getter live consistency, and
  best-effort release of every acquired COM reference. One consolidated repair
  closed all five, and the refreshed 410-call installed matrix retained the
  same protected-state digest with no second repair cycle.
- The repaired candidate's read-only integrity gate then rejected four text
  hygiene defects inherited from the original candidate. Design revision 2
  normalized only those solution/project/lock paths against the original task
  base; no product behavior or live ETABS evidence changed.
- The first hosted run exposed platform-dependent CRLF checkout for changed C#
  files. Explicit LF attributes for `.cs`, `.csproj`, and `.slnx` now align
  local and hosted formatter bytes; the failed run never reached or invalidated
  product tests and was not merged.

## WP10-03 bounded operation broker

State: implemented, deterministic focused proof passing, the accepted WP10-02
capture replayed offline, and one exact-host getter-only broker acquisition
completed without protected-state drift.

Confirmed outcomes:

- The optional ETABS adapter now runs each acquisition on a dedicated STA
  worker with explicit message pumping and a process-keyed exclusive lease.
  A second operation cannot attach while that process lease is active.
- Absolute deadlines return `transaction_uncertain` without retry or final
  artifact. A late provider call retains the lease until host cleanup quiesces,
  preventing an overlapping second operation.
- Every permitted getter is surrounded by durable, write-through `started` and
  `returned` records. The continuous hash chain reuses WP10-01 canonical call
  and ledger identities and accepts only paired getter returns with status zero.
- Exact-SHA recorded replay reconstructs the accepted raw managed types and
  call order without a process or model file. The broker requires complete
  recorded-source consumption before postflight or publication. The 410-call
  WP10-02 capture reproduced its exact protected-state digest before the live
  gate.
- Final evidence uses a no-overwrite atomic move only after postflight identity
  equality, complete ledger construction, host disposal, and lease release.
  Pre-existing output, denied effects, deadline, identity drift, failed cleanup,
  incomplete replay or ledger, and artifact tampering all fail closed without
  an accepted final artifact.
- One final installed run produced 820 paired records across all 48 frozen
  getter operations. Process `7316` remained alive; the saved model's 703,208
  bytes, SHA-256, lock, units, result epoch, and selected combination were
  unchanged before and after.

The committed evidence is
`docs/verification/wp10-03-operation-broker-evidence.json`. Raw acquisition and
journal files remain external and hash-bound. WP10-03 does not normalize the
portable snapshot, write Excel, mutate ETABS, qualify performance, or broaden
the exact installed-version claim.

## WP10-04 offline projection and normalization

State: complete; exact retained-input normalization and independent Python
replay passed and [PR #972](https://github.com/Pravin-surawase/structural_engineering_lib/pull/972)
merged as `0d790b56ba92a059b2cac574be970a2cf9106821`. The task delivery ledger
binds the reviewed tree and required hosted run.

`EtabsCaptureProjector.Normalize` validates exact durable bytes and all 48
getter operations before producing a complete typed source projection.
`AnalysisSnapshotNormalizer.Normalize` owns units, topology, physical faces,
static concurrency, row conservation and canonical construction. The Analysis
assembly has no ETABS or Excel dependency. Failures expose no partial snapshot.

The retained capture produces 97 model records and 13 concurrent action rows;
all 110 source records are accepted, with no exclusions. All 410 getter calls
and the original 820-record ledger remain traceable. The portable ledger uses
equivalent UTC `Z` instants. The portable numeric serializer now matches PF4
scientific-number spelling; the durable artifact v1 encoder preserves existing
capture identities. Original WP10-01 golden vectors are unchanged.

The bounded policy supports horizontal straight rectangular members with
geometry-proved axes and static selected dependency closure. Original
cardinal insertion, separate section/object modifiers and getter details are
retained in typed raw evidence. There is no centroid relocation or implied
eccentric-force transformation. Nonzero joint offsets/release springs,
mirroring, transformed stiffness, unresolved topology or unsupported selected
analysis bases withhold the snapshot. Material kind is caller-supplied with
provenance; no material strength is inferred from names. Evidence-derived
revision/epoch identities describe the capture, not today's live model state.

Evidence: [WP10-04 normalization receipt](../verification/wp10-04-normalization-evidence.json).
The synthetic shared vector contains invented data only; proprietary capture,
API help and emitted retained snapshot remain external. WP10-05 Excel import
is next and has not started. No live acquisition, installed application test,
performance qualification, mutation, release or engineering approval is claimed.

WP10-05 preparation checked the actual Excel command, table-store, transaction
and freshness owners. Its [executable plan](../planning/xll-product/wp10-etabs-read-adapter.md#wp10-05-preparation-review-and-executable-plan--2026-09-05)
requires bounded chunk storage, explicit source/member binding, cache
invalidation, real Excel save/reopen and forced rollback. `XL-CMD-02` is not
implemented yet. Earlier WP09 installed evidence does not qualify this command.
The production acquisition entry point and PF9-sized multi-member acquisition
also remain unimplemented; WP10-05B/05C now own these prerequisites before
WP10-06. No whole-model compatibility or performance pass is inferred from
the retained one-member capture.
