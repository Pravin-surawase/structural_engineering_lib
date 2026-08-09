---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: reference
complexity: advanced
tags: [automation, scripts, audit, maintenance, archive, maint-008]
---

# Automation Script Audit — 2026-08-09

## Outcome

The active automation surface was audited one item at a time. The baseline
inventory contained **113 top-level scripts**. After the first P0 implementation
pass, the active surface contains **106 top-level scripts**: **89 Python** and
**17 shell**, totaling **39,811 lines**. The extended control surface also
contains the root `run.sh` dispatcher, four GitHub Actions workflows, zero
repository-enforcement Git hook entrypoints, three non-Git Python hook-framework
modules, and seven shared Python support modules.

The active scripts should **not** be archived in bulk. The evidence-backed
disposition is:

| Disposition | Count | Meaning |
|---|---:|---|
| Keep | 53 | Supported role, including the repaired API contract checker and new Codex workflow guard |
| Update | 37 | Active or useful, but a confirmed defect, stale contract, unsafe behavior, or metadata problem still needs repair |
| Review | 13 | Low-use, overlapping, or specialized; prove a current consumer before keeping or archiving |
| Archive candidate | 3 | Strong evidence of replacement or one-time use; still requires safe-delete preview and owner acceptance |
| **Total active** | **106** | Current top-level script inventory after seven wrapper retirements |

The original audit was read-only. The user then authorized a P0 implementation
pass over five named scripts and directed that Git/GitHub work move to Codex.
No independent commit, push, PR mutation, merge, issue action, release, or
publication was performed during the bounded P0 implementation; its changes
were integrated into the parent `LIB-IS456-V1` branch for native Git closeout.

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

## Snapshot and scope

| Field | Value |
|---|---|
| Repository | `structural_engineering_lib` |
| Branch | `task/LIB-IS456-V1` |
| Baseline commit | `8bfdac09564995a04bd0fb249b90934cd4c80011` |
| Baseline subject | `ci(maint-008): consolidate GitHub workflow lanes` |
| Audit date | 2026-08-09 |
| Baseline active top-level scripts | 113 |
| Current active top-level scripts | 106 |
| Existing archived scripts | 101: 68 Python and 33 shell |
| Shared support modules | 7 under `scripts/_lib/` |
| Hook framework modules | 3 non-Git modules under `scripts/hooks/` |
| Repository-enforcement Git hook entrypoints | 0 under `scripts/git-hooks/` |
| Active workflows | 4 under `.github/workflows/` |
| Root dispatcher | `run.sh` |
| Subagents used | 0 |

The 101 files already under `scripts/_archive/` were not re-reviewed as active
automation. Their boundary was checked instead: `validate_script_refs.py`
found no active runtime call to an archived-only script. Its 13 results were
informational consolidation comments/docstrings only.

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
| Focused Python automation tests | 21/21 pass |
| Focused React batch-design tests | 10/10 pass |
| Non-Git hook-framework self-test | 1/1 pass |
| Link validation | 1,048 links checked; 0 broken |
| Quick gate | 9/9 pass |
| Integrated full gate after P0 and library-first work | 29/29 pass |

The earlier generated-manifest and OpenAPI drift was resolved by the owning
library-first work before the final integrated gate.

### Terminal issues encountered

- ⚠️ TERMINAL ISSUE: Homebrew Node 25 could not load `libsimdjson.29.dylib` → the bundled Codex Node runtime ran the focused Vitest lane successfully.
- ⚠️ TERMINAL ISSUE: `generate_enhanced_index.py` rejected multiple folder arguments → each affected folder was regenerated in a separate supported invocation.
- ⚠️ TERMINAL ISSUE: Vitest launched from the repository root missed the React jsdom configuration (`window is not defined`) → rerunning from `react_app/` passed 10/10 tests.
- ⚠️ TERMINAL ISSUE: a diagnostic zsh loop used the reserved `path` variable and temporarily hid `git` inside that one process → the verification was rerun in a clean shell with non-reserved names.

