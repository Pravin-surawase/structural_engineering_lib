---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: advanced
tags: [automation, scripts, audit, maintenance, archive, maint-008]
---

# Automation Script Audit — 2026-08-09

## Outcome

The active automation surface was audited one item at a time. The baseline
inventory contained **113 top-level scripts**. After all implementation,
governance, discovery, archive, and CLI-normalization batches, the active
surface contains **104 top-level scripts**: **87 Python** and **17 shell**,
totaling **40,034 lines**. The extended control surface also
contains the root `run.sh` dispatcher, four GitHub Actions workflows, zero
repository-enforcement Git hook entrypoints, three non-Git Python hook-framework
modules, and seven shared Python support modules.

The active scripts should **not** be archived in bulk. The evidence-backed
disposition is:

| Disposition | Count | Meaning |
|---|---:|---|
| Keep / updated | 92 | Supported role; all 30 confirmed update items were repaired in the completed batches |
| Review | 12 | Low-use, overlapping, or specialized; prove a current consumer before keeping or archiving |
| Archived in final batch | 3 | Proven replacements, reviewed safe-delete previews with no live callers, and Git-recoverable removal |
| **Total active** | **104** | Current inventory after all approved retirements/archives and the two maintained control additions |

The original audit was read-only. The user then authorized a P0 implementation
pass over five named scripts and directed that Git/GitHub work move to Codex.
The second authorized P0 batch removed five missing-script control targets and
closed the remaining P0 finding. The third authorized batch repaired five P1
agent-governance and permission scripts plus their direct shared controls. The
remaining batches repaired the discovery/control plane, archived only the three
proven candidates, and normalized the essential CLI and terminal paths.
No independent commit, push, PR mutation, merge, issue action, release, or
publication was performed during the bounded implementation passes themselves.
The follow-up closeout isolated their still-uncommitted changes from concurrent
product work before using the Codex-native Git/GitHub lifecycle.

## P0 implementation update — 2026-08-09

The five requested priority scripts were handled as follows:

| Requested script | Result | Outcome |
|---|---|---|
| `scripts/ai_commit.sh` | Retired | Codex now owns scoped staging, commits, pushes, and connected GitHub PR work. |
| `scripts/safe_push.sh` | Retired | Removed automatic stash/rebase/checkout/drop behavior from the supported workflow. |
| `scripts/recover_git_state.sh` | Retired | Recovery now fails closed: inspect exact state and stop before choosing a destructive path. |
| `scripts/finish_task_pr.sh` | Retired | Merge, cleanup, branch deletion, and release remain explicit user-confirmation actions. |
| `scripts/check_api.py` | Repaired | Scans production TS/TSX calls, fails on zero coverage, and matches method/path against live FastAPI OpenAPI. |

Three direct dependencies were also retired so the four wrappers could not be
reintroduced indirectly: `create_task_pr.sh`, `should_use_pr.sh`, and
`install_git_hooks.sh`. The three tracked enforcement hooks and the dormant
Python pre/post-commit hook modules were removed. `core.hooksPath` was cleared
from both local and global Git configuration; the standard pre-commit framework
hook remains available.

The obsolete Git-script line-budget check was replaced with
`check_codex_git_workflow.py`, which asserts that retired lifecycle paths remain
absent and that current authoritative instructions preserve the Codex-native
boundary. During verification, the repaired API checker found and enabled the
fix of a real production contract defect: the React SSE batch client used
`/api/v1/stream/batch-design`, while FastAPI exposes `/stream/batch-design`.

## P0 Batch 2 implementation update — 2026-08-09

The second batch addressed the five missing script targets individually:

| Missing target | Result | Outcome |
|---|---|---|
| `scripts/run_vba_smoke_tests.py` | Dead entrypoint removed | `run.sh` no longer exposes an unsupported `test --vba` lane. |
| `scripts/test_vba_adapter.py` | Dead entrypoint removed | The second failing command behind `test --vba` is no longer reachable. |
| `scripts/check_cost_optimizer_issues.py` | Dead hook removed | The archived cost-optimizer scanner is no longer an active pre-commit target. |
| `scripts/check_streamlit.py` | Two dead hooks removed | Both Streamlit AST/fragment hook entrypoints were removed. |
| `scripts/check_performance_issues.py` | Dead hook removed | The archived Streamlit performance scanner is no longer an active target. |

The missing files were already absent, so Batch 2 deleted no additional files.
`validate_script_refs.py` now scans `run.sh`, pre-commit, GitHub workflows, and
active top-level scripts for missing runtime targets, including `$SCRIPTS/...`
dispatcher calls. It fails on executable missing references while preserving
historical comments and consolidation docstrings as informational evidence.

## P1 Batch 3 implementation update — 2026-08-09

The next five individual scripts were repaired as an agent-governance and
permission-truth batch:

| Requested script | Result | Outcome |
|---|---|---|
| `scripts/agent_compliance_checker.py` | Repaired | Defaults to current-session evidence and returns failure when the session, agent attribution, or evidence set is absent. Historical selection remains explicit. |
| `scripts/agent_context.py` | Repaired | Loads the canonical 16-agent registry, validates its metadata, accepts every registered agent, and prints root-stable commands. |
| `scripts/agent_drift_detector.py` | Repaired | Current-session/no-evidence cases fail closed; the default is read-only and files are written only with `--write` or `--output`. |
| `scripts/agent_trends.py` | Repaired | Historical trend analysis is read-only by default, missing agents fail instead of receiving synthetic zero-score results, and writes are explicit. |
| `scripts/tool_permissions.py` | Repaired | Resolves explicit task and mode permissions, respects agent ceilings and file scope, and fails closed for unknown tasks or modes. |

Direct support changes made the five fixes enforceable: the shared agent-data
helper now identifies current dated sessions; the tool registry stopped
guessing permissions from keywords; automation-map entries declare the repaired
operations and mutating modes; and the permission/governance audits validate
that metadata. Two bounded read-only reviewers inspected the independent
evidence-selection and permission designs. Both used Terra; no Sol agent was
used.

## Terminal/worktree runtime repair — 2026-08-09

