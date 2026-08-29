# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Implement only W3C's transport-neutral ETABS catalogue adapter from the exact accepted W3B getter matrix
- Completed: Bound a fresh W3C worktree to exact W3B merge/tree; added complete/no-partial proved-shape decoding and seven public exports; passed 24 focused tests, Ruff, Mypy, API controls and quick gate 10/10 without application access
- Git receipt: docs/verification/etabs-w3c-catalogue-adapter-git-handoff-receipt.json | sha256:12b8413ee4783fa3f6a57f0dd90812477875611f909e1972ddf06c0b95715cf8 | HOLD
- Git identity: codex/etabs-w3c-catalogue-adapter-windows@94c058f108351dd78195be5ee228b78da1d6a635 | upstream=NONE | base=origin/main@94c058f108351dd78195be5ee228b78da1d6a635 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: CREATE_W3C_CANDIDATE_COMMIT
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W3A is accepted in PR #901. W3B is accepted in PR #902: merge `94c058f108351dd78195be5ee228b78da1d6a635`, tree `a93377058f7c04445a311a4267cfd2fb4f21ef11`. W3C implements the transport-neutral catalogue adapter on `codex/etabs-w3c-catalogue-adapter-windows` and is awaiting candidate freeze, hosted review and normal merge. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Complete. The owner explicitly authorized the dependency-ordered W3 campaign; every packet still requires its exact predecessor and packet-specific stop conditions. |
| **Next** | Merge unchanged W3C only after all required checks pass; then create a fresh W3D worktree from its exact merge/tree and run the separately bounded live getter-only acceptance on the positively identified copied model. |
| **Held** | W3C imported/created no COM object, called no live getter and made no live model-value claim. W3D must not select output, run analysis/design, unlock, save, write Excel or mutate the copied model. Independent frame analysis, release and engineering/professional/construction approval remain unapproved. |

## W3A-W3B accepted and W3C candidate outcome

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
All 15 operation signatures are proved. W3C uses `GetTypeOAPI_1` for full case
design/auto identity, accepts `Auto` only as exact zero/one, and blocks any
nonblank linear-static initial case until that semantic is represented
publicly. It decodes only proved caller-supplied shapes, retains every call
verdict/source identity, and returns no partial catalogue after a provider,
shape, return-code, identity/status, selection, normalization or capacity
failure. W3C created no COM object, called no live getter and makes no
live-model claim.

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

## Next W3D handoff

After W3C merges unchanged, create a fresh packet worktree from its exact
merge/tree and bind the source-selected runtime to that worktree. Reprove the
authorized copied-model path/hash/size/mtime, ETABS 23.3.1 identity, lock,
units, complete case statuses and current result-selection state before a live
getter. Use the accepted W3B source digest and W3C adapter to extract one
complete catalogue and the linked same-row demand snapshot. Reconcile direct
and source-bound REST canonical hashes, then prove model file identity, lock,
units and selection unchanged. Do not select outputs, run analysis/design,
unlock, save, write Excel or mutate the copied model during W3D.

### Completed W3C operator checklist

- [x] User explicitly authorized W3C as part of the full W3 campaign.
- [x] `origin/main`, W3B merge/tree, evidence and contract hashes match.
- [x] Worktree is operation-free and unrelated retained work is preserved.
- [x] Only W3B-proved getter operations and exact list/tuple/scalar semantics
  are decoded; every call records source, shape, return and verdict evidence.
- [x] `GetTypeOAPI_1`, exact `Auto` and nonblank-initial-case guards are enforced.
- [x] No ETABS/Excel process was opened, attached or automated; no live
  `SapModel` call occurred and no REST surface was added.
- [x] Every tested failure returns a stable issue and no partial normalized
  request/catalogue.
- [x] Transport-neutral compatibility is distinguished from live model,
  solver, engineering and professional acceptance.
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
