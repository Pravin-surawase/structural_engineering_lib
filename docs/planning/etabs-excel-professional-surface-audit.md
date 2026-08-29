---
owner: Main Agent
status: draft
last_updated: 2026-08-30
doc_type: spec
complexity: advanced
tags: [etabs, excel, professional-review, digital-signature, api, react, retirement]
---

# ETABS, Excel, Professional Attestation, and Surface Retirement Audit

## Purpose and boundary

This is the companion audit to the
[ETABS data, beam analysis, and optimization foundation](etabs-data-analysis-optimization-foundation-plan.md).
It covers the next read-only ETABS data needs, Excel review workflow,
professional attestation, public-API retirement, React scope, and repository
compaction.

This audit authorizes no deletion, public-contract break, release, ETABS
analysis/design/save/write-back, credential claim, or professional approval.
W2C is integrated through PR #898, and the exact W3-readiness predecessor is
PR #899 merge `7af545ec0e239bac8fa6d480ecbb2b05a60aa40d` with tree
`cc40650b7f6569227c880d61a9967ee3bbdfab31`. The W3-readiness maintenance
separately authorized removal of only the ignored, recreatable local React
dependency and build caches; all tracked API, React, evidence, documentation,
branch, and worktree retirement remains held.

The intended operating model is:

```text
ETABS model and result evidence
  -> versioned library snapshots and calculations
  -> Excel review projection and comments
  -> immutable calculation dossier
  -> qualified review and external digital signature
```

Excel is a review surface. ETABS is the final global-analysis authority. The
library is the calculation, provenance, screening, and reconciliation layer.
None of those software roles makes the software a professional signatory.

## Decisions

| Question | Decision |
|---|---|
| Should the library capture more ETABS information? | Yes, as bounded hash-linked definition/result snapshots rather than one unbounded vendor object. |
| Should optional inputs copy the ETABS API style? | Only for read filters, explicit alternatives, opt-in checks, and expected-state guards. Missing calculation-bearing data must not acquire a default. |
| Should professional review/signature be added? | Yes, as a separate provider-neutral attestation contract over an immutable dossier. A typed name field or workbook approval cell is not a signature. |
| Should Excel calculate structural results? | No. Keep Office.js formula-free for structural calculations; project canonical service results and review evidence. |
| Should public functions be removed now? | No. The maintained ledger has zero approved retirement candidates and explicitly denies deletion/public-contract-break authority. |
| Should React be stopped? | Freeze broad feature expansion while the ETABS/data/solver foundation is built, but retain the working application and narrow validation routing. |
| Should dead React hooks/components be reviewed? | Yes. Four exact UI modules are candidates for a later caller-proved retirement packet; this audit does not delete them. |
| What produces the largest immediate local disk saving? | A controlled removal of recreatable `react_app/node_modules` and `dist`, not deletion of the 1.20 MiB tracked React source. |
| Should old documentation be deleted? | No bulk deletion. Keep historical evidence archived/excluded, compact active logs through the maintained command, and separately review the large CSI reference mirror for provenance and relocation. |

## Exact repository evidence

The audit used branch `codex/etabs-analysis-foundation-audit` at base
`ee50aaa3cad619b41c6153f5f7970553ef65248c`. The worktree contained only the
first audit's three documentation paths before this companion was added. The
repository authority reported no operation, conflict, or lock and continued to
report remote freshness as `NOT_CHECKED`.

The W3-readiness refresh observed PR #898 merged the exact reviewed candidate
`57f53d48...` as `f1873e7b...`, with tree equality at `bb20ba0c...`. The final
installed evidence reconciles the same 3,502-station direct/REST baseline with
all seven Excel tables and exact canonical JSON. The earlier six-table
`BLOCKED_SAFE_EXCEL_JSON_WRITE` artifact remains retained as historical
root-cause evidence, not the current verdict.

The 2026-08-30 W3 planning pass fetched and independently verified
`origin/main`, `FETCH_HEAD`, PR #899 and merged-tree identity before editing.
This companion inherits the master plan's `L0`-`L7` evidence levels and does
not promote workbook, signature or software evidence to professional approval.

