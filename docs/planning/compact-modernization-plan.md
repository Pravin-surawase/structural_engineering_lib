---
owner: Main Agent
status: ready-after-pr-676
last_updated: 2026-08-09
doc_type: implementation-plan
task: MAINT-008
title: MAINT-008 Compact Project Modernization Plan
---

# MAINT-008 — Compact Project Modernization Plan

## 1. Outcome

Modernize the repository's CI, maintenance controls, and agent-facing workflow without changing the structural-engineering product outcome.

The finished repository must have:

- one truthful required PR check that runs whenever a main-process input changes;
- a small, understandable workflow set with no duplicate PR fan-out;
- one scheduled full-verification lane and one separately approved release lane;
- no active commands or hooks that point to removed applications or scripts;
- a compact, discoverable instruction path that a lower-cost agent can follow safely;
- the same proven import, design, detailing, API, UI, export, and package results as the baseline.

This is a control-plane modernization. It is not a product rewrite.

## 2. Main-process contract

Every decision in this plan is evaluated against this process:

```text
ETABS/CSV input
    -> GenericCSVAdapter and import API
    -> beam design and detailing
    -> BeamDesignResponse over REST/WebSocket
    -> React/R3F editor and dashboard
    -> BBS/DXF/HTML/PDF/BOQ exports
    -> clean wheel and approved release
```

For every proposed finding or change, ask:

> Would fixing this change the outcome, reliability, or truthful verification of this main process?

If the answer is no, do not include it in MAINT-008. Preserve it as a follow-up only when losing the concern would create real future work.

## 3. Proven baseline that must not regress

The current maintenance branch has already produced the following accepted evidence:

| Evidence | Baseline |
|---|---:|
| Imported/designed beams | 153 / 153 passing |
| Reinforcement steel | 2,663.4 kg |
| Concrete | 114.8 m3 |
| Quick gate | 9 / 9 |
| Full gate | 29 / 29 |
| Audit | 22 / 22 |
| Health | 100 |
| Parity | 96 |
| Release-preflight Python tests | 5,159 |
| Release-preflight FastAPI tests | 336 |
| Release-preflight React tests | 146 |
| Clean-wheel Python tests | 5,120 |
| Docker Python tests | 5,158 |

Record the exact baseline commit at MAINT-008 start. Closeout compares against that commit, not against remembered numbers alone.

## 4. Confirmed current-state problems

These are the only starting problems authorized by this plan:

1. The repository has 17 GitHub Actions workflow files and a single PR push can create roughly 10 workflows and 21 checks.
2. The active main-branch ruleset requires `Quick Validation (Python 3.11 only)`, but that check can skip when files that affect the main process change. A skipped required check is not truthful protection.
3. Nightly QA has created 129 open failure issues. Automated issue creation is producing noise rather than an actionable verification signal.
4. `governance-health.yml` calls `.venv/bin/python` in GitHub Actions even though that environment does not create a repository `.venv`.
5. Active pre-commit and command surfaces still contain references to removed Streamlit and VBA paths.
6. The repository contains a large agent, script, and documentation surface. It must be made easier to enter and navigate, but historical evidence and ETABS reference material must not be deleted merely to reduce file count.
7. The repository-level Codex configuration previously forced a parent model. That override has been removed; user-selected model and reasoning settings are now authoritative.

## 5. Non-goals and protected areas

The following are outside MAINT-008 unless a change is strictly required to keep the main process working:

- changing IS 456 formulas, coefficients, units, source values, or engineering assumptions;
- changing public calculation results or benchmark truth;
- adding product features, endpoints, visualizations, exporters, or structural elements;
- redesigning the React interface;
- increasing test coverage, adding falsification cases, or adding new tests during review;
- generic security hardening, concurrency hardening, comment cleanup, style cleanup, or speculative edge-case handling;
- rewriting all custom agents, prompts, or skills;
- deleting vendor ETABS reference files or historical release evidence;
- closing existing GitHub issues, merging a PR, publishing a package, creating a release, or changing a GitHub ruleset without the required owner approval;
- changing the user's global or project model choice again.

