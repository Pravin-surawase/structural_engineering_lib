# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Audit only the installed ETABS 23.3.1 managed assembly, x64 type
- Completed: Rebound a fresh W3B worktree to exact accepted W3A merge/tree and proved the; Reproved ETABS 23.3.1.4563, signed application/managed-assembly identities,; Statically proved all 15 accepted operations, including managed signature,
- Git receipt: docs/verification/etabs-w3b-installed-getter-signature-git-handoff-receipt.json | sha256:05dcb3d7a4c7fbac80d1900177772423016fcd0ef7a3898c6913045a6c2f20ad | HOLD
- Git identity: codex/etabs-w3b-installed-signatures-windows@3ce8c81ba26448d6a3b319bc6288864dcfaed189 | upstream=origin/main@b7351bb5a3269e4281ba7b34c780e45d2599749b | base=origin/main@b7351bb5a3269e4281ba7b34c780e45d2599749b | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: CREATE_W3B_CANDIDATE_COMMIT
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W3A is accepted in PR #901: merge `b7351bb5a3269e4281ba7b34c780e45d2599749b`, tree `b895008b4f4d3212b6d1e1fe28894e07efc2c7df`. W3B statically proves all 15 installed ETABS 23.3.1.4563 getter signatures on `codex/etabs-w3b-installed-signatures-windows` and is awaiting candidate freeze, hosted review and normal merge. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Complete. The owner explicitly authorized the dependency-ordered W3 campaign; every packet still requires its exact predecessor and packet-specific stop conditions. |
| **Next** | Merge unchanged W3B only after all required checks pass; then implement W3C's transport-neutral fake-COM catalogue adapter from the exact proved operation matrix and both fail-closed guards. |
| **Held** | W3B made no COM object/getter call and no live model-value claim. Model mutation remains held until the later expressly bounded copied-model packets; release and engineering/professional/construction approval remain unapproved. |

## W3A accepted and W3B candidate outcome

Accepted W3A freezes public, versioned, vendor-independent contracts for
exact ETABS demand provenance before expanding design or optimization:

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

W3B binds that accepted surface to ETABS 23.3.1.4563 static installed metadata.
All 15 operation signatures are proved. W3C must use `GetTypeOAPI_1` for full
case design/auto identity and must block any nonblank linear-static initial
case until that semantic is represented publicly. W3B created no COM object,
called no getter and makes no live-model claim.

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
  solver and model-specific calibration packets are both separately accepted.

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

## Next W3C handoff

After W3B merges unchanged, create a fresh packet worktree from its exact
merge/tree. Implement only the statically proved getters behind the ETABS
service boundary using fake list/tuple/scalar providers. Retain every operation
verdict/source identity; decode nonzero CSI returns, count mismatches, source
drift and capacity errors as fail-closed blockers. Use `GetTypeOAPI_1`, require
`Auto` in `{0, 1}`, and block nonblank `GetInitialCase` values. Do not open or
attach ETABS/Excel during W3C.

### Completed W3B operator checklist

- [x] User explicitly authorized W3B as part of the full W3 campaign.
- [x] `origin/main`, W3A merge/tree and contract hashes match.
- [x] Worktree is operation-free and unrelated retained work is preserved.
- [x] Installed application, assembly, typelib, wrapper, Python and comtypes
  identities are recorded with hashes.
- [x] No ETABS/Excel process was opened, attached or automated; no `SapModel`
  call occurred.
- [x] Every accepted getter has exact signature/default/return/container
  evidence and a verdict.
- [x] No arbitrary case payload mapping was invented; both discovered guards
  fail closed.
- [x] Static compatibility is distinguished from live model, solver,
  engineering and professional acceptance.
- [x] No secrets, proprietary model/workbook/result bytes or generated vendor
  wrapper source entered Git.

## Required Reading

1. [W3 ETABS data, beam-analysis, and optimization master plan](etabs-data-analysis-optimization-foundation-plan.md)
2. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
3. [ETABS, Excel, professional-attestation, and surface-retirement audit](etabs-excel-professional-surface-audit.md)
4. [Transactional W2C installed evidence](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json)
5. [Windows ETABS/Excel recurring-pitfall guide](../guides/excel-etabs-python-bridge-pilot.md#windows-etabsexcel-recurring-pitfall-checklist)
6. [Current task board](../TASKS.md)
7. [Newest session entry](../SESSION_LOG.md)