### Current surface sizes

| Surface | Tracked files | Tracked bytes | Working-tree observation | Meaning |
|---|---:|---:|---:|---|
| `react_app` | 201 | 1,260,788 (1.20 MiB) | 456 MiB total | About 452 MiB is recreatable `node_modules`; source deletion is not the size solution. |
| `Python` | 590 | 7,076,160 (6.75 MiB) | 120 MiB total | Runtime/cache/environment content dominates the working-tree total. |
| `docs` | 3,049 | 51,842,685 (49.44 MiB) | 56 MiB total | Large vendor/reference and evidence material dominates. |
| `docs/_archive` | 509 | 7,510,613 (7.16 MiB) | Excluded from the published site and routine metadata checks | Already historical; moving more files here preserves Git bytes. |
| `docs/reference/vendor/etabs` | 1,760 | 27,693,265 (26.41 MiB) | Extracted CHM mirror | Largest tracked file-count compaction candidate, but current policy says preserve pending a separate decision. |

The Git object database reports 64.45 MiB in packs. Removing current files
would shrink a future checkout, not erase their existing Git history. A history
rewrite is disproportionate and is not proposed.

## Findings from official sources

### ETABS API

The official CSI API surface supports the foundation already proposed:

- response combinations expose type and an ordered case/combo constituent list
  with scale factors through
  [`cCombo.GetCaseList`](https://docs.csiamerica.com/help-files/etabs-api-2016/html/c46d4ff6-a816-f7ea-4b74-3eed6bf68e15.htm);
- load patterns expose names, types, and self-weight multipliers through the
  [`cLoadPatterns` interface](https://docs.csiamerica.com/help-files/etabs-api-2016/html/831f3fb4-226d-10a3-39f6-c6bc071610f5.htm);
- result selection is stateful, and the results interface includes frame
  forces, joint displacement/reaction, modal, and story response getters in
  [`cAnalysisResults`](https://docs.csiamerica.com/help-files/etabs-api-2016/html/3abebdb5-a279-ddcb-f2de-a058c9468c42.htm);
- [`JointDispl`](https://docs.csiamerica.com/help-files/etabs-api-2016/html/1bb2ca14-4532-795c-4e5a-50160dc144a4.htm)
  retains object/element, selection, step, translation, and rotation arrays;
- concrete-design comparison data is available from the
  [`cDesignConcrete` interface](https://docs.csiamerica.com/help-files/etabs-api-2016/html/4444b23f-4ec2-f061-a12d-239e8ca6dfc6.htm),
  including beam summary areas, shear/torsion results, design combinations,
  errors, and warnings; and
- CSI introduced `cDatabaseTables` as a broad tabular output/editing interface
  with case/combo filters and array/CSV/XML/Excel formats in the official
  [ETABS 18 release notes](https://installs.csiamerica.com/software/ETABS/18/ReleaseNotesETABSv1800.pdf).

These public documents prove that the required concepts exist. They do not
prove the Python/comtypes tuple shapes for installed ETABS 23.3.1. Every new
operation still needs the same installed managed-signature and live getter-
shape audit used by W2 before it enters the frozen matrix.

`cDatabaseTables` should first be an inventory and reconciliation path. Its
editing/import functions remain outside scope until a separately approved
mutation contract exists.

### Excel

Microsoft documents that `Range.values` interprets strings beginning with
`+`, `-`, or `=` as formulas. That exactly matches the W2C JSON failure; it is
not an ETABS or canonical-JSON defect. See the official
[`Excel.Range` reference](https://learn.microsoft.com/en-gb/javascript/api/excel/excel.range?view=excel-js-1.1).

Excel cells have a 32,767-character limit according to the official
[Excel limits](https://support.microsoft.com/en-US/Excel/excel-specifications-and-limits).
The present 15,000-code-point chunks are below that limit, but code points are
not by themselves a literal-text contract.

Microsoft's newer
[`valuesAsJson` data-type API](https://learn.microsoft.com/en-us/office/dev/add-ins/excel/excel-data-types-concepts)
can write an explicit `StringCellValue`, but it requires ExcelApi 1.16. The
repair therefore needs a runtime requirement-set check and an installed-
version test. A compatible fallback may add a safe transport prefix and strip
it during verified reconstruction; it must still prove the exact original
UTF-8 bytes and SHA-256.

Workbook settings are add-in/file-scoped state useful for freshness and review
flags, not a security boundary. Microsoft documents this distinction in
[workbook management](https://learn.microsoft.com/en-us/office/dev/add-ins/excel/excel-add-ins-workbooks?view=excel-js-preview).
Worksheet protection is also explicitly not a security feature in Microsoft's
[worksheet-protection guidance](https://support.microsoft.com/en-us/excel/protect-a-worksheet).

Microsoft's Office-signing guidance says a digital signature supports origin
and integrity and that a digitally signed document becomes read-only. The
correct sequence is therefore calculation/review, dossier freeze, then
signature—not signing a workbook that still needs design edits. See
[digital signatures for Microsoft 365 files](https://support.microsoft.com/en-US/Office/security-privacy/add-or-remove-a-digital-signature-for-microsoft-365-files).

### Indian electronic signature and professional boundary

The Information Technology Act recognizes electronic records and electronic/
digital signatures; the authoritative text is available through
[India Code](https://www.indiacode.nic.in/handle/123456789/15442). The
[Controller of Certifying Authorities eSign service](https://cca.gov.in/eSign.html)
describes licensed-CA digital signatures over a document hash with an audit
trail. CCA's
[signature-verification guidance](https://cca.gov.in/signature_verification.html)
also requires certificate-chain and revocation checking and recommends
long-term archival signature evidence.

Professional competence is a separate question from cryptographic validity.
The Ministry of Housing and Urban Affairs'
[Model Building Bye-Laws 2016](https://mohua.gov.in/upload/uploadfiles/files/MBBL.pdf)
and the BIS
[National Building Code overview](https://www.bis.gov.in/standards/national-building-code/?lang=en)
place structural design/certification and, in applicable cases, peer review on
competent professionals. Registration and permitted practice can depend on
the relevant state/local authority. The library must capture the claimed
jurisdiction and credential evidence; it cannot declare one universally valid
structural-engineer licence or decide legal eligibility for every project.

This is a software architecture boundary, not legal advice. Project-specific
signing and submission requirements require qualified professional and local-
authority confirmation.

## Future ETABS data and function audit

The public API should expose vendor-neutral immutable contracts. ETABS-shaped
COM calls remain in the adapter and installed signature ledger.

| Priority | Information | Proposed public contract/function | Optional-input rule | Use |
|---|---|---|---|---|
| E0 | Model/runtime/file/units/lock/analysis state | existing context plus `build_etabs_model_context_v1` | Expected identity guards optional only for read; required for mutation | Stop before stale/wrong-model reads |
| E1 | Load-pattern names/types/self-weight | `ETABSLoadPatternCatalogueV1` | Name filter optional; type/multiplier never inferred | Dead/live/self-weight basis |
| E1 | Load cases, types, status, relevant definitions | `ETABSLoadCaseCatalogueV1` | Case-family detail is a typed union; unsupported families are retained as `NOT_CAPTURED` | Exact analysis basis |
| E1 | Combo type, ordered constituents, factors, nesting | `ETABSCombinationCatalogueV1`; `build_etabs_result_catalogue_v1` | Selection filters optional; incomplete definitions block an accepted catalogue | Remove load-combination assumptions |
| E1 | Output-selection state | part of result catalogue and query evidence | Caller may request read-only selection filter; adapter must not silently select | Prevent wrong/empty results |
| E2 | Releases, offsets, insertion points, modifiers, supports/springs | `ETABSModelDefinitionSnapshotV1` | Capture modules may be optional; the local solver states which ones are mandatory | Beam-line interpretation |
| E2 | Materials and frame-section properties | typed section/material definitions | No grade/default inference from labels | Design and stiffness basis |
| E2 | Frame-force stations | existing W2 baseline plus `BeamActionRowV1` | Exact selection/member filters only | Strength demand and same-row envelopes |
| E2 | Joint displacements/rotations | `ETABSDisplacementSnapshotV1` | Explicit selection/node scope; omission means action-only calibration | Deflection and solver calibration |
| E2 | Reactions | `ETABSReactionSnapshotV1` | Explicit selection/support scope | Equilibrium and foundation actions |
| E3 | Story drifts, modal periods/masses/shapes | separate lateral/dynamic snapshots | Entire module opt-in; never required for the first gravity beam solver | Whole-model candidate safeguards |
| E3 | Concrete design summary, preferences, overwrites, design combos | `ETABSConcreteDesignComparisonV1` | Required only when claiming ETABS-design comparison | Diagnose library-versus-ETABS design differences |
| E3 | Database-table catalogue/export | `ETABSDatabaseTableInventoryV1`, bounded paged table snapshot | Table key, fields, cases/combos, row cap explicit | Discovery, reconciliation, bulk evidence |

### Public signature pattern

New entry points should use versioned request objects and keyword-only
convenience facades. A request contains:

- exact source/model/runtime identity;
- an explicit query scope;
- expected-state guards;
- typed units and sign/axis basis;
- finite row/byte limits;
- a missing-data policy; and
- a provenance/evidence mode.

An optional field is permitted only when omission cannot silently change an
engineering conclusion. Query filters can default to “all within the bounded
contract.” Engineering inputs such as material grade, cover, support model,
stiffness modifier, slab participation, load-combination definition, and
detailing standard remain required or produce a visible hold.

Raw COM tuples, return-code positions, and mutable ETABS objects are never
public-library values. Each getter records operation name, installed signature
identity, returned shape, status, units, count, disposition, and snapshot hash.

## Professional review and signature foundation

### Current gap

The repository already separates software `PASS/FAIL/HOLD`, freshness, and
qualified-review state. Calculation passports bind inputs, results, library
identity, and workbook evidence. However, current report models carry only
free-text `engineer_name` and `checker_name`; they do not bind a credential,
jurisdiction, review scope, artifact revision, certificate, signature, or
verification result. Current exports are calculation evidence, not signed
professional documents.

### Proposed contracts

Add provider-neutral contracts before integrating any signing service:

| Contract | Minimum fields |
|---|---|
| `ProfessionalIdentityV1` | Person name, organization, role, claimed jurisdiction/authority, credential type/identifier, issuing authority, validity dates when applicable, and evidence reference |
| `ReviewScopeV1` | Project/member/scenario scope, code editions/amendments, reviewed inputs/results, assumptions, exclusions, holds, and independent-check requirement |
| `ReviewAttestationV1` | Attestation ID/revision, dossier SHA-256, identity, role (`PREPARED`, `CHECKED`, `APPROVED`), decision, comments, UTC time, and supersedes link |
| `DigitalSignatureEvidenceV1` | Provider/mechanism, signed-artifact hash, signature value/reference, certificate subject/issuer/serial/thumbprint, algorithm, signing time, chain/revocation status and verification time |
| `SignedCalculationDossierV1` | Project/model/catalogue/demand/calculation/report hashes, all attestations, signature evidence, immutable artifact identity, and final status |

The provider-neutral public function signatures are:

```python
def build_calculation_dossier_v1(
    request: CalculationDossierBuildRequestV1, /
) -> CalculationDossierBuildResultV1: ...

def record_review_attestation_v1(
    dossier: CalculationDossierV1,
    attestation: ReviewAttestationV1,
    /,
) -> AttestedCalculationDossierV1: ...

def attach_digital_signature_evidence_v1(
    dossier: AttestedCalculationDossierV1,
    evidence: DigitalSignatureEvidenceV1,
    /,
) -> SignedCalculationDossierV1: ...

def verify_signed_calculation_dossier_v1(
    dossier: SignedCalculationDossierV1,
    *,
    verification_time_utc: str,
) -> DossierVerificationResultV1: ...
```

These functions build and verify evidence; they do not sign bytes, hold private
keys, validate professional eligibility for every jurisdiction, or turn a
typed name into approval. `record_review_attestation_v1` rejects a dossier hash
or review scope mismatch. `attach_digital_signature_evidence_v1` rejects a
signed-artifact hash mismatch. Verification separately reports artifact hash,
certificate chain, revocation, credential-evidence and review-scope states so
one success cannot mask another hold.

The library validates schema, hashes, internal consistency, staleness, and
cryptographic verification evidence. A credential-authority adapter may verify
external facts for one jurisdiction. The core library must not claim that the
person is legally authorized for the project merely because a field is filled
or a certificate is cryptographically valid.

### State model

```text
DRAFT
  -> REVIEW_READY
  -> REVIEWED_ACCEPTED or REVIEWED_REJECTED
  -> SIGNATURE_PENDING
  -> SIGNED_VERIFIED

Any calculation/model/report byte change -> STALE_SUPERSEDED
Failed chain/revocation/hash verification -> SIGNATURE_INVALID
```

Software engineering status remains separate throughout. A signed dossier may
contain an engineering `FAIL` or `HOLD` if the signer is recording a rejection
or limitation. Conversely, software `PASS` never becomes professionally
approved without a valid, in-scope attestation.

Private keys must never enter the library, workbook, repository, or review
bundle. Signing belongs to the user's certificate provider/eSign client. The
library produces and verifies canonical bytes and retains verification
evidence.

## Excel workbench roadmap

### X0 — Complete: literal W2C transport

PR #898 requires ExcelApi 1.16 and writes explicit `valuesAsJson` String,
Double, Boolean, and Empty cells. Installed Excel proved `+`, `-`, and `=`
prefixes remain literal, and all 242 chunks rejoin to the exact 3,626,096-byte
canonical JSON and SHA-256. Structured blanks and 15-significant-digit numeric
storage are normalized without rounding the canonical JSON.

### X1 — Complete for the seven W2 controlled tables

The accepted implementation preflights every collision and header, snapshots
the full touched range for every existing table, removes every newly created
controlled sheet on failure, restores existing dimensions and typed cells, and
verifies rollback. Success is accepted only after every structured cell,
projected-row total, JSON byte count, and SHA-256 reconciles. A future review
workbook may still adopt staging sheets or a commit marker as an additional
publication affordance, but it is not an unresolved W2 blocker.

### X2 — Review workbook

After the W3 data contracts are accepted, add formula-free controlled tables
for:

- project/model/runtime identity and source hashes;
- load-pattern/case/combination catalogue and selected scenarios;
- beam demand rows and governing same-row references;
- library results, ETABS design comparison, assumptions and held checks;
- reviewer comments/dispositions and revision history; and
- dossier/export/signature verification status.

The bounded projection separates compact review from lossless transport:

- identity/catalogue tables retain pattern, case, status, selection,
  combination and ordered-factor rows;
- scenario/governing tables retain exact `BeamGoverningReferenceV1` row IDs and
  never present independent extrema as one concurrent action;
- raw action, displacement and reaction rows use explicit bounded pages or the
  canonical JSON bundle rather than silent truncation;
- comments/dispositions are user-owned review data with revision identity and
  never alter canonical calculation bytes; and
- dossier/signature tables display evidence state but never store private keys
  or fabricate approval.

Before any write, the add-in must preflight requirement sets, controlled sheet/
table collisions, headers, row/byte limits and the complete intended write
set. Publication is all-table transactional: snapshot existing controlled
ranges, write typed values, read back structured cells, rejoin canonical UTF-8
bytes, verify counts/hashes, then mark the revision committed. Failure removes
new controlled sheets and restores every existing controlled range/dimension.
The accepted W2 `valuesAsJson` literal-string path remains the first transport
choice; any fallback needs its own installed proof.

Workbook settings may cache UI freshness state, but the canonical evidence
must remain in hash-bound tables/bundles. Sheet protection is presentation
control only. Mac owns schema/transaction/fake-host tests; Windows owns the
separately authorized installed Excel save/readback/rollback evidence.

### X3 — Professional-signature handoff

Excel gathers review metadata and freezes the dossier. It then exports the
canonical JSON plus a human-readable PDF/HTML report for external signing.
After signing, Excel may import verification evidence and display it. It does
not store private keys, fabricate a signature image, or treat a typed name as
approval.

## Public API retirement audit

### Current facts

The maintained compatibility ledger records:

- 328 canonical owners;
- 843 facade projections;
- 45 root compatibility-stub modules with 520 projections;
- 1,650 caller records;
- zero ambiguous maintained callers;
- zero retirement candidates; and
- `deletion_authorized=false` and
  `public_contract_break_authorized=false`.

`structural_lib.api` is a 397-byte formula-free re-export stub. The optimizer
root stubs are each about 0.4–0.5 KiB. Removing these modules would reduce
discoverability clutter but would not materially shrink runtime or improve
calculation speed; it would break existing imports.

Four historical ETABS helpers are already marked `HELD_COMPATIBILITY` without
a removal version:

- `load_etabs_csv`;
- `normalize_etabs_forces`;
- `create_job_from_etabs`; and
- `create_jobs_from_etabs_csv`.

They remain callable because their historical shapes cannot represent the
accepted snapshot contract. They become retirement candidates only after the
new catalogue/demand/public journey is accepted and a current caller census
shows no required use.

### Retirement sequence

1. Classify the exact symbol/module/route and all maintained, example, test,
   documentation, fixture, archive, and external known callers.
2. Provide one accepted replacement with equal or safer outcome behavior.
3. Migrate maintained callers and publish a migration example.
4. Add deprecation metadata only with an owner-approved removal version.
5. Test warnings explicitly because Python hides `DeprecationWarning` by
   default; see the official
   [Python warnings documentation](https://docs.python.org/3.13/library/warnings.html).
6. Keep the compatibility shim for the declared window and exact-wheel UAT.
7. Remove only in a separately authorized breaking release with rollback and
   release notes.

The project is pre-1.0. Although
[Semantic Versioning](https://semver.org/) gives 0.x releases special latitude,
the repository policy correctly does not treat that as permission for an
unannounced break.

## React and hook audit

### Keep the application, freeze expansion

The current React source is not an inert older prototype. It carries active
project import/review/design/results routes, ETABS snapshot identity, same
public optimization endpoint, 3D member review, building gravity, slabs,
columns, footings, exports, and status presentation. The parity dashboard
reports 13/13 maintained API-connected hooks and the TypeScript configuration
rejects unused locals/parameters.

The verification manifest already routes `react_app/**` changes to the React
domain while this documentation-only audit selects only the docs domain.
Therefore deleting React does not make ordinary Python/ETABS packets skip a
gate they are already allowed to skip. The broad milestone/release gate should
continue to test React once after all packets integrate.

Recommended status through the ETABS foundation:

- maintenance-only for current supported journeys;
- no new general UI or visualization initiative;
- implement only UI needed to review accepted ETABS/data/solver evidence;
- keep exact route and result-status regressions; and
- allow recreatable dependency caches to be absent outside React work.

### Exact later retirement candidates

A production-caller search found these modules referenced only by their own
file, barrel export, and/or tests:

| Candidate | Current role | Required proof before action |
|---|---|---|
| `hooks/useGeometryAdvanced.ts` | Old server-side visualization hooks | Prove current client geometry replaces both endpoints for every supported journey; decide endpoint ownership separately |
| `hooks/useTorsionDesign.ts` | Standalone torsion endpoint hook | Prove integrated beam-design flow is the accepted UI successor and migrate examples/tests |
| `hooks/useRebarEditor.ts` | Standalone validate/apply hooks | Prove current detailing/geometry flow covers the intended editor journey |
| `components/design/ExportPanel.tsx` | Unmounted export panel | Prove active dashboard/editor/design export controls cover its BBS/DXF/report behavior |

These are candidates, not confirmed deletions. Endpoints can remain public even
if an unused UI adapter is removed. The seven legacy URL routes are small
compatibility redirects to current workbench/project stages; keep them until
usage/consumer evidence supports a separately announced route removal.

### Disk compaction

When React work is paused, a separately authorized cache cleanup can remove
only ignored `react_app/node_modules` and `react_app/dist` after recording the
exact `package-lock.json` identity and `npm ci` / frontend-build restore
commands. This can recover roughly 455 MiB in the current worktree while
preserving every source file and hook. Sibling worktrees require their own
inventory and must not be cleaned by a broad recursive command.

## Documentation compaction

The existing `_archive` boundary is useful: it is excluded from the published
site, routine front-matter checks, and normal maintained-link validation. Do
not delete it simply to improve file statistics.

Priorities:

1. run the maintained session-log compactor in its own task when the active log
   reaches the agreed threshold;
2. move only superseded planning/reference documents whose replacement,
   inbound links, authority, and recovery path are proven;
3. keep one small maintained index that points to current ETABS, Excel, solver,
   and professional-review authorities;
4. exclude archive/vendor trees from routine broad searches and generated
   inventories; and
5. review the extracted CSI CHM mirror and duplicate source CHM separately for
   licence/provenance and relocation to a checksum-bound local cache plus
   official online links.

The current compact-modernization plan says to preserve
`docs/reference/vendor/etabs`; this audit does not override it. Any relocation
needs a new decision, link/caller proof, and recovery evidence. Do not rewrite
Git history merely to remove those historical objects.

## Dependency-ordered programme

| Packet | Scope | Indicative effort | Exit |
|---|---|---:|---|
| R0 | W2C literal JSON and transactional Excel publication | Complete through PR #898 | Seven tables, exact reconstructed hash, rollback, and installed preservation accepted |
| R1 | Load pattern/case/combo catalogue and installed getter audit | 2–4 weeks | Complete hash-linked definitions with no inferred factors |
| R2 | Model-definition and displacement/reaction snapshots | 2–5 weeks | Solver/calibration inputs are explicit or held |
| R3 | Professional identity/review/dossier contracts | 1–3 weeks | Provider-neutral immutable attestation schemas and hash tests |
| R4 | Excel review/dossier projection | 2–4 weeks after R1/R3 | Formula-free review workbook with freshness and staged writes |
| R5 | External digital-signature adapter proof | 2–6 weeks, provider/jurisdiction dependent | Signed hash verifies with chain/revocation evidence; no private-key custody |
| R6 | React freeze cleanup and exact dead-adapter packet | 2–5 focused days | Caller-proved small removal or explicit keep decisions; React journey remains green |
| R7 | Documentation/vendor/log compaction | 2–5 focused days | Current authority clearer; recovery/link/provenance evidence complete |

R1/R2 feed the beam-line and optimization packets in the companion foundation
plan. R3/R4 can proceed without ETABS mutation. R5 requires a selected signing
provider and project/jurisdiction requirements; it must not be guessed.

## Immediate order

1. Start W3A by freezing the load pattern/case/combination catalogue and demand
   contracts without opening or mutating ETABS.
2. After W3A is accepted and merged, and only after separate user authority,
   run the bounded Windows ETABS 23.3.1 static getter/signature audit; do not
   infer live model values from it.
3. Repair Pareto shear truth in a separate library packet before optimizer use.
4. Add the professional dossier/attestation types before adding signature UI.
5. Build the bounded beam-line solver and local screening only on accepted
   W3A inputs.
6. Prune only proven dead React adapters and compact only proven historical or
   recreatable material in separately authorized packets.

Do not start with public-function deletion, a broad React removal, worksheet
signature images, ETABS setters, or a general 3D FEM engine.