Protected calculation paths:

```text
Python/structural_lib/core/
Python/structural_lib/codes/is456/
```

If a packet unexpectedly needs to edit either protected path, stop the packet and return to the parent. Do not make the edit.

## 6. Execution rules

1. Work in the order defined in section 9. Do not run packets B or C before packet A has a visible, passing `PR Gate`.
2. One parent task owns integration. Use at most two bounded workers, and only on independent packets.
3. A worker receives only its packet, the current branch/commit, and the minimum referenced files. Do not send the full session history.
4. Inspect with folder indexes and targeted `rg` before opening large files.
5. Fix confirmed root causes. Do not mask failures with `continue-on-error`, `|| true`, broad exclusions, or skipped jobs.
6. Use existing tests. Do not add tests as part of this maintenance review.
7. Run a targeted check while iterating, `./run.sh check --quick` once before each commit, the PR gate after push, and the full gate once at closeout.
8. Use `./scripts/ai_commit.sh` or `./run.sh commit` for every commit. Never use manual Git commit/push commands.
9. Use `scripts/safe_file_delete.py` and `scripts/safe_file_move.py` for repository deletions or moves. Always inspect a dry run first.
10. Never bypass hooks, required checks, or safe-push controls.
11. Any terminal failure must be returned as `WARNING TERMINAL ISSUE: what failed -> what worked instead`.
12. A worker does not merge, release, close issues, delete remote branches, or change GitHub repository settings.

## 7. Minimum gate ladder

| Stage | Required verification | When |
|---|---|---|
| Inspect | Targeted read-only commands and existing focused check | During implementation |
| Commit | `./run.sh check --quick` | Once before each packet commit |
| PR | Stable aggregate `PR Gate` | After each pushed packet |
| Closeout | `./run.sh check`, `./run.sh audit`, `./run.sh health`, `./run.sh efficiency check` | Once after all packets |
| Main flow | Import pipeline plus UI/export evidence | Once after all packets |
| Release | `./run.sh release preflight 0.21.7` and Docker preflight | Only before an approved release |

Do not repeat the full suite inside every worker packet. A failed narrow check must be diagnosed before escalating to a wider gate.

## 8. Target end state

### 8.1 GitHub Actions

Target no more than four active workflow files:

| Workflow | Trigger | Responsibility |
|---|---|---|
| `fast-checks.yml` | Pull requests and relevant pushes | One truthful PR validation workflow with stable aggregate `PR Gate` |
| `nightly.yml` | Weekly and manual | Full existing tests, dependency audit, clean-wheel/CLI verification; no issue creation |
| `publish.yml` | Approved tag or manual release | Package build, validation, TestPyPI/PyPI/GitHub release flow |
| `deploy-docs.yml` | Relevant main changes or manual | Documentation build and publication |

The final number may exceed four only if the parent records a main-process reason and owner accepts it. Convenience, historical ownership, or generic hardening is not sufficient.

### 8.2 Required branch check

The final main-branch ruleset requires exactly one stable aggregate check named `PR Gate` for this modernization.

`PR Gate` must:

- always be created for a pull request;
- depend on every essential job in `fast-checks.yml`;
- fail if an essential dependency fails or is cancelled;
- allow an intentionally non-applicable component job to report skipped only when another job still validates the changed repository surface;
- use `if: always()` so it reports a conclusion even when a dependency fails;
- never become green merely because all useful jobs were filtered out.

The repository ruleset is changed only after `PR Gate` has appeared and passed on the PR. Preserve the previous ruleset JSON before mutation so it can be restored.

### 8.3 Agent and command entry path

A new agent should need only this sequence:

1. `AGENTS.md`
2. `docs/TASKS.md`
3. `docs/planning/next-session-brief.md`
4. this plan or the active task-specific plan
5. the specific folder index and files named in its packet

No worker should need to scan `SESSION_LOG.md`, all agent definitions, all prompts, or all archived scripts to begin a bounded task.

