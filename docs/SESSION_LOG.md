# Session Log

> Append-only decision log for AI agent sessions.
> Earlier sessions (1-100): [SESSION_LOG_through_session_100.md](_archive/SESSION_LOG_through_session_100.md)

---

## 2026-08-16 — Session: Index Local-Artifact Determinism Repair

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/index-local-artifact-determinism` from PR #810 merge
`755ed9d95c0a8f7e8c4a2165ddb748262df54482`

**Git handoff receipt:**
`docs/verification/post-india2-index-local-artifact-git-handoff-receipt.json`

**Focus:** Repair the one material post-merge defect found by primary-checkout
validation: checkout-local hidden artifacts changed recursive subfolder counts
and therefore the otherwise deterministic `docs/index.json` watermark.

### Summary

- Preserved both user-local editor swap files and every retained Git lane.
- Made recursive subfolder counts follow the scanner's existing top-level rule
  by excluding hidden files and hidden directory contents.
- Added a regression proving visible subfolder files remain hash-significant
  while `.swp` files and hidden editor directories do not affect counts or the
  freshness hash.
- Used one explicit repair candidate under the immutable closeout rule; no
  status-only update was appended to PR #810.

### Issues encountered

- After PR #810 merged with exact reviewed-tree equality, primary `main`
  reported only `docs/index.json` stale while a fresh detached worktree at the
  same tree reported 32/32 current.
- The first live-primary proof after excluding hidden paths restored the
  `planning` and `verification` counts but correctly differed from the old
  stored hash because the tracked hidden placeholder
  `docs/audit/reports/.gitkeep` also stopped contributing to `audit` count.

### Root causes and resolutions

- Confirmed root cause: direct-folder scanning excluded dot-prefixed files and
  directories, but recursive subfolder counting used unrestricted `rglob` and
  excluded only named cache/build directories. The primary checkout's ignored
  planning and verification `.swp` files increased those counts by one each.
  Resolution: reject any recursive file whose path relative to the subfolder
  contains a dot-prefixed component. Proof: the regression adds both a `.swp`
  and `.editor/state.json`; visible count and folder hash remain unchanged.
- Confirmed root cause: the first proof compared the new hidden-path semantics
  with the pre-repair stored hash, which still counted a tracked `.gitkeep`.
  Resolution: treat all hidden paths consistently as non-index content and
  perform one affected-index migration in the repair candidate. Proof: final
  evidence compares the migrated stored hash with a read-only scan of the real
  primary checkout containing both preserved swap files.

### Validation

- The three focused index-hash tests pass: visible subfolder changes remain
  significant; filesystem `mtime` and hidden local artifacts do not.
- Exact validation and immutable closeout requirements are recorded in
  `docs/verification/post-india2-index-local-artifact-evidence.json`.

### Timing

- Post-merge primary verification exposed the defect at approximately
  `2026-08-16T18:01:00Z`; root cause was confirmed within four minutes.

---

## 2026-08-16 — Session: Post-INDIA-2 Index Determinism Repair

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/index-mtime-determinism` from maintenance merge
`7541a7c768aee408e38bf8e7b4a1997469b0b9b1`

**Git handoff receipt:**
`docs/verification/post-india2-index-determinism-git-handoff-receipt.json`

**Focus:** Remove filesystem-time churn from maintained index freshness,
replace all-folder regeneration guidance with affected-folder refresh, and add
one read-only weekly drift audit without changing product, engineering,
dependency, release, or retained Git-lane state.

### Summary

- Made the index freshness watermark depend on repository content and structure
  while retaining `last_updated` only as observational display metadata.
- Added a regression that changes only a source file's filesystem timestamp and
  requires an unchanged folder freshness hash.
- Kept the existing docs/scripts structural guards because they validate real
  registry and link contracts; no all-folder freshness check existed in PR CI
  or pre-commit.
- Added one non-writing all-folder freshness audit to the existing Monday
  workflow and changed operator guidance to refresh only folders reported
  stale.
- Performed the one-time deterministic-hash migration for all 32 maintained
  indexes and bound the candidate to independent fresh-worktree validation.

### Issues encountered

- After PR #809 merged with a tree exactly equal to its reviewed candidate,
  the maintenance worktree reported 32/32 indexes current while primary
  `main` reported all 32 stale for the same Git tree.
- The existing closeout wording allowed agents to update versioned session,
  PR, hosted-check, or merge status after index generation or PR creation,
  creating a documentation-to-index-to-CI mutation loop.
- The first patch application could not match the decorative folder-scanner
  separator; no file changed in that failed attempt.
- The first focused Black check required one mechanical line-wrap change in
  the timestamp regression.

### Root causes and resolutions

- Confirmed root cause: file analyzers derive nested `last_updated` values from
  filesystem `mtime`, but the generator excluded only the top-level
  `last_updated` field from `content_hash`. A fresh linked worktree therefore
  produced a different freshness hash for byte-identical files. Resolution:
  recursively omit observational timestamps from the hash projection while
  retaining per-file content hashes and every deterministic structural field.
  Proof: the regression moves one unchanged Python file from 2020 to 2021,
  observes a changed display date, and observes an identical freshness hash.
- Confirmed root cause: the generator's stale-result message prescribed
  `--all`, encouraging repository-wide regeneration even when only one folder
  changed. Resolution: report all stale folders and explicitly require only
  those folders to be refreshed; agent guidance now separates the global
  read-only audit from focused writes.
- Confirmed root cause: the workflow required an immutable candidate but did
  not state the final mutation cutoff explicitly across all agent/session entry
  points. Resolution: freeze logs, task/handoff state, local evidence, and the
  pre-commit receipt first; refresh affected indexes once as the last repository
  write; keep later PR/CI/merge facts in GitHub and the external handoff. Proof:
  the canonical Git workflow, cross-agent instructions, session skill, and
  session-end prompt now carry the same ordered rule.
- Confirmed root cause: the failed patch used an inexact Unicode separator as
  context. Resolution: anchor the patch to function definitions and assertions.
  Proof: the intended implementation diff applies cleanly and the
  focused regression passes.
- Confirmed root cause: the handwritten multi-line assertion did not match the
  repository formatter's compact layout. Resolution: run Black on the one test
  file. Proof: Black, Ruff, and all 164 focused governance tests pass.

### Validation

- The focused content-hash tests pass, including timestamp independence and
  subfolder-projection sensitivity.
- Final evidence, exact counts, same-commit fresh-worktree proof, repository
  gates, and immutable handoff binding are recorded in
  `docs/verification/post-india2-index-determinism-evidence.json`.

### Timing

- Root-cause investigation began during maintenance closeout at approximately
  `2026-08-16T17:44:00Z`; bounded repair work began at approximately
  `2026-08-16T17:47:00Z`.

---

