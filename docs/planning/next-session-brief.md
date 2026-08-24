# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Repair only the G0-bounded IS 13920 beam-column-joint SCWB
- Git receipt: docs/verification/india-3-joint-r1-git-handoff-receipt.json | sha256:11f497065d6553de74732bd19dd159eb33e4f91d10e701cb69fbb95c8ffd79e1 | HOLD
- Git identity: codex/india-3-joint-r1@20b60a047e5c6d88b800f7094dd64fcf4bebad28 | upstream=origin/main@20b60a047e5c6d88b800f7094dd64fcf4bebad28 | base=origin/main@20b60a047e5c6d88b800f7094dd64fcf4bebad28 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: CREATE_IMMUTABLE_CANDIDATE_AFTER_FOCUSED_QUICK_AND_HOOKS
<!-- HANDOFF:END -->

## Latest Handoff

| State | Boundary |
|---|---|
| **Current** | `INDIA-3-JOINT-R1` has completed its bounded local repair on source-bound `codex/india-3-joint-r1` from exact hosted source-metadata merge `20b60a04` |
| **Decision** | The joint SCWB contract uses fixed factor 1.4 and explicit direction, factored-axial-load capacity basis, applicability, and interior/exterior topology |
| **Next** | Integrate this unchanged candidate with required hosted checks green, then create `INDIA-3-BEAM-R1`; it was not started here |
| **Source** | IS 13920:2016 First Revision plus Amendment 1 (2017) and Amendment 2 (2020); 2021 reaffirmation is not a new edition; the draft successor is not used |
| **Held** | Whole-joint acceptance from one directional case, beam/column repairs, walls/foundations, IS 875/1893, source/distribution/support/version/release/professional-use changes, and branch/worktree/archive/source/alias deletion |

## Joint repair result

- The reproduced G0 case now fails truthfully: column capacity 250 kNm against
  beam capacity 200 kNm requires 280 kNm, not the former 220 kNm false-pass
  threshold. Equality at exactly 1.4 passes.
- The IS 13920 entry point has no factor argument. Every result remains fixed
  to 1.4 and records the standard plus source/amendment basis.
- Each bounded result identifies one principal plane, one shaking direction,
  the beam capacity direction, the opposing column capacity direction, and the
  top/bottom factored axial loads used for column capacities. It explicitly
  refuses a whole-joint claim from one directional case.
- Roof joints and flat-slab systems cannot receive a passing or failing result.
  Interior joints require two beam sides; left and right exterior joints each
  require exactly their one present beam side.
- The code-namespace owner and 29 direct tests are the only callers. No package
  export, service, FastAPI route, React/Excel surface, capability promotion,
  package version, release, or professional-use state changed.

## Frozen follow-on sequence

1. Merge the unchanged green `INDIA-3-JOINT-R1` candidate. Do not delete its
   branch, worktree, archive, source copy, alias, or any unrelated lane.
2. Create `INDIA-3-BEAM-R1` as the next sequential formula/contract packet; it
   was intentionally not started by this task.
3. `INDIA-3-COLUMN-R1` remains the separately frozen repair packet after beam.
4. `INDIA-3-IS13920-M0` runs cumulative source, benchmark, transport,
   capability, package, and qualified-review acceptance after the repairs.
5. Wall/foundation detailing and the later IS 875/1893 sequence remain separate.

## Required Reading

1. [Joint repair evidence](../verification/india-3-joint-r1-evidence.json)
2. [G0 decision evidence](../verification/india-3-g0-is13920-audit-decision.json)
3. [Source metadata repair evidence](../verification/india-3-source-meta-r1-evidence.json)
4. [G0 truth-audit plan](india-3-g0-is13920-truth-audit.md)
5. [Private source-library boundary](../verification/india-3-g0-private-source-library-evidence.md)
6. [Generated Indian-code capability truth](../verification/indian-code-capability-coverage.json)
7. [Current task board](../TASKS.md)
