# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Integrate the accepted W2C predecessor, preserve and rebind the
- Completed: Rechecked PR #898 against exact base `ee50aaa3...`, exact head; Preserved the two task-owned audit plans and the historical BHEEM link,; Added a fail-closed `superseded` session-usage checkpoint for a genuinely
- Git receipt: docs/verification/etabs-w3-readiness-maintenance-git-handoff-receipt.json | sha256:2c64608e89c8ab1dacf03daf4df819172ea34b852478ab0925e796e06cf44328 | HOLD
- Git identity: codex/etabs-analysis-foundation-audit@f1873e7b910134e01abf082169d20c04d6375669 | upstream=NONE@UNKNOWN | base=origin/main@f1873e7b910134e01abf082169d20c04d6375669 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_APPLICABLE | PR=NOT_APPLICABLE#UNKNOWN | review=NOT_APPLICABLE | retention=OBSERVED
- Next action: COMMIT_PUSH_CREATE_PR_AND_MERGE_WHEN_REQUIRED_CHECKS_PASS
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W2C is integrated exactly and this maintenance packet is the only active pre-W3 candidate. Its scope is session-state repair, audit-plan refresh, safe ignored-cache cleanup, and the W3A handoff. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Maintenance** | Session-state repair, audit-plan refresh, and recoverable ignored-cache cleanup are complete on the maintenance candidate after all required local/hosted gates. No tracked React source or public API was retired. |
| **Next** | Start `ETABS-EXCEL-BEAM-W3A-DEMAND-CONTRACT` as one bounded Mac read-only contract packet from the final integrated maintenance commit. |
| **Held** | Opening ETABS/Excel, analysis/design/unlock/save, model or workbook mutation, solver/optimizer implementation, automatic write-back, release, and engineering/professional/construction approval. |

## W3A objective

Freeze public, versioned, vendor-independent contracts for exact ETABS demand
provenance before expanding design or optimization:

1. load-pattern definitions, including type and self-weight multiplier;
2. load-case catalogue and relevant typed case parameters/status;
3. response-combination type, ordered constituents, scale factors, and nested
   combination references;
4. result-selection identity and definition/catalogue digests;
5. same-row signed beam actions with member/station/step provenance;
6. explicit demand scenarios, envelope rules, and compact governing references;
7. links back to the immutable W2 baseline and exact raw station identities;
8. optional-field semantics that distinguish unavailable, not requested, not
   applicable, blocked, and present values.

W3A is contract-first and read-only. It may add types, pure validators,
serialization, fake-adapter fixtures, public API registrations, tests, and
documentation. Installed getter evidence is a later Windows packet after the
contracts and exact ETABS 23.3.1 signature matrix are accepted.

## Required acceptance

- Every design-facing action identifies the W2 baseline, member, selection,
  case/combination, station, step, component, sign, and governing rule.
- No envelope combines incompatible station rows or independently maximized
  action components.
- Load combinations preserve ordered constituents, scale factors, nesting, and
  source-definition digest; names alone are insufficient.
- Optional fields never silently default missing ETABS information to zero,
  false, or an assumed engineering value.
- The new contracts respect Core -> IS 456 -> Services -> UI import direction,
  explicit units, and deterministic canonical serialization.
- No ETABS setter, `RunAnalysis`, design command, unlock/save, section/load
  mutation, Excel write, or optimization path is introduced.
- Independent frame analysis remains `HELD_NOT_SUPPORTED` until its separate
  solver/calibration programme is accepted.

## Separate high-priority repair

The Pareto optimizer currently accepts `vu_kn` but does not use shear in
candidate feasibility. Keep it unavailable for ETABS candidate selection.
Repair it as a separate P1 packet with compatibility and result-schema review;
it does not block the read-only W3A contract work.

## Preservation rules

- Preserve all retained W2 branches, worktrees, receipts, evidence, models,
  workbooks, historical blocked runs, and public compatibility surfaces.
- Mac owns normal W3A development/review/integration. Windows remains the
  installed Excel/ETABS evidence host for a separately bounded getter packet.
- Move source only through GitHub. Proprietary model/workbook/result payloads
  remain off Git and are referenced only through bounded digests/counts.
- Do not compact the session archive or retire React/hooks/docs/public APIs in
  W3A; those require separate caller, successor, recovery, and owner evidence.

## Required Reading

1. [ETABS data, beam-analysis, and optimization foundation](etabs-data-analysis-optimization-foundation-plan.md)
2. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
3. [ETABS, Excel, professional-attestation, and surface-retirement audit](etabs-excel-professional-surface-audit.md)
4. [Transactional W2C installed evidence](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json)
5. [Windows ETABS/Excel recurring-pitfall guide](../guides/excel-etabs-python-bridge-pilot.md#windows-etabsexcel-recurring-pitfall-checklist)
6. [Current task board](../TASKS.md)
7. [Newest session entry](../SESSION_LOG.md)

## Starter prompt

Start `ETABS-EXCEL-BEAM-W3A-DEMAND-CONTRACT` from the exact integrated
W3-readiness maintenance predecessor. Implement one bounded Mac read-only
packet for typed load-pattern, load-case, response-combination, selection,
same-row beam-action, scenario/envelope, and governing-reference contracts.
Keep vendor COM arrays inside adapters, preserve explicit units and canonical
digests, fail closed on missing/ambiguous definitions, and add focused tests
and public API registration only where the accepted contract needs it. Do not
open ETABS/Excel, add setters, run analysis/design, mutate models/workbooks,
repair the Pareto optimizer in the same packet, start the local frame solver,
or claim engineering/professional approval.