## 2026-08-16 — Session: Post-INDIA-2 Maintenance

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/post-india2-maintenance` from cleanup-execution merge
`3b08a9c1a0471dea86ac36e7a0ca1e03b045b82e`

**Git handoff receipt:** `docs/verification/post-india2-maintenance-git-handoff-receipt.json`

**Focus:** Complete only `MAINT-010-POST-INDIA2`: generated-truth refresh,
history compaction, completed-plan archival, feedback verification, and
review-only monthly evolution without product, engineering, dependency,
release, or additional Git-cleanup behavior.

### Summary

- Refreshed five stale generated count occurrences across four maintained
  guidance files; a repeated session-sync scan reports zero updates.
- Inspected the exact 32-folder index target set, ran one full live generation,
  and retained only deterministic generated-index changes.
- Compacted 107 parsed session entries to ten live plus 97 month-partitioned
  archives. Full-body multiset hashing proved no missing or duplicate entry;
  the final maintenance entry is compacted under the same ten-entry limit.
- Kept exactly 20 recent completed task rows, moved 49 older rows intact into
  `docs/_archive/tasks-history.md`, and preserved current release, no-active-
  task, INDIA-2 closeout, pile-cap HOLD, and raft HOLD truth.
- Used individual safe-move dry runs and live moves to archive the deprecated
  agent-evolver plan and completed post-v0.20 maintenance plan. The Git-
  hardening plan was already archived during Phase A, and `_active` now reports
  no active multi-session plans.
- Confirmed feedback is already clean, made no tester-instruction change, and
  ran the overdue monthly evolution in preview/review-only mode with no report
  or automated mutation.

### Issues encountered

- The planning snapshot expected 105 session entries, two pending feedback
  items, and three active plans. Live state had 107 entries, zero feedback
  items, and only two active plans because Phase A already archived the Git-
  hardening plan.
- ⚠️ TERMINAL ISSUE: the first two safe-move dry runs failed with
  `env: bash: No such file or directory`; no file moved.
- ⚠️ TERMINAL ISSUE: the first independent task-row hash report used a literal
  backslash-n separator, so its displayed digest differed from the mover's
  newline-delimited digest even though row counts and uniqueness passed.
- Repeating compaction after adding this maintenance entry preserved all 108
  session bodies but rebuilt `logs/session_index.json` as only 11 total / one
  archived entry, omitting the prior 97 archive rows from the index.
- The first new compaction regression stopped in its temporary fixture because
  the status printer could not express an archive path outside `REPO_ROOT`.
- The first final 32-folder index check found four stale indexes after the
  planned live generation pass.
- The first focused Black check required a mechanical layout change in the new
  archive-reader call.
- The first commit attempt was blocked before commit because the 91-entry
  August archive was 521,084 bytes, above the 500 KB added-file gate.

### Root causes and resolutions

- Confirmed root cause: the cleanup audit and execution added two new session
  records after the planning snapshot; Phase A advanced one explicitly
  authorized plan archival; the feedback ledger had already been resolved on
  merged `main`. Resolution: reconcile to live state, retain the latest ten and
  archive the actual remaining 97, skip already-complete feedback/plan actions,
  and preserve all feedback holds. Proof: session body hash/counts, feedback
  summary, and `_active` inventory are recorded below.
- Confirmed root cause: in zsh, the loop variable `path` is tied to the special
  `PATH` array; assigning the destination filenames to it temporarily removed
  `bash` from executable lookup. Resolution: stop, avoid the reserved variable,
  and invoke the worktree-bound Python launcher normally. Proof: both repeated
  dry runs and both live safe moves completed with zero broken links.
- Confirmed root cause: the read-only verifier encoded `\\n` rather than an
  actual newline when independently rebuilding the task-row digest. Resolution:
  use `chr(10)` as the delimiter. Proof: the corrected independent SHA-256
  `fda1896831fba820dc54d540e3b50b333f16203418b2c67ef6b65c376728b67e`
  exactly matches the mover's pre-write digest; all 68 original rows were
  present once before adding MAINT-010 and rotating the twentieth row.
- Confirmed root cause: `cmd_compact` rebuilt the session index from live
  entries plus only the entries archived in the current invocation; it never
  re-read existing monthly archives. Resolution: add one archive reader and use
  its complete parsed result in both the compaction and no-op index paths.
  Proof: the recurrence test passes and the repaired live index reports 108
  total, ten live, and 98 archived entries, matching the files on disk.
- Confirmed root cause: the new test monkeypatched the log/archive paths but
  left `REPO_ROOT` pointed at the real checkout. Resolution: bind all four
  repository paths to the temporary fixture. Proof: the exact test then passes
  without touching workspace archives.
- Confirmed root cause: the first live index generation preceded the newly
  required compactor repair/test, final handoff evidence, and next-session
  brief; those legitimate later writes changed the four indexed folders.
  Resolution: run one maintained corrective all-folder generation after content
  freeze. Proof: the repeated check reports all 32 indexes current.
- Confirmed root cause: the manually wrapped function call did not match the
  repository's Black layout. Resolution: format only `scripts/session.py` and
  regenerate its maintained index. Proof: Black and Ruff pass on the changed
  script and regression file, and all 32 indexes remain current.
- Confirmed root cause: strict one-file-per-month grouping did not account for
  the repository's per-file size ceiling, and the session index assumed every
  archived entry lived in the unnumbered monthly file. Resolution: shard a
  month into bounded parts below 480,000 bytes, preserve/parse all existing
  bodies before rewriting, and attach the actual archive path to each indexed
  entry. Proof: the commit hook stopped without a commit; August now occupies
  two files of 475,805 and 45,322 bytes, the pre/post body multiset hash is
  equal with zero duplicates, and the 108-row index names both parts.

### Validation

- Session compaction proof initially reports 107 total entries, ten live, 97
  archived, no duplicate bodies, and exact pre/post full-body multiset hash
  `90e50dc5a5a10f36e5b4deef4f4def26f1bef72c53de19a9efc52a2102567659`.
- Final proof after adding this entry reports 108 total entries, ten live, 98
  archived, zero duplicate bodies, and an unchanged pre/post multiset hash;
  the stable digest is stored outside the hashed session bodies in the
  maintenance evidence record, and the rebuilt index carries the same
  108/10/98 counts with actual part paths.
- Task compaction reports 20 unique live rows and 49 intact older rows in the
  new archive section after adding MAINT-010; closeout and both foundation HOLD
  IDs remain live. The task-format checker passes.
- All 163 focused tests in `test_agent_governance_automation.py`,
  `test_session_automation.py`, and `test_branch_disposition.py` pass,
  including the targeted index-generator write-scope regressions.
- Generated-number sync reports zero pending updates, and the corrective final
  index check reports 32/32 current.
- Health is 100/100 with zero issues; audit passes 19/19; parity remains 13
  supported / 8 held and 81/81 endpoints directly tested. Monthly evolution
  review completes in preview mode and feedback summary reports no pending
  items. Links validate all 1,319 internal references with zero broken links;
  strict metadata passes; the quick gate passes 10/10 and the full gate passes
  30/30 in 10.9 reported seconds. After the compactor repair and Black pass,
  all 163 focused tests, 32/32 indexes, links, quick 10/10, and full 30/30
  repeat green; the final full gate reports 11.3 seconds. Immutable-head,
  hosted, and merge-tree gates remain before integration.

### Timing

- Clean/source-bound maintenance orientation began at approximately
  `2026-08-16T17:24:00Z`.
- Count/index refresh, both compactions, safe archival, feedback reconciliation,
  review-only evolution, root-cause repair, and local validation completed in
  approximately 12 minutes.
- Final validation, hosted CI wait, merge closeout, and cumulative workflow time
  are recorded after the immutable candidate is integrated.

---

## 2026-08-16 — Session: Post-INDIA-2 Cleanup Execution

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/post-india2-cleanup-execution` from audited merge
`cbe10638fcba3f8919f8776462af34247b0604d0`, tree
`83804f8c3af4edcc7454c8f916e4f0fb3ca36231`

