# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-08-30 — resolved-merge repair PR #911 is accepted; LIB-PRO-015 freezes the refreshed professional API/documentation renewal plan

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items
- **Streamlit is retired** — React is the only active UI. Do not restore its runtime, dependencies, hooks, or feature work; legacy files are reference-only until removal.

---

## Maintenance Recovery Dashboard

> Maintenance baseline comes before feature work. Preserve the inherited April worktree before cleanup.
> Consolidated evidence: [maintenance recovery audit](audit/maintenance-recovery-audit-2026-08-07.md).

| ID | Task | Priority | Status | Exit condition |
|----|------|----------|--------|----------------|
| MAINT-001 | Preserve April worktree and recover the Mac Mini development baseline | P0 | ✅ DONE | GitHub/SSH, Python/Node, Colima/Docker, and release preflight pass; PR #676 required checks are green |
| MAINT-002 | Repair nightly QA and stale import E2E response-envelope assertions | P0 | ✅ DONE | Nightly command is valid; import/sample/dual/batch scripts pass against the live API |
| MAINT-003 | Rebuild dependency and security baseline | P0 | ✅ DONE | Reproducible environment plan exists; npm/Python high-risk findings are upgraded or explicitly accepted |
| MAINT-004 | Make `run.sh check` the canonical truth source and repair stale indexes/scanners | P1 | ✅ DONE | Canonical check, audit, health, API manifest, schemas, hooks, and registries agree |
| MAINT-005 | Restore frontend confidence and define the v0.21.7 finish line | P1 | ✅ DONE | Live import→design→3D→dashboard→export flow and byte-level artifacts pass; v0.21.7 preflight is ready |
| MAINT-006 | Enforce low-token Codex operation | P1 | ✅ DONE | User-selected parent model is preserved; Terra-first advisory routing, bounded worker packets, two-subagent cap, and quick-gate check pass |
| MAINT-007 | Refresh onboarding, agents, tools, and usage telemetry | P1 | ✅ DONE | Terminal-only PR status, current bootstrap/counts, complete 14-skill discovery, honest usage checkpoints, and focused regressions pass |
| MAINT-008 | Compact CI, maintenance controls, and agent entry paths | P0 | ✅ DONE | Four-lane workflow, truthful `PR Gate`, native Codex Git/GitHub lifecycle, and retired unsafe wrappers are merged |
| LIB-PRO-001 | Remediate the historical professional library audit without repeating completed maintenance | P0 | ⏸ SUPERSEDED | T0 and R1-R8 remain historical evidence; later direct public-route replay reopened the release hold under LIB-PRO-003, so this row is not a current professional-readiness claim |

### Maintenance evidence captured 2026-08-07

- Git object database and transferred sample data are intact; local and remote `main` both point to `fa854e0f`.
- Inherited worktree: 73 modified tracked files plus 47 untracked files before session startup; 70 Python diffs are AST-equivalent formatting changes.
- Final release preflight: 5,159 Python tests passed, 3 skipped, 6 deselected; 336 FastAPI and 146 React tests pass. A clean built-wheel environment independently passes 5,120 tests, 41 skips, 6 deselections, and packaged CLI workflows.
- Repository release gates were green before PR #676 was safely merged. GitHub CLI/SSH, Colima, and Docker are recovered. React's 17.74% statement coverage remains an accepted stabilization risk outside this maintenance scope.
- Canonical validation is 28/28 checks, 22/22 audit readiness, 100/100 health, and 96% parity. Feedback is 22/23 resolved; only the existing tester-output recurrence watch remains open.
- MAINT-005 checkpoint `6f119132`: direct tests now cover 60/60 routes; parity is 96%. The live 153-beam import → auto-design → 3D editor → dashboard path passes with no new browser warnings.
- Runtime/product repairs from the browser sweep: the launcher selects Node 24 from `.nvmrc` and kills listeners only; canonical compliance utilization replaces misleading `Mu/Mu_lim`; imported spans are rounded; dashboard and BOQ steel totals agree.
- MAINT-005 export actions remain validated. ADOPT-001 Packet F later bound the tracked 153-beam dataset and actual geometry to a reproducible BOQ record: 1,928.49 kg steel and 48.7319 m³ concrete. The older 2,663.4 kg / 114.8 m³ checkpoint is superseded because it was not dataset- or calculation-identity-bound; see `docs/verification/bundled-sample-boq-evidence.md`.
- Release automation now selects `.nvmrc` Node 24, evaluates reclaimable macOS memory, and installs wheel `[dev]` dependencies for isolated verification. `./run.sh release preflight 0.21.7` reports READY TO RELEASE with zero warnings.
- GitHub CLI API and SSH auth now pass end to end. Colima's stale transferred-disk lock was released only after Lima confirmed the VM was stopped; the existing VZ disk was preserved and Docker is healthy.
- Docker release preflight passes with 5,158 Python tests, 8 skips, 6 deselections, and a Node 24 React production build. That evidence was merged through PR #676.
- Low-token policy checkpoint `6e8e4a31` defaults Codex to Terra/medium, disables Fast mode, caps subagents at two, replaces full-history handoffs, and adds a ninth canonical quick check.
- Authenticated analytics showed 1,858 turns in the one-month view: 1,065 GPT-5.5, 635 Sol, 96 Luna, 43 Terra, and 19 older models. On 2026-08-10 the user confirmed Luna is unavailable; the checked-in picker now starts on Terra and approval-gates Sol.
- MAINT-007 removed the default `gh pr view --web` side effect from `./run.sh pr status`; browser opening now requires `--web`. Session checkpoints record model, reasoning, elapsed time, parent/subagent counts, optional dashboard values, verification, and Git state without estimating tokens or cost.
- MAINT-007 closeout: 32 focused regressions, Ruff/Black, quick 9/9, full 29/29, audit 22/22, and health 100/100 pass; folder indexes and the 282-document global index are current.
- PR #676 was safely squash-merged and synchronized; clean MAINT-008 baseline commit is `755ac9fb`.
- MAINT-008 skills lane: all 14 skills have valid frontmatter and current commands, `skill_tiers.json` is the single catalog, registry routing/counts validate, the four-layer architecture checker is green, missing API discovery fails closed, release verification selects exact artifacts, and evolution proposals stop below 15 collected sessions.
- PR #689 was safely squash-merged at `b611f6b3`; Packet A PR #690 was merged at
  `ce3a2c5b`, and ruleset `11390214` now requires its passing `PR Gate`.
- Packet B maps the 13 superseded workflow signals, removes those files, and
  retains `fast-checks.yml`, weekly/manual `nightly.yml`, corrected `publish.yml`,
  and `deploy-docs.yml`. No release or publication was run.

### Recovery progress

- Recovery checkpoint `b28ee4e3` is pushed on `task/MAINT-001`.
- Python editable metadata/module version repaired to v0.21.6; Node 24.19.0 installed keg-only and React passes 139 tests, lint, and build on it.
- Quick canonical gate is 8/8 green; import validation resolves all 3,248 scanned imports.
- MAINT-001 is complete. Commit `242ba8ce` removed the empty-link inputs, replaced the crawler-blocked pricing URL, and pinned Ruff 0.15.8 across active install surfaces; all PR #676 checks pass.
- MAINT-002 validation: 18/18 live import E2E checks, 153/153 sample beams, and 1,056/1,056 internal documentation links pass.
- MAINT-003 validation: a clean Python 3.11 environment has zero known vulnerabilities; npm dropped from 13 findings to one documented RSC-only advisory. The later final gates pass 5,159 Python, 336 FastAPI, and 146 React tests.

---

## Current Release

| **Current public release** | v0.24.0 | ✅ NORMAL SOFTWARE RELEASE — immutable tag and non-prerelease GitHub/PyPI artifacts recorded; Beta maturity and supported-scope limitations remain |
| **Release candidate** | — | No later candidate is selected or authorized |
- **Release evidence:** tag target `e66de6ef`; public wheel SHA-256 `7b5bc0b6…a093`; public sdist SHA-256 `d530f10c…6640`; production workflow `33150227524`, exact-wheel UAT, and isolated public install are green
- **Strategy:** Incremental micro-releases — each focuses on one quality dimension (tests, API, security, performance)
- **Focus:** API introspection → security hardening → performance baselines → stabilization
- **Target:** keep later roadmap work inactive until separately activated
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution
- **Architecture:** [unified-architecture-v1.md](architecture/unified-architecture-v1.md) §20 — complete v0.21.5→v1.0 roadmap

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | ✅ Released (v0.20.0) | Batch design React UI, compliance checker, cost optimizer, 86 API tests |
| **v0.21** | React UX + Library Expansion | ✅ Released (v0.21.0) | Editor-centric UX, BeamDetailPanel, FloatingDock, PDF export, load calc, BOQ, torsion |
| **v0.21.4** | Stabilization | ✅ Released (v0.21.4) | CostProfile fix, float sanitization, footing API, bearing check, torsion shim |
| **v0.21.5** | Test Coverage & Regression Prevention | ✅ DONE | Golden vectors (42+), contract tests (18), 99% branch coverage |
| **v0.21.6** | API Quality & Introspection | ✅ Released | check_code(), show_versions(), OpenAPI freeze, limitation docs |
| **v0.21.7** | Security Hardening | ✅ READY FOR RELEASE | Input validation, error sanitization, packaging gates, CI hardening |
| **v0.21.8** | Performance & Property Testing | 📋 PLANNED | Benchmarks, Hypothesis, performance baselines |
| **v0.22.0** | Stabilization Release | 📋 PLANNED | API naming convention (Batch 3), provenance, SP:16 verification |
| **v0.23** | Bounded IS 456 slabs + footing completion | ✅ ALPHA RELEASED | Case-qualified development preview; professional review remains a final stable/engineering-use gate |
| **v0.24** | Multi-Code Infrastructure and bounded IS 456 external preview | ✅ NORMAL SOFTWARE RELEASED | `v0.24.0` contains accepted S0/B0/F0/R0 and the cumulative audit; normal distribution does not claim stable API, complete IS 456, or professional approval |
| **v0.25** | ACI 318-19 Beam | 📋 PLANNED | ACI beam flexure + shear, PCA Notes ±0.1% benchmarks |
| **v1.0** | Production Multi-Code | 📋 PLANNED | IS 456 complete, ACI 318 beam+column, EC2 beam, API stability guarantee |

### React migration status

| Feature | React | API Ready | Priority |
|---------|-------|-----------|----------|
| Single beam design | ✅ | ✅ | Done |
| CSV import (40+ cols) | ✅ | ✅ | Done |
| 3D visualization | ✅ R3F | ✅ | Done |
| Export (BBS/DXF/Report) | ✅ | ✅ | Done |
| Dashboard insights | ✅ | ✅ | Done |
| Rebar suggestions | ✅ | ✅ | Done |
| **Batch design UI** | ✅ | ✅ streaming.py | Done |
| **Compliance checker** | ✅ DesignView panel | ✅ insights.py | Done |
| **Cost optimizer** | ✅ DesignView rebar | ✅ canonical flexure/shear/cost service | P1 PR #853 — real fields/decisive inputs implemented; hosted FastAPI repair rerun pending |
| **AI Assistant** | -- | Partial | ⏸ Deferred |
| Learning center | -- | -- | 🟢 Low |

### v0.21 Remaining Items (Library Expansion)