| Check | Result |
|---|---|
| Python AST parse, top-level | 89/89 pass |
| Shell syntax, top-level plus `run.sh` | 25/25 pass |
| Nested support/hook Python AST parse | 12/12 pass |
| Installed Git hook shell syntax | 3/3 pass |
| Safe help probes | 82/82 pass |
| Static-only scripts without recognized safe help path | 31 |
| Script index coverage | 113/113 pass at baseline; 106/106 after P0 retirement |
| Automation-map physical coverage | 113/113 pass at baseline; 106/106 after P0 retirement |
| Canonical full gate | 29/29 pass |
| Focused script/infrastructure tests | 218/218 pass |
| CLI smoke suite | 12/13 pass; `find_automation.py beam` fails |
| Token-efficiency policy | pass |
| Skill assignment validation | pass |
| Workflow YAML parse | 4/4 pass |
| Python hook-framework self-test | 6/6 pass |
| Live PR #691 `PR Gate` | pass |
| ShellCheck | not installed; syntax only |
| actionlint | not installed; YAML parse only |

The green 29/29 gate is useful but incomplete. It does not currently detect
missing `run.sh`/pre-commit targets, automation-map category drift, vacuous API
signature scanning, behavior-inaccurate permission metadata, or the failing CLI
smoke case.

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

### P0 — Five active control paths point to missing scripts

| Surface | Missing target | Current behavior |
|---|---|---|
| `run.sh` | `scripts/run_vba_smoke_tests.py` | `./run.sh test --vba` fails |
| `run.sh` | `scripts/test_vba_adapter.py` | `./run.sh test --vba` fails |
| `.pre-commit-config.yaml` | `scripts/check_cost_optimizer_issues.py` | Dead hook filtered to removed Streamlit path |
| `.pre-commit-config.yaml` | `scripts/check_streamlit.py` | Two dead hooks filtered to removed Streamlit path |
| `.pre-commit-config.yaml` | `scripts/check_performance_issues.py` | Dead hook filtered to removed Streamlit path |

`streamlit_app/`, `VBA/`, `Excel/`, `tests/apptest/`, and
`.pylintrc-streamlit` are also absent. Remove these dead entrypoints rather than
restoring removed product trees. The existing `validate_script_refs.py` did not
find them because it only compares active scripts against names present in
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

### P1 — Automation discovery is physically complete but semantically stale

`automation-map.json` has 125 task entries and 17 legacy categories. The file
maps all 113 physical scripts, but its semantic integrity has drifted:

- seven category members do not exist as tasks;
- 14 task entries are not present in any legacy category;
- three duplicate-command groups represent compatibility aliases;
- `test vba adapter` says its target was removed but is not marked deprecated;
- Streamlit and VBA categories still produce removed-product results;
- `_tmp_add_groups.py` is exposed as a supported WorkspaceWrite tool; and
- `find_automation.py` still claims 87 tasks/16 categories.

The CLI smoke test fails because `find_automation.py beam` returns no result.
Either change the smoke query to a guaranteed automation task or add a truthful
beam-workflow mapping. Do not keep a failing test merely to prove the runner can
fail.

### P1 — Permission labels do not match operation behavior

`audit_permissions.py --check` reports no anomalies, but it checks registry
consistency, not the script's real side effects. Examples:

- `generate_enhanced_index.py`, `pipeline_state.py`, and `session_store.py` are
  labeled ReadOnly even though normal subcommands write files/state;
- `prompt_router.py` and `config_precedence.py` are labeled WorkspaceWrite even
  though their normal route/audit modes are read-only;
- check-only utilities inherit DangerFullAccess from the assigned agent; and
- one script with both read-only and mutating modes receives only one permission
  label.

Model permissions per operation/subcommand, or conservatively use the maximum
side effect while documenting a safe read-only invocation. Extend the
permission audit to compare declared metadata with observed/static behavior.

### P1 — Agent governance automation can be false-green or unexpectedly write

- `agent_context.py --list` exposes only 11 of the current 16 agents. It rejects
  `structural-math`, `security`, `library-expert`, `innovator`, and
  `agent-evolver`, even though `AGENTS.md` claims all 16 are supported.
- four commands printed by `agent_context.py` use
  `cd Python && .venv/bin/python ...`, which points to a nonexistent venv.
