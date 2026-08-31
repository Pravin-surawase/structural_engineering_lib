# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-31
- Focus: Complete the simplest source-supported serviceability path without new analysis or inferred inputs.
- Completed: Added strict complete span/depth and supplied Annex F service checks through; Kept separate service-case/source/geometry/bar-revision evidence; no factored; Corrected aggressive crack-width limits and added explicit EXTREME handling.
- Git receipt: docs/verification/etabs-w3-serviceability-git-handoff-receipt.json | sha256:aa8a18b3a5ae43dafa938f57641dfbd52427e85325b27a9ce7780ff762288dc9 | HOLD
- Git identity: codex/etabs-w3e-serviceability-windows@773d96739aaa68d5205d606010f0e0540dc4aa7c | upstream=origin/main@773d96739aaa68d5205d606010f0e0540dc4aa7c | base=origin/main@773d96739aaa68d5205d606010f0e0540dc4aa7c | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

The [whole-W3 reset](etabs-data-analysis-optimization-foundation-plan.md#whole-w3-execution-reset-2026-08-31) owns sequencing; the [saved-basis decision](etabs-w3-saved-basis-and-criteria.md) owns the current next packet.
Source: accepted PR #936 merge `773d96739aaa68d5205d606010f0e0540dc4aa7c`; [current serviceability packet](etabs-w3-serviceability.md).
Windows owns the bounded serviceability branch; exact external integration receipt governs acceptance. Mac NOT_CHECKED.

| State | Next action / claim boundary |
|---|---|
| **Current** | Strict span/depth <=10 m and supplied Annex F inputs implemented through canonical/W3 checks. Complete service evidence required; separate SLS identity and exact row/location binding. Candidate gates/integration receipt govern acceptance. No live calls. |
| Migration | Nonzero raw torsion now requires explicit corner-bar geometry and opposite depth. Al is total Me1/Me2 required tension steel, not additive torsion steel; source-corrected G7 replaces historical numbers. |
| **Next** | Project service-input evidence and mandatory detailing/constructability criteria. Direct/long-term deflection and torsion detailing/BBS remain held. Reuse accepted owners; do not repeat pilot inputs. |
| H route | Stop broad table diagnosis. Acquire only named support/mesh/transfer gaps after physical route choice; more getters cannot fix unsupported solver physics. No solver fitting. |
| Retained | A-D/R, bounded E/F/G/H/J acceptance; #925 repair closed. #931 CSI 1 and #932 binder causes unconfirmed; #933 timestamp defect confirmed. No frozen retry. |
| Held | Actual-building H; required serviceability and installed-rebar claims; I/K/L; final combined gates/Mac review; professional/release approval. |

No ETABS/UI/export/solver/design calls in this packet. Saved evidence is not fresh
lock/units/status/selection proof. Keep `v0.24.0`; no release is authorized.

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
