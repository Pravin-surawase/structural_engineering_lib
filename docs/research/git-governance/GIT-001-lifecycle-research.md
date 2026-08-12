---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 1
---

# GIT-001 Phase 1 — Factual Lifecycle Map

## Status and reading key

This is a source-backed, non-normative map. It does not replace the canonical
workflow and does not authorize policy, settings, cleanup, or release changes.

- **EF — external fact:** supported by an official source ID in the evidence register.
- **PO — project observation:** dated evidence from this repository.
- **UC — unresolved choice:** a decision deliberately held for later design/review.
- **NA — not applicable:** supported by a dated topology observation.

## Foundational state model

| State surface | Factual meaning | Scope | Evidence | Label |
|---|---|---|---|---|
| Commit/object | A commit records the index as a new immutable history object and normally advances the current branch. | Repository history; shareable after ref publication | GIT-F01, GIT-F06 | EF |
| Branch/ref | A branch names a commit; an upstream is separately configured tracking metadata. | Shared ref namespace in linked worktrees | GIT-F03, GIT-F07 | EF |
| Index | The index is distinct from both `HEAD` and the working tree and can hold merge stages. | Per worktree | GIT-F01–F03 | EF |
| Working tree/untracked paths | Modified and untracked content is not made durable merely by naming a branch or task. | Per worktree filesystem | GIT-F02, GIT-F06 | EF |
| Remote-tracking ref | Fetch updates local knowledge of configured remote refs; it does not integrate those commits into the current branch. | Shared repository refs | GIT-F08 | EF |
| Remote branch | Push updates remote refs under refspec and server rules. | Shared/published | GIT-F10 | EF |
| Reflog/unreachable object | Reflogs and unreachable objects provide time-limited recovery evidence subject to expiry and garbage collection. | Local repository | GIT-F05, GIT-F17 | EF |
| Codex task/chat | A task thread retains conversation context; archive retains it and delete is irreversible through product recovery surfaces. | OpenAI account/product history | OAI-F01, OAI-F03 | EF |
| Codex worktree mapping | No located public contract binds a task snapshot/handoff/archive event to a Git commit, ref, or worktree lifecycle. | Product/Git boundary | UNRESOLVED-OAI-01–03 | UC |

## Lifecycle stage map