- `agent_compliance_checker.py --agent orchestrator` selected a stale
  2026-04-07 session, produced an empty result set, returned zero, and then
  printed “All compliance checks passed.”
- `agent_drift_detector.py` and `agent_trends.py` wrote ignored local report
  files during their default analysis invocations. Their output was based on
  stale April session data rather than the current task.

Prefer the dynamic registry-backed `agent_brief.sh`, which successfully handled
all five newer agents in focused checks. Make no-evidence cases fail closed and
make report-only/no-write behavior explicit.

### P1 — `check_scripts_index.py` protects counts, not supported behavior

The index checker passes 113/113 while all P0 findings above remain. Expand it
or add a narrow control-surface validator that checks:

1. every active `run.sh`, pre-commit, workflow, and hook script target exists;
2. every automation category member resolves to a task;
3. deprecated/removed descriptions agree with deprecated metadata;
4. every destructive operation has a truthful preview/no-write path;
5. required CLI smoke cases pass; and
6. a validation lane cannot pass after scanning zero applicable files unless
   zero is the explicitly expected result.

## Maintenance-quality findings

These are lower priority than the P0/P1 items and should be handled in a compact
documentation/CLI-contract pass, not as 60 separate rewrites:

- 35 of 89 Python scripts lack the catalog's required “When to use” contract.
- 31 of the baseline 113 top-level scripts had no safely recognized `--help` path, despite
  the scripts README saying all scripts should support help.
- 60 scripts contain 309 bare `python scripts/...` command examples instead of
  the root-stable `.venv/bin/python` or `./run.sh` entrypoint.
- `agent_context.py` contains four specifically broken
  `cd Python && .venv/bin/python` commands.
- `check_root_file_count.sh` recommends raw `git mv` instead of
  `safe_file_move.py`.
- `check_circular_imports.py` and `check_type_annotations.py` now scan the
  Python library correctly, but their titles/help still describe Streamlit.
- `check_version_consistency.sh`, `bump_version.py`, `test_api_parity.py`, and
  `watch_tests.sh` retain removed VBA/Streamlit framing.
- 20 scripts are manual-only: they have no active caller in `run.sh`, workflows,
  pre-commit, hooks, other scripts, or direct tests. Manual-only is not proof of
  obsolescence, but each should retain a named owner/use case or move to review.
- 30 scripts exceed 500 lines and nine exceed 800 lines. The largest are
  `session.py` (2,258), `release.py` (1,053), `check_governance.py` (1,025),
  `project_health.py` (900), and `launch_stack.sh` (884). Split only when a
  confirmed maintenance defect requires it; line count alone is not an archive
  reason.

## One-by-one disposition ledger

“Keep” means no outcome-changing defect was found in this bounded audit. It is
not a certification of every branch or an instruction to skip normal tests.

