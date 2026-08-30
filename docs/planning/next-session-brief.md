# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Accept the bounded installed read with explicit calibration holds, then stop before W3G.
- Completed: Preserved the repair branch and all older lanes/data. Rebound the task-owned; Inspected the existing ETABS 23.3.1 copied-model window before and after the; One attachment completed all 40 scoped getter records for one accepted
- Git receipt: docs/verification/etabs-w3f-spring-live-git-handoff-receipt.json | sha256:90738f8057927297c4930dce86c93b169e03f5c8243f13704299f316e6c82b6b | HOLD
- Git identity: codex/etabs-w3f-spring-live-windows@cce05508ea5f55559f5aeb07b8945bbabb7f3c06 | upstream=NONE@UNKNOWN | base=origin/main@cce05508ea5f55559f5aeb07b8945bbabb7f3c06 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | W3A-E/W3R and W3F static/readback are merged. PR #911 repaired merge guards/manifest; PR #912 merged the plan-only LIB-PRO-015 update. W3F spring repair PR #913 merged as `cce05508ea5f55559f5aeb07b8945bbabb7f3c06`, tree `d384f56d548e43454c5dc464ae9ec9f82d9bd230`; its bounded installed read now reconciles with unchanged copy/state and explicit calibration holds. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Complete. The owner explicitly authorized the dependency-ordered W3 campaign; every packet still requires its exact predecessor and packet-specific stop conditions. |
| **Next** | Stop after W3F as the owner requested. New chat: fetch, inspect the accepted stop receipt and preserved lanes, then separately resume W3G pure solver work; do not repeat live W3D/F. LIB-PRO-015 still needs plan acceptance before D0. Shared-path predecessors must be accepted or explicitly rebound first. |
| **Held** | W3E does not accept installed reinforcement or canonical serviceability. Pareto torsion/serviceability/stirrup-cost/global-analysis holds remain. No shortlist or mutating candidate until W3F-H calibration and W3I criteria pass. Release and engineering/professional/construction approval remain unapproved. |

## W3A-W3D accepted through local W3D content freeze

Accepted W3A freezes versioned, vendor-independent ETABS demand contracts:

1. load-pattern definitions, including type and self-weight multiplier;
2. load-case catalogue and typed case parameters/status;
3. combination type, ordered constituents, factors and nested references;
4. result-selection identity and definition/catalogue digests;
5. same-row signed beam actions with member/station/step provenance;
6. explicit demand scenarios, envelope rules, and compact governing references;
7. links back to the immutable W2 baseline and exact raw station identities;
8. distinct unavailable, not requested, not applicable, blocked and present states.

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
documented claim holds remain explicit. W3R is accepted through PR #907 with
matching candidate/merge tree and passing required hosted checks. W3E adds
the strict pure beam-audit layer; its evidence is L1 synthetic acceptance only.

## Required acceptance

- Every design-facing action identifies the W2 baseline, member, selection,
  case/combination, station, step, component, sign, and governing rule.
- No envelope combines incompatible station rows or independently maximized
  action components.
- Load combinations preserve ordered constituents, scale factors, nesting, and
  source-definition digest; names alone are insufficient.
- Optional fields never silently default missing ETABS information to zero,
  false, or an assumed engineering value.
- Contracts preserve Core -> IS 456 -> Services -> UI, explicit units and canonical JSON.
- No ETABS setter, `RunAnalysis`, design command, unlock/save, section/load
  mutation, Excel write, or optimization path is introduced.
- Independent frame analysis remains `HELD_NOT_SUPPORTED` until its separate
  solver and model-specific calibration packets are both separately accepted.

## Separate high-priority repair

W3R repairs the confirmed Pareto defect as a separate P1 packet, merged unchanged in PR #907.
Keep the optimizer unavailable for ETABS candidate selection until W3E/W3H/W3I gates are also accepted. Evidence: `docs/verification/etabs-w3r-pareto-shear-feasibility-evidence.json`.

## Preservation rules

- Preserve all retained W2 branches, worktrees, receipts, evidence, models,
  workbooks, historical blocked runs, and public compatibility surfaces.
- Mac owns normal W3A development/review/integration. Windows remains the
  installed Excel/ETABS evidence host for a separately bounded getter packet.
- Move source only through GitHub. Proprietary model/workbook/result payloads
  remain off Git and are referenced only through bounded digests/counts.
- Do not compact the session archive or retire React/hooks/docs/public APIs in
  W3A; those require separate caller, successor, recovery, and owner evidence.

## W3F contract closeout and installed handoff

W3F freezes exact typed topology, signed frame/nodal loads and six-component
displacement/reaction snapshots; source counts, identities and five states
fail closed. See `docs/verification/etabs-w3f-foundation-evidence.json`.
Contract PR #909 and static/readback PR #910 are merged; preserve both lanes. The latter records 38 installed signatures and semantic guards in `docs/verification/etabs-w3f-installed-signature-evidence.json`.
Live getters require its accepted merge, a verified copy, explicit scopes and
unchanged file/lock/units/status/selection postflight. Nonempty undocumented
joint-load steps and unproved spring forms remain visibly UNAVAILABLE.
Synthetic W3E/F fixtures are NOT owner engineering criteria or live evidence.

W3F spring repair PR #913 is accepted; its exact merge completed 40 installed getters, one-frame/three-joint definition, 3 displacement + 1 reaction rows and all 24 signed components. Model hash/size/mtime, lock, units, 15 finished cases and 77 flags stayed unchanged.
Springs and diaphragm/slab context remain UNAVAILABLE; required-calibration replay blocks with no partial snapshots. Exact replay/hashes/counts/signs reconcile. See the newest session and `docs/verification/etabs-w3f-spring-live-evidence.json`; all old dirty lanes remain preserved.
Stop before W3G. No analysis, design, model mutation, Excel, services, optimization or professional approval occurred in this continuation.

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
8. [Professional API and documentation renewal plan](lib-pro-015-professional-api-and-documentation-renewal-plan.md)