| Stage | Git state and external facts | GitHub/Codex external facts | Current project observation | Held choice or required evidence | Sources | Label set |
|---|---|---|---|---|---|---|
| 1. Classify and baseline | `HEAD`, branch, upstream, index, working tree, untracked paths, operation state, and refreshed remote refs are distinct evidence. | A task thread is context, not proof that Git content is committed or published. | GIT-001 intake found a clean attached branch exactly at its upstream before synchronization. | Ownership and intended target remain unresolved until the baseline names them. | GIT-F01–F03, GIT-F07–F08, OAI-F01, OBS-05 | EF, PO, UC |
| 2. Isolate | A linked worktree separates filesystem, `HEAD`, index, and operation state but still shares refs, objects, and default configuration. | Codex supports separate task threads and built-in worktrees. | Six attached worktrees existed on 2026-08-12; none was detached, locked, or prunable. | Worktree creation, branch naming, and shared-surface ownership are later policy choices. | GIT-F03, GIT-F16, OAI-F01, OBS-03 | EF, PO, UC |
| 3. Persist locally | Commit records the selected index; unstaged/untracked content is excluded unless explicitly staged. | A reviewed diff in a task does not itself create Git history. | This repository uses conventional scoped commits and pre-commit checks under the current canonical policy. | Commit size, checkpoint cadence, and temporary-commit conventions remain open. | GIT-F02, GIT-F06, OBS-06 | EF, PO, UC |
| 4. Refresh and synchronize | Fetch refreshes remote-tracking refs; pull additionally integrates; a non-fast-forward merge commit retains both parent histories; rebase recreates commits on a new base. | A PR can become stale when its base or head changes and required checks bind to the latest relevant SHA. | GIT-001 merged `origin/main` without rewriting and produced an exact-main tree at `54a03557`. | Merge versus rebase by lane type is a later design choice. | GIT-F08–F12, GH-F01–F02, OBS-04 | EF, PO, UC |
| 5. Verify | Tree, diff, tests, and exact commit identity are different receipts. Reachability is not patch equivalence. | Required checks and their conclusions must be evaluated for the latest relevant SHA. | The synchronization quick gate passed 10/10 and both tree IDs equaled `origin/main`. | Required local gate by risk class remains open. | GIT-F04, GH-F01–F02, OBS-04–05 | EF, PO, UC |
| 6. Publish | Push updates remote refs; non-fast-forward branch updates are normally rejected unless overridden. | Publication can create/update a PR; draft PRs cannot merge. | The synchronized research branch was fast-forward pushed to its existing remote branch. | When to publish checkpoints or open a draft PR remains open. | GIT-F10, GH-F04, OBS-05 | EF, PO, UC |
| 7. Review | Patch identity and commit identity can differ after squash, rebase, or selective reproduction. | Reviews, required checks, mergeability, and merge method are separate PR facts. | Prior GIT-001 research was squash-integrated, so `git cherry` rather than ahead/behind exposed equivalence. | Review count, reviewer roles, and acceptable merge methods remain open. | GIT-F04, GH-F01–F05, OBS-08 | EF, PO, UC |
| 8. Integrate | Merge, rebase, cherry-pick, and revert have different ancestry and recovery effects. | Merge commit, squash, rebase, auto-merge, and merge queue create different histories/validation events. | Recent GIT-001 incident-recovery PRs used exact-head checks and squash merges, but Phase 1 does not endorse that choice. | Integration method and merge-queue adoption remain open. | GIT-F11–F13, GH-F05–F07, OBS-08, OBS-10 | EF, PO, UC |
| 9. Release | Tags bind names to objects; annotated/signed tags carry additional identity; published tag replacement is hazardous. | A GitHub release is a distinct object tied to a selected tag/target and can have notes/assets and draft/prerelease state. Environments can add deployment gates. | The repository has release tags and GitHub release evidence; GIT-001 makes no new release claim. | Signing, immutable-release, environment, and artifact-publication policy remain open. | GIT-F18, GH-F08–F09, OBS-09 | EF, PO, UC |
| 10. Retain and close | Commit/ref reachability, reflogs, and garbage collection provide different retention horizons. | Archiving retains a Codex chat; deleting it is unrecoverable through UI/API/support. | Historical PMM and workflow refs were intentionally retained after selective recovery. | Required forensic refs, chat retention, and closeout duration remain open. | GIT-F05, GIT-F17, OAI-F03, OBS-08, OBS-10 | EF, PO, UC |
| 11. Clean up | Worktree remove/prune/repair and branch deletion are separate operations; branch attachment can block deletion. Clean removes untracked files. | Codex archive/delete behavior does not publish a Git cleanup guarantee. | Excel/Alpha worktrees and branch candidates remain held behind explicit decisions in the disposition plan. | Exact approval scope and retention period remain unresolved; no cleanup is authorized here. | GIT-F03, GIT-F07, GIT-F15, UNRESOLVED-OAI-02, OBS-08 | EF, PO, UC |
| 12. Recover | Reflog, revert, restore, reset, stash, cherry-pick, merge abort/continue, and rebase/sequencer controls affect different state surfaces. | A changed PR head/base invalidates prior exact-head evidence; deleted Codex chats cannot be recovered. | PMM and PR #723 were selectively recovered instead of applying either stale mixed branch as a unit. | Recovery action requires path/state/ownership diagnosis; the command decision remains case-specific. | GIT-F05, GIT-F11–F17, GH-F02, OAI-F03, OBS-10 | EF, PO, UC |

## Path maps

### Normal single-lane work

**PO — current canonical-practice sequence (OBS-06), recorded as an observation
rather than adopted here as new policy:**

```text
Classify -> isolate/attach -> edit -> stage -> commit -> refresh
-> synchronize -> verify -> push -> review -> integrate -> retain/close
```

- **EF:** commit, fetch, synchronization, push, PR, and integration are distinct
  state changes (GIT-F06–F13, GH-F01–F06).
- **PO:** the repository currently requires branch/upstream/diff/PR inspection
  before mutation in its canonical policy (OBS-06).
- **UC:** checkpoint cadence, draft-PR timing, and merge method remain Phase 4
  design questions.

### Parallel work

**PO — current canonical-practice topology (OBS-07), recorded as an observation
rather than adopted here as a new ownership model:**

```text
Shared repository objects/refs/config
  -> task A: worktree A + branch A + index A + working tree A
  -> task B: worktree B + branch B + index B + working tree B
  -> coordinate ownership before overlapping shared/generated writes
```

- **EF:** worktrees isolate filesystem and operation state, not all Git state or
  configuration (GIT-F03, GIT-F16).
- **EF:** Codex provides separate threads and built-in worktrees (OAI-F01).
- **UC:** OpenAI does not publish a complete task-snapshot-to-Git mapping;
  therefore app isolation alone is not proof of branch/ref safety
  (UNRESOLVED-OAI-01–03).

### Integration

**PO — current canonical-practice sequence (OBS-06), recorded as an observation
rather than selected here as the future integration model:**

```text
Refresh -> establish exact candidate/base -> verify required checks
-> choose merge mechanism -> integrate -> capture resulting identity
-> verify reachability and, when history changed, patch equivalence
```

