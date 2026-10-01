---
owner: Main Agent
status: active
last_updated: 2026-10-01
doc_type: spec
---

# IS 456 source reconciliation and Amendment 3-6 qualification packet

The parent authorized this bounded documentation packet on 1 October 2026 after
the initial planning handoff. It continues the
[supported-library completion checklist](../verification/library-supported-scope-completion.md)
without approving draft #1019's programme. This documentation packet makes no
calculation change or whole-library qualification claim. The solver's own
coordinator and Project_Manager V1 retain their existing authority and priority.

## Recommendation

Reconcile the actual controlled source collection with the current official
edition, then review every provision changed by Amendments 3-6 and map it to
the maintained supported callers. The finite source-review set is **20 PDF
pages**: four in Amendment 3, six in Amendment 4, seven in Amendment 5 and
three in Amendment 6. Reuse accepted Amendment 1-2 and calculation evidence
only where exact source/case identities substantiate the row. Unknown coverage
stays unknown. This first packet does not close the complete issued-amendment
gate merely by finding all six amendment files.

Estimated effort: 2-6 hours for inventory, visual provision indexing and a
bounded caller matrix, with uncertainty from interpretation and owner coverage.
Six hours is an investigation checkpoint, not a conclusion deadline. Record
progress and unresolved evidence without guessing or dropping a dependent row.

## Verified starting point

- PR #1020 is merged as `32576ae0893bc246de152e6e9912efec89642717`.
  GitHub's direct comparison of that commit to `main` was identical on
  1 October 2026; `git fetch origin` completed. Accepted head `371c1fe5`
  and its numerical evidence remain preserved.
- The primary checkout is clean on the completed branch
  `codex/library-next-evidence-20260930`. Planning is isolated in
  `external_data/task-worktrees/is456-amendment-qualification-20261001` under
  the primary repository, branch
  `codex/is456-source-qualification-plan-20261001`, based on the merge commit.
  The task is the sole writer for that planning branch. Existing worktrees
  were inspected and preserved; no publication ordering decision was made.
- The [live BIS catalogue](https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6InVIejZUOFI5V1Z5RXZMWEZGNnh4a1E9PSIsInZhbHVlIjoiZ1ZhcnlpWEFRVE00Q1dndk1Tc3lrQT09IiwibWFjIjoiYjAzMjg2ZDY3YWE0NzhkNGRlZDczYzI2ZGJiZTVkNThiNThlYmZmNTI3MDFmZTA0MzljNWM5Njg1ZWNmYjhhNiIsInRhZyI6IiJ9)
  was directly read in the browser: IS 456:2000, Fourth Revision, reviewed
  2025, reaffirmed July 2025, six amendments, years 2001/2005/2007/2013/2019/2024.
  A circulated Fifth Revision draft does not establish a published replacement.
- Both protected PDFs match their recorded SHA-256 values. Their title and
  Amendment 3-6 heading pages were rendered and visually inspected using
  existing macOS PDFKit. No installation or new source acquisition was needed.
  The initial planning turn inspected identity/heading pages. The authorized
  continuation has inspected all 20 amendment pages; two are blank versos.
  The dated [source inventory](../verification/is456-official-source-inventory.json)
  separates that inspection from supported-impact qualification.

## Source inventory

The machine-readable [planning baseline](is456-amendment-qualification-baseline.json)
binds the verified metadata, safe source identifiers and owner-file hashes.
Original PDFs, extracted prose and images stay in the existing private source
store or durable ignored private evidence, outside Git and package contents.

| Source | Verified identity | PDF pages, one-based | Review still needed |
|---|---|---|---|
| Controlled IS 456 collection | `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`; 127 pages | Base/title 1-102; A1 103-108; A2 109-110; A3 111-114; A4 115-120; A5 121-127 | A3-5 pages indexed; full qualification retains explicit matrix HOLDs and A1-2 reuse limits |
| Amendment 6, June 2024 | `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`; 3 pages | 1-3 | All pages indexed; unresolved caller/material interpretations retained |
| BIS catalogue | Dated direct browser observation, 2026-10-01 | Six amendment metadata rows | Preserve a safe dated observation in the qualification receipt |
| Historical archival scan | Reviewed predecessor establishes A1-2 only | Existing accepted anchors | Cannot substitute for A3-6 or certify complete impact coverage |

The controlled file's cover identifies an August 2014 reprint including
Amendments 1-4 and reaffirmation through 2021; Amendment 5 is appended.
"Through Amendment 5" describes available source coverage. It must not imply
that every correction is already integrated into the base pages or the code.
The local corpus manifest is explicitly `UNREVIEWED_SOURCE_CORPUS`; automated
clause/table candidates do not establish reviewed interpretations.

## Scope and maintained owners

Freeze the 13 family journeys in
[`family_facade_registry.py`](../../Python/structural_lib/services/family_facade_registry.py)
and the promoted workflows, supported cases and exclusions in
[`capabilities.py`](../../Python/structural_lib/services/capabilities.py).
Use the [API classification](../reference/api-classification.json) to resolve
advanced public callers. Trace each affected owner through current code
source-reference constants and its existing family scope/acceptance ledger.
Experimental P-M-M, general frame analysis and excluded structural cases do
not become supported through this exercise.