| # | Task ID | Feature | Status |
|---|---------|---------|--------|
| 7 | TASK-520 | Report/3D Test Coverage | ✅ DONE (71 new tests) |
| 8 | TASK-521 | Beam Rationalization | 📋 [→ v0.22.0] |

> v0.21 React UX Overhaul (TASK-522–528, all ✅) and Library Expansion items 1–6 (TASK-514–519, all ✅) archived to [tasks-history.md](_archive/tasks-history.md).
> Detailed specs: [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) Part 2.

---

## Active

`LIB-PRO-012-S0-P0-SAFETY-CLOSURE` and its required post-merge repair are
accepted. Repair PR #878 reviewed candidate
`1485da58297379a65882be7e4be8a23d6d86117d` and merge
`49c2fe4553e923a7433ca0a5fa28ea364956ae30` share exact tree
`704190f7322b8c29bc4a85036d7ade54d355f306`; hosted run 33088194292 passed all
required changed-path checks. The current exact-wheel A0 replay confirms that
unused `rebar_layers`, unsafe BBS/DXF span fallback, coercion, and extra fields
remain fail-closed without changing valid beam, torsion, BBS, or engineering
`FAIL` outcomes. The public `0.24.0a1` artifacts predate S0 and remain a
separate held artifact identity.

`LIB-PRO-013` owns the whole-library renewal audit. Its
[master plan](planning/lib-pro-013-whole-library-renewal-audit-plan.md) defines
the truth freeze, audit-of-audits, external-user/API, engineering-evidence,
application, package/dependency, test, Git/CI/release, agent/skill/automation,
efficiency, retention, and peer-comparison lanes. The consolidated
[A0 audit](verification/lib-pro-013-a0-renewal-audit.md) completes the initial
read-only universe through C2 at exact source `49c2fe45...` / tree
`704190f...`: all 42 Section 7 domains are owned and disposed, 16 deduplicated
findings are routed, and no new current-source P0 was reproduced. The plan and
audit were read-only at that snapshot. A0 PR #879 subsequently merged as
`db6905c3` with exact final-candidate/merge tree `ee28473e`. The
[owner sequencing decision](verification/lib-pro-013-owner-sequencing-decision.json)
now authorizes B0, then F0 and R0 after their dependency gates. The derivative
[A0 execution plan](planning/lib-pro-013-a0-execution-plan.md) groups the
15–24 engineer-day audit into four evidence passes inside one read-only
session, branch, candidate, PR, and hosted cycle. Professional review is not an
intermediate programme gate. The newer owner decision keeps one practicing-
engineer review deferred until the owner declares the intended library
complete; R0 integration alone does not trigger that review.

`LIB-PRO-012` remains the remediation specification and scope authority. S0
closes the mapped beam/detailing/BBS, torsion, column, typed-input, identity,
and existing REST v1 safety boundary. A0 routes common/canonical/downstream
contract convergence to B0, family construction/facade convergence to F0, and
documentation/generated/package/cumulative artifact/evidence closure to R0.
Packets C-E are integrated through B0 candidate `96d7cc93...` and merge
`44ef7bc4...`, with exact shared tree `12a6f683...`; PR #880 and hosted run
`33100194911` passed every required changed-path check. The strict canonical
Python beam contract is frozen, exact v1/v2 parity passes, named downstream
consumers fail closed without partial artifacts, the final focused selection
passes 451 cases, the post-hook invalidated-path replay passes 416 cases, and
the source-free B0 wheel `25eacdd7...a803942f` passes the 29-case UAT with 15
registered CLI commands. F0 Packets F1-F3 are accepted through PR #882 at
merge `59ef74c0ad44da6c313a2ca943c7362158230f38`, tree
`295c7a61d6781a749796e015e58a1fc38b4fc20f`: 13 frozen facade route/contract classes have strict grouped
construction, common typed result/error semantics, generated schemas and
compatibility ownership, and valid/invalid exact-wheel recipes. The 143-case
focused owner/golden/publication selection and the exact wheel
`797dfd9a...d73f78f` pass without changing the accepted B0 owners. The
immutable candidate passed its hosted cycle and merged unchanged. The separate
Windows source-lane rebind receipt is integrated through PR #883 at merge
`879d32ca...`, tree `c7ebc826...`. R0 Packets G-I are accepted through PR #884
at merge `b1ba36e3...`, tree `81854f06...`:
13 generated cookbook journeys, 28 advertised Python/CLI entries, zero unowned
promoted request fields, 7,165 broad Python and 526 FastAPI tests, and the
source-free wheel `53e0485b...c39d4` pass. The immutable candidate passed its
hosted cycle and merged unchanged. Exact `v0.24.0` was subsequently published
as the normal software release; this does not retroactively make release an
F0/R0 gate, and the single engineer review remains deferred until the owner
declares the intended library complete. Shared
validation, facade, result, manifest, generated API, documentation, task, and
session owners remain single-writer surfaces.

`LIB-PRO-014-POST-R0-CUMULATIVE-AUDIT` audited the exact 30-commit, 244-file
delta from public tag `v0.24.0a1` (`71b70652...`) through accepted R0 merge
`b1ba36e3...`. The engineering/facade replay found no calculation-owner,
golden-outcome, supported-family, or contract defect. Two main-process control
defects were confirmed and repaired at their roots: stale/masked API inventory
counts, and a full-stack launcher that bypassed the worktree-aware Python
runtime. The changed Python selection passes 1,050 tests, changed FastAPI
selection passes 200, React passes lint/283 tests/build, all 13 family journeys
  and 18 canonical beam checks pass, and the real browser/default-beam/BBS route
  plus full-stack start/stop journey pass. PR #885 merged unchanged at
  `e7956f78...`, tree `78494828...` after required hosted checks passed. The
  audit's Alpha-version recommendation was superseded by the owner's later
  exact `v0.24.0` normal-software-release decision.

`RELEASE-0240-STABLE-SOFTWARE` is the active single-writer release task. It
separates a normal final package version from stable-API, professional,
engineering-use, and construction-use claims; retains the Beta maturity label;
and records broader library development plus one cumulative practicing-engineer
review as still in progress. Local wheel `64343a33...40d1` and sdist
`32fb86a0...322c` pass Twine, clean import, CLI, 29/29 exact-wheel UAT cases,
28 advertised entries, and 13 family-facade entries. Immutable candidate,
hosted checks, exact authorization, TestPyPI, unchanged merge, tag, publication,
and public verification remain.

The [LIB-PRO-013 Windows evidence lane readiness receipt](verification/lib-pro-013-windows-evidence-lane-readiness.json)
records `READY_FOR_FUTURE_WINDOWS_EVIDENCE_SETUP_ONLY` at exact B0 merge
`44ef7bc4...`. The task-owned
[F0 rebind receipt](verification/lib-pro-013-windows-f0-rebind-evidence.json)
is integrated through PR #883 at merge `879d32ca...` and proves the separate
linked Windows worktree and repository-local Python source binding at accepted
F0 merge `59ef74c0...`, tree `295c7a61...`. It ran no R0, Excel, ETABS,
workbook, model, calculation, or engineering acceptance. R0 did not open or
mutate that protected future application-evidence lane.

The owner removed the fixed documentation-count limit. `check_docs.py` now
reports the active count only as an informational inventory; canonical topic
ownership, duplicate search, append-first updates, metadata, lifecycle, index,
and link checks remain enforced. The deprecated `--budget` spelling is a
non-failing compatibility alias for `--inventory`.

`MAINT-0136` is locally complete through its exact authorized cleanup boundary.
Phase 1 PR #874 merged at reviewed head `37b36785`; Phase 2A removed the exact
30-cache manifest, Phase 2B-R proved the owner-only Google Drive recovery
package, Phase 2B-W retired exactly 63 worktrees without force, and Phase 2C
removed exactly four local and two matching remote branches. The consolidated
successor preserves every frozen commit and is reconciled with merged
`origin/main` without rewriting history. No Phase 2D was defined and no further
branch, worktree, archive, tag, Codex-ref, protected-source, or alias deletion
is authorized by this closeout. Hosted publication and merge of the immutable
consolidated candidate are the external completion gate.

`RELEASE-SMOOTH-001` is the active release-control task. It converts the
`v0.24.0a1` delays into a single-candidate next-release flow: fail-fast final
metadata validation, one bounded post-review packet, clean candidate citation
state, no broad pre-mutation suite, and public identity-only verification with a
bounded propagation retry. It does not select, authorize, tag, or publish a new
version. The focused local release-control batch is green after one exact stale-
expectation repair, and the one quick gate passed 10/10. Only impact-mapped PR
checks remain. Stable/engineering-use wording, INDIA-4 qualified review,
professional approval, later scope, and cleanup remain separate held decisions.

`INDIA-3-IS13920-M0` merged through PR #869 at `b85d514e` with exact
candidate/merged tree `8a45afa4`. Beam, rectangular-column, and directional
joint contracts are accepted only as bounded source-aligned software. The
[status clarification](verification/lib-pro-009-is13920-status-semantics.json)
records replay `PASS` separately from beam `NOT_EVALUATED`, the bounded column
benchmark `PASS`, and the represented joint check `FAIL`. Every family retains
`qualified_review_required=true`; IS 13920 wall/foundation, IS 875/1893,
INDIA-4 review, release, and professional use remain held.

`LIB-PRO-006` merged through PR #851 at `2d6df18e`. It confirms the practical
10 m x 4 m audit arithmetic and fail-closed footing-detailing `HOLD`, adds a
maintained runnable example and explicit builder, exports the workflow from the
package root, promotes one deterministic governing reason, and separates
component/composed-workflow discoverability from tool eligibility.

`LIB-PRO-007-G0` merged through PR #852 at `a6d47a85` and freezes the successor
product boundary before any additional engineering scope. P1 repairs the
outcome-changing cost optimizer; P2-P4 close
the selected beam-bar, footing-anchorage, and explicit-action gravity gaps; P5
freezes one hash-bound ETABS exported-data snapshot; P6 proves identical
Python/REST/React/Excel results; P7 converges compatibility only after canonical
destinations work. It does not require every library helper to become an HTTP
route and does not authorize a broad legacy deletion.

`LIB-PRO-007-P1` merged through PR #853 at `9119cadc`. It applies exact material grades, effective-depth basis,
section grid, utilization threshold, unit rates, factored shear, and supplied
stirrup area. It rejects infeasible shear and unsupported objectives, derives
all response engineering fields from the stable result, and preserves the
explicit boundary that stirrup mass is not part of the current cost quantity.
PR #853's first hosted run exposed and repaired one integration defect:
an infeasible optional smart-cost search now preserves the canonical beam
`FAIL`, returns no cost advice, and publishes an explicit warning. All required
hosted checks passed on the repair head before the unchanged tree was merged.

`LIB-PRO-007-P2` merged through PR #854 at `e4d86d13` with exact
candidate/merged tree `305d2165`. It adds an explicit bar-selection and
source-referenced supplied-bar basis, corrects clear-spacing truth and boundary
rounding, and proves calculated-demand `HOLD`, inadequate supply `FAIL`, and
complete bounded `PASS`. The maintained open-hall example recommends bars but
remains `HOLD` because no project bar schedule is supplied.

`LIB-PRO-007-P3` merged through PR #855 at `0ea3e2d4` with exact
candidate/merged tree `d3e3e9a3`. It fixes the shared standard U-hook anchorage
value, adds an exact unrounded straight-plus-bend/hook evaluator, and extends
the isolated-footing package, gravity, and REST contracts with explicit
approved geometry. Supported straight, 90-degree bend, and U-hook vectors
reach decisive `PASS` or `FAIL`; missing or unsupported arrangements remain
`HOLD`.