**Git handoff receipt:** `docs/verification/post-india2-cleanup-execution-git-handoff-receipt.json`

**Focus:** Execute only frozen candidate set
`POST-INDIA2-2499DF4ADE0DF704`, preserve every audit hold/exclusion, and publish
an action-level receipt with exact identities and postconditions.

### Summary

- Revalidated all 193 frozen actions against the audited merge, current local
  and GitHub refs, open pull requests, worktree states, protected branches, and
  held lanes before mutation.
- Removed exactly 58 clean inactive worktrees, 64 detached local branches, and
  71 remote branches; every action was immediately checked and recorded.
- Recovered 8,388,911,104 bytes from worktree surfaces, exactly matching the
  audited estimate; no force option, prune, reset, stash, history rewrite, PR
  closure, issue closure, or non-candidate deletion was used.
- Preserved 17 held/excluded union branches, including dirty detached `e54a`,
  Excel, `gh-pages`, all seven open Dependabot heads, and every detached,
  mismatched, owner-unknown, or integration-unknown lane.
- Final state has 11 worktrees, 8 local branches, and 16 remote branches. The
  receipt proves every candidate worktree/local/remote surface absent and every
  required protection postcondition true.

### Issues encountered

- After all 58 worktrees were removed, the first local-branch classification
  stopped before deletion because 28 squash-integrated branches were reported
  as `HOLD_UNIQUE_OR_UNPUBLISHED_WORK` with
  `UNIQUE_COMMITS_OR_PATCHES`. No local or remote branch had yet been deleted.
- ⚠️ TERMINAL ISSUE: a read-only `jq` projection assumed the worktree list was
  nested under a second `worktrees` key; the projection failed after the
  independent exact-tree assertion had already passed.
- ⚠️ TERMINAL ISSUE: the first semantic-workflow command guessed the obsolete
  direct path `scripts/check_git_workflow_semantics.py`; metadata passed, but
  the chained command stopped before the quick gate.
- The first session-end check accepted the session content but reported that
  the action receipt was not declared as a task-to-Git handoff contract.

### Root causes and resolutions

- Confirmed root cause: the inspection-only classifier intentionally treats
  commit/patch ancestry as a hold, while a multi-commit PR that was squash
  merged can retain unique commits/patches even when its complete head tree is
  byte-for-byte equal to the reachable merge tree. Resolution: stop closed,
  preserve the 58 completed removals in the receipt, then resume only after
  rechecking exact local/remote heads, selected PR identity, equal branch and
  merge trees, and merge-commit reachability for every named exception. Proof:
  the receipt binds 56 conservative classifier exceptions to those exact facts,
  all 193 actions are `REMOVED`, and all candidate refs are absent.
- Confirmed root cause: `git_state.py --json --worktrees` emits `worktrees` as a
  top-level array. Resolution: query its actual shape and repeat the read-only
  counts. Proof: the corrected projection reports 11 worktrees and no inventory
  query failures; no mutation occurred in either command.
- Confirmed root cause: semantic Git-workflow validation is maintained as
  `scripts/check_codex_git_workflow.py`. Resolution: discover it with
  `./run.sh find` and invoke that maintained path. Proof: the semantic check and
  the repeated quick gate pass.
- Confirmed root cause: the action-level cleanup receipt proves deletion and
  preservation outcomes but intentionally does not implement the repository's
  task-to-Git handoff schema. Resolution: generate the separate fail-closed
  handoff receipt from `git_state.py` plus fresh owner-authority evidence and
  declare its path on one line in this entry. Proof: the maintained receipt
  validator returns `CLEAN-001-POST-INDIA2-PHASE-B | HOLD`, and the repeated
  session-end check must discover it.

### Validation

- Receipt invariant checks pass: candidate-set hash is unchanged; 193/193
  actions are removed; failed actions are zero; expected and observed recovery
  are equal; all candidate absence flags and protection postconditions are true.
- `Python/tests/test_branch_disposition.py` and
  `Python/tests/test_git_state.py` pass all 89 focused tests.
- `scripts/check_links.py` validates 1,317 internal links with zero broken
  links; strict metadata, the maintained semantic Git-workflow check, and the
  targeted `docs/verification` index hash check pass.
- `./run.sh check --quick` passes 10/10 and `./run.sh check` passes 30/30 in
  11.7 reported seconds. Immutable-candidate audit, hosted checks, and
  post-merge tree comparison remain before Phase B integration.

### Timing

- Execution preflight began at `2026-08-16T16:42:32Z`.
- The fail-closed first pass removed worktrees through
  `2026-08-16T16:56:34Z`; root-cause confirmation and the independent resume
  boundary took about 4 minutes.
- Local and remote deletion completed at `2026-08-16T17:17:09Z`; focused
  postcondition validation completed by `2026-08-16T17:18:43Z`.

---