`run.sh`, `check_all.py`, `test_cli_smoke.py`, and 23 active pre-commit entries
assumed that every linked Git worktree contained its own `.venv`. That made the
first clean-worktree gate and commit hooks fail before their Python checks ran.

`scripts/python_runtime.sh` is now the single internal resolver. It uses, in
order, an explicit `STRUCTURAL_LIB_PYTHON`, the current checkout's `.venv`, the
primary Git worktree's `.venv`, or an active `VIRTUAL_ENV`; otherwise it exits
with an actionable error. The dispatcher, check orchestrator, smoke suite, and
pre-commit entries call this resolver. A linked worktree with no local `.venv`
now runs repository checks without a temporary link.

## Remaining batches completion update — 2026-08-10

Packets C3-C5 are complete:

| Area | Final outcome |
|---|---|
| Discovery truth | Removed the parallel legacy category structure; 113 supported tasks now derive 14 groups from canonical task metadata. |
| Registry integrity | `check_scripts_index.py` validates physical mapping plus legacy groups, missing groups, removed-but-active entries, and temporary targets. Current result: 104/104. |
| Gate integration | CLI smoke is part of the 30-check canonical gate and Repository Validation; an explicitly selected zero-check category fails instead of returning a false green. |
| Permission truth | Stateful/default/mode metadata now covers the remaining migration, index, evolution, session-store, pipeline, routing, preflight, archive, and local-CI commands. |
| Terminal/runtime | `agent_start.sh`, preflight, changed-test, evolution, watch, and session guidance use the worktree-aware runtime. Startup no longer changes global Git config, fetches/prunes refs, or queries GitHub. |
| Dry-run/data safety | Batch migration dry-run writes nothing; generated rollback uses safe file operations. Archive and root-file guidance use link-aware safe moves. External CLI refuses to replace an existing work directory. |
| Product cleanup | Stale Streamlit/VBA/Excel help and version targets were removed from maintained scripts without rewriting historical evidence. |
| Archive | `_tmp_add_groups.py`, `pre_commit_check.sh`, and `test_sample_endpoint.py` were removed after direct-caller searches and per-file safe-delete previews. Git history is the recovery path. |

Two bounded read-only reviewers were used for this final batch. Both used
Terra, received concise packets, and made no workspace edits; no Sol subagent
was used.

## Snapshot and scope

| Field | Value |
|---|---|
| Repository | `structural_engineering_lib` |
| Final-batch branch | `codex/automation-remaining-batches` |
| Final-batch baseline commit | `f812eb3f6422cba4d883eb81a6d2a9cab47d5c18` |
| Final-batch baseline subject | `fix(automation): close governance and control gaps` |
| Audit date | 2026-08-09 |
| Baseline active top-level scripts | 113 |
| Current active top-level scripts | 104 |
| Existing archived scripts | 101: 68 Python and 33 shell |
| Shared support modules | 7 under `scripts/_lib/` |
| Hook framework modules | 3 non-Git modules under `scripts/hooks/` |
| Repository-enforcement Git hook entrypoints | 0 under `scripts/git-hooks/` |
| Active workflows | 4 under `.github/workflows/` |
| Root dispatcher | `run.sh` |
| Subagents used | 4 bounded read-only Terra reviewers across Batches 3 and final; 0 Sol reviewers |

The 101 files already under `scripts/_archive/` were not re-reviewed as active
automation. Their boundary was checked instead: `validate_script_refs.py`
found no active runtime call to an archived-only or otherwise missing script.
Its 25 results were informational consolidation comments/docstrings only.

## Method

Every top-level `.py` and `.sh` file was individually included in the inventory
and received at least these checks:

1. physical file, catalog, and automation-map reconciliation;
2. Python AST parse or `bash -n` syntax validation;
3. safe `--help` execution where a recognizable help path existed;
4. caller search across `run.sh`, workflows, pre-commit, Git hooks, other
   scripts, active docs, and tests;
5. task/group/permission lookup through the active automation registry;
6. stale product-path, removed-script, mutation, dry-run, and duplication scan;
7. focused execution for suspicious read-only paths; and
8. keep/update/review/archive-candidate classification.

Potentially destructive modes were not executed. In particular, the audit did
not invoke Git recovery, commit, push, merge, branch deletion, file move/delete,
release, publication, auto-fix, or live migration modes.

## Verification summary

The table below preserves the baseline audit evidence. The P0 implementation
was then verified separately:

| P0 implementation check | Result |
|---|---|
| Codex-native Git workflow guard | pass; retired files absent and `core.hooksPath` clear |
| Current script index and automation map | 106/106 pass |
| API contract validation | 24 call sites / 9 files / 62 OpenAPI paths pass |
| API zero-coverage behavior | expected failure confirmed |
| Focused Python automation tests | 23/23 pass |
| Active script target validation | 0 runtime breaks; 25 informational historical references at P0 |
| Pre-commit configuration validation | pass |
| Focused React batch-design tests | 10/10 pass |
| Non-Git hook-framework self-test | 1/1 pass |
| Link validation | 1,050 links checked; 0 broken |
| Quick gate | 9/9 pass |
| Integrated full gate after P0 and library-first work | 29/29 pass |

The earlier generated-manifest and OpenAPI drift was resolved by the owning
library-first work before the final integrated gate.

Batch 3 verification was performed after the five-script P1 implementation:

| P1 Batch 3 check | Result |
|---|---|
| Canonical agent registry | 16/16 agents listed; `structural-math` focused context returned rc 0 |
| Current evidence defaults | compliance and drift returned expected rc 1 because only stale historical sessions were available |
| Read/write permission modes | reviewer read-only health allowed; `--fix` denied; undeclared operation denied |
| Focused governance/evolver tests | 106/106 pass |
| Formatting, lint, and compile | pass for all changed Python implementation/test files |
| Permission declaration audit | pass; no anomalies |
| Governance compliance | pass; explicit permission metadata check included |
| Script index | 106/106 pass |
| Active script target validation | 0 runtime breaks; 24 informational historical references |
| CLI smoke | 12/13 at initial Batch 3 verification; resolved to 13/13 in the worktree follow-up below |
| Quick gate | 9/9 pass |
| Full gate in isolated worktree | 29/29 pass |