Start with the shared requirements that can affect several callers: concrete
grade/applicability, reinforcement type and bond, material assumptions,
detailing cross-references and source-version claims. Then resolve every other
A3-6 target against the frozen caller set. Include Tables 12/13/26/27 for
maintained slab callers, and Annex F plus the Cl. 35.3.2 Amendment 4 exposure
limit for maintained beam serviceability callers. Do not use the
older `docs/reference/clause-map.json` as a complete owner list: its registry
count is 119, while current `clauses.json` records 180; decorator coverage is
an inventory aid, not provenance qualification.

Two concrete initial anchors warrant reconciliation, without presuming a new
calculation defect:

- The accepted deep-beam ledger already identifies the A3 correction from
  Cl. 29.3.4 to Cl. 32.5. Verify its current implementation and reuse the
  accepted bounded evidence rather than treating it as a new repair.
- A4 Table 2 Note 2 qualifies applicability above M60. Direct material
  helpers currently accept `fck=15-80 N/mm2`; supported route domains are
  separate. Map actual callers and declared engineering boundaries before
  claiming the representative formulas apply throughout that helper range.

Keep named profiles `IS456_FIG23_REP_GS115_V1` and
`IS456_ANNEX_C_RECT_SINGLE_V1`. Manufacturer steel-family applicability,
arbitrary reinforcement layouts, finite creep history and slab direct
deflection retain their existing limits. Passing hosted Windows/macOS tests
does not supply real installed Windows/ETABS/Excel/XLL evidence.

## Proposed deliverables and separate commits

1. `docs/verification/is456-official-source-inventory.json`: dated official
   status, numbered source chain, actual hashes/page ranges and review states.
2. `docs/verification/is456-amendment-impact.json` and a short companion
   Markdown explanation: one reviewed row per changed A3-6 provision,
   supported-caller crosswalk, declared applicability and unresolved coverage.
3. A surgical update to the source/edition section of
   `docs/verification/library-supported-scope-completion.md`, preserving the
   accepted historical evidence and separating current inventory from impact
   qualification. Reconcile another family source claim only if its exact row
   proves the statement needs qualification.

Use one local commit for dated inventory and one for the reviewed impact matrix
and completion-checklist reconciliation. A future new PR requires the parent's
separate publication scope after content freezes. Exact
rows govern the changes. No production formula, table value, runtime profile,
contract, dependency or installed application changes are in this packet.
An outcome-changing discrepancy needs an independent calculation and a
separately explicit correction scope before implementation.

Each matrix row records: amendment number/date; protected source ID/hash;
PDF and printed page anchors; clause/table/figure/annex identifier; project-
authored change classification; governing earlier/later amendments; maintained
caller/owner; supported case and units where relevant; applicability boundary;
impact (`unchanged`, `affected`, `unknown`, `outside_supported_scope`);
resolution (`current_conforms`, `confirmed_discrepancy`, `unverified`, or
`not_applicable`); independent evidence anchor; and a concise rationale.
`affected/current_conforms` is distinct from a discrepancy. Absence from a
registry cannot alone justify `outside_supported_scope` or `unchanged`.

## Testable acceptance and finite stop

- The dated source inventory accounts for the published Fourth Revision and
  all six amendments; source possession and page review are separate fields.
- Every one of the 20 A3-6 pages receives visual inspection; every amendment
  change has a stable row and source anchor. Later substitutions are applied
  in order. Unreadable or ambiguous changes retain `unknown` with a reason.
- Every frozen family journey and promoted advanced workflow has a coverage
  disposition through its actual governing source owners, or an explicit
  unresolved owner. Tables/annexes and shared material requirements are included.
- Every non-unknown supported-impact conclusion has primary-source and
  current-owner anchors. A suspected numerical discrepancy is not closed by
  comparator agreement or a passing regression alone.
- Independent review uses exact document/source hashes and the frozen caller
  inventory. Existing accepted benchmarks are reused by identity; any actual
  discrepancy is returned as a separately bounded proposed correction.
- After documents freeze, validate JSON structure, unique row IDs, page/owner
  references, status completeness, links and protected-content exclusions.
  Run only the applicable documentation/metadata checks. No unchanged broad
  numerical, frontend or installed-application suite is duplicated locally.
  A future PR must pass its required hosted checks on its final head.
- Stop after one inventory pass, one complete A3-6 provision pass and one
  independent matrix review, with every unresolved row explained. At six hours,
  record an investigation checkpoint; elapsed time does not authorize dropping
  unknowns or concluding an incomplete row. Never turn missing evidence into a
  formula edit or guessed verdict.

## Dependencies and actual blockers

The controlled sources and existing runtime are present; new accounts,
purchases, dependency installs and repeated licensing permission are not
dependencies. Official download attempts previously failed technically; this
turn's browser metadata read succeeded and required no download.

Complete latest-amendment impact qualification remains blocked on the actual
provision/caller reconciliation, independent interpretations and any unresolved
A1-2 reuse coverage. Steel-family and higher-grade concrete applicability are
separate declared-domain questions. Real installed Windows/ETABS evidence
requires the existing installed-evidence lane and its coordinator; this Mac
planning packet cannot close it. The source files' existence does not satisfy
any of those gates.

No push, merge, tag, package, release or solver-source organization is part of
this planning turn. Before future publication, refresh main and compare active
candidate bases/heads and changed paths under the canonical Git workflow.