## 2026-08-16 — Session: Post-INDIA-2 Cleanup Audit

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/post-india2-cleanup-audit` from freshly fetched
`origin/main = d8202fef2566cd4955b2ba041914ff318d15d043`

**Focus:** Build one inspection-only union inventory of every pre-existing
worktree, local branch, GitHub branch, and associated pull-request integration
receipt. Freeze exact cleanup candidates and holds without removing any Git or
filesystem surface in Phase A.

### Summary

- Verified the fresh default anchor, clean primary, `source_bound=true`,
  `READY_LOCAL`, exact base equality, and no operation marker before writing.
- Inventoried 67 pre-existing worktrees, 70 pre-existing local branches, and 86
  GitHub branches; the audit lane raises the live local totals to 68 worktrees
  and 71 branches while the packet is active.
- Bound PR heads, submitted-review heads, merge commits, branch/merge trees,
  live owners, remote/API identities, open dependencies, worktree state, and
  disk estimates for every union member.
- Froze candidate set `POST-INDIA2-2499DF4ADE0DF704`: 71 evidence-complete
  branches and 193 separately bound worktree/local/remote actions, with about
  7.8 GiB recoverable only from the 58 worktree surfaces.
- Retained `main`, dirty detached `e54a`, `gh-pages`, the current audit lane,
  and Dependabot-managed refs; held Excel, all detached lanes, every mismatch,
  and every owner/integration-unknown branch.
- Performed no worktree removal, branch/ref deletion, prune, PR/issue closure,
  stash operation, history rewrite, release, or cleanup mutation in Phase A.

### Issues encountered

- ⚠️ TERMINAL ISSUE: immediately after `git worktree add`, the first runtime
  diagnosis and session command still ran from the primary checkout.
- The inherited planning snapshot said there were no open PRs, while the live
  GitHub query found seven open Dependabot PRs.
- The first full evidence-generator pass failed when it treated the nullable
  `mergeCommit` field on an open PR as an object; no partial artifact was
  produced.
- The first strict documentation metadata check rejected the new proposal's
  noncanonical `doc_type: verification` value.
- The first commit attempt was blocked by the 500 KB added-file limit because
  the evidence JSON repeated classifier inputs/outputs already present in the
  union rows; no commit was created.
- The first full repository gate passed 29/30 and failed only the hard
  documentation budget: the required proposal raised the non-archived count
  from the existing limit of 400 to 401.
- ⚠️ TERMINAL ISSUE: the first exact-commit invariant command used escaped
  quotes inside an f-string expression and stopped with `SyntaxError`; the
  committed candidate and repository were unchanged.

### Root causes and resolutions

- Confirmed root cause: creating a worktree does not change the caller's
  process working directory. Resolution: rerun diagnosis and every evidence or
  validation command with the audit path as the explicit working directory.
  Proof: runtime diagnosis resolves `structural_lib` under the audit lane and
  reports `source_bound=true`; `git_state.py` reports `READY_LOCAL` there.
- Confirmed root cause: GitHub state changed after the planning snapshot.
  Resolution: use fresh branch API, `ls-remote`, and all-state PR observations;
  all seven open heads are Dependabot-managed and remain excluded. Proof: the
  JSON packet reports seven open PRs and zero non-Dependabot open PRs.
- Confirmed root cause: GitHub represents an unmerged PR with
  `mergeCommit: null`, not an empty merge object. Resolution: normalize the
  nullable field before reading its OID and rerun the complete union build.
  Proof: the regenerated JSON parses and every candidate has an
  exact equal branch/merge tree reachable from current `origin/main`.
- Confirmed root cause: the content category was incorrectly reused as a
  metadata type. Resolution: keep the artifact in `docs/verification/` but use
  canonical `doc_type: reference`. Proof: the repeated strict metadata check
  passes.
- Confirmed root cause: the indented evidence serialized the same remote, PR,
  worktree, and classifier fields up to three times. Resolution: deduplicate
  projections, retain all decision-bearing classifier identities/facts, and
  use compact JSON. Proof: the artifact is 329,393 bytes, its candidate-set
  hash remains `POST-INDIA2-2499DF4ADE0DF704`, and all invariant checks pass.
- Confirmed root cause: `origin/main` was already at the 400-document ceiling,
  while this packet requires a new non-archived Markdown proposal. Resolution:
  advance one already-authorized maintenance action: dry-run then safely move
  the explicitly superseded Git-hardening plan to `docs/_archive/planning/`,
  update its maintained links, and reconcile `_active/README.md` to two plans.
  Proof: the safe mover preserves zero broken links; the corrective full gate
  must accept the restored 400-document count.
- Confirmed root cause: Python forbids backslashes inside f-string expression
  segments. Resolution: compute `head` and `tree` before formatting the line.
  Proof: the repeated committed-data audit passes at head `4240cc12`, tree
  `321fb684`, candidate set `POST-INDIA2-2499DF4ADE0DF704`, and 193 actions.

### Validation

- JSON syntax and invariant assertions pass for counts, protected exclusions,
  owner evidence, remote/API SHA equality, exact squash-tree equality, current-
  main reachability, and complete worktree action identities.
- `Python/tests/test_branch_disposition.py` and
  `Python/tests/test_git_state.py` pass all focused tests.
- `scripts/check_links.py` passes 1,319 internal links with zero broken links;
  strict metadata and semantic Git-workflow checks pass.
- Targeted `docs/verification` dry-run, live generation, and hash check pass;
  the maintained index advances from 141 to 143 files.
- Initial and final `./run.sh check --quick` runs pass 10/10.
- Immutable-candidate inspection, the full repository gate, exact-head hosted
  checks, and post-merge tree comparison remain before Phase A integration.

### Timing

- Orientation and live-state reconciliation started at approximately
  `2026-08-16T16:22:00Z`.
- Inventory/evidence implementation and first corrective passes took about 14
  minutes through the initial focused validation boundary.
- Hosted CI wait, Phase A closeout, and total elapsed workflow time are recorded
  in the cleanup execution receipt after the audit packet merges.

---

## 2026-08-16 — Session: INDIA-2 Final Closeout

**Agent:** Codex (`reviewer`, sole writer)

**Branch:** `codex/india-2-closeout` from freshly fetched
`origin/main = d28852156752ea6e44b0c9fbb67988088851bf3e`, tree
`38958c8a484d5f63a1092b2e852af64bef7afc2a`

**Git handoff receipt:** `docs/verification/india-2-closeout-git-handoff-receipt.json`

**Focus:** Administratively close INDIA-2 around six accepted bounded families
and explicit pile-cap/raft holds. Freeze one cumulative evidence index, pass
the broad Python suite and full repository gate, and publish without adding
calculation, service, API, React, capability, release, cleanup, or professional-
approval behavior.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconciled the task board, parent/dedicated plans, and next-session brief to
  the final INDIA-2 accepted/held boundary.
- Added one durable evidence index linking source, benchmark, publication,
  focused acceptance, PR/merge, tree, and Git receipt evidence for all six
  accepted families.
- The first broad Python run exposed 11 stale downstream contracts from the
  exact stress-block correction. Replayed the values independently and repaired
  only the affected tests/golden data; production calculation code is unchanged.
- The first full repository gate exposed the public API manifest still at 160
  symbols after the already-integrated strap Python workflow raised the actual
  public surface to 165. Regenerated only the maintained manifest.
- Bound pile-cap PR #804 and raft PR #805 as explicit G0 holds with no
  implementation and retained their exact reactivation contracts.
- Preserved generated truth at 13 supported / 8 held and 81/81 directly tested
  endpoints; no executable or capability-promotion file changed.

### Issues encountered

- The status projections intentionally still named `INDIA-2-CLOSEOUT` as next
  after raft G0 merged, so umbrella INDIA-2 could not yet be reported complete.
- The first broad Python run failed 11 tests: five beam golden cases, two
  footing golden cases, three isolated-footing/detailing cases, and one obsolete
  branch-coverage case still expected the pre-PR-#803 rounded inverse/clamp.
- The first full repository gate passed 29/30 and failed only API-manifest
  determinism because all five strap public exports were absent from the
  generated reference artifact.
- The first candidate Black check required a mechanical layout change in the
  rewritten stress-block domain-guard test.
- ⚠️ TERMINAL ISSUE: the first read-only commit/tree inspection loop assumed
  POSIX word splitting for quoted rows; zsh kept each row as one value and Git
  received an empty revision.
- ⚠️ TERMINAL ISSUE: one read-only status search used an unmatched shell glob;
  zsh stopped that command before `rg` ran.
- ⚠️ TERMINAL ISSUE: the first index-help lookup used the obsolete filename
  `scripts/generate_folder_indexes.py`; the interpreter reported that the file
  does not exist and made no changes.
- ⚠️ TERMINAL ISSUE: the first read-only diagnostic serializer did not provide
  an enum fallback to `json.dumps`; it stopped on `DesignSectionType` before
  printing the requested values and made no changes.
- ⚠️ TERMINAL ISSUE: the first `./run.sh session end --agent reviewer` could
  not discover the valid closeout receipt because its path was wrapped onto the
  line after the `Git handoff receipt` label.

### Root causes and resolutions

- Confirmed root cause: family/G0 packets correctly deferred umbrella status,
  cumulative gates, and the final evidence index to this dedicated closeout
  packet. Resolution: link all immutable family receipts in one closeout
  record, mark only the bounded INDIA-2 wave complete, and keep both held
  foundations and all post-INDIA-2 authority boundaries explicit. Evidence:
  final document, link, manifest/parity, broad Python, full repository, quick,
  exact-head, and hosted checks pass.
- Confirmed root cause: PR #803 deliberately replaced the approximate rounded
  inverse with shared exact Clause 38.1/Annex G equilibrium, but its focused
  selection did not include older broad beam golden vectors or isolated-footing
  expectations that consume the same helper. One coverage test also described
  the removed clamp instead of the exact solver's fail-closed domain guard.
  Resolution: independently replay the exact quadratic at high precision,
  update only the affected Ast/xu/pt/downstream shear expectations, and rewrite
  the obsolete coverage test to require `ValueError` outside the rectangular
  stress-block domain. Evidence: all 88 affected focused tests pass; the broad
  rerun is the cumulative acceptance proof.
- Confirmed root cause: strap publication PR #796 added four public types and
  one workflow but did not regenerate `docs/reference/api-manifest.json`; the
  later D and focused-acceptance packets validated Indian-code/OpenAPI truth,
  not this broad public-symbol artifact. Resolution: run the maintained API
  manifest generator and accept only its five-symbol 160-to-165 diff. Evidence:
  direct manifest check and focused API-manifest tests pass; the corrective full
  gate rerun is the repository-wide acceptance proof.
- Confirmed root cause: the manually wrapped `pytest.raises` call did not match
  Black's canonical layout. Resolution: run repository-bound Black on that one
  test file. Evidence: Black check, Ruff, and the exact domain-guard test pass.
- Confirmed root cause: zsh does not perform the assumed implicit word
  splitting on scalar expansions. Resolution: encode each row as
  `name:revision` and split it with zsh parameter expansion. Evidence: all nine
  requested commit/tree pairs resolved exactly; no files changed during the
  failed or corrected read-only commands.
- Confirmed root cause: zsh rejects unmatched globs before invoking a command.
  Resolution: use exact maintained paths or discover candidates with
  `rg --files` before filtering. Evidence: the subsequent targeted status and
  frontmatter searches completed; the worktree diff remained limited to the
  closeout documentation set.
- Confirmed root cause: the maintained index generator is named
  `scripts/generate_enhanced_index.py`; the attempted plural filename was an
  unverified recollection. Resolution: run `./run.sh find "generate folder
  indexes"` before invoking the maintained command. Evidence: repository
  discovery returned the exact generator and its help completed successfully.
