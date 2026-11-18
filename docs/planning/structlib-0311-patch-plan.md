# StructLib 0.31.1 patch findings and S0–S5 plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-11-18
**Last Updated:** 2026-11-18
**Abstract:** S0 scope selection and S1–S5 plan for the 0.31.1 continuous slab correction.

---

## Planning status

The S0 planning review is complete. The recommended 0.31.1 scope centers on the
continuous one-way slab false pass. Issue discovery may continue. Review new
evidence before changing the selected scope, and record its workflow, source
or artifact identity, observed effect and verification status. S1–S5 are
planned work.

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
| REL-01 and release workflow redesign | Keep the timing baseline and proposals. Select CI sharding or further workflow automation after profiling and equivalent-run proof. |
| Human-maintainability plan, AI pilot and broader contributor work | Keep the Lab's entry-point-to-owner-to-test map as the proposal for a separate documentation pass. The slab PR can record its own owner and focused test commands. Defer moving files or tests, splitting output/transport responsibilities, and running the broader adoption pilot. #1127 and #1128 retain their own review lanes. |
| Remaining Lab and programme proposals | Retain the A40 special replay status, A51 caller binding and A52/A53 catalogue controls under their own evidence and scope. Keep FLOW04, new footing topologies and other element extensions in their programme lanes. |

The proposed scope is bound to the published `v0.31.0` commit above.
FLOW04 #1117 and release guidance #1125 remain open draft paths. Recheck
their SHAs, affected paths and sequencing before establishing an
implementation candidate. The linked planning and documentation drafts
can be reviewed separately.

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

The built-in fixture's 1,000 mm software reference is **11.25 kN·m/m**
positive moment, **13.20 kN·m/m** negative moment, **285.921 mm²/m**
required positive steel, **170.391 mm²/m** supplied and **17.6625 kN/m**
shear. Freeze the independent dimensional check and comparison tolerances
in S1. These are fixture expectations for the repair.

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

Figures below come from the final successful 0.31.0 hosted sequence on
18 November 2026. The final Weekly run began at 16:13:21 IST. The clean PyPI
installation was verified at 17:29:15 IST, **1h15m54s** later. This interval
excludes earlier qualification attempts and local candidate preparation.

| Checkpoint | Observed duration | Evidence |
| --- | ---: | --- |
| Exact-head PR validation | 1m38s | [PR gate](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44288061714) |
| Final cross-platform Weekly verification | 41m06s | [Weekly run](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44288057712) |
| Full Python suite with branch coverage within Weekly | 36m33s | [Weekly workflow and threshold](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/.github/workflows/nightly.yml#L57-L62) |
| Weekly completion to TestPyPI workflow start | 20m05s | [TestPyPI workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44297424623) |
| TestPyPI workflow | 1m19s | [TestPyPI workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44297424623) |
| TestPyPI completion to production workflow start | 4m57s | [Production workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44298365078) |
| Production workflow | 1m47s | [Production workflow](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44298365078) |
| Production completion to fresh public install verification | 6m40s | [Public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json) |

The exact-head PR check ran alongside Weekly, so adding the two runtimes would
overstate the critical path. The earlier [Windows broker failure](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44280286349)
exposed a real defect and required fresh evidence. The three generated-content
failures were avoidable preflight rework.
[Façade failure 1](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44043674410) ·
[Façade failure 2](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44044136301) ·
[Compatibility ledger failure](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/44272632653)

Use 0.31.1 to capture timing with the existing workflow. Keep the following
targets for later release-process improvement:

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

- Rebind to the verified implementation base and confirm the existing Lab
  replay on the released package. Freeze exact fixture inputs, source
  basis, units, expected positive and negative demands, shear values and
  tolerances for both coefficient routes.
- Record the deficient and passing width controls, built-in coefficient
  provenance, existing B02 benchmark and the capacity-exceeded diagnostic
  control. Preserve the original release timing receipts for comparison.

### S2 — Repair the shared units and protect the entry points

- Correct physical-strip and per-metre reporting at the calculation owner.
  Align shear force, steel area and strip width in the shared strength
  service. Preserve public fields, coefficient applicability and submitted
  geometry.
- Verify the public JSON façade, the supplied-coefficient path and affected
  HTTP routes. Require invariant per-metre results and a completed
  engineering `FAIL` at each challenged width. Keep the passing and
  rejection controls. Record the narrow commands in the repair PR.

### S3 — Prepare the affected guidance and release handoff

- Explain which continuous slab results need rerunning and show the checked
  example's expected result. Reconcile #1125 in the existing integration
  order for the public install and CSV guidance.
- Run the existing generated-reference checks when their inputs are ready.
  Stage the retained artifact record before generating its ledger entries.
  Prepare the handoff fields and record gate and review timestamps.

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