`LIB-PRO-007-P4` merged through PR #856 at hosted commit `426d401b` with exact
merged tree `a5b01272`. It accepts only
caller-assigned full-span wall/beam line, beam point, and supported slab-area
actions with unique source identity, reference, case, units, destination, and
basis. Each action receives source/destination ledger entries and exact
reconciliation; no IS 875 generation, lateral action, or destination inference
is added.

`LIB-PRO-007-P5` merged through PR #857 at hosted commit `6d533b6f` with exact
merged tree `d3bbaeb2`. It converges separate lossless ETABS geometry/force CSVs, EDB/E2K
identity, selected-table archive hashes, units, local axes, one exact result
selection, stable ETABS `UniqueName` member IDs, and exhaustive `ACCEPTED` /
`APPROVED_EXCLUSION` / `BLOCKED` source-row dispositions into one deterministic
snapshot. Only an accepted snapshot emits existing canonical beam requests.
Manual table export remains valid when the trial API is unavailable. Live
At P5 closeout, live ETABS control, EDB parsing, analysis changes,
save/write-back, P6/P7, INDIA-3 engineering, release, and professional approval
remained held.

`LIB-PRO-007-P6` merged through PR #858 at hosted commit `6cb47221` with
reviewed candidate `9647fedd` and exact candidate/merged tree `d2b3efa3`. It
repairs the project-batch loss of a derived effective-depth
basis, then proves both P5 fixture beams preserve normalized input identity,
canonical result identity, governing status, and issues across Python, REST,
React, and Excel. React now rejects envelope/evidence identity disagreement and
stales retained results when imported source metadata changes. The maintained
gravity example preserves its workflow-result hash, governing `HOLD`, and issue
identity through Python, REST, and React. No transport receives a structural
formula; Excel is not expanded into a gravity calculator.

`LIB-PRO-007-P7` merged through PR #859 at hosted commit `823b3989`, with
reviewed candidate `c9589815` and exact candidate/merged tree `e5b1e9ee`. Its
deterministic ledger reconciles all 620 live root/service/legacy
facade projections, records exact canonical object or namespace-symbol owners,
and accounts for maintained callers with no ambiguous route. Maintained source,
scripts, examples, and current documentation use canonical owners or the
deliberately supported package-root facade. The four older ETABS helpers remain
`HELD_COMPATIBILITY` and cannot be described as accepted P5 snapshots. No
public export/signature/file is removed, no retirement candidate is activated,
and no second structural calculation path was found.

`LIB-PRO-007-M0` merged through PR #860 at hosted `3e979687`, from reviewed
candidate `eb92db48`, with exact candidate/merged tree `f673e604`. The
cumulative Python suite passed 6,934 tests, FastAPI passed 491, React passed 283
plus lint/build, architecture/import/parity were green, and exact wheel
`0a42d90e…347ca` passed source-free tests, transport identity, CLI flows, and
all 29 negative-UAT cases. The production website loaded catalogue 1.3.0,
recalculated quick beam with a changed calculation identity, and ran the
maintained zero-residual gravity example with truthful `HOLD 6 / PASS 5`.
Frozen quick/full/hooks, session end, and all required hosted checks passed
before the unchanged candidate tree merged.

`MAINT-0134` assigns cross-agent policy to `AGENTS.md`, composes Claude
through `@AGENTS.md`, keeps a concise standalone Copilot baseline, retires
legacy executable routing, requires exact scoped-rule projection parity, and
validates session/runtime/governance semantics. PR #850 is merged at the exact
`69c09cc7` base used for LIB-PRO-006.

`MAINT-0133B-PACKET-A` merged through PR #848 at `f24c3904`. The owner then
selected `INDIA-3-G0` and authorized use of additional local IS-code PDFs under
the existing non-distribution boundary. The durable tracked source boundary
merged through PR #849 at `40aa5864`, and the ignored private library remains
preserved. The older candidate `9c976b1f` is retained but not cherry-picked:
its shared session/task handoff files predate M0 and its base omits the later
product packets. INDIA-3-G0 now runs on fresh branch
`codex/india-3-g0-truth-audit` from exact hosted `3e979687`.

INDIA-2 remains administratively complete within its recorded accepted/held
boundary. The reproduced public-route safety packet and M0 are integrated.
INDIA-3-G0 merged through PR #863 at `c0e34235`: beam, column, and joint each
require a separate repair packet. `INDIA-3-SOURCE-META-R1` merged through PR
#864 at `20b60a04` and corrected only ignored private catalogue metadata while
retaining all 25 documents, 27 aliases, 732 cached pages, six IS 13920
documents, and four standalone amendment copies. `INDIA-3-JOINT-R1` corrects
only the code-namespace SCWB contract and direct tests; it adds no service,
route, React/Excel surface, support promotion, package version, release, or
professional approval.

`LIB-PRO-008` merged through PR #862 at `3bcc3422`: torsion and WebSocket
checking fail closed on invalid or missing engineering inputs; compatibility
scanning uses the Git-maintained source set, the 1,502-caller ledger is current,
and documentation CI owns its freshness; single-loop stirrup geometry rejects
unsupported multi-leg output. Its reviewed and merged trees are equal.

`LIB-PRO-003-A` was accepted and exact-tree merged through PR #832 at
`e7698a63b86d2db6db2f3970871122af1ce562f6`; Packet B was accepted and
exact-tree merged through PR #833 at
`e19b757ccb9922061369a236501f037ec20503ab`; Packet C was accepted and
exact-tree merged through PR #834 at
`027554457c58303f435dc4a9940dc683def22895`. `LIB-PRO-002-G0` was
independently accepted and merged through PR #812 at
`55104e11257937b0a42fb06f931a70b8484cef39`. Packet A was independently
accepted and merged through PR #814 at
`3986935ecb473c1f9d56dec44aeb4218d9192f84`; Packets B-G merged through PR #815
at `fe4ab025419b834c6d0f840e9492c0604ae74201`. Packets I-J are software-
complete. Alpha `v0.23.1a2` was published from tag target `09861d3d` on
2026-08-17; its public wheel is SHA-256 `279b8270…43a9`. Later Gravity/E1
merges are not part of that immutable artifact and require a new version before
any future package publication.

The separately accepted integrated component/gravity program completed A1,
A2, B1, and B2 through PRs #822-#825. Building Gravity Workflow V1 is merged at
`c127e4b2`. E1 then passed its real installed-desktop-Excel journey at exact
candidate `ede01ef4`, including no-recovery open, lossless row reconciliation,
deterministic pane export, stale gating, save/reopen freshness, and clean host
closeout. Cumulative PR #830 merged as `b720119e`; its merged tree exactly
matches the accepted candidate tree. ETABS file/live work and all
write-back/nightly work remain outside E1.

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| ETABS-EXCEL-BEAM-W2-BASELINE | Freeze and implement the complete read-only beam/model topology, result-provenance, and independent-frame-analysis feasibility contract before any optimization or write-back | Main Agent | one local contract packet plus separate Windows acceptance | P1 | ✅ COMPLETE — PR #898 merged exact reviewed candidate `57f53d48...` as `f1873e7b...`, tree `bb20ba0c...`. Direct/REST/all seven Excel tables and 3,626,096 canonical bytes reconcile baseline `d4c28586...` with 3,502 stations while model identity/lock/units/selection remain exact. `HELD_NOT_SUPPORTED`, no-analysis/no-model-mutation, and professional-review holds remain. |
| ETABS-W3-MASTER-PLAN-AUDIT | Freeze the dependency-ordered W3 data, audit, surrogate, optimization, ETABS-reanalysis, Excel and professional-evidence programme plus the guarded next-machine handoff | Main Agent | one planning/audit packet | P1 | ✅ ACCEPTED — PR #900 merged as `69399777b3ccdf9eb678ec567ab8a5c616959132`, tree `cc1f6528abce3c3a4532d8ad3c1a7b3dc852c71a`; owner authorized the bounded W3 campaign |
| ETABS-EXCEL-BEAM-W3A-DEMAND-CONTRACT | Freeze versioned availability, load-pattern/case/combination, analysis-status/result-selection, same-row beam-action, scenario, envelope, governing-reference, paging and canonical-hash contracts before design expansion | Main Agent | one read-only contract packet; installed getter evidence separate | P1 | ✅ ACCEPTED — PR #901 merged unchanged as `b7351bb5...`, tree `b895008b...`; 34 focused W3A/W2 tests plus local and hosted gates passed; no ETABS/Excel/COM/design/solver/optimizer activity |
| ETABS-EXCEL-BEAM-W3B-INSTALLED-GETTER-SIGNATURES | Audit the accepted W3A getter candidates against installed ETABS 23.3.1 assembly/type-library/generated-wrapper identities without creating COM or opening ETABS/Excel | bounded Windows evidence owner | one static evidence packet after accepted/merged W3A | P1 | ✅ ACCEPTED — PR #902 merged unchanged as `94c058f10...`, tree `a9337705...`; all 15 installed signatures are proved against ETABS 23.3.1.4563/comtypes 1.4.16 with no COM/SapModel call; W3C must use `GetTypeOAPI_1` and block nonblank linear-static initial cases |
| ETABS-EXCEL-BEAM-W3C-CATALOGUE-ADAPTER | Decode only W3B-proved getter shapes into one complete deterministic W3A catalogue while retaining every operation verdict/source identity | Main Agent | one transport-neutral implementation packet after accepted/merged W3B | P1 | ✅ ACCEPTED — PR #903 merged unchanged as `a44bf0c8...`, tree `fb6976c3...`; 24 focused tests plus local/hosted gates passed with no COM, ETABS, Excel, REST, analysis, selection or model mutation |
| ETABS-EXCEL-BEAM-W3D-LIVE-CATALOGUE | Extract one complete live read-only catalogue and linked same-row demand snapshot, reconciling direct/REST hashes with unchanged model, lock, units and selection | bounded Windows evidence owner | one live acceptance after merged W3C, plus evidence-backed narrow repairs for proved installed sentinels | P1 | ✅ ACCEPTED — R1/R2 merged through PRs #904/#905; final W3D PR #906 merged as `d0cc95bf...`, tree `56acf7ea...`. The complete catalogue (`d44e6b89...`) and demand snapshot (`7c1a4e21...`) reconcile direct/REST exactly with unchanged model, lock, units, statuses and selection; all local and hosted checks passed. |
| ETABS-W3-PARETO-SHEAR-REPAIR | Repair the public Pareto optimizer so nonzero shear participates in feasibility/utilization and unknown objectives fail closed | Main Agent | separate candidate after W3D | P1 | ✅ ACCEPTED — PR #907 merged unchanged as `f67c2406...`, tree `d253b003...`; focused 28 Python/FastAPI and 6 React tests, docs 8/8, quick 10/10, normal hooks and every required hosted check passed. Shear changes feasibility/Pareto membership; all scope holds remain. |
| ETABS-EXCEL-BEAM-W3E-AUDIT | Bind strict caller-owned material/detailing/applicability bases to accepted demand and evaluate every signed station through canonical beam checks | Main Agent | one L1 packet after W3D and W3R | P1 | ✅ ACCEPTED — PR #908 merged corrected candidate `07b696df...` as `06285155...`, tree `98dc2abe...`; 53 focused tests and required local/hosted gates passed. Required serviceability BLOCKED propagates; optional unavailable stays visible. No installed reinforcement/serviceability approval. |
| ETABS-EXCEL-BEAM-W3F-FOUNDATION | Freeze model/topology/displacement/reaction contracts, prove installed getter signatures, normalize and accept separately bounded read-only evidence | Main Agent / Windows evidence | L1 then L2/L3, before W3G/H | P1 | 🟢 READ-ONLY ACCEPTED WITH HOLDS — PR #913/#914 accepted 40 getters and exact state preservation. Spring/diaphragm calibration remains blocked; no live repeat is needed for W3G. |
| ETABS-W3G-BEAM-LINE | Pure bounded beam-line solver and independent numerical references | Main Agent / sole Windows writer | W3F predecessor accepted; W3H remains separate | P1 | LOCAL REFERENCES PASS; immutable review/integration pending at content freeze. 40 focused tests, 94% branch-aware coverage; no installed application access. See W3G receipt. |
| LIB-PRO-015-MERGE-HOOK | Repair the existing resolved-merge exception in both pre-commit Git guards | Main Agent | one bounded repair before audit rebind | P1 | ✅ ACCEPTED — PR #911 merged `17494b53...`, tree `9b89431b...`; 120 focused tests, all local/hosted gates and 7,350 broad Python tests pass. Ordinary and unrelated stale-ref holds remain; old audit states are preserved. |
| LIB-PRO-015-PROFESSIONAL-API-AUDIT-PLAN | Audit Python signatures, reference/example quality, OpenAPI, ETABS wrapper documentation and compatible product renewal | Main Agent | plan only; D0 first after separate acceptance | P1 | 🟡 PLAN FROZEN — [renewal plan](planning/lib-pro-015-professional-api-and-documentation-renewal-plan.md) and reproducible evidence bound to PR #911 main: 117 root functions, 41 facade projections, 97 HTTP operations. No API implementation or release authorized; normal candidate/hosted gates remain. |
| LIB-PRO-013-F0 | Converge F1-F3 family construction/facades and exact-wheel recipes on the accepted B0 foundation | @structural-math | 16–26 engineer-days | P1 | ✅ COMPLETE ON MERGE — PR #882 merged unchanged as `59ef74c0...`, tree `295c7a61...`; Windows/professional/release claims remain held |
| LIB-PRO-013-WINDOWS-REBIND | Bind the protected Windows source lane to accepted F0 before R0 uses it | bounded Windows evidence owner | evidence gate | P1 | ✅ COMPLETE — PR #883 merged at `879d32ca...`; exact F0 Git/Python source binding proved; no application evidence was run |
| LIB-PRO-012-R0 | Close external-preview documentation, generated gates, cumulative artifact/evidence, and owner-decision package | Main Agent | final programme cycle | P1 | ✅ COMPLETE — PR #884 merged as `b1ba36e3...`, tree `81854f06...`; release, Windows application evidence, and professional claims remain held |
| LIB-PRO-014-POST-R0-CUMULATIVE-AUDIT | Audit the public-tag-to-R0 programme, repair confirmed misses, and establish the next-tag posture | Main Agent | one bounded audit cycle | P1 | ✅ COMPLETE — PR #885 merged as `e7956f78...`; no engineering defect reproduced; API inventory and linked-worktree launcher root causes repaired |
| RELEASE-0240-STABLE-SOFTWARE | Publish the audited supported scope as normal `v0.24.0` while preserving Beta/in-progress claim boundaries | Main Agent | one release cycle | P1 | ✅ RELEASED — PR #886 merged as `e66de6ef...`; tag, PyPI, non-prerelease GitHub Release, public hashes, and isolated install verified |
| SPARK-001-G0 | Reassess the stale Spark work-program proposal before any implementation | repository owner | review gate | P2 | ⏸ OWNER REVIEW — the 2026-08-11 model/preview assumptions and bulk wave require refresh or rejection |