- Confirmed root cause: dataclass serialization included an enum that standard
  `json.dumps` cannot encode. Resolution: add `default=str` to the read-only
  diagnostic serializer. Evidence: the corrected command printed all beam,
  footing, service, and detailing values without repository mutation.
- Confirmed root cause: the session checker intentionally parses a receipt path
  only when it appears on the same line as its label. Resolution: use the
  established one-line declaration. Evidence: direct receipt validation and
  the repeated session-end check both accept the same committed receipt.

### Validation

- First `./run.sh test`: 6,301 passed, 11 failed, 3 skipped, 6 deselected in
  55.21 seconds; this is diagnostic evidence, not acceptance.
- Focused repair selection: 88 passed after independently replaying the exact
  stress-block and downstream values.
- Corrective broad `./run.sh test` rerun: 6,312 passed, 3 skipped, 6 deselected,
  and 46 warnings in 50.59 seconds (51.98 seconds wall time).
- First `./run.sh check`: 29/30 passed; only API manifest failed because the
  five integrated strap exports were absent.
- Corrective `./run.sh check` rerun: 30/30 passed in 11.0 seconds (3.16
  seconds wall time); API, docs, architecture, governance, FastAPI, Git, stale-
  reference, and code-quality groups are all green.
- Focused frontmatter, links, manifest, parity, folder-index, and quick-gate
  results are recorded after the human-owned closeout content is frozen.
- Required hosted checks must pass on the unchanged reviewed head before merge.

### Timing

- Orientation and exact Git/runtime verification: approximately 3 minutes.
- Evidence-chain sampling and final truth reconciliation: approximately 9
  minutes before cumulative validation.
- Initial plus corrective broad validation and focused repair: approximately 4
  minutes. First full gate plus API-manifest repair: approximately 2 minutes.
  Corrective full validation: 11.0 reported seconds. Candidate audit, hosted CI
  wait, closeout, and total elapsed time are reported in the final handoff.

