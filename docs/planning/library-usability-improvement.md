---
owner: Main Agent
status: active
last_updated: 2026-11-07
doc_type: spec
---

# Library usability and implementation quality

**Current programme.** [0.27 beam and column release preparation](#027-beam-and-column-release-preparation)
owns the next feature scope. The [release ledger](../getting-started/releases.md#v0260-published-and-verified)
records the published 0.26.0 artifacts. The consumer fixes originally planned
for 0.26.1 are merged in
[PR #1045](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1045)
and will ship with 0.27.0. Their installed regressions are part of Goal 5.

The [professional standards programme](#professional-standards-programme-8-october-2026-revision-2)
and [assessment record](../verification/library-professional-standards-20261008.json)
retain the earlier scope and delivery evidence. GitHub owns the exact
reviewed-head, check and merge facts for each completed packet.

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

## 0.27 beam and column release preparation

The owner selected one 0.27.0 release that closes the identified beam and
column gaps. Goals 1–4 delivered the comparison fixtures, public examples,
layered column response and ordinary beam member evidence. The remaining
beam and column work comes before versioned qualification in Goal 5. The
slab and footing programme starts in 0.28.

[Jira epic LIB-7](https://pravinsurawase.atlassian.net/browse/LIB-7) owns work
status and dependencies. [Confluence](https://pravinsurawase.atlassian.net/wiki/spaces/SD/pages/17989634/StructLib+0.27+release+preparation)
summarizes the release for readers. The [comparison baseline](../verification/library-027-comparator-baseline.json)
records the observed outputs and package identities. The
[frozen references](../verification/library-027-comparator-reference.md) give
the independently derived targets, exact inputs, and method-specific replay
tolerances for all four cases. The
[working roadmap](https://chatgpt.com/space/page_32cfec9f5b288191ac31548609dbe25f)
keeps the staged programme and later member profiles.

### Measured scope

Published StructLib 0.26.0 and the installed build of main at `67c4555d`
gave identical outputs. The public `structural_lib.beam` component operations
already cover the supplied singly reinforced mixed-diameter beam, doubly
reinforced beam and two-layer flanged beam. The maximum observed difference
from rcdesign 0.4.18 was 0.32% or less for moment and total shear. Independent
replay traced the offsets to the flexural block and shear conventions.
Both engines pass their own reference targets. The public example exercises
the existing operations and matched all 21 frozen values on an isolated
0.26.0 wheel install.
[Beam comparison guide](../cookbook/python/beam-comparator-reference.md)

The layered column section operation returns the raw response for a solid
rectangle at a prescribed neutral axis. It has a separate request and result
from the two-face member workflow. The 900 mm case and the full-depth
boundary match the independent references within 0.001 kN and 0.001 kN·m.
[Layered column guide](../cookbook/python/layered-column-section.md)

The ordinary and multilayer worked members already produce bound calculation
JSON, BBS CSV and HTML. The doubly reinforced comparator lacks support-width
evidence and has a clear-cover/depth conflict under the member convention.
The existing member HOLD remains a regression control.

### Goal 3 layered column section response

`column.load_layered_section` accepts a mapping or JSON and validates
dimensions, strengths, a positive `xu` with finite depth ratio and depth-wise layers. The
section operation uses the closed-form Fig. 21 resultants and strain plane
with the existing Fig. 23 steel law. It returns compression-positive
axial force, signed centroidal moment, strains and contributions. The
versioned result carries `COMPLETED` with member and detailing acceptance
both `NOT_EVALUATED`. The 900 mm case returns 1394.806807 kN and
9.955790 kN·m above the slice's nominal cap. At `xu = D = 450 mm`, the
force and moment are 1124.900363 kN and 56.942945 kN·m, with zero strain
at the far face. The independent fixtures and invalid-input tests set the
verification boundary for the installed replay in Goal 5.
[Guide and runnable example](../cookbook/python/layered-column-section.md)

### Goal 4 ordinary beam member workflows

Both member cases ran from a source-bound development wheel and their JSON,
CSV and HTML agreed on the check set, physical revisions, bar paths and
schedule. The single-layer case retained 19 checks and 39 paths. The multilayer
case retained 27 checks and 43 paths. The supplied-beam diagnostic held for
missing support width and failed for depth mismatch and insufficient
reinforcement. The two full member overload replays produced draft artifacts
with the actual load basis. Goal 5 reuses the replay verifier against both
versioned archives.
[Member guide](../cookbook/python/ordinary-beam-member.md)
· [Installed replay receipt](../verification/library-027-member-replay.json)

### Beam and column closure before Goal 5

The release scope covers selected IS 456 beam sections and ordinary
rectangular column members. Use rcdesign for the shared section cases and
independent calculations for acceptance. The physical member workflows
also need their own geometry, detailing, support and output evidence.
The broader section analysis programme covers arbitrary shapes, general
interaction surfaces, moment–curvature and other layouts and code bases.

| Order | Work | Evidence required before release |
|---|---|---|
| A | Finish the layered rectangular column section API | The existing request now accepts partial compression and mixed diameters as separate groups at one depth. Both new cases, signed steel stress, displacement, continuity at `xu = D`, strict JSON, invalid geometry, and the original 450 mm and 900 mm cases are covered. [Guide](../cookbook/python/layered-column-section.md) |
| B | Close the remaining beam section comparison gaps | The supplied section API covers vertical and 45° stirrups plus single or repeated bent-up bars, with independent component, limit and combined checks. Sagging flexure is verified within the flange and in both web branches, including the Annex G cutoff and rounded force gap. [Guide and evidence](../cookbook/python/beam-section-closure.md) |
| C | Finish an ordinary physical four-corner column member | The physical short braced profile resolves four equal bars from cover, tie diameter and corner inset. Both principal directions match independent section references. Actual cage checks, missing/insufficient tie and overload controls, bound JSON and HTML, and the runnable example are covered. [Guide and scope](../cookbook/python/column-four-corner-member-check.md) |
| D | Compose rectangular beam flexure, shear and torsion through detailing | Reuse the [torsion evidence plan](https://pravinsurawase.atlassian.net/browse/LIB-3) and [member implementation plan](https://pravinsurawase.atlassian.net/browse/LIB-4). Qualify one ordinary non-seismic supplied rectangular member with concurrent actions, actual closed links, and longitudinal steel on both relevant faces. Resolve torsional load path, support, serviceability, anchorage and fit before admission. Replay nonzero torsion, zero-torsion compatibility, missing evidence and insufficient provision. Match paths, BBS and report to the checked layout. |
| E | Complete the ordinary sagging T-beam member workflow | Reuse the supported monolithic T-beam calculation and qualify one actual supplied layout with zero torsion. Prove flange geometry and bar fit, web shear width, anchorage, and agreement between member checks, detailing, paths, BBS and report. Verify a failed or held case alongside the passing case. |

Packet A extends the existing 230 × 450 mm M20/Fe415 fixture.
The standard-library reference and pinned rcdesign 0.4.18 agree on these
starting targets. Use absolute tolerances of 0.001 kN and 0.001 kN·m.

| Case | Change to the frozen fixture | Axial force (kN) | Centroidal moment (kN·m) |
|---|---|---:|---:|
| Partial compression | Prescribe `xu = 300 mm` with the original layers | +633.823982 | +110.974614 |
| Mixed diameters | Prescribe `xu = 900 mm` with Ø16, Ø20 and Ø16 at the 50 mm depth | +1432.527185 | +16.556856 |

For each packet, record the source and independent expected values before
changing calculations. Deliver a runnable example and guide, verify the
affected outputs, and keep PASS, FAIL, HOLD and rejected inputs distinct.
Goal 5 starts once all five packets have accepted evidence. If a packet
cannot qualify, record the unresolved case and bring the release scope
decision back to the owner.

### Packet C implementation and acceptance

Packet C admits one short braced solid rectangle with four equal
corner bars, ordinary closed deformed ties and one selected principal
bending direction. The caller supplies the factored axial force and moment,
end restraint, material strengths, nominal cover, aggregate size, actual
tie dimensions and an explicit corner inset. The physical bar centres
determine the steel area and equivalent two-face depth.

1. Freeze independent geometry, detailing limits and section/member targets
   before changing calculation owners. Verify x and y directions by rotating
   the section and retaining the same four physical bars.
2. Add a strict versioned request and public loader/check operation. Preserve
   structured rejection of malformed inputs and separate FAIL and HOLD for
   inadequate provision and missing tie evidence.
3. Reuse column classification, effective length, minimum eccentricity,
   steel-law, P–M and tie-spacing owners. Check every physical face and the
   rounded inside tie corner. Reuse the beam containment geometry through
   its code-independent owner.
4. Bind the result and HTML report to the same input identity, physical
   arrangement, supplied tie, named checks, units and source references.
5. Deliver one runnable example with passing x/y, insufficient strength,
   inadequate ties and missing-tie controls. Add a guide and verify a fresh
   development-wheel installation, the affected regressions and required
   hosted checks.
6. Close the packet with its merge evidence. Update the handoff for Packet D
   and archive superseded dated handoffs with their links and provenance.

### Packet D revised work order and evidence boundary

The source review found that the existing station check used transverse
stirrup centre dimensions in the Cl. 41.4.3 reinforcement equation. That
equation needs the distances between corner longitudinal-bar centres.
The stirrup dimensions belong to the separate pitch rule in Cl. 26.5.1.7.

D1 starts with this root correction in the Python and C# calculation owners.
The frozen 300 × 400 mm M25/Fe415 station has four Ø20 corners at
(50,50), (250,50), (50,350) and (250,350) mm. Use the same concurrent
row with V2 = 60 kN, M3 = 15 kN·m and T = 15 kN·m. Corner dimensions
are 200 × 300 mm; the Ø8 link centre dimensions are 242 × 342 mm.
The independently required Asv/s is 0.914000831 mm²/mm. Two Ø8 legs
at 100 mm supply 1.005309649 and pass this station check. At 125 mm they
supply 0.804247719 and fail despite satisfying the 146 mm pitch limit.
[Independent source and fixture](../verification/library-027-torsion-station.json)

| Stage | Work and exit evidence | Current boundary |
|---|---|---|
| D1 | Freeze the source-correct station inputs, fix corner dimensions, expose method/basis, replay adequate and inadequate provision in Python and C#, and preserve the zero-torsion route. | Implemented source correction with an executable station replay. |
| D2 | The [physical worked profile](../cookbook/python/physical-torsion-member.md) binds concurrent source rows, support faces and critical sections, actual closed cage/paths, hooks, full-stress direct tension anchors at all eight ends, both-face continuity, mild durability and signed torque transfer through checked receiver sections. | Physical/ULS evidence is complete for this profile; the D2-only replay deliberately retains its three serviceability HOLDs. |
| D3 | The [selected transient service case](../cookbook/python/physical-torsion-member.md#complete-the-selected-d3-service-case) adds distinct service/permanent actions, actual-bar cracked flexural response, time-dependent permanent deflection, supplementary cracked torsional stiffness, edge-displacement criteria and indirect Annex-B service stress/detail crack control. | All 31 obligations qualify for the declared demonstration. Missing or unsupported service histories and boundary evidence retain HOLD; torsional crack width and universal twist limits are not claimed. |

The source review distinguishes collapse-limit torsion in Cl. 41 from the
flexural deflection and crack provisions in Cl. 42–43 and Annex F.
A supplementary uncracked elastic stress screen would need its own declared
assumptions and does not supply torsional crack-width or twist acceptance.
The D3 closeout below adopts a separately identified cracked torsional
stiffness method, applicable displacement and indirect crack-control
criteria, and traceable service actions. An uncracked screen is not used
to discharge the torsional serviceability obligation.

**Owner clarification — 7 November 2026.** No project-specific torsional
serviceability assessment or twist/crack criteria are available. Selecting
and qualifying the demonstration's method is library work; the owner is not
required to invent numerical limits. Continue D2 strength, detailing and
output preparation while D3 remains HOLD.

D3 must first establish the applicable requirements for the named profile,
using the controlled source and amendment set. IS 456 Cl. 35.3.2 provides
general crack-control guidance, while Cl. 43.1 and Annex F address flexural
cracking. A crack-width limit alone does not supply a torsional response
model, and this review has not established a universal numerical twist limit.
Research must distinguish applicable code requirements from criteria needed
for a particular use. Published methods from other codes or research are
candidates to assess, not automatically adopted IS 456 rules. Declare any
demonstration assumptions and independently verify the selected method;
project acceptance cannot be inferred from those assumptions. Missing
essential evidence retains HOLD, and the agreed 0.27 scope stays unchanged.
[Primary text reviewed](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf)
(public 2007 reprint including Amendments 1–2; later controlled amendments
remain part of method qualification).

Use full design-stress anchorage unless a source-consistent calculation
establishes each actual torsion-face bar stress. The ordinary zero-torsion
worked beam's top compression anchorage cannot establish tension anchorage
for a torsion-induced opposite-face demand.

D1 station PASS alone leaves the full member on HOLD. D2 and the selected
D3 service profile are implemented below; Goal 5 still waits for Packet E
and its own exact-archive qualification. The runnable
station example makes this boundary explicit.
[Station example](../../Python/examples/torsion_station_reference.py)

#### Packet D2 requirement ownership

D2 froze its physical member and independent targets before extending
orchestration. The D1 station is a section control;
its actions do not establish a member load diagram or torsional restraint.
The following matrix retains the implementation requirements and reuse points;
the worked-profile closeout below records their D2 disposition.

| Required evidence | Reuse owner | D2 addition or qualification |
|---|---|---|
| Concurrent actions and support-face/critical-station coordinates | `analysis.normalize_action_snapshot`, `analysis.define_beam_topology` | Bind every named station to its original concurrent row and topology revision. Preserve the separate source of analysis and support-restraint evidence. |
| Combined section strength and both-face longitudinal demand | `shear_torsion.check_torsion` | Run D1 at the required stations and map primary/opposite equivalent moments to the actual top/bottom bars and paths. |
| Perimeter cage, cover, clearances and enclosure | `detailing.check_reinforcement_arrangement` | Check every required physical arrangement with the same corner bars, closed links and reinforcement revision. Scalar steel area cannot replace fit evidence. |
| Ordinary link hook/tail compliance and fabricated geometry | `bar_paths.resolve_bar_paths` supplies tangent, bend and tail geometry | Add a source-bound ordinary-link compliance check; path resolution alone does not verify hook requirements. |
| Tension anchorage at both faces and both ends | `detailing.check_anchorage`, `DevelopmentLengthRequest`, `AnchoragePath` | Build face/end scopes at the actual critical support faces using tension development. The ordinary example's top compression anchorage is not reusable as this evidence. |
| Continuous perimeter bars and station steel demand | `detailing.check_laps_and_curtailment` | Derive demands for every torsion-required face/role and bind them to the actual continuous runs. The ordinary example supplies bottom-role demand only. |
| Torque equilibrium and transfer into each support | No complete member-evidence owner identified in the current beam composition | Add a narrow check of supplied actions, reactions and declared transfer evidence. Topology alone cannot establish torsional restraint; analysis/model validity stays with its analysis owner. |
| Exposure, material and required cover | Arrangement checks actual supplied cover; project criteria carry references | Resolve the applicable source requirements and add a bound admission/check leaf. Neither supplied cover nor narrative criteria establish durability compliance. Reuse shared source helpers where available. |
| Complete required check set | `member.MemberDesignRequest` and profile/check scopes | Freeze the expanded D2 leaf set before execution. Preserve the ordinary 19-leaf and multilayer 27-leaf regression profiles. Missing evidence keeps the member incomplete. |
| Flexural and torsional serviceability | Existing flexural `serviceability.check_crack_width` and `check_deflection` | Retain their applicable flexural evidence. Torsional SLS stays a distinct D3 obligation with an adopted method, service actions and acceptance criteria. |

Implementation order: freeze the physical/load-path profile and independent
references; bind topology, actions and station strength; supply the missing
hook, support-transfer and durability evidence owners; resolve the common
physical paths, both-face tension anchorage and continuity; then compose all
expected leaves and reconcile outputs. The profile remains HOLD while any
essential evidence, including D3 torsional SLS, is missing.

#### Packet D2 worked profile and closeout

The [standalone example](../../Python/examples/physical_torsion_member.py)
uses a 300 × 400 mm M25/Fe415 beam, four continuous Ø20 bars and actual
Ø8/100 links. Its support centres are 5000 mm apart, clear faces 4000 mm
apart, and all main bars extend 950 mm past the near support faces.
The independent [D2 reference](../verification/library-027-torsion-physical.json)
retains the supplied 5000 mm analysis span separately from the Cl. 22.2
effective-span geometry of 4350 mm; no action target was changed to the
shorter span. Exact signed row targets, source identities, Ld, hook and
physical-length targets are independently replayable.
The nine concurrent action rows include both exact combined bending/torsion
peaks either side of midspan; the governing equivalent moment is
37.528258362 kNm rather than the plain bending peak of 37.5 kNm.

For the eccentric 12 N/mm load, each end transfers 30 kN and an external
-1.5 kNm torque through named reaction lines into a transverse receiver
crosshead. Both support couples have the same global sign. The receiver
loads, geometry, topology, case and real section flexure/shear results
are bound together, including explicit gross factored receiver self-weight;
actual receiver bars are staggered from the primary main bars and links,
with a conservative 25 mm minimum crossing clearance against resolved paths;
its end reactions define the supporting-system
boundary. This packet does not design bearing/contact stresses, receiver
end connections, other supporting members or foundations.

All eight tension anchors use `direct_support`: the full unrounded
805.915178571 mm development requirement is compared against 950 mm,
without a flexural M/V reduction. The actual path/cage binding, ordinary
90° tangent tails, hook-plane separation, constant pitch and supplied
mild-exposure mix/cover are checked. The ordinary 135°/180° source limits
are preserved without importing seismic tail floors.

The profile declares 31 leaves before execution: 28 D2 qualifications and
three held serviceability leaves. Draft JSON, BBS and HTML keep D2 results,
the 54 physical paths and the D3 HOLD distinct. Inadequate or missing D2
evidence cannot remove an obligation or turn the member into an accepted
result. Existing ordinary/multilayer profiles retain their 19/27 checks.

The D2-only replay preserves this historical serviceability boundary.
The optional D3 replay below resolves the three obligations for a declared
service case without inventing project facts or universal numerical limits.

#### Packet D3 selected service profile and closeout

The [D3 reference](../verification/library-027-torsion-serviceability.json)
was frozen independently before production calculations. The existing
physical example now accepts `--with-serviceability`; its original D2-only
command remains a HOLD regression control.

Declared demonstration components are permanent G=5 N/mm at zero
eccentricity (3 self-weight plus 2 superimposed), and imposed Q=3 N/mm at
400/3 mm eccentricity. G starts at age28days; finishes at56days; Q is
assessed immediately at application at3650days. Total service is 8 N/mm
at50mm eccentricity. Equal1.5 factors reproduce every frozen D2 ULS row
at12 N/mm and50mm eccentricity; no torque is discarded. Permanent torque
is zero. This is an explicit selected model, not a declaration about a
user's project. Finite-duration or permanent torsion needs further evidence.

Actual compression/tension bars determine fully cracked flexural stiffness.
Permanent deflection is re-solved at Ec/(1+1.6), with a conservative in-range
AnnexC3 shrinkage estimate that ignores beneficial compression steel.
After-finishes deformation conservatively includes all creep and shrinkage.
AnnexF uses elastic tension-surface strain, retaining no tension-stiffening
benefit. Its result is flexural cracking only.

Torsional rotation uses the supplementary Bruun/Kuan/Bentz2020 cracked
secant stiffness model, Eq3, independently checked against its published
worked example. The source requires the **cube** of corner-bar enclosed
area; dimensional analysis and the worked value reject a squared-area
misreading. This is research mechanics, not an IS456 torsional formula.
Actual receiver model symmetry and explicit pinned, zero-settlement
receiver end conditions establish the same-edge support-chord datum;
absolute supporting-system movement is outside this profile. Torsion-induced
edge displacement is added to flexural deflection under Cl23.2. Separate
AnnexB5/B6 service stress/detail compliance provides indirect torsional
crack control, with no claimed numerical torsional crack width.

| Qualified service quantity | Independent value | Criterion |
|---|---:|---:|
| Final total edge deflection bound | 8.532890067 mm | 17.4 mm |
| After-finishes edge deflection bound | 4.653362991 mm | 12.428571429 mm |
| Flexural crack-width upper bound | 0.162898079 mm | 0.3 mm |
| Relative midspan twist | 0.002169322602 rad | Included as physical edge displacement |

The actual5000mm action/deformation span remains distinct from the4350mm
code span used for the conservative limits. The full31-leaf member and
54 paths reach issue_ready with engineering approval unreviewed. At
21 N/mm ULS, D2 still passes but the AnnexB service compression limit
fails, correctly keeping the member and outputs failed/draft. Missing
history, nonzero permanent torque, finite imposed duration, stale or
conflicting actions, missing peaks and unknown/asymmetric receiver models
retain HOLD. Zero and reversed torsion retain their real signs.

Packet E now supplies the ordinary sagging T-beam physical member below.
Goal 5 must replay this D3 service case
and its FAIL/HOLD controls from both exact archives. No release follows
from D3 implementation alone.

#### Packet E implementation plan — ordinary sagging T-beam member

**Delivery status (7 November 2026):** E1–E5 are implemented and qualified
for the bounded profile below. The original five-unit plan is retained to
show the acceptance obligations. The [guide](../cookbook/python/t-beam-member.md),
[independent reference](../verification/library-027-t-beam-member.json) and
[installed qualification receipt](../verification/library-027-t-beam-qualification.json)
record the delivered behavior. GitHub owns the final candidate's required
hosted checks, review and merge facts. Goal 5 is next; no 0.27 package has
been published by Packet E.

| Unit | Delivered evidence |
|---|---|
| E1 | Original six-web-bar targets frozen before production changes; supplemental independently established local strip/parallel-steel audits disclosed separately. Controlled source hashes, numerical tolerances and standard-library checker retained. |
| E2 | Actual T-union cover and path containment, including shoulders and concrete end cover; explicit global/web projection; all-six-bar cage/hook binding; 46 actual beam paths. |
| E3 | 30 fixed obligations: 18 member rules and 12 actual bar-end anchorages. Main and width-limited members qualify 30/30. Separate flange participation, action provenance, lateral restraint and actual-T service evidence remain required. |
| E4 | Runnable base-install example, strict request/schema exports, matching JSON/BBS/HTML and actual T drawing. Physical concrete/steel ownership is explicit; separately owned slab steel is excluded from beam BBS and receives no beam strength credit. |
| E5 | Fresh neutral wheel install from site-packages: two adequate members, eight FAIL controls and three HOLD controls; strict public API round trips and deterministic artifact reconciliation. 34 new tests and 291 affected existing tests passed, with focused repair replay; type checks passed for 340 source files. |

The main member uses 1000 mm physical/effective flange width. The variant
uses 2500 mm physical width and 2200 mm compression width. Both retain the
300 mm web, actual self-weight and independently checked local transverse
strip. The web-shear trap fails when evaluated with `bw`, as required.
The service route is the complete flanged span/depth **screen**, with an
actual T cracked-section Annex F soffit envelope and both eligible-slab-steel
and no-slab-credit states. It does not calculate a deflection in millimetres.
Nonzero torsion remains HOLD: the new Python-only zero-torsion operation
proves zero demand across ULS, total-service and permanent snapshots; it
does not calculate T torsion resistance. Native changes are append-only
flange path-role metadata and matching WP06/WP07 schemas, not a native
T-member API. Existing rectangular torsion behavior remains unchanged.

The qualified development wheel retains **0.26.0 metadata** and is bound by
SHA-256 and packaged-source parity in the receipt. This is development
qualification, not evidence of a published 0.27 release or professional
approval. Goal 5 must rebuild and replay both exact versioned archives.

**Objective:** qualify one ordinary, monolithic, symmetric sagging T-beam
member with supplied reinforcement, zero torsion and separate ULS/SLS
actions, from actual geometry through strength, serviceability, detailing,
bar paths, BBS, quantities and calculation JSON/HTML. Include a width-limited
variant of that same profile and genuine FAIL/HOLD controls. Completion is
the whole member and its installed consumer journey, not another section
capacity example.

**Initial candidate to freeze in E1:** M25/Fe415, 300 mm web, 550 mm overall
depth, 150 mm flange thickness, 1000 mm physical flange width and nominal
6000 mm analysis span; four Ø20 bottom bars and two Ø16 top bars, all beam
longitudinal bars inside the web cage. These are proposed starting inputs,
not a verified design. Cover, exact bar centres, ordinary web links/hooks,
support faces and lengths, development, exposure, G/Q components, self-weight
and loading/finish history must be resolved together before numerical
targets freeze. Recompute every target for the actual six-bar arrangement;
do not copy Packet B's different five-bar section values or D3's rectangular
service values. Adjust the candidate with disclosed reasons before freeze
if any required physical or service provision is infeasible.

**Scope and ownership:** first support a supplied, prismatic, simply supported
T member under concurrent static vertical actions and sagging bending.
Retain separate obligations for stability/lateral restraint, flange
participation, actual cage fit, anchorage, continuity, durability and SLS
where applicable. Freeze the applicability evidence in E1. Nonzero torsion,
hogging flange participation, L sections, seismic design, axial/biaxial
interaction, arbitrary openings/layout search, splices/cutoffs, non-monolithic
interfaces and whole-slab design are separate profiles. Such inputs receive
an explicit unsupported/HOLD disposition; they cannot be silently projected
onto the selected T case. Required local flange/interface reinforcement or
load-transfer evidence must be supplied and checked, or implemented within
this packet if necessary for the admitted case. Do not waive an essential
T-member obligation by calling it future slab work.

##### E1 — freeze the engineering profile, inputs and independent references

Read the controlled IS 456 source and amendment set for effective flange
width/participation, Annex G flexure, web shear, reinforcement and ordinary
hooks/development, durability, effective span, lateral restraint and
serviceability. Record source hashes, clauses/table rows, modeling assumptions,
units, shared lineage, independent expected values and justified absolute
tolerances before production changes. The existing
[Packet B fixture](../verification/library-027-beam-section-closure.json)
and its independent replay are regression evidence, not the new member's
numerical answer. Pinned rcdesign comparisons may corroborate the shared
section domain; acceptance also needs independent statics, geometry and
service references.

Freeze these distinctions in the public input/schema design:

| Input/basis | Required meaning and binding |
|---|---|
| Physical concrete | `bw`, overall `D`, `Df`, actual left/right flange overhangs, actual T outline and section revision; monolithic participation evidence |
| Effective compression width | Derived `bf_effective` and governing limit, separately from `bf_physical`; record the correct zero-moment distance `l0`/code basis, rather than copying an arbitrary span |
| Spans/supports | Actual analysis span, code effective span, `l0` where different, both support centres/faces/widths and real available anchorage; no unexplained substitution |
| Positioned steel | Actual IDs, diameters, faces/layers, global coordinates, web-cage association, starts/ends, grades and the reinforcement revision; distinguish beam bars from separately owned slab/flange steel |
| Links/hooks | Web-only cage dimensions, active legs, pitch/zones, bend radii, ordinary hook angles/tangent tails and actual fabricated paths |
| Actions | Distinct current ULS, total-service and sustained/permanent snapshots, concurrent row IDs/axes/units, load decomposition/factors, governing stations and load-history reference |
| Service criteria | Exposure/harmful-cracking basis, actual T service-section stiffness/NA/steel and surface strains, time/history and applicable deflection conditions; missing basis stays HOLD |
| Ownership | Member/profile/input identities, flange/slab concrete and reinforcement ownership, support-interface deduction policy and formwork measurement policy |

Choose the service method before strength implementation starts: either a
source-qualified T-specific span/depth screening basis with all applicable
factors or a calculated T-section response with source-qualified creep and
shrinkage. Freeze the chosen complete route and the flexural crack-control
basis for the actual supplied bars. A supplied deflection/strain number or
an unverified modification factor is not its own calculation evidence.
Do not copy D3's rectangular `Icr`, neutral axis, shrinkage shortcut, timing
or method revision into a T result.

**E1 exit:** an explicit admitted-domain and requirement-to-owner matrix,
the entire expected leaf/scoping set, independently frozen main and
width-limited cases, and invalid/FAIL/HOLD targets. Derive the expected count
from these obligations; do not copy 19, 27 or 31 from older examples. Resolve
every essential source/model gap before treating this profile as admissible.

##### E2 — bind actual T geometry, web cage and fabricated steel

The current physical geometry, enclosure and path owners use rectangular
bounds. Add a bounded T-outline/containment owner or verified composition
that distinguishes the flange from the web. Use one global physical frame:
x from the **left edge of the actual flange**, y from the **top of the flange**,
and longitudinal station from the declared member origin. Store the web's
offset explicitly. Translate to web-local coordinates only in a named,
identity-bound projection consumed by an existing rectangular web-cage
helper; preserve IDs and prove the projection's round trip. Flexure's current
bar validation does not establish x containment, so a strength PASS cannot
discharge this geometry leaf.

Physical containment, cover and collision checks must use the actual T
boundary, including flange soffits/shoulders. Web links stay around the web
steel; never widen them to the effective/physical flange width merely to
obtain an enclosure PASS. The first beam cage keeps its longitudinal bars
in the web; this is not a claim that a six-bar cage constitutes all slab
reinforcement. Account separately for any flange steel needed by the frozen
participation basis. A bounding-box-only path result cannot qualify steel
passing through the empty area beside the web below the flange.

| Reuse owner | Reuse and confirmed addition/qualification |
|---|---|
| `beam.flexure.FlexuralCapacityRequest`, `flexural_capacity`, `check_flexure` | Existing sagging T compression branches; supply independently derived effective width and actual y coordinates. Add the physical x/material-containment evidence outside the strength result. |
| `codes.is456.beam.flexure.calculate_effective_flange_width` and the existing flanged service facade | Reuse the width calculation/source basis without assuming the facade proves physical detailing or installed member admission. |
| `beam.reinforcement.effective_depth` / `evaluate_geometry` | Reuse area/depth/spacing owners through the explicit web projection where valid; add full-T material/cover binding. |
| `ReinforcementArrangementCheckRequest`, `LinkCage`, `check_reinforcement_arrangement` | Reuse rounded web-cage enclosure, spacing and collision checks; keep the actual T boundary separate. Do not require slab-owned bars to be enclosed by a fictitious flange-wide web link. |
| `ClosedLinkDetailRequest`, `check_closed_link_detail`, `ordinary_link_anchorage_limits` | Reuse source hook limits and actual path mechanics. The current physical hook binding expects four longitudinal bars; qualify a shared all-required-bars binding for the proposed six-bar cage without weakening the D2 four-corner regression. |
| `BarPathRequest`, `BarPathSeed`, `PathPoint`, `resolve_bar_paths` | Reuse 3D straight/bend/tail resolution and lengths; add T-material containment and web/global datum binding. A rectangular envelope alone is not a T fit check. |

**E2 exit:** all steel has actual paths, correct cover/fit and one set of
coordinates shared by section checks, cage, anchorage and outputs. Freeze
controls for a bar/path in the empty shoulder region, a flange-width web
cage, short hook/insufficient clearance and a mismatched geometry revision.
These controls must fail or HOLD at the responsible owner, not disappear
from the expected check set.

##### E3 — compose the complete strength, service and detailing checks

Bind the same section, topology and reinforcement revision to each source
row/critical station. Reuse `check_flexure` for sagging T strength and
`check_shear`/`ShearCapacityRequest` for the actual web width, effective depth
and eligible continuing tension steel. Retain Packet B's within-flange,
reduced/full-flange web branches and `FLEXURE.FLANGE_FORCE_GAP` unsupported
control. They remain section regression evidence unless a variant also
passes the whole physical/service profile; do not advertise full-member
coverage for a section-only branch.

Reuse `check_anchorage` with `AnchoragePath`/`DevelopmentLengthRequest` at
the real support faces and actual path ends. Bottom sagging bars need the
qualified tension-development criterion. Top bars need their actual
supported stress/continuity basis or an explicitly conservative full-tension
development check; no borrowed compression label or M/V relaxation without
evidence. Reuse `check_laps_and_curtailment` for the selected continuous runs
and station steel demands, with no splice/cutoff search added.

Supply the independently qualified T service-state provider to the existing
`check_deflection`, `check_crack_width` and limit owners. Its effective
flange width, centroid, gross/cracked inertia, neutral axis, compression
steel displacement and surface/bar strains must describe the same section
and service loads. Verify the case with the neutral axis on either side
of the flange boundary if those states are admitted; unsupported states
retain HOLD. Distinguish instantaneous, sustained, creep, shrinkage and
after-finishes effects according to the selected route. A rectangular SLS
PASS or zero-torsion result cannot substitute for the T-specific evidence.

Compose the full `BeamDesignProfile`, `DesignCheckRule`, scoped
`MemberLeafEvidence`, depth iteration and `MemberDesignRequest`. All required
leaves must be present before member qualification; applicable geometry,
flange participation, stability, durability and SLS evidence cannot be
removed to obtain a smaller green profile. Preserve ordinary non-seismic
non-applicability explicitly. Freeze public typed inputs/outputs, semantic
method revisions, source references and strict JSON schemas at their
maintained owners; a new HTTP/native interface is not implied by this packet.

**E3 exit:** complete main and width-limited member results, plus a
strength/service/detail failure and a missing-evidence HOLD. Each result
has an independently inspectable reason and the actual required/provided
reinforcement. No generic 'section safe = member complete' shortcut.

##### E4 — reconcile construction outputs and the consumer example

Reuse `create_bbs`, `calculate_construction_quantities` and
`create_calculation_package` with their current result/payload identities.
Show the actual T outline and positioned web cage in the guide/report's
section view; distinguish physical width, effective width and web width.
Reconcile every bar/mark/count, developed straight/bend/hook length, scheduled
steel mass and physical path ID across BBS, JSON and HTML.

Concrete uses a non-overlapping physical T union, such as flange plus web
below the flange. **Effective compression width is not a quantity width.**
Give the flange/slab and support interfaces one ownership/deduction policy;
do not count the flange twice as beam and slab. Formwork distinguishes web
soffit/sides and flange soffits/edges under a named policy; internal web/flange
interfaces are not exposed formwork. Any separately owned slab steel must
remain labeled and excluded from beam quantities unless supplied in the
admitted ownership scope.

Deliver a standalone public-API example and a beginner guide with complete
inputs, units, schemas, assumptions, supported/unsupported cases and copied
commands that work in a base installation. JSON/HTML must expose all required
leaves, governing values, method/source identities and limitations. All
adequate leaves may produce `issue_ready` with approval still unreviewed;
FAIL/HOLD cases retain their actual inputs/paths and draft construction
outputs. Unsupported geometry must not gain apparently valid quantities or
an issue-ready report from its rectangular bounding box.

**E4 exit:** one deterministic verifier proves the complete output agreement
for both positive variants and the negative/held cases; rendering transports
the decision and does not grant engineering approval.

##### E5 — qualify the final candidate and hand Goal 5 a closed packet

Delivered artifacts (the original E1–E5 acceptance sequence remains above):

- Independent fixture and standard-library replay:
  `docs/verification/library-027-t-beam-member.json` and
  `docs/verification/check_library_027_t_beam_reference.py`.
- Public example/guide: `Python/examples/t_beam_member.py` and
  `docs/cookbook/python/t-beam-member.md`.
- Focused behavior/artifact tests:
  `Python/tests/integration/test_t_beam_member.py`, plus affected owner tests.
- Maintained public schemas/registries where the new contracts require them,
  and the canonical plan/handoff with exact completion evidence.

| Verification case | Required observation |
|---|---|
| Adequate main member | Every required leaf qualifies; actual paths/BBS/quantities/JSON/HTML agree; approval remains separate |
| Effective-width-limited variant | Compression uses the independently derived effective width while containment, self-weight, outline and quantities retain actual physical width |
| Web shear trap | A case that would pass if `bf` replaced `bw` fails correctly with the web width |
| Physical/anchorage failure | Material containment, cage/hooks or actual available development fails without losing the offending bars/inputs |
| Insufficient strength or SLS | The responsible check fails and the full member cannot issue; choose a service-only failure as well if the admitted route allows one |
| Missing/stale/conflicting basis | Missing flange/support/service evidence, depth conflict or stale geometry/action/detail identity cannot qualify the member |
| Unsupported profile | Nonzero torsion, hogging/L/non-monolithic or otherwise unadmitted input gets a precise unsupported/HOLD result |
| Existing regressions | Packet B section branches and force gap, ordinary 19/27-leaf workflows, D2-only HOLD and D3's documented 31-leaf PASS/FAIL/HOLD behavior remain intact |
| Installed external use | A fresh neutral base-only wheel install runs the copied example/guide, API/schema/strict-JSON round trips and positive/negative artifact verifier from site-packages |

Use one implementation writer, sequential cohesive units and bounded
independent source/output review. Run only a necessary narrow reproducer
while developing. After content freezes, batch the affected formatter/linter,
type/architecture/import checks, independent references and the union of
affected tests; use the essential changed-area checks and one final required
hosted PR cycle. Broad suites need a concrete impact/release reason, not
one run for each unit. Do not bypass required checks.

Packet E closes only after its source/reference and full-member evidence,
installed replay, output review, required checks and exact candidate/merge
tree identity are observed and the plan/tracker handoff is read back. Keep
the development-wheel identity and its limited version metadata distinct
from a published 0.27 artifact. Goal 5 then freezes and qualifies **both**
the exact versioned wheel and sdist, including E's journeys and the accepted
D3 controls, before the separate version-specific release authorization.

### Goal 5 qualify and release 0.27.0

**Current release decision — HOLD, 7 November 2026:** subsequent isolated
consumer reviews reproduced one P1 column-action defect and four P2 consumer
defects against the retained wheel. The completed qualification below is
historical evidence for its selected assertions; it is insufficient for
publication. Follow the [five-step repair plan](#027-pre-release-repair-plan)
before building and qualifying replacement archives. Planning is authorized;
this update implements no repairs and authorizes no publication.

**Initial candidate qualification — 7 November 2026:** the exact 0.27.0 wheel and
sdist are built and retained. All **18 installed profiles passed**, including
separate wheel and sdist beam/column profiles with **378 tests each**, zero
failures/errors/skips and 16 independent-checker/public-driver commands each.
The [qualified artifact record](../verification/library-0270-release-artifacts.json)
binds filenames, sizes, SHA-256, package payload, build inputs and Python tree.
GitHub owns the final immutable-head PR/Weekly checks, independent review and
integration facts. Qualification does not authorize publication.

| Evidence | Observation |
|---|---|
| Both base archive installs | Site-packages identity and all 341 package files match source; 29 UAT cases, 13 inherited family journeys and 106 numerical comparisons each pass. |
| Beam/column corpus in each archive | Three beam comparisons, all four layered-column cases, supplied shear/flange branches and force gap, four-corner x/y/tie controls, D1/D2/D3, ordinary single/multilayer workflows, T members and PR #1045 consumer regressions pass their existing acceptance assertions. |
| T-member external replay | 13 journeys per archive: two PASS, eight FAIL, three HOLD; strict APIs/schemas and JSON/BBS/HTML reconcile. |
| Reports and consumers | Required/provided steel and absent detailing survive JSON/HTML/Markdown. Seventeen inherited standalone examples and 12 public example/guide checks pass. Eight PDF outputs (16 pages) rendered and visually inspected; physical DXF, BBS and report identities agree. |
| Dependencies and performance | All declared extras, exports and transport profiles pass their stated scope; baseline performance ratios remain below the frozen 3× limit. CAD/ETABS native acceptance stays HOLD and PMM stays experimental. |
| Source preflight and repair | Initial broad run: 8972 Python passes and three source-gate failures, 626 FastAPI passes and React build PASS. Stale API/Indian-code manifests and an unrecognized explicit `angle_degrees` unit suffix were repaired at their owners. Ten focused repair checks and all 12 essential checks pass; package/build bytes are unchanged. Final full hosted evidence belongs to GitHub. |

The initially retained pair must **not** be published: the confirmed defects
occur in those bytes. Preserve its hashes, receipts and passing assertions
as the baseline. After the repairs, build one replacement pair from the
frozen candidate and qualify both archives. Only that replacement can enter
the separately authorized publication packet. No upload, tag or GitHub
Release was performed. The current public release remains 0.26.0. The
original acceptance procedure below applies to the replacement candidate.

1. Prepare one versioned 0.27.0 candidate from the merged Goals 1–4 and
   the completed beam and column closure packets. Use
   maintained version tooling, record the commit and Python tree, and
   retain one wheel and one sdist with their sizes and SHA-256 values.
   Run `./run.sh release preflight --wheel <wheel>` on the built candidate.
2. Run the required source and hosted checks and review the exact candidate.
   Use `release verify --version 0.27.0 --source wheel --wheel-dir <dir>
   --qualification --sdist <sdist> --receipt <receipt>` through `./run.sh`.
   Update the installed example inventory as needed so both clean installs
   exercise the three beam sections, the column at 900 mm and at `xu = D`,
   both beam member replays with the admission and draft controls, and
   the new section and member journeys admitted by the closure packets.
   Run the merged PR #1045 consumer regressions on both installations.
   Check required and provided steel, absent detailing, report formats,
   copied API recipes, effective-depth rejection and release guidance.
   Retain the independent numerical and artifact comparisons.
3. Check the publication surfaces and bind the qualified pair to the
   review and the version-specific owner authorization for TestPyPI, the
   exact tag, PyPI, and the GitHub Release. Use the retained-artifact
   publication procedure. Verify both files on TestPyPI before creating the
   exact tag and dispatching production. Use the qualified bytes for delivery.
4. Read back the tag commit, PyPI wheel and sdist, and GitHub Release assets.
   Verify their identities against the retained pair and run a fresh public
   identity install. Append the publication receipt to the release ledger.
   Keep install pins tied to verified registry availability.
[Current release process](../getting-started/releases.md#current-release-process-29-october-2026)
· [Retained artifact procedure](../getting-started/releases.md#retained-artifact-publication-procedure--29-october-2026)

### Five goals and acceptance

| Goal | Reuse and concrete exit |
|---|---|
| 1. [LIB-9](https://pravinsurawase.atlassian.net/browse/LIB-9) Freeze references | [Four cases frozen and replayed](../verification/library-027-comparator-reference.md#expected-values-and-acceptance), with controlled source identity, independent values, numerical tolerances and separate engine methods. |
| 2. [LIB-10](https://pravinsurawase.atlassian.net/browse/LIB-10) Promote beam comparisons | [Runnable example and guide](../cookbook/python/beam-comparator-reference.md) delivered. All seven values for each of the three sections and both method identifiers verified from the 0.26.0 wheel. The separate doubly reinforced member diagnostic retains HOLD. |
| 3. [LIB-11](https://pravinsurawase.atlassian.net/browse/LIB-11) Add column section response | [Public API and both benchmarks](#goal-3-layered-column-section-response) delivered, with a runnable example and separate member status. |
| 4. [LIB-12](https://pravinsurawase.atlassian.net/browse/LIB-12) Promote ordinary beam member | [Both member workflows and controls verified](#goal-4-ordinary-beam-member-workflows) with a public guide and repeatable artifact reconciliation. |
| Before Goal 5 | [Packets A–E delivered for their selected profiles](#beam-and-column-closure-before-goal-5), including the full T member and its installed replay. Unsupported profiles retain HOLD. |
| 5. [LIB-13](https://pravinsurawase.atlassian.net/browse/LIB-13) Qualify and release 0.27.0 | After closure. [Prepare and verify the exact candidate, then publish and verify the retained files](#goal-5-qualify-and-release-0270). |

Goal 5's initial archive qualification is complete as recorded above, but
release readiness is reopened by the confirmed consumer defects. Complete
the repair plan and replacement-archive qualification before publication.
Packet D is qualified only for its documented physical and service profile;
unsupported torsional histories retain HOLD.
There is no standalone 0.26.1 release. Candidate preparation uses the
maintained version tooling after scoped implementation and documentation
freeze. A Jira fix version is a
planning record. Keep the public installation instructions tied to the latest
verified publication. Follow the [release process](../getting-started/releases.md#current-release-process-29-october-2026)
for version-specific authorization, tags and registry delivery.

### 0.27 pre-release repair plan

**Decision and scope — 7 November 2026.** Repair the confirmed supported-route
defects before 0.27.0 publication. This is a continuation of Goal 5, with
five sequential steps and one implementation writer. The owner started
`LIB027-REPAIR-QUALIFY` on 7 November 2026 and authorized all five steps,
including replacement-archive qualification, with no publication. Checkboxes
remain open until their complete evidence is observed. The owner retains the
separate release decision. Professional approval, unsupported engineering
profiles and installed-native acceptance remain separate.

#### Ready-to-start goal — repair and requalify 0.27.0

**Goal ID:** `LIB027-REPAIR-QUALIFY`

**Status:** Started by the owner on 7 November 2026; implementation and
qualification in progress. Publication remains outside this goal.

> Repair all five confirmed pre-release defects R1–R5 within StructLib's
> agreed beam and column scope, verify the complete supported caller journeys,
> and build and qualify one exact replacement 0.27.0 wheel and sdist. Preserve
> valid existing behavior, independent engineering references and FAIL/HOLD
> controls. Finish with an evidence-bound release-ready or HOLD report and
> a reproducible handoff. Stop before TestPyPI, tagging, package upload or
> GitHub Release; publication requires separate owner authorization.

**Execution:** use the five detailed steps below,
in order, as one parent implementation goal:

1. Fix and verify the column action contract (R1).
2. Fix shared canonical/legacy report adaptation and retained evidence (R2–R4).
3. Replace and execute the complete developer quickstart (R5).
4. Qualify the actual installed caller journeys and preserve existing controls.
5. Freeze, build and qualify replacement archives, complete required hosted
   checks and reviewed integration, then issue the readiness report.

At execution start, inspect the live Git/PR state and bind the planning
candidate from [PR #1063](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1063)
before implementation. Do not assume this draft is merged. Select the current
required PR and full/cross-platform release checks from the maintained release
procedure. Keep one writer and one milestone implementation PR, with bounded
independent read-only review. Record completed steps and remaining work so a
later session resumes from observed evidence rather than restarting the goal.

**Completion requires all of the following:**

- Every R1–R5 reproduction is closed by observed behavior. The conflicting
  400 kNm/zero-end request cannot return PASS; supported canonical report
  handoffs do not crash or change the source outcome; exported reports retain
  known inputs, actual versus required steel, failure reasons and review state.
- The exact documented quickstart runs from an isolated installation with
  dependencies declared at their actual boundaries. All original selected
  A–E controls retain their expected engineering and draft/issue states.
- Both replacement archives independently pass all 18 required profiles and
  the expanded beam/column, report and guide inventory. Verify site-packages
  origin, package payload, sizes/SHA-256, source/build/verifier identities,
  independent references and supported visible exports. Keep the old pair
  unchanged as rejected baseline evidence; its passes do not qualify new bytes.
- Required checks pass on the final immutable candidate; independent review,
  merged/source-tree identity and retained-artifact verification agree. Update
  the plan, handoff and artifact record with the actual result and limitations.
- Deliver a concise readiness decision, completed-finding list, verification
  evidence and any remaining blockers. An unresolved defect or required gate
  failure keeps release HOLD. Software readiness does not confer professional
  approval, installed-native acceptance or general beam/column completeness.

**Decision boundary:** prefer structured rejection of contradictory column
actions under the current profile. If preserving a valid caller requires a
different engineering normalization, freeze its source basis and independent
expected outcomes before implementation; seek an owner decision only when
the evidence leaves a material scope choice unresolved. Do not manufacture
missing inputs or promote unsupported profiles to PASS to finish the goal.

**Excluded:** new reinforcement arrangements or stable actual-bar P–M–M,
broader beam member profiles, new serviceability/detailing combinations,
slab/footing implementation, licensing reconsideration and publication.
The detailed repair steps and exclusions below remain the acceptance owner.

**Execution checkpoint:** R1's bounded end-envelope rejection and field-path
contracts pass their focused Python/canonical/HTTP regressions; independent
review accepted the rule. R2–R4 share the new explicit report projection,
including the retained scalar compatibility protocol and missing-check
status precedence; affected focused checks and independent review pass.
The base developer journey now executes. Optional output and replacement
archive replays, final candidate checks and release-readiness acceptance
remain pending. No replacement artifacts have been qualified at this checkpoint.

The first replacement at `423097e8` passed all 18 initial expanded profiles
and local preflight (9007 Python / 629 FastAPI passes), but a further R2
negative control exposed conflicting legacy aggregate/strength envelopes.
It is retained as intermediate evidence and is not selected for publication.
The repair now preserves the original calculation envelope separately,
reports the aggregate FAIL and detailing reason, and keeps its unminted
aggregate identity unavailable. Requalification must include this control.

The reviewed baseline is merged PR #1062,
`1c35d9485fa3499e69f1926657e91e84fe0d7bb8`. The retained wheel SHA-256 is
`cfbbc47b5ada59011ef0c4c9049781e8e30cbc9c341ef8eb8a813244139f3a79`.
An independent replay verified all 341 installed package files against that
wheel. The same package payload is present in the retained sdist; that
identity does not substitute for executing each replacement archive.
The [artifact record](../verification/library-0270-release-artifacts.json)
retains the initial evidence and records the publication hold.

#### Confirmed defects to close

| ID | Priority and observed main-process failure | Owning boundary and required correction |
|---|---|---|
| R1 | P1: slender rectangular column accepts `Mux=400 kNm` and zero signed end moments, checks `Mux_design=20 kNm`, and returns PASS. Equal 400 kNm ends or omitted legacy ends instead check 420 kNm and FAIL. The canonical facade also accepts the conflicting case. | `services/column_api.py`, `services/contracts/family_f1.py`, `design/is456/column.py`, and affected HTTP contracts. Define and enforce one action contract before dispatch to `codes/is456/column/long_column.py`; no admitted governing demand may disappear. |
| R2 | P2: canonical beam design/detail returns PASS with nine BBS rows, but `reports.generate_html_report` renders FAIL with both fallback and Jinja2. `api.generate_calculation_report` raises a missing `geometry` attribute error. | `reports/generator.py` and `services/calculation_report.py` use legacy shape guesses. Add explicit canonical-result adaptation shared by the report surfaces; preserve existing supported legacy routes. |
| R3 | P2: accepted design-only reports lose retained geometry, materials and actions; combined reports still lose actions. JSON inputs are incomplete and HTML/Markdown show unavailable known values. | The calculation-report input projection and renderers must retain the calculation basis, explicit units and provenance, rather than inventing defaults for absent inputs. |
| R4 | P2: an evaluated deflection failure survives only as an overall FAIL. `failed_checks`, serviceability results, governing values/limits and review status disappear from report projection/rendering. | The same explicit adapter must retain evaluated check evidence and reasons. Preserve unevaluated checks as unevaluated and engineering review as required. |
| R5 | P2: the actively linked developer quickstart fails immediately on `beam_id`; its later attributes, BBS, DXF and report recipes also target retired contracts. | Replace the complete journey in `docs/developers/platform-guide.md` using maintained canonical operations and verify the actual documented block from an installed archive. |

Raw isolated-review evidence remains in the review worktrees under ignored
`output/independent-review/` and `output/extended-review/`; the durable trigger,
owners and required outcomes are recorded here. Passing existing tests do
not close these counterexamples. No new repository tests were added during
the reviews.

#### Step 1 — reconcile column actions (R1)

- [ ] Specify per-axis semantics for applied first-order moment magnitudes
  and signed end moments, their sign/order rules, omission/default behavior,
  and the role of minimum eccentricity. Distinguish an end-moment-only profile
  from an independent interior peak or an already amplified action.
- [ ] Prefer structured rejection of contradictory/unsupported combinations
  for this repair. If a normalization is selected instead, freeze its
  engineering basis and independent expected outcomes before changing the
  calculation. Merely taking a maximum or changing the printed result is
  insufficient evidence of a correct second-order check.
- [ ] Enforce the rule at the shared service boundary, with matching canonical
  validation and HTTP field/error contracts. Keep low-level signed-curvature
  calculation ownership and explicit units intact. Record rejected field
  paths and preserve accepted action provenance.
- [ ] Verify the exact 300 × 450 mm, M25/Fe415, 2400 mm² supplied-steel,
  50 mm centroid-depth case: Pu=500 kN, braced hinged ends, 6000 mm unsupported
  length, Mux=400 kNm, Muy=0 and all explicit ends zero must never produce
  PASS. Omitted legacy ends and equal 400 kNm x ends must retain the verified
  420 kNm/FAIL outcome under the existing model.
- [ ] Add x/y and axis-swapped checks, same/opposite curvature, sign reversal,
  ordering, explicit zero versus omitted fields, partial legacy end inputs,
  short/slender boundary and minimum-eccentricity controls. Replay affected
  direct service, canonical load/check/schema, and HTTP routes. Reuse the
  existing long-column reference and contract tests; add regressions for
  the confirmed demand-loss path, not duplicate formula implementations.

**Exit:** accepted actions, design moments and status agree in every selected
route; conflicting actions produce the documented structured intake outcome.
Any change to numerical conventions requires its own independent reference.

#### Step 2 — one explicit report projection (R2, R3, R4)

- [ ] Inventory the documented report producers/consumers. Handle canonical
  `BeamDesignAndDetailResultV1`, legacy combined results and design-only
  compliance results by explicit type/schema adapters; reject unsupported
  objects with a clear error. Reuse one normalized projection across HTML,
  fallback HTML and calculation-report JSON/HTML/Markdown/PDF surfaces.
  Keep existing raw canonical JSON exports and their versioned envelope.
- [ ] Preserve member/story/case identity, geometry, materials, Mu/Vu/Tu,
  effective-depth basis and supplied detailing. Known retained values must
  survive; missing cover/span/detailing remain explicitly unavailable.
  Preserve required versus actually provided steel and actual bars/BBS
  without deriving provided steel from a requirement or filling defaults.
- [ ] Preserve intake/calculation/engineering/review states, issues,
  `failed_checks`, evaluated deflection/cracking/torsion evidence, governing
  values, limits, sources and unevaluated/HOLD reasons. Show the responsible
  check beside an overall failure. Do not recalculate engineering status
  from absent legacy `is_ok` keys.
- [ ] Verify the canonical PASS plus nine-row BBS reproduction, design-only
  success with absent detailing, a real detailing failure, strength FAIL,
  serviceability-only FAIL, and the existing missing-evidence HOLD cases.
  Use the accepted legacy compliance route for the evaluated serviceability
  reproduction. Canonical automatic detailing after explicit serviceability
  currently retains `SERVICEABILITY_DETAILING_SCOPE_HOLD`; this packet does
  not add a combined serviceability/detailing engineering workflow.
  The frozen deflection control uses 300 × 500 mm, d=444 mm, M25/Fe500,
  Mu=150 kNm, Vu=100 kN, span=10000 mm and tension-steel modification factor
  0.5: retain `failed_checks=['deflection']`, L/d=22.5225225 and allowable=10.
- [ ] Check content agreement across JSON, HTML, Markdown and supported PDF;
  exercise base-only fallback and the `[report]` renderer separately. Render
  and visually inspect representative PDF pages. Preserve qualified-review
  requirements and draft/issue readiness independently of a calculation PASS.

**Exit:** supported producers reach their advertised report surfaces without
crashes or invented status, and a reviewer can identify the inputs, actual
reinforcement and reason for every evaluated FAIL/HOLD.

#### Step 3 — repair the complete active quickstart (R5)

- [ ] Replace its design-through-export blocks using
  `design.is456.beam.load`/`design_and_detail`/`bbs`, reusing the maintained
  `Python/examples/canonical_workflows.py` input and detailing conventions.
  Update the whole stale journey, including later result attributes,
  compliance, BBS, DXF and report instructions.
- [ ] Keep base installation sufficient for the canonical calculation, BBS
  and supported JSON exports. Label and verify DXF/report/PDF dependency
  extras at their actual boundaries. Show canonical HTML only after Step 2
  supplies the supported adapter; distinguish it from raw JSON export.
- [ ] Execute the exact guide blocks in a fresh neutral directory and verify
  input/result identities, engineering/review state, nonempty BBS and matching
  exported quantities. Confirm README/docs/developer index links still lead
  to the corrected route and installation instructions use verified versions.

**Exit:** a new user can copy the documented main journey end to end without
source-checkout imports, retired arguments or undocumented result conversions.

#### Step 4 — qualify the repaired caller journeys

- [ ] Add the confirmed reproductions and exact guide recipe to the maintained
  release driver inventory in `scripts/_lib/release_beam_column.py` and its
  required transitive inputs. Copy only drivers/fixtures, never package source
  or repository `conftest.py`, into isolated installed verification.
- [ ] Exercise the affected API/schema/HTTP error paths and report formats;
  compare accepted requests, calculation/check states, BBS and exports by
  values and identity rather than snapshot text or a lack of exceptions.
- [ ] Obtain bounded independent read-only review of action semantics and the
  producer-to-report handoff. Preserve all original A–E numerical references,
  ordinary/multilayer member journeys, D2-only HOLD, D3 scope controls and
  T-member PASS/FAIL/HOLD outcomes. Unsupported profiles retain their limits.
- [ ] After all scoped content freezes, run the union of focused tests,
  affected formatting/lint/type/architecture checks and essential changed-area
  validation once. Repair only outcome-changing defects and rerun their
  affected evidence. Integrate the units in one milestone PR; no separate
  release or broad verification cycle per internal unit.

**Exit:** every R1–R5 reproduction is closed by observed behavior, required
consumer journeys pass, and no selected engineering control loses its status.

#### Step 5 — replace artifacts and repeat the release decision

- [ ] Freeze the repaired versioned source/build inputs and expanded verifier
  inventory. Because 0.27.0 is unpublished, retain that version while building
  a new wheel and sdist. Record new sizes, SHA-256, Python tree, verifier/input
  hashes and environments; preserve the old pair as rejected baseline evidence.
- [ ] Run all 18 required profiles against the new exact pair, including the
  expanded beam/column corpus from both wheel and sdist, independent references,
  copied guides and report controls. Run base-only and optional-extra paths in
  their declared environments. Previous profile passes cannot be carried over
  as passes for changed bytes.
- [ ] Use required hosted PR checks and the final full/cross-platform release
  verification on the immutable candidate. The concrete broad-check reason is
  the changed shared column intake and report projections across existing
  callers; do not duplicate the full suite after each repair unit.
- [ ] Bind independent review, final checks, merge/tree identity and retained
  artifact check. Update this plan, handoff and artifact record with an observed
  readiness verdict. An unresolved R1–R5 defect or required gate failure keeps
  publication HOLD; do not describe planned checks as completed evidence.
- [ ] Only after readiness and separate version/target-specific owner
  authorization: TestPyPI verification, exact tag, same-byte PyPI/GitHub Release
  delivery and public hash/installation readback under the maintained procedure.

**Exit:** an exact replacement pair has observed release evidence and an honest
readiness decision. Publication remains a distinct authorized action.

#### Features outside this repair packet

The comparison review's proposed eight-bar then oriented six-bar physical
columns, qualified actual-bar P–M–M, broader L/hogging/continuous beam member
profiles, splices/cutoffs and circular columns remain unselected extensions.
Do not promote helper existence into complete-member support or general
beam/column completion. The supported 0.27 result is a bounded IS 456 beta
with its documented profile limits. This plan does not move the approved
0.28 slab/footing theme or reopen permission for normalized IS code data.

### Later release themes

For 0.28, first compare one solid one-way slab and one concentric isolated
footing. Preserve the continuous one-way, two-way, combined and strap cases as
regressions. Compare selected checks on matching model and source assumptions.
Keep raft and pile-cap source and benchmark HOLDs visible.

For 0.29, choose one bounded next family, such as a straight-flight stair or
braced axial wall, once its independent benchmark and installed user journey
are ready. Installed native-host work retains its own evidence and sequencing.
The [October Jira plan](https://pravinsurawase.atlassian.net/browse/LIB-1)
retains its original readiness and conditional torsion history.

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

## Next-version proposal — 6 October 2026

**Type:** Plan

**Audience:** Library owner, developers and engineering reviewers

**Status:** Draft proposal; planning requested, implementation scope not selected

**Importance:** High

**Created:** 2026-10-06

**Last Updated:** 2026-10-06

### Recommendation and intended user outcome

Plan **v0.26.0: accuracy and professional quality** around dependable supported
workflows. A user should be able to install one exact version, supply explicit
engineering inputs, obtain an honest calculation outcome, inspect its basis,
and carry the same result through JSON, assessment, BBS and reports.

The mandatory candidate consists of the confirmed repairs below, numerical
evidence for affected calculations, clearer caller contracts and consistent
outputs. The highest-value proposed engineering addition is one bounded
supplied rectangular member with concurrent bending, shear and torsion. Admit
that addition only through the existing LIB-3 → LIB-4 evidence sequence.

The version number is provisional. An additive public capability supports a
minor release; if the selected deliverable contains only compatible repairs,
use a patch release such as v0.25.1. Freeze the number before candidate and
artifact preparation. This proposal does not authorize implementation, a tag,
publication or professional approval, and does not revoke earlier approvals.

### Current baseline and reused authority

The [latest GitHub release](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.25.0)
and [PyPI package](https://pypi.org/project/structural-lib-is456/0.25.0/) were
checked on 6 October 2026: v0.25.0 was published on 3 October. The fetched
`origin/main` and clean local intake both resolve to
`eb6f8b51988a3f9b26a10f07164aa958309d0d84`. Git-state `remote_freshness` remains
`NOT_CHECKED`; the separate successful fetch and live release readback provide
the dated remote evidence. No newer runtime change is assumed.

Reuse these existing owners:

- This document owns caller quality and the accepted single/multilayer member
  work. Earlier dated observations remain historical; the September finding of
  no repair to queue is superseded by the consumer reproductions below.
- [Supported-scope completion](../verification/library-supported-scope-completion.md)
  and [amendment impact](../verification/is456-amendment-impact.md) own accepted
  corrections and unresolved source/material/applicability qualification.
- [LIB-PRO-015](lib-pro-015-professional-api-and-documentation-renewal-plan.md)
  supplies reference/migration patterns. Its August inventory is historical;
  completed facade documentation and typed-builder work must not be repeated.
- [LIB-1](https://pravinsurawase.atlassian.net/browse/LIB-1) through
  [LIB-6](https://pravinsurawase.atlassian.net/browse/LIB-6) retain the existing
  readiness → torsion evidence → physical member → delivery sequence.
  LIB-2 readiness is present in the released source and
  [public example](../../Python/examples/member_readiness_workflow.py).
  Jira still reports all six tickets as To Do, with LIB-2's description saying
  not started. Reconcile that mismatch against delivery evidence before using
  tracker state to choose implementation; do not rebuild LIB-2.

Keep the 13 existing family journeys and their individual supported/advanced/
held classifications. The earlier consumer audit reproduced 11 PASS journeys,
one intentional FAIL and one intentional HOLD; those outcomes are retention
controls, not complete numerical qualification of every family.

### Mandatory corrections, in outcome order

| ID / priority | Confirmed main-process defect and root cause | Maintained owner | Required corrected outcome |
|---|---|---|---|
| Q-F01 / P0 | An admitted overloaded beam reaches engineering FAIL, but compliance produces infinite utilization and canonical output raises `CalculationError`. Reproduced on 6 October with `mu_knm=2000`, `vu_kn=75`, 300 × 500 mm, `d_mm=457`, M25/Fe500. | [Compliance](../../Python/structural_lib/codes/is456/compliance.py), [shear](../../Python/structural_lib/codes/is456/beam/shear.py), [canonical beam result](../../Python/structural_lib/services/canonical_beam.py) | Valid FAIL/HOLD remains inspectable and serializes as standards-compliant JSON with a typed unavailable value/reason where a ratio is undefined. Preserve the decisive status and issues; never clamp to PASS or permit Infinity/NaN. Review compatibility before selecting the representation. |
| Q-F04 / P0 | `smart` accepts pipeline JSON but reads nested geometry/materials as flat fields, substituting defaults. Reproduced on 6 October: supplied 444 mm depth/40 mm cover become 450 mm/30 mm; generated bars need 454 mm. | [`cmd_smart`](../../Python/structural_lib/__main__.py) and the existing [pipeline result owner](../../Python/structural_lib/services/beam_pipeline.py) | Consume the maintained result/deserializer and retain member identity, geometry, material, actions, reinforcement/depth and source basis. Reject unsupported schema or absent required facts before recalculation; do not silently invent design inputs. |
| Q-F02 / P1 | The shipped five-beam CSV fails at the first generated layout: strength depth 460 mm versus bar centroid 444 mm. Reproduced on 6 October. The earlier beginner replay failed for the same reason. | [Sample CSV](../../Python/examples/sample_beam_design.csv), [quickstart](../getting-started/python-quickstart.md), [depth binding](../../Python/structural_lib/services/beam_detailing_binding.py) | Every advertised starter case completes its promised design/detail/BBS/export journey using internally consistent inputs. Keep effective-depth validation; use explicit supplied or derived depth with the actual reinforcement basis. |
| Q-F03 / P1 | The current quickstart installs base 0.25.0 but three optional/Colab commands pin 0.24.0 and its sample link points to that older tag. Reconfirmed in current source on 6 October. | [Quickstart](../getting-started/python-quickstart.md) and maintained release/version generation | Base, extras, Colab, example links and publication statements agree on the selected candidate. Resolver replay retains its exact version; fix the maintained generation/check boundary where it owns these pins. |
| Q-F05 / P1 | The consumer audit's rendered PDF clips the section-depth label. Current SVG still places the label at x=264 inside a 300-wide viewBox, with no reserved annotation width. | [Report SVG](../../Python/structural_lib/services/report_svg.py), [report service](../../Python/structural_lib/services/report.py) | Dimension labels and units are fully visible in rendered HTML/PDF at ordinary size. Bind the candidate visual check to the actual exported file. The earlier PDF observation and present source binding are evidence; a fresh PDF replay is still required during implementation. |

The October consumer audit was an installed-package exercise on one Mac with
Python 3.11.15. It supplies concrete triggers, not whole-library acceptance.
The present planning pass reproduced Q-F01/Q-F02/Q-F04 and inspected current
Q-F03/Q-F05 owners. No implementation repair or new test was made in this pass.

### Milestones and acceptance

Use one implementation stream and one release scope. Responsible roles below
are ownership requirements, not staffing assignments or agent-spawn requests.

| Milestone | Deliverable and role | Measurable exit | Dependency |
|---|---|---|---|
| Q0 — Freeze the candidate scope | Owner and implementer bind the version, touched workflows, maintained callers, source editions/amendments, compatibility and unresolved holds. | Every selected change has an owner, reproducer or explicit product requirement, acceptance row and focused command. Retain completed work; reconcile LIB-2/LIB-5 delivery history without duplicating tickets. | Scope selection; current baseline above. |
| Q1 — Correct result and assessment flow | Implementer fixes Q-F01/Q-F04 at their existing calculation/result/adapter owners. | Nominal PASS, valid engineering FAIL/HOLD and invalid-input rejection retain distinct outcomes across affected Python/JSON/CLI/HTTP callers. `smart` receives the exact original engineering basis or rejects it explicitly. | Q0. |
| Q2 — Make first use and outputs dependable | Implementer/documentation owner completes Q-F02/Q-F03/Q-F05 and their maintained generation/check paths. | Unedited advertised examples finish their promised journeys; extras keep the candidate version; emitted BBS/drawings/reports agree on member, bars, dimensions and status; all required labels are visible. | Q1 for producer/consumer fixtures. |
| Q3 — Qualify affected engineering behavior | Engineering evidence owner freezes and checks independent references for any numerical or applicability change. | Every changed engineering branch has exact source/case identity, independent expected values, justified tolerances, nominal/boundary/failure controls and an explicit verdict. Unchanged accepted benchmarks remain controls; disagreement is resolved at the calculation owner. | Frozen Q1/Q2 calculation behavior. |
| Q4 — Improve professional consumption | Implementer/documentation owner extends existing contracts and reports only for selected caller needs below. | Selected public operations have accurate typed signatures, field basis, limitations, error/status examples and executable help. A result explains which checks ran, failed or were held and why; transport/export preserves its input and source identity. | Q1–Q3; demonstrated caller gaps. |
| Q5 — Deliver the exact candidate | Release owner assembles migration/examples, reviewed candidate and artifact evidence using the existing release workflow. | Required hosted checks pass on the reviewed head; clean installed wheel reproduces promoted journeys and failures; source/wheel/sdist/tag/index identity matches; release authorization is recorded for this version. | Q1–Q4; optional feature only if admitted. |

Q1/Q2 are mandatory fixes. Q3 is an accuracy gate for affected scope. Q4 is
selected product completion, not a repository-wide API rewrite. Q5 retains
the repository's software-release and professional-review distinction.

### Additional points worth including

Select these as user-facing improvements to existing owners, rather than
inventing more calculation wrappers:

1. **A coherent calculation dossier.** Carry input/depth basis, load role,
   governing case, source/method revision, actual supplied reinforcement,
   required/provided values, per-check verdict and review state from the
   existing result to JSON and the report. Reuse current member/reporting
   contracts. Add a projection only when a real consumer loses a required fact.
2. **Actionable readiness and failures.** Surface the existing missing-input
   and unsupported-profile diagnostics beside each requested member. Preserve
   supplied zero versus absent, assumption versus source fact, and current
   versus stale result. Every requested member remains accounted for.
3. **One dependable recommended entry path.** Keep
   `structural_lib.design.is456.<family>` for new integrations. Generate
   reference/examples from the selected live contracts, document migrations,
   and retain compatibility calls. Do not revive historical documentation debt
   already closed by PRs #1006–#1010.
4. **A shipped worked accuracy case.** Extend existing ordinary/multilayer
   examples with the selected source-bound comparison and artifact receipt.
   A user can replay the same inputs and inspect how the result was checked.
   A worked case does not grant a general support or professional-use claim.

A small runtime baseline should accompany any claimed performance improvement:
same machine/runtime, input, process boundaries and before/after distribution.
Do not optimize unmeasured code or add dependencies to meet an invented target.

### Conditional engineering addition: concurrent bending, shear and torsion

Reuse [LIB-3](https://pravinsurawase.atlassian.net/browse/LIB-3) to freeze one
ordinary non-seismic rectangular supplied member with single-layer aligned
longitudinal bars and actual closed links, using concurrent same-row M3/V2/T.
Source/method, units/axes/signs, ranges, both faces, torsional support/load path,
serviceability, anchorage/continuity, bar fit and construction outputs must all
have an accepted applicability and evidence basis.

After accepted LIB-3 evidence and separate implementation selection,
[LIB-4](https://pravinsurawase.atlassian.net/browse/LIB-4) may carry that member
through existing strength, physical bars/paths, BBS, quantities and report.
Keep the existing operation/leaf owners; a second torsion wrapper adds no
value. Retain exclusions for axial, weak-axis/biaxial action, arbitrary layouts,
splice/cutoff cases, changed stiffness and automatic search expansion.

Exit requires an independently reviewed complete required-check matrix,
finite PASS/FAIL/HOLD transport, physical bar/BBS/report agreement and exact
installed-wheel replay. If any essential source, SLS, support or physical
obligation remains missing, record HOLD with resolver and resume condition;
do not advertise a completed torsion member or make it block delivery of the
separately selected mandatory quality repairs.

[LIB-5](https://pravinsurawase.atlassian.net/browse/LIB-5) supplies examples and
migration evidence for the actual selected scope, extending what v0.25.0
already shipped. [LIB-6](https://pravinsurawase.atlassian.net/browse/LIB-6)
remains a separate conditional installed force/station pilot.

### Focused verification and release gates

Implementation packets complete code, tests, documentation and intended output
changes before one affected verification batch. The following existing owners
provide starting commands; Q0 narrows test nodes and adds meaningful regression
cases for the confirmed defects during implementation, not during this plan:

```bash
# Q1: finite result semantics and faithful producer/consumer composition
./scripts/python_runtime.sh -m pytest --no-cov -q \
  Python/tests/unit/test_compliance.py \
  Python/tests/integration/test_canonical_beam_facade.py \
  Python/tests/integration/test_canonical_transport_contract_v1.py \
  Python/tests/integration/test_cli.py \
  Python/tests/integration/test_smart_designer.py

# Q2: depth binding and generated output behavior
./scripts/python_runtime.sh -m pytest --no-cov -q \
  Python/tests/integration/test_job_cli.py \
  Python/tests/integration/test_cli_report_regression.py \
  Python/tests/test_report_svg.py

# Q4/Q5: current generated examples, documentation and changed-area checks
./scripts/python_runtime.sh scripts/generate_family_facade_docs.py --check
./run.sh check
```

Render and inspect the affected PDF/drawing; text extraction cannot prove
visible annotations. Extend existing independent benchmarks only where a
selected numerical branch or support claim changes. Freeze tolerances before
comparison, disclose shared reference lineage, and preserve failures. Run the
union of affected tests once on the final integrated candidate and required
hosted checks once per candidate; repeat affected evidence after a repair.

At release freeze, run the broad Python regression suite once for the concrete
risk of shared result/serialization and engineering-owner changes across
families. Use existing source/artifact verifiers for all 13 retained journeys,
their negatives and the repaired caller examples. Prove installed `site-packages`
origin without repository import paths, including affected CLI/HTTP adapters
and selected extras. Independent-reference acceptance and visible export
checks remain necessary even when all tests pass.

Use existing release preflight, exact-wheel verification and publication-surface
checks with the chosen version. Bind review, required checks, TestPyPI, final
wheel/sdist hashes, owner authorization, merge/tag and PyPI/GitHub readback to
the exact candidate. A normal software release does not imply qualified
structural-engineering review; any professional-use claim needs the separate
frozen-scope qualified review and recorded acceptance.

### Scope, delivery order and next decision

Solver continues to own structural analysis; Library owns member design,
reinforcement/detailing and construction outputs. The six-phase beam/ETABS
programme and separate XLL learning/product track keep their own authority.
This release proposal adds no new code family, steel design, general building
solver, global optimization, ETABS model mutation, UI redesign or installed
Excel/XLL qualification. Current source/amendment/material/host holds remain
visible. Owner permission for required normalized IS data and public
distribution is already recorded; do not reopen that permission gate.

The [draft 50-day plan PR #1019](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1019)
is still open, based at `96170d81`, head
`d8ca7ff99491237bbed34c0e5b6900575b5b5bed`. Its six paths include this document
and its calendar/capacity decisions remain unconfirmed. This proposal preserves
that draft and selects no dates or daily capacity. Before publishing/integrating
an overlapping planning packet, integrate the predecessor or explicitly replan
and rebind the affected candidate to current main. This planning branch does
not authorize merging or closing #1019 or disposing of another worktree.

Recommended execution order: **Q0 → Q1 → Q2 → Q3 → Q4 → Q5**. LIB-3 evidence
can be prepared once selected; LIB-4 enters only after its evidence gate.
The inherited LIB-3/LIB-4 estimate is 14–25 active human engineering workdays,
with low confidence and external waits excluded; it is not Codex elapsed time
or a calendar commitment. Estimate the mandatory quality scope after Q0 names
the affected callers and required independent references; do not reuse the
unconfirmed 50-day schedule as a release promise.

The next owner decision is concrete: select the mandatory quality candidate
and Q4 additions, then decide whether to prepare LIB-3 evidence for this minor
release or retain the torsion member as a later gated extension. Implementation
and per-version release authorization remain later decisions. The present
deliverable is the completed proposal and its planning validation.

## Professional standards programme — 8 October 2026 (revision 2)

The next version should be dependable for a developer, an engineer and an
automated caller from installation through an inspectable result. This revision
expands the six-milestone proposal above into a whole-library quality programme:
public APIs, signatures, admission, schemas, errors, documentation, examples,
coding practices, engineering qualification, physical outputs, adapters,
packaging and release evidence. It retains Q-F01–Q-F05 and the separately gated
LIB-3/LIB-4 extension. **S0–S6 below are the current execution sequence**;
Q0–Q5 remain the earlier proposal and its reusable defect details.

Candidate version **0.26.0 is provisional**. A compatibility review determines
whether the selected changes fit that version and whether a schema migration
is required. No date, capacity, new code family or professional-use approval is
implied by this plan. Existing accepted capabilities should be made more
reliable before adding another advertised workflow.

### Applicable standards and authority

“All standards” means a declared, applicable profile with an evidence boundary,
not a claim of universal certification. S0 expands the register whenever a
maintained consumer, supported platform or selected engineering claim adds a
relevant obligation. Evaluate both the written obligation and the actual
main-process behavior. Classify a confirmed defect, an approved compatibility
exception, an advisory practice and an untested claim separately.

| Authority | Application and evidence |
| --- | --- |
| Repository contract | [AGENTS.md](../../AGENTS.md), maintained path rules, control plane, canonical documentation registry and Git workflow govern execution and architecture. Reconcile subordinate active guides; do not follow obsolete examples as authority. |
| Python practices and typing | [PEP 8](https://peps.python.org/pep-0008/), [PEP 257](https://peps.python.org/pep-0257/) and the [typing specification](https://typing.python.org/en/latest/spec/) inform configured style, public annotations and useful documentation. Record project exceptions. Retain the current rendered NumPy docstring convention rather than rewriting valid documentation for style alone. |
| Public HTTP and JSON | Check the actual emitted [OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0), [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) and [RFC 8259 JSON](https://www.rfc-editor.org/rfc/rfc8259) boundaries. Schema validity, instance admission and engineering meaning are three separate checks. |
| Packaging and compatibility | Apply [PyPA project metadata](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and [version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/), the current API taxonomy and the explicitly declared project compatibility policy. A snapshot update alone does not approve a breaking change. |
| Engineering sources | Freeze applicable IS editions/amendments, clauses/tables, cases, assumptions, limits, units and tolerances per promoted claim. Preserve provenance and independent reference lineage. Software checks do not establish qualified engineering acceptance. |
| Distribution and release | Required normalized IS data/public-distribution permission is already passed in the [owner record](../verification/is456-public-distribution-permission.json). Exact-candidate release authorization, engineering acceptance and installed/native-host acceptance retain their separate gates. |

### Current assessment and what it proves

The assessment is bound to released **v0.25.0**, source
`eb6f8b51988a3f9b26a10f07164aa958309d0d84`, and planning head
`7f1429501bb30d69b51b8833b84d10d65a551423`. The release was rechecked live;
the current source contains the same library implementation. The branch has
only planning changes at intake. A completed fetch is recorded separately;
the Git-state receipt still labels remote freshness `NOT_CHECKED` and must not
be represented as fresh-remote proof.

The durable [assessment JSON](../verification/library-professional-standards-20261008.json)
records commands, scopes, hashes, results and limits. Its six-root guidance
inventory contains **127 files, including 118 Markdown documents and 705 Python
fences**. Inventory is complete for those named roots, while semantic review
was targeted. Instructions, skills, CI and registries were inspected separately;
S0 must finish the applicable-authority census, including release, security and
platform guidance outside those roots. Do not call all 705 cells executed or
all documents semantically accepted.

| Assessment | Observed result | Practical limit |
| --- | --- | --- |
| Configured formatting, lint and typing | Black: 325 files unchanged; Ruff: zero diagnostics; mypy: 325 source files pass. | Configuration-bound software checks; not proof of mathematical accuracy. |
| Four-layer imports | Architecture check passes over 268 files: 31 core, 87 IS-code, 89 services, 61 UI. | Static boundary check, not every runtime path. |
| Additional code controls | Custom annotations: 217 files / 1,950 functions pass. Function-quality scanner: 89 decorated functions, zero mandatory failures, 401 advisory observations. | The custom annotation subset is smaller than mypy's population. Advisory observations are not 401 defects; the scanner does not qualify every calculation. |
| Standalone examples | All 17 current scripts exit successfully for their recorded invocation and scratch outputs. | Not every internal branch, the CSV job CLI or an independent engineering benchmark. |
| Canonical family recipes | All 13 current positive round trips and their declared invalid cases pass the maintained verifier; intentional two-way slab FAIL and staircase HOLD remain visible. | One negative per recipe is not complete input admission coverage or new support authorization. |
| Published copy-paste pages | 12 of 13 pages pass; 26 of 27 sequential Python cells pass. The beam engineering FAIL cell raises `CalculationError` for `inf`. | This is a fresh main-process failure, Q-F01. Generation consistency had passed without executing this failing cell. |
| Public API inventory | 11 family modules / 60 function projections; 245 compatibility exports / 115 functions; 14 classified surfaces / 1,308 projections. | Projections are not 1,308 separately promoted end-user workflows. |
| Signature policy | 32 compatibility functions exceed the guide's three-positional-parameter rule. | Classify retained exceptions or migrations; do not break legacy callers to satisfy a style rule. No numerical defect follows from this count. |
| HTTP/schema inventory | 92 operations, 91 paths, 487 component schemas; all 487 pass Draft 2020-12 meta-validation and the maintained snapshot matches. | Meta-validation does not prove units, admission semantics, response meaning or compatibility. WebSocket evidence is separate. |
| HTTP documentation signals | 12 operations lack descriptions; 3,054 of 3,955 direct component properties lack descriptions; 146 have an inline example. | Inventory signals to triage by field/consumer role, not counts of confirmed calculation defects. |
| Existing contract checks | API binding and compatibility checks pass. Legacy schema snapshots cover five models and two enums. 32 React production callsites in 12 files match path/method. Twelve focused transport tests pass. | Snapshot/path checks and 12 tests do not establish full semantic or runtime parity across every HTTP operation. |
| Guidance structure | Metadata, indexes, instruction composition and local links pass; 606 Markdown files / 1,847 local targets, zero broken targets in that check. | Active guide contradictions survive these structural checks. |

This assessment did not rerun the broad Python/FastAPI/React suites, install a
new wheel, qualify native Excel/ETABS/XLL execution, run candidate hosted checks,
or obtain qualified professional acceptance. The older consumer PDF is bound
to its original audit and present source; a fresh affected PDF remains required.
The caller ledger was stale at intake because the 6 October plan added a
maintained reference. Regenerate that derived record after this planning packet
freezes; this is documentation consistency, not a runtime API migration.

### Findings and dispositions

Reuse the five confirmed consumer issues [above](#mandatory-corrections-in-outcome-order)
at their existing root-cause owners. Q-F01 and Q-F04 are P0 because a legitimate
engineering outcome becomes uninspectable or the caller's design basis changes.
Q-F02, Q-F03 and Q-F05 are P1 first-use/output defects. Never fix them by
weakening effective-depth checks, allowing non-finite JSON or hiding FAIL/HOLD.

| Additional item | Classification and consequence | Planned closure |
| --- | --- | --- |
| PS-F06 — active coding guide contradicts architecture/execution | P1 confirmed guidance conflict. [Agent coding standards](../contributing/agent-coding-standards.md) says three layers and routes to retired UI paths; it also presents unbound commands and mutating validation. This can send the main implementation process to the wrong owner. | Reconcile this canonical guide with four-layer ownership, runtime binding and scoped frozen verification. Classify illustrative templates; current command examples must execute in their declared directory. |
| PS-F07 — public stability guide conflicts with current API | P1 confirmed guidance conflict. [Library Contract](../reference/library-contract.md) is active, calls the library beam-only/production-ready and recommends older orchestration entrypoints, while [current API levels](../reference/api-levels.md) promote typed family facades. | Establish one current support/version/compatibility policy and label historical v1 aspirations. Every recommended entrypoint must agree with the maintained classification and declared release channel. |
| PS-O01 — signature deviations | Policy deviations, not automatically runtime defects. Existing callers may rely on positional forms. | For all 32, choose a retained documented exception or a separately reviewed migration; new promoted signatures follow the selected standard. |
| PS-O02 — operation/property documentation gaps | Measured inventory; missing prose alone is not an engineering failure. | Prioritize fields whose undocumented units, roles, defaults or admissibility can change the caller's result. Reuse shared schema descriptions where appropriate. |
| PS-O03 — legacy coercion | A wall HTTP model accepts a numeric string and converts it to a float; canonical strict admission is not universal. No wrong result was demonstrated by this observation. | Declare strict/coercing policy per boundary and test semantically meaningful cases. Preserve supported legacy conversion through an explicit adapter if selected. |
| PS-O04/05 — assurance controls overstate their reach | Generated recipe checks pass while the promoted FAIL cell crashes. Snapshots detect drift; route matching does not prove payload meaning; decorated scanners cover a subset. | Tie each public claim to an executing outcome gate and publish the checked population. Avoid calling a narrow check whole-library acceptance. |

### Eighteen areas with measurable candidate gates

Every area needs an accountable named person at S0; the role below identifies
the maintained owner, not a new service or mandatory agent process. `PASS`
requires its selected scope and evidence. `PARTIAL`, `FAIL`, `HOLD` and
`NOT_RUN` must remain visible. Do not report an overall percentage that averages
away a P0 defect or an engineering hold.

| ID / area | Accountable role and priority | Acceptance on the selected candidate |
| --- | --- | --- |
| PS-01 — authority and guides | Governance/documentation; P1 | All applicable active guidance is inventoried with owner, authority and current/historical disposition. Resolve outcome-changing conflicts and link one maintained source for each rule. Include scoped instructions, workflow skills and platform/release guides. |
| PS-02 — API ownership/discovery | API owner; P1 | Every maintained public projection maps to its canonical owner, intended consumer and support class. Every promoted journey has a complete callable recipe and one authoritative reference. Keep compatibility/internal helpers clearly scoped. |
| PS-03 — signatures/units/typing | API and compatibility; P1 | Compare callable signature, manifest, IDE annotations, request schema and rendered documentation. Check parameter names, units, order, keyword policy, defaults and return/error types. Dispose of all 32 legacy deviations without an unapproved caller break. |
| PS-04 — input admission | Request/domain owner; P0 for changed basis | Per contract: required/default/null/extra-field/type/coercion/enum/finite/range/cross-field rules are explicit. Geometry, actions, materials and reinforcement provenance survive loading. Meaningful rejected cases identify exact field paths and stable issue codes. |
| PS-05 — schema semantics/evolution | Contract/transport; P1 | Classify every schema's role and owner; validate schema and positive/negative instances. Test round trips, references, discriminators, defaults, nullability and unknown fields. Review semantic/signature/schema diffs before updating snapshots; breaking changes have an approved version/migration. |
| PS-06 — results/status/errors | Result/domain; P0 | Admitted PASS/FAIL/HOLD always yields finite inspectable output. Distinguish intake rejection, calculation failure, engineering status, completeness, freshness and approval. Undefined quantities have a typed reason. Preserve error identity and member/source basis across callers. |
| PS-07 — documentation/help | Documentation/API; P1 | Promoted API docstrings and guides state purpose, units, parameter/return/error meaning, assumptions, supported cases, limitations and code basis. Generated reference agrees with source. Installation, extras, Colab and examples use the exact released candidate. |
| PS-08 — examples/first use | Consumer/documentation; P1 | Classify every indexed code cell as standalone, sequential, fragment, template or historical. Every advertised runnable script/cell has invocation, prerequisites and asserted expected outcome; execute promoted recipes against source and clean-installed artifact, including meaningful valid FAIL/HOLD and rejected intake. |
| PS-09 — transports/clients | HTTP/CLI/WebSocket/React owners; P0 for basis | Disposition all 92 HTTP operations and declared CLI/WebSocket/client flows. Execute promoted paths and selected maintenance operations. Compare actual payloads/errors/units/statuses and member identity, not only route names. Authentication/mutation/async boundaries follow existing applicable contracts. |
| PS-10 — architecture/coding | Core/services maintainers; P1 | Changed code preserves Core ← IS-code ← Services ← UI, pure mathematics, explicit units, deterministic results and existing shared helpers. Configured format/lint/type and affected architecture checks pass. Review changed main-process behavior without a generic style rewrite. |
| PS-11 — engineering accuracy | Domain owner + qualified independent reviewer; P0 for claims | Each promoted branch binds exact source edition/amendment/case, formulas/tables, units, assumptions and exclusions. Freeze reference lineage and tolerances before comparison. Accept meaningful normal/limit/failure cases and preserve unsupported/insufficient-evidence HOLD. |
| PS-12 — detailing/exports | Physical-detailing/output; P1 | Calculation, physical bars, centroid/per-bar capacity, cover/spacing, BBS, drawings and report share the same member/input basis. Inspect exact rendered exports for dimensions, units and status. Invalid physical combinations remain rejected. |
| PS-13 — package/install | Packaging; P1 | Exact wheel/sdist includes correct metadata, typing marker/data, declared dependencies and selected extras. Clean installs on the declared Python/platform matrix execute advertised workflows with site-packages origin and no repository imports. Base imports do not require undeclared extras. |
| PS-14 — compatibility/migration | Compatibility; P1 | Canonical owner/projection/caller ledger reconciles and known callers are replayed for selected changes. Each intentional semantic, signature, schema or artifact-format change has a migration/disposition; no unapproved public break. |
| PS-15 — verification/CI | Test/CI; P1 | Every promised candidate claim maps to a meaningful existing or affected outcome gate and published population. Execute examples rather than only generating them. Numerical changes include independent benchmarks. Required hosted checks use the frozen final head; changed-area tests are batched. |
| PS-16 — performance/resources | Workflow/performance; P2 unless blocking use | Measure named representative imports and workflows, including batch/serialization behavior. Freeze meaningful baselines and limits; optimize only after correctness. No cap weakening or relaxed engineering tolerance to obtain a pass. |
| PS-17 — security/distribution | Security/release; P1 for applicable exposure | Use existing security policies and required checks for exposed services, file/adapters and package provenance. Disposition consequential known findings; verify dependency/artifact identity. Avoid unrelated hardening or speculative checklist expansion. |
| PS-18 — end-to-end/release | Release owner + separate qualified reviewer; P0 release gate | Exact installed final candidate completes selected caller journeys and affected visible outputs; required checks and per-version owner authorization pass. Report engineering/professional/native-host acceptance separately and publish only supported claims. |

“Every” above means the declared population: all maintained projections are
classified, all applicable guides are dispositioned, and every advertised
runnable example is assigned and executed or explicitly demoted/withdrawn.
It does not require a separate bespoke example for every private helper or
calling an unsupported engineering route qualified. Existing valid HOLD
outputs are evidence of honest boundaries, not release defects by themselves.

### Contract and example assessment records

S0 creates a current per-contract matrix using existing manifests, schema
snapshots, compatibility ledger and family evidence records. Extend maintained
owners rather than creating a competing catalogue. Required columns:

- **Identity:** public module/operation, canonical owner, supported caller,
  release/support class, request/result/error version and source hash.
- **Signature:** exact parameter names/order/kinds, explicit units, types,
  required/default behavior, return type, exception/error identity and retained
  compatibility exception if applicable.
- **Admission:** missing/null/unknown/duplicate fields; booleans versus numbers,
  numeric strings, finite values, enums/ranges; relevant geometry/material/action
  relationships and explicit supplied/derived facts. A case is required when
  its outcome can change the advertised main process.
- **Result:** valid nominal outcome, meaningful admitted engineering FAIL/HOLD,
  invalid intake and calculation failure; finite JSON round trip; completeness,
  freshness, approval and provenance; cross-caller meaning.
- **Engineering/output:** applicable source/case, assumptions and exclusions,
  independent reference/tolerance, physical basis, exact rendered artifact when
  advertised, reviewer and acceptance boundary.
- **Example:** guide/script and cell identity, executable class, preceding-cell
  dependencies, prerequisites/extras, command/runtime, expected outcome, actual
  assertions, source/artifact identity and replay receipt.

Use the 13 current family journeys as the first promoted contract population,
then the remaining promoted family operations and complete-member/readiness
workflows. Classify all 60 family function projections and 115 compatibility
functions; builders, loaders, calculations and exports have different case
obligations. Classify the 92 HTTP operations into design, query, import/export,
workflow and mutation roles so a model-definition endpoint is not mistaken for
a qualified calculation endpoint. Review the separate WebSocket contract.

The initial 705-fence census is a starting denominator, not a permanent
execution list. Record each fence's file/hash and position, then its executable
class and expected outcome. Sequential notebook/tutorial cells run with their
declared context; templates and intentionally invalid snippets need explicit
labels. After repairs, require **zero unexpected failures among advertised
runnable examples**. Execute the shipped CSV job workflow as well as the 17
script invocations; their current script passes did not resolve Q-F02.

For API documentation, cover fields by semantic role and reuse shared owners:
identity; geometry/units; materials; actions and sign convention; physical
reinforcement; source/case; schema/version; result/status; freshness/approval;
errors. An undocumented hidden engineering default is more consequential than
a missing description on a generated wrapper identifier. Triage the measured
3,054 missing descriptions accordingly, and publish disposition counts.

### Delivery milestones, dependencies and completion evidence

| Milestone | Deliverable and accountable roles | Dependency / exit gate |
| --- | --- | --- |
| S0 — freeze scope and authority | Parent/API/domain owners select the quality candidate; finish the guide/authority and contract census; name owners, support populations, applicable standards, compatibility exceptions, source/reviewer dependencies and measurements. Resolve overlap with draft #1019 before publication/integration. | Current source identity and scope approved; all 18 areas have owned obligations and honest current states. No calendar promise from the unconfirmed 50-day draft. |
| S1 — repair outcome and input fidelity | Result/adapter owners implement Q-F01/Q-F04 at the calculation/result and producer/consumer owners. Cover finite FAIL/HOLD, explicit unavailable quantities and faithful deserialization. | S0. Affected Python/JSON/CLI/HTTP outcomes retain identity/basis/status; meaningful regression cases and compatibility review pass. |
| S2 — dependable first use and guidance | Documentation/output owners complete Q-F02/Q-F03/Q-F05/PS-F06/PS-F07; reconcile active guides, version pins and physical starter inputs; execute promoted cells and inspect affected PDF/drawings. | S1 for shared fixtures. Advertised first-use workflows complete; active instructions route correctly; rendered exports preserve visible dimensions/units/status. |
| S3 — complete public contracts | API/schema/adapter owners finish PS-02–PS-09/PS-14 matrices across declared populations. Resolve signature exceptions, semantic field documentation, input coercion policies and schema evolution; execute selected cross-caller outcomes. | S1/S2. No ambiguous promoted owner, undocumented outcome-changing default, unexplained public drift or unapproved compatibility break. Snapshots and ledger regenerate only after semantic review. |
| S4 — qualify engineering and outputs | Domain owners and qualified independent reviewer accept selected existing support claims and affected calculation branches, physical detailing and export basis. Reuse LIB-2 evidence without reopening its completed implementation. | Frozen sources, tolerances and references. A numerical change is accepted only for its exercised scope; source/host/engineering holds remain explicit. LIB-3 evidence and LIB-4 torsion enter only if separately selected and their existing gates pass. |
| S5 — freeze and verify the integrated artifact | Packaging/test owners freeze implementation/docs, run the union of focused evidence and affected independent benchmarks; verify clean installed base/extras and representative performance; run named release regression and required hosted checks. | S1–S4 accepted for candidate scope. Exact wheel/sdist/source/head identities agree; runnable examples and affected outputs pass on the artifact; all exclusions and holds are published. |
| S6 — authorize and release the exact candidate | Release owner completes existing release preflight, TestPyPI/exact-wheel verification, final version authorization, publication-surface verification and user-facing migration/support notes. | S5 plus per-release owner authorization and unchanged reviewed candidate. PyPI/GitHub readback matches hashes. Professional-use or native-host claims require their separate recorded acceptance. |

S1 is the first runtime packet; this audit and plan do not start it. Within each
selected milestone, implement its code, meaningful regression cases and intended
documentation before one affected verification batch. Cohesive internal units
may share one milestone PR when authority and installed/external gates permit.
Reuse the focused test owners above and existing canonical transport, family,
example, schema and export verifiers. Do not add a new check for every advisory
inventory observation or rerun unchanged broad suites after every edit.

At S5, one broad Python regression is justified by shared result/serialization
changes and cross-family artifact acceptance. FastAPI/React checks apply to
their maintained callers and changed semantic boundaries. Host-specific
execution is included only when the candidate advertises that host. A skipped
native run cannot become PASS through fixture or source parity.

Estimate duration after S0 measures the contract/example population and names
independent engineering/reviewer/host dependencies. Track active implementation
effort separately from source/reviewer/external wait. Schedule S1/S2 before
optional additions; a new workflow cannot compensate for an unresolved P0/P1
consumer defect. The earlier LIB-3/LIB-4 estimate remains only that extension's
low-confidence estimate, not this programme's total duration.

### Evidence and release admission

Each candidate receipt records requirement ID, owned population, exact source
or artifact hash, runtime/command, expected and observed main-process outcome,
status and limitation. A claim lacking its required receipt stays `NOT_RUN` or
`HOLD`. Changing a calculation/reference after evidence freeze invalidates its
affected acceptance and requires that evidence to be rerun; do not broaden
testing when no changed behavior or unresolved concern justifies it.

Release admission requires all of the following for the selected scope:

1. Zero unresolved P0/P1 defects that prevent or misrepresent an advertised
   main-process outcome; Q-F01–Q-F05 and PS-F06/PS-F07 have accepted closures.
2. Complete owner/support disposition of maintained public projections,
   applicable active guidance, schemas and advertised code examples. Promoted
   examples have zero unexpected runtime failures and assert intended outcomes.
3. Signature/schema/input/result/documentation agreement for every promoted
   contract, with recorded legacy exceptions and approved migration semantics.
   PASS/FAIL/HOLD and approval/freshness remain distinct and finite.
4. Accepted affected independent engineering references and physical/output
   evidence, exact limits and exclusions. No unsupported source/amendment/case
   or native-host claim is silently promoted by a passing software test.
5. Final installed wheel/sdist identity, source/adapter/extras evidence, required
   hosted checks, applicable security/provenance gates and per-version release
   authorization agree on the unchanged candidate.

If source evidence is insufficient, freeze the affected claim as HOLD or remove
it from promoted scope through an explicit decision. If compatibility would
break, present the concrete migration/version choice before changing retained
callers. Neither uncertainty nor a policy deviation authorizes substituting
engineering inputs, weakening validation or raising safeguards.

This revision delivers the expanded assessment and executable plan. Its runtime
fixes, deeper per-contract qualification, clean candidate artifact, qualified
review and release are future milestone work. It preserves the open draft
[#1019](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1019),
the separate solver/library ownership boundary, the six-phase beam programme
and XLL track, and the existing torsion and native-host gates.

## S0/S1 execution — 29 October 2026

The owner selected S0 and S1 and both P0 corrections. The selected writer lane
is `codex/lib-s0-s1-correctness`, based on current main
`eb6f8b51988a3f9b26a10f07164aa958309d0d84` plus the retained reviewed planning
head `9c30032debc38d315a150809f36a96a047ed654d`. Codex `/root` owns the packet,
integration and finite-result repair; `/root/public_contract_audit` implements
the bounded smart adapter; `/root/coding_guidance_audit` performs read-only
software review. Pravin Surawase retains scope/release decisions. A qualified
engineering reviewer for later S4 is not appointed or implied by these roles.

### S0 scope and authority decision

The [S0/S1 record](../verification/library-s0-s1-20261029.json) assigns all 18
quality areas, binds their public populations to the maintained API/schema
owners, and expands the earlier six-root inventory to 371 guide/reference,
instruction, workflow and authority records. Its 24 curated authority records
include path-scoped rules, conditional calculation workflows, actual CI,
source-use permission and historical release authority. Inventory/assignment
does not claim every guide is semantically accepted or every example executed.
Six missing canonical reference paths are explicitly assigned to later guide
reconciliation; none is used as the engineering source for this repair.

AGENTS and scoped four-layer/source-bound rules govern S1 where the active
coding guide conflicts. PS-F06/PS-F07 remain S2 documentation repairs. Required
normalized-data/public-distribution permission is already PASSED. All 32
positional-policy deviations remain retained compatibility exceptions for
this packet; S3 decides broader migration and documentation.

The current 18-area quality programme, selected by the owner, supersedes the
overlapping quality portion of draft #1019 for this packet. The S0/S1 candidate
is explicitly rebound to current main and the retained planning predecessor;
the older draft/calendar is not a predecessor for these repairs. Preserve its
open draft and unconfirmed capacity/calendar. Its overlapping content must be
rebound to the integrated S0/S1 successor before later integration. No closing,
merging, branch disposal or schedule approval is granted for #1019.

### S1 contract and root-cause correction

Q-F01 originates in an unavailable check: overload produces excess tension
steel, the maintained Table 19 domain check fails, and compatibility compliance
uses positive infinity for its unevaluated utilization and governing ranking.
The generic canonical serializer rejects that sentinel. This repair preserves
the native numeric/ranking contract and the decisive failed checks, while the
domain-owned transport projects only known unavailable ratios to `null` plus
`UTILIZATION_NOT_EVALUATED` and a reason at their exact field paths. A finite
known ratio is unchanged. Unexpected NaN, negative infinity or unexplained
positive infinity still fails serialization; no safety limit or table lookup
is relaxed. No IS456 engineering formula, factor or tolerance changes.

The finite projection covers canonical beam/composed results, compatibility
compliance/report transport and pipeline JSON. The canonical Python,
`beam-v1` CLI and FastAPI v2 route consume the same result. The affected retained
smart HTTP route also carries nullable utilization with the typed unavailable
reason; a valid failed calculation is not rejected as HTTP input error. Existing
v1 beam-design display caps and broader schema/transport consistency remain S3 work; this
packet does not claim all 92 operations have acquired new semantic parity.

Q-F04 originates in a nested producer result being read as flat raw inputs.
The strict `BeamDesignOutput.from_dict` owner restores current wrapped or
standalone pipeline results without redesigning them or inventing facts.
Identity, geometry, materials, actions, reinforcement/detailing, original
`design_inputs`, depth receipt and result envelope are retained. Missing,
unsupported, inconsistent or stale serialized results reject before smart
analysis. Declared raw flat-input behavior remains separate and supported.

The default smart path also replayed sensitivity from a partial input mapping,
dropping compression depth, stirrup area and serviceability basis. It now uses
the original calculation arguments, and refuses an unavailable baseline or
perturbed finite-difference basis explicitly. The dashboard retains the source
engineering FAIL/HOLD; unavailable sensitivity has a code/reason rather than
NaN derivatives. Both reduced and default smart analyses are verification
targets, so disabling optional analyses is not the completion criterion.

### Verification and remaining gates

Acceptance rows S0-A1–A3 and S1-A1–A6 live in the S0/S1 JSON record. Required
evidence includes the actual published overload recipe, nominal and valid
finite-failure retention, native governing-case ranking, unexpected non-finite
error preservation, canonical CLI/HTTP parity, real-producer smart round trips,
invalid serialized-basis rejection, original-input sensitivity replay and the
default smart failure workflow. Retain the 13 family recipes and their existing
PASS/FAIL/HOLD outcomes, and use existing serialization tests for the shared
dataclass traversal risk.

Finish the intended code/tests/docs, format changed files, run the union of
focused checks once, then review the final candidate. Required changed-domain
hosted checks and final integration must bind the same reviewed head. The JSON
record captures local receipts; the pull request remains the authority for
hosted-check, review and merge facts. The S5 broad release regression and exact
installed-wheel qualification remain later work unless essential review exposes
a concrete additional local risk. S2–S6, LIB-3/LIB-4 torsion, native-host runs,
professional acceptance and per-version package publication remain outside this
packet. There is no release authorization or claim of engineering-use approval.


## S2 execution — 29 October 2026

The owner selected Q-F02/Q-F03/Q-F05 and PS-F06/PS-F07, with complete tests and
review. The writer lane is `codex/lib-s2-first-use` in a fresh managed checkout
of main `a3ea3f0d9bf6cd7904ed3182522cf13e615e5b87`, following integrated S0/S1.
The previous squash-merged branch is preserved. Codex `/root` owns all writes;
bounded read-only agents diagnosed first-use/guidance/output paths and review
the frozen result. Draft #1019 and its unconfirmed calendar remain preserved
under the existing successor/rebinding decision.

### Physical starter inputs and first use

The five-beam source CSV now declares `tension_bar_diameter_mm`, clear cover and
link diameter instead of stale supplied effective depths. The existing strict
admission derives the strength depth and the actual generated one-layer layout
must match it. No effective-depth, bar-fit or multilayer check is relaxed.

| Member | Main bar diameter (mm) | Generated bottom count | Resolved depth (mm) |
| --- | --- | --- | --- |
| B1 | 16 | 5 | 444 |
| B2 | 16 | 4 | 394 |
| B3 | 20 | 4 | 540 |
| B4 | 20 | 4 | 442 |
| B5 | 20 | 6 | 630 |

The beginner and quickstart compatibility cells use the same physical basis.
The Colab B2 teaching section is explicitly 240 mm wide so its four 16 mm bars
fit a verifiable layer; the old 230 mm case still rejects as unverified rather
than acquiring an invented centroid. Required first-run files are supplied,
DXF/render extras are explicit, and caller-file/serviceability command forms
are distinguished from runnable first-use recipes. The external CLI harness
uses the same strict shipped CSV. Source onboarding points to actual paths and
file outputs. Excel/VBA/XLL are separate artifact/host tracks, not a promised
add-in installed by the Python wheel.

### Version and guide owners

The maintained bump/check population includes the beginner/Colab/example and
CLI guides. One matcher covers base/extras pins and tagged raw-input links;
regressions catch the former false PASS while preserving historical release
claims. Current public pins resolve exactly to 0.25.0. The corrected CSV is
supplied inline/current source instead of sending beginners to an immutable
older-tag sample with inconsistent depths. A source sync does not grant a tag,
registry availability or publication; the S6 version decision remains later.

The coding-standard owner, connected coding/reuse/onboarding guides and library
contract now route to four-layer ownership, the bound runtime, frozen-batch
verification, promoted family APIs and the existing pre-1.0 compatibility
policy. Retired migration commands are removed or explicitly historical.
The six missing canonical references are resolved to maintained scoped owners;
old Week 3 sketches are historical and old 3D timings are dated measurements.
The append-only release ledger gains a current process that supersedes its
older Alpha-only instructions without rewriting past entries. This does not
claim semantic qualification of every guide in the S0 inventory.

### PDF/drawing meaning and visible output

The report SVG reserves annotation space inside its viewport so its depth label
is visible in the actual WeasyPrint PDF. The report is explicitly a
calculation-depth schematic, not an invented physical bar-count drawing. It
retains the actual stirrup area from the design inputs instead of displaying a
false missing-value warning. Print-only spacing keeps the short units-status
section with its calculation tables; the five-member report has 11 pages rather
than five orphan units-status pages added to a 16-page report.

The DXF preview helper renders dark lines/text on white while preserving the
source DXF. The export owner separates span dimensions, bottom-bar callouts,
link callouts and development/lap notes into shared bands and reserves their
extents in grid layout. This repairs the actual small-beam label collisions
and text over reinforcement, without changing engineering bar geometry, units,
marks or calculation results. BBS/drawing mark parity and actual five-member
outputs are checked. The modelspace preview is not a qualified fabrication
sheet or native CAD/print acceptance.

### Evidence and remaining gates

The [S2 record](../verification/library-s2-20261029.json) binds the source-free
local development wheel, current source hashes, commands, outputs, targeted
repairs, focused regressions and visual review. All 17 promoted scripts and the
13 family pages (27 Python cells) replay; the family controls retain 11 PASS,
one intentional FAIL and one intentional HOLD. Beginner/quickstart/Colab
library and CLI cells, the source-onboarding and sample-job flow, exact public
pin resolution and the external CLI harness have their own receipts. Colab's
browser download UI and native Excel/ETABS/XLL acceptance are not implied.

The 341-case focused union passes. Outcome-changing final drawing/report
repairs have their affected 23/54-case refreshes; these are overlapping evidence,
not additional distinct test counts. Mypy passes for 330 library files, with an
affected drawing-owner recheck. Four HTML goldens are intentionally refreshed
after actual rendered review; numerical/status content is retained.
Independent exact-head software review, required hosted checks and merge are
recorded on the milestone PR after this local freeze. S3 contract completion,
S4 engineering/output qualification, S5 final release-artifact verification and
S6 authorization/publication remain later work. No source version bump,
package/tag/PyPI/GitHub Release or professional approval is performed by S2.

<a id="post-s2-maintenance--29-october-2026"></a>

## Post-S2 maintenance — 29 October 2026

### Selected packet and ownership

The owner selected a maintenance plan followed by execution before S3.
`LIB-MAINT-20261029` has one Mac writer, Codex `/root`, on
`codex/lib-maintenance-20261029` in a fresh managed worktree from fetched main
`afe785be5c6a72cd22de75ba48c3da6ea1d19a34`. The completed S2 branch and its
sample outputs remain preserved. One bounded read-only reviewer traces live
CI/dependency evidence; the parent owns all edits and independently checks the
result.

| Work | Question and action | Acceptance |
| --- | --- | --- |
| M1 — source and delivery | Verify S0/S1 and S2 integration, current main, source-bound runtime, task-owned candidates and retained artifacts. | Clean fresh lane; no unfinished operation or conflicting writer; exact reviewed/merged identities retained. |
| M2 — next-session truth | Reconcile the task board and startup handoff with the released v0.25.0 and integrated S0–S2. Preserve dated source/engineering records. | Actual startup routes to maintenance/S3; no expired overnight instruction or superseded release/feature number is presented as current authority. |
| M3 — CI failures | Inspect current required checks and the failed 26 October Weekly Verification run. Trace its failed step to current source before selecting a fix. | The failure has a confirmed current repair or an explicit evidence-bound disposition; no passing PR is substituted for an unexecuted scheduled suite. |
| M4 — dependencies | Classify the 11 open PRs and the consumers of changed manifests. Adopt an update only for a demonstrated compatibility/delivery need. | Stale-base checks are not current-candidate proof; no bulk or unrelated major upgrade. Required domain routing follows actual workflow installers. |
| M5 — controls and recurrence | Inspect health, feedback, context/instruction composition and the existing recurrence index. Reuse RR-004 for the confirmed milestone-to-handoff propagation miss. | Index count, evidence basis, last-seen task and generated handoff agree; no invented root cause or rework timing. |
| M6 — freeze and integrate | Finish intended edits, then run the affected checks once, review the essential diff and use one normal PR if changes are needed. | Required hosted checks pass on the reviewed head; merge tree matches; task timer closes once. |

### Baseline and confirmed repair scope

Health is 100/100 with zero reported issues, feedback has no pending items,
context validation passes, scoped instructions compose exactly and the
configuration audit has no conflicts. These are repository diagnostics, not
engineering acceptance. Runtime diagnosis binds imports to this worktree.

The material defect is stale operational routing: startup reads the maintained
handoff's 1 October focus, while the task board still calls v0.24.0 current and
assigns v0.25 to an older ACI proposal. Release #1026 and S0/S1 #1032 plus S2
#1034 were not propagated to those owners. Refresh the current projections and
retain the old dated evidence under an explicit historical boundary. This is
one further RR-004 event, not one event per affected document.

The 26 October scheduled run failed its strict Python dependency audit with
55 advisory entries in six locked packages, and its Python ledger comparison.
S1 already repaired the demonstrated Pydantic metadata spelling difference;
reuse its regression and current generator check. The exact current audit
reproduces 70 advisory entries in seven packages. These are audit entries, not
a claim of 70 distinct vulnerabilities or a reproduced exploit. A constrained
resolver selected fixed Black, Brotli, Certifi, Filelock, Pillow, Tornado and
Virtualenv versions; Virtualenv also requires python-discovery 1.6.1. Preserve
the rest of the locked inventory and synchronize the direct Black pin in both
root requirements and package dev metadata. The production npm audit reports
zero findings. Current S2 selected PR checks and post-merge documentation
deployment passed; neither observation reruns the older scheduled workflow. Dependency #1033 and tooling #1028 are
behind current main. The existing #1033 candidate does not lift Filelock or
Pillow to the fixed branches, so it is not an adequate repair as-is. #1028
bundles Black with an unrelated Ruff update; take only the demonstrated Black
security pin into this packet and leave its other tooling change unselected.
The other older React/.NET/mypy updates and draft #1019 are preserved and do
not select current work. The root-requirements rule correctly selects FastAPI and
repository checks: Python and documentation PR jobs use their own package and
explicit documentation installers. Shared dependency names alone do not
justify routing unrelated domains or changing their gates.

### Boundaries and verification plan

No engineering formula, public API contract, native host, publication,
GitHub setting, branch deletion or broad dependency migration is selected.
Existing normalized IS-data distribution permission remains passed. S3–S6
and their engineering, installed-artifact and release gates remain separate.

For the operational-document repair, exercise the actual startup brief and
existing handoff/recurrence readers, the focused session automation tests,
documentation metadata/links, context and instruction checks. Run the
essential changed-area gate after content freeze; do not duplicate the S2
341-case suite or add broad suites without a named failure requiring them.
The dependency repair requires the exact strict lock audit, a clean constrained
installation and pip check, formatter compatibility and existing focused
Pillow/report/DXF, virtualenv/runtime, API ledger/schema and FastAPI consumer
evidence. This is the concrete reason for testing those changed dependency
consumers. Any confirmed workflow repair gets its affected command/selector evidence.
Keep final hosted-check, review and merge facts on the maintenance PR.


### Local candidate evidence and next handoff

The constrained clean Python 3.11 installation retains all 140 packages with no
additions or removals. Only the following versions change; Black is also
synchronized in root requirements and package dev metadata.

| Package | Before | Final candidate |
| --- | --- | --- |
| Black | 26.5.1 | 26.10.1 |
| Brotli | 1.2.0 | 1.2.1 |
| Certifi | 2026.7.22 | 2026.10.19 |
| Filelock | 3.32.2 | 4.2.1 |
| Pillow | 12.3.0 | 13.0.0 |
| python-discovery | 1.6.0 | 1.6.1 |
| Tornado | 6.5.9 | 6.6 |
| Virtualenv | 21.7.13 | 21.14.13 |

The initial Virtualenv 21.14.9 candidate still reported one advisory and is
rejected. The [upstream advisory](https://github.com/pypa/virtualenv/security/advisories/GHSA-4f8h-vr72-p32c)
identifies 21.14.10 as patched; the final 21.14.13 package resolves, installs and
passes the repeated exact strict audit. Preserve that rejected report separately
from final acceptance; do not count a candidate repair as another occurrence.

Final local results:

- Exact `pip-audit --strict --no-deps --requirement requirements-lock.txt`:
  zero known findings across the 140-package final inventory. This is the
  observed advisory-service result, not a claim of no possible vulnerability.
  The command's default resolver reports 139 records, omitting Packaging;
  the supplemental `--disable-pip` pre-resolved audit reports all 140 exact
  pins, including Packaging, with zero findings and no skipped dependency.
- Clean constrained install and `pip check` pass. The final Virtualenv creates
  a new environment using a task-owned app-data cache; its pip runs successfully.
- Focused dependency/caller/handoff union: 314 passed, no failures/errors/skips.
  The final Virtualenv patch has 18 overlapping environment/runtime checks plus
  actual creation proof; these are not additional distinct test counts.
- Black 26.10.1 accepts the maintained session owner and its existing test file.
  No unrelated formatting or Ruff upgrade is introduced.
- Strict MkDocs succeeds in the same constrained environment. Actual five-beam
  design/BBS/DXF/report and PDF/PNG generation succeed; the PDF has 11 pages and
  all D450/500/600/700 mm labels. No source calculation or report golden changes.
- Production npm audit:zero findings; no React lock or application change.
- RR-004 increments once to 36 for the operational projection miss. RR-051
  records one continuing dependency-lock audit event. Counts, basis, last task
  and deep links are synchronized; old session bytes remain unchanged.

The local receipts reside under `/tmp/lib-maint-20261029-*` during execution.
After final source freeze, preserve copies and source hashes in the task's
local verification output folder. Required changed-area checks, independent
exact-head review, hosted checks and integration remain owned by the milestone
PR. This source record does not claim a rerun of the complete scheduled workflow.

After maintenance integration, freeze S3's declared public-contract population
and decisive cross-caller cases. Existing source/engineering/native-host HOLDs
and S4–S6 remain explicit; no new release, branch deletion or API implementation
is performed by maintenance.

<a id="s3-public-contracts--29-october-2026"></a>

## S3 public contracts — 29 October 2026

The owner selected S3 planning and implementation: signatures, inputs, schemas,
defaults, compatibility, fixes, tests and independent review. Task
`LIB-S3-20261029` uses `codex/lib-s3-contracts` from fetched main
`ec3f230767dcfbdc1cbb18ccb48273f7e9db7682`, following maintenance #1035.
Codex `/root` is the sole writer. Two bounded read-only reviewers inspect
Python and HTTP/client contracts; the parent verifies their evidence and owns
all implementation, documentation and generated records.

### Declared population and acceptance

Existing classification, compatibility ledger, manifests, strict request
contracts, workflow registry and OpenAPI remain authoritative. Extend those
owners; execution receipts are evidence, not a competing API catalogue.

| Requirement | Declared work | Required proof |
| --- | --- | --- |
| S3-A1 — ownership/signatures | All 14 surfaces / 1,308 projections, 60 typed functions in 11 modules and 115 compatibility functions / 245 exports. | Callable/annotation/manifest/owner identity, parameter kind/order/default/return agreement and consumer/support dispositions; no promotion of internal helpers. |
| S3-A2 — positional policy | All 32 legacy over-limit functions plus the root-only observation evidence API. | Reviewed exact owner/signature exception and reason; reject unexplained new deviations. Retain existing positional call forms. |
| S3-A3 — input/default semantics | All 13 family requests / 564 field leaves plus promoted complete-member/readiness contracts. | Required/default/null/type/bool/string/finite/extra/enum/range/cross-field/provenance decisions, schema links and meaningful positive/rejected cases. Distinguish supplied inputs, derived facts and legacy defaults. |
| S3-A4 — schema evolution | All 488 component schemas and referenced family request/result/error schemas. | Exhaustive owner/role/reachability/field/default/null/reference dispositions; meta-validation, meaningful positive/negative instances and round trips. Semantic review before snapshots; missing-description counts alone are not defects. |
| S3-A5 — transports/clients | All 92 HTTP operations / 91 paths, CLI flows, separate WebSocket messages and maintained React callers. | Operation roles and request/result/error/coercion/mutation boundaries; actual promoted/selected payload, unit, status and member/source/unavailable-quantity assertions. Native evidence remains separately qualified. |
| S3-A6 — help/examples | Promoted operations, indexed cells, 13 family journeys and maintained member/readiness examples. | Source/reference/schema agreement; purpose/units/default/return/error/limitation meaning; executable class, prerequisites and outcome dispositions. Reuse S2 evidence only for unchanged identities; replay changed consumers and frozen installed artifact. |
| S3-A7 — compatibility | Canonical/projection/caller ledger, retained exceptions and affected saved/client payloads. | No ambiguous owner, unexplained drift or unapproved breaking migration. Every intentional correction has a compatibility decision and known-caller replay. |
| S3-A8 — verification/integration | Frozen union of affected outcomes and generators. | Relevant format/lint/type/architecture checks, focused regressions, independent exact-head reviews, required hosted checks and matching merged tree. Broad local suites need a named shared-contract risk. |

At intake all HTTP schemas are reachable: 125 request-only, 323 response-only
and 40 shared; all 92 operations carry the shared problem-response contract.
These are role/coverage measurements, not semantic acceptance. The 32 legacy
positional deviations are retained exceptions, not numerical defects. Numeric
boolean and duplicate-JSON probes reject across all 13 strict family journeys;
the remaining matrix obligations still require their own evidence.

### Confirmed transport failures and selected root repair

Legacy `design_beam` WebSocket duplicates the REST projection and has diverged:
missing envelope/depth-basis fields make React synthesize HOLD for known
PASS/FAIL. Its `asv_required` omits division by effective depth while declaring
mm²/mm; the measured error is 457-fold at d=457 mm. REST and WebSocket also cap
the field described as governing utilization at 2.0, even when the core ratio
is unavailable and its evidence already records null.

Reuse one shared REST/WebSocket projection without changing IS mathematics,
limits, bar geometry or support. Preserve physical/source identity and expose
the actual finite-or-unavailable ratio with the existing typed reason vocabulary.
Retain required legacy fields under an explicit compatibility decision rather
than silently inventing an ordinary number. Update known React consumers to
use authoritative ratios/status and display unavailable quantities honestly.
Document schema/client evolution before regenerating snapshots.

Wall and legacy WebSocket numeric-string conversions remain explicit adapter
policies. Preserve supported conversions and validate at the canonical boundary;
do not weaken strict family requests. Any additional outcome-changing default
or schema discrepancy receives the same source-bound root-cause treatment.

### Execution order and boundaries

Complete live matrices and defect probes; implement the shared projection,
client/result contracts, retained-exception policy and documentation at their
owners. Add meaningful regressions during implementation. Freeze and run their
focused union once; repairs refresh only affected evidence. Regenerate derived
records after semantic review, preserve rejected probes, and bind artifact
replays to installed origin and exact bytes. One milestone PR owns hosted
checks/integration; no side merge may invalidate the reviewed candidate.

S4 engineering/output qualification, S5 final released-version artifact and S6
per-release authorization/publication remain later gates. Existing source,
physical and native-host HOLDs and normalized-data distribution permission
remain unchanged. S3 authorizes no tag, publication, support expansion or
native application mutation.

The complete S3 signature census additionally retains the existing root-only
ETABS target-observation function: 33 unique reviewed owners across the public
surfaces, of which 32 belong to the legacy compatibility manifest. Batch
non-finite JSON, WebSocket unknown/duplicate input and active installation-pin
drift are confirmed contract defects within this same selected milestone.
The shared projection and actual/null client migration include dashboard ratio
intake; no new engineering algorithm or native operation is selected.

The final local FastAPI suite is justified by the shared response projection,
problem decoding and all-operation schema reconciliation. The React suite and
production type/build check are justified by shared response types and persisted
batch/dashboard/viewport consumers. Python verification stays focused on the
changed batch/dashboard owners, strict facade/member/readiness/CLI contracts,
compatibility, schema and version tools. No broad Python or full repository
suite is selected as a duplicate of hosted required checks.

<a id="s4-engineering-and-outputs--29-october-2026"></a>

## S4 engineering and outputs — 29 October 2026

The owner selected S4 implementation after S3 merged in PR #1038. Task
`LIB-S4-20261029` runs on `codex/lib-s4-engineering` from fetched main
`7e19a23b829022da98f562104f47b3fda6cbb85e`. Codex is the sole writer;
bounded independent technical reviewers inspect engineering and physical
outputs. On 29 October the owner identified himself as the structural engineer
and directed that no separate external-reviewer dependency be added. Pravin
Surawase is the engineering owner; independent numerical and technical review
remain required. This does not grant project-specific professional approval.

### Population and acceptance

The existing capability/family/workflow registries remain the claim owners.
Do not replace a supported claim with a smaller case merely to obtain a pass.
Reconcile all 13 promoted family journeys, the promoted ordinary and multilayer
complete-member cases, and their governing beam/material/flanged/column/SLS
branches. Retain existing evidence for unchanged accepted branches only after
checking source and case identity. Separately held source, physical and native
claims remain visible; LIB-3/LIB-4 extensions are not selected.

| Requirement | Work and proof |
| --- | --- |
| S4-A1 — claim and branch census | Map every promoted family, complete-member case and governing branch to its maintained implementation, support limits, source, benchmark and output owner. Preserve PASS/FAIL/HOLD and identify supplied external facts. |
| S4-A2 — controlled sources | Verify the controlled IS 456:2000 collection and issued Amendment 6 hashes, applicable amendment/clause/table/figure locators and assumptions. Reconcile current relevant amendment dispositions; source possession or catalogue metadata is not calculation qualification. |
| S4-A3 — independent engineering | Freeze independent expected values, units, reference lineage and justified absolute/relative tolerances before comparing production results. Exercise meaningful normal, limiting, failure and held cases across the declared branches. Golden values, wrapper parity and duplicated production formula calls do not substitute for independent calculation. |
| S4-A4 — physical member consistency | Verify actual longitudinal layers, signed per-bar equilibrium, centroid/depth, cover/clear spacing, shear/link basis, anchorage/path geometry, lengths, counts, mass and quantities for ordinary and multilayer cases. Invalid combinations remain rejected or draft. |
| S4-A5 — faithful exports | Carry identical member/source/result/schedule identity through JSON, physical BBS, DXF/drawings and HTML/PDF reports. Parse actual entities and quantities, then render and inspect final output dimensions, bar positions, units, marks, status and readability. Physical outputs must use resolved paths rather than a one-row schematic. |
| S4-A6 — root repairs and compatibility | Repair confirmed outcome-changing math/applicability/physical-output defects at their owner; preserve public binding and known callers or document an intentional correction. Add meaningful implementation regressions and independent references for every changed numerical branch. |
| S4-A7 — frozen verification and review | Complete intended code, tests, references and documentation before the focused union. Run affected format/lint/type/architecture and export/benchmark checks, independent exact-head technical reviews, and required hosted checks. Repaired candidates refresh affected evidence only. |
| S4-A8 — integration and boundaries | One milestone PR integrates the reviewed candidate with matching merged tree. Retain reviewable source/case/expected/actual/tolerance and output receipts. S5 final-version artifact qualification, S6 release authorization and native-host acceptance remain separate. |

### First confirmed output defect and repair direction

The generic DXF elevation locates longitudinal steel at cover plus bar radius,
omitting the link. Promoted B1 requires its bottom centre 56 mm from the bottom
(40 mm cover + 8 mm link + T16 radius); the drawing puts it at 48 mm. More
fundamentally the generic section projection collapses layers to one row and
cannot represent the promoted multilayer schedule's 50/125 mm bottom-centre
levels or its 412.5 mm tension centroid. Mark parity alone does not prove
physical geometry. The complete-member example currently exports JSON/CSV/HTML
and carries drawing metadata rather than a path-derived drawing.

Correct the ordinary projection and provide a resolved schedule/path-bound
physical drawing at the existing output owners, including identity and issue
state. Do not disguise multilayer geometry by adjusting a single row. Verify
actual DXF entities against the accepted physical paths and BBS, and inspect
rendered output. Any additional engineering discrepancy must have an
independent source-based reproducer before implementation.

At intake the 13 family recipe replays establish contracts/statuses, not
independent numerical qualification for every journey. S4 will bind each to
controlled source-derived numerical evidence and retain existing stronger
beam/per-bar/column/material/SLS references where identities agree. The old
amendment diagnostic failures are historical and must not be presented as
current defects without reproduction.


### S4 implementation checkpoint

The [execution receipt](../verification/library-s4-20261029.json) now binds all13
journeys to106 independent metrics and the retained governing branch references.
It records four source-confirmed repairs: strap vertical-stirrup strength capped
at415; consistent ordinary HTTP/WS Asv/s; resolved physical layer identity; and
link-aware, path-bound digital drawings. Both member cases have parsed DXF,
JSON/BBS identities and visually inspected HTML-derived PDF reports/drawings.
These cases exercise the declared supported models; they do not replace or
silently narrow their support claims. Existing exclusion/applicability and
normal/limit/failure tests remain part of the focused union.

Pravin Surawase is the engineering owner by direct instruction. Independent
numerical and exact-head technical reviews are required; a separate external
engineering-review dependency is removed. Full amendment qualification remains
HOLD at its existing owner. S4 software/evidence acceptance does not grant
project-specific professional, native CAD/fabrication or release approval.

The final local union covers the affected family code/boundary, independent
material/flange/column/SLS, physical-member/export and HTTP/WS owners. New shared
export/binding behavior and the two shear consumers justify these checks;
required hosted broad suites cover integration. No duplicate local full Python
or full repository run is selected. Exact commands/results and final integration
belong to this milestone PR and its retained execution receipt.


<a id="s5-s6-efficient-artifact-and-release-plan--29-october-2026"></a>

## S5/S6 efficient artifact and release plan — 29 October 2026

The owner selected planning and S5 execution after S4 PR #1039 integrated at
`a39e02b24c85ed1c2852021c3e511375366b9112`. Task `LIB-S5-20261029` uses
`codex/lib-s5-artifact`; Codex is the sole writer, with at most two bounded
read-only reviewers. Prepare **0.26.0** as the unpublished normal candidate for
the audited supported scope. This minor candidate records additive physical
exports and intentional corrections to unsafe results/unresolved geometry;
pre-1.0 compatibility notes must identify those corrections. Pravin Surawase is
the engineering owner; no external-reviewer dependency is reintroduced.

### S5 obligations and decisive evidence

| Gate | Required outcome and evidence |
| --- | --- |
| S5-A1 — coherent candidate | One prepared/unpublished version across package, app, API, citation and active guidance; current public 0.25.0 remains identified. Preserve historical release facts, exclusions and HOLDs. |
| S5-A2 — one frozen distribution pair | Build one wheel/sdist pair after implementation/docs freeze. Record SHA256, build inputs, source commit and Python-tree identity. Inspect membership/data/templates and reject forbidden research/migration/test payloads. Evidence-only integration commits must preserve the exact frozen build-input tree; runtime/build-input repairs invalidate and rebuild/requalify the affected candidate. |
| S5-A3 — isolated base/contract/numerical behavior | Fresh installed wheel and sdist environments prove site-packages origin before/after execution, declared dependencies and pip-check. Replay all 13 promoted family journeys, their 106 S4 independent metrics and valid/invalid/FAIL/HOLD behavior; retain S0/S3 canonical Python/CLI/HTTP/WS/batch coverage through existing drivers. No checkout structural_lib import or broad root requirements may mask missing dependencies. |
| S5-A4 — declared extras | Inventory every declared extra: dev,dxf,render,report,pdf,validation,cad,pmm,docs,etabs. Also verify the promoted combined export installation `[dxf,render,report,pdf,validation]`. Verify each dependency closure in an isolated profile and exercise its existing advertised non-native behavior. The cad extra currently supplies PyVista only: record dependency availability, no public library CAD/STL exporter, and native CAD HOLD. Windows-only etabs markers are checked on this Mac; installed Windows/Excel/ETABS acceptance stays explicit and unclaimed. The pmm experimental boundary remains unchanged. |
| S5-A5 — installed physical/output fidelity | From the installed export-capable wheel replay ordinary and multilayer member cases, parse actual JSON/BBS/DXF identities/paths/layers/lengths/masses and HTML/PDF/report outputs, then inspect rendered artifacts. Bind results to the exact distribution hashes. Package data/template probes must execute from installed resources. |
| S5-A6 — representative performance | Measure fixed valid ordinary-beam, batch and family workflows with warmups/repeated timings, record environment and error counts. Set budgets before measurement; compare supported common calls with the public 0.25.0 baseline when suitable. This is a representative regression check, not a general speed guarantee. |
| S5-A7 — one integrated verification cycle | Finish code/docs/tests first. Run affected focused checks, one named broad Python release regression and affected FastAPI/React through the canonical frozen-candidate preflight. Use only `preflight --wheel <exact-path>` after the version bump; do not duplicate a pre-bump full suite or Docker path. Independent exact-head reviews and required hosted checks bind the final milestone PR. Repairs rerun affected evidence only. |
| S5-A8 — reviewed integration | One milestone PR integrates the accepted candidate. Verify final reviewed/merged tree and frozen Python/build-input identity; retain exact artifact, environment, numerical, export and timing receipts. All support exclusions/HOLDs remain visible. S5 completes without any publication target. |

Reuse the release CLI, version generator, F0/S0/canonical artifact drivers,
S4 reference inputs and physical workflow. Extend the maintained artifact owner
for missing sdist/installed-numerical/extra/export evidence rather than copying
an independent build/release lifecycle. Upgrade/version syntax is validated by
`release run` before its mutation; the single final artifact preflight owns
broad source verification. All source changes, including actual packaging
repairs found by clean installs, belong to the same milestone candidate.

One source broad regression and narrow installed profiles answer different
questions. Do not rerun a second broad source suite merely to repeat a green
result. Archive the first failed candidate evidence; do not change reference
values or weaken origins/claims to obtain a pass. Build/install commands use
unique disposable environments and pip caches; never clean unrelated outputs.

### S6 execution packet, kept separate

S6 consumes the exact accepted S5 artifacts and identities. First revalidate
version/support/migration notes and the publication mechanism's ability to use
those bytes or reproduce their hashes. Any byte-changing rebuild requires
artifact requalification before upload. Prepare one bounded publication-state
packet: dated citation/changelog, an appended authorized ledger entry and the
maintained per-version authorization record, with the frozen Python tree
unchanged. Run the existing publication-surface and exact-target authorization
checks. TestPyPI, tag creation/push, PyPI and GitHub Release require the owner's
explicit per-version/target authorization; S5 does not select those actions.

After authorization, verify the TestPyPI/public files against the retained
hash manifest and install/import identities. Publish user-facing changes,
compatibility corrections, tested installation profiles and support exclusions.
Reuse exact installed UAT for identical bytes; rerun it only if identity differs
or prior evidence does not cover the selected target. Final public readback
must match the accepted manifest. Native/professional-use claims retain their
separate evidence; a normal software release grants neither by itself.


S5 timing budgets are frozen before measurement: ordinary-beam p95 <=100ms,
100-member batch p95 <=2000ms, and each family journey p95 <=1000ms. Warmups and
sample counts are retained in the receipt. Common valid beam/batch median time
must not exceed 3x the public 0.25.0 baseline measured on the same host/runtime;
absolute budgets also apply. No unrelated or intentionally corrected FAIL/HOLD
case is used to claim a speed improvement.


### Frozen S5 execution commands

After the cohesive implementation commit is clean, build and qualify the exact
pair. The example evidence directory is outside the Git checkout so receipts
cannot dirty the frozen source; the execution receipt retains the actual path.

```bash
./scripts/python_runtime.sh -m build Python
./run.sh release verify --qualification --version 0.26.0 --source wheel --sdist Python/dist/structural_lib_is456-0.26.0.tar.gz --receipt ../library-s5-evidence/qualification.json
./run.sh release preflight --wheel Python/dist/structural_lib_is456-0.26.0-py3-none-any.whl
```

The qualifier defaults to all16 profiles: base, sdist, each of10 declared extras,
the promoted combined export extras, canonical application transport, copied
standalone examples and promoted starter guide cells, and the
public0.25.0 performance baseline. Use `--qualification-profiles` only for an
explicit affected-evidence repair against identical artifact hashes; incomplete
populations remain PARTIAL. Source preflight and exact installed profiles must
both pass before S5 acceptance. No command above selects publication.

### S5 executed evidence and final source binding

All16 installed profiles passed on the retained 0.26.0 pair. Wheel and sdist
each passed29 negative-UAT cases, all13 family journeys and106 independent
numerical comparisons. The copied17 standalone examples and eight maintained
public-example/guide checks passed without a checkout package. Ordinary and
multilayer exports retained39/43 physical bars, four/eight section bars and
56.952293/129.914581 kg scheduled steel. All eight generated PDFs were rendered
and inspected; the two engineering spacing failures in the educational CSV
example remain explicit Check results.

The first source preflight exposed stale generated-client version pins and a
generic-DXF text fixture that unintentionally requested multilayer steel. The
version owner now updates both clients; the text fixture uses one layer while
the dedicated multilayer rejection remains intact. Hosted verification then
found two declared optional imports missing from the external-package registry
and a fresh pytest9.2/pytest-benchmark5.3 incompatibility. The registry now
recognizes PyVista/MkDocs. Package and root dev requirements cap pytest below9.2;
the dev profile executes the real maintained benchmark fixture, which passes
with pytest9.1.1/pytest-benchmark5.3.0. See the
[upstream report](https://github.com/ionelmc/pytest-benchmark/issues/321).

The metadata repair changed artifact bytes, so the previous pair and receipts
are explicitly superseded and preserved. All16 profiles ran again on the final
pair from one build head. Its build and review Python trees match; all327
distributed files and four build inputs match frozen source. The final exact-
wheel canonical preflight passed8814 Python tests,626 FastAPI tests and the
pinned React production build. Two earlier preflight attempts belong to the
superseded candidate; no pre-bump or local Docker duplicate was run.

An earlier confirming rebuild reproduced wheel bytes but changed sdist archive
timestamps despite identical file contents. Preserve the final qualified pair
by hash. S6 must consume those retained bytes or requalify any different bytes.

The [S5 receipt](../verification/library-s5-20261029.json) records exact hashes,
build/review identities, profiles, timings, repairs and remaining boundaries.
The [milestone PR #1040](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1040)
owns final exact-head review, required hosted checks and merge identity. Its
accepted integration completes S5. S6 publication remains unselected.


## S6 studied release plan — 29 October 2026

The owner selected S6 after S5 PR #1040 merged at
`f21fb5555c22f319f3b2399ff6aefa2fc43df309`: “thanks, now do s6.
do it efficienlty, las few release were lot of rework, so plan study and replan
then start”. This selects the established v0.26.0 TestPyPI, tag, PyPI and GitHub
Release packet. Record the effective per-target authorization after its review
conditions are satisfied. Source/table distribution permission remains passed;
Pravin Surawase is the engineering owner, without an external-reviewer gate.

### Confirmed causes and scope

The current publisher always rebuilds distributions and repeats source tests
and exact-wheel UAT. S5 already demonstrated timestamp-dependent sdist bytes.
Those defaults cannot publish the retained S5 pair unchanged. The earlier
v0.25 release also needed stale version/docs repairs; S5 exposed an omitted
client pin target and an unbounded pytest/plugin compatibility combination.
Their fixes are integrated and are not reopened by S6.

The selected repair extends the existing release owner and workflow. A compact
committed artifact record binds the retained pair, frozen Python/build inputs,
all16 qualification profiles, installed29-case UAT and qualified-base SBOM.
A collaborator-only draft GitHub Release transports the two local package files
to hosted Actions. The retained path downloads and checks these exact assets;
it never builds or reruns covered source/installed suites. Legacy source-build
behavior remains for releases without a retained record. Retained tag-push
runs validate the selected version but do not upload; production is an explicit
dispatch from the exact tag after TestPyPI. Verify-only dispatch stays read-only
with respect to registries and publication.

### One bounded implementation cycle, then publication

1. Freeze the tooling, artifact record, operational guidance and focused tests
   together. Recheck retained files against S5 hashes and frozen Python tree
   `442d4abb561e7df482438229fde36ccf381f49e8`. Keep all Python files unchanged.
   Acceptance: wrong bytes, changed build/Python inputs and incomplete UAT/profile
   evidence fail before upload; actual workflow routing keeps verify and tag-push
   paths nonpublishing. No local rebuild, broad Python suite, full check or
   duplicate S5 installation matrix is selected.
2. One tooling PR owns essential independent review, required hosted checks and
   one exact-head Weekly run. Merge this candidate with a merge commit so its
   reviewed/check head remains an ancestor of the final publication head; this
   avoids the existing exact-review guard's squash-ancestry mismatch.
3. Make one final metadata packet after accepted review: dated CITATION/CHANGELOG,
   appended release-ledger authorization, exact-candidate review receipt and
   per-target authorization JSON. Only the maintained post-review evidence paths
   change; Python remains frozen. Run publication-surface and the three target
   authorization checks. Its required PR gate applies; do not repeat Weekly for
   these bounded metadata paths.
4. Create/populate the selected version's draft release at the verified final
   publication commit. Upload the retained wheel/sdist only, then independently
   read back their bytes. Verify transport through one nonpublishing retained
   dispatch, followed by TestPyPI using the same source release ID and pair.
   Confirm TestPyPI version/files/hashes and installed import identity.
5. Create/push the exact version tag if absent, without replacing any tag.
   Dispatch production from that tag, explicitly selecting PyPI. Before uploads,
   the existing owner/review gates and exact hashes apply. Production also checks
   the exact TestPyPI registry files; draft promotion checks exact PyPI files.
   Publish the populated
   draft only after PyPI succeeds; attach verified evidence without rebuilding
   or replacing package assets. Record the final manifest, run and asset IDs.
6. Independently read back PyPI and GitHub Release files, match both retained
   SHA256 values and the tag/commit/Python tree, then perform identity-only public
   installation. Reuse covered UAT for identical bytes. Close S6 only after the
   public readback is complete; preserve all original/failure evidence.

The current registry inspection found v0.26.0 absent from both PyPI and TestPyPI.
Recheck availability immediately before irreversible upload. No release issue
closure, branch deletion, native application mutation, full-amendment claim or
professional approval is included. A failed boundary is repaired at its cause;
repeat only affected evidence and the required changed candidate checks.