| Script | Group | Disposition | Evidence and next action |
|---|---|---|---|
| `_tmp_add_groups.py` | Infrastructure | ARCHIVE CANDIDATE | One-time map migration says delete after use; no active caller. |
| `agent_brief.sh` | Session | KEEP | Dynamic agent brief handled all five newer agents; retain as the compact entrypoint. |
| `agent_compliance_checker.py` | Governance | UPDATE | Empty compliance set returned rc 0 and “all passed”; fail closed on no evidence. |
| `agent_context.py` | Session | UPDATE | Only 11/16 agents; four broken `cd Python/.venv` commands; consolidate with dynamic registry. |
| `agent_drift_detector.py` | Governance | UPDATE | Default run writes ignored reports and selected stale session; add no-write/current selection. |
| `agent_evolve_instructions.py` | Evolution | REVIEW | Manual-only evolution writer; retain only with the current evidence workflow. |
| `agent_feedback.py` | Governance | KEEP | Active feedback command; no outcome-changing defect found. |
| `agent_mistakes_report.sh` | Governance | KEEP | Session-start consumer works; no outcome-changing defect found. |
| `agent_scorer.py` | Governance | REVIEW | Review fallback scoring and stale-session inputs before operational use. |
| `agent_session_collector.py` | Governance | REVIEW | Manual-only collector; verify current Codex session source before keeping. |
| `agent_start.sh` | Session | UPDATE | Depends on incomplete `agent_context.py` for named-agent deep context. |
| `agent_trends.py` | Evolution | REVIEW | Writes output by default and selected stale April data during audit. |
| `ai_commit.sh` | Git | RETIRED | Codex owns scoped commit, push, and connected GitHub PR work. |
| `archive_old_files.sh` | Docs | UPDATE | Uses raw `mv` instead of link-aware safe file operations. |
| `audit_error_handling.py` | Quality | KEEP | Safe audit/help path passed; retain. |
| `audit_input_validation.py` | Quality | KEEP | Safe audit/help path passed; retain. |
| `audit_permissions.py` | Infrastructure | KEEP | Retain registry-consistency audit, but do not treat it as behavior validation. |
| `audit_readiness_report.py` | Generation | KEEP | Canonical audit consumer works; retain. |
| `batch_migrate_runner.py` | Migration | UPDATE | `--dry-run` still creates logs; rollback script emits raw `rm`/`cp`. |
| `benchmark_api.py` | Testing | KEEP | Supported benchmark with explicit modes; retain. |
| `bump_version.py` | Release | UPDATE | Remove stale missing Excel/VBA doc targets and normalize commands. |
| `check_all.py` | Quality | KEEP | Canonical 29-check orchestrator works; expand coverage through focused validators, not ad hoc duplication. |
| `check_api.py` | Discovery | KEEP (UPDATED) | Validates 24 production React call sites against 60 live OpenAPI paths and fails closed on zero coverage. |
| `check_api_compat.py` | Quality | UPDATE | Add missing “When to use”/CLI contract; underlying check is distinct and useful. |
| `check_architecture_boundaries.py` | Quality | KEEP | Focused and canonical architecture check passed. |
| `check_bootstrap_freshness.py` | Quality | KEEP | Canonical freshness check passed. |
| `check_circular_imports.py` | Quality | UPDATE | Implementation scans Python core, but title/help still say Streamlit. |
| `check_clause_coverage.py` | Quality | UPDATE | Add missing “When to use” contract; retain structural coverage role. |
| `check_cli_reference.py` | Quality | KEEP | Canonical check passed. |
| `check_doc_versions.py` | Quality | KEEP | Canonical check passed. |
| `check_docker_config.py` | Infrastructure | KEEP | Canonical check passed. |
| `check_docs.py` | Docs | KEEP | Consolidated doc validation passed. |
| `check_fastapi_issues.py` | Infrastructure/Quality | KEEP | Active FastAPI scanner passed; remove only stale Streamlit aliases around it. |
| `check_function_quality.py` | Quality | UPDATE | Add missing “When to use” contract; retain specialist use. |
| `check_codex_git_workflow.py` | Quality | KEEP (NEW) | Prevents retired lifecycle wrappers/hooks from returning and validates the canonical boundary. |
| `check_git_script_budget.py` | Quality | RETIRED | Wrapper line-budget control was replaced by the Codex-native boundary guard. |
| `check_governance.py` | Quality | KEEP | Canonical governance check passed. |
| `check_instruction_drift.py` | Quality | KEEP | Canonical drift check passed. |
| `check_links.py` | Docs | KEEP | Canonical link check passed. |
| `check_new_element_completeness.py` | Quality | UPDATE | Add missing “When to use” contract; retain specialist use. |
| `check_next_session_brief_length.py` | Quality | KEEP | Canonical check passed. |
| `check_not_main.sh` | Git | REVIEW | Manual-only guard duplicated in active Git wrappers. |
| `check_openapi_drift.py` | CI | REVIEW | Overlaps snapshot checker; retain only with documented exact-deep nightly distinction. |
| `check_openapi_snapshot.py` | Quality | REVIEW | Overlaps drift checker; retain only with documented PR-summary distinction. |
| `check_python_version.py` | Quality | KEEP | Canonical check passed. |
| `check_repo_hygiene.py` | Quality | KEEP | Canonical check passed. |
| `check_root_file_count.sh` | Quality | UPDATE | Printed remediation uses forbidden raw `git mv`. |
| `check_scripts_index.py` | Quality | UPDATE | Does not validate category integrity, active missing targets, help, or behavior. |
| `check_tasks_format.py` | Quality | KEEP | Canonical check passed. |
| `check_token_efficiency.py` | Agent Infrastructure | KEEP | Policy check passed. |
| `check_type_annotations.py` | Quality | UPDATE | Implementation scans Python core, but title/help still say Streamlit. |
| `check_unfinished_merge.sh` | Git | KEEP | Small active guard; canonical check passed. |
| `check_version_consistency.sh` | Quality | UPDATE | Still reports optional missing VBA version after product removal. |
| `check_wip_limits.sh` | Quality | REVIEW | Manual-only and likely overlaps `check_tasks_format.py`/`check_governance.py`. |
| `ci_local.sh` | Git | UPDATE | Installs/builds in place, uses `python3`, and duplicates the canonical gate without preview. |
| `cleanup_stale_branches.py` | Infrastructure | KEEP | Default is dry review; deletion remains explicit. |
| `collect_diagnostics.py` | Infrastructure | KEEP | Purpose is distinct; retain with explicit output expectations. |
| `collect_metrics.sh` | Infrastructure | REVIEW | Manual-only metrics writer; prove a scheduled/report consumer. |
| `config_precedence.py` | Infrastructure | UPDATE | Registry says WorkspaceWrite for read-only audit/list operations. |
| `create_doc.py` | Docs | KEEP | Explicit creation tool with clear target; retain. |
| `create_task_pr.sh` | Git | RETIRED | PR creation/update moved to Codex and the connected GitHub integration. |
| `create_test_scaffold.py` | Testing | KEEP | Explicit generator with required target; retain. |
| `diagnose_ci.py` | Quality | UPDATE | Split read-only diagnosis permission from explicit `--fix`. |
| `discover_api_signatures.py` | Discovery | KEEP | Focused lookup and tests passed. |
| `dxf_render.py` | Infrastructure | KEEP | Distinct product-support utility; retain. |
| `evolve.py` | Evolution | UPDATE | Document which report/review modes write evidence; make dry-run side effects explicit. |
| `export_paper_data.py` | Infrastructure | REVIEW | Research-only exporter with no active caller; move to research tooling or archive. |
| `external_cli_test.py` | Testing | UPDATE | Document isolated temp behavior/cleanup and correct permission semantics. |
| `find_automation.py` | Discovery | UPDATE | Stale counts; beam smoke fails; legacy categories contain dead entries. |
| `finish_task_pr.sh` | Git | RETIRED | Removed automatic merge/clean/reset/delete behavior. |
| `fix_broken_links.py` | Docs | REVIEW | One-time removed-product cleanup; archive after remaining cleanup is complete. |
| `generate_all_indexes.sh` | Generation | KEEP | Canonical explicit generator; retain. |
| `generate_api_manifest.py` | Discovery | KEEP | Check/generate modes are explicit and canonical. |
| `generate_client_sdks.py` | Generation | KEEP | Explicit generator; retain. |
| `generate_docs_index.py` | Generation | KEEP | Preview/write split is clear; retain. |
| `generate_enhanced_index.py` | Generation | UPDATE | Writes indexes but registry labels it ReadOnly; align permission and preview semantics. |
| `generate_error_docs.py` | Generation | KEEP | Check/generate role is distinct; retain. |
| `governance_health_score.py` | Quality | REVIEW | Overlaps `project_health.py` and uses fallback metrics; define one canonical score. |
| `install_git_hooks.sh` | Git | RETIRED | Custom `core.hooksPath` enforcement was removed locally and globally. |
| `launch_stack.sh` | Infrastructure | KEEP | Canonical dev launcher; retain and keep listener-only cleanup evidence. |
| `migrate_python_module.py` | Migration | KEEP | Dry-run is tested; retain. |
| `migrate_react_component.py` | Migration | KEEP | Dry-run is tested; retain. |
| `model_picker.py` | Agent Infrastructure | KEEP | Advisory-only behavior and focused tests passed. |
| `parity_dashboard.py` | Quality | UPDATE | Add missing “When to use” contract; retain cross-stack evidence role. |
| `pipeline_state.py` | Infrastructure | UPDATE | State-changing commands are labeled ReadOnly in registry. |
| `pre_commit_check.sh` | Git | ARCHIVE CANDIDATE | Manual-only duplicate of installed pre-commit and canonical quick checks. |
| `preflight.py` | Session | UPDATE | Add `--help` and “When to use” contract. |
| `project_health.py` | Governance | UPDATE | Preserve canonical role; make no-write versus `--fix` permissions explicit. |
| `prompt_router.py` | Infrastructure | UPDATE | Registry labels normal read-only routing as WorkspaceWrite. |
| `recover_git_state.sh` | Git | RETIRED | Unclear Git state now stops for Codex inspection; no automated destructive recovery. |
| `release.py` | Release | KEEP | Canonical release CLI and focused tests passed; publishing still requires approval. |
| `repo_health_check.sh` | Governance | REVIEW | Manual disk/file diagnostic overlaps health and diagnostics tools. |
| `safe_file_delete.py` | Docs | KEEP | Explicit dry-run and backup behavior; retain, then repair callers that bypass it. |
| `safe_file_move.py` | Docs | KEEP | Tested dry-run and link-aware behavior; retain. |
| `safe_push.sh` | Git | RETIRED | Removed automatic checkout/stash/drop/rebase behavior. |
| `session.py` | Session | KEEP | Canonical session CLI and focused tests passed. |
| `session_store.py` | Infrastructure | UPDATE | State-changing `new`/`end` commands are labeled ReadOnly. |
| `should_use_pr.sh` | Git | RETIRED | Codex applies the documented PR policy from actual task scope. |
| `skill_tiers.py` | Infrastructure | KEEP | Canonical validation passed. |
| `sync_numbers.py` | Session | KEEP | Preview versus `--fix` is explicit; retain. |
| `test_api_parity.py` | Testing | UPDATE | Current parity is useful; remove stale Streamlit/VBA framing and alias. |
| `test_changed.py` | Testing | UPDATE | Add help/“When to use” contract and keep root-stable pytest paths. |
| `test_cli_smoke.py` | Testing | UPDATE | 12/13 pass; beam lookup fails and suite is absent from canonical gates. |
| `test_import_pipeline.py` | Testing | UPDATE | Add help and explicit live-server prerequisite; retain as maintained E2E path. |
| `test_sample_endpoint.py` | Testing | ARCHIVE CANDIDATE | Standalone subset of `test_import_pipeline.py`; no active caller/help. |
| `tool_permissions.py` | Infrastructure | UPDATE | Audit does not compare permissions with actual script side effects. |
| `tool_registry.py` | Infrastructure | UPDATE | Exposes temp/stale aliases and behavior-inaccurate permissions. |
| `update_test_stats.py` | Testing | KEEP | Report versus write modes are explicit; retain. |
| `validate_api_contracts.py` | Quality | KEEP | Canonical contract check passed. |
| `validate_git_state.sh` | Git | KEEP | Canonical read-only validation passed. |
| `validate_imports.py` | Quality | KEEP | Canonical import validation passed. |
| `validate_schema_snapshots.py` | Quality | KEEP | Canonical snapshot validation passed. |
| `validate_script_refs.py` | Quality | UPDATE | Only checks archived names; misses five active references to nonexistent scripts. |
| `watch_tests.sh` | Testing | UPDATE | Uses bare `pytest`/ambiguous default path and legacy Streamlit message; `fswatch` is absent locally. |

