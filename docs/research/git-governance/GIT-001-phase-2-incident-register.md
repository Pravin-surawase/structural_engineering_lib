---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 2
---

# GIT-001 Phase 2 — Project Incident Register

## Purpose and authority boundary

This register traces confirmed Git, worktree, automation, CI, release, and
recovery failures from this repository. It is forensic evidence for the later
gap analysis and operating-model design. It does **not** change canonical Git
policy, GitHub settings, hooks, scripts, cleanup state, release state, or branch
ownership.

The current normative workflow remains
[`git-workflow-single-source.md`](../../git-automation/git-workflow-single-source.md).
Historical commands are evidence only; where an old record recommends reset,
stash, rebase, force-push, or automatic cleanup, the current fail-closed policy
takes precedence.

## Method and evidence standard

An incident is admitted only when a maintained or preserved repository record
identifies a visible symptom and main-process impact. Each entry uses the Phase
1 chain:

`Symptom -> Impact -> Confirmed root cause -> Unsafe reaction -> Preventive control -> Recovery -> Verification`.

If the evidence does not prove why the original state arose, the cause is
marked `unconfirmed`; the register does not turn a plausible explanation into a
fact. A near miss is included only when work or release evidence was already at
risk and a preservation hold prevented loss.

## Incident ledger

| ID | Failure family | Main-process outcome | Root-cause status | Current disposition |
|---|---|---|---|---|
| GIT-I01 | Diverged push reported as ready | Push failed; agent used unsafe history operations | Confirmed | Old lifecycle wrappers retired; current policy fails closed |
| GIT-I02 | Dirty long-lived lane met a newer main | Thirteen paths and shared records required controlled recovery | Partly confirmed | Checkpoint, normal merge, semantic reconciliation, full gates |
| GIT-I03 | Stale PR mixed useful and unrelated work | Whole-branch integration was unsafe and conflicted | Confirmed | Selected behavior rebuilt on a fresh lane; historical ref retained |
| GIT-I04 | Linked worktree imported another lane | Green tests initially proved the wrong source tree | Confirmed | Worktree-bound launcher and import-identity proof |
| GIT-I05 | Global generator rewrote unrelated projections | Review scope was polluted by 23-28 unrelated index changes | Confirmed | Unrelated output restored; owned folders regenerated narrowly |
| GIT-I06 | Wall-clock performance lived in required CI | Three unrelated PRs were blocked by hosted-runner variance | Confirmed | Deterministic assertions retained; performance moved to scheduled evidence |
| GIT-I07 | Local release preflight and CI tested different surfaces | Candidate PR failed only after publication-bound work reached CI | Confirmed | FastAPI added to local/Docker preflight; version truth made dynamic |
| GIT-I08 | Dirty or unknown lane could be marked trusted | Mutation controls could proceed from unsafe state | Confirmed | Exact clean sentinel, known branch, and Git return codes required |
| GIT-I09 | Squash integration looked unmerged by ancestry | Cleanup/synchronization could repeat or discard integrated work | Confirmed | PR, patch/tree, reachability, tests, and retained refs used together |
| GIT-I10 | Documented intake/help behavior did not match the lane | Startup stopped; help unexpectedly wrote and then failed | Confirmed | Read-only task brief and non-writing, lane-bound index help rebuilt |

## GIT-I01 — diverged push falsely reported as ready

- **Symptom:** the retired `safe_push.sh` printed `Push ready` for a diverged
  `task/TASK-640` branch; the subsequent push was rejected as non-fast-forward.
- **Impact:** the error offered the same failing push path, after which the agent
  attempted `git pull --rebase`, `git rebase --skip`, and
  `git push --force-with-lease` before a PR was finally created.
- **Confirmed root cause:** the wrapper's divergence branch fell through to a
  literal success message instead of classifying independent local and remote
  commits. The automation therefore asserted safety it had not proved.
