# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Run the single cumulative P1-P7 software acceptance across broad
- Git receipt: docs/verification/lib-pro-007-m0-cumulative-acceptance-git-handoff-receipt.json | sha256:314ac53c4dfcfd22d304ef36bc6ea731a76efc554e61e780604fd1ed3ec02156 | HOLD
- Git identity: codex/lib-pro-007-m0-cumulative-acceptance@823b39896a53fde7e4c5e0805faa8ec02e075ee5 | upstream=origin/main@823b39896a53fde7e4c5e0805faa8ec02e075ee5 | base=origin/main@823b39896a53fde7e4c5e0805faa8ec02e075ee5 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: RUN_FROZEN_QUICK_FULL_AND_STAGED_HOOKS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-007-M0` content is frozen from exact hosted P7 commit `823b3989` / tree `e5b1e9ee`; cumulative suites, exact-wheel vectors, and repaired production website journey are green |
| **Next** | Run the one frozen quick gate, one full repository gate, and normal staged hooks; merge only the unchanged reviewed head after every required hosted check passes |
| **Why** | M0 closes P1-P7 as a cumulative software milestone and records the three integration repairs instead of relying on packet-local checks |
| **Held** | Release/tag/publication, professional or engineering-use approval, live ETABS/EDB/model control/save/write-back, INDIA-3 formulas/source promotion, and branch/worktree deletion |

## M0 candidate outcome

- P7 merged through PR #859 at hosted `823b3989`, reviewed candidate
  `c9589815`, with exact candidate/merged tree `e5b1e9ee`; M0 starts from that
  exact tree and preserves every unrelated lane plus INDIA-3 candidate
  `9c976b1f`.
- The repaired broad Python suite passes 6,934 tests; FastAPI passes 491; React
  passes 283 plus lint and production build. Architecture, imports, circular
  imports, and cross-layer parity are green.
- Exact wheel `0a42d90e…347ca` imports only from an isolated installation,
  passes 5,920 tests and CLI job/report flow, preserves Python/CLI/FastAPI
  `d_mm=443` with truthful `FAIL`, and passes all 29 negative-UAT cases.
- The production website loads catalogue 1.3.0, changes calculation identity
  after a quick-beam input edit, and runs the maintained gravity example with
  26 zero-residual load boundaries, immutable identities, and truthful
  `HOLD 6 / PASS 5`. Console errors, page errors, and failed requests are zero.
- M0 changes no Excel/Office.js surface, structural formula, public export, or
  public signature. Installed Windows Excel is
  `NOT_REQUIRED_UNCHANGED_SURFACE`; no retirement candidate is activated.

## M0 closeout boundary

- Treat the machine evidence as cumulative software compatibility only. It is
  not release authorization, whole-standard completion, professional approval,
  or engineering-use approval.
- Run `./run.sh check --quick` once on frozen content, `./run.sh check` once,
  then normal staged hooks once during the immutable commit.
- After an unchanged green merge, create a fresh INDIA-3 lane from the new
  hosted `main`, compare and transplant only reviewed task-owned changes from
  preserved candidate `9c976b1f`, and do not rewrite the original lane.

## Required Reading

1. [M0 cumulative evidence](../verification/lib-pro-007-m0-cumulative-acceptance-evidence.json)
2. [Product-foundation convergence plan](lib-pro-007-product-foundation-convergence.md)
3. [P7 compatibility ledger](../reference/api-compatibility-ledger.json)
4. [P7 machine evidence](../verification/lib-pro-007-p7-compatibility-convergence-evidence.json)
5. [P6 cross-surface parity evidence](../verification/lib-pro-007-p6-cross-surface-parity-evidence.json)
6. [Current task board](../TASKS.md)
7. [Git workflow single source](../git-automation/git-workflow-single-source.md)