The clean Codex worktree removed the unrelated API-manifest/OpenAPI drift seen
in the shared release worktree. The complete gate then passed without
regenerating or overwriting those concurrent owner-controlled artifacts.

The runtime follow-up was then verified in the same linked worktree after
removing its temporary `.venv` link:

| Worktree runtime check | Result |
|---|---|
| Runtime resolution | primary-worktree Python 3.11.15 selected without local `.venv` |
| Focused governance/runtime tests | 108/108 pass |
| Script index and automation map | 107/107 pass |
| CLI smoke | 13/13 pass using a guaranteed registered automation task |
| Quick gate without local `.venv` | 9/9 pass |
| Full gate without local `.venv` | 29/29 pass |

Final remaining-batch verification:

| Check | Result |
|---|---|
| Clean linked-worktree startup without local `.venv` | pass; primary-worktree Python 3.11.15 resolved |
| Script index and automation semantics | 104/104 physical coverage; 0 semantic errors |
| Automation discovery | 113 active tasks across 14 canonical groups |
| Permission declaration audit | pass; 0 anomalies |
| Focused automation/session/migration tests | 152/152 pass |
| CLI smoke | 13/13 pass |
| Quick gate | 10/10 pass |
| Full gate | 30/30 pass |
| Formatting, Ruff, compile, shell syntax | pass for changed implementation/test paths |

### Terminal issues encountered

- ⚠️ TERMINAL ISSUE: Homebrew Node 25 could not load `libsimdjson.29.dylib` → the bundled Codex Node runtime ran the focused Vitest lane successfully.
- ⚠️ TERMINAL ISSUE: `generate_enhanced_index.py` rejected multiple folder arguments → each affected folder was regenerated in a separate supported invocation.
- ⚠️ TERMINAL ISSUE: Vitest launched from the repository root missed the React jsdom configuration (`window is not defined`) → rerunning from `react_app/` passed 10/10 tests.
- ⚠️ TERMINAL ISSUE: a diagnostic zsh loop used the reserved `path` variable and temporarily hid `git` inside that one process → the verification was rerun in a clean shell with non-reserved names.
- ⚠️ TERMINAL ISSUE: an `rg` command placed `--glob` filters after the `--` pattern terminator, so ripgrep treated them as paths → the search was rerun with filters before `--`.
- ⚠️ TERMINAL ISSUE: the first Black check reported that `validate_script_refs.py` needed formatting → Black was applied and the final format check passed.
- ⚠️ TERMINAL ISSUE: clean linked-worktree session startup stopped because `agent_start.sh` required a local `.venv` → it now resolves the primary-worktree environment through `python_runtime.sh`; startup passed without copying or linking an environment.
- ⚠️ TERMINAL ISSUE: the first regenerated index check treated `python_runtime.sh` as the only mapped script in wrapped commands → the checker now collects every script target token; final coverage is 104/104.
- ⚠️ TERMINAL ISSUE: focused Ruff found an unused local in the touched type-annotation checker → the dead assignment was removed and the final lint passed.
- ⚠️ TERMINAL ISSUE: the first commit attempt stopped when the standard end-of-file hook normalized generated `scripts/index.json` → the hook-only newline change was inspected, staged, and the commit checks were rerun normally.

Baseline audit evidence before the completed remaining batches:

| Check | Result |
|---|---|
| Python AST parse, top-level | 89/89 pass |
| Shell syntax, top-level plus `run.sh` | 25/25 pass |
| Nested support/hook Python AST parse | 12/12 pass |
| Installed Git hook shell syntax | 3/3 pass |
| Safe help probes | 82/82 pass |
| Static-only scripts without recognized safe help path | 31 |
| Script index coverage | 113/113 at baseline; 107/107 after runtime follow-up |
| Automation-map physical coverage | 113/113 at baseline; 107/107 after runtime follow-up |
| Canonical full gate | 29/29 pass |
| Focused script/infrastructure tests | 218/218 pass |
| CLI smoke suite | 13/13 pass |
| Token-efficiency policy | pass |
| Skill assignment validation | pass |
| Workflow YAML parse | 4/4 pass |
| Python hook-framework self-test | 6/6 pass |
| Live PR #691 `PR Gate` | pass |
| ShellCheck | not installed; syntax only |
| actionlint | not installed; YAML parse only |

The final 30/30 gate now detects missing active script targets, vacuous API
signature scanning, malformed declared permission metadata, automation-map
semantic drift, and CLI smoke regressions. It still cannot prove runtime side
effects for every undeclared manual task; such a task must receive explicit
metadata before permission enforcement treats it as supported.

## Highest-priority confirmed issues

### P0 — Git safety automation conflicts with the written safety policy — RESOLVED

The scripts described as the safest path contain behavior that can change or
discard user state:

- `ai_commit.sh` exposes `--force` specifically to bypass the PR check, although
  `AGENTS.md` forbids that bypass. Its `--finish` path calls
  `finish_task_pr.sh --wait --force`.
- `safe_push.sh` can run `git checkout -- .`, stash/pop/drop working changes,
  and automatically rebase.
- `recover_git_state.sh` can run `git checkout -- .`, `git clean -fd`, and
  `git reset --hard` while being prescribed as the first recovery command.
- `finish_task_pr.sh` can merge, delete the remote branch, force-clean the
  worktree, hard-reset main, and delete local branches.
- the installed `pre-commit` and `pre-push` hooks accept
  `GIT_HOOKS_BYPASS=1`, while their output advertises that forbidden escape;
  `commit-msg` advertises `--no-verify`.
- no active test directly exercises `ai_commit.sh`, `safe_push.sh`,
  `recover_git_state.sh`, `finish_task_pr.sh`, or the installed Git hooks.

These were main-workflow and data-preservation defects, not generic hardening.
The wrapper and enforcement layer was retired rather than repaired. Current
instructions assign normal Git/GitHub closeout to Codex, preserve standard
validation, fail closed on unclear repository state, and keep destructive
actions behind explicit user confirmation.