## Extended control-surface disposition

### Root/configuration entrypoints

| Item | Disposition | Evidence and next action |
|---|---|---|
| `run.sh` | UPDATE | Remove broken `test --vba` branch, keep help aligned, and add target-existence validation. |
| `.pre-commit-config.yaml` | UPDATE | Remove dead Streamlit hooks and their missing targets; retain current React/FastAPI/Python hooks. |
| `scripts/automation-map.json` | UPDATE | Remove stale categories/aliases/temp tool and align permissions/deprecation metadata. |
| `scripts/index.json` / `index.md` | KEEP/REGENERATE | Physical inventory is truthful now; regenerate only after approved script changes. |
| `scripts/README.md` | UPDATE | Replace stale PR/deprecation guidance and make help/dry-run claims match reality. |

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
| `scripts/_lib/agent_data.py` | UPDATE with agent evidence/no-write fixes |
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

1. Remove the five missing-script entrypoints from `run.sh` and pre-commit.
2. **Completed:** replace the vacuous API lane with the live React/OpenAPI contract check.
3. Extend target/category/smoke validation so the remaining defects cannot return.
4. Run focused checks, `./run.sh check --quick`, and inspect the live `PR Gate`.

### Packet C2 — Git data-preservation repair

**Completed by retirement:** the wrapper scripts, their direct dependencies,
custom enforcement hooks, and dormant pre/post-commit modules were removed.
Codex now owns ordinary scoped Git/GitHub work, while merge, branch deletion,
issue closure, release, and history rewriting retain explicit approval gates.

