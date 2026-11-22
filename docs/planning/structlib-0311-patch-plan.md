# StructLib 0.31.1 patch findings and S0–S5 plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-11-18
**Last Updated:** 2026-11-22
**Abstract:** 0.31.1 slab scope, source verification, migration guidance and release handoff.

---

## Planning status

S0–S4 are complete for the continuous one-way slab correction. The
[specific source freeze](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1126)
pins `91a33345ad288791b9690991c4809a82dd6c93fe`. On 22 November 2026 the
owner separated the full React workbench refresh into
`codex/structlib-react-workbench-refresh`. 0.31.1 retains the slab scope,
CSV guidance predecessor and the faster release work below. S5 archive
qualification and publication authorization are pending.

Use the [library adoption and maintenance guide](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1128)
to choose evidence for affected user journeys. The
[element workflow guide](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1127)
provides release-pinned examples and explains their outcomes. Both guides
are in separate drafts. The issue register and S0 selection govern patch scope.

## Baseline and scope

Proposed patch **0.31.1** starts from published **0.31.0** at
`16c6b660a03cdfe4942e7e50d2141e4824cf5a24`. PyPI and GitHub publish the same
qualified archive hashes, and the public receipt records a fresh installation.
The initial audit covered installation diagnostics, release-facing
maintenance and hosted timing. The S0 review adds the subsequently
reproduced continuous slab verdict defect and reconciles it with the
Coding Lab and Maintenance Lab handoffs.
[Published package](https://pypi.org/project/structural-lib-is456/0.31.0/) ·
[Public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json)

## S0 scope decision

### Include in 0.31.1

- **SLAB-01 is the release blocker.** Correct the physical-strip and
  per-metre basis mismatch for the supported continuous one-way slab
  workflow. Carry the correction through the shared calculation and
  shear owners, the public built-in façade, the supplied-coefficient
  service and the affected HTTP paths. Limit the correction to continuous
  one-way slab cases. Add the focused regressions and a release note telling
  users of affected 0.31.0 results to rerun the continuous slab check with
  the corrected release.
- **DOC-01 follows the existing public-guidance work.** Reuse #1125 in its
  authorized integration order. Verify the install pin and status against
  the actual published package. Carry the slab correction and its affected
  scope into the 0.31.1 release notes and publication closeout.
- **Use the existing release checks and record their timing.** Apply the
  generated-reference check in order and prepare the verified artifact
  handoff fields early. These are the immediate parts of REL-02 and REL-03.
  Record gate, review, dispatch and retry time with the existing receipts.

### Defer or validate separately

| Item | Disposition and reason |
| --- | --- |
| FOOT-01 — isolated footing minimum steel | High-priority follow-up. The Lab reports 810.00 mm² per direction at 830 kN and 764.22 mm² at 900 kN against the same 810 mm² gross-area floor. Tagged flexure only applies that floor after an effective-depth percentage screen, and its percentage feeds preliminary shear. The checked detailing path has its own gross-area check. Both reported service calls had calculation `PASS` and overall `HOLD`. Obtain the exact fixtures and confirm the effect on preliminary shear, the final checked layout and governing status. Reopen patch scope if that evidence shows an incorrect accepted or checked result. |
| APP-01 — batch interruption | Separate application maintenance. The Lab reports an interrupted job at 1 of 64 members and a `complete` event with `IN_PROGRESS`. The tagged route breaks on disconnect, while the job manager completes only at the total count. Reproduce interruption and polling on the same job ID, preserve completed results and verify the normal-completion control. |
| SETUP-01, SETUP-02 and DOC-02 | Confirmed preflight and dependency-reference problems. Group them into the next bounded installation-maintenance change so the slab correction can qualify on its own. |
| REL-01 and release workflow redesign | Use the existing verified-parallel workflow and time its coverage step for this patch. Profile CI sharding separately and require equivalent test and coverage evidence before switching. |
| React workbench refresh | Planned in its own branch and chat. It has separate implementation and browser acceptance. |
| Human-maintainability plan, AI pilot and broader contributor work | Keep the Lab's entry-point-to-owner-to-test map as the proposal for a separate documentation pass. The slab PR can record its own owner and focused test commands. Defer moving files or tests, splitting output/transport responsibilities, and running the broader adoption pilot. #1127 and #1128 retain their own review lanes. |
| Remaining Lab and programme proposals | Retain the A40 special replay status, A51 caller binding and A52/A53 catalogue controls under their own evidence and scope. Keep FLOW04, new footing topologies and other element extensions in their programme lanes. |

The proposed scope is bound to the published `v0.31.0` commit above.
The public 0.31.0 guidance in [#1125](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1125)
merged at `675ccbebecbe7656e727b15dfef58331aea6b9ba`. The 0.31.1 candidate
uses that base. [FLOW04 #1117](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1117)
is queued after the patch and will rebind to the resulting `main` before its
affected checks and review. #1127 still owns a separate ledger change.

## SLAB-01 evidence and acceptance

The Coding Lab's `continuous-slab-strip-width.md` handoff records the
public built-in coefficient workflow returning `PASS` at **500 mm**
and `FAIL` at **1,000 and 2,000 mm** for the same deficient slab. The
unchanged cookbook control returned `PASS`. The cached wheel, reproducer
and all four tagged source files matched the hashes recorded in
`continuous-slab-strip-width-v031.json`. This S0 review checked the
existing replay and source bindings.

The kernel stores physical-strip demand under per-metre result fields.
Strength compares that demand to supplied steel per metre. The shear
caller also mixes physical width with the action and reinforcement basis.
Repair the published units at the calculation owner and align force, steel
and width at the shear boundary. Preserve physical strip geometry and
line load separately. [Calculation owner](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/structural_lib/codes/is456/slab/one_way_continuous.py#L143-L232) ·
[Shared strength checks](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/structural_lib/services/slab_api.py#L329-L378)

| Lab fixture | Expected candidate result |
| --- | --- |
| Built-in coefficient challenge at 500, 1,000 and 2,000 mm | Completed engineering `FAIL` and `area_passed=false` for positive steel at every width. Compare width-invariant positive and negative moment, required and provided steel, shear force and shear steel percentage. |
| Supplied-coefficient B02 challenge at the same widths | Width-invariant per-metre results and deficient positive steel at all widths. Preserve the physical strip line load and the submitted width. |
| Existing cookbook and applicability controls | Cookbook remains `PASS`, sufficiently reinforced control passes at all three widths, and existing coefficient selection, provenance, rejection behavior and diagnostics remain valid. |

The [frozen slab cases](../verification/library-0311-s1-continuous-slab.json)
capture the exact cookbook payload, challenge overrides, published-wheel
observations and S2 acceptance values. The deficient built-in case must
return `FAIL` with positive `area_passed=false` at all three widths. At
each width the expected values include **11.25 kN·m/m** positive moment,
**13.20 kN·m/m** negative moment, **285.920793 mm²/m** governing positive
steel, **170.391466 mm²/m** supplied and **17.6625 kN/m** shear.

| Width | Deficient on 0.31.0 | Deficient in S2 | Cookbook on 0.31.0 | Cookbook in S2 |
| ---: | --- | --- | --- | --- |
| 500 mm | `PASS` | `FAIL` | Not run | `PASS` |
| 1,000 mm | `FAIL` | `FAIL` | `PASS` | `PASS` |
| 2,000 mm | `FAIL` | `FAIL` | Not run | `PASS` |

On the one-metre basis, positive moment is `(10.5/12 + 3.75/10) × 3²`,
negative moment magnitude is `(10.5/10 + 3.75/9) × 3²`, and end shear is
`(0.4 × 10.5 + 0.45 × 3.75) × 3`. A T8 bar every 295 mm provides
`(π × 8² / 4) × (1,000 / 295)` mm²/m. With effective depth 115 mm,
these actions give a shear stress of **0.153586957 N/mm²** and a tension
steel percentage of **0.148166492%**. Physical line loads are **7.125,
14.25 and 28.5 kN/m** at the three widths. Solving section equilibrium on
the one-metre basis reproduced the 1,000 mm wheel steel values and supplied
the candidate negative steel and limiting moment expectations. The JSON
also records absolute comparison tolerances and the fields to check for
width invariance. These values define software regression acceptance.

## Other confirmed issues and release observations

| ID | Evidence on 0.31.0 | Patch action and acceptance |
| --- | --- | --- |
| SETUP-01 | `install-preflight` reports `render: installed` when only Matplotlib is available. The published extra declares both Matplotlib and ezdxf. In a fresh PyPI wheel environment with Matplotlib, JSON reported render available and DXF unavailable, and importing ezdxf failed. | Check the declared prerequisites for each reported extra. Preserve JSON keys and boolean types. Missing either rendering dependency must report render unavailable. Run equivalent partial-install controls for the two declared PDF prerequisites. Document that dependency discovery and a successful export are separate checks. |
| SETUP-02 | The same installed-wheel probe in a virtual environment named `Audit Environment` produced a repair command with an unquoted interpreter path. A POSIX shell splits the command at the space and cannot invoke the reported interpreter. | Generate an invocation that targets the reported interpreter with its full path and the intended package pin. Verify shell parsing for a spaced path and run a harmless argument-capture control. Verify the documented invocation separately for supported Windows shells if it differs. |
| DOC-01 | Published 0.31.0 and the audited `main` disagree with the Current Release page and Quick Start, which still direct readers to 0.30.0. The repair passed the GitHub gate on draft #1125. | Coordinate #1125 with the active FLOW04 candidate under the repository merge-order rule. Reuse the existing patch. Verify both default-branch guides, the publication receipt link, synchronized install pins and the strict Generic CSV span guidance once integrated. |
| DOC-02 | The runtime dependency reference says the package core requires only the standard library. The wheel declares mandatory `pydantic>=2.0`. Maintenance Lab also identified that preflight output can be mistaken for a successful capability check. | Correct the runtime dependency reference and document how to read preflight identity, exit status and dependency indicators. Compare the wording to the candidate wheel metadata and to the resolved behavior of SETUP-01 and SETUP-02. |
| REL-01 | Weekly Verification was the release's critical path. The Python coverage step ran for 36m33s out of 41m06s. | Profile the Python job on hosted runners before changing execution. Shadow-test a parallel layout only if profiling identifies a suitable split. Keep a complete test inventory, combined branch coverage and the existing 85% threshold. |
| REL-02 | Three earlier documentation runs failed on generated façade or compatibility-ledger drift. The source changes and generated release evidence reached CI out of sequence. | Use the existing generators and the hosted documentation checks in a single candidate-freeze step. Bind the actual release record before regenerating its consumers. Target zero generated-doc and compatibility-ledger failures on the next two patch candidates. |
| REL-03 | From final Weekly success to production-workflow completion took 28m08s. TestPyPI and production themselves took 1m19s and 1m47s. Measurable gaps remained around the review, authorization and dispatch handoffs. | Prepare the reviewed-head fields, retained artifact identities, release ID and dispatch inputs while verification runs. After review and authorization, continue through the existing gated sequence using one handoff. Record each transition and distinguish approval wait from execution time. |

Setup evidence comes from the installed 0.31.0 wheel in a disposable macOS
environment, outside the checkout. To reproduce, install
`structural-lib-is456==0.31.0` and `matplotlib` into a clean virtual environment
with a space in its directory name. Invoke that environment's interpreter
with `-m structural_lib install-preflight --json`. Compare `optional_extras`
with the declared dependencies and check that the first shell argument of
`repair_command` equals `interpreter`. Leave ezdxf absent for the partial
installation control. The audit did not execute the generated install command.
[Published CLI](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/structural_lib/__main__.py#L1286-L1334) ·
[Package dependencies](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/pyproject.toml#L26-L59) ·
[Runtime dependency reference](../reference/third-party-licenses.md) ·
[Release guidance repair](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1125)

## Lab reconciliation and evidence boundaries

### Coding Lab review through R02-A53

Reconciled the current queue and its recent source-bound packets against the
published 0.31.0 tag on 18 November 2026. The late static packets were pinned
to `ca4d6c72c373461490afa2f271cd3e45508c4368`. The review added follow-up
dispositions and reuse suggestions. It found no additional confirmed patch
defect within those scoped packets.

| Lab item | Evidence and plan disposition |
| --- | --- |
| R02-A23 | The required-cost evidence repair shipped. Keep the missing-cost draft and inactive-approval behavior as an existing regression control. |
| R02-A49 and R02-A50 | The named strict span, ETABS pairing, mixed force-format and equivalent numeric station findings have release fixes. Keep those controls and the unsupported-action-column controls. The separate A50-F02 station-contract proposal supplies reference cases for future work on the station model. |
| R02-A40 | Ordinary WebSocket transport passed. The safeguarded reconnect-during-in-flight scenario remains `NOT_RUN`. Keep it as an open evidence item. A separately scoped replay may change that disposition. |
| R02-A51 | The lab proposed binding snapshot row identity, concurrent actions, verified axes and analysis revision to the section request. Keep the signed-row and missing-evidence controls with FLOW04 and future caller integration. A new snapshot-to-section API needs its own scope decision. |
| R02-A52 and R02-A53 | Static catalogue reviews found no outcome-changing defect. Reuse proposed rank, budget, stale-analysis and withheld-selection controls if an admitted change touches the corresponding catalogue path. Those proposal fixtures were unexecuted in the lab review. |

The release archive record covers 53 focused intake regressions and
three original frozen controls on each exact archive. Preserve a new lab
item's ID, exact target, observed effect and evidence state during discovery.
Rebind historical observations before nominating them as patch repairs.
[Release changes](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0) ·
[Exact archive evidence](../verification/library-0310-release-artifacts.json)

### Other evidence and scope

- **Maintenance Lab.** Reconciled the 17 November handoff and workboard
  against the 0.31.0 release. ML-001, ML-002, ML-004 and ML-009 are closed
  for their original scope. The ML-012 text proposal targeted earlier
  0.30.0 publication wording and is superseded on the current source.
  The current public-pin drift belongs to DOC-01 and the existing #1125
  draft. The Pydantic reference and preflight wording belong with the
  deferred SETUP-01/02 and DOC-02 work. Check the next candidate's public
  description and links during DOC-01 closeout.
  [Published description](https://pypi.org/project/structural-lib-is456/0.31.0/) ·
  [Installation diagnostics](../getting-started/installation-notes.md)
- **Independent engineering comparisons.** Previous cage, slab creep,
  torsion-receiver and report controls informed the 0.31.0 repairs. The sampled
  two-span solver's plotted stations can miss local extrema between samples.
  The checked torsion receiver uses an exact between-station peak and the
  admitted T-flange strip uses a conservative design envelope. Preserve the
  distinction between sampled diagrams and design demand when reviewing any
  future consumer. [Receiver check](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/structural_lib/beam/physical_torsion.py#L936-L951) ·
  [T-flange demand](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/Python/structural_lib/beam/t_flange.py#L555-L588)
- **Scope.** FLOW04 and PROJECT01/02 remain open on their programme path.
  PROJECT03 retains its site-evidence gate. New footing capabilities belong
  to separate scope decisions. Use the existing case definitions and review
  boundaries.
  [Programme plan](beam-column-programme-delivery.md) ·
  [Exact candidate review](../verification/library-0310-exact-candidate-review.json)

## First-use and AI acceptance

Keep these controls for the follow-up adoption work. The 0.31.1 scope uses
the published install and affected slab cookbook checks. The AI pilot can
use one public beam journey later. On a clean install of 0.31.0,
the maintained beam recipe returned `PASS`. Removing its required width
`section.b_mm` returned structured `REQUIRED_FIELD_MISSING` for that path.
This gives a pinned baseline for the published recipe and for the pilot.
[Beam recipe](../cookbook/python/beam-design.md) ·
[Generated family contracts](../reference/family-facade-contracts.md)

| Audience or workflow | Observe and record |
| --- | --- |
| First-time Python user | Starting from one release-aligned page, install the version it names, confirm the package origin and run the documented example. Capture the command and result and any step that needed help outside the page. |
| AI-assisted developer or recurring job | Provide the same version, recipe, contract and fixture. The caller identifies the documented entry point and uses the stated units. The valid fixture returns `PASS`. The missing-width fixture returns the field diagnostic and the caller asks for the missing input. Record the actual result separately from the assistant's explanation. |
| Contributor or upgrader | When the change affects contributor setup, a fresh checkout and the documented focused check should reproduce the change. When it affects existing inputs or APIs, record the old and new behavior and the smallest migration example. |

The AI pilot uses the public recipe and its generated contract in a
disposable environment. Keep broader AI tooling, new generated surfaces and
additional element capabilities on separately selected work. The existing
[beam tool manifest](../reference/beam-tool-manifest.md) defines its own
operation and execution conditions.

## Release timing baseline and targets

The baseline spans **1h15m54s** from creation of the final Weekly run at
16:13:21 IST to clean public-install verification at 17:29:15 IST on
18 November 2026. Earlier qualification attempts and local candidate
preparation are outside this measured interval. All table times are UTC
on 18 November. Workflow durations run from creation to completion,
including any queue time.

| Checkpoint | UTC time or interval | Duration | Evidence |
| --- | --- | ---: | --- |
| Exact-head PR validation | 10:43:22–10:45:00 | 1m38s | [PR gate](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44288061714) |
| Final Weekly verification | 10:43:21–11:24:27 | 41m06s | [Weekly run](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44288057712) |
| Full Python suite with branch coverage within Weekly | 10:45:08–11:21:41 | 36m33s | [Weekly jobs](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44288057712) |
| Weekly completion to TestPyPI workflow creation | 11:24:27–11:44:32 | 20m05s | [TestPyPI workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44297424623) |
| TestPyPI workflow | 11:44:32–11:45:51 | 1m19s | [TestPyPI workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44297424623) |
| TestPyPI completion to production workflow creation | 11:45:51–11:50:48 | 4m57s | [Production workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44298365078) |
| Production workflow | 11:50:48–11:52:35 | 1m47s | [Production workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44298365078) |
| Production completion to fresh public-install verification | 11:52:35–11:59:15 | 6m40s | [Public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json) |

The exact-head PR check ran alongside Weekly on `07e1449a`. TestPyPI and
production ran on the merged release head `16c6b660`. Within the 20m05s
between Weekly and TestPyPI, review was recorded at 11:26:25 and owner
authorization became effective at 11:29:27. The authorization commit's
required PR workflow finished at 11:36:54, the PR merged at 11:38:50, and
TestPyPI was created 5m42s after merge. These timestamps measure elapsed
time between milestones. The records do not quantify hands-on work.
[Review receipt](../verification/library-0310-exact-candidate-review.json) ·
[Authorization receipt](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/docs/verification/release-publication-authorization.json) ·
[Final PR workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44295893819) ·
[Release PR](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1123)

Weekly completion to production workflow completion took **28m08s**.
GitHub published the release at 11:52:31. From that timestamp to clean
public-install verification took **6m44s**.
[GitHub release](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0) ·
[Public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json)

The earlier [Windows broker failure](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44280286349)
exposed a real defect and required fresh evidence. The three generated-content
failures were avoidable preflight rework.
[Façade failure 1](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44043674410) ·
[Façade failure 2](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44044136301) ·
[Compatibility ledger failure](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44272632653)

### Faster execution for 0.31.1

- Resolve the integration base before versioning and package build. Stage the
  retained proof before generating dependent references. Run the generated
  cookbook and compatibility checks locally before the final push to avoid
  another hosted cycle for drift.
- Build and retain one wheel and sdist from the frozen 0.31.1 payload. Run the
  installed qualification and replay the slab cases against both archives.
  Carry the exact hashes through later authorized stages. Requalify affected
  evidence for a change and preserve the reason for each retry.
- Once the final candidate and evidence are ready, run the required PR gate
  and cross-platform Weekly on the same head concurrently. Prepare the review
  packet, artifact identifiers and dispatch fields during the hosted runs.
  Bind the independent decision to the completed evidence.
- After exact review and separate owner authorization, use the existing
  TestPyPI, same-byte readback, production and clean-install sequence. Target
  dispatch within five minutes of each eligible handoff. Record required gate
  completion, review, authorization and dispatch separately so wait is
  visible. Compare with the 0.31.0 baseline of 41m06s for Weekly and 20m05s
  from Weekly completion to TestPyPI creation.

Keep the following targets for release-process improvement:

- **Weekly ≤30 minutes** after a test runner change proves equivalent on the
  same candidate, with the slowest shard and fan-in timing recorded. Compare
  at least two comparable hosted runs before relying on a speedup. Keep the
  established full job if parity or reliability is unresolved.
- **TestPyPI dispatch within five minutes of reviewed, authorized and
  merge-ready evidence**, and **production dispatch within five minutes of
  passing TestPyPI readback** when the exact owner authorization is available.
  Record required checks, approval wait, dispatch wait, workflow execution
  and public-install verification as separate intervals.
- **Zero drift failures** on the next two patch candidates and one qualified
  archive pair per frozen release payload. Preserve a fresh run for material
  changes and retain evidence about the reason for each retry.

## S0–S5 next-patch plan

### S0 — Record the scope decision

- The selected scope, evidence, deferred work and active dependencies are
  recorded above. The slab calculation owner and shared slab service own the
  repair. The release documentation owner owns the public guidance handoff.
- Bring back evidence that changes patch scope before S1 starts or as soon
  as it is established. Track the A40 special replay as `NOT_RUN`.

### S1 — Freeze the slab cases and expectations

- Frozen on the published 0.31.0 source. The
  [case record](../verification/library-0311-s1-continuous-slab.json)
  binds the saved Lab replay and the unchanged cookbook to exact inputs
  and per-metre expectations at 500, 1,000 and 2,000 mm.
- The supplied-coefficient B02 companion freezes the same three widths
  with deficient positive steel. Retain the original B02 benchmark and
  applicability checks. The overload control preserves the capacity
  diagnostic in physical-strip kN·m. The companions are planned candidate
  checks.
- The [release timing baseline](#release-timing-baseline-and-targets)
  records the hosted timings and source receipts. Use the same checkpoints
  in 0.31.1 and capture the candidate and archive identities, review and
  authorization timestamps, dispatch intervals, and retry reasons.
- This stage used the saved replay and checked fixture arithmetic for the
  S2 handoff.

### S2 — Repair the shared units and protect the entry points

- The calculation owner now solves the moment, reinforcement and shear
  demands on a one-metre basis. The shared strength check uses the same
  basis for shear force, steel area and width. Submitted geometry, physical
  line load and the physical-strip capacity diagnostic retain their units.
- Source tests confirmed completed engineering `FAIL` on the built-in JSON
  façade at 500, 1,000 and 2,000 mm. The supplied-coefficient B02 case returned
  `area_passed=false` at all three widths, its direct service's positive steel
  verdict. Both routes matched the frozen per-metre values. The cookbook
  control returned `PASS` at all three widths.
- The affected HTTP routes, applicability checks and physical-strip capacity
  diagnostic passed their focused tests. The repair PR records the commands.
  Installed archive qualification remains in S5.

### S3 — Prepare the affected guidance and release handoff

- The [continuous slab cookbook](../cookbook/python/slab-continuous-one-way.md#rerun-affected-0310-results)
  names the 0.31.0 results to rerun and includes the corrected `FAIL` example
  at all three widths. The [Unreleased note](../../CHANGELOG.md#unreleased)
  carries the same rerun scope.
- [Draft #1125](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1125)
  at `8ec9d8d784236e8e0fe75d14f2b68b0c6bb2baa6` correctly scopes the CSV
  change to strict Generic CSV import. Put a finite positive span in the
  combined file or in the geometry file of a paired import. Its examples
  use `span_mm` or `Span (mm)` for 4,200 mm and `Span_m` or `Span (m)`
  for 4.2 m. The ledger records 4,200 mm for either input. The direct
  low-level adapter still uses a 5 m visualization placeholder when the
  span header is absent. Strict import requires explicit source geometry.
  Reuse the #1125 guidance in the integration order and verify the public
  pins again after integration.
- The [release handoff](#0311-release-handoff) records what S4 and S5 must bind
  and the timestamps to collect. Stage the real retained artifact record
  before generating dependent ledger entries during qualification.

#### 0.31.1 release handoff

The proposed version is `0.31.1`. The S2 source evidence is pinned to
`c141b3ce28e838fb500aed8fa55b2d92f5c6335a`. S4 will record the reviewed
candidate after checking the integration base. Archive identities, release
authority and publication receipts are pending. [S2 source gate](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44350501845)

| Checkpoint | Record when it happens |
| --- | --- |
| Candidate freeze and retention | Record freeze time in UTC, base and candidate head/tree, Python tree, source build-input and package payload digests, and retained wheel and sdist filenames, byte counts and SHA-256 hashes. Link the artifact record and installed checks for the frozen cases. |
| Required checks | For the exact head, record PR gate and Weekly run IDs, attempt, result and creation, start and completion times. Record Python coverage step start and completion inside Weekly. |
| Independent review and authorization | Link the reviewed head and artifact-bound receipt and its `reviewed_at_utc`. Record the owner instruction and effective `authorized_at_utc` for the exact version, tag and permitted targets. |
| Integration and TestPyPI | Record final required-check completion, merged SHA and `mergedAt`. Bind the retained draft release ID. Record TestPyPI run ID and creation, start, completion and same-byte readback times. |
| Production and public verification | Record the production run ID and creation, start and completion times, PyPI and GitHub hash readbacks, GitHub `published_at` and the clean PyPI install receipt's `verified_at_utc`. |
| Retries | Record the reason, affected candidate or archive identities, workflow attempt and which evidence was rerun. |

Compare the successful sequence with the [0.31.0 timing baseline](#release-timing-baseline-and-targets).
Measure workflow execution and queue time from run timestamps, review and
authorization from receipts, and dispatch wait between steps. Compute the
critical path without adding overlapping PR and Weekly runs. Keep failed
attempts visible so retries can be compared separately. The handoff follows
the [retained-artifact release procedure](../getting-started/releases.md#retained-artifact-publication-procedure--29-october-2026).

### S4 — Review and freeze one candidate

- Review the affected workflow from install instructions to the slab result
  and diagnostic. Compare the width controls to the frozen expectations and
  review the migration and publication text. Record the governing decisions
  and supported-path boundaries in the repair PR.
- Verify generated references and the selected source-bound slab controls.
  Carry forward already qualified regression evidence for unaffected paths.
- Bind the exact build inputs and allowed post-review publication metadata.
  Confirm the candidate contains the selected work.

### S5 — Qualify the exact archives and prepare the release

- Retain one wheel and sdist from the frozen payload. Generate dependent
  evidence against the retained record and check it locally. Run the
  existing required installed qualification, exact-head hosted checks and
  cross-platform Weekly, with the selected slab and cookbook controls.
  Bind independent review to the exact candidate and archive hashes.
- With separate owner authorization, verify the retained bytes on TestPyPI
  before production. Verify PyPI and GitHub readback and a fresh PyPI
  install. After the public receipt passes, align the Current Release and
  install guidance and replay the affected public first run.
- Close with the evidence for the selected work, publication receipt if
  authorized, and measured gate, handoff and retry times. The adoption
  evidence belongs in the existing handoff for changes that affect it.

Use the existing Git and release checks for this patch. Preserve qualified
engineering scope, exact artifact identity, independent candidate review,
publication authorization and the TestPyPI-before-production order. Validate
the existing hosted evidence-reuse rules before changing any release gate.
[Git workflow](../git-automation/git-workflow-single-source.md) ·
[Publication workflow](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/.github/workflows/publish.yml)
