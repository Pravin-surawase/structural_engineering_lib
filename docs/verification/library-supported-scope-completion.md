---
owner: Main Agent
status: active
last_updated: 2026-10-01
doc_type: reference
---

# Supported-library completion and remaining qualification

**Type:** Reference
**Audience:** Developers
**Status:** Active
**Importance:** High
**Created:** 2026-10-01
**Last Updated:** 2026-10-01

This checklist continues the owner's existing-scope library correctness work.
It does not approve draft PR #1019's 50-day programme or add structural systems.
The replacement solver remains the main product and Project_Manager V1 retains
priority on the shared Mac. Local evidence is under
`external_data/library-evidence/96170d8/completion-qualification-20261001/`;
the separately reviewed material/SLS packet remains immutable.

The original ten-failure qualification below is preserved as history. The
authorized metadata/fixture follow-up is recorded separately under
`external_data/library-evidence/96170d8/completion-reference-repair-20261001/`.
Its receipt owns the revised candidate identity and actual acceptance results;
the accepted numerical module contents remain unchanged.

The maintained scope owners are
[`capabilities.py`](../../Python/structural_lib/services/capabilities.py),
[`family_facade_registry.py`](../../Python/structural_lib/services/family_facade_registry.py),
the [API classification](../reference/api-classification.json), and the
[caller-completion criteria](../planning/library-usability-improvement.md#work-and-completion-evidence).
Use their supported cases and exclusions rather than treating every exported
helper or experimental module as a general design capability. The promoted
inventory has 13 family journeys: beam, torsion, supplied-column check, three
slab journeys, braced wall, straight staircase, simply supported deep beam,
regular interior flat slab, concentric isolated footing, symmetric combined
footing and strap footing. Their approved case limitations remain in force.
General frame analysis, arbitrary column layouts, experimental P-M-M as a
stable design decision, installed Windows/ETABS/XLL acceptance, manufacturer
constitutive laws and new structural-system features are outside this packet.

## Accepted corrections and identities

The strain/concrete column, signed long-column and per-plane reduction packets
and the Annex G flange branch/root packet have separately reported bounded
independent acceptance. Their original files, receipts and verdicts are not
replaced by later work.

The parent reported bounded independent acceptance of material/SLS wheel
`29929814498854639b4082fe6abf89013374037f744fcfa2e3bfc4f68b2a201b`,
candidate manifest
`3189fef6943d1f0b5cea6ae82f31dc0f1ad8267d2f5754694ea678560848320b`.
Independent evidence includes 351 wheel tests, 225 installed origins, zero
fallback, 122 signed steel states, 12 compression-bar/full-compression states,
62 SLS states and eight retained unsupported HOLD domains. All 825 packet files
and 3,013 predecessor files matched. The review record is alongside, not inside,
the frozen packet:
`external_data/library-evidence/96170d8/material-sls-independent-review-20261001.json`.

Accepted named profiles are `IS456_FIG23_REP_GS115_V1` and
`IS456_ANNEX_C_RECT_SINGLE_V1`. The 161 kNm axis-relabelled example is equally
SAFE at about 0.9932 under this steel law. Its earlier unsafe outcome is
historical evidence for the earlier material profile; axis/sign invariance
remains corrected. Steel-family applicability, finite creep history and complete
latest-amendment qualification are outside that verdict.

The [reference-method decision](column-pmm-benchmark.md#engineering-reference-method-owner-decision-30-september-2026)
and [SLS model decision](../library/reference/wp04-serviceability.md#legacy-scalar-annex-c-correction-1-october-2026)
remain: derive mechanics, use original standards for code requirements, inspect
actual comparator implementations, and verify with independent calculations
and benchmarks. NPTEL is supporting reference material. Exact integration is
exact for the selected constitutive law; it is not independent proof of that
law's physical applicability. Prescribed design coefficients and nominal axial
caps remain separate from integrated section analysis.

## Additional qualification completed

The shared material law and legacy SLS signatures justify one cumulative check
of consumers outside the earlier focused packet. A separate temporary source
snapshot and venv reused existing dependencies read-only. No third-party
download, dependency upgrade, source edit or original-environment change was
needed. Existing resolved focused cases, slow/performance cases, marked
repository-only modules and the redundant wheel-build fixture were excluded.

| Check | Current exact-candidate evidence | Remaining limit |
|---|---|---|
| Missing Python consumers | Original replay: 6,343 pass, 16 fail, four skip; six context failures subsequently pass with repaired harness/repository context | Original freeze retained ten qualification failures below; follow-up receipt owns their repair results |
| HTTP consumers | 527 additional tests pass using the exact wheel; 231 imported library origins, zero top-process source fallback | Slow/performance and previously qualified column cases excluded; no live server/browser acceptance |
| Maintained CLI/input UAT | 29 cases and 28 advertised entry classifications pass | Development software evidence, not engineering-use approval |
| Minimal declared dependencies | Same 29 UAT cases pass and all 13 expected family recipe outcomes are reproduced with only Pydantic and its declared dependency closure copied from existing installations; NumPy/SciPy/ezdxf/Jinja2/pytest/matplotlib absent | No fresh registry install or cross-platform binary provenance claim |
| Family outcomes | 11 PASS, one FAIL and one HOLD retained | FAIL/HOLD are expected engineering results, not failures to suppress |
| Documentation | Current copied candidate builds with `mkdocs build --strict`; changed decision pages rendered | This separate checklist was added afterward; no website publication |
| Artifact identity | Exact reviewed source and wheel reused; no production files changed during qualification | A future repaired candidate requires a new identity |

The four skips are three unavailable real-ETABS-data checks and one Windows
saved-file-path contract. They do not establish installed ETABS acceptance.
The original failed runs and wrapper diagnostics remain in the new evidence
directory. One accidental repeat of the API replay is explicitly excluded from
additional qualification counts. Failed setup/namespace/spawn diagnostics are
not presented as production defects.

## Bounded reference repair: original ten-case scope

The original ten failed cases were classified without changing the reviewed
candidate. The owner authorized their metadata/test reconciliation as a new
candidate. No new numerical model is introduced and the accepted packet is
not rewritten.

| Required repair | Confirmed cause and scope | Acceptance | Effort estimate |
|---|---|---|---|
| Clause metadata count: two cases | This packet incorrectly set `metadata.total_clauses` to the sum of four registry groups, 201. Its existing contract counts `clauses` only, currently 180. Restore that count; retain all source identifiers and entries | Both count/hygiene tests pass; clause/table/figure/annexure contents and numerical module hashes unchanged | 15–30 min |
| Generated Indian-code manifest: one case | Source reference/decorator metadata changed; the committed manifest is stale | Regenerate through the existing owner; deterministic comparison passes without expanding supported-case or engineering-verification claims | 20–45 min |
| SLS property/regression callers: four cases | Cracked helper calls omit required x/d geometry and assume the old Branson model. Annex C cannot infer that geometry from Ig/Icr/Mr/M alone | Use physically consistent section geometry and independent Annex C references, preserving missing-basis rejection and inertia bounds; no fallback to Branson | 30–60 min |
| Doubly reinforced verification pin: one case | Pre-profile `Asc=296.55513585 mm²` is stale. Independent 60-digit Decimal mechanics gives `296.398530245371069... mm²`, matching current `296.3985302453713` | Update provenance-backed expected value; retain Mu_lim, Ast and existing precision/tolerance | 10–20 min |
| Two authored W3 positive journeys | Fixtures request shear-strength basis Ast=1326/901.6 mm² but generate two 20 mm bars per zone, 628.318530718 mm². The unchanged validator correctly rejects them. Three bar records represent start/mid/end zones, not six simultaneous bars | Reconcile the authored supplied-steel basis/layout with actual per-zone area; preserve rejection of overstated shear steel. Do not relax the validator or reopen completed per-bar equations | 30–60 min |

Estimated total is roughly 1.5–3.5 hours, with uncertainty from fixture
dependencies and deterministic manifest generation. No numerical production
change is included. If a repair exposes a new outcome-changing calculation
defect, stop that dependent change and define a separately evidenced correction.

After this small batch, run only the ten affected cases and required generated
metadata checks. Reuse unchanged successful consumer evidence by exact source
identity. A changed wheel must be rebuilt offline and checked for metadata,
RECORD/package contents, installed origin and expected outcomes. Do not rerun
all previously accepted numerical benchmarks merely because bookkeeping
metadata changed.

## Source availability and edition gate

The subsequent [bounded issued-amendment slab corrections](slab-issued-amendment-corrections.md)
address the two demonstrated distribution-spacing and solid-slab maximum-shear
outcomes. Their independent mapping review, separate numerical commits and exact
wheel evidence belong to a new candidate. They preserve the cumulative edition,
material/applicability and installed-Windows qualifications listed below.

The controlled IS456:2000 collection includes Amendments 1-5 and reaffirmation
markers through 2021, SHA-256
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`,
and Amendment 6, June 2024, SHA-256
`4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
Both PDFs match their recorded hashes. The collection's base provisions are
not uniformly consolidated: PDF47/printed46 still shows 450 mm while appended
A3 PDF112/printed2 changes Cl. 26.3.3(b)(2) to 300 mm. Apply ordered amendment
instructions, rather than inferring conformance from the cover or file name.
Original SP16 remains corroborating historical evidence, not the selected
integration engine. Its age alone does not invalidate a provision.

The lawful current-status sources are the
[official BIS standards portal](https://standards.bis.gov.in/) and its
[IS456 catalogue entry](https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6InVIejZUOFI5V1Z5RXZMWEZGNnh4a1E9PSIsInZhbHVlIjoiZ1ZhcnlpWEFRVE00Q1dndk1Tc3lrQT09IiwibWFjIjoiYjAzMjg2ZDY3YWE0NzhkNGRlZDczYzI2ZGJiZTVkNThiNThlYmZmNTI3MDFmZTA0MzljNWM5Njg1ZWNmYjhhNiIsInRhZyI6IiJ9).
The original web reader received a JavaScript shell. The follow-up direct
rendered-browser observation on 1 October successfully read Fourth Revision,
reviewed 2025, reaffirmed July 2025, and six amendment rows with years
2001/2005/2007/2013/2019/2024. The dated
[source inventory](is456-official-source-inventory.json) separates official
publication status, private source possession and provision qualification.
All 20 physical A3-6 pages were visually reviewed, including two blank versos.

The [reviewed impact matrix](is456-amendment-impact.md) indexes 95 instruction
blocks against 13 supported family journeys and 25 advanced exports. It
identifies two supported-slab discrepancies: the distribution-spacing cap
retains 450 mm instead of amended 300 mm, and solid-slab maximum shear uses
full Table 20 instead of half. No numerical change was made in this source
packet. The matrix records existing bounded conformance separately from
unverified applicability and source interpretations.

The resumed A1-2 follow-up on PR #1023 main,
`c45cb89f13e8821716553b096003eb22763e083e`, visually indexes eight additional
physical pages and 42 instruction blocks against the same 38 maintained
callers: 1,596 new dispositions. Its current owner hashes and 11 read-only
canonical/owner diagnostics are separate from the original A3-6 evidence.
The arithmetic union is 137 blocks and 5,206 dispositions across the two
snapshots; these counts include explicit unknowns and exclusions. See the
[current A1-2 packet](is456-amendment-impact.md#amendment-1-2-current-source-packet--1-october-2026).
Complete independent review and its essential concrete-bearing classification
repair are accepted for bounded documentation purposes; six affected checks
and identity/count validation pass. No calculation code changed and no new
numerical defect was demonstrated by this A1-2 packet.

The separately authorized [staircase spacing follow-up](is456-amendment-impact.md#current-staircase-spacing-follow-up--1-october-2026)
subsequently confirmed and locally corrected the old 450 mm scalar ceiling in
the maintained longitudinal waist-slab route. Independent frozen review
accepts the software correction; 92 focused cases, full Python 8,664, FastAPI
614, React 293 and repository 32/32 pass (ten unchanged-input check results
reused). The original ledger failure history is preserved. Eight isolated
installed Mac wheel cases pass, with 224 installed module origins and no source
fallback. Physical spacing datum/drawing, installed Windows/ETABS/Excel/XLL
qualification and full engineering approval stay HOLD. It preserves the
original A3-6 and A1-2 snapshots and accepted PR #1022 numerical evidence.

The separate [current concrete-bearing reconciliation](is456-amendment-impact.md#current-concrete-bearing-operation-follow-up--1-october-2026)
traces the actual Cl. 34.4 `fck` consumer across 95 A3-6 instruction blocks:
43 unknowns, 36 external procedures and 16 absent changed calculations. The
original geometry-only assignments remain historical; the current appendix
retains physical material/grade/exposure HOLDs and the advanced/preview scope.
Independent frozen review accepts the bounded operation documentation;
identity/coverage checks and 12/12 affected repository checks pass, with six
unchanged-input results reused. No numerical defect or new supported capability
is demonstrated by that documentation packet.

The full six-amendment impact gate remains HOLD. The two demonstrated slab
outcomes are corrected in merged PR #1022. A1-2 inventory/caller coverage is
now recorded; remaining engineering qualification requires physical
material/coating domains, above-M60 substantiation, unverified cover/tie,
coefficient/direction bindings and the unresolved caller/source interpretations
recorded in both snapshots.
Source possession and page-count coverage do not close those qualifications.
A circulated draft is not an adopted standard. Companion-code scope retains
its own source version; no IS13920 or code-family scope expansion is inferred.
No new account, purchase or credentials were used. Standing source-use and
normalized-data distribution permission is passed; this is an edition and
interpretation gate, not another licensing-permission request.

## Final integration and publication state

### Current integrated state — 1 October 2026

[PR #1020](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1020)
merged the column, flange, material and bounded SLS corrections at
`32576ae0893bc246de152e6e9912efec89642717`.
[PR #1022](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1022)
then integrated the issued-amendment mapping and two supported-slab corrections
at `617cec0692680e38a82308b8705d9845d3758503`. Both merged trees match their
reviewed heads, and their required and broad hosted checks passed. The
[slab correction record](slab-issued-amendment-corrections.md#integration-and-acceptance--1-october-2026)
binds the final candidate, wheel and check identities. Original failed runs,
baseline matrix hashes and accepted private receipts remain historical evidence.

Software integration is complete for these two bounded packets. The cumulative
edition/material/applicability and installed Windows/ETABS/Excel/XLL HOLDs
remain; complete engineering approval remains false. No new package, tag or
release was published. Draft #1019's programme remains unaccepted. PR #1023
integrated the prior closing documentation. The owner subsequently resumed
bounded Library qualification overnight through 2 October 2026 03:30 UTC,
superseding the pause. The A1-2 documentation checkpoint has bounded independent
acceptance and passed affected local checks; external publication is
coordinated with the parent. Use the [current brief](../planning/next-session-brief.md)
and preserve the separate solver's coordinator and priority. Overnight work
does not authorize a release, merge or engineering-use certification.

### Historical qualification freeze and publication proposal

At the original qualification freeze, the local branch was
`codex/library-next-evidence-20260930`, HEAD/base
`96170d81cd94d323b56f0914ed0214d1bff967b8`. The correction candidate is
uncommitted; the 50 existing intended dirty paths and staged work are preserved.
This checklist was an additional documentation file. The follow-up may record
authorized local commits separately from the planning change. No push, merge, tag,
deployment or package publication occurred. Cached origin/main equals the base;
remote freshness is `NOT_CHECKED`, not current remote proof. Draft PR #1019
belongs to a different planning candidate and does not supply approval for its
broader programme. PR #1017's revision 2b2fac7 has verified successful validation
run 36374778128 and remains a separate dependency/code-owner review; older
weekly failures are not evidence that this revision or current main is broken.

Once the bounded repair and source gates are reconciled, the remaining final
software qualification is one exact committed-candidate hosted cycle: required
PR checks and a revision-specific cumulative Python/coverage, API and packaging
run. The maintained weekly lane also owns full React, dependency-audit and
Docker checks; they have not been duplicated on the shared Mac. Their exact
head and outcome must be recorded before claiming full-stack completion.
Cross-platform/minimum-runtime package support remains for that lane rather
than inference from this Mac's Python 3.11.15.

Before any publication, inspect active candidate worktrees and overlap/order,
refresh remote state, integrate the reviewed repairs, retain release metadata
and source identities, and follow the repository's exact release authorization
and required checks. Existing v0.24.0 authorization does not authorize
republishing this dirty candidate. No publication is part of this task.

Supported-library completion requires the caller, calculation, intake/status,
examples, transport and artifact criteria in the existing plan, with retained
case exclusions and source evidence. The accepted packets close their bounded
defects; they do not by themselves establish whole-library completion or
qualified engineering/construction approval.