### P0 — Five active control paths point to missing scripts — RESOLVED

| Surface | Missing target | Resolution |
|---|---|---|
| `run.sh` | `scripts/run_vba_smoke_tests.py` | Removed the unsupported `test --vba` dispatch branch. |
| `run.sh` | `scripts/test_vba_adapter.py` | Removed with the same unsupported dispatch lane. |
| `.pre-commit-config.yaml` | `scripts/check_cost_optimizer_issues.py` | Removed the dead archived-product hook. |
| `.pre-commit-config.yaml` | `scripts/check_streamlit.py` | Removed both dead Streamlit hooks. |
| `.pre-commit-config.yaml` | `scripts/check_performance_issues.py` | Removed the dead archived-product hook. |

`streamlit_app/`, `VBA/`, `Excel/`, `tests/apptest/`, and
`.pylintrc-streamlit` remain absent; no removed product tree was restored.
`validate_script_refs.py` now guards active control surfaces generically, so a
future missing target fails even when its name is not present in
`scripts/_archive/`.

### P0 — `check_api.py --signatures` passes without checking the React calls — RESOLVED

The signature lane defaults to `react_app/src` but scans only top-level
`*.py` files. That directory contains zero Python files; the React tree contains
93 `.ts`/`.tsx` files, including 16 hook files. The command therefore reports
“No API signature issues” without examining the live React API surface.

The selector now recursively scans production `.ts`/`.tsx` sources, resolves
direct and local-variable `fetch`/`EventSource` targets, extracts the HTTP
method, and matches path shapes against the live FastAPI OpenAPI schema. It
fails if the source tree or internal call-site count is zero. The pre-commit
trigger now covers React and FastAPI files. Current evidence is 24 call sites
across nine production files matched against 62 OpenAPI paths.

### P1 — Automation discovery is physically and semantically complete — RESOLVED

`automation-map.json` now has 113 active task entries in 14 groups derived from
each task's canonical `group` field. The parallel legacy-category structure,
dead Streamlit/VBA tasks, and the temporary map-migration task were removed.
`find_automation.py` reports the live counts dynamically and retains
`--category` only as an alias for canonical `--group` lookup.

`check_scripts_index.py` now fails on physical map/index drift, legacy category
data, missing task groups, removed-but-active descriptions, and temporary
targets. Current physical coverage is 104/104. The CLI smoke query uses the
guaranteed task `run tests`, while product-domain beam routing remains covered
separately by `prompt_router.py`.

### P1 — Permission labels do not match operation behavior — RESOLVED FOR DECLARED OPERATIONS

The keyword-based classifier was removed. The resolver now uses explicit task
and mode metadata, applies the registered agent ceiling and file scope, and
denies unknown task/mode combinations even when an agent has
`DangerFullAccess`. The permission audit and canonical governance gate reject
malformed declarations.

Fourteen high-value operations now have explicit defaults and ten declare
mutating modes. Examples verified in this batch include read-only `project
health` versus WorkspaceWrite `--fix`, and read-only drift/trends versus
WorkspaceWrite `--write`/`--output`. Undeclared task aliases are reported as
`Unspecified` instead of receiving invented labels; permission enforcement
rejects an undeclared operation or mode until metadata is added.

This resolves the misleading-label root cause. Future script batches should add
explicit metadata when an undeclared operation becomes an enforced entrypoint;
the audit does not claim that static inspection can prove every runtime side
effect.

### P1 — Agent governance automation can be false-green or unexpectedly write — RESOLVED

- `agent_context.py --list` now exposes and accepts all 16 canonical agents,
  validates the registry count/names, and emits root-stable commands.
- default compliance/drift checks require a current dated session and return
  nonzero for missing sessions, absent agent attribution, or empty evidence;
  historical sessions remain available only through explicit selectors.
- drift and trend reports are read-only by default; managed or custom output
  requires `--write` or `--output`.
- trend lookup for an absent agent returns failure instead of manufacturing a
  zero-score record.

Focused tests cover evidence availability, current-session selection, all 16
agents, root-stable commands, no-write defaults, explicit writes, and missing
agent behavior.

### P1 — `check_scripts_index.py` protects supported discovery behavior — RESOLVED

The semantic checks and canonical gate integration described above close the
confirmed discovery false-green. Inventory observations remain useful for
future disposition work:

## Maintenance-quality findings after completion

The 30 scripts with confirmed outcome or operator-contract defects were
repaired. Current catalog checks still report 20 of 87 Python scripts without a
“When to use” phrase and 371 legacy bare `python scripts/...` example lines in
the broader active tree. Those are informational style/catalog observations,
not confirmed main-process defects; update them only when the owning script is
otherwise changed. The essential scripts identified by this audit now use
root-stable examples and truthful help.

Inventory observations retained for later archive decisions:

- 20 scripts are manual-only: they have no active caller in `run.sh`, workflows,
  pre-commit, hooks, other scripts, or direct tests. Manual-only is not proof of
  obsolescence, but each should retain a named owner/use case or move to review.
- 28 scripts exceed 500 lines and eight exceed 800 lines. The largest are
  `session.py` (2,261), `release.py` (1,053), `check_governance.py` (1,041),
  `project_health.py` (902), and `launch_stack.sh` (884). Split only when a
  confirmed maintenance defect requires it; line count alone is not an archive
  reason.

## One-by-one disposition ledger

“Keep” means no outcome-changing defect was found in this bounded audit. It is
not a certification of every branch or an instruction to skip normal tests.