- **EF:** squash/rebase/merge create different commit identities (GH-F05).
- **EF:** required checks bind to the latest relevant SHA (GH-F01–F02).
- **UC:** current-base requirements, merge queue, auto-merge, and accepted merge
  methods remain governance choices (GH-F03, GH-F06–F07).

### Release

**PO — current canonical-practice evidence chain (OBS-09), recorded as an
observation; GIT-001 does not authorize any release:**

```text
Verified source commit -> exact tag object -> artifact build/test identity
-> deployment/environment gates -> GitHub release object/assets
-> public receipt and retained evidence
```

- **EF:** tag identity, GitHub release identity, and deployment environments are
  separate surfaces (GIT-F18, GH-F08–F09).
- **PO:** current repository release policy has additional artifact and owner
  authorization gates; this research does not alter them (OBS-09).
- **UC:** tag signing, immutable releases, and environment configuration remain
  later decisions.

### Cleanup

**PO — current disposition sequence (OBS-08), recorded as an observation; no
cleanup target or action is authorized by this map:**

```text
Refresh -> classify ownership/unique work -> prove reachability and patch state
-> obtain exact approval -> remove worktree -> delete local ref if authorized
-> delete remote ref only if separately authorized -> verify inventory
```

- **EF:** worktree removal, branch deletion, remote deletion, pruning, and clean
  are different actions (GIT-F03, GIT-F07–F08, GIT-F10, GIT-F15).
- **EF:** Codex chat archive/delete is separate from Git retention (OAI-F03).
- **UC:** the published Codex documentation does not define managed-worktree
  cleanup on archive (UNRESOLVED-OAI-02).

### Recovery

**PO — current canonical-practice sequence (OBS-06, OBS-10), recorded as an
observation rather than a universal recovery algorithm:**

```text
Stop mutation -> identify operation/state/owner -> preserve recoverable evidence
-> choose the state-specific action -> verify tree/history/outcome
-> publish or retain receipts -> only then resume or clean up
```

- **EF:** merge/rebase/sequencer markers and continue/abort/quit actions are
  operation-specific (GIT-F11–F13).
- **EF:** reset, restore, stash, clean, reflog, and revert affect different state
  surfaces and have different loss/recovery properties (GIT-F05, GIT-F13–F17).
- **PO:** the PMM and PR #723 cases are project evidence for preservation-first,
  selective outcome recovery (OBS-10).
- **UC:** no single recovery command is accepted as universally safe.

## Hold-state evidence matrix

| Observed state | What is factually unknown or at risk | Minimum evidence before a later decision | Label |
|---|---|---|---|
| Detached `HEAD` | Which ref, if any, should retain new commits | Exact `HEAD`, reflog, intended owner/ref | EF + UC |
| Dirty index/working tree/untracked paths | Ownership and durability of content | Per-path classification and diff/status evidence | EF + UC |
| Missing/wrong upstream | Intended publication and comparison ref | Branch config plus remote-ref inspection | EF + UC |
| Behind/diverged branch | Integration method and conflict/outcome risk | Fetch, graph, patch-equivalence, ownership | EF + UC |
| Merge/rebase/cherry-pick/revert in progress | Operation-specific continuation or cancellation effect | Git-path markers, staged conflict entries, operation docs | EF + UC |
| Reviewed PR with changed head/base | Whether prior checks/review still bind | Latest head/base SHA and required-check state | EF |
| Squash/selective recovery history | Whether intended patch exists despite ancestry mismatch | PR receipt plus patch-equivalence/range comparison | EF + PO |
| Cleanup candidate | Whether unique work or external task ownership remains | Clean/attached/ref/PR/reachability/patch/owner evidence | EF + UC |
| Release candidate | Whether tag, artifact, checks, and release object identify the same source | Exact hashes, tag object, artifact proof, environment/release receipt | EF + UC |

## Not-applicable findings for the current topology

- **NA:** submodule lifecycle is not part of the current repository topology;
  `git submodule status` returned no entries on 2026-08-12 (GIT-F19, OBS-01).
- **NA:** shallow-history restrictions do not apply to the inspected checkout;
  `--is-shallow-repository` returned `false` (GIT-F19, OBS-02).
- **NA:** partial-clone missing-object behavior does not apply to the inspected
  checkout; no promisor/partial-clone configuration was found (GIT-F19, OBS-02).

## Phase 1 boundary result

The factual map covers normal work, parallel work, integration, release,
cleanup, and recovery. It keeps external facts, current project observations,
not-applicable topology, and unresolved choices visibly separate. Two
independent read-only coverage reviews passed after requiring explicit PO
labels and traceable OBS evidence for every local claim. Phase 1 is complete;
no Phase 4 policy, cleanup action, GitHub setting, or release is authorized.
