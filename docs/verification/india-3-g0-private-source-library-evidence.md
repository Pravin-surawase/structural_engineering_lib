---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: reference
task: INDIA-3-G0
---

# INDIA-3 G0 Private Source-Library Evidence

## Decision

**SOURCE FOUNDATION READY; ENGINEERING DECISION PENDING.** The primary checkout
now retains one Git-ignored, hash-bound, searchable private source library for
the existing IS 456 corpus and the newly discovered IS 875, IS 1893, IS 13920,
and IS 2950 PDFs. This clears repeated source discovery and navigation work. It
does not accept an edition, amendment effect, formula, benchmark, capability,
release, or professional-use claim.

Protected PDFs, extracted page text, database bytes, private helper code, and
source-expression search results remain under `private_sources/` in the primary
checkout. They are untracked, excluded from packaging, and not materialized in
linked worktrees. Public repository content records only this boundary and
aggregate verification facts.

## Exact local inventory

The private SQLite library contains:

| Standard family | Distinct PDF identities | Cached pages |
|---|---:|---:|
| IS 456 | 2 | 130 |
| IS 875 | 7 | 181 |
| IS 1893 | 8 | 280 |
| IS 13920 | 6 | 84 |
| IS 2950 | 2 | 57 |
| **Total** | **25** | **732** |

Twenty-seven original paths resolve to those 25 identities; two exact repeated
downloads are aliases rather than duplicate stored files. Twenty-three PDFs
were copied from Downloads into the private archive. The two existing
controlled IS 456 PDFs remain in the earlier private corpus and are referenced
without duplicate bytes.

The database and its private importer record:

- SHA-256, logical and hash-bound source IDs, original filename aliases, title,
  standard, part, edition, revision, amendment, reaffirmation metadata, byte
  size, PDF page count, and archive path;
- separate identity, review, applicability, and distribution states;
- page-numbered extracted text plus text hashes and FTS5 private search;
- explicit visual/OCR-required flags; and
- project-authored normalized references with units, conditions, page range,
  review state, and no source-excerpt field.

## Extraction and review boundary

Private verification reports 590 text-searchable pages and 142 pages requiring
visual or OCR review: 113 pages have only a low-volume text layer and 29 have no
extractable text. The low-text rule was added after the consolidated IS 13920
PDF revealed scanned pages containing only a short watermark text layer.

No incomplete clause pointer was saved as accepted source normalization. Three
`UNREVIEWED_IMPLEMENTATION_CLAIM` navigation records bind the current beam,
column, and strong-column/weak-beam symbols to their existing decorator and
capability-manifest clause claims. They contain no source-derived values and no
page acceptance. The accepted source-normalized engineering-value count is
zero. INDIA-3-G0 must inspect the complete relevant pages and amendment chain
before promoting any beam, column, or joint reference record.

All newly imported non-IS-456 documents remain
`UNKNOWN_PENDING_ENGINEERING_REVIEW`. Parallel byte-distinct copies exist for
IS 13920 Amendments 1 and 2 and IS 2950 Part 1; none is silently preferred.
The older monolithic IS 1893:1984 source is explicitly historical pending
review.

## Reuse contract

Future source work starts by listing or searching the private database, then
visually reviews only the complete pages that govern the bounded packet. A
downloaded filename, search hit, OCR result, decorator registration, or
existing implementation is navigation evidence only.

Normalized data may be added only when one bounded packet records the exact
source identity, edition/amendment applicability, clause/table/figure/formula
reference, units, limits, conditions, page location, independent benchmark,
unsafe and out-of-domain behavior, and review state. Protected prose, page
images, or publication-ready reproductions must not enter tracked files or
package artifacts.

## Verification

- Git ignore: database and representative archived-PDF paths resolve through
  the root `/private_sources/` rule; `git ls-files private_sources` is empty.
- SQLite integrity, foreign keys, all 25 PDF hashes, 732 cached page rows, and
  FTS ownership pass the private verifier.
- The exact-download seed is idempotent by SHA-256; duplicate paths become
  aliases and originals in Downloads are not moved or deleted.
- Repository boundary regression covers the prior IS 456 manifest, the new
  SQLite database, and an archived IS 13920 PDF path.
- The affected focused checks, documentation front matter, maintained links,
  context manifest, and consolidated quick gate pass; quick reports `10/10`
  with zero reused results.

## Next INDIA-3-G0 boundary

Use the controlled IS 13920 consolidated/base copies and separate amendment
copies to audit the current beam, column, and strong-column/weak-beam joint
surface. Freeze one truthful acceptance sequence or return `HOLD` where the
source, amendment applicability, benchmark, or public contract is incomplete.
Do not implement IS 875, IS 1893, new IS 13920 formulas, wall/foundation
provisions, release, ETABS, or professional approval in this G0 packet.
