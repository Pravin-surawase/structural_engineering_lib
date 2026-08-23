---
task: INDIA-3-G0
title: IS 13920 Existing-Surface Truth Audit
status: active
owner: Main Agent and qualified structural engineer
created: 2026-08-24
last_updated: 2026-08-24
doc_type: spec
complexity: advanced
tags: [india-3, is13920, source-truth, audit, beam, column, joint]
---

# INDIA-3-G0 IS 13920 Existing-Surface Truth Audit

## Decision

**READY FOR ONE BOUNDED G0 AUDIT; ENGINEERING IMPLEMENTATION IS NOT YET
AUTHORIZED.** Start from exact hosted `main` commit `3e979687`, after M0 merged
through PR #860 with all required checks green. Audit only the existing IS
13920 beam, column, and strong-column/weak-beam joint checks. The G0 result may
accept a current bounded claim, require a separately scoped repair packet, or
return `HOLD`.

The preserved source-library candidate `9c976b1f` is not transplanted or
cherry-picked. Its durable private-source boundary already merged through PR
#849, while its shared task/session documents predate M0 and its base lacks the
subsequent product packets. The fresh branch
`codex/india-3-g0-truth-audit` owns the reconciled G0 packet.

This packet changes no structural formula, public signature, API response,
React surface, Excel workbook, or capability status. It does not promote any
private navigation record to accepted engineering truth.

## Source-readiness boundary

The Git-ignored private archive verifies 25 documents, 27 aliases, 732 cached
pages, three project-authored IS 13920 implementation-navigation records, and
142 pages requiring visual or OCR review. The six IS 13920 PDF identities
comprise a 2016 base, a 2016 consolidated Amendment 1-2 candidate reaffirmed in
2021, and separate byte-distinct Amendment 1 and Amendment 2 copies. Every IS
13920 document remains `UNREVIEWED_SOURCE_CORPUS`; non-base applicability is
`UNKNOWN_PENDING_ENGINEERING_REVIEW`.

The three beam, column, and joint records remain
`UNREVIEWED_IMPLEMENTATION_CLAIM`. They provide symbol navigation only. The
accepted source-normalized engineering-value count remains zero. A filename,
search hit, extracted text fragment, decorator, current implementation, or
passing test is not source acceptance.

The audit may record normalized project-authored values only after complete
governing-page and amendment-chain review. Protected prose, page images,
watermarks, extracted text, private hashes, database bytes, or private helper
code must not enter tracked files, packages, logs, or PR messages.

## Exact current surface

| Family | Core owner | Public/transport surface | Direct test inventory | Current generated claim | G0 disposition |
|---|---|---|---:|---|---|
| Beam detailing checks | `codes/is13920/beam.py`: geometry, minimum/maximum tension steel, confinement spacing, composed check | package/service `check_beam_ductility`; `POST /api/v1/design/beam/ductility-check` | 5 example/unit + 17 property tests | `IMPLEMENTED_BOUNDED` | `AUDIT_REQUIRED` |
| Column detailing checks | `codes/is13920/column.py`: geometry, longitudinal-steel limits, confining spacing/length/area, composed check | package/service `check_column_ductility_is13920`; `POST /api/v1/design/column/ductile-detailing` | 18 direct core tests plus typed-route coverage | `IMPLEMENTED_BOUNDED` | `AUDIT_REQUIRED` |
| Beam-column joint SCWB check | `codes/is13920/joint.py`: `check_scwb` | code-namespace only; no package-root service or FastAPI route | 21 direct core tests | `IMPLEMENTED_BOUNDED` with no complete joint/public-service claim | `AUDIT_REQUIRED` |
| Wall detailing | none | none | 0 | `HELD` | `OUT_OF_SCOPE_RETAIN_HOLD` |
| Foundation detailing | none | none | 0 | `HELD` | `OUT_OF_SCOPE_RETAIN_HOLD` |

The generated manifest currently reports three supported and two held IS 13920
families. That is the claim under review, not the audit conclusion. The same
manifest has 16 known IS 13920 references, five registered references, and 11
metadata-only references. Several exact subclauses used by code remain
registration-only, and the displayed titles for Clauses 6.1.2 and 6.2.1 must be
checked against the accepted source chain before they are retained or changed.

## Audit sequence

### G0-1 — Resolve source identity and amendments

1. Visually inspect every complete governing page for the current beam,
   column, and joint claims in the base, consolidated, and separate amendment
   copies.
