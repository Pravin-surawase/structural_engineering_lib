# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: LIB-PRO-002 Packets I-J advertised CLI and release-signal closure
- Required ancestor: A-G merge `fe4ab025419b834c6d0f840e9492c0604ae74201` (PR #815); Packet I starts from exact fetched `origin/main` after this reviewed plan merges, and Packet J starts only after Packet I merges
- Lane: `codex/lib-pro-002-usability-refresh`; documentation/evidence owner only; unrelated worktrees preserved
- Accepted improvement: strict batch/import/HTTP/SSE/React, cross-element review truth, evidence identity, API classification, and the declared 19-case exact-wheel UAT pass the reproduced cases
- New blocker: advertised `python -m structural_lib design` still skips malformed CSV rows, exits 0, and reports a partial PASS; the 19-case exact-wheel matrix omits the CLI
- Hosted blocker: Weekly Verification run `31988837003` failed six full-suite governance/session tests because the scheduled workflow did not export the selected setup-python interpreter; the publish full-suite step has the same environment gap
- Verdict blocker: pre-bump `release preflight 0.23.1a2` passed 6,387 Python tests, 446 FastAPI tests, and the React build but incorrectly printed `READY TO RELEASE` with no exact wheel while authorization remained `HOLD`
- Release: HOLD; `docs/verification/release-publication-authorization.json` contains no exact version/tag/target authorization
- Whole-building workflow: Packet H is not activated and component-only claims remain
- Exact next action: merge this planning packet; implement and merge Packet I; then implement Packet J, run the cumulative broad/exact-wheel gates and a manually dispatched full hosted workflow, and merge only unchanged accepted heads
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; no stable, professional-approval, or whole-building claim |
| **Next** | LIB-PRO-002-I then LIB-PRO-002-J; no release-candidate mutation or publication |
| **Held** | Publication, professional approval, Packet H, INDIA-3, dependency work, branch/worktree cleanup, and unrelated retained lanes |

## Required Reading

1. [Active post-fix plan](pre-release-input-safety-and-professional-readiness-plan.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
4. [Publication authorization record](../verification/release-publication-authorization.json)
5. [Exact-candidate review receipt template](../verification/exact-candidate-review-receipt-template.json)

## Resume safely

Start Packet I in fresh source-bound lane `codex/lib-pro-002-i-cli` from exact
fetched `origin/main` after this reviewed plan merges. After Packet I's exact
head is accepted, passes hosted checks, and merges, start Packet J in a second
fresh lane `codex/lib-pro-002-j-release-signal` from the new exact
`origin/main`. Never keep both packets as active writers. Do not mutate primary
`main`, reuse historical candidate lanes, or clean unrelated worktrees.

```bash
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `fe4ab025…` as an ancestor, record each actual fetched base/head,
`source_bound=true`, no operation marker, and no new overlapping writer before
mutation. Before Packet J starts, prove Packet I is integrated and compare all
open task-owned candidate paths. Preserve every unrelated lane.

## Packet I boundary

- freeze the default valid output as the existing versioned `beams` envelope
  before replacing orchestration; migrate by a compatibility adapter rather
  than silently switching downstream consumers to the service `members` shape;
- replace the `design` CLI's row-skipping/defaulting intake with the lossless
  ledger and strict project command;
- block the whole CLI project on any malformed, missing, non-finite, unknown,
  duplicate, ambiguous, or unaccounted design-bearing record;
- require explicit effective-depth or complete derivation basis; do not supply
  hidden cover/material/load/identity values;
- freeze a versioned CLI output contract before migration; keep stdout/output
  JSON parseable, send diagnostics to stderr, and prove retained `bbs`, `detail`,
  and `dxf` consumers accept valid `design` output;
- add valid, malformed-only, mixed-validity, empty, missing-depth/cover,
  duplicate, unknown-field, and ambiguous-format CLI cases to exact-wheel UAT;
- bind all advertised calculation entry points to a generated or validated
  inventory classifying calculation entry, result consumer, inspection,
  compatibility, deprecated, and held surfaces so a future route cannot be
  omitted silently;
- retain the corrected one-storey beam result for complete canonical input.

Packet I owns only CLI/import/service/UAT and directly affected docs/tests. It
does not own workflow interpreter policy, release verdict labels, dependency
updates, new formulas, whole-building work, version bump, or publication.

## Packet J boundary

- reuse `STRUCTURAL_LIB_PYTHON="$(command -v python)"` in the Weekly
  Verification and publish full-suite steps so recursive repository launchers
  inherit the exact setup-python interpreter;
- preserve `python_runtime.sh` fail-closed selection; do not add a bare-system-
  Python fallback;
- add workflow-contract tests that fail if a hosted full suite can invoke
  `run.sh`/`python_runtime.sh` without the interpreter binding;
- replace the single preflight success label with
  `READY_TO_PREPARE_CANDIDATE`, `CANDIDATE_TECHNICALLY_READY` plus explicit
  holds, and `READY_TO_PUBLISH` only after exact authorization;
- keep pre-bump validation read-only and allow it to run before authorization,
  but never describe missing wheel/review/hosted/authorization evidence as a
  warning-compatible release-ready state;
- manually dispatch Weekly Verification on Packet J's exact remote head and
  require every full Python/FastAPI/React/docs/summary job to pass.

Packet J owns only `.github/workflows/nightly.yml`, the directly affected
publish validation step, `scripts/release.py`, focused workflow/release tests,
and directly affected release guidance. It does not bump a version, create a
tag, authorize targets, upload a package, or activate Packet H.

## Next-session execution order

1. Fetch `origin/main`; inspect all worktrees/open task-owned PRs and require a
   clean fresh Packet I lane with `source_bound=true`.
2. Freeze Packet I tests before orchestration changes: valid legacy `beams`
   output/downstream compatibility, whole-file blocking, stdout/stderr, exit
   code, row/field conservation, and advertised-entry-point inventory.
3. Implement all Packet I writes, then run its consolidated CLI, Excel-edge,
   import, batch, release-UAT, and quick checks listed in the detailed plan.
4. Complete Packet I session/handoff/index writes, hooks, immutable review,
   hosted PR checks, and unchanged-head merge. Do not start J before merge.
5. Create the fresh Packet J lane from fetched post-I `origin/main`; freeze
   workflow/preflight verdict tests, then implement all J writes.
6. Run Packet J's workflow-contract, release-script, release-environment, and
   quick checks listed in the detailed plan.
7. Freeze Packet J documentation/evidence/indexes, run normal hooks, then run
   Python, FastAPI, React, and the full canonical gate once cumulatively.
8. Build one clean technical-acceptance wheel for the unchanged current source,
   run expanded source-free UAT/public examples and exact-wheel preflight, then
   obtain immutable review, required PR checks, and the manual Weekly
   Verification receipt. This wheel is evidence for I-J, not authority to
   republish `0.23.1a1`.
9. Merge only the unchanged accepted J head, synchronize clean primary `main`,
   and stop. A later owner-authorized release-preparation session selects and
   bumps the next version, writes release notes, builds the final versioned
   wheel, repeats exact review/hosted gates, and requests exact target
   authorization.

## Acceptance and stop rules

Required final evidence is: Packet I and J base/head/tree receipts; source-
bound diagnostics; focused counts; exact wheel filename and SHA-256; expanded
entry-point matrix identity and result; public-example result; independent
review decision; PR check URLs; Weekly Verification URL; and a publication
authorization check that still returns `HOLD` until the owner separately acts.

Do not publish a package, create a tag or GitHub Release, claim professional
approval, activate Packet H, close issues/PRs, delete branches, or clean retained
worktrees without the separately required authorization.
