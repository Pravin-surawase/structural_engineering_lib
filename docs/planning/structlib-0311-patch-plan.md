# StructLib 0.31.1 patch findings and S0–S5 plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-11-18
**Last Updated:** 2026-11-18
**Abstract:** Bounded 0.31.0 audit and next-patch plan for setup diagnostics, release guidance and release-cycle efficiency.

---

## Planning status

Issue discovery is open. This working draft records the evidence and proposed
fixes collected so far. Add new findings with their affected workflow, source
or artifact identity, observed impact and verification status. S0 will select
the patch scope after discovery and review. The later stages describe how to
implement and qualify the selected work.

## Baseline and scope

Proposed patch **0.31.1** starts from published **0.31.0** at
`16c6b660a03cdfe4942e7e50d2141e4824cf5a24`. PyPI and GitHub publish the same
qualified archive hashes, and the public receipt records a fresh installation.
The audit covered installation diagnostics, release-facing maintenance,
selected Coding Lab and independent comparison findings, and actual hosted
release timing. It confirmed two setup defects and operational release problems.
The scoped review found no new confirmed engineering calculation defect.
[Published package](https://pypi.org/project/structural-lib-is456/0.31.0/) ·
[Public install receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.31.0/public-install-verification.json)

## Confirmed issues and proposed fixes so far

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

- **Coding Lab.** R02-A23's required cost evidence and R02-A49/A50's span,
  force-format and station-identity findings have release fixes and applicable
  archive evidence. R02-A40's ordinary WebSocket transport repair passed.
  Its safeguarded reconnect-during-in-flight replay remains `NOT_RUN` and
  may be tracked as a separate acceptance check. Retain the previous controls
  as regression inputs. [Release changes](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0) ·
  [Exact archive evidence](../verification/library-0310-release-artifacts.json)
- **Maintenance Lab.** The dependency wording and preflight interpretation
  were checked again against the released code and metadata. The historical
  ML-012 proposal targeted earlier 0.30.0 publication prose. The 0.31.0 PyPI
  description identifies its current version and places 0.30.0 under its
  historical feature heading. Review the next candidate's package description
  for accurate current status and release links during the DOC-01 follow-through.
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
  PROJECT03 retains its site-evidence gate. Any new footing capability or
  snapshot-to-section API belongs to a separate scope decision. Use the
  existing case definitions and review boundaries.
  [Programme plan](beam-column-programme-delivery.md) ·
  [Exact candidate review](../verification/library-0310-exact-candidate-review.json)

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

Proposed timing targets for the next patch:

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

| Stage | Work | Exit evidence |
| --- | --- | --- |
| **S0 — Bind scope and ownership** | When discovery is complete, recheck the published baseline, reconcile new evidence and decide which SETUP, DOC and REL items belong in the patch. Confirm ownership of #1125 and capture the sequencing decision on #1117 before an integration write. | Record the selected items, deferred items and exact baseline. Recheck historical findings against the selected baseline before admitting them. |
| **S1 — Freeze reproducers and timing controls** | Preserve the two installed-wheel setup probes, partial/full extra and plain/JSON controls, spaced interpreter paths, and the original timing receipts. Profile Weekly's slowest tests and coverage overhead before selecting a parallel runner design. Record comparable runner and dependency identities. | Positive and negative controls have expected results. The timing baseline records CI and handoff stages independently. |
| **S2 — Fix setup and current guidance** | Repair the preflight dependency mapping and command formatting. Update dependency and installation guidance in the same packet. Reconcile #1125 and validate the live 0.31.0 guidance after integration. | Focused tests pass through the public CLI. The advertised registry version, docs pins and migration guidance agree. |
| **S3 — Remove release rework** | Apply the existing release-generation and checking sequence before artifact qualification. Stage the appropriate artifact record before generating the compatibility ledger. Prepare the S5 handoff packet early. If profiling supports it, trial balanced hosted Python shards with FastAPI and React work scheduled independently. | Generated checks pass before CI. A shadow comparison proves the same selected test IDs, successful required jobs and combined coverage with the 85% gate. A missing or failed shard must still prevent a pass. |
| **S4 — Freeze one candidate** | Review the affected paths together. Verify generated docs, source-bound CLI diagnostics and any shadow CI results. Recheck covered files and publication text before building. Keep A40 special replay status explicit unless a safeguarded run produces new evidence. | Source review fixes the build input tree and the allowed post-review metadata scope. The supported engineering cases and publication gates remain as specified in the existing policy. |
| **S5 — Qualify and hand off the exact pair** | Build a single wheel and sdist from the frozen payload and retain both hashes. Regenerate dependent release evidence against the retained record and check it locally. Run existing installed qualification and acceptance profiles, the S2 CLI controls, exact-head required CI and required cross-platform Weekly. Obtain independent review of the exact candidate. With the owner's authorization for the exact release, verify the same bytes on TestPyPI before production publication. Verify PyPI/GitHub readback and a fresh PyPI install. Record publication and synchronize the Current Release and install guidance once the public check passes. | Candidate sign-off binds source, archive pair, gates, scope and timing. Publication requires its own owner authorization. Close the patch after the public receipt, guidance and actual elapsed intervals are recorded. |

Use the existing Git and release checks for this patch. Preserve qualified
engineering scope, exact artifact identity, independent candidate review,
publication authorization and the TestPyPI-before-production order. Validate
the existing hosted evidence-reuse rules before changing any release gate.
[Git workflow](../git-automation/git-workflow-single-source.md) ·
[Publication workflow](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.31.0/.github/workflows/publish.yml)