- **Unsafe reaction:** skipping a conflicting commit and rewriting a shared ref
  could silently drop or replace work.
- **Preventive control:** normal Git/GitHub lifecycle mutation now belongs to
  Codex; repository scripts may inspect state but may not stage, synchronize,
  push, merge, rewrite, or recover automatically.
- **Recovery and verification:** TASK-900-series controls were later completed,
  then the entire wrapper/enforcement layer was retired. The current
  `check_codex_git_workflow.py` rejects reintroduction of the retired paths.
- **Evidence:** [`git-workflow-hardening-plan.md`](../../_archive/planning/git-workflow-hardening-plan.md)
  lines 17-68 and the current canonical workflow.

## GIT-I02 — dirty Spark lane and shared-surface collision

- **Symptom:** the Spark program lane contained 13 uncommitted planning/control
  paths while current `main` had advanced; a controlled merge later produced
  seven conflicts in task, handoff, session, and generated-index surfaces.
- **Impact:** unsaved work, newer main truth, and single-writer records could not
  be reconciled safely by checkout, rebase, reset, stash, or automatic conflict
  selection.
- **Confirmed root cause:** both histories changed the same shared ledgers and
  projections, and the stale lane predated the current `task brief` command.
  Why the original session ended with all 13 paths uncommitted is
  **unconfirmed** by the durable record.
- **Unsafe reaction avoided:** no rebase, reset, stash, force operation, or
  history rewrite was used; conflicts were not resolved by choosing one side
  wholesale.
- **Preventive control:** classify ownership before staging, checkpoint all
  intended paths, name shared/generated surfaces as single-writer, and
  synchronize with a two-parent merge only after preservation.
- **Recovery and verification:** checkpoint `47fce48e` preserved all 13 paths;
  merge `f0314f3e` integrated `origin/main`; shared documents were reconciled
  semantically and only affected indexes regenerated. Focused tests passed 18,
  quick gate 10/10, and full gate 30/30.
- **Evidence:** `docs/SESSION_LOG.md`, session `SPARK-001 Phase 2 Recovery and
  Integration`.

## GIT-I03 — stale mixed PR could not be integrated as a unit

- **Symptom:** PR #723 was 53 commits behind `main`, conflicted with current
  shared surfaces, and combined useful intake/runtime changes with broad policy,
  generated files, and unrelated work.
- **Impact:** merging or cherry-picking the old PR as a unit would have restored
  superseded policy and overwritten current shared truth.
- **Confirmed root cause:** the PR evolved across several unrelated work streams
  without a stable ownership boundary or current-base integration checkpoint.
- **Unsafe reaction avoided:** the three commits were not merged, rebased, or
  cherry-picked as a unit, and the historical lane was not deleted before
  replacement proof existed.
- **Preventive control:** stale mixed work is evidence, not an implementation
  unit. Start from current `main`, recover named outcomes only, and retain the
  old ref until exact-head replacement CI and integration prove supersession.
- **Recovery and verification:** `task brief` plus lane-bound index help/runtime
  behavior were rebuilt through PR #736; required CI passed at unchanged head
  `aec9fbb2`, integrated as `30ec598d`, and the remote historical head
  `75d66681` remains available for audit.
- **Evidence:** [Packet 7A](GIT-001-phase-7A-preservation-workflow-recovery.md)
  and `docs/SESSION_LOG.md`, session `GIT-001 Preservation and Workflow Recovery`.

## GIT-I04 — linked-worktree source identity leaked

- **Symptom:** the first focused Column PMM test run in the preserved worktree
  imported `structural_lib` from the primary checkout.
- **Impact:** nine green tests initially described another lane, so they could
  not validate the preserved PMM commit or support a recovery decision.
- **Confirmed root cause:** the old lane predated the maintained worktree-bound
  runtime, while the shared editable environment could resolve the primary
  checkout even when the executable itself was usable.
