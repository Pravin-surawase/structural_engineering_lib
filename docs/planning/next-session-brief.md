# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Complete the bounded existing-surface audit for IS 13920 beam,
- Git receipt: docs/verification/india-3-g0-audit-decision-git-handoff-receipt.json | sha256:56f0737301666a236d48819aacf4fcf45aaeb79b6b9e6c460945b43fb448bdd5 | HOLD
- Git identity: codex/india-3-g0-acceptance@482de736b28059b8a87336dccfd6ef00bdcc57ba | upstream=origin/codex/india-3-g0-acceptance@482de736b28059b8a87336dccfd6ef00bdcc57ba | base=origin/main@3bcc34223d8eaf236c62a5f54dfe4b7960876457 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: REPAIR_GENERATED_COMPATIBILITY_LEDGER_AND_RERUN_FAILED_DOCUMENTATION_PATH
<!-- HANDOFF:END -->

## Latest Handoff

| State | Boundary |
|---|---|
| **Current** | `INDIA-3-G0` is complete on source-bound `codex/india-3-g0-acceptance` from exact post-LIB-PRO-008 hosted baseline `3bcc3422` |
| **Decision** | Beam, column, and joint are each `REPAIR_PACKET_REQUIRED`; no current IS 13920 family is engineering-accepted |
| **Next** | Integrate this unchanged decision candidate, then start only one separately authorized repair packet, beginning with source metadata or the selected beam/column/joint family |
| **Source** | IS 13920:2016 First Revision plus Amendment 1 (2017) and Amendment 2 (2020); 2021 reaffirmation is not a new edition; the draft successor is not used |
| **Held** | Formula implementation in G0, current support acceptance, walls/foundations, IS 875/1893, release, professional use, and branch/worktree/archive deletion |

## G0 result

- The private archive verifies 25 documents, 27 aliases, 732 cached pages, and
  142 visual-review pages. Two byte-distinct copies of each amendment are
  normalized-text equal page by page and remain preserved.
- The beam family uses the pre-amendment eight-bar spacing limit instead of six,
  accepts the exact 0.3 ratio boundary, and can report non-finite or incomplete
  requirement output as compliant.
- The column family uses incorrect post-amendment clause references, returns
  longitudinal limits unmapped to the reviewed source, omits the second
  governing rectangular confinement-area expression, and adds a hidden 40 mm
  cover/core assumption while reporting compliance without provided steel.
- The joint family uses a default factor of 1.1 instead of 1.4. A frozen case
  with column capacity 250 kNm and beam capacity 200 kNm is a source failure but
  a current-code pass. Direction, axial-load capacity basis, and applicability
  are also absent from the contract.
- Existing software tests remain baseline evidence only; they reproduce several
  outdated constants and therefore do not establish source correctness.

## Frozen follow-on sequence

1. `INDIA-3-SOURCE-META-R1` corrects private document-kind/renderability
   metadata without deleting or distributing source material.
2. `INDIA-3-BEAM-R1`, `INDIA-3-COLUMN-R1`, and `INDIA-3-JOINT-R1` remain
   independent formula/contract repair packets. The owner selects their order.
3. `INDIA-3-IS13920-M0` runs cumulative source, benchmark, transport,
   capability, package, and qualified-review acceptance after the repairs.
4. Wall/foundation detailing and the later IS 875/1893 sequence remain separate.

## Required Reading

1. [G0 decision evidence](../verification/india-3-g0-is13920-audit-decision.json)
2. [G0 truth-audit plan](india-3-g0-is13920-truth-audit.md)
3. [G0 readiness snapshot](../verification/india-3-g0-truth-audit-readiness.json)
4. [Private source-library boundary](../verification/india-3-g0-private-source-library-evidence.md)
5. [Generated Indian-code capability truth](../verification/indian-code-capability-coverage.json)
6. [Current task board](../TASKS.md)