## Backlog

The version roadmap and historical backlog remain below. The canonical
[Indian-code completion plan](planning/indian-code-completion-plan.md) defines
INDIA-0 through INDIA-4, and the dedicated
[INDIA-2 execution plan](_archive/planning/india-2-remaining-is456-elements-plan.md)
defines the remaining family packets. INDIA-0 and INDIA-1 are complete. The
historical INDIA-2A-D packets form the completed `INDIA-2-STAIR` family. Bounded
wall, deep-beam, flat-slab/punching, combined-footing, and strap-footing
families are accepted, and umbrella INDIA-2 is complete within that bounded
scope after final cumulative closeout. Pile-cap G0 is complete as HOLD:
the repository lacks both a controlled IS 2911 companion source and an accepted
structural two-pile-cap benchmark, so no calculation implementation was
authorized. Raft G0 is also complete as HOLD: the repository lacks a controlled
IS 2950 source and an accepted structural raft benchmark, so no calculation
implementation was authorized. Clause 38.2 truth hygiene closed
with exact beam stress-block arithmetic and controlled Clause 38.1/Annex G
provenance. Exact post-INDIA-2 cleanup is complete for frozen candidate set
`POST-INDIA2-2499DF4ADE0DF704`: 58 worktrees, 64 local branches, and 71 remote
branches were removed; every non-candidate lane remains retained or held.
The v0.23.1a2 Alpha is published; Gravity and E1 are later `main` work and are
not part of that immutable artifact.
UIX-001 P0-P15 is accepted: the revision-safe workbench, authoritative
3D inspection, versioned capability catalogue, curated renderer, bounded
development workflow, generated beam manifest, canonical routes, and integrated
live acceptance are complete. INDIA-4 cumulative qualified review and separate
owner authorization remain required before stable-release or engineering-use
approval.

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| INDIA-3-IS13920-M0 | Cumulatively accept the repaired bounded IS 13920 source, benchmark, unsafe-case, cross-surface, capability, package, and qualified-review boundary | Main Agent | ✅ LOCAL COMPLETE — 7,024 broad Python and 498 FastAPI cases pass after one cumulative metadata/test repair; exact source-free wheel and 29-case UAT pass; quick/full/hooks/immutable candidate/hosted checks/unchanged merge/tree equality remain required; no successor packet started |
| INDIA-3-COLUMN-R1 | Repair the G0-bounded IS 13920 column applicability, actual/provided confinement, amended formulas, result meaning, and cross-surface clause contract | Main Agent | ✅ COMPLETE ON UNCHANGED GREEN MERGE — PR #868 merged at `306e2a46`, tree `cbe0f8d9`; `INDIA-3-IS13920-M0` started only afterward |
| INDIA-3-BEAM-R1 | Repair the G0-bounded IS 13920 beam amendment, geometry, finite-intake, result-meaning, and cross-surface clause contract | Main Agent | ✅ COMPLETE ON UNCHANGED GREEN MERGE — PR #867 merged at `cfe29f89`, tree `a0a095e0`; `INDIA-3-COLUMN-R1` started only afterward |
| INDIA-3-JOINT-R1 | Repair the G0-bounded IS 13920 joint SCWB factor, directional/axial basis, applicability, and supported topology contract | Main Agent | ✅ COMPLETE ON UNCHANGED GREEN MERGE — focused 29-case contract evidence passes; no API/product surface or support/release/approval promotion; `INDIA-3-BEAM-R1` not started |
| INDIA-3-SOURCE-META-R1 | Correct private IS 13920 document-kind and page-renderability metadata while preserving every source and alias | Main Agent | ✅ COMPLETE ON UNCHANGED GREEN MERGE — private archive verifies; no formula, runtime, support, release, or approval scope changed; `INDIA-3-JOINT-R1` not started |
| INDIA-3-G0 | Audit the current IS 13920 beam/column/joint surface and freeze one bounded companion-code acceptance sequence | Main Agent | ✅ COMPLETE ON MERGE — source chain resolved; all three current families are `REPAIR_PACKET_REQUIRED`; no formula or support promotion occurred |
| LIB-PRO-008 | Close confirmed torsion, WebSocket, compatibility/CI, and stirrup-geometry safety gaps before resuming INDIA-3-G0 | Main Agent | ✅ COMPLETE ON MERGE — focused behavior and compatibility evidence pass; quick/full/hooks and hosted checks remain immutable-candidate prerequisites |
| MAINT-0133 | Froze the exact read-only cleanup inventory, two-operation future batch, four unresolved holds, and zero deletion candidates | Main Agent + governance | ✅ DONE — PR #847 merged at `417a1659`; candidate and merged trees equal `0b3076d0`; quick 10/10, full 31/31, and hosted checks pass |
| MAINT-0132 | Added shared task-bound elapsed time, compact preflight-only orientation, automatic verification-step timing, and exact external integration closeout | Main Agent + governance | ✅ DONE — PR #846 merged at `60e95bbe`; candidate and merged trees equal `292c562d`; focused, quick 10/10, full 31/31, and hosted 9/9 pass |
| MAINT-0131 | Repaired preparation exit semantics, helper impact routing, safe-file executable compatibility, and mandatory closeout fields | Main Agent + governance | ✅ DONE — PR #845 merged at `d4e5b122`; candidate and merged trees equal `94bd3164`; focused 235, quick 10/10, full 31/31, and hosted 9/9 pass |
| MAINT-0130 | Replaced split move/delete/migration safety with one fail-closed transactional safe-file system and retired age-only archival | Main Agent + governance | ✅ DONE — PR #844 merged at `58ecc149`; bulk cleanup remains separately classified and authorized |
| MAINT-012D | Consolidated true duplicate scanners, archived obsolete compatibility paths, migrated live callers, and preserved distinct safety evidence | Main Agent + governance | ✅ COMPLETE ON MERGE — frozen candidate requires broad Python, quick/full, normal hooks, and all applicable hosted checks; PR facts remain external |
| MAINT-012C | Unified local/hosted impact scheduling and exact content-addressed PASS reuse under one strict seven-domain verification manifest | Main Agent + governance | ✅ DONE — PR #842 merged at `84f3cbe6`; unknown paths fail closed and ordinary hooks reuse only exact matching evidence |
| MAINT-012B | Replaced 141 generated index artifacts with a strict context manifest and bounded live summaries | Main Agent + governance | ✅ DONE — PR #841 merged at `646660e3`; generic index topology and regeneration were retired |
| MAINT-012A | Established the strict canonical operation registry, complete permissions, structured commands, CLI, and deterministic legacy projection | Main Agent + governance | ✅ DONE — PR #840 merged at `efd21917`; index architecture was explicitly deferred to MAINT-012B |
| MAINT-011 | Repaired staged/all-file hook parity, JSONC/Bandit dispositions, developer readiness, and audit/session truth | Main Agent + ops + governance | ✅ COMPLETE ON MERGE — 15 root-cause dispositions implemented; all-file byte cleanliness, focused/quick/full/local hooks, and required hosted checks are merge prerequisites |
| LIB-PRO-005 | Closed confirmed WebSocket, BOQ, lower-level scalar, PMM packaging, root-export, React-status, and evidence-truth defects without hiding the wider audit hold | backend + api + frontend + ops | ✅ DONE — PR #837 merged at `3f61bd93`; every required check passed and remaining 361 UNPROVEN parameters stay explicit |
| LIB-PRO-004 | Repaired six lower-level boundaries and replaced misleading validation/function-quality diagnostics with evidence-bearing results | reviewer + backend + governance | ✅ DONE — integrated through PR #836 at exact merge `f1a9937c`; diagnostic truthfully retained 370 UNPROVEN parameters and required a successor route-safety packet |
| LIB-PRO-003-D | Made Excel CI and readiness audits decisive and synchronized release/route-count/documentation truth | ops + governance | ✅ DONE — integrated through PR #835 at exact merge `640c7839`; readiness remains truthful PARTIAL/exit 2 and release HOLD |
| E1-EXCEL-ROUTINE-WORKBENCH | Delivered the macro-free selected-table Excel workbench, deterministic review bundle, workbook-open repair, and installed Excel acceptance | Main Agent | ✅ COMPLETE — `G3_PASS`; cumulative PR #830 merged as `b720119e` with exact candidate/merged tree `bcc7fcf1`; no ETABS or professional-approval claim |
| ETABS-EXCEL-PILOT-W1 | Accept the bounded installed Windows Excel + ETABS read-only beam pilot against one exact copied, analyzed model | Main Agent | ✅ SOFTWARE ACCEPTANCE PASS — direct and installed Excel one-/five-beam responses reconcile exactly after bounded COM/identity repairs; copied model identity and units preserved; no analysis, write-back, optimization, or professional approval |
| RELEASE-0231A2 | Published the exact v0.23.1a2 Alpha artifact | Main Agent + ops | ✅ RELEASED — tag target `09861d3d`; PyPI/GitHub wheel SHA-256 `279b8270…43a9`; later main changes require a new version |
| B2-GRAVITY-WORKFLOW-V1 | Bound the B1 ledger to canonical components, calculation book, CLI, REST, and review UI | Main Agent | ✅ COMPLETE — PR #825 merged at `c127e4b2`; focused, broad, full, hosted, and exact-head gates pass |
| B1-GRAVITY-MODEL-LOAD-LEDGER | Froze the deterministic building model, load actions, and reconciled ledger | Main Agent | ✅ COMPLETE — PR #824 merged at `cb49234f` |
| A2-LOSSLESS-INTAKE-CALCULATION | Closed lossless intake, effective-depth, load, and ETABS file-adapter root causes | Main Agent | ✅ COMPLETE — PR #823 merged at `32daa013` |
| A1-CANONICAL-TRUTH-TRANSPORT | Froze the canonical result, runtime identity, and maintained transport contract | Main Agent | ✅ COMPLETE — PR #822 merged at `a0458e19` |
| LIB-PRO-002-I | Converged the advertised `design` CLI on lossless/strict intake and expanded exact-wheel negative UAT | backend + tester + release | ✅ SOFTWARE COMPLETE — merged through PR #819; strict whole-project blocking, retained downstream compatibility, and 29-case/12-command UAT contracts pass |
| LIB-PRO-002-J | Bound hosted full suites to the selected interpreter and converged release/closeout signals | ops + tester + release | ✅ SOFTWARE COMPLETE — mode-accurate release verdicts, content-stable indexes, and read-only closeout are merged through PR #820 |
| MAINT-010-POST-INDIA2 | Refreshed generated truth, compacted session/task history without loss, archived superseded plans, completed review-only evolution, and removed cross-worktree timestamp and hidden-local-artifact index drift | Main Agent + governance | ✅ COMPLETE ON MERGE — deterministic affected-folder indexes, weekly read-only audit, immutable closeout freeze, health, audit, parity, focused governance, quick/full, hosted, and exact-tree gates recorded |
| INDIA-2-CLOSEOUT | Reconciled the complete accepted/held evidence index, final truth, and cumulative validation without adding behavior | Main Agent + reviewer | ✅ COMPLETE ON MERGE — six bounded families accepted; pile-cap and raft remain `HELD / NOT_IMPLEMENTED`; broad Python and full 30/30 gate pass |
| INDIA-2-FOUNDATION-RAFT-G0 | Audited one regular rectangular rigid-raft candidate, the conventional-method boundary, controlled-source inventory, and structural benchmark readiness | Main Agent + structural engineer | ⏸ HOLD — PR #805 merged as `d2885215`; no controlled IS 2950 source or accepted replayable structural benchmark; no calculation files created |
| INDIA-2-FOUNDATION-PILE-CAP-G0 | Audited the frozen centred axial two-pile candidate, source inventory, structural-model boundary, and benchmark readiness | Main Agent + structural engineer | ⏸ HOLD — PR #804 merged as `def0b493`; no controlled IS 2911 companion source or accepted replayable structural benchmark; no calculation files created |
| INDIA-2-TRUTH-HYGIENE-38-2 | Rebound live beam-flexure provenance to controlled Clause 38.1/Annex G identities and replaced the false-safe rounded inverse with shared exact equilibrium | Main Agent + structural engineer | ✅ COMPLETE — PR #803 merged as `1139e9ea`; 190 focused tests pass and the supported discriminator changes false PASS to `E_FLEXURE_003` |
| DOC-FRONTMATTER-CONTRACT | Made JSON frontmatter validation fail on invalid records, added direct valid/invalid report regressions, and repaired exactly eight invalid lifecycle/type records | Main Agent + doc-master | ✅ COMPLETE ON MERGE — live JSON/text modes pass with zero invalid and 60 permitted legacy records unchanged |
| GIT-001-P8-RECONCILIATION | Verified GIT-7E adoption, corrected transition-versus-closeout receipt semantics, reconciled current ledgers, and refreshed preservation holds | Main Agent + ops | ✅ COMPLETE ON MERGE — primary/e54a retained; Excel and all other pre-existing lanes remain `UNKNOWN/HOLD`; no cleanup performed |
| GIT-001 | Researched and implemented the evidence-backed Git operating model through adoption closeout | Main Agent + repository owner | ✅ COMPLETE ON MERGE — Phases 0-8 close with fail-closed maintenance/reactivation rules and preserved unknown lanes |
| INDIA-2-FOUNDATION-STRAP | Implemented, published, and focused-accepted one bounded property-line two-footing equal-pressure no-soil-contact strap workflow | Main Agent + structural engineer | ✅ DONE — G0/A-D integrated; frozen and non-frozen benchmarks, exact-head audit, focused gates, and hosted checks pass; qualified review and excluded systems remain held |
| INDIA-2-FOUNDATION-STRAP-D | Published the strict nested FastAPI transport, exact OpenAPI contract, capability/semantic truth, and deterministic manifest promotion | Main Agent + API developer | ✅ COMPLETE — one bounded workflow is supported at 13/21 truth and all 81 routes have direct tests; family acceptance is separately complete |
| INDIA-2-FOUNDATION-STRAP-C | Published the typed property-line strap Python composition, immutable provenance/result/status types, mapping builder, canonical exports, executable benchmark, and public docs | Main Agent + backend | ✅ COMPLETE — public Python PASS/FAIL/fail-closed/provenance tests pass; capability remains held until D |
| INDIA-2-FOUNDATION-STRAP-B | Implemented exact stress-block flexure, minimum/provided and side-face steel, Table 19/20 shear and vertical stirrups, spacing, cover, anchorage, and composed disposition | Main Agent + structural math | ✅ COMPLETE — frozen PASS, valid FAIL, exact-helper regression, and fail-closed boundaries pass; public composition/publication remain held |
| INDIA-2-FOUNDATION-STRAP-A | Implemented typed strap geometry/action/approval contracts, equal-pressure/common-factor eligibility, reactions, bearing, clear-strap actions, and equilibrium | Main Agent + structural math | ✅ COMPLETE — frozen benchmark, source-equation reduction, valid bearing failure, and fail-closed boundaries pass; strength/publication remain held |
| INDIA-2-FOUNDATION-STRAP-G0 | Froze one property-line two-footing system with equal uniform pressure, an explicit no-soil-contact strap model, independent benchmark, and externally verified footing-slab prerequisites | Main Agent + structural engineer | ✅ GO — activated the now-complete A-D and focused-acceptance chain; capability stayed held until D |
| INDIA-2-FOUNDATION-COMBINED | Implemented, published, and focused-accepted one bounded symmetric equal-load two-column rigid rectangular combined-footing workflow | Main Agent + structural engineer | ✅ DONE — G0/A-D integrated; 84 family tests, 339 focused public-contract tests, frozen and non-frozen benchmarks, exact-head audit, and hosted checks pass; qualified review and excluded systems remain held |
| INDIA-2-FOUNDATION-COMBINED-D | Published strict nested FastAPI transport, exact OpenAPI drift, capability/semantic truth, and deterministic manifest promotion | Main Agent + API developer | ✅ COMPLETE — one bounded workflow is supported at 12/21 truth and all 80 routes have direct tests; integration receipt remains live-closeout evidence |
| INDIA-2-FOUNDATION-COMBINED-C | Published one typed Python composition with immutable provenance/result/status types, canonical exports, executable benchmark, public API docs, and retained held truth | Main Agent + backend | ✅ COMPLETE — 7 direct C and 78 combined A/B/C tests pass; capability remains held until D |
| INDIA-2-FOUNDATION-COMBINED-B | Implemented flexure/minimum/provided steel, spacing/cover/anchorage, concrete one-way/punching shear, bearing/dowels, and composed disposition | Main Agent + structural math | ✅ COMPLETE — 28 direct tests and immutable independent source-candidate audit pass; capability remains held until C/D |
| INDIA-2-FOUNDATION-COMBINED-A | Implemented typed eligibility, gross/net pressure, resultant equilibrium, longitudinal critical sections, and transverse actions | Main Agent + structural math | ✅ COMPLETE — frozen benchmark and additional symmetric equilibrium cases pass; strength and public capability remain held |
| INDIA-2-FOUNDATION-COMBINED-G0 | Froze one symmetric equal-load two-column rigid rectangular footing under caller-approved uniform pressure with a pre-implementation benchmark | Main Agent + structural engineer | ✅ GO — COMBINED-A-D activated; general/asymmetric soil interaction and public capability remain held |

