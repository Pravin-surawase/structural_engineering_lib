# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-31
- Focus: Whole-W3 research, missing dependencies and repeated-work audit.
- Completed: Fetched the accepted GitHub boundary, inspected 36 prior lanes and open PRs,; Audited the full W3 plan and implementation/evidence owners. Corrected stale; Identified an existing 271,593-byte text backup and inventoried its input
- Git receipt: docs/verification/etabs-w3-whole-plan-audit-git-handoff-receipt.json | sha256:b3a8a962e1956d901781ee14323783cca9da1bf3e881823f1979aeef34b9729d | HOLD
- Git identity: codex/etabs-w3-whole-plan-audit-windows@ce9c799030754cbb105a308f45da9f66434392a8 | upstream=origin/main@ce9c799030754cbb105a308f45da9f66434392a8 | base=origin/main@ce9c799030754cbb105a308f45da9f66434392a8 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

The [whole-W3 reset](etabs-data-analysis-optimization-foundation-plan.md#whole-w3-execution-reset-2026-08-31) owns sequencing; the [research audit](etabs-w3-whole-plan-research-audit.md) explains it.
Base: PR #933 merge `ce9c799030754cbb105a308f45da9f66434392a8`.
Windows owns this branch; Mac is NOT_CHECKED. Fetch the accepted audit merge before continuing.

| State | Next action / claim boundary |
|---|---|
| **Current** | W3A-D data contracts/catalogue, W3R shear repair, W3E strength software, bounded W3F, W3G solver, W3H comparator/authored benchmarks and bounded fictional W3J review/rollback. #925 validation repair is closed. |
| New finding | An existing 271,593-byte `.$et` backup contains model-input sections. Its narrow section inventory is not semantic/revision reconciliation or a completed W3F snapshot. |
| **Next** | Reconcile saved definitions/loads against accepted evidence, make at most three candidate-line input matrices, and decide physical suitability before another API packet. Independently specify serviceability/applicability and screening criteria. |
| Alternative sources | Already proved object getters; supported SQLite/CSV/XML exports; integrated managed table client only for residual required gaps. Any installed action still needs its own exact packet. |
| Closed diagnostics | #931 CSI 1 and #932 managed-binding causes unconfirmed; #933 outer timestamp type defect confirmed. 69 controlled cases do not prove the real collector/entrypoint. No frozen retry; no table access proved. |
| Held | Actual-building H; required canonical serviceability and any installed-rebar claim; candidate screening I, reanalysis K, iteration L, final integrated gates/Mac review, professional/release approval. |

No applications, solver or benchmarks ran in this planning audit. Existing saved
data are not fresh lock/units/status/selection proof. Do not repeat accepted
benchmarks, recovery, registration or broad validation just to revisit the plan.
`v0.24.0` remains the retained release boundary; no release work is authorized.

## Historical W3A-W3D details (current sequence above takes precedence)

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

W3G merged unchanged and its usage checkpoint is closed. The workflow repair adds read-only source/hook preflight and gate wall timings. Both devices fetch before new work; Mac execution is not inferred from Windows/POSIX tests. See the newest session and workflow readiness receipt.

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