| Script | Group | Disposition | Evidence and next action |
|---|---|---|---|
| `_tmp_add_groups.py` | Infrastructure | ARCHIVED | One-time map migration was replaced by canonical task `group` metadata; removed after safe-delete preview. |
| `agent_brief.sh` | Session | KEEP | Dynamic agent brief handled all five newer agents; retain as the compact entrypoint. |
| `agent_compliance_checker.py` | Governance | KEEP (UPDATED) | Current-session selection and explicit historical selectors now fail closed on missing session, attribution, or evidence. |
| `agent_context.py` | Session | KEEP (UPDATED) | Canonical registry validation exposes all 16 agents and emits root-stable commands. |
| `agent_drift_detector.py` | Governance | KEEP (UPDATED) | Current evidence fails closed; default analysis is read-only and writes require `--write`/`--output`. |
| `agent_evolve_instructions.py` | Evolution | REVIEW | Manual-only evolution writer; retain only with the current evidence workflow. |
| `agent_feedback.py` | Governance | KEEP | Active feedback command; no outcome-changing defect found. |
| `agent_mistakes_report.sh` | Governance | KEEP | Session-start consumer works; no outcome-changing defect found. |
| `agent_scorer.py` | Governance | REVIEW | Review fallback scoring and stale-session inputs before operational use. |
| `agent_session_collector.py` | Governance | REVIEW | Manual-only collector; verify current Codex session source before keeping. |
| `agent_start.sh` | Session | KEEP (UPDATED) | Uses the canonical registry and worktree-aware runtime; no global Git config, ref pruning, GitHub query, or script-wide chmod remains. |
| `agent_trends.py` | Evolution | KEEP (UPDATED) | Historical analysis is read-only by default; absent agents fail and output writes are explicit. |
| `ai_commit.sh` | Git | RETIRED | Codex owns scoped commit, push, and connected GitHub PR work. |
| `archive_old_files.sh` | Docs | KEEP (UPDATED) | Live and dry-run paths use `safe_file_move.py`; dry-run creates no archive directory and counts survive the loop. |
| `audit_error_handling.py` | Quality | KEEP | Safe audit/help path passed; retain. |
| `audit_input_validation.py` | Quality | KEEP | Safe audit/help path passed; retain. |
| `audit_permissions.py` | Infrastructure | KEEP (UPDATED) | Validates explicit automation permission levels and mode declarations; static metadata is not runtime side-effect proof. |
| `audit_readiness_report.py` | Generation | KEEP | Canonical audit consumer works; retain. |
| `batch_migrate_runner.py` | Migration | KEEP (UPDATED) | Dry-run writes no log tree; live rollback manifests invoke validated safe move/delete operations. |
| `benchmark_api.py` | Testing | KEEP | Supported benchmark with explicit modes; retain. |
| `bump_version.py` | Release | KEEP (UPDATED) | Missing Excel/VBA documentation targets were removed and operator commands are root-stable. |
| `check_all.py` | Quality | KEEP (UPDATED) | Canonical 30-check orchestrator includes CLI smoke and fails explicit zero-check selections. |
| `check_api.py` | Discovery | KEEP (UPDATED) | Validates 24 production React call sites against 62 live OpenAPI paths and fails closed on zero coverage. |
| `check_api_compat.py` | Quality | KEEP (UPDATED) | Distinct compatibility check now has a clear use case and root-stable update guidance. |
| `check_architecture_boundaries.py` | Quality | KEEP | Focused and canonical architecture check passed. |
| `check_bootstrap_freshness.py` | Quality | KEEP | Canonical freshness check passed. |
| `check_circular_imports.py` | Quality | KEEP (UPDATED) | Title/help now match the Python structural library actually scanned. |
| `check_clause_coverage.py` | Quality | KEEP (UPDATED) | Structural coverage role now has a clear use case and root-stable examples. |
| `check_cli_reference.py` | Quality | KEEP | Canonical check passed. |
| `check_doc_versions.py` | Quality | KEEP | Canonical check passed. |
| `check_docker_config.py` | Infrastructure | KEEP | Canonical check passed. |
| `check_docs.py` | Docs | KEEP | Consolidated doc validation passed. |
| `check_fastapi_issues.py` | Infrastructure/Quality | KEEP | Active FastAPI scanner passed; remove only stale Streamlit aliases around it. |
| `check_function_quality.py` | Quality | KEEP (UPDATED) | Specialist quality check now has a clear use case and root-stable examples. |
| `check_codex_git_workflow.py` | Quality | KEEP (NEW) | Prevents retired lifecycle wrappers/hooks from returning and validates the canonical boundary. |
| `check_git_script_budget.py` | Quality | RETIRED | Wrapper line-budget control was replaced by the Codex-native boundary guard. |
| `check_governance.py` | Quality | KEEP | Canonical governance check passed. |
| `check_instruction_drift.py` | Quality | KEEP | Canonical drift check passed. |
| `check_links.py` | Docs | KEEP | Canonical link check passed. |
| `check_new_element_completeness.py` | Quality | KEEP (UPDATED) | Cross-layer element check now has a clear use case and root-stable examples. |
| `check_next_session_brief_length.py` | Quality | KEEP | Canonical check passed. |
| `check_not_main.sh` | Git | REVIEW | Manual-only guard duplicated in active Git wrappers. |
| `check_openapi_drift.py` | CI | REVIEW | Overlaps snapshot checker; retain only with documented exact-deep nightly distinction. |
| `check_openapi_snapshot.py` | Quality | REVIEW | Overlaps drift checker; retain only with documented PR-summary distinction. |
| `check_python_version.py` | Quality | KEEP | Canonical check passed. |
| `check_repo_hygiene.py` | Quality | KEEP | Canonical check passed. |
| `check_root_file_count.sh` | Quality | KEEP (UPDATED) | Printed remediation previews the link-aware safe move command. |
| `check_scripts_index.py` | Quality | KEEP (UPDATED) | Validates 104/104 physical coverage plus canonical group/active/temp semantic integrity. |
| `check_tasks_format.py` | Quality | KEEP | Canonical check passed. |
| `check_token_efficiency.py` | Agent Infrastructure | KEEP | Policy check passed. |
| `check_type_annotations.py` | Quality | KEEP (UPDATED) | Title/help now match the Python structural library actually scanned. |
| `check_unfinished_merge.sh` | Git | KEEP | Small active guard; canonical check passed. |
| `check_version_consistency.sh` | Quality | KEEP (UPDATED) | Removed the obsolete optional VBA probe; checks maintained package metadata only. |
| `check_wip_limits.sh` | Quality | REVIEW | Manual-only and likely overlaps `check_tasks_format.py`/`check_governance.py`. |
| `ci_local.sh` | Git | KEEP (UPDATED) | Delegates to maintained validation commands; it no longer installs environments or performs Git/GitHub work. |
| `cleanup_stale_branches.py` | Infrastructure | KEEP | Default is dry review; deletion remains explicit. |
| `collect_diagnostics.py` | Infrastructure | KEEP | Purpose is distinct; retain with explicit output expectations. |
| `collect_metrics.sh` | Infrastructure | REVIEW | Manual-only metrics writer; prove a scheduled/report consumer. |
| `config_precedence.py` | Infrastructure | KEEP (UPDATED) | Audit/list/show are explicitly ReadOnly with a safe default command. |
| `create_doc.py` | Docs | KEEP | Explicit creation tool with clear target; retain. |
| `create_task_pr.sh` | Git | RETIRED | PR creation/update moved to Codex and the connected GitHub integration. |
| `create_test_scaffold.py` | Testing | KEEP | Explicit generator with required target; retain. |
| `diagnose_ci.py` | Quality | KEEP (UPDATED) | Read-only diagnosis is separate from explicit WorkspaceWrite `--local --fix`. |
| `discover_api_signatures.py` | Discovery | KEEP | Focused lookup and tests passed. |
| `dxf_render.py` | Infrastructure | KEEP | Distinct product-support utility; retain. |
| `evolve.py` | Evolution | KEEP (UPDATED) | Preview/review is read-only; reports require `--report` and changes require `--fix`. |
| `export_paper_data.py` | Infrastructure | REVIEW | Research-only exporter with no active caller; move to research tooling or archive. |
| `external_cli_test.py` | Testing | KEEP (UPDATED) | Uses a unique temp directory by default and refuses to replace an explicit existing directory. |
| `find_automation.py` | Discovery | KEEP (UPDATED) | Reports 113 active tasks/14 canonical groups dynamically and hides removed/temp entries. |
| `finish_task_pr.sh` | Git | RETIRED | Removed automatic merge/clean/reset/delete behavior. |
| `fix_broken_links.py` | Docs | REVIEW | One-time removed-product cleanup; archive after remaining cleanup is complete. |
| `generate_all_indexes.sh` | Generation | KEEP | Canonical explicit generator; retain. |
| `generate_api_manifest.py` | Discovery | KEEP | Check/generate modes are explicit and canonical. |
| `generate_client_sdks.py` | Generation | KEEP | Explicit generator; retain. |
| `generate_docs_index.py` | Generation | KEEP | Preview/write split is clear; retain. |
| `generate_enhanced_index.py` | Generation | KEEP (UPDATED) | Default is WorkspaceWrite while `--dry-run`/`--check` are explicitly ReadOnly. |
| `generate_error_docs.py` | Generation | KEEP | Check/generate role is distinct; retain. |
| `governance_health_score.py` | Quality | REVIEW | Overlaps `project_health.py` and uses fallback metrics; define one canonical score. |
| `install_git_hooks.sh` | Git | RETIRED | Custom `core.hooksPath` enforcement was removed locally and globally. |
| `launch_stack.sh` | Infrastructure | KEEP | Canonical dev launcher; retain and keep listener-only cleanup evidence. |
| `migrate_python_module.py` | Migration | KEEP | Dry-run is tested; retain. |
| `migrate_react_component.py` | Migration | KEEP | Dry-run is tested; retain. |
| `model_picker.py` | Agent Infrastructure | KEEP | Advisory-only behavior and focused tests passed. |
| `parity_dashboard.py` | Quality | KEEP (UPDATED) | Cross-stack evidence role now has a clear use case and root-stable examples. |
| `pipeline_state.py` | Infrastructure | KEEP (UPDATED) | Read commands and state-changing commands now have explicit distinct permissions. |
| `pre_commit_check.sh` | Git | ARCHIVED | Duplicate manual wrapper removed after safe-delete preview; canonical checks remain. |
| `preflight.py` | Session | KEEP (UPDATED) | Has argparse help, a clear use case, runtime resolution, and worktree-safe merge detection. |
| `project_health.py` | Governance | KEEP (UPDATED) | Canonical role retained; automation metadata now declares read-only default versus WorkspaceWrite `--fix`. |
| `prompt_router.py` | Infrastructure | KEEP (UPDATED) | Normal routing is explicitly ReadOnly and examples are root-stable. |
| `python_runtime.sh` | Infrastructure | KEEP (NEW) | Resolves an approved Python interpreter across primary and linked Git worktrees without creating or copying environments. |
| `recover_git_state.sh` | Git | RETIRED | Unclear Git state now stops for Codex inspection; no automated destructive recovery. |
| `release.py` | Release | KEEP | Canonical release CLI and focused tests passed; publishing still requires approval. |
| `repo_health_check.sh` | Governance | REVIEW | Manual disk/file diagnostic overlaps health and diagnostics tools. |
| `safe_file_delete.py` | Docs | KEEP | Explicit dry-run and backup behavior; retain, then repair callers that bypass it. |
| `safe_file_move.py` | Docs | KEEP | Tested dry-run and link-aware behavior; retain. |
| `safe_push.sh` | Git | RETIRED | Removed automatic checkout/stash/drop/rebase behavior. |
| `session.py` | Session | KEEP | Canonical session CLI and focused tests passed. |
| `session_store.py` | Infrastructure | KEEP (UPDATED) | Read commands and state-changing `new`/`end` commands now have explicit distinct permissions. |
| `should_use_pr.sh` | Git | RETIRED | Codex applies the documented PR policy from actual task scope. |
| `skill_tiers.py` | Infrastructure | KEEP | Canonical validation passed. |
| `sync_numbers.py` | Session | KEEP | Preview versus `--fix` is explicit; retain. |
| `test_api_parity.py` | Testing | KEEP (UPDATED) | Framing now matches the active React/FastAPI architecture. |
| `test_changed.py` | Testing | KEEP (UPDATED) | Has a clear use case and uses the worktree-aware runtime with root-stable paths. |
| `test_cli_smoke.py` | Testing | KEEP (UPDATED) | 13/13 pass and the standalone suite now runs in the canonical local and PR validation paths. |
| `test_import_pipeline.py` | Testing | KEEP (UPDATED) | Documents the live FastAPI prerequisite and remains the maintained import E2E path. |
| `test_sample_endpoint.py` | Testing | ARCHIVED | Redundant subset removed after safe-delete preview; coverage remains in `test_import_pipeline.py`. |
| `tool_permissions.py` | Infrastructure | KEEP (UPDATED) | Explicit operation/mode resolver applies agent ceilings and file scope and fails closed on undeclared input. |
| `tool_registry.py` | Infrastructure | KEEP (UPDATED) | Explicit permission resolution remains and temp/stale discovery aliases were removed from the canonical map. |
| `update_test_stats.py` | Testing | KEEP | Report versus write modes are explicit; retain. |
| `validate_api_contracts.py` | Quality | KEEP | Canonical contract check passed. |
| `validate_git_state.sh` | Git | KEEP | Canonical read-only validation passed. |
| `validate_imports.py` | Quality | KEEP | Canonical import validation passed. |
| `validate_schema_snapshots.py` | Quality | KEEP | Canonical snapshot validation passed. |
| `validate_script_refs.py` | Quality | KEEP (UPDATED) | Scans active CLI, pre-commit, workflow, and script surfaces and fails on any executable missing target. |
| `watch_tests.sh` | Testing | KEEP (UPDATED) | Uses the runtime resolver, defaults to `Python/tests/`, has help that works without `fswatch`, and no longer prints legacy Streamlit status. |

