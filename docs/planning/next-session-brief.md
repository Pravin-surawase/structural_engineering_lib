# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Preserve the second blocked W3D continuation and repair only the undocumented ETABS 23 auto-flag interpretation
- Completed: Merged R1 in PR #904; one clean continuation passed zero-state handling and stopped on raw `Auto=5`; added exact `raw_auto_flag` plus five-state Boolean evidence without a live retry; 24 focused tests, Ruff and Mypy pass
- Git receipt: docs/verification/etabs-w3d-auto-flag-semantics-repair-git-handoff-receipt.json | sha256:1f63e2c3f5815fe88db4d3118a585119da6cfb3f90e084b6591b6b48d2738b8b | HOLD
- Git identity: codex/etabs-w3d-auto-flag-repair-windows@e16870d0613b27cedc0f0f2ede4c5d205305bba8 | upstream=NONE | base=origin/main@e16870d0613b27cedc0f0f2ede4c5d205305bba8 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: COMPLETE_W3D_R2_GATES_AND_CREATE_CANDIDATE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W3D-R1 is accepted through PR #904 merge `e16870d0613b27cedc0f0f2ede4c5d205305bba8`, tree `a6584729c159fd8bffaf3bccad824789fc398715`. One clean continuation passed the repaired zero-state sentinel, then correctly blocked with no partial catalogue when ETABS 23.3.1 returned undocumented raw `Auto=5`; the copied model stayed exact. A separate R2 candidate retains the raw integer and makes only its Boolean interpretation `UNAVAILABLE`. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Complete. The owner explicitly authorized the dependency-ordered W3 campaign; every packet still requires its exact predecessor and packet-specific stop conditions. |
| **Next** | Complete API/docs/quick/hook/hosted review for R2, merge only its unchanged head, then create a new clean continuation from its exact merge/tree before one further W3D attempt. Preserve both earlier blocked evidence roots permanently. |
| **Held** | Do not rerun live evidence from dirty or unmerged R2 source. Do not coerce raw `Auto=5` to a Boolean. W3D must not select output, run analysis/design, call `FrameForce`, unlock, save, write Excel or mutate the copied model. Real prior initial-case names remain blocked. Independent frame analysis, release and engineering/professional/construction approval remain unapproved. |

## W3A-W3C accepted and W3D sentinel-repair outcome

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
design/auto identity and decodes only proved caller-supplied shapes, retaining every call
verdict/source identity, and returns no partial catalogue after a provider,
shape, return-code, identity/status, selection, normalization or capacity
failure. W3C created no COM object, called no live getter and makes no
live-model claim. W3C is accepted in PR #903. The first W3D live attempt then
proved that installed ETABS returns literal `None` for the zero unstressed
linear-static initial condition. CSI's official getter documentation confirms
blank/`None` are zero-state sentinels. The separate repair retains the raw
sentinel through `LinearStaticInitialConditionV1`, normalizes only blank/`None`
to `ZERO_UNSTRESSED`, and continues to block every real prior-case name.
R1 merged in PR #904. The clean continuation then proved ETABS 23.3.1 may
return raw `Auto=5` for an internal case although CSI's published mapping only
defines 0/1. R2 retains that exact integer in `raw_auto_flag`; `is_auto` is
`PRESENT` only for documented 0/1 and otherwise `UNAVAILABLE`. No truthiness
coercion or live retry from unmerged source is permitted.

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

After the auto-flag repair merges unchanged, create another fresh continuation
worktree from its exact merge/tree and bind the source-selected runtime to that
worktree. Reprove the
authorized copied-model path/hash/size/mtime, ETABS 23.3.1 identity, lock,
units, complete case statuses and current result-selection state before a live
getter. Use the accepted W3B source digest and W3C adapter to extract one
complete catalogue and the linked same-row demand snapshot. Reconcile direct
and source-bound REST canonical hashes, then prove model file identity, lock,
units and selection unchanged. Preserve and reference the first blocked attempt;
do not overwrite or relabel it. Do not select outputs, run analysis/design,
call `FrameForce`, unlock, save, write Excel or mutate the copied model during
W3D.

### Completed W3D R2 operator checklist

- [x] User explicitly authorized W3D as part of the full W3 campaign.
- [x] `origin/main`, W3C merge/tree, evidence and contract hashes match.
- [x] Worktree is operation-free and unrelated retained work is preserved.
- [x] Only W3B-proved getter operations and exact list/tuple/scalar semantics
  are decoded; every call records source, shape, return and verdict evidence.
- [x] Both live reads were getter-only and returned no partial value on their
  exact semantic guards; the copied model identity stayed unchanged.
- [x] Official CSI semantics plus installed 23.3.1 evidence prove blank/`None`
  mean zero unstressed initial conditions.
- [x] R1 retains and accepts only documented zero-state forms; every actual
  prior-case name remains blocked.
- [x] R2 retains raw `Auto=5` and makes its Boolean meaning `UNAVAILABLE`; it
  does not guess, discard the case, or weaken other fail-closed guards.
- [x] No live rerun occurred after R2 code modification; a clean merged source
  is mandatory before the next continuation.
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