## 2026-08-16 — Session: INDIA-2 Foundation Raft G0

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-foundation-raft-g0` from freshly fetched
`origin/main = def0b493e33fa566fd3f23bf166287fcda6169d6`, tree
`7da91c66143e83933a88bb9a4d5396bede89cf6d`

**Git handoff receipt:**
`docs/verification/india-2-foundation-raft-g0-git-handoff-receipt.json`

**Focus:** Decide whether exactly one regular rectangular rigid raft can be
source-bound and independently benchmarked. Publish `HOLD` with exact
reactivation conditions if either prerequisite is absent. Do not create
calculation, service, API, React, release, cleanup, or retirement work.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconfirmed the controlled IS 456 source hashes and found no retained IS
  2950 or other raft companion source.
- Verified official BIS discovery: IS 2950 (Part 1):1981 is active, reaffirmed
  2023 with one amendment, and its preview covers conventional rigid and
  simplified flexible methods for mainly vertical/evenly distributed loads.
- Verified that IISc/NPTEL describes a relevant conventional rigid-mat model,
  but neither that chapter nor the located question set supplies a complete,
  independently replayable structural raft benchmark.
- Returned `HOLD`, retained the regular rigid-raft candidate, and created no
  numeric design result or raft calculation/publication file.
- Made the hold machine-visible in the generated manifest with a direct
  regression and reconciled the task board/plans/brief to name cumulative
  `INDIA-2-CLOSEOUT` next.

### Issues encountered

- The required controlled IS 2950 source/amendment binding and structural raft
  benchmark were absent, so the conventional rigid candidate could not be
  activated or verified through strength/detailing.
- The public material initially appeared promising because it included both a
  conventional analysis procedure and a raft-design question, but it did not
  include the complete worked structural result set required by G0.

### Root causes and resolutions

- Confirmed root cause: the repository-controlled source registry contains
  only IS 456:2000 through Amendment 5 and Amendment 6. The BIS catalogue and
  preview prove IS 2950 discovery/scope but are not a committed authenticated
  source/amendment identity. Resolution: publish `HOLD`, preserve
  `HELD / NOT_IMPLEMENTED`, and require the exact standard/amendment hashes
  before reactivation. Evidence: the decision record binds current official
  discovery separately from the controlled-source inventory.
- Confirmed root cause: the NPTEL chapter defines a rigid planar-pressure/
  whole-mat method, while the question set asks for a raft design without an
  accepted solution; neither closes the requested pressure, equilibrium,
  orthogonal actions, flexure, shear, reinforcement, or anchorage values.
  Resolution: retain the candidate but treat conceptual procedure and unsolved
  prompts as non-benchmarks. Evidence: the G0 record lists the missing
  intermediates and a five-part reactivation contract.

### Validation

- `./scripts/python_runtime.sh -m pytest Python/tests/test_indian_code_manifest.py -q`:
  `10 passed`.
- `./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check`:
  current; raft is `HELD / NOT_IMPLEMENTED`, has no workflow, and cites the G0
  hold evidence.
- `./scripts/python_runtime.sh scripts/check_docs.py --frontmatter --json`:
  345 scanned, 285 with frontmatter, 60 permitted legacy records, zero invalid.
- `./scripts/python_runtime.sh scripts/check_links.py`: 1,277 internal links,
  zero broken.
- `./run.sh efficiency check`: pass.
- Black and Ruff on the two owned Python files: pass.
- `./run.sh parity`: 13 supported / 8 held, 81/81 endpoints directly tested,
  and 13/13 React hooks connected.
- `./run.sh check --quick`: `10/10` pass.

### Timing

- Orientation/source/Git inspection and public evidence verification:
  approximately 3 minutes.
- Decision record, truth reconciliation, and focused validation before
  candidate closeout: approximately 2 minutes.
- Hosted CI wait, closeout, and total elapsed: record after merge.

## 2026-08-16 — Session: INDIA-2 Foundation Pile-Cap G0

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-foundation-pile-cap-g0` from freshly fetched
`origin/main = 1139e9ea06751c72b66098a575c1f5e327c56ef5`, tree
`0abefcd0255157bd1444549f2066eb937f45e5a0`

**Git handoff receipt:**
`docs/verification/india-2-foundation-pile-cap-g0-git-handoff-receipt.json`

**Focus:** Decide whether exactly one centred axial two-pile structural cap can
be source-bound and independently benchmarked. Publish `HOLD` with exact
reactivation conditions if either prerequisite is absent. Do not create
calculation, service, API, React, release, cleanup, or retirement work.

### Summary

- Verified the exact fresh base, `source_bound=true`, `READY_LOCAL`, no Git
  operation marker, and a clean one-writer linked worktree before editing.
- Reconfirmed the controlled IS 456 source hashes and found no retained IS
  2911 or other pile-cap companion source.
- Searched existing code, tests, evidence, official BIS discovery surfaces,
  and primary NPTEL material. No pile-cap implementation or accepted,
  independently replayable structural two-pile-cap benchmark exists.
- Returned `HOLD`: neither a footing critical-section analogy nor generalized
  strut-and-tie model has enough authority to activate. No numeric design
  result and no pile-cap calculation/publication file was created.
- Made the hold machine-visible in the generated manifest with a direct
  regression and reconciled the task board, both INDIA-2 plans, and the compact
  brief to name decision-only raft G0 next.

### Issues encountered

- The required controlled IS 2911 companion source and structural two-pile-cap
  benchmark were absent, so the candidate could not select or verify a
  structural action model.
- The linked worktree has no `private_sources/` directory because the retained
  controlled sources are ignored and live only under the primary checkout.
- ⚠️ TERMINAL ISSUE: the first source-inventory command used the worktree-local
  `private_sources` path and failed; a later `shasum` glob also included
  directories and reported them as invalid hash targets.
- ⚠️ TERMINAL ISSUE: one multi-section documentation patch used a stale line-
  wrapping context and applied nothing.
- The first Black check found the added manifest regression needed mechanical
  formatting.
- The all-folder index generator also refreshed modification dates in unrelated
  folders because linked-worktree file mtimes are current even when content is
  unchanged.

### Root causes and resolutions

- Confirmed root cause: the repository-controlled source registry contains
  only IS 456:2000 through Amendment 5 and Amendment 6; official IS 2911
  catalogue/preview pages are discovery evidence, not controlled
  implementation inputs. The benchmark search found pile-group/geotechnical
  material and a course syllabus, not a complete structural cap example.
  Resolution: publish `HOLD`, preserve `HELD / NOT_IMPLEMENTED`, and require an
  authenticated controlled companion source plus a replayable benchmark before
  reactivation. Evidence: the G0 decision record inventories the sources,
  compares both candidate models, and states five exact reactivation gates.