### Packet C3 — Registry and agent truth

1. Make the dynamic 16-agent registry the source for context and permission
   discovery.
2. Fail closed on missing/stale agent evidence.
3. Add explicit no-write modes to drift/trend/report commands.
4. Normalize operation-level permissions and remove temp/removed aliases.
5. Repair the CLI smoke case and make it part of repository validation.

### Packet C4 — Archive/consolidate the proven candidates

Start with only these three:

```text
scripts/_tmp_add_groups.py
scripts/pre_commit_check.sh
scripts/test_sample_endpoint.py
```

For each item:

```bash
rg -n "candidate_name|candidate_path" run.sh .github .pre-commit-config.yaml scripts docs AGENTS.md
.venv/bin/python scripts/safe_file_delete.py --dry-run scripts/candidate
```

Do not execute deletion until all live references are updated, the parent
accepts the replacement, and the preview is clean. After deletion, regenerate
only `scripts/index.json`, `scripts/index.md`, and the automation map surfaces
that actually changed. Then re-run the focused smoke/integrity tests and one
canonical gate.

### Packet C5 — Low-priority CLI/documentation normalization

Repair help/“When to use”/root-stable command examples in one surgical pass.
Do not mass-rewrite working scripts or split large files solely to improve
counts. Reassess the 13 review items only after C1-C4 establish truthful usage
and caller data.

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
.venv/bin/python scripts/check_scripts_index.py --json
.venv/bin/python scripts/validate_script_refs.py --fix
bash -n <each active shell script and hook>
AST parse <each active Python script and support module>
safe --help probe <each script with a recognizable help path>
.venv/bin/python scripts/test_cli_smoke.py --json
./run.sh check
.venv/bin/pytest -q <focused script/infrastructure test files>
./run.sh efficiency check
.venv/bin/python scripts/skill_tiers.py validate
gh pr checks 691
gh run list --workflow <each retained workflow> --limit 3
```

Current live PR evidence:

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
- Live-server scripts such as `test_import_pipeline.py` and
  `test_sample_endpoint.py` were inspected rather than executed because this
  audit did not start/alter the development stack.
- Migration, Git, file-operation, release, auto-fix, and archive modes were not
  executed.
- `agent_drift_detector.py` and `agent_trends.py` unexpectedly wrote ignored
  local evidence files during their default analysis modes. They did not change
  the tracked worktree; the side effect is retained as a finding rather than
  deleted.
- `./run.sh session end --agent orchestrator` completed its read-only checks but
  returned exit 1 because three documentation paths were uncommitted: this audit
  report plus two out-of-scope planning changes. Its handoff, link, session-log,
  task-archive, and governance checks all passed. No `--fix` mode was run.
- **TERMINAL ISSUE:** an early `awk` inventory expression failed with a quoting
  error -> simpler `git ls-files`, Perl, and Python path-based counts produced
  the reconciled 113-script inventory.

## Handoff

The next session should start at Packet C1, not with archiving. Preserve this
report as the decision ledger, refresh caller/live-run evidence immediately
before edits, and update each row only when a focused change has been verified.
Do not merge PR #691, publish v0.21.7, close historical issues, or delete remote
branches as part of the script-maintenance packets without separate owner
approval.