## Archive

Completed historical tasks live in [tasks-history.md](_archive/tasks-history.md)
(`docs/_archive/tasks-history.md`).

## Completed (Archived)

> All completed items below have been archived. See [tasks-history.md](_archive/tasks-history.md) for full details.

| Section | Items | Summary |
|---------|-------|---------|
| Architecture Doc Enhancement | 1 ✅ | unified-architecture-v1.md enhanced 413→1108 lines, 8 new sections, 9-agent review (library-expert, security, structural-engineer, reviewer, frontend, api-developer, innovator, tester, governance) |
| v0.21.2 Packaging Fixes | TASK-PKG-1–6 ✅ | Wheel content, package discovery, CI tests |
| v0.21.2 External Audit | EA-1–23 ✅ | 23 audit findings fixed (test infra, imports, API, security, frontend, docs) |
| v0.21.5 Stabilization | 8 items ✅ | CostProfile, sanitize_float, footing wiring, bearing pressure |
| Recent Fixes | 21 items ✅ | Response envelope, CI, audit P0–P2, column math, git hardening, variable naming |
| Audit P1 Batch 1 | 4 items ✅ | clause_cli, FlexureResult limits, streaming 404, Three.js cleanup |
| External Audit Remediation | 8 items ✅ | ETABS units/batch/geometry, SmartDesigner CLI, .j2 packaging, README fixes, bbs import path |

---

## External Audit Remediation — v0.21.6 ✅ DONE

**Theme:** Fix 8 external audit findings across ETABS import, SmartDesigner CLI, packaging, and documentation.
**Completed:** 2026-04-07