2. Reconcile duplicate amendment copies by engineering identity without
   deleting or silently preferring any retained source.
3. Record one accepted edition/amendment applicability chain per family, or a
   precise `HOLD_SOURCE_IDENTITY` / `HOLD_AMENDMENT_APPLICABILITY` reason.
4. Keep reaffirmation, edition, amendment, applicability, and distribution as
   separate fields.

### G0-2 — Map source to every current calculation

For each core function, record its exact governing reference, variables,
units, equations or normalized limits, conditions, domain, result meaning, and
failure behavior. Compare that map with decorators, docstrings, error clauses,
package exports, FastAPI descriptions, and the generated capability manifest.

The audit must explicitly test—not assume—the following current claims:

- beam dimensional limits, minimum and maximum tension steel, confinement-zone
  spacing, and the meaning of the composed result;
- column dimensional/aspect limits, minimum and maximum longitudinal steel,
  special-confinement spacing and length, confining reinforcement area, and
  the service wrapper's default confined-core-area assumption; and
- joint moment-capacity direction/combination rules, applicability, required
  factor, equality tolerance, and the meaning of `PASS`/`FAIL`.

Any behavior without a confirmed governing reference is `HOLD_UNMAPPED`, even
when its existing tests pass. Metadata-only and registration-only entries must
not be counted as implemented calculations.

### G0-3 — Freeze independent benchmarks and unsafe cases

Create one independent, replayable hand benchmark per retained family. Each
benchmark binds the accepted source identity, exact clause, input units,
supported case, expected intermediate values, final disposition, and numerical
tolerance. Existing implementation output and existing tests may reproduce a
benchmark but cannot originate it.

Each family also needs at least one governing boundary, one valid inadequate
case, one invalid input case, and one out-of-domain case. Unsupported geometry,
materials, assumptions, actions, or incomplete inputs fail closed rather than
receiving an inferred design result.

### G0-4 — Reconcile public-contract truth

Compare core, service facade, package root, FastAPI/OpenAPI, generated manifest,
and current documentation. Preserve only transports that delegate to the
accepted core result without changing units, defaults, status, errors, or
provenance. A public route is not required for the joint check; adding one is a
separate product decision.

Classify each family as one of:

- `ACCEPT_CURRENT_BOUNDED` — source, formula, benchmark, domain, tests, and
  public claim agree;
- `REPAIR_PACKET_REQUIRED` — a confirmed source/code/contract mismatch changes
  the main result or advertised scope; or
- `HOLD` — accepted source identity, amendment applicability, independent
  benchmark, or safe domain remains incomplete.

### G0-5 — Freeze the follow-on sequence

Only after G0-1 through G0-4 are complete, freeze the minimum independent
packets needed to resolve accepted findings. Beam, column, and joint decisions
stay separate so one incomplete family cannot inflate or block truthful status
for the others. One cumulative IS 13920 acceptance gate follows all accepted
repair packets.

## Explicit non-goals

- no new IS 13920 formula, wall, foundation, joint-design, or seismic-analysis
  capability;
- no IS 875 load generation, IS 1893 action generation, load combinations,
  response spectrum, dynamic analysis, FEM, ETABS model control/write-back, or
  Excel work;
- no new FastAPI or React surface merely for symmetry;
- no copied protected prose, source page image, OCR transcript, or private
  archive content in Git; and
- no package version, tag, publication, release, professional-use approval, or
  engineering-use approval.

## G0 acceptance criteria

G0 is complete only when:

1. each existing family has an accepted source/amendment chain or an explicit
   source hold;
2. every current numeric behavior and outcome-changing default is mapped to a
   confirmed source reference or held;
3. each proposed retained family has one independent benchmark plus boundary,
   inadequate, invalid, and out-of-domain cases;
4. decorators, docs, exports, routes, schemas, tests, and generated capability
   truth agree with the family decision;
5. the private verifier and repository boundary test pass with no private
   material tracked or packaged;
6. the decision evidence freezes the exact repair/hold sequence without
   implementing it; and
7. focused documentation/truth checks, the quick repository gate, normal
   staged hooks, and every required hosted check pass on one unchanged
   candidate.

The broad Python/FastAPI/React and full repository gates are deferred until a
later behavior-changing INDIA-3 milestone unless G0 exposes a confirmed
repository-wide defect. G0 is an audit/decision packet, not software or
engineering acceptance.