- Confirmed root cause: ignored controlled-source material is intentionally not
  populated in linked worktrees. Resolution: inspect the primary checkout's
  retained private-source registry by absolute path without mutation and hash
  the two exact PDF paths. Evidence: SHA-256 values reproduce as
  `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`
  and `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
- Confirmed root cause: the inventory/hash commands assumed worktree-local
  ignored files and then used a directory-bearing wildcard. Resolution: use
  the verified absolute primary registry and exact file targets. Evidence: the
  corrected inventory and both hashes completed successfully.
- Confirmed root cause: the failed patch copied a nearby sentence without its
  exact preceding line wrap. Resolution: inspect the target ranges and apply
  smaller exact-context hunks. Evidence: the plans now record pile-cap HOLD and
  identify raft G0 as next; `git diff --check` passes.
- Confirmed root cause: the new assertion exceeded the formatter's line width.
  Resolution: run repository-bound Black once on the owned test. Evidence:
  Black check and Ruff pass, and all nine manifest tests pass.
- Confirmed root cause: the index generator derives per-file update dates from
  filesystem mtimes, which are not stable content provenance in a newly
  materialized linked worktree. Resolution: use exact reverse patches through
  `apply_patch` to remove only generator-created unrelated diffs, retain the
  five owned folder indexes and two previously stale content hashes exposed by
  generation, then check each owned index directly. Evidence: the final diff
  contains no unrelated agent, React, FastAPI, example, core, insight, report,
  or visualization index, while all five owned index checks pass.

### Validation

- `./scripts/python_runtime.sh -m pytest Python/tests/test_indian_code_manifest.py -q`:
  `9 passed`.
- `./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check`:
  current; pile-cap is `HELD / NOT_IMPLEMENTED`, has no workflow, and cites the
  G0 hold evidence.
- `./scripts/python_runtime.sh scripts/check_docs.py --frontmatter --json`:
  344 scanned, 284 with frontmatter, 60 permitted legacy records, zero invalid.
- `./scripts/python_runtime.sh scripts/check_links.py`: 1,271 internal links,
  zero broken.
- `./run.sh efficiency check`: pass.
- Black and Ruff on the two owned Python files: pass.
- `./run.sh parity`: 13 supported / 8 held, 81/81 endpoints directly tested,
  and 13/13 React hooks connected.
- Direct checks for `Python/tests`, `docs`, `docs/planning`,
  `docs/verification`, and `scripts` indexes: pass.
- `./run.sh check --quick`: `10/10` pass.

### Timing

- Orientation/source and Git inspection: approximately 4 minutes.
- Decision research and evidence drafting: approximately 3 minutes.
- Repair and focused validation before candidate closeout: approximately 4
  minutes.
- Hosted CI wait, closeout, and total elapsed: record after merge.

## 2026-08-16 — Session: INDIA-2 Clause 38.2 Truth Hygiene

**Agent:** Codex (`structural-engineer`, sole writer)

**Branch:** `codex/india-2-truth-hygiene-38-2` from freshly fetched
`origin/main = df3635e8811a4d7e69f8786349ce3507f8a28001`, tree
`4de5ae83cdc115fe1984e2b97b616676e094e578`

**Git handoff receipt:**
`docs/verification/india-2-truth-hygiene-38-2-git-handoff-receipt.json`

**Focus:** Audit every live Clause 38.2 beam-flexure identity, independently
benchmark the rounded inverse against exact equilibrium, and repair arithmetic
only if a supported outcome changes. Do not start pile-cap, raft, cleanup,
release, React, dependency, or broad final-gate work.

### Summary

- Controlled-source inspection proved that live beam flexure must bind Clause
  38.1 and Annex G-1.1/G-1.2/G-2.2; the source contains no Clause 38.2, 38.3,
  or 38.4 identity.
- Replayed the legacy rounded inverse and exact equilibrium independently. A
  supported maximum-steel discriminator changed from a false safe result to
  `E_FLEXURE_003`, so metadata-only repair was rejected.
- Promoted one exact rectangular stress-block solver to the common IS 456
  layer, delegated the slab wrapper to it without changing the slab error
  contract, and routed beam required-steel design through it.
- Reconciled decorators, serialized result provenance, registry metadata,
  traceability examples, parity/regression data, active formulas/maps, and the
  generated Indian-code manifest without changing public signatures or units.
- Named decision-only `INDIA-2-FOUNDATION-PILE-CAP-G0` as the sole next packet
  after merge; no foundation implementation was started.

### Issues encountered

- Live metadata and result provenance named nonexistent Clause 38.2/38.3/38.4
  identities and misapplied flanged Annex G-2.2 to rectangular steel design.
- The rounded `4.6` inverse returned steel just below the maximum for a valid
  supported beam while exact equilibrium returned steel just above it, changing
  the main-process safety outcome.
- The first focused test command guessed a nonexistent
  `Python/tests/codes/is456/beam` directory and stopped before collection.
- After executable truth changed, the deterministic committed Indian-code
  manifest was stale until its single planned generator pass.
- The first formatting gate found the new common helper and acceptance module
  did not match the repository Black layout, so the quick gate did not start.
- The first public-contract selection guessed two nonexistent Python API test
  files; the corrected maintained selection then exposed one stale hardcoded
  downstream shear value after the exact flexural steel percentage changed.
- Hosted FastAPI validation passed 441 tests but failed two additional
  benchmark-derived literals: the 153-beam BOQ total and isolated-footing
  screening steel percentage still reflected rounded beam flexure.

### Root causes and resolutions

- Confirmed root cause: historical registry and decorator entries treated
  derived beam design cases as Clause 38 subclauses without checking the
  controlled source hierarchy. Resolution: remove unsupported 38.2/38.3/38.4
  registry entries, register G-1.2, and bind each live consumer to Clause 38.1
  and the applicable Annex G case. Evidence: semantic tests and the generated
  manifest show G-1.2 registered to doubly reinforced design and zero
  registration-only references.
- Confirmed root cause: beam required-steel design used rounded algebraic
  coefficients (`0.5` and `4.6`) instead of solving the canonical `0.36/0.42`
  stress-block equilibrium already used exactly in later foundation/slab work.
  Resolution: one common exact solver now serves beam and slab paths. Evidence:
  the independent `100 kN m` back-substitution closes equilibrium, and the
  `572.05 kN m` discriminator now returns `6600.050311675635 mm2`, exceeds the
  `6600 mm2` maximum, and fails with `E_FLEXURE_003`.
- Confirmed root cause: the focused command assumed a test-folder topology
  instead of discovering maintained paths. Resolution: use `rg --files` to
  select the actual integration/property/regression/unit/slab files, then rerun
  the complete focused selection. Evidence: 190 focused tests pass.
  ⚠️ TERMINAL ISSUE: guessed nonexistent beam test directory -> discovered and
  ran maintained focused files with `rg --files`.
- Confirmed root cause: clause/decorator truth is an input to the deterministic
  Indian-code manifest. Resolution: run the maintained generator exactly once
  after code and tests froze. Evidence: the deterministic-current manifest test
  passes with 173 known references, 98 registered, and zero registration-only.
- Confirmed root cause: hand-applied multiline expressions differed from
  Black's deterministic line wrapping. Resolution: format only the two reported
  files, rerun all 190 focused tests, then run the quick gate. Evidence: Black
  and Ruff pass and the quick gate passes 10/10.
- Confirmed root cause: the public beam test correctly derives shear steel per
  spacing from returned `tau_v` and `tau_c`, but also pinned the old rounded-
  flexure-derived scalar; exact Ast changes the tension percentage and Table 19
  interpolation. Resolution: preserve the formula assertion and update only the
  exact derived scalar. Evidence: the actual maintained beam/capability/public-
  documentation selection passes 17 tests. ⚠️ TERMINAL ISSUE: guessed two
  nonexistent Python public API tests -> discovered the maintained FastAPI
  public-contract paths with `rg --files` and reran them.
- Confirmed root cause: the bundled BOQ test derives selected-bar weight from
  all 153 exact beam results, while the footing screening value uses the shared
  rectangular stress-block inverse; both assertions pinned outputs from the
  replaced rounded solver. Resolution: update only the observed derived
  scalars, retaining dataset hash, calculation identity, PASS, provided-steel,
  and shear-basis assertions. Evidence: the two failed tests and the complete
  FastAPI suite are rerun before the replacement PR head is accepted.

### Validation through content freeze

- Startup: `source_bound=true`, `READY_LOCAL`, no operation marker, exact base
  equality with freshly fetched `origin/main`, and a clean fresh lane.
- Focused flexure, slab compatibility, traceability, manifest, parity,
  regression, service, property, and unit selection: 190 passed.
- Focused FastAPI beam, capability, and public-documentation contracts: 17
  passed.
- Hosted failure reproduction: both exact failing tests reproduced locally,
  then passed after the derived-value repair; the complete FastAPI suite passed
  all 449 tests with 52 warnings.
- Exact equilibrium and false-safe outcome have direct semantic regressions;
  public signatures and unit conventions remain stable.
- Links, maintained indexes, quick `10/10`, normal hooks, hosted checks,
  immutable-head review, merge-tree equality, and final elapsed time complete
  during candidate/publication closeout.

### Timing through content freeze

- Orientation and source audit: `14:51:40Z` to `14:56:30Z` — 4 minutes 50
  seconds.
- Implementation, benchmark repair, and focused validation: `14:56:30Z` to
  `15:02:20Z` — 5 minutes 50 seconds.
- Evidence, plan, task, and handoff freeze: `15:02:20Z` to `15:05:00Z` — 2
  minutes 40 seconds.
- Generator/gates, hosted CI wait, merge closeout, and total wall time are
  reported by the final closeout observation.

## 2026-08-16 — Session: Documentation Frontmatter Contract Repair

**Agent:** Codex (`doc-master`, sole writer)

**Branch:** `codex/doc-frontmatter-contract` from freshly fetched
`origin/main = c8fcd2f0f9b933eb8e8787dc901ee440e05ae984`, tree
`41d878c0681e5e51d159615d14290d5c3964c822`

**Focus:** Make machine-readable frontmatter validation fail whenever invalid
records exist, add direct valid/invalid regressions, and repair exactly the
eight frozen lifecycle/type records. Do not bulk-add frontmatter to 60
permitted legacy documents or start Clause 38.2, pile-cap, raft, cleanup,
release, React, dependency, or broad-gate work.

### Summary

- Reproduced the defect on the clean source-bound lane: JSON mode reported
  `342` checked, `282` with frontmatter, `60` without frontmatter, and `8`
  invalid, but exited `0`; text mode exited `1` on the same records.
- Made JSON mode return the same invalid-count result as text mode without
  changing the report object, and added direct valid/invalid payload-and-exit
  regressions.
- Changed only the eight frozen metadata values: the closed library-first plan
  is `archived`; live combined/flat/deep/wall evidence is `active`; strap A/B/C
  evidence uses `doc_type: reference`. Narrative engineering outcomes remain
  unchanged.
- Reconciled the task board, execution plan, and compact handoff so
  `INDIA-2-TRUTH-HYGIENE-38-2` is the sole next packet after merge.

### Issues encountered

- JSON validation visibly printed eight invalid records but returned success,
  allowing a machine consumer to accept an invalid documentation state.
- Eight documents used completion/acceptance/evidence words as schema lifecycle
  or type values, conflating narrative engineering outcome with maintained
  document metadata.
- The first normal commit-hook run stopped because the compact brief used
  `## Required reading` instead of the exact required heading
  `## Required Reading`, blocking candidate publication.

