# Session Log

> Append-only decision log for AI agent sessions.
> Earlier sessions (1-100): [SESSION_LOG_through_session_100.md](_archive/SESSION_LOG_through_session_100.md)

---

## 2026-08-22 — Session: E1 complete review-bundle export

**Agent:** Codex (`reviewer`, sole writer)

**Branch:** `codex/e1-review-bundle-export`, stacked on exact Windows-validated
predecessor `514155b266af6dff3e30bf39ee28671c17345454`.

**Git handoff receipt:** `docs/verification/e1-review-bundle-export-git-handoff-receipt.json`

**Focus:** Close the G3 export-surface gap with one complete, deterministic,
fail-closed Python/REST/Office.js successor; preserve workbook bytes,
calculations, manifest, ETABS/VBA, release, merge, cleanup, and professional
approval boundaries.

### Summary

- Added a versioned complete review-bundle request/result contract and
  deterministic JSON serialization.
- Added a same-origin REST attachment whose file, logical bundle, and canonical
  result identities are explicit.
- Added an installed-pane Export control that is eligible only after a current
  run or explicit freshness check and verifies response bytes before download.
- Extended focused Python, REST, Office.js, source-free wheel, plan, evidence,
  and Windows acceptance surfaces.

### Issues encountered

- The frozen G3 journey required pane-accessible deterministic review-bundle
  export, but the installed pane and REST router exposed no export operation.
- The existing deterministic Markdown renderer was a compact status summary;
  it omitted the complete mapping, structured results, passports, raw ledger
  detail, and issues required for qualified review.
- The first OpenAPI assertion found the new route documented no response
  content even though its runtime JSON attachment passed.
- The first affected-file Ruff run stopped before mypy because two new service
  contract imports were not in canonical order.

### Root causes and resolutions

- Confirmed root cause: local renderer determinism had been accepted as proof
  of a complete installed Excel export journey even though no source-to-pane
  route existed. Resolution: add one typed export request, service regeneration
  boundary, raw JSON attachment route, pane action, and exact identity checks.
- Confirmed root cause: the old renderer was designed as a human-readable
  summary and its tests asserted repeatability plus hash presence, not complete
  artifact content. Resolution: make `ExcelReviewBundleV1` contain the full
  canonical run result, preserve the renderer as a summary-only compatibility
  surface, and add nested-content plus deterministic-byte tests.
- Confirmed root cause: setting generic `Response` as the decorator response
  class suppressed FastAPI's schema content even with a response model.
  Resolution: keep `ExcelReviewBundleV1` as the documented response model and
  return a raw `Response` instance only at runtime. Proof: the failed OpenAPI
  assertion and refreshed 89-endpoint/434-schema baseline check pass.
- Confirmed root cause: the new retained/export contract imports were added in
  semantic rather than Ruff alphabetical order. Resolution: reorder only those
  imports; affected Black/Ruff and the previously skipped configured mypy pass.

### Validation through content freeze

- Focused Python/REST/Open XML: 22 cases pass using one impact-mapped repair
  rerun; Office.js: 21/21; four JavaScript modules and the manifest parse.
- Black, Ruff, configured mypy, 217-file architecture, 685-file/4,732-import
  validation, and the 89-endpoint/434-schema OpenAPI baseline pass.
- A source-free wheel proves unchanged workbook SHA-256 `497dd44d…ac85`, new
  library content identity `87ae4fbe…d57a5`, and complete deterministic 8,987-
  byte review evidence with both structured result and passport.
- Documentation, maintained indexes, quick gate, hooks, immutable commit/audit,
  hosted checks, and Windows G3 remain in the closeout sequence.

## 2026-08-22 — Session: E1 blank-workbook guard repair

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/e1-blank-workbook-guard`, stacked on
`codex/e1-w0-maintenance-plan` at
`654e40b1370d098fca4d001146a030b9937536a8`.

**Git handoff receipt:** `docs/verification/e1-blank-workbook-guard-repair-git-handoff-receipt.json`

**Focus:** Diagnose the exact Windows blank-workbook pane failure, repair only
the Office.js startup boundary, freeze local evidence, and leave G3 and all
ETABS/VBA work held.

### Summary

- Recovered the long Windows W0 task, completed the restricted SMB/trusted-
  catalog setup, and loaded the exact E1 add-in from `SHARED FOLDER`.
- Moved the new source diagnosis into a fresh, read-only Windows task and bound
  it to E1 head `ef5ee05c` and tree `30d8eb79`.
- Added a guarded, testable Office.js workbook-surface boundary that leaves
  blank/wrong workbooks read-only and keeps controls disabled.
- Preserved strict complete-workbook initialization and genuine Office/API
  failure reporting; no calculation, workbook, manifest, Python, ETABS/VBA, or
  G3 behavior changed.

### PRs Merged

- None.

### Key Deliverables

- `excel_addin/taskpane-office.mjs`
- `excel_addin/tests/taskpane-office.test.mjs`
- `docs/verification/e1-blank-workbook-guard-evidence.md`
- Updated W0/E1 evidence, task state, and next-session handoff.

### Issues encountered

- The exact trusted add-in loaded in a new blank workbook but stopped with
  `WORKBOOK CONTRACT ERROR — The requested resource doesn't exist` before its
  definition API request. This blocks W0 and therefore G3.
- The first remote task initially described the failure at the broad document-
  settings initialization stage because W0 did not capture `error.code`,
  `debugInfo`, or a JavaScript stack. Treating that visible message as the root
  cause would have repaired the wrong boundary.
- The first immutable repair head reached Windows with a new local module
  import but no matching `serve.mjs` route. `/taskpane-office.mjs` returned 404,
  leaving the pane at `INITIALIZING` and preventing the definition request.
- Closing the blank workbook produced a save prompt even though the missing
  module meant the repaired JavaScript never executed. Save-prompt presence is
  therefore not a reliable proxy for document-settings writes.

### Root causes and resolutions

- Confirmed root cause: startup saved/read the workbook ID, then
  `registerInputChange()` called `worksheets.getItem("Beam_Workbench")` in a
  blank workbook containing only `Sheet1`. The following `context.sync()`
  raised Office `ItemNotFound`; this documented error message and the source
  order match the observed pre-API failure. Resolution: inspect both the sheet
  and table with `getItemOrNullObject()` before any settings write/event
  registration, return the controlled `E1 WORKBOOK NOT OPEN` state when absent,
  and retain strict failures after the complete surface exists. Proof: 15/15
  Office.js tests, four JavaScript parse checks, manifest XML validation, and
  217-file architecture validation pass.
- Confirmed root cause of the initial broad attribution: the UI catch grouped
  settings, event registration, and API startup under one generic `WORKBOOK
  CONTRACT ERROR`, while the W0 receipt lacked runtime error metadata.
  Resolution: the read-only Windows source trace followed execution order and
  compared the blank workbook contents with Microsoft Office.js semantics;
  production now reports workbook check, local API, and strict workbook
  initialization failures separately and preserves Office code/debug location.
- Confirmed root cause of the Windows repair-load failure: `serve.mjs` uses an
  explicit static-file map, and the initial repair added a module import without
  adding its route. Resolution: serve `/taskpane-office.mjs` from the trusted
  origin and add a focused test that compares local `taskpane.mjs` imports with
  the server map. The original W2 receipt proves the 404 and clean shutdown;
  the consolidated local Office suite provides the repaired route evidence.
- Confirmed root cause of the misleading save-prompt criterion: inserting an
  Office add-in can itself dirty an unsaved workbook independently of document
  settings. Resolution: discard the W0 workbook and rely on exact code/test
  evidence plus the controlled visible state; record, but do not interpret, any
  close prompt.

### Notes

- The repair base and original E1 candidate remain clean and immutable.
- Windows revalidation must use the exact repair commit and reuse passing setup
  evidence; no broad rebuild or G3 work is authorized by this local result.


## 2026-08-21 — Session: E1 Windows W0 evidence and maintenance

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/e1-w0-maintenance-plan`, stacked on the immutable E1 head
`ef5ee05c785904e1a01c2d09cc65649edc8745ab`.

**Git handoff receipt:** `docs/verification/e1-w0-maintenance-git-handoff-receipt.json`

**Focus:** Record the completed Windows setup and legacy VBA/API handoff,
reconcile current library progress, run a non-destructive maintenance pass,
and freeze the next controlled work sequence.

### Summary

- Recorded W0 as `SETUP_BLOCKED`, with all entitlement, candidate, wheel,
  artifact, HTTPS, and loopback checks passing and one restricted SMB catalog
  share remaining before the blank-workbook add-in check.
- Preserved the 2019-2021 ETABS/VBA, exporter, structural-design, and legacy
  workbook bundles as historical reference evidence with hashes and explicit
  no-live-model/no-macro-execution boundaries.
- Verified live GitHub progress: PRs #822, #823, and #825 are merged; draft PR
  #826 is clean at the exact E1 head and all required hosted checks pass.
- Ran health, audit, parity, efficiency, feedback, source-binding, and local
  branch-disposition checks. Corrected four confirmed endpoint/router count
  drifts and preserved all uncertain lanes.

### PRs Merged
| PR | Summary |
|----|---------|
| None | This session did not merge or close a pull request. |

### Key Deliverables

- `docs/verification/e1-windows-w0-setup-evidence.md`
- Updated E1 evidence, task board, next-session brief, and four onboarding/API
  counts.
- Non-destructive cleanup result: 25 local non-default branches classify
  `HOLD_UNKNOWN_OWNER` without refreshed per-branch ownership, PR, remote-ref,
  and retention evidence; no branch, worktree, file, or stash was removed.

### Issues encountered

- The Mac controller lost readable access to the remote Windows Codex task,
  even though the task continued and completed on Windows.
- Documentation health found four stale endpoint/router counts after the recent
  API additions.
- Cleanup classification found 25 local branches without enough refreshed
  authority for safe retirement; one separate detached worktree is also dirty
  and remains preserved.
- The all-folder index audit found six stale aggregate indexes. Three were
  inherited from E1 (`Python/structural_lib`, `Python/tests`, and `fastapi_app`)
  and three reflected this session's documentation changes.
- The first normal commit hook rejected the rewritten next-session brief because
  its `Required Reading` heading used lowercase `reading`; the failed-only
  session check then exposed missing exact `Current` and `Next` table labels.
- The first clean exact-head session audit could not discover the valid handoff
  receipt because its path was wrapped onto the following line.

### Root causes and resolutions

- Remote disconnect root cause is `unconfirmed`. Completed Windows commands,
  clean Git, stopped services, and the final receipt localize the symptom to the
  Codex remote-control/task-visibility path rather than the build or candidate.
  The passing work is retained and will not be rerun; only the remaining catalog
  and blank-workbook checks will resume after the user action.
- E1 and preceding API work raised the maintained surface to 88 endpoints and
  26 routers, but four descriptive counts remained at 81/24. The four exact
  values were updated; direct `sync_numbers.py` and documentation checks provide
  the correction evidence.
- Branch age or apparent merge history is not retirement authority. Without
  current owner, PR, remote-ref, and retention receipts, the classifier correctly
  fails closed. All 25 branches and every existing worktree remain untouched;
  any destructive cleanup requires a separately reviewed proposal and explicit
  user authorization.
- E1 refreshed its directly changed nested indexes but did not refresh three
  maintained parent aggregate indexes whose hashes include those descendants.
  This session also changed three indexed documentation folders. Resolution:
  refresh exactly the six reported stale folders plus `docs/verification` for
  its newly added evidence; the final all-folder read-only check must report
  32/32 current.
- The session checker intentionally treats the exact `Required Reading` heading
  and `Current`/`Next` table labels as a machine-readable handoff contract.
  Resolution: restore those canonical tokens without losing the clearer W0/G3
  content, refresh only the affected docs/planning and docs indexes, and rerun
  the failed check before the normal commit hooks; all other first-pass hooks
  had passed.
- The session-end receipt parser requires the label and tracked path on the same
  line. Resolution: bind the existing valid receipt on that line and create a
  minimal repair commit after refreshing only the root docs index; no product,
  Windows, G3, or ETABS evidence was repeated.

### Notes

- Health initially reported 94/100 only because of the four stale numbers;
  code, agents, infrastructure, and feedback were 100/100.
- Audit was 21/22 with one non-blocking function-quality diagnostic warning;
  parity showed 88/88 endpoint tests and 13/13 React hook connections.
- ETABS snapshot/live work, Excel G3, repository publication, release, and
  professional approval were not run.


## 2026-08-18 — Session: E1 Excel Routine Workbench V1 implementation

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-excel-routine-workbench`.

**Git handoff receipt:** `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`

**Focus:** Implement the frozen E1 selected-table rectangular-beam workflow,
including strict intake and row reconciliation, canonical Python/CLI/REST
results, calculation passports and freshness, one macro-free workbook, a
bounded Office.js task pane, installed-wheel artifact identity, documentation,
and evidence. ETABS file/live work, write-back, optimization, nightly work,
release, and professional approval remain excluded.

### Summary

- Implemented the strict selected-table Python/CLI/REST workflow, canonical row
  ledger, calculation passports, four-hash freshness, and explicit capability
  truth without adding a second structural calculation path.
- Packaged and verified one macro-free six-sheet workbook plus a bounded
  Office.js task pane; focused tests, source-free wheel proof, documentation,
  quick gates, and normal commit hooks pass.
- Retained `TO_VERIFY_WINDOWS` for the separate installed Windows Excel G3 cell
  and held ETABS, write-back, optimization, release, and approval work.

### Issues encountered

- The previous session's time-bounded Git handoff evidence had expired before
  implementation resumed.
- The first header mapper case-folded structural notation `D` and `d`, so seven
  of ten new service vectors were blocked as duplicate mappings.
- Two first-pass REST cases asked pytest for an `unwrap` fixture although the
  maintained helper is an ordinary function.
- The artifact patch helper created its temporary builder under the primary
  checkout instead of the visualization workspace, and the E1 safe-move script
  could not move a file whose source was outside the current worktree.
- The first workbook's placeholder row populated both categorical dropdown
  cells, so it was not a blank row and would have become `BLOCKED` instead of
  explicitly `EXCLUDED`. Its first render also expanded the input sheet to 204
  rows and cramped the information-sheet workflow text.
- The first workbook location was a repository output outside Python package
  data, so a built wheel could not prove or expose the exact artifact.
- Retaining the complete result bundle in Office document settings would scale
  poorly for a large selected table even though full evidence already persists
  in workbook tables.
- The first frozen architecture/import commands used guessed script names, and
  root-level mypy saw the same module through both `Python.structural_lib` and
  `structural_lib` package identities. The corrected mypy run then exposed
  literal, inherited-schema, and untyped-constructor weaknesses.
- The root `Excel/` ignore rule also matched the lower-case installed package
  data directory on the default macOS filesystem, hiding the workbook and its
  manifest from an ordinary Git add.
- The first strict documentation closeout rejected descriptive E1 front-matter
  values even though all E1 links and the repository quick gate passed.
- The first normal commit hook run rejected the new session order and the new
  wheel verifier's missing automation-map registration.
- The first immutable read-only session audit could not find completion items
  or the Git handoff receipt in the newest E1 entry.

### Root causes and resolutions

- Confirmed root cause: the start receipt intentionally expires and cannot be
  reused as current authorization. Resolution: bind fresh user continuation to
  exact branch head `64f3518a`, regenerate the handoff receipt, and validate it
  before writes. Evidence: the receipt validator returned valid `HOLD` with the
  E1 task authority and unchanged base.
- Confirmed root cause: case folding erased the semantically significant
  uppercase/lowercase depth distinction. Resolution: preserve exact `D_mm` and
  `d_mm` aliases before folded aliases. Evidence: all 13 consolidated Python
  E1/workbook cases pass, including PASS/FAIL/HOLD/blocked and mapping vectors.
- Confirmed root cause: the new REST file copied a fixture-style call pattern
  for a helper exported from `fastapi_app.tests.conftest`. Resolution: import
  and call the helper directly. Evidence: all three consolidated REST cases
  pass.
- Confirmed root cause: `apply_patch` is rooted at the desktop session workspace,
  not the per-command shell workdir, and `safe_file_move.py` intentionally
  rejects cross-worktree sources. Resolution: run the generated builder only
  from the exact temporary primary path, verify the output, safely delete the
  one untracked builder, validate and unlink only its known dependency symlink,
  and recheck the primary checkout. It is clean. ⚠️ TERMINAL ISSUE: patch
  workdir assumption placed one temporary file in the primary checkout -> used
  exact-path cleanup and prefixed all later E1 patches with the linked-worktree
  path.