- **Unsafe reaction avoided:** the green result was rejected rather than cited;
  no calculation code was integrated from that evidence.
- **Preventive control:** bind source to the invoking worktree and assert the
  resolved package path, not merely the Python executable path.
- **Recovery and verification:** `PYTHONPATH="$PWD/Python"` produced nine passing
  focused tests against the preserved lane; current
  `python_runtime.sh --diagnose` reports interpreter, repository, module path,
  and `source_bound=true`.
- **Evidence:** `docs/SESSION_LOG.md`, session `GIT-001 Preservation and Workflow
  Recovery`, and [the PMM recovery case study](../../git-automation/git-recovery-case-study-column-pmm.md).

## GIT-I05 — global index generation polluted bounded changes

- **Symptom:** a planning-only Spark session's global index command rewrote 28
  unrelated indexes; later Phase 1 closeout changed 23 unrelated indexes.
- **Impact:** unrelated projection drift obscured the owned diff and increased
  conflict and review risk on shared generated surfaces.
- **Confirmed root cause:** `./run.sh generate indexes` intentionally processes
  every maintained folder and can surface existing drift outside the task's
  ownership boundary.
- **Unsafe reaction avoided:** broad generated churn was not accepted merely
  because it came from the canonical generator.
- **Preventive control:** preview generated scope, distinguish handwritten and
  generated ownership, restore unrelated output to the exact baseline, and run
  folder-targeted generation child-first for owned folders.
- **Recovery and verification:** unrelated changes were inspected and restored;
  only required planning/parent or task-owned governance indexes remained.
  Targeted drift checks, `git diff --check`, and the quick/full gates passed.
- **Evidence:** `docs/SESSION_LOG.md`, sessions `GPT-5.3-Codex-Spark Work
  Program` and `GIT-001 Phase 1 Completion`.

## GIT-I06 — nondeterministic timing blocked unrelated PRs

- **Symptom:** PRs #724, #725, and #726 failed the same FastAPI load assertion at
  158.4 ms, 206.9 ms, and 161.5 ms against an absolute 150.0 ms threshold.
- **Impact:** three feature branches whose diffs did not touch the load test were
  merge-blocked by hosted-runner timing rather than a product correctness
  regression.
- **Confirmed root cause:** a duplicate wall-clock average-latency assertion was
  part of the ordinary required PR suite, where shared-runner scheduling is not
  a stable correctness input.
- **Unsafe reaction avoided:** thresholds were not weakened per feature branch
  and required checks were not bypassed.
- **Preventive control:** required CI owns deterministic success/error outcomes;
  performance measurement belongs to a scheduled/manual benchmark lane with a
  durable artifact.
- **Recovery and verification:** the latency-only test was removed while
  deterministic concurrent behavior remained. The focused FastAPI run passed
  376 with 6 deselected, the dedicated load file passed 8, and benchmark JSON
  generation/overwrite was verified before the blocked feature PRs advanced.
- **Evidence:** `docs/SESSION_LOG.md`, sessions `Recent-Work Maintenance and
  Cleaning` and `FastAPI Load-Lane Fix`.

## GIT-I07 — release preflight and CI surface skew

- **Symptom:** PR #732's FastAPI job failed because a BOQ test hard-coded public
  version `0.23.0` while the candidate correctly reported `0.23.1a1`; prior
  local release preflight had passed.
- **Impact:** a release-candidate contradiction reached remote required CI after
  expensive local artifact preparation, and the local receipt overstated parity
  with the publication gate.
- **Confirmed root cause:** local release preflight exercised Python and React
  but omitted the maintained FastAPI suite; the failing test encoded historical
  version text instead of the maintained application version surface.
- **Unsafe reaction avoided:** required CI was not bypassed and the candidate
  artifact was not published from the failing head.
- **Preventive control:** local, Docker, and CI release surfaces must be mapped
  explicitly; dynamic cross-surface assertions must derive from one maintained
  version authority.
