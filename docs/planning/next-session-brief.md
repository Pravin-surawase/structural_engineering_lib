# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Repair only the confirmed software safety and verification defects
- Git receipt: docs/verification/lib-pro-008-pre-india3-safety-git-handoff-receipt.json | sha256:01e9d4015048729b98d28f5035c496321a47dc79f7a7fb065e7709ea46ec52b2 | HOLD
- Git identity: codex/lib-pro-008-pre-india3-safety@e2fac7419551988def59101ac63a5f8e491bc7a2 | upstream=NONE@UNKNOWN | base=origin/main@e2fac7419551988def59101ac63a5f8e491bc7a2 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: RUN_FROZEN_QUICK_FULL_AND_STAGED_HOOKS
<!-- HANDOFF:END -->

## Latest Handoff

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-008` is frozen on `codex/lib-pro-008-pre-india3-safety` from exact hosted `e2fac741` |
| **Decision** | Resume `INDIA-3-G0` only after this unchanged candidate passes local and hosted integration |
| **Next** | Run immutable-candidate closeout, merge only unchanged green work, then resume the bounded INDIA-3-G0 audit |
| **Repaired** | Torsion non-finite intake, WebSocket hidden defaults/loose cases, compatibility environment drift/stale ledger, documentation CI ownership, and unsupported stirrup geometry |
| **Held** | Version bump/publication, IS 13920 formula change or acceptance, broader IS 875/1893 work, professional use, and any branch/worktree/archive deletion |

## Exact packet state

- The load-case-only WebSocket reproducer now returns a sanitized input error;
  no `check_result` calculation data is emitted.
- Every public torsion scalar rejects `NaN`, infinity, booleans, and non-real
  values before arithmetic can create a false-safe result.
- Compatibility scanning uses Git's tracked source allowlist in a checkout and
  a generated-output-filtered fallback in a source archive. The regenerated
  ledger contains 1,502 caller records and zero ambiguous callers.
- Documentation validation now runs compatibility freshness, so a docs-only
  public-API reference cannot bypass the check.
- `compute_stirrup_path` validates its full geometry boundary and rejects 4/6
  legs because one closed-loop path cannot represent disconnected inner legs.
- The separately dirty detached worktree and the private source archive remain
  untouched.

## Local evidence and next action

- Focused Python passed 187 tests; the affected geometry module passed 69 after
  the one audit-driven repair. Focused FastAPI passed 12 tests.
- Compatibility generation/check passes with no classification-registry drift.
- Readiness remains truthfully `PARTIAL`: 23/24 checks pass, zero fail, and the
  longstanding 359-parameter input-ownership diagnostic is the sole warning.
- Run one frozen quick gate, one full 31-check gate, normal staged hooks, create
  the immutable candidate, run read-only session end, and require all hosted
  checks. Merge only if the reviewed head is unchanged and green.
- After merge, resume the already-frozen G0 audit order below. Do not begin with
  formula edits.

## Bounded INDIA-3-G0 audit order

1. Resolve exact IS 13920 edition/amendment applicability for each governing
   beam, column, and joint page.
2. Map every current input, formula/limit, output, default, status, and failure
   behavior to confirmed source or an explicit hold.
3. Freeze independent replayable benchmarks and invalid/out-of-domain cases.
4. Reconcile core, service, package, transport, tests, documentation, and
   generated capability truth.
5. Classify each family `ACCEPT_CURRENT_BOUNDED`,
   `REPAIR_PACKET_REQUIRED`, or `HOLD` before implementation packets.

## Required Reading

1. [LIB-PRO-008 evidence](../verification/lib-pro-008-pre-india3-safety-evidence.json)
2. [G0 truth-audit plan](india-3-g0-is13920-truth-audit.md)
3. [G0 readiness evidence](../verification/india-3-g0-truth-audit-readiness.json)
4. [Private source-library boundary](../verification/india-3-g0-private-source-library-evidence.md)
5. [Generated Indian-code capability truth](../verification/indian-code-capability-coverage.json)
6. [Current task board](../TASKS.md)