| ID | Finding | Priority | Status |
|----|---------|----------|--------|
| EXT-P1-1 | ETABS job generator uses `"SI-mm"` units → fixed to `"IS456"` | P1 | ✅ DONE |
| EXT-P1-2 | ETABS batch groups by `beam_id` only → fixed to `(story, beam_id)` to prevent cross-story collision | P1 | ✅ DONE |
| EXT-P1-3 | Geometry merge keys by `label` only → fixed to `(story, label)` with fallback to prevent overwrite | P1 | ✅ DONE |
| EXT-P1-4 | SmartDesigner CLI uses wrong function → fixed to `design_single_beam()` returning `BeamDesignOutput` | P1 | ✅ DONE |
| EXT-P1-5 | Report `.j2` templates missing from wheel → added to `pyproject.toml` package-data | P1 | ✅ DONE |
| EXT-P2-1 | README batch example uses non-existent `parse_file()` → fixed to `load_combined()` | P2 | ✅ DONE |
| EXT-P2-2 | `bbs.py` imports from deprecated shim → fixed to canonical `codes/is456/beam/detailing` | P2 | ✅ DONE |
| EXT-P3-1 | README version `0.21.3` → updated to `0.21.5` | P3 | ✅ DONE |
| EA-6 | Internal `ductile` import triggering deprecation warnings — fixed in `is456/__init__.py` | P2 | ✅ DONE |
| AUDIT-RPT | Wire reports `_generate_fallback_html` instead of raising `ImportError` | P2 | ✅ DONE |
| AUDIT-PIN | Update README git pin from `v0.21.3` to `v0.21.5` | P3 | ✅ DONE |
| AUDIT-SMOKE | Add 9 wheel smoke tests (`TestWheelSmokeTests`, `TestREADMESnippets`) | P2 | ✅ DONE |

---

## v0.21.5 — Test Coverage & Regression Prevention ✅ DONE

**Theme:** Golden vector baselines and contract tests. No future change can silently break existing calculations.
**Completed:** 2026-04-06
**Quality Gate:** `pytest -m golden` passes with 0 failures, branch coverage 99% on `codes/is456/` ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-720 | Golden vector baselines for all IS 456 functions (`@pytest.mark.golden`) — 42+ tests (9 beam + 20 column + 13 footing) | @tester | ✅ DONE |
| TASK-721 | Contract tests for API surface stability (`@pytest.mark.contract`) — 18 contract tests | @tester | ✅ DONE |
| TASK-520 | Report & 3D visualization test coverage — 71 new tests | @tester | ✅ DONE |
| TASK-722 | conftest.py golden_vectors fixture with SP:16 values | @tester | ✅ DONE |
| TASK-723 | CI gate: `pytest -m golden` in GitHub Actions python-tests.yml | @ops | ✅ DONE |
| — | 90%+ branch coverage on `codes/is456/` — 99% achieved | @tester | ✅ DONE |
| — | Add `@clause("34.1")` to `size_footing()` | @structural-math | ✅ DONE |

## v0.21.6 — API Quality & Introspection ✅ DONE

**Theme:** Self-describing, self-validating library
**Completed:** 2026-04-06
**Quality Gate:** check_code("IS456") returns report, OpenAPI drift check in CI ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-724 | Implement `check_code("IS456")` — validates code implementation contract | @backend | ✅ DONE |
| TASK-725 | Implement `show_versions()` — library + dependency info | @backend | ✅ DONE |
| TASK-726 | API surface freeze: OpenAPI baseline diff in CI | @ops | ✅ DONE |
| TASK-727 | Function limitation docs — what each function does NOT do | @doc-master | ✅ DONE |

## v0.21.6 Pre-Release Audit (2026-04-07)

**Theme:** Comprehensive 14-agent audit before PyPI release
**Overall Score:** A+ (9.0/10)
**Audit Report:** [comprehensive-library-audit-2026-04-04.md](audit/comprehensive-library-audit-2026-04-04.md)

### Release Blockers — NONE ✅

No critical or high-severity findings blocking this release.

### Version Fixes Required Before Tag

| Item | File | Fix | Status |
|------|------|-----|--------|
| CHANGELOG heading | CHANGELOG.md | `[Unreleased]` → `[0.21.6] — 2026-04-07` | 📋 |
| CHANGELOG link | CHANGELOG.md bottom | Add `[0.21.6]` compare link | 📋 |
| API docs version | docs/reference/api.md | `0.21.5` → `0.21.6` | 📋 |
| Python README git pin | Python/README.md | `@v0.21.5` → `@v0.21.6` | 📋 |
| Git-automation version | docs/git-automation/README.md | `0.21.5` → `0.21.6` | 📋 |

### Known Issues — Accepted Deferrals

These findings are documented in the comprehensive audit and planned for future releases. They are NOT release-blocking because they represent planned improvements, not regressions.

| ID | Finding | Severity | Deferred To | Reason for Deferral |
|----|---------|----------|-------------|---------------------|
| FE-NEW-01 | Three.js memory leak — no dispose() on unmount | CRITICAL | v0.22.0 | Requires R3F architecture change; no crash in normal usage, affects only rapid route switching |
| UX-01 | d_mm > D_mm accepted silently (impossible geometry) | ~~CRITICAL~~ | ✅ FIXED | _validate_plausibility in common_api.py now raises ValueError |
| UX-02 | Column returns dict, beam returns dataclass | CRITICAL | v0.22.0 | Breaking API change — requires major version or deprecation cycle |
| ARCH-NEW-12 | services/api.py god module (3610 lines) | HIGH | v0.22.0 | Structural refactor, no functional impact |
| S-NEW-01 | ImportError messages leak internal paths (22 instances) | HIGH | v0.21.7 | Security hardening release |
| H-01 | WebSocket connections lack rate limiting | HIGH | v0.21.7 | Security hardening release |
| M-04 | create_dev_token() importable in production | MEDIUM | v0.21.7 | No auth enabled by default, defense-in-depth improvement |
| M-05 | No per-endpoint scope checking | MEDIUM | v0.21.7 | Auth disabled by default, planned for security release |
| T-NEW-01 | MagicMock in 2 test files (TE-3 violation) | HIGH | v0.22.0 | Test quality, not production code |
| IS-NEW-01 | 4 footing functions lack @clause decorators | HIGH | v0.22.0 | Traceability enhancement, not math error |
| IS-NEW-02 | 17 serviceability functions lack @clause | HIGH | v0.22.0 | Traceability enhancement, not math error |

### Audit Highlights

- **Test Infrastructure:** 5003/5003 tests passing, 99% branch coverage on IS 456 code, 42+ golden vectors, 18 contract tests
- **Security:** 0 CVEs, Docker hardened (non-root, cap_drop ALL), JWT production safeguard, rate limiting on REST endpoints
- **Agent Infrastructure:** 16/16 agents, 14/14 skills, 16/16 prompts, all cross-references valid
- **Architecture:** 4-layer boundary intact, 108 API exports, consistent parameter naming with unit suffixes
- **IS 456 Compliance:** All formulas verified correct, 42 clauses + 8 IS 13920 covered, A+ compliance score
- **Packaging:** pyproject.toml v0.21.6, .j2 templates in wheel, all 19 modules have __init__.py
- **CI/CD:** 18 workflows, CodeQL + pip-audit + OpenSSF Scorecard, golden gate in CI

### Infrastructure Issues (non-blocking)

| Issue | Location | Impact | Fix Plan |
|-------|----------|--------|----------|
| skill_count=10 in registry metadata | agents/agent_registry.json | Cosmetic — actual count is 14 | Update _meta.skill_count |
| session_summary.py referenced but doesn't exist | CLAUDE.md, terminal-rules | Use `session.py summary` instead | Update 4 doc references |
| 3 architecture import violations in FastAPI | main.py, design.py, geometry.py | Non-functional, code works | Refactor in v0.22.0 |

## v0.21.6 Post-Audit: Online Research & Root Cause Analysis

**Source:** Online best practices (OWASP 2025, PyPI Trusted Publishers, PEP 740 attestations, IStructE software validation guidance) + External Audit EA-1 through EA-23 root cause patterns.

### NEW Issues Found (from online research)

These were NOT caught by the 14-agent audit. They come from comparing our setup against 2025 industry best practices.

| ID | Category | Issue | Severity | Target | How Found |
|----|----------|-------|----------|--------|-----------|
| OL-01 | Supply Chain | No `check-wheel-contents` validation in CI — malformed metadata can ship to PyPI | HIGH | v0.21.7 | PyPI packaging best practices |
| OL-02 | Supply Chain | No `twine check` in CI — README rendering errors discovered only post-publish | MEDIUM | v0.21.7 | PyPI publishing guide |
| OL-03 | Supply Chain | No SLSA provenance attestation — OWASP 2025 A03 (Supply Chain Failures) | HIGH | v0.22.0 | OWASP Top 10:2025 A03 |
| OL-04 | Supply Chain | No artifact signing (sigstore) — PEP 740 digital attestations now standard | MEDIUM | v0.22.0 | PyPI attestations blog (Nov 2024) |
| OL-05 | Docker | Base image `python:3.11-slim` not pinned to digest — reproducibility risk | MEDIUM | v0.21.7 | Container security best practices |
| OL-06 | Docker | No multi-stage build — dev tools included in production image (~1GB) | LOW | v0.22.0 | Docker security hardening guide |
| OL-07 | Docker | No retained container-image CVE scan in the compact workflow set | LOW | v0.21.7 | OWASP A03 + A06. Reintroduce only if outcome-changing, using a pinned action |
| OL-08 | Security | OWASP 2025 A10 "Mishandling of Exceptional Conditions" — 2-4 HTTP-exposed ImportError leaks (38 total catch sites, all properly sanitized via sanitize_error()) | LOW | v0.21.7 | OWASP Top 10:2025 (NEW category) |
| OL-09 | Security | No security logging / alerting — OWASP 2025 A09 has no implementation | MEDIUM | v0.22.0 | OWASP Top 10:2025 A09 |
| OL-10 | Packaging | No TestPyPI dry-run before production release | LOW | v0.21.7 | PyPI publishing workflow guide. TestPyPI job exists but only on workflow_dispatch, not mandatory gate |
| OL-11 | Packaging | No sdist contents verification (only wheel checked) | LOW | v0.22.0 | Python packaging best practices |
| OL-12 | Packaging | Optional dependency groups untested (`.[dxf]`, `.[report]`) | LOW | v0.21.7 | pip install variations |
| OL-13 | Licensing | No license compliance scan — BSD dependency chain could break GPL | LOW | v0.22.0 | FOSSA / pip-licenses |
| OL-14 | Struct Eng | No consolidated verification methodology doc — V&V infrastructure exists (42+ golden vectors, verification-checklist.md, validation-pack.md) but fragmented across 6+ files | MEDIUM | v0.22.0 | IStructE software validation guidance |
| OL-15 | Struct Eng | MERGED into TASK-735 — services/audit.py already provides basic audit trail; CalculationProvenance extends it | LOW | v0.22.0 | Building standards guidance on computer programs |
| OL-16 | API | No OpenAPI drift check in publish workflow — API clients break silently | MEDIUM | v0.21.7 | API versioning best practices |

### Additional Findings from 4-Agent Review (2026-04-07)

