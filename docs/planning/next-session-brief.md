# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Repair only the G0-bounded IS 13920 rectangular-column geometry,
- Git receipt: docs/verification/india-3-column-r1-git-handoff-receipt.json | sha256:793eb731063af7c2ba7d412990ea9ac33ea4f6700ed2400bc7ed86cea084a5a9 | HOLD
- Git identity: codex/india-3-column-r1@cfe29f890e62c40546f3a91c8810e1daf7c0d722 | upstream=origin/main@cfe29f890e62c40546f3a91c8810e1daf7c0d722 | base=origin/main@cfe29f890e62c40546f3a91c8810e1daf7c0d722 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: CREATE_IMMUTABLE_CANDIDATE_AFTER_FOCUSED_QUICK_AND_HOOKS
<!-- HANDOFF:END -->

## Latest Handoff

| State | Boundary |
|---|---|
| **Current** | `INDIA-3-COLUMN-R1` has completed its bounded local repair on source-bound `codex/india-3-column-r1` from exact hosted beam merge `cfe29f89` |
| **Decision** | The rectangular-column contract requires explicit applicability, actual core/hoop geometry, and provided confinement; both accepted area expressions govern and longitudinal steel remains not evaluated |
| **Next** | Integrate this unchanged candidate with required hosted checks green, then create `INDIA-3-IS13920-M0`; it was not started here |
| **Source** | IS 13920:2016 First Revision plus Amendment 1 (2017) and Amendment 2 (2020); IS 456:2000 Cl 26.5.3.1(a) is a separately labeled companion limit source |
| **Held** | Non-rectangular columns, derived applicability, provided longitudinal-steel compliance, cumulative IS 13920 acceptance, walls/foundations, IS 875/1893, source/distribution/support/version/release/professional-use changes, and branch/worktree/archive/source/alias deletion |

## Column repair result

- The accepted 400 x 500 mm benchmark returns maximum spacing 100 mm,
  minimum confinement length 500 mm, and governing required hoop area
  222.28915662650604 mm2. The independent low-core-ratio case now returns the
  second-expression result 277.10843373493975 mm2 instead of the former
  181.03719224724983 mm2.
- The exact 300 mm dimension and 0.4 aspect-ratio boundaries pass; values below
  either boundary fail. NaN and infinity cannot return a calculation or a
  success-like result.
- The existing package/service and HTTP route now require the actual gross/core
  and hoop geometry, provided spacing/length/area, rectangular topology, and a
  caller-confirmed applicability decision with its basis. No 40 mm cover or
  core geometry is invented.
- `is_compliant` covers only geometry and the explicitly provided special
  confinement. The 0.8% and 4.0% values remain visible as IS 456 companion
  limits and are explicitly `NOT_EVALUATED` because no provided longitudinal
  steel is accepted.
- No new route or product workflow was added, and the generated capability
  status was not promoted. Beam/joint/wall/foundation/IS 875/IS 1893 formulas,
  React/Excel, package version, release, and professional-use state did not
  change.

## Frozen follow-on sequence

1. Merge the unchanged green `INDIA-3-COLUMN-R1` candidate. Do not delete its
   branch, worktree, archive, source copy, alias, or any unrelated lane.
2. Create `INDIA-3-IS13920-M0` for cumulative source, benchmark, unsafe-case,
   transport, capability, package, and qualified-review acceptance. It was
   intentionally not started by this task.
3. Wall/foundation detailing and the later IS 875/1893 sequence remain
   separate.

## Required Reading

1. [Column repair evidence](../verification/india-3-column-r1-evidence.json)
2. [G0 decision evidence](../verification/india-3-g0-is13920-audit-decision.json)
3. [Beam repair evidence](../verification/india-3-beam-r1-evidence.json)
4. [Joint repair evidence](../verification/india-3-joint-r1-evidence.json)
5. [Source metadata repair evidence](../verification/india-3-source-meta-r1-evidence.json)
6. [G0 truth-audit plan](india-3-g0-is13920-truth-audit.md)
7. [Private source-library boundary](../verification/india-3-g0-private-source-library-evidence.md)
8. [Generated Indian-code capability truth](../verification/indian-code-capability-coverage.json)
9. [Current task board](../TASKS.md)