- Confirmed root cause: preset dropdown values are data, and formatting/data
  validation across 200 unused rows expanded the workbook used range.
  Resolution: leave the placeholder's 17 cells null, retain validation only on
  the compact three-row table, widen/wrap the workflow panel, and visually
  inspect all six final renders. Open XML checks prove the exact sheets/tables,
  no formulas, no formula errors, and no VBA/macros.
- Confirmed root cause: root `outputs/` is not inside the setuptools package
  tree. Resolution: move, do not copy, the single workbook and manifest into
  maintained package data and make the definition service verify installed
  bytes, size, and SHA-256. The repaired source-free wheel contains the exact
  workbook and reports canonical PASS for one installed-package row.
- Confirmed root cause: complete row ledgers and result JSON grow with table
  size, while freshness needs only bundle, source-table, mapping, and engine
  identities. Resolution: persist those four hashes plus the stale flag and
  workbook ID in Office settings; keep full ledgers, results, and passports in
  their named worksheets. The focused Python, REST, and seven Office.js tests
  pass.
- Confirmed root cause: the maintained commands are
  `check_architecture_boundaries.py` and `validate_imports.py`, and configured
  mypy requires the `Python/` package workdir. Resolution: correct the frozen
  evidence commands, then fix the real type roots with literal-final constants,
  a standalone run-request schema, and a direct typed result constructor.
  Evidence: 217 architecture files have zero violations, 685 Python files have
  zero broken imports, and mypy reports no issues in both new modules.
  ⚠️ TERMINAL ISSUE: guessed architecture/import script paths and root-level
  mypy failed -> discovered the registered commands and ran mypy from `Python/`.
- Confirmed root cause: Git's case-insensitive path matching on the current
  filesystem applied the broad `Excel/` output ignore to the new lower-case
  package-data path. Resolution: force-stage only the exact verified workbook
  and manifest; once tracked, later changes remain visible normally. Evidence:
  `git ls-files --stage` lists both exact package-data paths and their SHA-256
  values remain bound by the workbook manifest and artifact verifier.
- Confirmed root cause: the three new E1 documents used human-readable workflow
  states where the maintained checker accepts only its controlled `status` and
  `doc_type` vocabularies. Resolution: retain the exact software-candidate/G3
  hold in document content while using `status: active` and the supported
  `spec`/`log` document types. The failed-only strict documentation rerun and
  impact-mapped quick gate are the repair evidence.
- Confirmed root cause: the implementation session was appended after older
  entries even though the maintained checker requires newest-first ordering,
  and adding a maintained script requires both its generated index and the
  hand-maintained automation map. Resolution: move only the new E1 session to
  the top and register the verifier as a read-only Testing task with exact-wheel
  usage. The two failed hook checks and impact-mapped quick gate are the repair
  evidence; no calculation suite is repeated.
- Confirmed root cause: the audit parser recognizes completed work only below
  `### Summary` or `**Completed:**` and discovers a receipt only from the exact
  bold label in the same newest session block. Resolution: add those two
  machine-readable boundaries without changing any implementation or evidence
  claim. The failed-only session check and exact-head read-only audit are the
  repair proof.

### Validation through content freeze

- Focused Python workbook/service/CLI/Open XML: 13 passed; focused REST: 3
  passed; Office.js: 7 passed plus syntax and XML parsing; advertised-command
  UAT: passed.
- Architecture: 217 files, zero violations. Imports: 685 files and 4,729
  imports, zero broken. OpenAPI: 88 endpoints and 432 schemas match baseline.
  Black and Ruff pass on every changed Python path; configured mypy passes both
  new source modules.
- Repaired source-free wheel SHA-256:
  `c4c5d09872d080ac5b1bee9e72c5af87e52df65c893358a15cc478cc4b5753b9`;
  installed library content identity:
  `6b2d8f43c4fecd8eaa0c3ec692db13db4118ac04fe141458307e114421ab1764`;
  workbook SHA-256:
  `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85`.
- Documentation/index, quick gate, normal hooks, immutable session audit, push,
  and hosted validation remain the closeout sequence. The supported real
  Windows Excel journey remains `TO_VERIFY_WINDOWS`, so Gate G3 is held.