| ID | Finding | Severity | Source | Target |
|----|---------|----------|--------|--------|
| AR-01 | Trivy action@master unpinned (supply chain risk) | LOW | @security | v0.21.7 |
| AR-02 | Auth default-off even when JWT_SECRET_KEY is set in production | MEDIUM | @security | v0.21.7 |
| AR-03 | requirements.txt uses floor versions; Dockerfile installs unpinned deps | LOW | @security | v0.21.7 |
| AR-04 | Documentation drift — code fixes ahead of task board (e.g., UX-01 already fixed) | MEDIUM | @library-expert | Ongoing |
| AR-05 | No deprecation policy for 46 backward-compat stubs | LOW | @library-expert | v1.0 |
| AR-06 | Import time ~3-5s — ezdxf/pydantic eager loading in __init__.py | MEDIUM | @library-expert | v0.22.0 |
| AR-07 | Negative Mu silently abs-valued — no hogging/sagging guidance | MEDIUM | @library-expert | v0.21.7 |
| AR-08 | Column API not exported from structural_lib.__init__.py | HIGH | @library-expert | v0.21.7 |
| AR-09 | show_versions() reports stale version (0.21.1) from source install | LOW | @library-expert | v0.21.7 |

### Missing Root Cause Patterns (from @library-expert)

| # | Pattern | Severity | Description |
|---|---------|----------|-------------|
| 7 | Documentation Drift | MEDIUM | Code moves faster than docs; version strings, task statuses, verification checklist version all lag behind code |
| 8 | API Stability / No Deprecation Policy | LOW (HIGH at v1.0) | 46 backward-compat stubs with no formal removal timeline |
| 9 | Import Performance | MEDIUM | Cold start ~3-5s due to eager imports of ezdxf, pydantic, all stubs |

### External Audit Root Cause Analysis (EA-1 through EA-23)

We analyzed WHY each external audit finding was missed. Six patterns emerge:

| Pattern | Findings | Root Cause | Prevention Measure | Status |
|---------|----------|-----------|-------------------|--------|
| **Repo ≠ Installed** | EA-1, EA-6, EA-8, EA-9 | Tests only run in dev environment, never tested installed wheel | `@repo_only` marker, wheel smoke tests in CI | ✅ Fixed |
| **Dev-centric defaults** | EA-2, EA-10, EA-11, EA-16 | Config optimized for developer experience, not production safety | `.env.example`, auth-on-by-default in prod, lazy imports | ✅ Fixed |
| **Undocumented API ergonomics** | EA-3, EA-5, EA-12, EA-13 | API grew incrementally without UX design review | API levels doc, build_detailing_input() factory, e2e examples | ✅ Fixed |
| **Mixed API patterns** | EA-4, EA-14 | Features added fast without consistency enforcement | to_dict() added, task-oriented README | ✅ Fixed |
| **Security in exception messages** | EA-17, EA-18, EA-20 | Error messages treated as debug output, CORS hardcoded | sanitize_error() utility, Settings-based CORS, RateLimitMiddleware | ✅ Fixed |
| **Incomplete IS 456 coverage** | EA-21, EA-22, EA-23 | Code added without a namespaced capability/traceability contract | INDIA-0 generated manifest separates supported scope, held scope, decorator registration, and qualified review | ✅ Reclassified; remaining work is explicit |

### Are We Protected Against Recurrence?

| Prevention | Implemented? | Gap? |
|------------|-------------|------|
| Wheel smoke test in CI | ✅ Yes — weekly/manual clean-wheel verification | No gap |
| Clean import test | ✅ Yes — TestImportSilence, TestImportStrictWarnings | No gap |
| API stability test (105 functions) | ✅ Yes — TestAPIStability | No gap |
| E2E pipeline test | ✅ Yes — test_full_pipeline_e2e.py (8 tests) | No gap |
| RateLimitMiddleware on all endpoints | ✅ Yes — global middleware | No gap |
| sanitize_error() for all routers | ⚠️ Partial — 2-4 HTTP-exposed ImportError leaks (38 total catch sites properly sanitized) | OL-08 above |
| Indian-code traceability | ⚠️ Explicit — INDIA-0 reports namespaced `REGISTERED`, `METADATA_ONLY`, and `REGISTRATION_ONLY` records separately from capability support; registration is not implementation evidence | Generated `indian-code-capability-coverage.json`; follow-on traceability packets only when they change supported workflow evidence |
| Cross-field input validation | ✅ Yes — _validate_plausibility in common_api.py raises ValueError for d>D | ✅ Fixed (was UX-01) |
| TestPyPI before prod publish | ❌ No — publish goes direct to PyPI | OL-10 above |
| OWASP 2025 A03 (Supply Chain) | ⚠️ Partial — Trusted Publishers ✅, but no attestations/provenance | OL-03, OL-04 |
| OWASP 2025 A09 (Logging) | ❌ No — no security event logging | OL-09 |
| OWASP 2025 A10 (Exceptions) | ⚠️ Partial — sanitize_error exists but not applied everywhere | OL-08 |
| Structural eng verification methodology | ⚠️ Partial — V&V infrastructure exists (42+ golden vectors, verification-checklist.md, validation-pack.md) but fragmented across 6+ files | OL-14 |
| Container security scanning | ❌ Not retained in the compact workflow set | OL-07 above |

## v0.21.7 — Security Hardening (In Progress)

