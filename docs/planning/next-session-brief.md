# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Validate controlled cases and earlier-building evidence separately.
- Completed: Updated the existing master plan: three distinct acceptance tracks for; Verified GitHub main, open PRs, all retained worktrees and current runtime;; Froze a separate two-span software model, EB-compatible shear basis, signs,
- Git receipt: docs/verification/etabs-w3h-two-span-git-handoff-receipt.json | sha256:87bda7095dd60b49ec95935c6175db119ec901bbe9e08be779e757574427aaff | HOLD
- Git identity: codex/etabs-w3h-validation-two-span-windows@19e181595b8a61c32281591c50e664f83bef2790 | upstream=NONE@UNKNOWN | base=origin/main@19e181595b8a61c32281591c50e664f83bef2790 | tree=dirty | operation=none
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
| **Next** | W3G PR #915, workflow-readiness PR #916 and W3H L1 comparison PR #917 (`3cdb3467...`, tree `dd8f80ce...`) are merged. Installed access/result recovery and fresh saved-revision references now pass. L5 remains held for explicit project mapping, support/slab basis and predeclared tolerances. LIB-PRO-015 still needs separate plan acceptance. |
| **Held** | W3E does not accept installed reinforcement or canonical serviceability. Pareto torsion/serviceability/stirrup-cost/global-analysis holds remain. No shortlist or mutating candidate until W3F-H calibration and W3I criteria pass. Release and engineering/professional/construction approval remain unapproved. |

W3H continuation: [guide](../guides/beam-line-calibration.md) and [receipt](../verification/etabs-w3h-comparison-evidence.json) bind the L1 checkpoint, exact next inputs and one-writer handoff; L5/W3I remain held.
`ETABS-W3H-ACCESS-RECHECK` recovered force access by one explicit reassertion of the already-selected combination. Fresh evidence: 153 beams/3,502 stations, complete catalogue, 40 foundation getters and 24 reconciled signed joint components; files/lock/units/status/flags unchanged. [Recovery receipt](../verification/etabs-w3h-access-recovery-evidence.json) and external `ETABS-W3H-RESULT-RECOVERY-20260830` supersede the old readback blocker. Do not rerun registration/recovery/analysis. L5/W3I still require supported physical mapping, unavailable spring/slab evidence and predeclared criteria; do not ask the owner to guess them. No Mac synchronization or calibration claim.

`ETABS-W3H-CALIBRATION-FEASIBILITY` assessed all 77 geometric lines: every line has an external endpoint/interior geometric contact; the 23 endpoint-graph exceptions are not proved isolated. A 31-getter read found the shortest candidate pinned but on unrestrained moving joints. Current solver support types do not encode imposed vertical movement. [Feasibility receipt](../verification/etabs-w3h-feasibility-evidence.json) distinguishes these facts from full mesh/support proof.
Owner approved three distinct validation tracks: data transport, beam checks using ETABS forces, and bounded independent prediction; see the active master plan. The [single-span receipt](../verification/etabs-w3h-independent-benchmark-evidence.json) retains 34 passing comparisons. The [two-span successor](../verification/etabs-w3h-two-span-evidence.json) adds 112 passing comparisons over 50 stations, one new analysis and exact protected building state. Zero ETABS shear-area modifiers explicitly match the EB benchmark basis, not native building behaviour. A saved-building replay verifies 60 evidence files, 153 beam sets/3,502 stations, catalogue and foundation output without Excel or new extraction. Next: bounded saved-building capability/mapping assessment plus asymmetric/patterned-load benchmarks. No repeat setup/recovery/passed runs; no guessed supports, whole-building calibration, W3I or professional approval. Windows owns this branch; Mac must fetch the accepted GitHub boundary.

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
That W3F session closed before W3G. Its data and unavailable calibration fields remain unchanged.

## W3G pure solver checkpoint

W3G merged unchanged; its originating usage checkpoint is closed. The workflow
repair adds read-only worktree/source/hook preflight and explicit gate wall
timings. Both devices must fetch before new work; Mac execution is not inferred
from Windows/POSIX tests. See the newest session and workflow readiness receipt.

`solve_beam_line_linear_v1(request, /)` now has strict core contracts, explicit
signs/units/supports/releases/offsets/loads and deterministic complete results.
Forty local reference tests pass; 94% branch-aware coverage. See
`../verification/etabs-w3g-beam-line-evidence.json` and the newest session.
Final integration truth is GitHub/external closeout, not the pre-push receipt.
W3H owns reference comparison/calibration; springs, diaphragm context, exact
model mapping and owner engineering tolerances must be proved. No hidden zero
stiffness, general ETABS parity, optimizer or professional approval is accepted.

### Retained W3D acceptance

W3D source/runtime/getter identity, repairs, direct/REST reconciliation and model/state preservation remain in its accepted receipt/session history. No live repeat; proprietary payloads stay outside Git and all old blocked evidence is preserved.

## Required Reading

1. [W3 ETABS data, beam-analysis, and optimization master plan](etabs-data-analysis-optimization-foundation-plan.md)
2. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
3. [ETABS, Excel, professional-attestation, and surface-retirement audit](etabs-excel-professional-surface-audit.md)
4. [Transactional W2C installed evidence](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json)
5. [Windows ETABS/Excel recurring-pitfall guide](../guides/excel-etabs-python-bridge-pilot.md#windows-etabsexcel-recurring-pitfall-checklist)
6. [Current task board](../TASKS.md)
7. [Newest session entry](../SESSION_LOG.md)
8. [Professional API and documentation renewal plan](lib-pro-015-professional-api-and-documentation-renewal-plan.md)