- **Recovery and verification:** the BOQ assertion now uses
  `fastapi_app.__version__`; local and Docker preflight include FastAPI. The
  exact failed test and all 413 FastAPI tests passed, followed by quick/full and
  clean-artifact gates without changing the wheel/sdist hashes.
- **Evidence:** `docs/SESSION_LOG.md`, session `0.23.1a1 Candidate Verification
  Root-Cause Repair`, and GitHub run `31463676435`.

## GIT-I08 — session trust accepted dirty or unknown state

- **Symptom:** session start counted a dirty tree but still wrote trusted state;
  an initial repair could also accept a clean tree when branch detection
  returned the `unknown` detached/error sentinel.
- **Impact:** downstream mutation controls could proceed as if lane ownership and
  recoverability were proved when the branch or working tree was unsafe.
- **Confirmed root cause:** trust logic searched formatted summary words such as
  `modified` and `untracked`, but the underlying function returned a count; it
  also treated a non-main sentinel as a known feature branch.
- **Unsafe reaction avoided:** independent review rejected the first repair
  before release closeout relied on it.
- **Preventive control:** trust is an allowlist: exact clean sentinel, known
  attached non-main branch, and successful Git command return codes. Dirty,
  detached, unknown, or command-error states fail closed.
- **Recovery and verification:** prevention regressions passed 135 tests;
  session start then reported the dirty tree untrusted and runtime diagnosis
  proved the current worktree source binding.
- **Evidence:** `docs/SESSION_LOG.md`, session `0.23.1a1 Candidate Verification
  Root-Cause Repair`.

## GIT-I09 — squash integration defeated ancestry-only cleanup

- **Symptom:** the GIT-001 research and Column PMM branches looked ahead or
  unmerged after their changes had been squash-integrated; ordinary ancestry
  counts retained apparent branch-only commits.
- **Impact:** an operator could repeat integrated work, rewrite a historical
  remote unnecessarily, or delete the wrong evidence based on a clean tree and
  ahead/behind counts.
- **Confirmed root cause:** squash creates a new commit identity even when the
  patch or resulting tree is equivalent; revision ranges prove reachability,
  not patch identity.
- **Unsafe reaction avoided:** age, cleanliness, and ancestry were not used as
  cleanup authority, and historical refs were preserved where they still
  carried audit value.
- **Preventive control:** disposition combines attachment, upstream, exact
  object IDs, PR receipt, reachability, `git cherry`/patch equivalence, tree
  comparison, tests, ownership, and explicit deletion approval.
- **Recovery and verification:** `git cherry origin/main
  codex/git-governance-research` reported `- 3be4790d`; the research lane was
  synchronized by normal merge and its tree proved exactly equal to main.
- **Evidence:** [the disposition plan](GIT-001-next-agent-disposition-plan.md),
  the [official evidence register](GIT-001-official-evidence-register.md), and
  the [PMM case study](../../git-automation/git-recovery-case-study-column-pmm.md).

## GIT-I10 — intake and help contracts drifted from executable behavior

- **Symptom:** documented `./run.sh task brief` was absent on the stale lane;
  `./run.sh generate indexes --help` started generation and then failed because
  the linked worktree lacked `.venv/bin/python`.
- **Impact:** safe startup stopped, a help request mutated shared generated data,
  and linked-worktree execution depended on a lane-local environment that the
  maintained runtime did not require.
- **Confirmed root cause:** documentation and old branch behavior advanced at
  different times; help dispatch fell into the write path; the generator
  hard-coded worktree-local runtime lookup.
- **Unsafe reaction avoided:** the failing historical implementation was not
  merged as a unit from PR #723.
- **Preventive control:** help and intake are non-writing contracts; generators
  use the invoking lane's maintained runtime; stale branches are synchronized
  only after their work is preserved.