### Root causes and resolutions

- Confirmed root cause: `check_frontmatter()` returned `0` unconditionally
  immediately after printing its JSON report, before applying the invalid-count
  rule used by text mode. Resolution: return `1` when
  `report["invalid_frontmatter"]` is nonzero in that branch. Evidence: the
  direct invalid fixture preserves the full report and returns `1`; the direct
  valid fixture preserves its report and returns `0`; both tests pass.
- Confirmed root cause: record authors used `completed`, `complete`, `accepted`,
  and `verification` to describe the body outcome/purpose even though the
  maintained schema defines document lifecycle as active, draft, deprecated,
  or archived and type as guide, reference, tutorial, index, spec, or log.
  Resolution:
  map the closed plan to `archived`, live evidence to `active`, and strap
  evidence to `reference`, without changing any engineering statement.
  Evidence: live JSON and text modes both exit `0`, report zero invalid, and
  retain exactly 60 permitted no-frontmatter records.
- Confirmed root cause: the handoff rewrite normalized heading capitalization
  without first checking the exact string contract enforced by
  `check_session_docs.py`; generic link, brief-length, and quick checks did not
  exercise that constraint. Resolution: restore the exact required heading and
  retain normal hooks as the publication guard. Evidence: the repaired hook
  run must pass before the candidate commit is accepted. ⚠️ TERMINAL ISSUE:
  normal commit hooks rejected the compact brief heading -> restored the exact
  maintained heading and reran the candidate gates.

### Validation through content freeze

- Startup: `source_bound=true`, `READY_LOCAL`, no operation marker, exact base
  equality with fetched `origin/main`, and a clean fresh lane.
- Focused regressions: `2 passed`; Ruff and Black pass for the checker and new
  test module.
- Live replay: JSON reports `invalid_frontmatter: 0` with `files_invalid: []`;
  JSON and text both exit `0`; total/with/without/skipped counts remain
  `342/282/60/462`.
- Maintained indexes, links, quick `10/10`, normal hooks, hosted checks, and
  merge-tree equality complete during candidate/publication closeout.

### Timing through content freeze

- Orientation and source binding: `14:23:14Z` to `14:24:24Z` — 1 minute 10
  seconds.
- Reproduction, implementation, and focused validation: `14:24:24Z` to
  `14:26:36Z` — 2 minutes 12 seconds.
- Task/plan/handoff reconciliation: `14:26:36Z` to `14:28:30Z` — 1 minute 54
  seconds.
- Generator/gates, hosted CI wait, merge closeout, and total wall time are
  reported by the final closeout observation.
