# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Repair only the confirmed Pareto shear-feasibility and unknown-objective defects while preserving every W3 claim and application boundary.
- Completed: Routed each flexure-valid candidate through maintained IS 456 shear using explicit `asv_mm2`; maximum stress and supplied stirrup capacity both govern.; Added separate flexure/shear/stirrup utilization and exact shear/spacing evidence; compatibility `utilization` is their truthful governing maximum.; Rejected empty/unknown objectives; Python, FastAPI/OpenAPI, generated compatibility data and React expose one coherent additive contract.
- Git receipt: docs/verification/etabs-w3r-pareto-shear-feasibility-git-handoff-receipt.json | sha256:eb3f6f87cc823cba4116a3fe43c8c08006182ee0e399cb607dd57f5861898d28 | HOLD
- Git identity: codex/etabs-w3r-pareto-shear-windows@d0cc95bf3b07120db51cf64439d28a5bb216337e | upstream=origin/main@d0cc95bf3b07120db51cf64439d28a5bb216337e | base=origin/main@d0cc95bf3b07120db51cf64439d28a5bb216337e | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W3D is accepted through PR #906 merge `d0cc95bf...`, tree `56acf7ea...`. Separate W3R is locally accepted on that exact base: maintained shear and explicit stirrup area govern Pareto feasibility, 60/200 kN produce different fronts, 500 kN fails closed, unknown objectives fail, and Python/FastAPI/OpenAPI/React expose separate flexure/shear/stirrup evidence and unchanged holds. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Complete. The owner explicitly authorized the dependency-ordered W3 campaign; every packet still requires its exact predecessor and packet-specific stop conditions. |
| **Next** | Finish W3R documentation/quick/hooks, create one immutable candidate, push/open one PR, wait for every required changed-path check and merge only the unchanged reviewed head. Then fetch current main and begin W3E's strict beam-audit evaluator in a fresh worktree without rerunning W3D. |
| **Held** | Do not rerun W3D or use Pareto for an ETABS shortlist until W3R merges. Preserve all external payloads and earlier blockers. Torsion, serviceability, stirrup cost, fixed-action/global-analysis, independent-frame analysis, release and engineering/professional/construction approval remain unapproved. |

## W3A-W3D accepted through local W3D content freeze

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
coercion or live retry from unmerged source is permitted. R2 merged in PR #905.
A fresh exact-source continuation then returned the complete catalogue and
linked demand snapshot. Direct and localhost REST canonical hashes reconcile
exactly, while file, lock, units, all case statuses and every current output-
selection state remained unchanged. W3D's installed-software acceptance is
merged through PR #906. W3R then repaired the separate Pareto defect without
opening ETABS or Excel: maintained shear and supplied stirrup capacity now
govern candidate retention, utilization evidence is separated, `vu_kn`
changes membership, high shear and unknown objectives fail closed, and all
documented claim holds remain explicit. W3R is locally accepted pending its
normal immutable candidate/hosted review.

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

W3R now repairs the confirmed Pareto defect as a separate P1 packet. Keep the
optimizer unavailable for ETABS candidate selection until its unchanged
reviewed head merges. The local acceptance evidence is
`docs/verification/etabs-w3r-pareto-shear-feasibility-evidence.json`.

## Preservation rules

- Preserve all retained W2 branches, worktrees, receipts, evidence, models,
  workbooks, historical blocked runs, and public compatibility surfaces.
- Mac owns normal W3A development/review/integration. Windows remains the
  installed Excel/ETABS evidence host for a separately bounded getter packet.
- Move source only through GitHub. Proprietary model/workbook/result payloads
  remain off Git and are referenced only through bounded digests/counts.
- Do not compact the session archive or retire React/hooks/docs/public APIs in
  W3A; those require separate caller, successor, recovery, and owner evidence.

## W3R closeout and W3E handoff

Do not repeat W3D. Complete W3R's documentation, quick gate, normal staged
hooks and GitHub review from the current branch. After an unchanged merge,
fetch current `origin/main`, preserve this worktree, and create a fresh W3E
worktree. W3E builds the strict beam-audit evaluator from accepted W3A/W3D
contracts and evidence; it must cite every scenario/action/input/clause and
leave missing design-bearing inputs blocked rather than guessed. W3E does not
authorize ETABS mutation, release activity, or a professional claim.

### Completed W3D operator checklist

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
- [x] No live rerun occurred before R2 merge; the accepted run used a fresh
  continuation bound to exact merged source.
- [x] The complete catalogue and retained-evidence demand were reconciled
  through source-bound REST with exact canonical hash equality.
- [x] Postflight re-proved copied-model file identity, lock, units, statuses and
  all output-selection states unchanged; services stopped and ports are free.
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