**Theme:** Input validation, error sanitization, packaging gates, CI hardening
**Target:** 2-3 sessions after v0.21.6
**Quality Gate:** `audit_input_validation.py` reports 0 unresolved findings. `pip-audit` clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-728 | JSON body size limit middleware (1MB default) | @api-developer | 📋 |
| TASK-729 | Cross-field plausibility guards (14 model validators) | @api-developer | ✅ DONE |
| TASK-730 | Input validation audit (16 gaps found + fixed, 49 tests) | @security | ✅ DONE |
| TASK-731 | Dependency CVE scanning in CI (`pip-audit`) | @ops | 📋 |
| — | WebSocket message rate limit (5 msg/s per session) | @api-developer | 📋 |
| — | Computation timeout (prevent pathological inputs) | @api-developer | 📋 |
| TASK-790 | `check-wheel-contents` + `twine check` in publish workflow (OL-01, OL-02) | @ops | 📋 |
| TASK-791 | TestPyPI dry-run step before production PyPI publish (OL-10) | @ops | 📋 |
| TASK-792 | Decide whether container-image scanning is outcome-changing; if retained, add a pinned scanner to weekly verification (OL-07) | @ops | 📋 |
| TASK-793 | Optional dependency group tests: `.[dxf]`, `.[report]` (OL-12) | @tester | 📋 |
| TASK-794 | Docker base image digest pinning (OL-05) | @ops | 📋 |
| TASK-795 | OpenAPI drift check in publish workflow (OL-16) | @ops | 📋 |
| TASK-796 | Fix ImportError path leaks (sanitize_error_string + 4 router fixes, 15 tests) | @api-developer | ✅ DONE |
| TASK-802 | Export column API to __init__.py (already exported — 6 contract test assertions fixed) | @backend | ✅ DONE |
| TASK-803 | Document negative Mu abs-value behavior + add hogging guidance (AR-07) | @doc-master + @structural-math | 📋 |
| TASK-804 | Auto-enable auth or log CRITICAL when JWT_SECRET_KEY set but AUTH_ENABLED=false (AR-02) | @api-developer | 📋 |
| TASK-CI-FIX | Fix 5 daily CI failures on main (Windows timing, SBOM CLI, Scorecard perms, OpenAPI drift, Nightly QA) | @ops/@backend | ✅ DONE (PR #550) |

**Recommended action order (4-agent consensus):**
1. TASK-729 + TASK-730 (Input Safety — cross-field + validation audit)
2. TASK-802 (Column API export — HIGH user impact)
3. TASK-796 (ImportError leaks — 2-4 actual HTTP-exposed)
4. TASK-790 + TASK-791 + TASK-793 (Packaging gates)
5. TASK-795 (OpenAPI drift in publish)
6. TASK-794 (Docker digest pin)
7. TASK-728 (JSON body size limit)

## v0.21.8 — Performance & Property Testing

**Theme:** Performance baselines and property-based invariants
**Target:** 2-3 sessions after v0.21.7
**Quality Gate:** All benchmarks baselined. Hypothesis tests pass 10,000 examples.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-732 | pytest-benchmark integration for hot-path functions | @tester | 📋 |
| TASK-733 | Property-based testing with Hypothesis (flexure/shear/column) | @tester | 📋 |
| TASK-734 | Performance regression baselines in CI (>20% slowdown blocks merge) | @ops | 📋 |
| — | Benchmark results stored in `Python/test_stats.json` | @tester | 📋 |

## Batch 3: API Naming Convention (v0.22.0)

**Theme:** Standardize parameter naming across L3 (services) API — `fck`→`fck_nmm2`, `fy`→`fy_nmm2`
**Ref:** Issue 15, architecture doc §10.5

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-740 | Standardize column_api.py param names (fck→fck_nmm2, fy→fy_nmm2) — 10 functions | @backend | ✅ |
| TASK-741 | Standardize beam_api.py outliers (check_beam_ductility, check_anchorage) — 2 functions | @backend | ✅ |
| TASK-742 | Update FastAPI column router + Pydantic models for new param names | @api-developer | ✅ |
| TASK-743 | Add deprecation warning tests for old param names | @tester | ✅ |
| TASK-744 | Document two-tier naming convention in architecture doc | @doc-master | ✅ |
| TASK-745 | Decide stable vs experimental API tiers (Issue 16 — defer to v0.23+) | @library-expert | 📋 |
| TASK-746 | Consolidate `_resolve_deprecated_param` from beam_api.py + column_api.py into common_api.py | @backend | 📋 [P4] |
| TASK-747 | Add direct unit tests for `_resolve_deprecated_param` TypeVar helper | @tester | 📋 [P4] |

---

## v0.22.0 — Stabilization Release

**Theme:** Production-quality release with full provenance and CI gates
**Target:** After all v0.21.x complete
**Quality Gate:** All v0.21.x quality gates pass simultaneously. SP:16 verification ±0.1%. Release preflight clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-735 | CalculationProvenance foundation (`core/provenance.py`) — see arch doc §11 | @backend | 📋 |
| TASK-736 | SP:16 full verification | @structural-engineer | 📋 |
| TASK-797 | SLSA provenance + PEP 740 digital attestations (OL-03, OL-04) | @ops | 📋 |
| TASK-798 | Security event logging framework — OWASP 2025 A09 (OL-09) | @security (define) + @api-developer (implement) | 📋 |
| TASK-799 | Multi-stage Dockerfile (builder→runtime, reduce image to ~400MB) (OL-06) | @ops | 📋 |
| TASK-800 | Independent verification methodology doc — IStructE guidance (OL-14) | @structural-engineer | 📋 |
| — | ~~TASK-761~~ Calculation audit trail — MERGED into TASK-735 (CalculationProvenance); services/audit.py already provides basic audit trail | — | ✅ Merged |
| TASK-801 | License compliance scan with pip-licenses (OL-13) | @security | 📋 |
| TASK-521 | Beam rationalization | @backend | 📋 [CARRIED OVER] |
| TASK-643 | SP:16 chart verification completion | @structural-engineer | 📋 [CARRIED OVER] |
| — | Deprecate old architecture docs | @doc-master | 📋 |
| — | Full CI/CD pipeline with all quality gates active | @ops | 📋 |
| — | Release checklist automation | @ops | 📋 |

## Library Expansion — Multi-Code, Multi-Element

> **v5.0:** Multi-code (IS 456 + ACI 318 + EC2), multi-element expansion. Every function goes through a 9-step quality pipeline.
> See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full plan.
> Use `/function-quality-pipeline` skill for every new function.

### Completed Phases (Summary)

| Phase | Scope | Tasks | Status |
|-------|-------|-------|--------|
| Phase 0 | Quality Infrastructure | TASK-600–610 (11/11) | ✅ Done |
| Phase 1 | Foundation Cleanup | TASK-611–625 (15/15) | ✅ Done |
| Phase 1.5 | IS 456 Beam Restructure | TASK-700–712 (13/13) | ✅ Done |
| Phase 2 | Column Design | TASK-630–646 (14/14) | ✅ Done |
| Phase 3 | Bounded isolated-footing core | TASK-650–656 (bounded scope) | ✅ Done |
| Variable Naming | IS 456 convention migration | TASK-660 (1/1) | ✅ Done |
| Agent Evolver | Self-evolving agent system | TASK-800.P3–P11 | ✅ Done (P12 burn-in) |
| Agent Infrastructure | claw-code adaptation | TASK-850–872 (23/23) | ✅ Done |
| Git Hardening | Git workflow automation | TASK-900–913 (13/14) | ✅ 13/14 |

> Full details for all completed phases: [tasks-history.md](_archive/tasks-history.md)

### Phase 3: Bounded Footing Design (Reconciled)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Bounded bearing/dowel load transfer | `check_isolated_footing_load_transfer` | Cl 34.4 / load transfer | ✅ DONE |
| TASK-656 | Bounded footing FastAPI consumer | `POST /api/v1/design/footing/load-transfer` | — | ✅ DONE |

> The bounded isolated-footing milestone is complete. Combined, strap, raft,
> pile-cap, settlement, and lateral-stability design remain explicitly outside
> this milestone.

---

## v0.23 — IS 456 Slabs & Footing Completion

**Ref:** Architecture doc §20.6

### Bounded Footing Status

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Bearing/dowel load transfer | `check_isolated_footing_load_transfer` | Cl 34.4 / load transfer | ✅ DONE |
| TASK-656 | Footing FastAPI consumer | `POST /api/v1/design/footing/load-transfer` | — | ✅ DONE |
| — | Combined footing design | — | — | ⏸ OUT OF SCOPE |
| — | Literal footing clause coverage target | — | — | ⏸ NOT A MILESTONE GATE |

### One-Way Slab Design (IS 456 Cl 24.1–24.2)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-737 | Bounded one-way slab design umbrella | — | Cl 24.1–24.2 | ✅ DONE |
| TASK-750 | Slab types + errors | `SolidRectangularSlabGeometry`, result records | — | ✅ DONE |
| TASK-751 | Slab classification | `classify_solid_rectangular_slab()` | ly/lx ratio | ✅ DONE |
| TASK-752 | Bounded continuous one-way coefficient lookup | `design_continuous_one_way_slab_builtin_is456()` | Table 12/13 | ✅ DONE FOR DECLARED DOMAIN |
| TASK-753 | Simply supported one-way design | `design_one_way_slab_is456()` | Cl 24.1–24.2 | ✅ DONE |
| TASK-754 | Bounded slab detailing/serviceability | `check_one_way_slab_detailing()` | Cl 26.5 | ✅ DONE |

### Two-Way Slab Design (IS 456 Cl 24.3, Annex D)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-738 | Bounded external-coefficient two-way flexure | — | Cl 24.3, Annex D | ✅ DONE |
| TASK-760 | Built-in normalized moment-coefficient lookup/interpolation | `design_two_way_slab_panel_builtin_is456()` | Table 26 | ✅ DONE FOR DECLARED DOMAIN |
| TASK-761 | Built-in simply-supported/free-corner coefficient route | `design_two_way_slab_panel_builtin_is456()` | Table 27 | ✅ DONE FOR DECLARED DOMAIN |
| TASK-762 | Interior-panel bounded flexure | `design_two_way_slab_is456()` | Annex D-1 | ✅ DONE |
| TASK-763 | Bounded corner-torsion reinforcement disposition | complete two-way panel workflows | Annex D | ✅ DONE FOR DECLARED DOMAIN |
| TASK-764 | Middle/edge strip distribution | complete two-way panel workflows | Annex D | ✅ DONE FOR DECLARED DOMAIN |
| — | Flat slab with drop panels | — | IS 456 Cl 31 | ⏸ OUT OF SCOPE |

### Punching Shear (Shared — Slab + Footing)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-770 | Generic shared punching-shear framework | — | Cl 31.6 | ⏸ OUT OF SCOPE; footing-specific check exists |

### Slab FastAPI + React

| ID | Task | Status |
|----|------|--------|
| TASK-780 | Bounded slab Python facade wiring | ✅ DONE |
| TASK-781 | One-way slab FastAPI consumer | ✅ DONE FOR BOUNDED SCOPE |
| TASK-782 | Revision-safe slab React workbench and review surface | ✅ DONE FOR DECLARED DOMAIN |

### Additional v0.23 Deliverables (from architecture doc §20.6)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | Truthful batch streaming/progress behavior (§13.2) | @backend | ✅ DONE |
| — | Expanded future error hierarchy (§13.3) | @backend | ⏸ OUT OF SCOPE |
| — | Property-based testing expansion to all modules (§14.1) | @tester | ⏸ OUT OF SCOPE |
| — | Additional performance expansion (§14.2) | @tester | ⏸ OUT OF SCOPE |

---

## v0.24 — Multi-Code Infrastructure

**Ref:** Architecture doc §20.7 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 2

> Future roadmap only. None of these tasks may start during C0-C4 of the
> bounded IS 456 milestone without a separate owner scope change.

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-739 | CodeRegistry thread-safe locking | Make CodeRegistry safe for concurrent use | @backend | 📋 |
| TASK-740 | DesignEnvelope wrapper | Multi-code result wrapper (§5.3) | @backend | 📋 |
| TASK-741 | core/units.py | Unit conversion at boundary (in→mm, psi→MPa) | @backend | 📋 |
| TASK-800-INFRA-1 | Activate CodeRegistry | `services/api.py` uses `CodeRegistry.get()` for dispatch | @backend | 📋 |
| TASK-800-INFRA-2 | IS456Code implements ABCs | FlexureDesigner, ShearDesigner, ColumnDesigner | @backend | 📋 |
| TASK-800-INFRA-3 | Code-specific input dataclasses | IS456BeamInput, ACI318BeamInput, EC2BeamInput | @backend | 📋 |
| — | Code Amendment Tracking metadata (§11.2) | @structural-math | 📋 |
| — | National annex support infrastructure | @backend | 📋 |
| — | Entry-point plugin discovery for third-party codes (§16.7) | @backend | 📋 |
| — | Auto-generated client SDKs (Python + TypeScript, §13.1) | @api-developer | 📋 |
| — | API v2 routes: `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-6 | Namespace clauses.json v2 | Add code field to clause entries | @backend | 📋 |
| TASK-800-INFRA-7 | Code discovery API | `list_codes()`, `get_capabilities()` | @backend | 📋 |
| TASK-800-INFRA-8 | FastAPI v2 routes | `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-9 | Feature flags for experimental codes | EXPERIMENTAL_CODES config | @ops | 📋 |

---

## v0.25 — ACI 318-19 Beam

**Ref:** Architecture doc §20.8 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 3

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-742 | ACI 318-19 beam flexure | `codes/aci318/beam_flexure.py` | @structural-math | 📋 |
| TASK-743 | ACI 318-19 beam shear | `codes/aci318/beam_shear.py` | @structural-math | 📋 |
| — | PCA Notes (12th Ed.) benchmarks ±0.1% | @tester | 📋 |
| — | `@register_code("ACI318")` activation | @backend | 📋 |
| — | ACI318 FastAPI endpoints | @api-developer | 📋 |

### v0.26–v0.28 (Future)

| Version | Code | Elements | Benchmark Source |
|---------|------|----------|-----------------|
| v0.26 | ACI 318-19 | Column + Slab | PCA Notes |
| v0.27 | EC2 | Beam (flexure + shear) | Concrete Centre ±0.1% |
| v0.28 | EC2 | Column + Slab | Concrete Centre |

---

## v1.0 — Production Multi-Code Release

**Ref:** Architecture doc §20.9

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | INDIA-4 acceptance for the explicitly declared supported Indian RC subset; no whole-standard-complete claim | @structural-math + qualified structural engineer | 📋 |
| — | ACI 318 beam + column | @structural-math | 📋 |
| — | EC2 beam (basic) | @structural-math | 📋 |
| — | CalculationProvenance on all results (§11) | @backend | 📋 |
| — | Export integrity/watermarking (§11.3) | @backend | 📋 |
| — | Full OWASP compliance (§12) | @security | 📋 |
| — | API stability guarantee (no breaking changes without major version) | @backend | 📋 |
| — | Complete documentation coverage | @doc-master | 📋 |
| — | Performance benchmarks all met (§14.2) | @tester | 📋 |
| — | RBAC / scope enforcement (§3.5) | @api-developer | 📋 |
| — | Design audit trail middleware (§11.1) | @api-developer | 📋 |

### Post-v1.0 Research (from architecture doc §20.10)

| Item | Description | Status |
|------|-------------|--------|
| WASM compilation path | Layer 2 pure math → Pyodide/Rust for client-side calc | 🔲 Research |
| msgspec serialization | Benchmark vs frozen dataclass for batch perf | 🔲 Research |
| structuralcodes integration | Material models as optional backend | 🔲 Research |
| IS 16700 (tall buildings) | Wind/seismic response spectra | 🔲 Research |
| IS 1893 integration | Seismic load generation | 🔲 Research |

---

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | ⏸ Deferred | Deferred — needs LLM API design, not in v0.22 scope |
| TASK-908 | bats-core tests for git scripts | 🟢 Low | Deferred — requires bats-core install |
| API-5 | OpenAPI examples on Pydantic models | 🟢 Low | Moved from v0.22 — non-blocking |
| OPS-3 | Python dependency lock file | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-4 | Footing section in api.md | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-5 | Clause-to-function mapping | 🟢 Low | Moved from v0.22 — non-blocking |
| — | E2E integration test (React against live FastAPI) | 🟡 Medium | Target v0.21.6+ |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | 🟢 Low | Use `/optimization/cost-rates` |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |
| — | IS 456 extended elements (Wall Cl 32, Staircase Cl 33, Deep beam Cl 29) | 🟢 Low | Post v1.0 |
| — | Companion codes (IS 875, IS 1893, ASCE 7, EN 1990/1991) | 🟢 Low | Post v1.0 |

---

## Archive

Sessions 32–73 and legacy TASK items have been completed. See [docs/_archive/tasks-history.md](_archive/tasks-history.md) for details.

Key milestones from archived sessions:
- **Session 73** (Jan 24): FastAPI skeleton (20 routes, 31 tests), WebSocket endpoint, `discover_api_signatures.py`
- **Session 66** (Jan 24): V3 automation foundation, 143 scripts audited, API latency validated
- **Session 65** (Jan 23): Agent effectiveness research, `docs-canonical.json`, `automation-map.json`
- **Session 63** (Jan 23): Rebar consolidation, scanner fixes, TASK-350/351/352 resolved
- **Sessions 32–62c** (Jan 22): Rebar editor, DXF export, cost optimizer, section geometry

---

**Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history.
**Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