- **Recovery and verification:** current-main implementations were rebuilt with
  focused regression coverage. `task brief` reports lane/base/upstream/sibling
  evidence without mutation, and a disposable linked-worktree test proves help
  is non-writing and generator calls are lane-bound.
- **Evidence:** [Packet 7A](GIT-001-phase-7A-preservation-workflow-recovery.md)
  and `docs/SESSION_LOG.md`, sessions `GIT-001 Program Start` and
  `GIT-001 Preservation and Workflow Recovery`.

## Cross-incident root causes

The ten incidents reduce to six outcome-changing root-cause families:

1. **Evidence compression:** tools or people collapsed distinct states—clean,
   saved, published, current, integrated, tested, or trusted—into one label.
2. **Scope leakage:** long-lived branches, mixed PRs, shared ledgers, global
   generators, and broad release automation crossed ownership boundaries.
3. **Identity leakage:** executable, checkout, imported source, artifact,
   branch, head SHA, and PR test SHA were treated as interchangeable.
4. **Gate skew:** local and CI surfaces differed, or deterministic correctness
   and performance evidence were mixed into one required result.
5. **Stale contract drift:** instructions, aliases, help behavior, validators,
   and old branches did not evolve together.
6. **Recovery before classification:** incomplete or misleading diagnostics
   encouraged rebase, skip, force, reset, or whole-branch integration before
   ownership and recoverability were established.

## Controls already proved useful

These are observed successful controls, not yet the final operating-model
proposal:

- a read-only task brief that inventories the current and sibling lanes;
- checkpoint-before-synchronization and fresh-lane selective recovery;
- normal non-rewriting merges for shared long-lived branches;
- exact source/artifact/head identity checks before accepting tests or CI;
- deterministic required checks with performance in a scheduled evidence lane;
- single-writer ownership for task/session/handoff/generated surfaces;
- PR, patch/tree, reachability, and retained-ref evidence together for cleanup;
- fail-closed trust and explicit owner authorization for destructive actions.

## Live Phase 3 inputs captured on 2026-08-13

The following are observations to compare in Phase 3, not findings or approved
changes:

- primary `main` was clean and exact with `origin/main` at `f3ad94dc`;
- the dedicated research lane was clean and exact with its upstream before a
  normal merge of current `origin/main`; its resulting tree remained identical
  to main while retaining the prior squash ancestry;
- six attached worktrees were present and all reported clean;
- the active `main_branch_rule1` ruleset blocks deletion and non-fast-forward
  updates and strictly requires `PR Gate`; the separate legacy branch-protection
  endpoint returned no rule;
- the ruleset does not currently list a required-pull-request rule and contains
  an always-bypass repository-role actor; the authenticated owner can bypass;
- repository merge settings allow merge commits, squash, and rebase; auto-merge
  and the update-branch button are disabled;
- the newest 30 workflow runs were successful, and recent documentation/PR
  validation runs generally completed in roughly 34-90 seconds;
- `validate_git_state.sh` took 4.05 seconds in the linked research worktree and
  performed a remote access probe even though the local lane was already
  classifiable.

Phase 3 must compare those live surfaces with the Phase 1 facts, current policy,
the ten incident chains, and actual executable behavior. It must distinguish a
confirmed outcome gap from an optional hardening idea.

## Phase 2 acceptance gate

- Ten evidence-backed incident families cover divergence, dirty lanes, mixed
  stale work, linked-worktree identity, generated-data scope, PR checks,
  release parity, trust, squash cleanup, and intake/help drift.
- Every incident names the main-process impact and either a confirmed root cause
  or an explicit unconfirmed boundary.
- Unsafe reactions are separated from successful recovery and verification.
- Historical commands are not promoted to current policy.
- No policy, GitHub setting, hook, cleanup behavior, branch, release, or runtime
  implementation changed in Phase 2.

Phase 2 is complete. Phase 3 may now build the gap/risk matrix; implementation
remains held until an owner-reviewed Phase 6 proposal and separately authorized
Phase 7 packet.
