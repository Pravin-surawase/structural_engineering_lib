---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: reference
complexity: intermediate
tags: [contracts, errors, status, units]
---

# External Contract, Error, and Status Guide

Canonical scalar names carry units (`_mm`, `_mm2`, `_kn`, `_knm`, `_nmm2`).
Member-design actions are finite non-negative magnitudes unless a future field
explicitly says `signed` and publishes its axis convention.

Invalid intake raises `InputContractError` containing `InputIssueV1` records.
Every issue has a stable code and exact path; optional received value,
constraint, allowed values, and correction guidance remain structured.

A valid calculation returns separate states:

| Axis | Meaning |
|---|---|
| intake | whether all calculation-bearing input was accepted |
| calculation | whether the declared calculation completed |
| engineering | `PASS`, `FAIL`, `HOLD`, or not evaluated |
| freshness | whether input and calculation identities still match |
| final review | claim state retained for the one end-of-programme engineer review |

The final-review field does not block B0, F0, or R0 implementation. It prevents
software completion from being misrepresented as an engineer-reviewed design.
Under the current owner decision, that review is assigned once after the
integrated library is complete.

Current source, public wheel, a newly built exact-head wheel, REST projection,
generated client, React projection, and Windows application evidence are
distinct objects. A passing source test does not prove a public artifact or a
Windows Excel/ETABS integration.