## 9. Dependency order

```text
Owner approves merge of PR #676
    -> Packet 0: establish MAINT-008 branch and baseline
        -> Packet A: create truthful PR Gate
            -> Owner approves main-ruleset switch
                -> Packet B: compact scheduled and release lanes
                    -> Packet C: compact supported local control surface
                        -> Packet D: integrated closeout
                            -> Owner separately approves merge
                                -> Owner separately approves release
```

Packets B and C may run in parallel only after packet A is complete and only if they do not edit the same files. Packet D is always performed by the parent.

## 10. Packet 0 — Parent/operations setup

**Owner:** parent/orchestrator or operations role only

**Start condition:** explicit owner approval to merge PR #676

**End condition:** a clean MAINT-008 task branch/PR with recorded baseline

### Objective

Finish the existing maintenance PR safely, then create a dedicated modernization branch so workflow changes are not mixed with the already-green recovery work.

### Steps

1. Run `./scripts/ai_commit.sh --status` and `./run.sh pr status`.
2. Confirm PR #676 is still green and its head is the expected commit.
3. Ask for explicit merge approval if it has not already been given.
4. Merge only through the repository's safe PR flow. Do not release.
5. Synchronize the local main branch using the repository workflow.
6. Create the MAINT-008 branch and PR:

   ```bash
   ./run.sh pr create MAINT-008 "Compact CI and maintenance control plane"
   ```

7. Record:

   ```bash
   git rev-parse HEAD
   git status --short
   find .github/workflows -maxdepth 1 -name '*.yml' -print | sort
   gh api repos/Pravin-surawase/structural_engineering_lib/rulesets
   ```

8. Save the ruleset ID, required-check name, workflow count, PR check count, and baseline commit in the MAINT-008 task note or PR description.

### Stop conditions

- PR #676 is not green.
- The checked-out commit does not match the remote PR head.
- The working tree contains unrelated changes.
- The safe PR workflow fails.

### Return format

```text
Packet: 0
Branch and PR:
Baseline commit:
PR #676 result:
Ruleset ID and current required check:
Workflow count:
Commands run:
Unexpected state:
Next packet authorized: yes/no
```

## 11. Packet A — Truthful PR gate

**Suggested worker:** Terra, normal implementation reasoning

**Files in scope:**

```text
.github/workflows/fast-checks.yml
.github/workflows/README.md
.github/workflows/auto-format.yml (pull_request trigger only)
.github/workflows/codeql.yml (pull_request trigger only)
.github/workflows/docker-build.yml (pull_request trigger only)
.github/workflows/git-workflow-tests.yml (pull_request trigger only)
.github/workflows/leading-indicator-alerts.yml (pull_request trigger only)
.github/workflows/link-check.yml (pull_request trigger only)
.github/workflows/performance.yml (pull_request trigger only)
.github/workflows/root-file-limit.yml (pull_request trigger only)
.github/workflows/security.yml (pull_request trigger only)
```

Other workflow files may have their `pull_request` triggers removed only after the aggregate gate appears and passes. Do not delete workflow files in this packet.

### Objective

Replace the skipped required check with one stable, truthful aggregate check named `PR Gate` while retaining the existing checks that protect the main process.

### Required design

1. `fast-checks.yml` must trigger for pull requests whenever any of these surfaces changes:

   ```text
   Python/**
   fastapi_app/**
   react_app/**
   scripts/**
   docs/**
   .github/workflows/**
   .codex/**
   AGENTS.md
   run.sh
   requirements*.txt
   pyproject.toml
   package-lock.json files
   pre-commit configuration
   ```

2. Keep jobs understandable by main-process layer:

   - Python/FastAPI validation;
   - React validation when React inputs change;
   - repository/docs/scripts policy validation;
   - aggregate `PR Gate`.

3. Reuse setup through YAML steps or a local composite action only if it measurably removes duplication. Do not introduce a new third-party action for cosmetic reuse.
4. Pin runtime versions to versions already supported by the repository.
5. Use dependency caching only where the official setup action already supports it.
6. The aggregate job uses `if: always()` and checks every essential `needs` result explicitly.
7. No essential validation step may use `continue-on-error` or `|| true`.
8. Do not rename `PR Gate` after the ruleset is switched to it.