## Extended control-surface disposition

### Root/configuration entrypoints

| Item | Disposition | Evidence and next action |
|---|---|---|
| `run.sh` | KEEP (UPDATED) | Broken `test --vba` dispatch/help/completion entries removed; supported test lanes retained. |
| `.pre-commit-config.yaml` | KEEP (UPDATED) | Missing-target Streamlit hooks removed; current React/FastAPI/Python hooks retained. |
| `scripts/automation-map.json` | KEEP (UPDATED) | 104/104 physical coverage, 113 active tasks, 14 canonical groups, and explicit high-value operation/mode permissions. |
| `scripts/index.json` / `index.md` | KEEP (REGENERATED) | Regenerated after the three approved archives; physical inventory is 104/104. |
| `scripts/README.md` | KEEP (UPDATED) | Codex-native Git boundary and worktree-aware runtime guidance now match supported behavior. |

### Git hook entrypoints

| Item | Status | Disposition |
|---|---|---|
| `scripts/git-hooks/commit-msg` | Retired | Removed with the wrapper-enforcement layer. |
| `scripts/git-hooks/pre-commit` | Retired | Removed; the standard pre-commit framework hook remains. |
| `scripts/git-hooks/pre-push` | Retired | Removed with its bypass and Git-lifecycle enforcement. |

