# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-30
- Focus: Audit and plan W3 from the exact integrated W3-readiness
- Completed: Fetched `origin/main` and verified `origin/main`, `FETCH_HEAD` and starting; Read live `AGENTS.md`, documentation rules, the existing W3 foundation,; Confirmed the W2 baseline already retains complete signed same-row six-
- Git receipt: docs/verification/etabs-w3-master-plan-audit-git-handoff-receipt.json | sha256:5ffa34a58238a56a878210164f5b4aa73b6dc641a44dadfd01c466ea1d6661ab | HOLD
- Git identity: codex/etabs-w3-master-plan-audit@48001ed0324d2a00151928a3e95a91e0accf9dd4 | upstream=NONE@UNKNOWN | base=origin/main@7af545ec0e239bac8fa6d480ecbb2b05a60aa40d | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the current immutable normal software release. No release work is authorized. |
| **Current** | PR #899 is the exact integrated W3-readiness predecessor: merge `7af545ec0e239bac8fa6d480ecbb2b05a60aa40d`, tree `cc40650b7f6569227c880d61a9967ee3bbdfab31`. The durable W3 plan is prepared for owner acceptance; W3A has not started. |
| **W2 complete** | PR #898 merged reviewed W2C head `57f53d48...` as `f1873e7b...`; candidate and merge tree are both `bb20ba0c...`. Direct service, REST, all seven saved Excel tables, and 3,626,096 reconstructed canonical JSON bytes reconcile to SHA-256 `d4c28586...`. |
| **Plan gate** | Review/accept the W3 master plan. Plan acceptance alone does not dispatch W3A or Windows work. |
| **Next** | After acceptance, start `ETABS-EXCEL-BEAM-W3A-DEMAND-CONTRACT` as one bounded Mac read-only contract packet from exact PR #899 predecessor. |
| **Held** | Opening ETABS/Excel, installed getter work, analysis/design/unlock/save, model or workbook mutation, solver/optimizer implementation, automatic write-back, release, deletion/retirement, and engineering/professional/construction approval. |

## W3A objective

Freeze public, versioned, vendor-independent contracts for exact ETABS demand
provenance before expanding design or optimization:

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

W3A is contract-first and read-only. It may add types, pure validators,
serialization, fake-adapter fixtures, public API registrations, tests, and
documentation. It adds no COM adapter or installed application evidence.

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

## W3A Mac starter prompt

```text
Start ETABS-EXCEL-BEAM-W3A-DEMAND-CONTRACT only after the W3 master plan is accepted. Fetch and verify origin/main at exact
PR #899 merge 7af545ec0e239bac8fa6d480ecbb2b05a60aa40d with tree cc40650b7f6569227c880d61a9967ee3bbdfab31; inspect AGENTS.md
and live Git/worktree authority before writing. Implement one bounded Mac read-only packet for the accepted availability, load-pattern,
load-case, response-combination/nested-factor, analysis-status, result-selection, same-row signed beam-action, scenario, envelope,
governing-reference, paging, canonical-hash and fail-closed build-result contracts and exact public signatures. Use normalized fake-adapter
fixtures only; preserve W2 contracts and HELD_NOT_SUPPORTED; add required focused tests, exports and caller/API ledger registrations.
Do not open ETABS/Excel, add COM/getter/setter code, run analysis/design, mutate a model/workbook, repair Pareto in this packet, start the
beam-line solver/optimization, delete/retire anything, publish a release, or claim engineering/professional approval.
```

## Later Windows W3B handoff — copy/paste only

Do not create, send or start this laptop task automatically. Use it only after
all three dispatch gates are true: the W3 plan is accepted, W3A is accepted and
merged, and the user explicitly authorizes the Windows packet. Replace every
bracketed placeholder with evidence from the accepted W3A merge.

```text
Run one bounded Windows metadata/signature audit for ETABS-EXCEL-BEAM-W3B-INSTALLED-GETTER-SIGNATURES. First fetch and verify origin/main
at exact W3A merge [W3A_MERGE_SHA], tree [W3A_TREE_SHA], and accepted W3A contract/getter-requirement digest [W3A_CONTRACT_DIGEST].
Inspect live AGENTS.md, Git/worktree authority, the W3 master plan/brief, accepted W3A contracts/tests, retained W2 signature evidence,
and installed ETABS source identities before writing.

This is static installed ETABS 23.3.1 getter/signature evidence only. Do not create COM, attach/open ETABS or Excel, call SapModel, run
analysis/design, change selection, unlock/save, mutate a model/workbook, implement Mac runtime/engineering code, optimize, delete/retire
branches/worktrees/evidence/public surfaces, publish a release, or claim engineering/professional approval.

Reprove installed ETABS 23.3.1.4563 x64 assembly/type-library/generated-wrapper and Python/comtypes identities. Audit accepted W3A
operations: LoadPatterns.GetNameList/GetLoadType/GetSelfWTMultiplier; LoadCases.GetNameList/GetTypeOAPI and accepted case-family getters;
RespCombo.GetNameList/GetTypeOAPI/GetCaseList or installed overload; Analyze.GetCaseStatus; both Results.Setup selection getters; and the
existing Results.FrameForce provenance contract. Per operation, record installed signature, argument/output order/types, defaults, enum,
CSI return form, generated Python call signature, outer/SAFEARRAY expectation, source hashes, verdict and limitations. Unknown overload,
missing symbol, source/runtime drift or operation outside the accepted matrix is BLOCKED, not inferred.

Produce one versioned evidence artifact, concise handoff/issue record and focused static-evidence checks. Report exact Git base/head/tree,
installed identities, proved/blocked counts and verdicts, limitations, stop reasons and Mac integration next step. Preserve
HELD_NOT_SUPPORTED and make no live model/result claim.
```

### Windows W3B operator checklist

- [ ] User explicitly authorized W3B; no authority was inferred from this file.
- [ ] `origin/main`, W3A merge/tree and contract digest match the filled prompt.
- [ ] Worktree has no conflict/operation/unknown owner state; unrelated work is preserved.
- [ ] Installed ETABS version, x64 typelib/assembly, generated wrapper, Python and comtypes identities are recorded with hashes.
- [ ] No ETABS/Excel process is opened, attached or automated; no `SapModel` call occurs.
- [ ] Every accepted getter has exact signature/default/return/container evidence and one verdict.
- [ ] Unsupported case families and unknown overloads remain blocked; no arbitrary payload mapping is invented.
- [ ] Evidence distinguishes static compatibility from live model, solver, engineering and professional acceptance.
- [ ] No secrets, proprietary model/workbook/result bytes or generated vendor wrapper source enter Git.
- [ ] Stop on predecessor drift, installed-source drift, missing accepted contract, operation outside matrix, or any need to open an application.
- [ ] Return once to Mac with the clean candidate/evidence identities; do not continue into live getters automatically.

## Required Reading

1. [W3 ETABS data, beam-analysis, and optimization master plan](etabs-data-analysis-optimization-foundation-plan.md)
2. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
3. [ETABS, Excel, professional-attestation, and surface-retirement audit](etabs-excel-professional-surface-audit.md)
4. [Transactional W2C installed evidence](../verification/etabs-excel-beam-w2c-installed-acceptance-transactional-evidence.json)
5. [Windows ETABS/Excel recurring-pitfall guide](../guides/excel-etabs-python-bridge-pilot.md#windows-etabsexcel-recurring-pitfall-checklist)
6. [Current task board](../TASKS.md)
7. [Newest session entry](../SESSION_LOG.md)