### Implementation sequence

1. Read `fast-checks.yml`, `.github/workflows/README.md`, the current ruleset output, and the commands behind `./run.sh check --quick`.
2. Map every existing PR workflow check to one of:

   - retained in `fast-checks.yml` because it changes main-process confidence;
   - scheduled in packet B because it is valuable but too expensive for every PR;
   - parked because it does not change the main-process outcome.

3. Implement the consolidated jobs and `PR Gate`.
4. Validate YAML through the repository's existing pre-commit/check tooling.
5. Run `./run.sh check --quick`.
6. Commit with the safe wrapper and push.
7. Wait for the PR and confirm `PR Gate` exists, runs even when a component job is skipped, and fails if an essential job fails.
8. Update `.github/workflows/README.md` with the actual trigger and job names.
9. Only after step 7, remove `pull_request` triggers from superseded workflows. Leave their scheduled, push, or manual triggers unchanged for packet B.

### Acceptance criteria

- `PR Gate` appears on every pull request update.
- `PR Gate` depends on all essential jobs and cannot pass after an essential failure/cancellation.
- A backend change runs backend validation; a frontend change runs frontend validation; workflow or shared-control changes run repository validation.
- A docs-only change still receives a real validation result rather than an all-skipped green state.
- One push no longer creates duplicate PR validation workflows after superseded PR triggers are removed.
- Quick gate passes.
- No production code or tests are changed.

### Pitfalls to reject

- leaving the current path filter unchanged;
- making `PR Gate` depend on only the Python job;
- treating skipped and successful results as universally equivalent;
- removing old triggers before the new check is visible;
- changing the GitHub ruleset from the worker packet;
- adding new tests or refactoring application code.

### Rollback

If `PR Gate` does not appear or reports an incorrect conclusion, restore the prior PR triggers before ending the packet. Do not ask the owner to switch the ruleset.

### Worker return format

```text
Packet: A - Truthful PR gate
Baseline commit:
Files changed:
Root cause corrected:
Old check mapping: retained / scheduled / parked
Commands and results:
PR Gate URL and conclusion:
Superseded PR triggers removed:
Acceptance criteria: pass/fail per item
Protected paths changed: no
Follow-ups strictly outside scope:
Terminal issues:
Commit:
```

### Parent-only approval checkpoint

After independently inspecting the YAML and the live PR result, the parent presents the exact old and new required-check names to the owner. With explicit approval:

1. fetch and save the current ruleset JSON;
2. update ruleset `11390214` only if it is still the active main ruleset and still has the observed old check;
3. replace `Quick Validation (Python 3.11 only)` with `PR Gate`;
4. re-fetch and verify the resulting ruleset;
5. restore the saved ruleset if protection disappears or the required check is wrong.

## 12. Packet B — Scheduled verification and release lanes

**Suggested worker:** Terra, normal implementation reasoning

**Start condition:** packet A complete and `PR Gate` is live

**Files in scope:**

```text
.github/workflows/nightly.yml
.github/workflows/publish.yml
.github/workflows/deploy-docs.yml
.github/workflows/README.md
README.md
superseded .github/workflows/*.yml files approved by the parent
```

### Objective

Reduce 17 workflows to the smallest set that verifies, documents, and releases the main process without daily issue spam or duplicated PR gates.

### Scheduled lane requirements

Rewrite `nightly.yml` as weekly plus manual verification:

- default weekly job: supported Ubuntu/Python version, full existing Python/FastAPI/React checks, clean-wheel/CLI smoke, and existing dependency audits;
- optional cross-platform matrix: manual or release-preflight only, not every scheduled run;
- permissions default to `contents: read`;
- no `issues: write`, no issue creation, and no automated closing of existing issues;
- one clear workflow summary containing failing command/job names;
- no duplicate PR or ordinary push trigger.