### Python hook framework

The pre/post-commit modules were retired. The three remaining non-Git framework
files parse and their self-test passes 1/1.

| Item | Disposition |
|---|---|
| `scripts/hooks/__init__.py` | REVIEW: integrate as the one hook framework or archive the dormant framework. |
| `scripts/hooks/__main__.py` | REVIEW with framework. |
| `scripts/hooks/post_commit.py` | RETIRED with Git lifecycle automation. |
| `scripts/hooks/pre_commit.py` | RETIRED with Git lifecycle automation. |
| `scripts/hooks/pre_route.py` | REVIEW with framework. |

### Shared support modules

All seven modules under `scripts/_lib/` parse. The evolver tests cover important
parts of agent data, registry, and scoring behavior.

| Item | Disposition |
|---|---|
| `scripts/_lib/__init__.py` | KEEP |
| `scripts/_lib/agent_data.py` | KEEP (UPDATED); shared current-session selection is covered by focused tests |
| `scripts/_lib/agent_registry.py` | KEEP; use it to eliminate hard-coded agent lists |
| `scripts/_lib/ast_helpers.py` | KEEP |
| `scripts/_lib/output.py` | KEEP |
| `scripts/_lib/scoring.py` | REVIEW with scorer fallback/evidence policy |
| `scripts/_lib/utils.py` | KEEP |

### GitHub Actions workflows

| Workflow | Static result | Live evidence | Disposition |
|---|---|---|---|
| `fast-checks.yml` | YAML pass | PR #691 run `31315505152` and `PR Gate` pass | KEEP/UPDATE: retain lane, add the missing control-surface checks and real API-call validation. |
| `nightly.yml` | YAML pass | No run of the new weekly definition yet; listed failures are from the old Nightly QA on main | KEEP/PENDING: manually validate after merge; do not infer success from old runs. |
| `publish.yml` | YAML pass | Last listed runs are April release runs, not this branch definition | KEEP/PENDING: validate without publishing; production remains tag/approval only. |
| `deploy-docs.yml` | YAML pass | recent main runs pass | KEEP |

## Recommended next maintenance sequence

### Packet C1 — Fail-closed control paths

1. **Completed:** remove the five missing-script entrypoints from `run.sh` and pre-commit.
2. **Completed:** replace the vacuous API lane with the live React/OpenAPI contract check.
3. **Completed for P0:** active-target validation now fails closed; category and CLI-smoke improvements remain P1.
4. **Completed locally:** focused checks and `./run.sh check --quick`; connected CI review belongs to Codex closeout.

### Packet C2 — Git data-preservation repair

**Completed by retirement:** the wrapper scripts, their direct dependencies,
custom enforcement hooks, and dormant pre/post-commit modules were removed.
Codex now owns ordinary scoped Git/GitHub work, while merge, branch deletion,
issue closure, release, and history rewriting retain explicit approval gates.

### Packet C3 — Registry and agent truth

1. **Completed:** the canonical 16-agent registry now drives agent context.
2. **Completed:** compliance and drift fail closed on missing/current evidence.
3. **Completed:** drift and trend analysis is read-only unless writing is
   explicitly requested.