## 2026-08-17 — Session: v0.23.1a2 Release Candidate Preparation

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/release-0231a2` from synchronized
`main = 970a78c1931a3aa0439f487e6892a888bb113962`

**Local evidence:** `docs/verification/alpha-0231a2-local-prepublication-rehearsal.md`

**Git handoff receipt:** `docs/verification/release-0231a2-preparation-git-handoff-receipt.json`

**Focus:** Prepare and locally verify the exact v0.23.1a2 Alpha candidate with
one source-bound wheel, while keeping TestPyPI, PyPI, tag, GitHub Release,
whole-building, professional-approval, and retained-lane actions explicitly
unauthorized.

### Summary

- A fresh linked worktree was created from live GitHub `main`; it reported
  `READY_LOCAL`, `source_bound=true`, and no open PR overlap. All retained
  detached, dirty, and historical lanes were preserved unchanged.
- The canonical release preparation changed source/package/documentation
  version surfaces from `0.23.1a1` to `0.23.1a2`, retained the published
  `v0.23.1a1` evidence, and added bounded candidate release notes.
- The preparation gate passed 6,414 Python tests with 3 skipped and 6
  deselected, then passed the repository-pinned Node 24 React production build.
- Repaired build anchor `a115b16efbb85db0459c79836f55b6c43a586470`
  produced one wheel and matching sdist. The wheel is 665,658 bytes with
  SHA-256 `34892d867845d044249236f32b700ab5e10ec558225407a47717fe3c3c2614bb`.
- The clean installed-wheel verifier passed 5,553 tests with 51 skipped and 2
  deselected plus installed `job`, `critical`, and HTML `report` workflows.
- The narrow exact candidate check passed the 29-case matrix, all 12 advertised
  commands, public examples, content/version boundaries, and clean installed
  package-origin assertion against the same wheel hash.
- Candidate wording is historical and explicit: at freeze it is not tagged or
  published. The current public Alpha remains `0.23.1a1`; publication and
  professional approval remain separate holds.

### Issues encountered

- The release-preflight skill instructed maintainers to record a checked
  publication authorization in the checklist before immutable review.
- The general installed-wheel verifier passed its broad package suite and
  legacy CLI workflows but did not execute the newer 29-case advertised-command
  release matrix.
- Version synchronization printed optional-pattern warnings for source files
  that deliberately do not contain those optional tag/metadata forms.
- The first direct index-generator command guessed the retired
  `scripts/generate_folder_indexes.py` path and stopped before any write.
- Exact-head Weekly Verification run `32006071604` passed the clean-wheel,
  Python, FastAPI, benchmark, Docker, and dependency stages, then stopped in
  documentation drift because `fastapi_app/index.json` was stale; React was
  skipped after that failure.
- The first repair closeout invocation passed two folder arguments to the
  single-folder index command; argument parsing stopped before either write.
- The first authorized exact-wheel publication preflight passed clean-wheel
  UAT, 6,413 Python tests, FastAPI, React, docs, and version checks, but one
  release test failed because it read the live authorization record after the
  owner correctly changed that record from `HOLD` to `AUTHORIZED`.
- A read-only generated-artifact inspection loop used the zsh variable name
  `path`, after which standard commands in that loop were reported as missing;
  the failed inspection made no writes.

### Root causes and resolutions

- Confirmed root cause: the skill retained the earlier checklist-marker
  authorization sequence after publication authority moved to the exact JSON
  authorization plus immutable review-receipt flow. Resolution: candidate
  preparation now requires unpublished/on-hold wording and forbids pre-checking
  tag/publication approval; post-review authorization is routed only through
  validator-permitted exact evidence. Proof: focused release-document checks,
  14 release environment/version regressions, and normal commit hooks pass
  while the v0.23.1a2 publication checkbox remains open.
- Confirmed root cause: `release verify` and `release candidate-check` have
  distinct maintained responsibilities; only the latter invokes packaged
  `structural_lib.release_uat`. Resolution: run the broad verifier once, then
  the narrow candidate check once without replaying manual CLI cases. Proof:
  both commands exit zero against wheel SHA-256 `34892d86...14bb`; the packaged
  matrix contains 29 cases and the advertised inventory contains 12 commands.
- Confirmed root cause: the version synchronizer reports absent optional regex
  forms even when all required candidate surfaces agree. Resolution: inspect
  the intended surfaces once and rely on `--check-docs`, release-doc checks,
  exact candidate validation, and commit hooks; no non-outcome tooling change
  was added. Proof: every maintained check exits zero and the warnings identify
  only non-applicable optional forms.
- Confirmed root cause: the direct script name was guessed instead of using the
  maintained `run.sh generate indexes <folder>` entry point documented by the
  live launcher. Resolution: discover the current command with `rg --files`
  and use only targeted dry-run/final refresh calls. Proof: the guessed command
  made no write; final affected-folder index checks pass. ⚠️ TERMINAL ISSUE:
  nonexistent direct generator path -> maintained targeted `run.sh` command.
- Confirmed root cause: release preparation changed `fastapi_app/__init__.py`,
  `fastapi_app/config.py`, and `fastapi_app/openapi_baseline.json`, but the
  affected-folder index refresh omitted `fastapi_app`. Resolution: regenerate
  only `fastapi_app/index.json`; do not rebuild or repeat wheel UAT because the
  Python package tree and exact wheel are unchanged. Proof: the exact failing
  command, `scripts/generate_enhanced_index.py --all --check`, reports all
  32 maintained indexes current before the single repair commit is pushed.
- Confirmed root cause: the maintained targeted generator accepts one optional
  positional folder, not a folder list. Resolution: invoke it once for `docs`
  and once for `docs/verification`; both targeted refreshes pass. ⚠️ TERMINAL
  ISSUE: combined two-folder index refresh -> separate maintained invocations.
- Confirmed root cause: `test_release_publication_authorization_holds_by_default`
  tested the mutable repository authorization record instead of an isolated
  default-HOLD fixture, making a genuine authorization state fail the release
  suite by construction. Resolution: create a temporary HOLD record inside the
  test and pass it explicitly to the validator. Evidence: the focused
  regression passes for the isolated HOLD state while the live three-target
  authorization checks remain reserved for the refreshed reviewed candidate.
- Confirmed root cause: zsh reserves `path` as an array tied to `PATH`, so the
  loop assignment replaced command lookup for that shell process. Resolution:
  rerun the inspection with the task-specific variable `release_artifact` and
  absolute command paths, then move only the inspected ignored, non-symlink
  build directories recoverably before the clean rebuild. Evidence: the
  corrected inspection identified exactly `Python/dist` and
  `Python/structural_lib_is456.egg-info`; the clean build, candidate check, and
  installed-wheel verifier all passed. ⚠️ TERMINAL ISSUE: zsh special variable
  `path` shadowed `PATH` -> task-specific variable plus absolute commands.

### Validation through local candidate freeze

- Live base/GitHub: `main = 970a78c1`; no open PRs; release worktree
  `READY_LOCAL`; `source_bound=true`.
- Focused release environment/version regressions: 14 passed.
- Canonical release preparation: 6,414 passed, 3 skipped, 6 deselected; React
  production build passed.
- Normal build-anchor commit hooks: all passed.
- Rebuilt exact installed wheel: SHA-256 `34892d86...14bb`; 5,553 passed, 51
  skipped, 2 deselected; installed CLI workflows passed.
- Exact candidate: 29/29 UAT cases and 12/12 advertised commands passed.
- Final affected indexes, quick 10/10, immutable final commit, hosted checks,
  and exact-head review complete in the next closeout stage. The exact-wheel
  publication preflight is intentionally reserved for the reviewed and
  authorized target identity.

### Timing through local candidate freeze

- Orientation, release controls, and lane creation: approximately 2 minutes.
- Canonical preparation, release-document correction, and focused checks:
  approximately 6 minutes.
- Exact build, installed verification, candidate UAT, and evidence recording:
  approximately 5 minutes.
- Hosted CI/review wait and final closeout are not included here.

## 2026-08-17 — Session: LIB-PRO-002-J Release Signal Convergence

**Agent:** Codex (`ops`, sole writer)

**Branch:** `codex/lib-pro-002-j-release-signal` from Packet I merge
`origin/main = 0ba2f397aec267bc74a31281f9158189fde2749d`

**Git handoff receipt:** `docs/verification/lib-pro-002-j-closeout-determinism-git-handoff-receipt.json`

**Focus:** Bind scheduled/tag full suites to the interpreter selected by
`actions/setup-python`, replace the preflight's shared release-ready label with
mode-accurate preparation/candidate/publication verdicts, and require exact-head
hosted receipts before publication readiness. Do not build a wheel, bump a
version, tag, publish, authorize targets, or activate Packet H; exact artifact
steps 3 and 4 are reserved for the next session at the owner's request.

### Summary

- Weekly Verification and publish validation now pass the exact setup-python
  executable through the supported `STRUCTURAL_LIB_PYTHON` contract when their
  full Python suites execute launcher-dependent tests. The strict launcher was
  not weakened and no bare-system fallback was introduced.
- Preflight now reports `READY_TO_PREPARE_CANDIDATE` without a wheel,
  `CANDIDATE_TECHNICALLY_READY` plus `PUBLICATION_HOLD` after exact-wheel/UAT
  success without complete publication evidence, `NOT_READY` on technical
  failure, and `READY_TO_PUBLISH` only for an exact authorized target.
- Candidate-wheel preflight now runs the packaged source-free release UAT and
  public examples in the disposable clean-install environment rather than
  treating metadata/import/CLI help alone as technical candidate evidence.
- The exact-candidate review receipt now binds passing required PR checks and
  Weekly Verification to the reviewed head. Wrong/missing hosted status, head,
  or run URL blocks publication readiness.
- The next-session brief records the owner's requested boundary: step 3 builds
  one temporary technical-acceptance wheel from unchanged synchronized `main`;
  step 4 clean-installs and verifies that same hash. Neither step authorizes a
  new version or publication.
- Maintained index dates now follow content identity instead of checkout mtime,
  and no-op generation skips disk writes. Session preparation no longer hides
  index generation or presents a pre-mutation Git snapshot as a final verdict;
  logs/tasks/receipts freeze first, affected indexes refresh once, and the last
  session check is read-only.

### Issues encountered

- Hosted Weekly Verification run `31988837003` had failed six otherwise valid
  governance/session tests because their recursive repository launchers could
  not resolve a project Python, while the publish full-suite step contained the
  same latent environment gap.
- A zero-error pre-bump run with no wheel, exact review, hosted receipt, or
  target authorization printed `READY TO RELEASE`, conflating permission to
  prepare a candidate with permission to publish.
- The exact-review receipt template and validator did not record hosted checks,
  so the future publication verdict could not machine-prove the plan's required
  exact-head PR and Weekly Verification evidence.
- The first post-implementation formatting check found one deterministic Black
  wrapping change in `scripts/release.py`; tests already passed, but the Python
  candidate was not yet format-frozen.
- The first focused index refresh again rewrote historical `last_updated` values
  for unchanged files in the fresh linked worktree, producing unrelated
  generated diff churn before the candidate freeze.
- The first React-suite command stopped before collection because the fresh
  Packet J worktree had no `react_app/node_modules`, so `vitest` was not found.
  No test executed and the attempt was not accepted as React evidence.
- Final semantic review found that the CLI still permitted two contradictory
  combinations: a future pre-bump positional version together with an exact
  current-source wheel, or a publication target without any wheel evidence.
- The first normal commit-hook run rejected the rewritten handoff because its
  `Required Reading` heading capitalization no longer matched the session
  checker's exact required contract. No commit was created.
- Manual Weekly Verification run `31998565603` passed dependency, clean-wheel,
  Docker, Python-coverage, and FastAPI work, then failed documentation drift;
  React was skipped and the summary correctly failed. Required PR checks had
  passed, so the Packet J head was not merged.
- The previous index-determinism repair excluded `last_updated` from freshness
  hashes but left every displayed file date sourced from filesystem mtime. A
  fresh linked worktree therefore still rewrote many byte-level projections
  even while `--check` correctly reported their content hashes current.
- `session end --fix` silently invoked the index generator from the dirty-path
  snapshot captured before its own handoff/task writes. It could therefore miss
  newly changed folders, mutate indexes before all source docs froze, and print
  a safe-closeout message from the earlier Git snapshot.
- The first durable freeze wording placed the final read-only `session end`
  before the candidate commit, but that command correctly treats intended
  uncommitted changes as a failed closeout. Following the wording would make a
  successful final verdict impossible.
- Active handoff guidance still required every new candidate to record its PR
  number inside `SESSION_LOG.md`, although the number normally does not exist
  until after the first push. That requirement itself forced a status-only
  post-PR rewrite and another index/CI cycle.
- Independent read-only review rejected the first closeout repair because a
  clean pre-mutation `session end --fix` could write the handoff and still exit
  `0`. The text said preparation-only, but machine callers could still accept
  the process status as final success.
- No Git, worktree, or Python interpreter-binding issue occurred in Packet J.

### Root causes and resolutions

- Confirmed root cause: `actions/setup-python` changes the workflow `python`
  path but does not create a repository `.venv` or set `VIRTUAL_ENV`; the full
  suites recursively invoke `run.sh`/`python_runtime.sh`, whose fail-closed
  contract accepts `STRUCTURAL_LIB_PYTHON` instead of guessing a system
  interpreter. Resolution: prefix the Weekly and publish full pytest commands
  with `STRUCTURAL_LIB_PYTHON="$(command -v python)"` and enforce both exact
  workflow steps in repository tests. Evidence: the focused workflow contract
  passes and the launcher remains unchanged.
- Confirmed root cause: `cmd_preflight` selected its final text only from the
  aggregate technical error count; wheel, review, hosted, target, and owner
  authorization states did not participate. Resolution: centralize a pure
  mode-specific verdict contract, add optional exact target evaluation, and
  print every remaining publication hold. Evidence: parameterized tests cover
  technical failure, missing wheel, technically ready/no target, authorization
  HOLD, and fully authorized publication with their exact exit codes.
- Confirmed root cause: clean-wheel preflight ran metadata inspection, import,
  and CLI help but not the packaged negative UAT/public examples. Resolution:
  run `structural_lib.release_uat --require-installed-wheel` inside the same
  disposable source-free environment before technical readiness. Evidence: a
  focused source contract test requires that exact invocation; live artifact
  execution is intentionally deferred to next-session step 4.
- Confirmed root cause: authorization validated an independent review receipt
  but the receipt schema contained no hosted evidence. Resolution: require
  `required_pr_checks` and `weekly_verification` PASS records, GitHub Actions
  URLs, and head SHAs equal to the reviewed candidate. Evidence: the valid
  authorization fixture passes and a mismatched Weekly head is rejected.
- Confirmed root cause: the new verdict helper and summary branch exceeded
  Black's canonical wrapping shape. Resolution: run Black on the one reported
  source file only. Evidence: the repeated 103-test selection, Black, Ruff, and
  `git diff --check` all pass.
- Confirmed root cause: the earlier hash repair treated `last_updated` as
  observation-only but every analyzer still recomputed that field from
  filesystem mtime, and writers always rewrote both projections. Resolution:
  date new/changed entries at generation, preserve prior entry dates by raw-file
  content hash and the folder date by deterministic projection hash, and skip
  byte-identical writes. Evidence: regressions change both checkout mtime and
  generation date yet retain byte-identical JSON/Markdown, while a content
  change at the same mtime advances both dates and changes the hash.
- Confirmed root cause: `session end --fix` mixed preparation, index mutation,
  and final validation while relying on one pre-mutation Git snapshot.
  Resolution: remove its index-generator call, label it preparation-only, make
  the final safe verdict available only without `--fix`, and encode the exact
  log/task/receipt -> one index refresh -> read-only validation order in agent
  and contributor instructions. Evidence: the session regression observes the
  canonical dirty paths, proves no generator subprocess is invoked, and proves
  preparation mode cannot print `Safe to end session`.
- Confirmed root cause: the freeze policy named the final repository write but
  did not explicitly place the immutable local commit before the clean-tree
  validation. Resolution: encode one unambiguous sequence everywhere:
  freeze sources/receipt, refresh affected indexes, commit locally, run plain
  `session end` read-only, then push unchanged. Evidence: the final command is
  now evaluated only against a clean committed candidate, while every later
  hosted/merge fact remains external.
- Confirmed root cause: the older continuity rule treated a future GitHub PR
  identifier as required versioned session content instead of external status.
  Resolution: include a PR number only when it is already known before freeze;
  never rewrite a candidate solely for a new PR number, hosted result, or merge
  hash. Evidence: all active onboarding/closeout guidance and the retained
  deprecated example now state the same no-rewrite boundary.
- Confirmed root cause: `cmd_end` changed its human message for `--fix` but left
  the shared `0 if all_passed else 1` return branch unchanged. Resolution: an
  otherwise passing preparation exits distinct status `2`; only plain read-only
  validation can exit `0`. Evidence: the new clean-state regression simulates a
  successful handoff write, requires exit `2`, and forbids the final safe text;
  the dirty preparation path continues to exit `1`.
- Confirmed root cause: linked worktrees share Git objects but not ignored
  dependency directories, and `./run.sh test --react` intentionally executes
  the pinned test command without installing packages. Resolution: select the
  repository's healthy pinned Node 24 runtime, run `npm ci` from the lockfile in
  the Packet J worktree, then execute the unchanged React command. Evidence:
  48 files and 267 tests pass.
  ⚠️ TERMINAL ISSUE: `vitest` was unavailable in the fresh worktree -> installed
  lockfile dependencies with pinned Node 24, then reran the actual React suite.
- Confirmed root cause: parser arguments represented independent options while
  verdict modes are mutually exclusive; no cross-option contract rejected the
  contradictory combinations. Resolution: add an explicit mode validator so
  future-version checks remain pre-bump-only and publication-target evaluation
  requires an exact wheel. Evidence: four mode-combination regressions pass and
  both contradictory modes return `NOT_READY` through the normal error path.
- Confirmed root cause: the handoff rewrite changed a machine-consumed heading
  from `Required Reading` to sentence case even though the session validator
  performs an exact heading match. Resolution: restore the canonical heading
  without changing the handoff content. Evidence: the repeated session-doc and
  normal commit-hook checks pass.
- Confirmed root cause: the scheduled/manual FastAPI benchmark saved its
  transient report into tracked `docs/reference` before the workflow ran the
  maintained index check. That outcome-changing write made
  `docs/reference/index.json` and parent `docs/index.json` stale on the hosted
  runner; it was unrelated to interpreter binding. Resolution: save and upload
  the report from `$RUNNER_TEMP`, leaving the indexed checkout immutable, and
  add a workflow regression forbidding the tracked path. Evidence: the focused
  workflow/release selection and local canonical gates pass; an exact-head
  Weekly rerun is required before merge.

### Validation through content freeze

- Startup: Packet I PR #819 passed required checks and merged unchanged at
  `0ba2f397`; primary `main` was clean/equal before a fresh Packet J linked lane
  was created from that exact commit.
- Source binding: Packet J reported `source_bound=true`, `READY_LOCAL`, clean
  tree, no operation marker, and equality with fetched `origin/main`.
- Focused Packet J release selection: 103 workflow-contract, release-script,
  and release-environment tests passed before the closeout repair. The added
  closeout/index regressions pass and are included in the final consolidated
  focused replay.
- Hosted-repair replay: the exact quick FastAPI benchmark saved a non-empty
  report under a fresh temporary directory, after which all 32 maintained
  indexes remained current; quick 10/10 and canonical 31/31 gates passed.
- Consolidated repository boundary: quick gate 10/10; Python 6,406 passed, 3
  skipped, and 6 deselected; FastAPI 452 passed; React 267 passed across 48
  files; the full canonical gate passes after content freeze; normal commit
  hooks pass on the immutable candidate.
- Exact wheel build and clean-install verification were not run because the
  owner explicitly assigned release-preflight steps 3 and 4 to the next
  session. Publication remains `HOLD`.

### Timing through content freeze

- Packet I hosted acceptance, exact-head merge, and primary synchronization:
  approximately 3 minutes.
- Packet J safe-lane orientation, root-cause trace, implementation, and focused
  proof: approximately 15 minutes.
- The cyclic closeout/index defect was accepted as an outcome-changing repair;
  final focused, quick/canonical, exact-head hosted, and merge closeout follow
  this new content freeze. No hosted/merge status-only repository write follows.

## 2026-08-17 — Session: LIB-PRO-002-I Advertised CLI Convergence

**Agent:** Codex (`backend`, sole writer)

**Branch:** `codex/lib-pro-002-i-cli` from freshly fetched
`origin/main = b3a9c367de012982a8b9adefda0db60e2d762d7b`

**Git handoff receipt:** `docs/verification/lib-pro-002-i-git-handoff-receipt.json`

**Focus:** Replace the advertised beam-design CLI's lossy/defaulting intake
with a fail-closed lossless/strict project boundary while retaining the
versioned `beams` output and its `bbs`, `detail`, and `dxf` consumers. Add the
advertised-entrypoint inventory and CLI cases to source-free release UAT. Do
not start Packet J, change formulas, bump a version, or publish.

### Summary

- Added one strict CLI design service. Generic CSV passes through the lossless
  import ledger; JSON rejects duplicate keys, non-finite constants, unsupported
  envelopes, unknown fields, alias conflicts, and empty projects.
- The entire project, including duplicate member identities and explicit
  effective-depth basis, validates before the first calculation call. Blocked
  input returns non-zero, writes no result, emits no partial PASS, and keeps
  stdout free of diagnostics.
- Retained output schema version `1` and its top-level `beams` envelope. Valid
  output remains accepted by BBS, detailing, and DXF consumers; the maintained
  sample and CLI guidance now provide complete explicit inputs rather than
  precomputed steel/status fields.
- Expanded packaged release UAT from 19 to 29 cases and bound all 12 live CLI
  commands to a packaged inventory classified as calculation entry, result
  consumer, inspection, or compatibility.
- Exposed a validation-only project-batch command so the CLI can prove whole-
  batch acceptance without performing the strict calculation and legacy
  compatibility calculation twice.

### Issues encountered

- The existing advertised `design` command silently skipped malformed CSV rows,
  supplied effective depth/cover values through legacy defaults, contaminated
  stdout with warnings, exited zero, and published a partial PASS artifact.
- The first worktree-creation command could not start because its execution
  working directory was the not-yet-created target path. No command ran and no
  repository state changed.
- The first formatting check found the expanded UAT and CLI test modules did
  not match Black/import ordering, so candidate formatting was not yet frozen.
- The first focused index refresh rewrote `last_updated` for many unchanged
  files because the fresh linked worktree gave all checked-out files today's
  filesystem mtime, creating unrelated candidate churn.
- The first session-end check could not discover the existing valid receipt
  because its Markdown path was wrapped onto the line after the required label.
- The first normal commit-hook run stopped on strict typing for derived-depth
  nullable values and Bandit's existing row-skip findings because the packet
  had unnecessarily changed the legacy adapter file.
- A follow-up direct hook diagnostic guessed a bare `pre-commit` executable,
  which is not exposed on this shell's PATH even though it is installed in the
  project-bound Python environment.

### Root causes and resolutions

- Confirmed root cause: `cmd_design` directly called
  `excel_integration.load_beam_data_from_csv`, whose compatibility parser
  catches row exceptions and continues, and whose model constructor fills
  structural defaults. Resolution: route CSV through `parse_single_csv_lossless`,
  use a strict versioned JSON reader, account every accepted field, validate the
  whole project through `validate_project_beam_batch_v1`, then call the retained
  beam pipeline only after all records pass. Evidence: malformed-only, mixed,
  empty, missing-depth, non-finite, unknown, duplicate, and ambiguous cases all
  return non-zero with zero calculation calls and no output artifact.
- Confirmed root cause: process creation resolves `workdir` before executing the
  shell, so a command cannot create its own nonexistent working directory.
  Resolution: create the linked worktree from the verified primary checkout,
  then run session/source-binding checks inside it. Evidence: the lane reported
  `source_bound=true`, `READY_LOCAL`, exact base equality, and a clean start.
  ⚠️ TERMINAL ISSUE: new worktree path used as `workdir` before creation ->
  created from the existing primary checkout, then changed command context.
- Confirmed root cause: hand-written additions required deterministic formatter
  wrapping and import sorting. Resolution: format only the two reported files
  and apply Ruff's import-order fix. Evidence: Black, Ruff, and
  `git diff --check` pass on all Packet I Python paths.
- Confirmed root cause: index dates are still derived from filesystem mtime,
  which is not stable provenance in a newly materialized linked worktree.
  Resolution: restore only the task-generated indexes to their reviewed base,
  set unchanged tracked source mtimes to their last commit time, and regenerate
  the affected folders once; retain task entries and genuine content-hash
  repairs while removing date-only churn. Evidence: final index checks pass and
  the reviewed index diff contains no unchanged-file date rewrites.
- Confirmed root cause: `_parse_git_receipt_path` requires the receipt label and
  path on one line. Resolution: place the existing repository-relative path on
  the label line without changing the receipt. Evidence: the repeated session-
  end validator resolves and validates the task ID, branch, and receipt hash.
- Confirmed root cause: runtime issue checks established complete numeric input,
  but Mypy could not narrow values stored in a `dict[str, float | None]`; CLI
  aliases were also added to the legacy adapter even though only the ledger
  needs them. Resolution: explicitly narrow the operands, annotate UAT helper
  arguments/parser choices, restore the adapter unchanged, and extend aliases
  only in the lossless import boundary. Evidence: focused tests, Mypy, Bandit,
  and the repeated normal hooks pass. No Bandit suppression was added.
- Confirmed root cause: the shell PATH does not include the primary checkout's
  virtual-environment scripts. Resolution: invoke the installed hook runner
  through `./scripts/python_runtime.sh -m pre_commit`. Evidence: targeted Mypy
  and Bandit diagnostics complete through the bound interpreter.
  ⚠️ TERMINAL ISSUE: bare `pre-commit` was unavailable -> used the maintained
  worktree-bound Python launcher with `-m pre_commit`.

### Validation through content freeze

- Startup: fetched `origin/main`; primary was clean/equal at `b3a9c367`; fresh
  linked lane was `source_bound=true`, `READY_LOCAL`, with no operation marker.
- Narrow contract diagnostic: 26 selected CLI tests and the release-UAT test
  passed before documentation closeout.
- Consolidated Packet I selection: 150 passed across CLI, Excel integration
  edges, lossless imports, strict batch, and expanded release UAT.
- Expanded source UAT: 29/29 cases pass; the live 12-command parser inventory
  exactly matches the packaged classified inventory.
- Black, Ruff, and `git diff --check` pass for every changed Python/test path.
- Exact-wheel build/install verification is intentionally reserved for the
  next release-preparation task at the owner's request; it is not publication
  authority.

### Timing through content freeze

- Git/source orientation and safe lane creation: approximately 5 minutes.
- Contract tracing, implementation, and focused repair: approximately 20
  minutes.
- Documentation, receipt, indexes, gates, hosted CI, and merge closeout are
  completed after this content freeze.

## 2026-08-17 — Session: LIB-PRO-002 Post-Fix Usability Re-Audit

**Agent:** Codex (`library-expert`, documentation/evidence owner)

**Branch:** `codex/lib-pro-002-usability-refresh` from A-G merge
`fe4ab025419b834c6d0f840e9492c0604ae74201` (PR #815)

**Git handoff receipt:** `docs/verification/lib-pro-002-post-fix-recheck-git-handoff-receipt.json`

**Focus:** Re-run the synthetic one-storey user workflow and manual comparison,
verify whether A-G fixed the original usability hazards, audit professional API
and publication surfaces, and update the active plan without changing runtime
behavior or authorizing publication/professional use.

### Summary

- Confirmed that the A-G fixes are material: canonical and compatibility beam
  services block malformed/empty inputs; named imports account rows/fields;
  column materials are explicit; beam/slab/column/footing results retain
  qualified-review truth; the current candidate wheel passes its declared
  19-case negative UAT.
- Recomputed a linked one-storey slab-to-beam-to-column-to-footing gravity
  example. The library matches the independent load, action, flexure, shear,
  column, footing pressure/moment/punching, and development-length arithmetic.
  The footing correctly remains `FAIL` for inadequate dowel anchorage and
  retains HOLD reasons for assumed load/soil/supporting-area bases.
- Reproduced one unresolved advertised-path defect: the `design` CLI skipped a
  malformed row, printed its warning to stdout, exited `0`, and emitted a
  one-of-one PASS summary. Its old intake also supplies cover/effective-depth
  assumptions outside the lossless/strict boundary.
- Confirmed that the published PyPI `0.23.1a1` is the pre-A-G artifact: its page
  has the wrong `0.23.0` pin and its displayed batch example raises
  `AttributeError` against the exact installed wheel. No claim was made that
  current source repairs the immutable old artifact.
- Updated the active plan, task board, planning handoff, and planning README.
  New Packet I owns CLI intake convergence, a versioned machine-readable output
  contract, retained `design -> bbs/detail/dxf` compatibility or explicit
  deprecation, advertised-entry-point inventory, and exact-wheel CLI negatives.
  Packet H whole-building planning remains inactive.
- A follow-up publication-readiness replay added Packet J rather than widening
  Packet I: scheduled/tag full suites must bind the setup-python interpreter,
  and pre-bump, technical-candidate, and authorized-publication modes must emit
  different verdicts. No version bump or release action was authorized.

### Verification

- Current source binding: `source_bound=true`; exact audit base
  `fe4ab025419b834c6d0f840e9492c0604ae74201`.
- Manual/library comparison matched the Section 2.4 values for slab, beam,
  column, and footing, including `Ast_slab=207.012 mm2`,
  `Ast_beam=465.092 mm2`, `Pu_column=68.789063 kN`,
  `q_footing=89.027778 kPa`, `Mu_footing=1.533643 kNm`, punching utilization
  `0.023010`, and required dowel `Ld=644.732 mm`.
- Built the current wheel into a temporary directory, installed it into a clean
  temporary environment, and ran `structural_lib.release_uat
  --require-installed-wheel`: `PASS`, 19/19 declared cases, installed origin.
- Focused current-source selection: 79/79 passed across batch, imports, column
  project contract, result contract, release UAT, and Excel-integration edges.
- Exact published-wheel replay: installed PyPI `0.23.1a1` into an isolated
  environment; the displayed `GenericCSVAdapter` example failed with
  `AttributeError: 'BeamGeometry' object has no attribute 'b_mm'`.
- API audit: root `__all__` 187 symbols; service facade 168 symbols (91
  functions, 77 classes); 28 service functions expose at least one audited
  unit-ambiguous name requiring canonical/compatibility disposition before a
  stable promise.
- Independent structural reviewer: ACCEPT; independently reproduced every
  Section 2.4 value and ran 101 focused tests, with no clause/claim
  contradiction. Independent release reviewer initially rejected two plan
  gaps; both the CLI output/downstream contract and post-plan-merge base wording
  were corrected, and the focused follow-up returned ACCEPT before closeout.
- Provisional `./run.sh release preflight 0.23.1a2`: 6,387 Python tests passed,
  446 FastAPI tests passed, and the React build passed; it also reported no
  candidate wheel and still printed `READY TO RELEASE`, so it is accepted only
  as green pre-bump local health—not publication readiness.
- Hosted Weekly Verification run `31988837003` at exact A-G merge
  `fe4ab025...`: Docker, locked dependency, and clean-wheel jobs passed; the
  full suite failed six governance/session tests because recursive repository
  launchers could not find a project interpreter, and the summary failed.
- Publication authorization checks for provisional `0.23.1a2` correctly
  returned non-zero for TestPyPI, PyPI, and GitHub Release because decision,
  version, tag, targets, owner, time, and exact review receipt remain unset.

### Issues encountered

- The advertised CLI retained the original row-loss/defaulting class after A-G
  merged, even though the declared 19-case wheel UAT passed.
- The first isolated PyPI replay inherited the repository `PYTHONPATH`, so it
  imported current source rather than the installed wheel and then failed on a
  missing dependency. That attempt was not accepted as package evidence.
- The first synthetic footing call used human-readable basis text where the
  strict contract requires exact controlled tokens. It blocked correctly before
  calculation.
- Independent release review found that a direct switch from the old CLI
  `beams` artifact to the strict service `members` envelope could silently break
  advertised `bbs`, `detail`, and `dxf` consumers, and that the handoff's exact
  `fe4ab025…` future base would become stale after this plan merges.
- The scheduled full workflow and publish full-suite step do not export the
  selected setup-python interpreter, although their tests can recursively call
  `run.sh`/`python_runtime.sh`; the scheduled run failed six such tests.
- Pre-bump preflight uses the same success label as publication readiness even
  when it has no exact wheel and does not evaluate immutable review, hosted
  receipts, or exact target authorization.
- ⚠️ TERMINAL ISSUE: a targeted workflow search included an unmatched
  `.github/workflows/*.yaml` zsh glob and stopped that compound command; running
  `rg` directly on `.github/workflows` produced the intended evidence.
- The first I-J handoff draft duplicated detailed-plan history and commands,
  reached 200 lines, and failed the repository's 150-line brief gate.
- Normal commit hooks accepted the plan but warned that the descriptive status
  `In Progress — Packets I-J Planned` was outside the canonical metadata enum.
- ⚠️ TERMINAL ISSUE: the first repair check guessed the nonexistent
  `scripts/check_doc_metadata.py`; `./run.sh find "doc metadata"` resolved the
  maintained command to `scripts/check_docs.py --metadata --strict`.

### Root causes and resolutions

- Confirmed CLI root cause: A-G's route inventory covered service,
  imports, HTTP/SSE/React, and selected package examples, but not every
  advertised calculation entry point. The historical CLI therefore continued
  calling `services.excel_integration.load_beam_data_from_csv`, which catches
  parse errors, prints a warning, and continues with surviving rows. Resolution
  in this documentation packet: add RC-7, CLI-01/CLI-02/REL-UAT-02, and Packet I
  with whole-file blocking, row/field conservation, non-zero exit, stderr-only
  diagnostics, versioned output compatibility, downstream workflow tests, and
  an advertised-entry-point inventory. Evidence: mixed-row live replay and
  direct source trace.
- Confirmed UAT root cause: the packaged matrix proves its handler set is
  complete relative to its data file, not complete relative to public docs/CLI
  surfaces. Resolution: Packet I binds matrix coverage to the advertised
  entry-point inventory and adds exact-wheel CLI cases. Evidence: 19/19 UAT PASS
  alongside the reproduced CLI failure.
- Confirmed installed-package evidence root cause: worktree-bound launchers set
  source routing that is unsuitable for an isolation proof. Resolution: remove
  `PYTHONPATH`/`PYTHONHOME`, install dependencies and the exact wheel in a fresh
  temporary environment, verify `structural_lib.__file__`, then accept the
  replay. Evidence: installed origin under temporary `site-packages` for both
  current candidate and published-wheel runs.
- The footing token failures were correct fail-closed validation, not product
  defects. Resolution: use the maintained exact values
  `includes_footing_self_weight_and_overburden` and
  `largest_frustum_1v_2h`; the corrected call then matched manual arithmetic.
- The independent review defects were plan incompleteness, not style issues.
  Resolution: freeze the CLI output/downstream contract and treat `fe4ab025…`
  as the required A-G ancestor while binding Packet I to exact fetched
  `origin/main` after this reviewed plan merges.
- Confirmed hosted-interpreter root cause: setup-python selects an executable
  but creates neither the repository `.venv` nor `VIRTUAL_ENV`; the launcher is
  intentionally fail-closed, and nightly/publish full suites omitted the
  supported `STRUCTURAL_LIB_PYTHON` binding already used by PR control-plane
  checks. Resolution in the plan: Packet J exports the exact
  `command -v python` path for recursive full suites, preserves strict launcher
  selection, adds workflow-contract tests, and requires a fresh manual Weekly
  Verification pass on the immutable J head.
- Confirmed preflight-verdict root cause: local pre-bump, exact-wheel technical,
  and authorized publication states share one `errors == 0` success label;
  missing wheel is only a warning and authorization is a separate command.
  Resolution in the plan: Packet J introduces mode-specific verdicts and
  reserves `READY_TO_PUBLISH` for exact wheel/UAT, review, hosted receipts, and
  target authorization. Evidence: the green provisional preflight coexisted
  with the reproduced CLI failure, failed hosted full run, and three rejected
  authorization checks.
- Confirmed brief-length root cause: the handoff repeated A-G history and full
  command blocks already owned by the detailed plan. Resolution: retain exact
  branches, I/J ownership, evidence, and stop rules while linking execution
  details to the plan; the brief is 141 lines and the brief-length gate passes.
- Confirmed metadata root cause: a descriptive suffix was placed in the strict
  `Status` field instead of plan prose. Resolution: restore canonical
  `In Progress`; validate through the discovered consolidated metadata command.

### Limitations and handoff

- This session changed documentation and work state only; it did not implement
  Packet I or alter structural calculations.
- The one-storey replay is a synthetic component/load-path regression, not a
  building analysis, source acceptance, geotechnical verification, qualified
  review, code-compliant deliverable, or professional approval.
- Next routine action: merge this plan, implement and merge Packet I from exact
  fetched post-plan `origin/main`, then implement Packet J from exact post-I
  `origin/main`. Run broad/exact-wheel/full hosted evidence at J, stop before a
  version bump, and keep publication and Packet H held.

## 2026-08-17 — Session: LIB-PRO-002 B-G Cumulative Safety Integration

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/lib-pro-002-b-lossless-import` from Packet A merge
`3986935ecb473c1f9d56dec44aeb4218d9192f84` (PR #814)

**Git handoff receipt:** `docs/verification/lib-pro-002-a-g-git-handoff-receipt.json`

**Focus:** Complete Packets B-G as one cumulative candidate: lossless imports,
transport/client convergence, cross-element result truth, evidence identity,
API/documentation truth, exact-wheel negative UAT, and publication policy.
Packet H, publication, professional approval, issue/PR closure, branch deletion,
and unrelated worktree cleanup remain out of scope.

### Summary

- Replaced first-match/row-dropping import behavior with explicit or uniquely
  detected adapters, a versioned every-field/every-row normalization ledger,
  stable blocking issues, exact source/accepted/blocked accounting, and strict
  single- and dual-CSV boundaries.
- Converged HTTP, SSE, compatibility, and React batch paths on the canonical
  strict beam service. Deprecated routes delegate; clients send explicit
  materials, actions, and depth basis without filling absent structural data.
- Added one fail-closed result contract separating intake, calculation,
  engineering, review, and overall state; required qualified review remains
  independent of serviceability escalation, and the footing dowel regression
  remains an engineering FAIL.
- Bound calculation, package content, controlled source/amendment, imported
  artifacts, normalization ledger, assumption origin, provenance, and replay
  identities without treating approval flags as verified source data.
- Added a machine-checked Alpha API classification, removed callable leakage,
  corrected version/claim/example documentation, and provided an installed-
  package interpreter/origin/extras preflight.
- Added the packaged source-free 19-case negative matrix and public-example
  runner, exact-wheel workflow receipts, and an explicit per-version/tag/target
  owner-authorization check before TestPyPI, PyPI, or GitHub Release actions.

### Issues encountered

- The owner had requested Git/worktree safety at the start of Packet A, yet a
  later policy side packet advanced `main` and overlapped Packet A's mutable
  session/index closeout surfaces, making the otherwise clean candidate
  diverge and forcing forward integration.
- The public single-CSV FastAPI route still bypassed the new lossless boundary,
  while the first lossless model counted one physical combined CSV as separate
  geometry and force rows.
- The streaming route initially imported the compatibility facade rather than
  the canonical service, preserving duplicate orchestration under a different
  import name.
- The first source-identity consolidation left footing code and the service
  evidence path with separate constants; an intermediate footing helper edit
  also misplaced a return and produced a `TypeError` in focused tests.
- The bundled sample route still substituted missing dimensions/actions and
  zero coordinates. React preserved the dataset hash separately but dropped
  each beam's sample/assumption provenance before batch calculation.
- Public API discovery exposed imported callables not covered by a complete
  stability class, while maintained READMEs and release checks disagreed about
  Alpha version and executable examples.
- The first architecture run found two FastAPI imports of a core model after
  strict import migration. This would violate the required Core to IS 456 to
  Services to UI dependency direction.
- The local React command initially assumed `$HOME/.nvm/nvm.sh`, which is not
  installed on this machine. An earlier `npm run type-check` attempt also found
  that the project declares no such script.
- PDF text extraction was unavailable during source-identity inspection, and
  an attempted release helper name (`source-surface-check`) did not exist.
- The first cumulative run exposed four stale dependent contracts: evidence
  schema `2.0` assertions after the intentional `3.0` upgrade, a React legacy
  response field used but omitted from its type, a compatibility-facade test
  monkeypatching internals removed for API classification, and a column test
  still requiring the deleted 25/415 defaults.
- The first exact-wheel candidate check stopped because the footing release-
  inclusion receipt still carried pre-INDIA-2 exact-arithmetic hashes and did
  not cover Packet E's reviewed footing assumption/provenance changes.
- The guessed direct index generator `scripts/generate_folder_indexes.py` does
  not exist in this repository, so that command stopped before any index write.
- The first full 31-check gate found three Packet F/governance omissions: the
  old API-doc sync check still required the deleted symbol-by-symbol stability
  duplicate, the new API-classification generator was absent from the script
  map/index, and placing its packaged UAT implementation at package root
  exceeded the root non-stub module limit.
- The second full gate passed 30/31 and found that the injected row-loss UAT
  adapter had suppressed Mypy's untyped-definition warning but still lacked
  the explicit return type required by the repository annotation checker.
- The first session-end check reported the handoff receipt missing even though
  the new receipt file existed and independently validated.
- A final verification attempt used the nonexistent `run.sh check-indexes`
  command, so the chained session-end step did not execute.
- The first maintained all-index check found three stale parent indexes after
  all directly edited child-folder indexes had been refreshed.
- The first staged diff check found trailing spaces in a new evidence file;
  the earlier unstaged diff check did not inspect untracked content.
- Normal commit hooks found four package-wide Mypy errors and rejected the
  noncanonical heading/row labels in the cumulative handoff brief.
- Independent exact-head review rejected `c66160c7` because publication
  authorization accepted arbitrary non-empty review-receipt text without
  resolving evidence or binding reviewed head/tree/version/target identity.
- A post-commit exact-wheel command was rejected before execution because its
  temporary cleanup trap used a raw recursive delete operation.
- A repair verification attempt guessed the nonexistent
  `scripts/check_annotations.py` path after the focused release suite passed.

### Root causes and resolutions

- Confirmed Git root cause: startup cleanliness was checked correctly, but lane
  safety was treated as a start-time property. Linked worktrees isolate files,
  not refs, and no active-candidate dependency/path-overlap gate ran before the
  later side packet merged. Resolution: Packet A added the durable whole-
  candidate overlap gate to `AGENTS.md` and the canonical Git workflow; this
  session then used one isolated cumulative writer from exact `origin/main`,
  made no primary-tree mutation, and preserved every unrelated lane. Evidence:
  `git_state.py --json --worktrees` reports the candidate at base equality,
  primary `main` clean, no operation marker, and the unrelated dirty detached
  `e54a` lane unchanged.
- Confirmed import root cause: parsing, adapter selection, row conversion, and
  compatibility return shapes were coupled, so downstream code could not prove
  conservation. Resolution: one ledger owns adapter candidates, artifacts,
  fields, physical rows, matches, exclusions, issues, and totals; combined CSV
  is an explicit single artifact role and every blocker returns no batch.
  Evidence: malformed, non-finite, ambiguous, duplicate, dropped, and unmatched
  regressions pass, including valid explicit zero.
- Confirmed orchestration root cause: transports independently normalized
  values because there was no canonical iterator/result boundary. Resolution:
  service validation prepares the complete batch contract and executes lazily;
  POST/SSE/React consume it, while legacy entry points delegate or deprecate.
  Evidence: service/HTTP/SSE request equivalence and calculation-call spies
  pass; blocked inputs make zero core calls.
- Confirmed identity root cause: source/amendment constants lived in an
  application service and were recopied into IS 456 code. Resolution: the
  layer-neutral identities now live in `core/source_identity.py`; evidence and
  footing import that one record, and the misplaced return was restored to its
  owning helper. Evidence: focused evidence/replay and footing tests pass, and
  the architecture checker reports zero violations.
- Confirmed sample root cause: the endpoint was historically a demo convenience
  path and therefore used `dict.get(..., plausible_value)` rather than treating
  bundled data as a controlled fixture. Resolution: all required strings and
  finite numbers are parsed without fallback, duplicate/unmatched identities
  fail closed, exact dataset/record identity and sample assumptions accompany
  every beam, and React preserves them. Evidence: the 153-beam BOQ/evidence
  regression plus the React provenance mapping test pass.
- Confirmed API/release root cause: public exposure, documentation, installed
  examples, artifact identity, and publication authority were independent
  lists. Resolution: generated classification and version checks fail on drift;
  exact-wheel UAT packages the negative matrix and advertised examples; the
  publish workflow checks a separate exact authorization record before any
  target. Evidence: classification, install-preflight, release-script, UAT,
  workflow-YAML, and current HOLD-policy tests pass.
- Confirmed architecture root cause: FastAPI constructed the historical core
  `DesignDefaults` compatibility model directly after migration. Resolution:
  explicit values enter a service factory and the UI layer imports services
  only. Evidence: 206 files pass the four-layer check and 661 files/4,498
  imports validate with zero broken imports.
- ⚠️ TERMINAL ISSUE: `$HOME/.nvm/nvm.sh` was absent -> used the repository-
  reported pinned Node 24 binary directory from `./run.sh frontend runtime`.
  The focused React test then passed. The missing `type-check` script is not a
  product failure; canonical React lint/tests/build are used instead.
- ⚠️ TERMINAL ISSUE: `pdftotext` was absent -> used maintained controlled-
  source manifests and hashes, without changing source claims. The nonexistent
  release helper name was replaced by the maintained `candidate-check` and
  direct version-surface helper tests discovered from `release.py`.
- Confirmed dependent-contract root cause: evidence/API/input contracts changed
  at their canonical owners, but four broad regressions still encoded the old
  surface. Resolution: update only those expectations/types to schema `3.0`,
  retain the explicit legacy `beam_id` fallback in its response type, patch the
  canonical common-version module rather than facade internals, and assert
  missing column materials block. Evidence: the four failed paths pass, and
  pinned React lint, all 267 tests, TypeScript production build, and Vite build
  pass.
- Confirmed receipt root cause: the D1 inclusion record was hash-frozen before
  the accepted exact stress-block correction in `d8202fef`, and Packet E then
  intentionally changed eight owned footing files. Resolution: inspect the
  exact diffs, record both reviewed refresh bases, update only the controlled
  owned-file hashes, and rerun the maintained inclusion check. Evidence: the
  inclusion gate and 40 Python/FastAPI footing regressions pass; no scope marker
  or original D1 source-head identity was weakened.
- ⚠️ TERMINAL ISSUE: the guessed `scripts/generate_folder_indexes.py` path was
  absent -> `./run.sh find "folder index"` identified the maintained
  `./run.sh generate indexes <owned-folder>` interface; only affected existing
  index folders are refreshed after every task-owned evidence write.
- Confirmed Packet F check-drift root cause: the generated classification
  registry replaced the old hand-maintained stability list, but
  `check_api.py --sync` still validated the removed duplicate rather than the
  new single source. Resolution: the checker now requires the stability page
  to bind `api-classification.json`, proves every documented compatibility
  symbol is classified, and excludes the literal `api.md` filename from symbol
  extraction. The three exported result dataclasses are explicitly identified
  as Alpha-preview calculation evidence in `api.md`. Evidence: all three API
  validation lanes pass.
- Confirmed control-plane root cause: the new generator was added to CI before
  the maintained automation registry/index, and the executable UAT lived at
  package root instead of behind a root facade. Resolution: register the
  generator with read/write permission modes, move the implementation with the
  maintained safe-file tool to `services/release_uat.py`, and retain the public
  `python -m structural_lib.release_uat` facade as a nine-line stub. Evidence:
  automation coverage is 110/110, the UAT test passes through the facade, and
  governance reports every root module stub-only with zero errors.
- Confirmed annotation root cause: the UAT test double used a local Mypy ignore
  instead of matching `InputAdapter.load_forces() -> list[BeamForces]`.
  Resolution: add the exact override type and remove the ignore. Evidence: all
  27 functions in the service UAT module are fully annotated and its 19-case
  regression passes.
- ⚠️ TERMINAL ISSUE: the first direct annotation-check command passed the file
  as a positional argument, but the maintained CLI requires `--file` -> reran
  with `--file Python/structural_lib/services/release_uat.py`; 27/27 functions
  report fully annotated.
- Confirmed session-end root cause: receipt discovery intentionally reads an
  explicit `**Git handoff receipt:**` path from the newest session entry and
  does not guess among many verification files. Resolution: bind this entry to
  the exact cumulative receipt path. Evidence: direct receipt validation
  already passes; session-end is rerun after the final index refresh.
- ⚠️ TERMINAL ISSUE: `run.sh` exposes maintained index validation as
  `./run.sh generate indexes --all --check`, not `check-indexes` -> discovered
  the exact interface with `./run.sh find "folder index validation"` and the
  built-in help, then used the maintained check before rerunning session-end.
- Confirmed index root cause: parent folder content hashes include changed
  descendants, so refreshing only folders containing directly edited files
  left `Python/structural_lib`, `fastapi_app`, and `react_app/src` stale.
  Resolution: regenerate those three maintained parents, then run the all-index
  check. Evidence: all 32 maintained index pairs must report current before the
  immutable commit.
- Confirmed staged-diff root cause: `git diff --check` covers tracked changes
  but not a new untracked file until it is staged. Resolution: remove the
  trailing spaces and require `git diff --cached --check` after intentional
  staging. Evidence: the staged candidate check passes before commit.
- Confirmed Mypy root causes: the strict import factory relied on two unused
  Pydantic compatibility defaults and typed the integer FastAPI stirrup value
  as `float`; the heterogeneous install-preflight report also widened its
  nested extras map to `object`. Resolution: pass the inert compatibility
  fields explicitly, match the boundary's integer type, and keep a separately
  typed `dict[str, bool]` for extras. Evidence: the package-wide Mypy commit
  hook must pass on all 234 source files.
- Confirmed handoff root cause: the general Markdown/index/brief-length checks
  accept heading case and descriptive table labels, while `scripts/session.py
  check` requires the canonical `## Required Reading`, `| **Current** |`, and
  `| **Next** |` literals. Resolution: restore those exact contract labels and
  retain the normal commit hook as the decisive contract. Evidence: the
  session-doc commit hook must pass before the candidate exists.
- Confirmed publication-gate root cause: the first authorization schema treated
  `exact_candidate_review_receipt` as a presence-only string and therefore
  could not distinguish immutable reviewed evidence from fabricated text.
  Resolution: require a repository-relative JSON receipt and exact SHA-256;
  validate ACCEPT, independent reviewer/time, reviewed head/tree/Python tree,
  version/tag/targets, review-before-authorization chronology, Git ancestry,
  clean checkout, unchanged package content, and an allowlisted evidence-only
  descendant delta. Evidence: valid reviewed candidate plus authorization must
  pass, while fabricated text, receipt tampering, identity drift, package
  drift, target drift, pre-review authorization, and extra changed paths must
  fail closed before publication.
- ⚠️ TERMINAL ISSUE: the first post-commit wheel command included a raw
  recursive temp-directory cleanup trap and was rejected before execution ->
  reran without any delete operation and retained the isolated UAT directory;
  exact-wheel UAT then passed 19/19 without repository mutation.
- ⚠️ TERMINAL ISSUE: `scripts/check_annotations.py` does not exist ->
  `./run.sh find "type annotation check"` resolved the maintained
  `scripts/check_type_annotations.py` command, which is used for the repair
  candidate instead.

### Validation before cumulative freeze

- Focused import/service/API/React, result/review, evidence/replay, API
  classification, install-preflight, release-policy, sample, and packaged-UAT
  regressions pass.
- Focused Mypy passes ten new/changed contract modules; Ruff and Black are
  clean on the complete Python/FastAPI/script surface.
- Architecture: 206 files, zero violations. Import validation: 661 files,
  4,498 imports, zero broken imports. OpenAPI baseline: 82 endpoints and 357
  schemas, current with no unrecorded drift. Publish workflow YAML parses with
  five jobs.
- Source-free candidate wheel
  `structural_lib_is456-0.23.1a1-py3-none-any.whl` passes clean-install version
  evidence, installed-package preflight, both advertised examples, and all 19
  declared negative UAT cases. Rehearsal SHA-256 is
  `cf16b49963374e31eee80a31b73f94d0997969fdf5515e805f270eafb16f4830`;
  matrix SHA-256 is
  `21da496a9dc9d90b3ce3537d100293db2a23d14461ed2f602b185fd13288f8ea`.
  The receipt says qualified review required and professional approval false.
- Publication authorization deliberately returns HOLD for `v0.23.1a1`/PyPI;
  the owner, exact future version/tag/targets, and candidate-review receipt are
  absent as required.
- Final cumulative suites pass on the repaired tree: Python 6,382 passed, 3
  skipped, 6 deselected; FastAPI 452 passed; React lint, 267 tests, TypeScript,
  and production build pass. The Git handoff source evidence and pre-index
  receipt validate with the expected HOLD for dirty/local-only/unchecked
  remote-review state.
- Immutable head `c66160c7bc25eba22011d051643fe93c1b406bac`
  passed normal hooks, the exact committed wheel (SHA-256
  `edefc7235944892a059345383f55547e71d49d1c3eb64cb0777d397433e811bc`)
  passed 19/19 UAT, all 6,382 Python/452 FastAPI/267 React tests passed, and all
  eight hosted PR #815 checks passed. Independent review correctly returned
  REJECT for the publication-receipt bypass above; none of those green gates
  overrides that outcome-changing finding.
- The first full canonical run passed 28/31 and exposed the three omissions
  above; their narrow API, automation, governance, and facade regressions now
  pass. The second run passed 30/31 and exposed the annotation omission above;
  its direct regression now passes. Refreshed affected indexes are the final
  repository writes. The final full 31-check retry, quick, session-end,
  immutable commit/review, and hosted results follow without changing this
  candidate evidence.

## 2026-08-17 — Session: LIB-PRO-002-A Strict Service Intake

**Agent:** Codex (`backend` and `tester`, sole writer)

**Branch:** `codex/lib-pro-002-a-strict-input` from freshly fetched
`origin/main = 55104e11257937b0a42fb06f931a70b8484cef39`

**Git handoff receipt:** `docs/verification/lib-pro-002-a-forward-integration-git-handoff-receipt.json`

**Focus:** Replace the beam batch service's silent structural defaulting and
implicit effective-depth derivation with the versioned strict project contract
frozen by G0. Do not edit imports, FastAPI/React transports, other element
families, release automation, API classification, or whole-building behavior.

### Summary

- Added strict versioned project beam input and result types with explicit-unit
  fields, stable issue codes and paths, orthogonal intake/calculation/
  engineering/review states, and a summary in which zero evaluated members can
  never PASS.
- Required every calculation-bearing value and exactly one explicit `d_mm` or
  complete cover/stirrup/tension-bar depth basis; malformed, empty, non-finite,
  out-of-range, unknown, conflicting, or duplicate inputs now block.
- Made the legacy batch functions a compatibility adapter that maps only known
  aliases, applies no structural defaults or alias precedence, and delegates to
  the canonical validator and calculation path.
- Preserved the accepted synthetic beam arithmetic and the completed unsafe-
  shear FAIL while proving every blocked member avoids `design_beam_is456`.
- Forward-integrated the subsequently merged workflow-policy packet without
  rewriting the original Packet A commit or touching unrelated worktrees.

### Issues encountered

- The live G0 task board and handoff still described G0 as a local candidate
  even though PR #812 had been independently accepted, merged, and synchronized
  to `main`; following that state literally would repeat the completed packet.
- The original batch path combined alias selection, numeric coercion, fallback
  structural values, fabricated member identity, and `D - cover - 8` depth
  derivation before invoking the calculation core.
- The first duplicate-identity implementation counted only otherwise-valid
  inputs, so a valid row could still calculate when its duplicate twin was
  independently blocked for another field error.
- Final pre-candidate review found that whole-batch duplicate validation also
  caused both strict and legacy iterators to calculate every accepted member
  before returning the first result, weakening streaming/cancellation behavior.
- The first focused Mypy run rejected the concrete `list[dict[str, Any]]`
  compatibility payload against an invariant `list[Mapping[...] | Input]`
  internal annotation.
- The first handoff-receipt command left zsh glob patterns unquoted, so the
  shell expanded the forbidden FastAPI/React/workflow paths and the receipt
  parser rejected the resulting arguments before writing a receipt.
- The first normal commit-hook run stopped because canonical Black reformatted
  one conditional-comprehension expression that Ruff format had left unchanged.
- Although Packet A started from a clean, current, isolated worktree, merging
  the later workflow-policy side packet advanced `main` and changed the same
  session/index surfaces before Packet A was published. Packet A therefore
  became `HOLD_DIVERGED` despite remaining clean.
- The first post-resolution quick gate passed all content checks but failed its
  two Git checks because the authorized merge operation necessarily remained
  open until the merge commit existed.

### Root causes and resolutions

- Confirmed root cause: immutable G0 closeout correctly froze versioned records
  before hosted review/merge facts existed, so the successor packet had to
  reconcile those external facts rather than mutate the prior candidate.
  Resolution: bind Packet A to fetched merge `55104e11`, mark G0 merged, and
  make Packet A the sole active task. Evidence: startup reports the new lane at
  exact base equality, `READY_LOCAL`, clean, and `source_bound=true`.
- Confirmed root cause: `_pick_first()` and `_to_float()` treated parsing,
  aliases, and assumptions as one operation and supplied 300/500/100/50/25/500/
  40 plus a generated ID whenever source values were absent or malformed.
  Resolution: one strict validator now accepts only canonical JSON numbers and
  a separately named compatibility adapter maps aliases without filling any
  structural value. Evidence: the table-driven service matrix and calculation
  spies pass; blocked/duplicate members make zero core calls.
- Confirmed root cause: duplicate counting used only validations that still
  held a constructed value, excluding invalid rows even when their non-blank
  `member_id` remained known. Resolution: count all validated member-ID hints,
  block every occurrence, and preserve each row's other issues. Evidence: the
  valid-plus-invalid duplicate-twin regression passes with two blocked members
  and zero calculation calls.
- Confirmed root cause: the first iterator delegated to a helper that eagerly
  constructed the complete typed batch result, coupling required whole-batch
  validation to calculation execution. Resolution: prepare all validations
  first but yield each blocked/calculated member lazily. Evidence: strict and
  legacy iterator regressions observe zero core calls before iteration and
  exactly one call after requesting the first of two members.
- Confirmed root cause: Python mutable lists are invariant even when their item
  types are compatible. Resolution: accept `Sequence` at the internal
  read-only batch boundary. Evidence: focused Mypy reports success for both new
  service modules.
- Confirmed root cause: zsh expands `**` before the called program can preserve
  it as a policy pattern. Resolution: quote every glob-valued receipt argument
  and rerun creation/validation. Evidence: the literal forbidden paths appear
  in the validated receipt. ⚠️ TERMINAL ISSUE: unquoted receipt globs expanded
  into repository paths -> quoted the patterns and reran the maintained tool.
- Confirmed root cause: Ruff format and the repository's pinned Black do not
  produce identical wrapping for the conditional-comprehension expression.
  Resolution: use the repository's normal Black hook result, run Black against
  all owned Python files, then rerun focused checks before restaging. Evidence:
  the retry must pass the unmodified normal hooks. ⚠️ TERMINAL ISSUE: commit
  hook reformatted one file -> accepted canonical Black output and reran gates.
- Confirmed root cause: worktree cleanliness and isolation were checked, but no
  active-candidate dependency/path-overlap gate was run before the later policy
  PR merged. Worktrees isolate files and indexes; they share refs, so advancing
  `main` made Packet A diverge, and the two packets overlapped
  `docs/SESSION_LOG.md` plus generated indexes. Resolution: preserve
  `22066d0d`, merge current `origin/main` into the existing Packet A branch,
  resolve only the predicted governance/index conflicts, and add a durable
  pre-publication active-candidate overlap gate to `AGENTS.md` and the canonical
  Git workflow. Evidence: the pre-merge comparison identifies only five shared
  governance/index paths, the merge reports conflicts only in those five paths,
  and no runtime source conflict occurs. ⚠️ TERMINAL ISSUE: a later side packet
  made the clean Packet A candidate diverge -> forward-integrated without
  rebase/reset/force and recorded the missing sequencing guard.
- Confirmed root cause: `git_state.py` correctly classifies any live merge as
  `HOLD_OPERATION`, while a merge cannot leave that state until its resolving
  commit is created. Resolution: for an authorized, fully resolved merge, run
  focused/content checks first, create the merge commit through normal hooks,
  then run the sole quick gate on the clean merge head before audit or push.
  Evidence: the premature quick run passes 8/10 content/governance checks and
  fails only `Git state` and `Unfinished operation` with the same explicit
  `operation: merge` hold. ⚠️ TERMINAL ISSUE: quick cannot pass inside an open
  merge -> move the single quick gate to the clean merge head.

### Validation through content freeze

- Startup: freshly fetched base equality at `55104e11257937b0a42fb06f931a70b8484cef39`,
  fresh linked worktree, `READY_LOCAL`, no operation marker, clean tree, and
  `source_bound=true`; the unrelated dirty detached `e54a` worktree remains
  untouched.
- Focused strict/compatibility service contract: 43 passed, including the
  complete negative matrix, calculation spies, accounted mixed/empty batches,
  explicit-versus-derived depth equivalence, lazy iterator execution, unchanged
  pilot numbers, and retained unsafe-shear FAIL.
- Ruff passes the three owned Python files; focused Mypy passes both service
  modules; `git diff --check` is clean.
- Architecture boundary check passes with 201 files and zero violations;
  import validation passes with 650 files, 4,416 imports, and zero broken
  imports.
- Forward integration started from clean heads `22066d0d` and `87205d64` with
  `source_bound=true`; all five conflicts were confined to the predicted shared
  session/generated-index paths.
- Receipt, affected indexes, quick `10/10`, session-end validation, immutable
  candidate commit, exact-head independent review, and hosted closeout remain
  after the final content freeze.

### Timing through content freeze

- Plan/Git/worktree safety and source binding: approximately 2 minutes.
- Test-first implementation, root-cause repair, and focused validation:
  approximately 14 minutes.
- Receipt/index/quick, immutable review, hosted wait, merge closeout, and total
  wall time remain to be recorded externally.

## 2026-08-17 — Session: Implementation-First Verification Policy

**Agent:** Codex (`governance`, sole writer)

**Branch:** `codex/implementation-first-verification-policy` from freshly
fetched `origin/main = 55104e11257937b0a42fb06f931a70b8484cef39`

**Git handoff receipt:** `docs/verification/implementation-first-verification-policy-git-handoff-receipt.json`

**Focus:** Make the owner's implementation-first, batched-verification cadence
durable for future repository chats. Preserve the clean Packet A candidate and
all unrelated worktrees; do not change structural calculations, APIs, React,
adapters, release behavior, or the active LIB-PRO-002 handoff.

### Summary

- Made one bounded packet, rather than each edit, the routine verification
  boundary.
- Limited during-implementation checks to narrow evidence needed to guide or
  debug a live question.
- Consolidated focused checks, the single quick gate, commit hooks, hosted
  checks, and the cumulative full gate into an explicit non-duplicative
  cadence shared by top-level instructions, canonical efficiency policy, and
  the quality-gate skill.
- Kept required safety, independent-review, hosted-CI, and release gates intact.

### Issues encountered

- Existing guidance said to use targeted checks while editing and to avoid
  duplicated gates, but did not explicitly say that routine verification
  starts only after the whole bounded packet is implemented and frozen. That
  ambiguity could make future chats rerun unchanged checks after small edits.
- The first session-end check did not discover the committed handoff receipt
  because its path was wrapped onto the line after the bold label.

### Root causes and resolutions

- Confirmed root cause: the intended cadence was split across `AGENTS.md`, the
  canonical token-efficiency guide, and the quality-gate skill, while the phrase
  “while editing” lacked a necessity condition. Resolution: align all three
  surfaces on implementation first, necessary diagnostics only, one
  consolidated post-freeze focused selection, one quick gate, required hosted
  checks, and one cumulative full gate. Evidence: the efficiency policy check,
  documentation checks, affected indexes, quick gate, session-end contract,
  and normal commit hooks complete after content freeze.
- Confirmed root cause: the session-end parser requires the receipt path on the
  same line as the bold `Git handoff receipt` label. Resolution: place the
  committed path on that label line and retain this exact format for future
  entries. Evidence: the repaired session-end check discovers and validates
  the receipt. ⚠️ TERMINAL ISSUE: session end reported a missing receipt ->
  matched the maintained same-line parser contract.

### Validation through content freeze

- Startup evidence: fresh fetch equality at
  `55104e11257937b0a42fb06f931a70b8484cef39`, a clean isolated policy lane,
  and current-worktree Python source binding.
- Packet A remains a separate clean `READY_LOCAL` worktree at
  `22066d0d83f84995b898a58b43993f621ec2d8d0`; the unrelated dirty detached
  worktree remains untouched.
- No task-board or next-session-brief update is required because this policy
  change does not alter the active LIB-PRO-002 packet sequence or handoff.

## 2026-08-17 — Session: Pre-Release Input-Safety Contract Freeze

**Agent:** Codex (`orchestrator` and `doc-master`, sole writer; two bounded
read-only reviewers)

**Branch:** `codex/pre-release-input-safety-plan` from freshly fetched
`origin/main = 904a2f8cf0ea5d4595f57c46dac06e2e837bba45`

**Git handoff receipt:** `docs/verification/lib-pro-002-g0-git-handoff-receipt.json`

**Focus:** Independently check the one-storey usability report, reconcile its
confirmed outcome-changing defects with the completed professional remediation
history and current release surface, and freeze a dependency-ordered plan
before implementation. Do not change calculation, API, React, adapter, or
release behavior and do not publish a package.

### Summary

- Bounded the reported numerical match to the exact synthetic cases and
  retained the correct footing dowel-development failure.
- Traced the unsafe PASS path to silent project defaults and then found the
  wider shared cause: normalization and structural derivation are duplicated
  across service batch, imports, streaming, React, and column entry paths.
- Reconciled two independent read-only audits into six root causes, a single
  outcome-changing issue register, strict target contracts, a negative
  acceptance matrix, and eight dependency-ordered packets.
- Held every next publication until the Alpha safety gate and separate owner
  authorization; stable, engineering-use, professional-approval, and
  whole-building claims have additional explicit gates.

### Key Deliverables

- `docs/planning/pre-release-input-safety-and-professional-readiness-plan.md`
- active `LIB-PRO-002-G0` task and exact Packet A boundary
- current next-session handoff and planning index entry

### Issues encountered

- `./run.sh session start` was first run from the clean primary `main` checkout
  during orientation and wrote a new session skeleton there, contrary to the
  intended fresh-lane-only mutation boundary.
- The earlier `LIB-PRO-001` plan is correctly marked software-complete, while
  the new user pilot proves a different end-user data-ingress defect. Treating
  the pilot as unfinished old work would corrupt the historical evidence
  ledger and hide the new root cause.
- Existing green audit/quick/health evidence and the exact arithmetic pilot do
  not exercise silent field replacement, ambiguous import selection, row loss,
  executable README examples, or exact-wheel negative paths.
- A guessed standalone `scripts/check_frontmatter.py` path did not exist because
  frontmatter validation is part of the maintained unified documentation
  checker.
- Independent candidate review found that the Alpha gate called for an
  unspecified “independent review” and classified exact replay provenance as
  stable-only even though the same gate required immutable release evidence.
- The first session-end check did not discover the valid receipt because its
  parser requires the receipt path on the same line as the bold label.
- The first staged diff check exposed trailing Markdown hard-break spaces in
  the new plan; earlier unstaged `git diff --check` did not inspect that
  untracked file.

### Root causes and resolutions

- Confirmed root cause: `session start` is intentionally a writing command,
  but it was invoked before the fresh worktree had been created. Resolution:
  inspect the exact primary diff, remove only the generated skeleton, verify
  primary returned clean, then create and bind the fresh lane before invoking
  it again. Recurrence guard: run `session brief` during read-only orientation
  and defer `session start` until the intended lane reports `READY_LOCAL`.
  ⚠️ TERMINAL ISSUE: session start wrote a skeleton on primary `main` -> exact
  generated block removed after diff inspection; the command succeeded in the
  source-bound task worktree.
- Confirmed root cause: the pilot covers live workflows added or exercised
  after the historical remediation packet and reveals no single canonical
  project-input boundary. Resolution: retain `LIB-PRO-001` unchanged and create
  `LIB-PRO-002` with new IDs, explicit compatibility policy, and route-level
  ownership.
- Confirmed root cause: present gates emphasize valid/happy paths and component
  calculations, so they can remain green while callers substitute or discard
  data before calculation. Resolution: freeze a cross-surface negative matrix,
  row/field conservation rules, executable exact-wheel examples, and
  publication holds before code changes. Evidence: the plan maps each live
  confirmed path to one packet and makes Packet G the cumulative release gate.
- Confirmed root cause: the old standalone frontmatter checker is archived and
  the maintained command is `scripts/check_docs.py --frontmatter --json`.
  Resolution: locate the current implementation with `rg --files`, use the
  unified checker, and retain `./run.sh find` plus `rg --files` as the discovery
  sequence. Evidence: the maintained documentation check passes with zero
  invalid frontmatter. ⚠️ TERMINAL ISSUE: guessed a retired standalone
  frontmatter path -> discovered and used the unified checker.
- Confirmed root cause: the issue register, Alpha gate, and stable gate used
  individually reasonable wording but had not been cross-checked as one claim
  matrix. Resolution: name the Alpha review as independent exact-head
  software/release-evidence review, state that it is not qualified engineering
  review, and promote replay/source identity `PROV-01` to the Alpha gate.
  Evidence: both bounded reviewers accepted the remaining plan and identified
  only these minimal corrections for exact-candidate reconciliation.
- Confirmed root cause: the session log followed several older two-line receipt
  examples, but `_parse_git_receipt_path()` recognizes only a same-line path.
  Resolution: place the validated receipt path on the label line and rerun
  session end. Evidence: the repaired checker must report the receipt and its
  expected pre-commit HOLD. ⚠️ TERMINAL ISSUE: session end reported a missing
  receipt -> matched the maintained same-line parser contract.
- Confirmed root cause: authoring used two-space Markdown line breaks, and Git's
  unstaged diff does not include untracked files. Resolution: remove trailing
  whitespace mechanically and require intended-path staging before the final
  `git diff --cached --check`. Evidence: the cached diff check must be clean
  before commit. ⚠️ TERMINAL ISSUE: staged diff check rejected trailing spaces
  -> normalized the new plan and refreshed only affected indexes.

### Validation through content freeze

- Startup evidence: fetched base equality at
  `904a2f8cf0ea5d4595f57c46dac06e2e837bba45`, fresh linked lane, no operation
  marker, and `source_bound=true` before intended edits.
- Live inspection confirmed service defaults and `D-cover-8`, import-model
  defaults and `D-cover-25`, React 25/500/40 defaults, first-match adapter
  selection, invalid-row/force fallback behavior, and the maintained unsafe
  slab review phrase/test.
- Both bounded reviewers returned `ACCEPT` after the Alpha review type was made
  explicit and `PROV-01` was promoted into the Alpha gate.
- The pre-commit Git handoff receipt validates as an expected `HOLD` with local
  dirty, remote/PR, and exact-head review evidence still pending; it grants no
  authority and records the user-selected planning-only boundary.
- Planning metadata, links, affected indexes, quick gate, session-end contract,
  exact-head independent review, and normal commit hooks complete during
  candidate closeout.

### Timing through content freeze

- Orientation, prior-state reconciliation, and two bounded audits began on
  2026-08-17; final wall time including validation and closeout is reported in
  the external handoff.


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

## 2026-08-17 — Session: A1 Canonical Truth and Transport Contract

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract` from clean base
`09861d3d5ef758abbe0f7c40b8b49b2f90510765`; isolated linked-worktree runtime
diagnosis reported `source_bound=true`.

**Focus:** Complete M2 packet A1 only: canonical result/error/unit/identity/depth,
serialization, API-surface classification, and transport adapters for the
reference beam journey and applicable maintained consumers. Do not begin A2,
gravity, live ETABS, Excel write-back, optimization, solver, or release work.

### Summary

- Added a shared fail-closed v2 structural-result envelope, stable issues and
  replay identity, a strict JSON normalizer, and a shared explicit/derived beam
  effective-depth contract.
- Migrated the root/service/compatibility Python APIs, CLI, workflow, FastAPI,
  OpenAPI, React catalogue/workflow/trust surfaces, and checked-in development
  clients without creating a second calculation authority.
- Separated HTTP transport acceptance from engineering PASS/FAIL/HOLD and
  normalized maintained JSON 4xx/5xx declarations and framework exceptions to
  `structural-problem/v1`.
- Added source-versus-wheel version authority, claim/artifact classification,
  readiness truth collection, and a reproducible source-free wheel plus
  exact-head FastAPI import-binding verifier.
- Kept the compatibility WebSocket on explicit HOLD when its old payload lacks
  the canonical result envelope. No gravity or A2 implementation was started.

### Issues encountered

- Source imports could be labelled by unrelated stale installed distribution
  metadata.
- Effective-depth arithmetic and required-field defaults were duplicated in
  workflow/transport consumers, including a hidden `D - 43` calculation.
- The parity script compared the same implementation twice and used shallow
  serialization while describing FastAPI parity.
- Readiness omitted semantic parity/quality/input-validation outcomes and could
  report false green.
- HTTP error declarations and framework 404 responses did not share one
  versioned problem contract.
- React accepted allowed status words without proving that the axes, aggregate,
  evidence, and replay identity agreed.
- The workflow catalogue, UI, drafts, generated clients, and tool manifest
  retained older schema versions or incomplete depth/status fields.
- Evidence normalization assumed deflection and crack-width parameter mappings
  always appeared together.
- Several large or multi-file edit attempts failed before changing their target,
  and one accidental signature edit was caught by syntax compilation.

### Root causes and resolutions

- Confirmed root cause: version lookup treated installed metadata as universal
  authority. Resolution: source checkout uses the adjacent package project and
  an installed wheel uses its distribution metadata. Proof selected: unit
  identities plus source-free artifact import receipt.
- Confirmed root cause: adapters owned calculation-bearing depth/default logic.
  Resolution: one resolver requires explicit `d_mm` or a complete cover/stirrup/
  bar basis; required workflow inputs are never filled from display defaults.
  Proof selected: exact `d=443 mm` PASS/FAIL boundary across Python, CLI,
  workflow, REST, React contract, and wheel probes.
- Confirmed root cause: parity did not cross distinct facades and the generic
  serializer did not reject non-finite JSON. Resolution: compare root, service,
  and compatibility facades through one recursive strict JSON round trip; HTTP
  parity remains owned by an actual FastAPI route test.
- Confirmed root cause: readiness collected file-presence proxies instead of
  semantic contract outcomes. Resolution: required API parity can fail the
  report, while advisory quality/input debt produces PARTIAL rather than PASS.
- Confirmed root cause: local route handlers and Starlette's framework 404 path
  used different error shapes. Resolution: one problem builder, global OpenAPI
  models, and shared request/HTTP/domain/generic handlers.
- Confirmed root cause: React treated each status field independently and trust
  presentation fell back to old booleans. Resolution: recompute overall status,
  validate review/depth/identity structure, require current matching evidence,
  and HOLD missing/contradictory WebSocket payloads.
- Confirmed root cause: maintained consumer schemas and generated templates
  were not bound to the new authority. Resolution: version/migrate catalogue,
  workflow, draft, OpenAPI, clients, tool manifest, and claim-surface matrix in
  the same packet; optional explicit depth has no hidden tool default.
- Confirmed root cause: evidence normalization coupled two independently
  optional serviceability mappings. Resolution: retain each supplied mapping
  independently and require at least one only when serviceability is enabled.
- ⚠️ TERMINAL ISSUE: one delete/add mega-patch and one malformed multi-file
  patch did not apply -> inspected exact ranges and used bounded hunks.
- ⚠️ TERMINAL ISSUE: an accidental broad signature edit failed targeted
  `py_compile` -> restored the exact public signature before any test batch.

### Validation through content freeze

- Startup/source: clean isolated base, no operation marker, exact equality with
  `origin/main`, and `source_bound=true`.
- Implementation diagnostics only: changed Python files compile; exact direct,
  workflow, and live FastAPI boundary vector agrees at `d=443 mm`, engineering
  `FAIL`, utilization approximately `1.0194422195`; live invalid request and
  framework 404 use the canonical problem envelope; all 82 HTTP operations
  declared the selected problem responses at inspection time.
- Post-freeze focused tests, deterministic projections, source-free wheel/app
  binding, quick gate, hooks, immutable audit, and hosted checks remain the
  frozen next steps; no broad suite was run during implementation.

### Efficiency receipt through content freeze

- Unchanged-suite reruns: 0.
- Quick/full Python/full repository/React/FastAPI suite runs: 0.
- Maintained index refreshes: 0; the one final refresh remains pending.

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

## 2026-08-17 — Session: A1 Canonical Transport Closeout Continuation

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract`.

**Focus:** Continue the immediately preceding full A1 session record through
the repository closeout sequence. All scope, non-goals, issues, root causes,
and frozen validation selections in that A1 record remain authoritative.

### Issues encountered

- The first append used a repeated historical closeout sentence as context and
  placed the full A1 record before the final older session entry, so it was not
  the physically newest entry consumed by session validation.
- The first index-tool discovery guessed a nonexistent
  `scripts/generate_folder_indexes.py` path and stopped without writing.
- The first focused-test tool call lost its result because the output wrapper
  referenced an undefined JavaScript variable; process inspection confirmed no
  pytest process remained before the batch was relaunched once.
- The focused React command exited before collection because this isolated
  worktree had no ignored `react_app/node_modules` installation, while the
  pinned dependency tree existed only in the primary checkout.
- The first post-freeze TypeScript build found one imprecise draft-parser cast
  and two older auto-design test fixtures without the required v2 result
  envelope; lint itself passed.
- The changed-file quality batch then rejected two missing optional-dependency
  metadata names, one unused validation assignment, three import-order
  findings, three formatting findings, and a guessed obsolete frontmatter
  checker path. This was the second material rejection, so A1 returned to a
  bounded replan before further validation.
- The first candidate commit was blocked before creation: mypy found two depth
  narrowing errors and one evidence tuple type error; the API-doc hook required
  explicit `api.EffectiveDepth*` tokens; and the scripts hook found the new
  artifact verifier absent from `automation-map.json`.
- After those repairs, the maintained contract suite found that public
  `design_beam_is456` had made `d_mm` omittable, contrary to its frozen
  signature. A further bounded replan was required before another candidate.
- A grouped command changed directory to `Python` for mypy, so two following
  root-relative pytest commands did not start.
- All other A1 material issues are recorded in the full
  `A1 Canonical Truth and Transport Contract` entry above.

### Root causes and resolutions

- Confirmed root cause: the session log contains repeated closeout phrases, so
  a patch with only generic trailing context matched an earlier occurrence.
  Resolution: add this bounded continuation after the uniquely identified
  final documentation-frontmatter timing block. Proof: this continuation is
  now the last session entry and contains both mandatory sections.
- Confirmed root cause: the maintained index entrypoint is
  `./run.sh generate indexes`, backed by `scripts/generate_enhanced_index.py`;
  the guessed plural filename was never a maintained path. Resolution: discover
  the entrypoint with targeted `rg` and use the documented targeted-folder
  command for the final batch. ⚠️ TERMINAL ISSUE: guessed a nonexistent index
  script -> discovered and used the maintained `run.sh` entrypoint.
- Confirmed root cause: the command runner was correct, but the surrounding
  result-rendering snippet referenced `rest` without defining it. Resolution:
  inspect live processes first, confirm no test remained active, then launch
  the one evidence-producing batch with a minimal output wrapper.
- Confirmed root cause: linked Git worktrees do not share ignored dependency
  directories. Resolution: run the pinned lockfile install in this worktree;
  `react_app/.gitignore` keeps `node_modules` outside Git. Proof selected: the
  failed command is rerun only after the dependency repair, followed by the
  frozen TypeScript/lint checks. ⚠️ TERMINAL ISSUE: Vitest was absent in the
  isolated lane -> install the exact lockfile dependencies locally and rerun
  the failed React evidence only.
- Confirmed root cause: `Object.fromEntries` loses the exact required-key shape,
  and the two fixtures predated the canonical result carrier. Resolution: build
  the already-validated draft object with explicit required keys and give both
  fixtures a typed canonical PASS envelope. Proof: 7 impacted tests, lint, and
  the production build pass.
- Confirmed root cause: the library-version migration removed
  `importlib.metadata` names that `show_versions()` still needs for optional
  dependency reporting; the depth resolver assignment survived after its value
  stopped being consumed; and changed import/test files had not received their
  normal formatter pass. Resolution: restore only the dependency lookup names,
  retain the resolver call as validation without assignment, and apply the
  maintained formatters to the reported files. The maintained frontmatter
  entrypoint is `scripts/check_docs.py --frontmatter`, not the guessed deleted
  path. Proof: 108 impact-mapped tests, all 3 parity vectors, Ruff, Black,
  frontmatter with zero invalid records, and all 1,363 links pass.
- Confirmed root cause: optional `d_mm` was not explicitly narrowed in the
  deflection helper, branch-specific tuple inference was too narrow, the API
  checker recognizes `api.Symbol` tokens rather than prose mentions, and every
  maintained script requires one automation-map task. Resolution: add the
  explicit `None` guard and tuple annotation, document both public types with
  recognized names, and register the verifier. Proof: mypy passes 236 source
  files, API documentation passes, and automation coverage is 111/111.
- Confirmed root cause: adding `=None` changed the frozen public signature even
  though the intended contract change concerned accepted depth methods, not
  keyword presence. Resolution: retain required `d_mm: float | None`; explicit
  callers use a number, while derived-basis callers use `d_mm=None` plus the
  complete basis. Proof: 42 affected tests, 18 frozen contract tests, all 3
  parity vectors, generated signature registries, and the final source-free
  wheel proof pass.
- ⚠️ TERMINAL ISSUE: `cd Python` changed the directory for later commands in
  the same shell block -> reran the two unstarted pytest commands from the
  workspace root with `./scripts/python_runtime.sh`; both passed.
- No additional calculation, API, transport, or engineering root cause was
  discovered after the full A1 record.

### Validation through the revised content freeze

- The frozen focused Python/FastAPI selection passed. The focused React
  selection passed with 10 files and 87 tests. The impact-mapped TypeScript
  repair passed 7 tests, lint, and the production build.
- The second-rejection replan passed its 108 impact-mapped tests, all 3 parity
  vectors, changed-file Ruff/Black checks, frontmatter, and link validation.
- API manifest, classification, beam tool manifest, and OpenAPI projections are
  current; OpenAPI matches 82 endpoints and 362 schemas.
- One external wheel passed source-free Python/CLI and exact-head FastAPI import
  binding. All used effective depth 443 mm and engineering `FAIL`; installed
  identity was version `0.23.1a2` with matching distribution metadata. The
  final rebuilt wheel SHA-256 is
  `2c943b2bbb61c8a2572ee7118b08b5650628ea25b83c2f87a71ed31afc359793`.
- The first quick gate passed 10/10. The first hook attempt rejected the
  candidate and created no commit. A revised-candidate quick gate, normal hooks,
  immutable audit, and hosted checks remain after this final content freeze and
  are not written back into the candidate.
- No A2, gravity, live ETABS, Excel write-back, optimizer, solver, or release
  work was started.

## 2026-08-17 — Session: A1 Hosted FastAPI Repair

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a1-canonical-transport-contract`.

**Focus:** Repair only the single FastAPI validation failure on PR #822 at
exact head `98927f1de4a1e8f60d1d9d66bf2e8a036c2a0dd2`.

### Issues encountered

- Hosted FastAPI Validation reported 449 passing tests and one failure in
  `test_depth_boundary_matches_the_canonical_failure_vector`; the aggregate PR
  Gate failed only because that required job failed.

### Root causes and resolutions

- Confirmed root cause: when A1 restored the frozen required `d_mm` keyword,
  the production FastAPI adapter and the canonical Python test were updated to
  pass `d_mm=None` with the complete derivation basis, but the direct comparison
  call in this FastAPI test was missed. Resolution: add the same explicit
  `d_mm=None` to that test fixture. Proof selected: run only the failed test,
  then normal commit hooks and the automatically triggered hosted validation;
  do not rerun unchanged local suites.

### Boundary

- No calculation, HTTP adapter, schema, React, A2, gravity, ETABS, Excel,
  optimization, release, or professional-approval behavior is changed.

## 2026-08-17 — Session: A2 Lossless Intake and Calculation Root Causes

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/a2-lossless-intake-calculation`.

**Focus:** Implement only Packet A2 bundles F3, F4, and the calculation/advice
part of F5 on the merged A1 base. Gravity, live ETABS, Excel, write-back,
optimization, solver, release, and professional approval remain excluded.

### Issues encountered

- The first exact-extrema diagnostic used `zip(..., strict=True)` for adjacent
  boundary lists whose one-item length difference is intentional, so the point
  load reproducer stopped before calculation.
- After retaining both sides of a point-load jump, the generic critical-point
  interpolator divided by zero between two samples at the same physical
  location.
- The frozen focused batch rejected five contract assertions: two tests still
  required exactly the requested plot count, the schema freeze omitted the
  intended additive ETABS provenance, one test used a nonexistent field
  attribute, and semantic reflection could not see optional nested dataclasses.
  Its first repair then exposed the same checker's inability to validate the
  deliberately serialized canonical result-envelope mapping, so the candidate
  returned to a bounded replan.
- The architecture check rejected a direct UI-to-core import in the repaired
  building route. The first service-facade repair then selected the facade's
  visualization `Point3D` name rather than the canonical nested point model,
  and two building-route cases returned 422.
- This isolated worktree did not contain ignored React dependencies. A direct
  `npm ci` used the shell's Node 26 and warned that the project requires Node
  24, although the lockfile installation completed.
- The cumulative Python run rejected 11 legacy assertions. Eight were one
  public effective-depth error-message drift, while three audit-readiness tests
  passed immediately in the isolated failed-only selection. The reconnect
  removed the original process handle after pytest had written its exact
  failed-node cache.
- The first full repository gate passed 28 of 31 checks and rejected only the
  intentionally changed ETABS API manifest, its additive `BeamForces` schema
  snapshot, and the 404-file active-document count against the 400-file limit.
- The first normal commit-hook attempt applied deterministic formatting/newline
  fixes, then rejected the candidate because mypy treated the seven new
  provenance fields as required constructor arguments and Bandit scanned three
  pre-existing silent invalid-member skips plus the `PASS` enum string.
- Hosted PR Validation passed repository, documentation, React, and Python but
  failed three FastAPI plausibility-validator tests whose direct
  `SmartAnalysisRequest` construction omitted A2's now-required explicit
  effective depth and span.

### Root causes and resolutions

- Confirmed root cause: `zip(boundaries, boundaries[1:])` is intentionally
  non-equal. Resolution: declare `strict=False`. Evidence: exact off-grid point,
  partial UDL, mirrored-location, and load-scaling vectors pass.
- Confirmed root cause: discontinuity plotting represents left/right shear at
  identical coordinates, but continuous zero-crossing interpolation assumed a
  positive interval. Resolution: skip interpolation when adjacent coordinates
  are equal while retaining both values. Evidence: applied moment and point-load
  discontinuity tests pass without losing extrema.
- Confirmed root cause: the contract tests encoded the old display-array and
  `BeamForces` shapes, used `.canonical_unit` instead of `.unit`, and traversed
  only direct dataclass annotations. Resolution: assert the exact critical-point
  behavior, freeze the additive provenance fields, traverse optional dataclasses,
  and validate serialized `result_envelope.*` paths against
  `StructuralResultEnvelopeV2`. Evidence: all eight semantic-contract checks and
  the failed schema/load assertions pass after the bounded replan.
- Confirmed root cause: UI code bypassed the service layer, while the facade has
  two historical `Point3D` meanings. Resolution: import only `BeamGeometry` and
  `FrameType` from the service facade and pass validated point/section mappings
  into the canonical Pydantic model. Evidence: six building-route tests pass;
  architecture reports 209 files and zero violations; 668-file import validation
  reports zero broken imports. ⚠️ TERMINAL ISSUE: direct core import failed the
  architecture gate -> used the maintained service boundary and typed mappings.
- Confirmed root cause: linked worktrees do not share ignored `node_modules`,
  and the interactive shell runtime is not the repository-pinned Node version.
  Resolution: install the exact lockfile once, then run every React command
  through `./run.sh frontend`, which selected Node 24.19.0/npm 11.17.0. Evidence:
  focused Vitest, production build, and lint pass. ⚠️ TERMINAL ISSUE: isolated
  React dependencies were absent and direct npm used Node 26 -> installed once
  and used the pinned frontend wrapper for evidence.
- Confirmed root cause: `resolve_effective_depth_v1` combined non-finite,
  non-positive, and geometric depth failures into newer generic messages after
  A1, while the public beam contract still distinguishes those outcomes.
  Resolution: retain the central validator and restore field-specific finite
  messages plus the established overall-depth relationship message. Evidence:
  all eight failed depth cases, the 46 canonical transport/batch cases, and
  changed-file Ruff pass.
- Root cause unconfirmed for the three audit-readiness failures: they passed in
  the first isolated failed-only selection with no code or fixture change, so
  no product behavior was changed for them. Their exact failed nodes were
  recovered from pytest's cache and the remaining gate will determine whether
  any reproducible repository-level issue remains. ⚠️ TERMINAL ISSUE: app
  reconnect removed the completed pytest process/output handle -> recovered the
  exact failed-node set from `Python/.pytest_cache/v/cache/lastfailed` and ran
  only that set with verbose output.
- Confirmed root cause: ETABS provenance fields changed the public dataclass and
  serialized model intentionally, but the generated manifest and snapshot still
  described the pre-A2 shapes. Resolution: regenerate each canonical artifact
  once with its maintained generator; no calculation code changed.
- Confirmed root cause: four documents already marked `archived` or `deprecated`
  remained in the active documentation tree, so adding the A2 evidence record
  exposed the hard limit. Resolution: preview and move exactly those four files
  through `safe_file_move.py`, preserving content and updating ordinary links;
  the active count is now 400 and link validation remains at zero broken links.
  A tempting INDIA plan was explicitly excluded because its preview would have
  rewritten immutable historical receipts.
- Confirmed root cause: positional `Field(None, ...)` defaults were valid at
  runtime but were not inferred as optional by the configured Pydantic mypy
  plugin for the extended `BeamForces` signature. Resolution: express those
  seven defaults as `default=None`; the exact configured mypy command passes all
  236 source files and 55 affected model/adapter tests pass.
- Confirmed root cause: touching the historical multi-format adapter brought
  three broad `except Exception: continue` paths into Bandit's changed-file
  scope, while `DesignStatus.PASS` is an engineering status false positive.
  Resolution: narrow those catches to validation errors, log every skipped
  member identity/reason, and annotate only the enum literal as non-credential
  `B105`. Changed-file Bandit reports no issues. The hook's Black and EOF edits
  were retained exactly.
- Confirmed root cause: the three older tests exercised only the depth/width
  validator and were outside the focused smart-route selection, so their setup
  still relied on the removed hidden `D - 50` and `12D` assumptions. Resolution:
  add realistic explicit `effective_depth` and `span_length` values without
  changing the assertions or production model. The exact three failed tests are
  the repair evidence; the unchanged hosted jobs are not rerun locally.

### Validation through content freeze

- Source binding: base `a0458e1935e9f14bcba47a838d5fe61b46174b05`,
  `source_bound=true`.
- Focused Python/FastAPI selection completed; every initially failed assertion
  passed through impact-mapped repair without rerunning unchanged suites.
- React contract `1/1`, production build, lint, changed-file Ruff, architecture,
  import validation, and OpenAPI all pass. OpenAPI remains 82 endpoints and now
  contains 368 schemas.
- Broad Python, full repository, quick, hooks, immutable audit, push, and hosted
  checks remain the cumulative M2/G1 closeout sequence after the final index
  refresh.

## 2026-08-17 — Session: B1 Gravity Model and Load Ledger

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/b1-gravity-model-load-ledger`.

**Focus:** Freeze the exact one-storey physical model, dead/live source basis,
self-weight ownership, deterministic slab-to-footing transfer ledger, and
balance evidence. Component design, Gravity Workflow V1 orchestration, REST,
CLI, React, Excel, live ETABS, solver, lateral loads, optimization, release,
and professional approval remain excluded.

### Issues encountered

- The initial ledger labelled a combined dead reaction/action as slab
  superimposed dead or column self-weight even though it contained several
  separately owned dead sources. The numbers balanced, but the provenance label
  would have misrepresented the engineering basis.
- The first physical-model validator permitted an extra unused section and did
  not reject a second accepted source record pointing to the same canonical
  entity, so exact model/source closure was incomplete.
- The first narrow test run had two test-fixture errors: one exception-message
  regex was narrower than the actual contract and one serialized nested model
  was treated as a model object instead of a dictionary.
- A root-level targeted mypy invocation combined the `Python.` and installed
  `structural_lib.` module identities, then the package-context invocation
  exposed the known Pydantic computed-property decorator diagnostic for the
  four new computed fields.
- Adding the B1 specification and evidence raised active documentation from the
  enforced limit of 400 to 402.
- The first frozen focused batch rejected the new specification's front matter
  because it used `doc_type: specification` instead of the repository's exact
  `doc_type: spec` vocabulary. Its parallel style/type lane also started in the
  `Python/` directory with a root-relative `./scripts/` path and did not run.
- The corrected changed-file Ruff lane then rejected one import-order rule and
  two constant-attribute `getattr` calls in the new model/test files.
- The first normal commit-hook attempt passed every substantive hook but its EOF
  fixer changed the freshly generated `docs/docs-index.json`, so no commit was
  created.
- The second hook attempt proved the EOF repair but Black reformatted the new
  docs-index regression test, so it also correctly created no commit.

### Root causes and resolutions

- Confirmed root cause: the entry category type had only source categories, so
  the implementation reused a source label after aggregation. Resolution: add
  the derived `COMBINED_DEAD` category and use it only after separately traced
  dead sources combine. Evidence: the hand vector preserves nine distinct
  sources, 41 accepted ledger entries, and exact zero-residual balances.
- Confirmed root cause: set equality proved that every canonical ID appeared
  but did not prove one-to-one source mapping, and the topology count did not
  freeze the three-section boundary. Resolution: require one material, one
  section of each exact kind, complete participation, one accepted source row
  per canonical entity, and one common base elevation. Evidence: the focused
  orphan and duplicate-source vectors reject before calculation.
- Confirmed root cause: `model_dump(mode="python")` serializes nested Pydantic
  models as dictionaries, and the test expected a different but equivalent
  error phrase. Resolution: mutate the serialized dictionaries and assert the
  stable contract phrase. No production behavior changed; the repaired test
  file passes all 10 cases.
- Confirmed root cause: running configured mypy against a repository-root path
  conflicted with its `explicit_package_bases` package context, while Pydantic
  computed fields require the same narrow `prop-decorator` suppression already
  used by repository Pydantic models. Resolution: run from `Python/`, add only
  the four exact ignores, and correct real type errors exposed in the first
  pass. Evidence: configured mypy reports no issues in both new source modules.
  ⚠️ TERMINAL ISSUE: root-level targeted mypy found one file under two module
  names -> ran the exact modules from the configured Python package directory.
- Confirmed root cause: the active-doc count was already exactly at its hard
  limit before the two required B1 records. Resolution: use the safe-file-ops
  preview and maintained move script to archive exactly two already-deprecated,
  unreferenced retired Git-wrapper documents. They remain recoverable under
  `docs/_archive/2026-08`; active count is 400 and all 1,361 links pass.
- Confirmed root cause: the human term "specification" differs from the
  generator/checker's controlled `spec` metadata token, and the parallel lane's
  workdir did not match its first command path. Resolution: change only the
  front-matter token, start changed-file Ruff from the repository root, and run
  configured mypy separately from `Python/`. The impact-mapped repair repeats
  documentation and the previously unexecuted style/type evidence only.
  ⚠️ TERMINAL ISSUE: a Python-workdir lane used `./scripts/python_runtime.sh` ->
  split root Ruff and package-context mypy commands with explicit workdirs.
- Confirmed root cause: the initial formatting pass normalized layout but did
  not run Ruff's import and bugbear rules. Resolution: group the Pydantic import
  deterministically and replace both constant `getattr` calls with typed direct
  attributes; the generic canonical sorter now declares its small `id`
  protocol and the test helper declares the exact ledger type. The repair
  repeats only changed-file Ruff, configured mypy, and the 10 directly affected
  gravity vectors.
- Confirmed root cause: `generate_docs_index.py --write` serialized JSON without
  a final newline, while the mandatory EOF hook adds one. This deterministic
  mismatch had also caused hook churn in an earlier packet. Resolution: make
  the maintained generator write UTF-8 JSON with one final newline and add a
  temporary-file regression proving valid JSON and the EOF contract. The hook's
  newline-only edit is retained; gravity evidence is unchanged.
- Confirmed root cause: the narrow generator repair check ran pytest and Ruff
  but omitted Black after creating the regression file. Resolution: retain the
  hook's formatting, refresh the test index, and add Black to the failed-only
  repair evidence before the next normal hook run. All other hooks passed and
  are not independently repeated.

### Validation through content freeze

- Source binding: base `32daa0138b969be0b77b59dd33d938ad170f3a9e`,
  `source_bound=true`.
- Hand arithmetic and adverse-contract file: `10 passed`; configured mypy for
  both new modules: no issues.
- Exact expected actions are 198 kN DL and 72 kN LL at foundation level, with
  49.5 kN DL, 18 kN LL, 67.5 kN service, and 101.25 kN factored action at each
  footing destination. All 26 reconciliation records have zero residual.
- The consolidated focused selection passed `52/52`; architecture checked 210
  files with zero violations, 238-file library import validation found zero
  broken imports, and 191-file circular analysis found no cycle. Documentation
  passes all five checks at 400 active files and zero broken links. The first
  quick gate passed `10/10`.
- The first normal hooks passed every substantive check, including 238-file
  mypy and Bandit; only the repaired generator/EOF mismatch prevented the
  commit. The repaired-candidate quick gate also passed `10/10`; final hooks,
  immutable audit, push, and hosted validation remain. Broad Python and the full
  repository gate remain reserved for cumulative M2+M3 closeout.

## 2026-08-17 — Session: B2 Building Gravity Workflow V1

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/b2-gravity-workflow-v1`.

**Focus:** Bind the frozen B1 model/load identities to exact member actions,
component applicability, canonical slab/beam/column/footing APIs, a calculation
book, CLI, versioned REST routes, and a review UI. Excel, live ETABS, write-back,
optimization, multi-storey/general analysis, release, and professional approval
remain excluded.

### Issues encountered

- Eagerly exporting the new gravity service from `services/__init__.py` caused
  a circular import through the established beam service pipeline.
- The first FastAPI response converted the already validated bundle to a
  dictionary containing its computed workflow hash. Response-model validation
  then treated that computed field as unknown input and rejected the request.
- The isolated B2 worktree did not contain ignored React `node_modules`.
  Attempts to invoke Vitest from the primary checkout could not resolve the B2
  worktree's dependencies.
- A zsh inspection loop used `path` as its variable name. In zsh, `path` is tied
  to `PATH`, so normal commands became unavailable inside that shell.
- The maintained safe-move tool rewrote normal links while archiving two guides
  but missed three links that included Markdown anchors, then correctly failed
  its link gate after completing each affected move.
- A guessed standalone documentation front-matter script name was not present;
  the repository now exposes that check through its unified documentation tool.
- The first frozen architecture check found that the new FastAPI router imported
  `GravityWorkflowRequestV1` directly from the core layer.
- The strict documentation batch exposed one unchanged A2 evidence document
  that had neither the current YAML metadata contract nor the complete legacy
  Type/Audience/Status header.
- The cumulative Python run passed 6,488 cases but rejected the new CLI because
  its maintained advertised-entry-point inventory had not been updated. The
  same run reproduced three audit-readiness tests that returned an empty
  evidence set only under the `run.sh test` working directory.
- Adding B2 evidence would otherwise return the active documentation tree to
  its enforced file limit, while the user requested that up to ten obsolete
  files be removed if safely possible.

### Root causes and resolutions

- Confirmed root cause: `services.__init__` initialization reached
  `gravity_workflow`, which imports `beam_api`, before the existing service
  facade had finished initializing. Resolution: remove the eager facade export
  and keep the exact public module import
  `structural_lib.services.gravity_workflow`. Focused imports and workflow tests
  load without a cycle.
- Confirmed root cause: FastAPI revalidated a serialized response as new model
  input, while `workflow_result_hash` is an output-only Pydantic computed field
  under an `extra="forbid"` contract. Resolution: pass the validated model object
  to the response wrapper and let FastAPI serialize it once. The three focused
  REST definition/run/rejection tests pass.
- Confirmed root cause: linked worktrees share Git objects but not ignored npm
  dependencies, and a shared binary still resolves packages relative to the
  calling worktree. Resolution: perform one lockfile-pinned, offline-preferred
  `npm ci` in the B2 worktree, then run the focused React test through the
  repository runtime. Both UI cases pass. ⚠️ TERMINAL ISSUE: shared Vitest could
  not resolve worktree dependencies -> installed the exact lockfile once.
- Confirmed root cause: zsh exposes `path` as a special array synchronized with
  the executable search path. Resolution: rename the loop variable to
  `doc_file`; inspection commands then ran normally. ⚠️ TERMINAL ISSUE: using
  `path` hid `basename`, `rg`, `wc`, and `tr` -> reran with `doc_file`.
- Confirmed root cause: the safe-move reference matcher handled file links but
  did not rewrite the same paths when an anchor suffix was present. Resolution:
  repair only the three exact anchored references with `apply_patch` and rerun
  link validation before each next move. Link validation remains at zero broken
  links. The tool itself is not changed in this feature packet.
- Confirmed root cause: front-matter validation was consolidated into
  `scripts/check_docs.py` while the old single-purpose implementation is
  archived. Resolution: use `scripts/check_docs.py --frontmatter`; the unified
  check reports zero invalid front matter. ⚠️ TERMINAL ISSUE: the guessed
  `scripts/check_docs_frontmatter.py` path did not exist -> used the maintained
  unified documentation checker.
- Confirmed root cause: the router reused the type's defining module instead of
  the service boundary required for UI/transport consumers. Resolution: export
  the request contract from the exact `services.gravity_workflow` module and
  import it there in the router, without adding the eager package-level export
  that caused the earlier cycle. The affected architecture, import, REST, Ruff,
  Black, and type checks form the repair evidence.
- Confirmed root cause: the A2 evidence body predated its integration into the
  strict active-document metadata set. Resolution: add the canonical lowercase
  front matter without changing its evidence claims. The B2 documents already
  had valid front matter; the failed-only documentation batch is repeated after
  the affected index refresh.
- Confirmed root cause: the CLI parser and implementation contained
  `gravity-v1`, while `advertised_entry_points_v1.json` still described the
  preceding parser surface. Resolution: add the command as a calculation entry
  bound to its exact CLI acceptance test and advance the frozen UAT inventory
  count from 12 to 13 with an explicit entry assertion; the failed release-UAT
  node is the repair evidence.
- Confirmed root cause: `collect_contract_truth_evidence` tested repo-relative
  `scripts/...` paths against the process working directory. `run.sh test`
  correctly runs pytest from `Python/`, so all three checks were silently
  skipped and the report falsely appeared empty/PASS; an isolated root-level
  test had previously masked that defect. Resolution: bind existence checks,
  script execution paths, and subprocess cwd to the audit script's repository
  root while retaining stable relative evidence labels. The exact three failed
  nodes are the repair evidence.
- Confirmed root cause: ten documents marked deprecated or superseded still
  occupied active guide/contributing locations. Resolution: archive exactly
  those ten through `safe_file_move.py`; content remains recoverable under
  `docs/_archive/2026-08`, ordinary references point to the preserved copies,
  and widely referenced active guides plus immutable historical receipts were
  excluded from cleanup. Active Markdown documents fall from 400 to 390 before
  the required B2 evidence record is added.

### Validation through content freeze

- Source binding: base `cb49234f93283e35a87789bf631596f35c8cfcb1`,
  `source_bound=true`.
- Exact hand output: 22 actions; beam service/ULS line actions 20.25/30.375
  kN/m; moments 91.125/136.6875 kNm; shears 60.75/91.125 kN; footing ULS
  handoff 101.25 kN; all 26 ledger boundaries have zero residual.
- The first focused implementation checks passed six Python workflow cases,
  three REST cases, and two React review cases. Subsequent adverse vectors add
  exact footing and CLI coverage to the frozen consolidated selection.
- Ten safe archive moves complete with 390 active Markdown files before the B2
  evidence record and zero broken links across 1,336 internal references.
- The consolidated focused, OpenAPI, index, quick, cumulative broad, hook,
  immutable-audit, push, and hosted-check results remain the closeout sequence
  for the frozen candidate.

## 2026-08-17 — Session: E1 Excel Routine Workbench next-session freeze

**Agent:** Codex (`orchestrator`, sole writer)

**Branch:** `codex/e1-excel-routine-workbench`.

**Focus:** Stop before M4 implementation and leave a durable, source-bound E1
plan and next-session handoff on the exact merged B2 base. ETABS file/live work,
write-back, optimization, release, and professional approval remain excluded.

### Issues encountered

- The first worktree-creation tool composition embedded shell `${name:?}`
  expressions in a JavaScript template literal, so JavaScript parsed them as
  incomplete interpolation before any shell command ran.
- A dependency search passed an unmatched `Python/requirements*.txt` glob to
  zsh, which rejected the command before the intended read-only search.
- The inherited task board and next-session briefing still described the older
  Alpha release/whole-building decision state even though A1, A2, B1, and B2
  are merged and E1 is now the requested next packet.
- The first two session handoff checks rejected the new briefing because its
  `Required Reading` heading used sentence-case capitalization and its state
  table used `Complete` where the parser requires the exact `Current` row.

### Root causes and resolutions

- Confirmed root cause: two interpreters were competing for the same `${...}`
  syntax in the tool wrapper. Resolution: pass the command as a normal
  JavaScript string so `${target_path:?}` reaches zsh unchanged; the isolated
  worktree was then created at exact base `c127e4b2`. No partial Git mutation
  occurred. ⚠️ TERMINAL ISSUE: JavaScript consumed shell parameter syntax ->
  reran with a non-template command string.
- Confirmed root cause: zsh uses `nomatch` for unmatched globs. Resolution:
  enumerate maintained dependency manifests with `rg --files`, then search only
  existing exact paths. ⚠️ TERMINAL ISSUE: unmatched dependency glob aborted a
  read-only search -> used exact discovered files.
- Confirmed root cause: the durable task/handoff records predated the integrated
  master-plan execution. Resolution: add the exact E1 execution plan, replace
  the next-session handoff, and minimally reconcile task state with PRs
  #822-#825. No E1 production or test code was changed.
- Confirmed root cause: the session parser matches the required handoff heading
  and `Current`/`Next` state rows literally. Resolution: use those exact
  contract labels; the failed handoff checks are the repair evidence.

### Validation through content freeze

- Source-bound isolated lane created from merged B2 commit
  `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6`; session start reported
  `READY_LOCAL` and `Python source binding: current worktree`.
- The E1 plan freezes the selected-table journey, workbook/table identities,
  strict field and row-accounting rules, canonical status/passport/stale
  behavior, implementation map, exact validation categories, Windows Excel
  matrix cell, and G3 stop conditions.
- Implementation remains intentionally unstarted. Only planning, task, session,
  and handoff records changed; calculation, FastAPI, React, Excel, ETABS, and
  broad repository suites are therefore unchanged and not rerun.

**Git handoff receipt:** `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`