The weekly lane catches drift. It is not a second PR gate.

### Release lane requirements

`publish.yml` remains the only package-release workflow:

- approved tag or explicit manual dispatch only;
- version and tag agreement must be validated before publishing;
- package build and install smoke must complete before upload;
- TestPyPI and production PyPI/GitHub Release stages remain visibly separated;
- environment approvals and secrets remain unchanged unless the owner explicitly approves a repository-settings change;
- a worker may validate the workflow and local preflight but may not publish.

### Documentation lane requirements

`deploy-docs.yml` remains only if the generated documentation is currently published and its failure changes the release/user outcome. Limit it to relevant main-branch changes and manual dispatch. It must not duplicate generic link or Python checks already owned elsewhere.

### Workflow disposition

The following workflows are candidates for removal after their essential function is mapped:

```text
auto-format.yml
codeql.yml
docker-build.yml
git-workflow-tests.yml
governance-health.yml
leading-indicator-alerts.yml
link-check.yml
performance.yml
python-tests.yml
root-file-limit.yml
sbom.yml
scorecard.yml
security.yml
```

Do not delete from this list blindly. For each file:

1. identify its main-process signal;
2. show where that signal now runs, or state why it is nonessential;
3. search README badges, docs, scripts, and rulesets for its workflow/check name;
4. run the safe-delete dry run;
5. let the parent approve the exact deletion list;
6. delete using the safe-delete script and update live references.

Example safe operation:

```bash
.venv/bin/python scripts/safe_file_delete.py --dry-run .github/workflows/example.yml
.venv/bin/python scripts/safe_file_delete.py .github/workflows/example.yml
```

### Existing failure handling

- Removing issue creation stops new Nightly QA spam.
- The 129 existing issues are not closed in this packet.
- `governance-health.yml` is not repaired as a standalone workflow unless its signal is proved essential. Move an essential command into the retained lane using the CI runtime's `python`, then remove the broken duplicate.
- The old removed `--fail-fast` problem must not be reintroduced.

### Acceptance criteria

- Four or fewer active workflow YAML files, unless an owner-approved main-process exception is documented.
- A normal PR creates only the consolidated PR workflow.
- Weekly/manual nightly runs without issue-write permission and creates no issue.
- Release workflow has no ordinary PR or push-to-main publishing path.
- All README badges and workflow documentation point to existing workflows/checks.
- Safe-delete reports no unhandled live references.
- `./run.sh check --quick` and live `PR Gate` pass.
- No release, merge, issue closure, or repository-setting change occurs.

### Pitfalls to reject

- deleting workflow files before mapping their only essential signal;
- keeping a workflow solely because it already exists;
- moving every old job into nightly and preserving the same redundancy;
- closing the 129 issues without owner approval;
- running a production publish as a test;
- weakening the release lane to compensate for a failing preflight.

### Worker return format

```text
Packet: B - Scheduled and release lanes
Baseline commit:
Files changed/deleted:
Workflow disposition table: file / signal / retained location or reason parked
Workflow count before/after:
Triggers after change:
Permissions after change:
Commands and results:
PR Gate URL and conclusion:
New issues created: 0 or explanation
Acceptance criteria: pass/fail per item
Protected paths changed: no
Owner approvals still required:
Terminal issues:
Commit:
```

## 13. Packet C — Compact supported local control surface

**Suggested worker:** Luna for inventory; Terra for edits

**Start condition:** packet A complete

**Files in scope:**

```text
run.sh
.pre-commit-config.yaml
scripts/automation-map.json
scripts/index.json
scripts/index.md
AGENTS.md
docs/planning/README.md
docs/planning/index.json
docs/planning/index.md
only confirmed orphan scripts approved by the parent
```

### Objective

Make active commands, hooks, automation lookup, and planning entrypoints describe only supported behavior. Preserve historical and vendor evidence while removing confirmed dead control paths.

### Required inventory method

For every candidate command, hook, or script:

1. find direct callers with targeted `rg` across `run.sh`, workflows, pre-commit, automation maps, package scripts, Python imports, and active docs;
2. identify whether it participates in the main process or current maintenance commands;
3. execute its help/dry-run/read-only path when one exists;
4. classify it as active, archive-only, or confirmed orphan;
5. change or delete it only if the classification is supported by evidence.

Confirmed starting candidates to investigate, not automatic deletions:

```text
scripts/_tmp_add_groups.py
scripts/batch_migrate_runner.py
scripts/test_sample_endpoint.py
```

### Required changes

1. Remove active Streamlit hooks or commands when their target tree does not exist.
2. Remove VBA test entrypoints when their target scripts do not exist.
3. Keep `run.sh` help aligned with commands that resolve to real implementations.
4. Keep `scripts/automation-map.json` and generated script indexes synchronized with supported automation.
5. Update `AGENTS.md` only where a command or model policy is confirmed stale. Do not rewrite agent philosophy.
6. Make the planning index expose this plan and the current next-session brief.
7. Preserve `docs/reference/vendor/etabs/`; exclude large reference/archive trees from routine agent discovery or generated indexes when possible instead of deleting them.
8. Do not mass-rewrite 16 agents, 14 skills, or 16 prompts. File one follow-up if common-instruction consolidation remains valuable after the active path is corrected.

### Safe-delete procedure

```bash
rg -n "candidate_name|candidate_path" run.sh .github .pre-commit-config.yaml scripts docs AGENTS.md
.venv/bin/python scripts/safe_file_delete.py --dry-run scripts/candidate.py
.venv/bin/python scripts/safe_file_delete.py scripts/candidate.py
```

If the dry run reports an unresolved reference, do not delete the file until the parent confirms whether the reference is active or historical.

### Acceptance criteria

- No active `run.sh` command or pre-commit hook points to a missing path.
- `./run.sh find` and tool discovery return current supported commands.
- Script indexes and automation-map validation pass with their new truthful counts.
- This plan is linked from the planning index, task board, and next-session brief.
- Large vendor/reference trees remain intact and are not required reading for a worker packet.
- Quick gate and `PR Gate` pass.
- No protected calculation file, application behavior, or test is changed.

### Pitfalls to reject

- using file age or name alone as orphan evidence;
- deleting archived evidence to improve repository statistics;
- running a broad generator that rewrites unrelated indexes without reviewing the diff;
- rewriting all agent definitions for consistency;
- adding a new automation framework to replace a few stale entries.

### Worker return format

```text
Packet: C - Compact local control surface
Baseline commit:
Files changed/deleted:
Inventory table: item / callers / classification / action
Missing-path references before/after:
Index and automation validation:
Commands and results:
PR Gate URL and conclusion:
Acceptance criteria: pass/fail per item
Protected paths changed: no
Follow-up bead proposed, if essential:
Terminal issues:
Commit:
```

## 14. Packet D — Parent integrated closeout

**Owner:** parent/orchestrator only

**Start condition:** packets A-C accepted independently

**End condition:** owner has a concise, evidence-backed merge decision

### 14.1 Independent review

For every worker change:

1. inspect the actual diff rather than accepting the summary;
2. verify no protected calculation path changed;
3. trace each deletion to its replacement or nonessential classification;
4. inspect workflow triggers, permissions, dependencies, and aggregate conclusions;
5. verify the worker ran only authorized commands;
6. reject adjacent cleanup even when it looks useful.

### 14.2 Structural diff guard

Run against the recorded baseline commit:

```bash
git diff --name-only BASELINE_COMMIT...HEAD -- \
  Python/structural_lib/core \
  Python/structural_lib/codes/is456
```

Expected output: empty.

### 14.3 One-time repository closeout

```bash
./run.sh check
./run.sh audit
./run.sh health
./run.sh efficiency check
```

All must pass or produce only an already-approved, documented exception.

### 14.4 Main-process verification

Start the supported stack and exercise the existing import pipeline:

```bash
./run.sh dev
./run.sh test import
```

Verify the existing primary user path:

- import the accepted ETABS/CSV sample;
- confirm 153/153 beam design success;
- confirm 2,663.4 kg steel and 114.8 m3 concrete;
- open the editor/dashboard and confirm the response renders;
- request the supported BBS/DXF/HTML/PDF/BOQ exports;
- confirm successful status and non-empty downloaded bytes;
- stop services with `./run.sh dev --kill-only`.

Do not change formulas or expected quantities to make this pass.

### 14.5 Release preflight

Only when preparing the already-planned v0.21.7 release:

```bash
./run.sh release preflight 0.21.7
./run.sh release preflight --docker
```

Preflight evidence authorizes a release decision; it does not authorize publishing. Obtain separate explicit owner approval before `./run.sh release run 0.21.7`.

### 14.6 Final live checks

- PR shows one passing `PR Gate` and no duplicate PR workflow fan-out.
- Main ruleset requires `PR Gate` and no longer requires the skipped old name.
- Weekly workflow can be manually dispatched and creates no issue.
- Publish workflow has not run unintentionally.
- Working tree is clean after the safe commit flow.

### Parent return format

```text
MAINT-008 closeout
Baseline -> final commit:
Main-process result and quantities:
Workflow count before -> after:
PR workflows/checks before -> after:
Required check before -> after:
Scheduled run result and issue count:
Quick/full/audit/health/efficiency results:
Release-preflight results, if run:
Protected calculation diff: empty/non-empty
Open owner decisions: merge / release / close historical issues
Known follow-ups outside scope:
Terminal issues:
Recommendation: merge / do not merge
```

## 15. Definition of done

MAINT-008 is complete only when all applicable statements are true:

- [ ] The main import/design/detailing/API/UI/export path produces the accepted baseline outcome.
- [ ] Protected calculation paths have no diff from the recorded baseline.
- [ ] One stable `PR Gate` appears for every PR update and is the required main-branch check.
- [ ] A normal PR launches one consolidated PR workflow, not the previous fan-out.
- [ ] Four or fewer active workflows remain, or an owner-approved main-process exception is documented.
- [ ] Nightly is weekly/manual, passes, has no issue-write permission, and creates no issue.
- [ ] Release publishing remains separate and owner-approved.
- [ ] No active command, hook, automation entry, badge, or planning link points to a removed path/workflow.
- [ ] User-selected Codex model/reasoning settings remain authoritative.
- [ ] Quick, full, audit, health, efficiency, and live PR gates pass at their specified stage.
- [ ] No tests, formulas, product features, or generic hardening were added to expand the maintenance scope.
- [ ] The task board and next-session brief contain the final evidence and next owner decision.

## 16. Follow-up parking lot

These items are explicitly not required for MAINT-008 completion:

- bulk review and owner-approved closure of the 129 historical Nightly QA issues;
- broader consolidation of the 16 agent definitions, 14 skills, and 16 prompts;
- archival policy for large historical documentation;
- optional CodeQL, Scorecard, SBOM, performance, or security automation that is not required for the main process;
- new test coverage or new falsification campaigns;
- new product capabilities or engineering-code certification work.

Create a follow-up task only if it has a named owner, a concrete outcome, and evidence that it should survive. Do not create generic backlog noise.

## 17. Copy-ready assignment preamble

Prepend this block to any worker packet:

```text
You are executing one bounded packet from MAINT-008. Work only in the named files.
Read AGENTS.md, docs/TASKS.md, docs/planning/next-session-brief.md, and the assigned
packet in docs/planning/compact-modernization-plan.md. Start with targeted rg and
folder indexes. Fix confirmed root causes only. Do not change structural formulas,
tests, product behavior, GitHub settings, releases, issues, or protected paths.
Do not add adjacent improvements. Run the packet's narrow checks and one quick gate.
Commit only through ./scripts/ai_commit.sh or ./run.sh commit. Return exactly the
packet's requested report, including commands, results, commit, and any terminal issue.
If scope or evidence is unclear, stop and return the exact blocker instead of guessing.
```