4. **Completed:** declared operation/mode permissions are enforced without
   keyword guessing, and temp/removed discovery aliases are gone.
5. **Completed:** the CLI smoke case passes 13/13 and runs in the canonical
   local and Repository Validation gates.

### Packet C4 — Archive/consolidate the proven candidates

**Completed:** only these three proven candidates were archived:

```text
scripts/_tmp_add_groups.py
scripts/pre_commit_check.sh
scripts/test_sample_endpoint.py
```

For each item:

```bash
rg -n "candidate_name|candidate_path" run.sh .github .pre-commit-config.yaml scripts docs AGENTS.md
./scripts/python_runtime.sh scripts/safe_file_delete.py --dry-run scripts/candidate
```

Each file passed a parent-verified dry-run after caller inspection. The files
were removed through `safe_file_delete.py`, and the map/index surfaces were
updated in the same branch. Recovery remains available through Git history.

### Packet C5 — Low-priority CLI/documentation normalization

**Completed:** repaired the confirmed help/“When to use”/root-stable examples
in one surgical pass. Working scripts were not mass-rewritten or split solely
to improve counts. The 12 `REVIEW` items remain active because the evidence is
insufficient to archive them safely.

## Archive decision rules for future sessions

A script may be archived only when all of the following are true:

1. it has no active caller in `run.sh`, workflows, pre-commit, installed hooks,
   other active scripts, packages, or current docs;
2. its behavior is replaced by a named supported command, or the behavior is
   no longer part of the supported product/workflow;
3. no unique main-process evidence is lost;
4. the safe-delete preview reports no unresolved live references;
5. index, map, help, tests, and docs are updated in the same bounded change;
6. quick and live PR gates pass; and
7. any destructive GitHub action has separate owner approval.

File age, line count, a temporary-looking name, or absence from `run.sh` alone
is not sufficient evidence.

## Commands and evidence

Key commands used in this audit:

```text
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh scripts/check_scripts_index.py --json
./scripts/python_runtime.sh scripts/validate_script_refs.py
bash -n <each active shell script and hook>
AST parse <each active Python script and support module>
safe --help probe <each script with a recognizable help path>
./scripts/python_runtime.sh scripts/test_cli_smoke.py --json
./run.sh check
./scripts/python_runtime.sh -m pytest -q <focused script/infrastructure test files>
./run.sh efficiency check
./scripts/python_runtime.sh scripts/skill_tiers.py validate
gh pr checks 691
gh run list --workflow <each retained workflow> --limit 3
```

Prior Batch 3 live PR evidence:

- `PR Gate`: pass
- `Python Validation`: pass
- `Repository Validation`: pass
- `FastAPI Validation`: intentionally skipped for this change set
- `React Validation`: intentionally skipped for this change set
- run: `https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/31315505152`

No release or publication workflow was triggered.

## Audit limitations and terminal notes

- `shellcheck` and `actionlint` are not installed. Shell received syntax
  validation and workflow YAML received parser validation, but not those deeper
  linters.
- `test_import_pipeline.py` was inspected rather than executed because this
  audit did not start/alter the live development stack. Its redundant sample
  subset was archived only after the maintained test was compared directly.
- A temporary-fixture live batch migration verified rollback manifests; the
  three approved archive candidates were removed through the safe-delete tool.
  Git recovery, merge, branch deletion, release, publication, and auto-fix
  modes were not executed during the implementation batches.
- The baseline audit observed default writes from drift/trends. Batch 3 removed
  that behavior and focused tests prove no output directory is created by the
  default commands.
- The original `./run.sh session end --agent orchestrator` returned exit 1 for
  three uncommitted documentation paths. The later Git closeout used a clean,
  isolated worktree so concurrent project changes were not staged. No `--fix`
  mode was run.
- **TERMINAL ISSUE:** an early `awk` inventory expression failed with a quoting
  error -> simpler `git ls-files`, Perl, and Python path-based counts produced
  the reconciled 113-script inventory.
- ⚠️ TERMINAL ISSUE: Ruff caught `required_level` inserted into the wrong
  permission helper during the first patch -> it was moved into
  `check_permission`, then formatting, lint, compile, and focused tests passed.
- ⚠️ TERMINAL ISSUE: `tool_registry.py` uses mutually exclusive query flags, so
  a combined `--permission Unspecified --stats` probe was rejected -> the two
  read-only queries were rerun separately and passed.
- ✅ RESOLVED TERMINAL ISSUE: the first clean-worktree gate and commit hooks
  could not find a local `.venv` and stopped before running Python checks ->
  `python_runtime.sh` now resolves the primary worktree environment, and the
  same linked worktree runs without a temporary link.
- ⚠️ TERMINAL ISSUE: a repository-wide `pre-commit --all-files` probe exposed
  pre-existing YAML/JSONC/Bandit/EOF debt and reformatted unrelated legacy and
  vendor files -> the exact hook-only edits were reversed, the intended 12-file
  scope was preserved, and pre-commit was rerun only against that scope.
- ⚠️ TERMINAL ISSUE: the first audit-index refresh used the absent pluralized
  `generate_folder_indexes.py` name -> the active
  `generate_enhanced_index.py docs/audit` command regenerated both indexes.
- ⚠️ TERMINAL ISSUE: a focused pytest command guessed two split test filenames
  that do not exist -> the repository's combined
  `test_agent_governance_automation.py` suite was run directly.
- ⚠️ TERMINAL ISSUE: the first automated transfer used standard Git range hunk
  headers that the patch tool did not accept -> the same exact-file patch was
  reapplied with supported hunk headers and verified with formatting, tests,
  and `git diff --check`.

## Handoff

Both confirmed P0 automation batches and the five-script P1 agent-governance
batch are complete. The next batch should address the remaining P1
automation-discovery/control-validation scripts, beginning with stale
categories and advertised task counts, not bulk archiving.
Preserve this report as the decision ledger and refresh caller/live-run evidence
immediately before edits. Do not merge a PR, publish a release, close
historical issues, or delete remote branches without separate owner approval.
The batch is isolated on its own Codex branch; preserve that separation during
review and do not pull concurrent release/product changes into its PR.
