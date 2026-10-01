---
owner: Main Agent
status: active
last_updated: 2026-10-01
doc_type: reference
---

# Bounded slab corrections from issued IS 456 amendments

This separately authorized implementation follows the
[source and caller reconciliation](is456-amendment-impact.md). That matrix
records the original PR #1020 numerical baseline; its diagnostic outputs and
owner hashes remain historical evidence. The basic one-way caller mapping
repair received a separate independent PASS before numerical implementation.
Final numerical acceptance requires independent review of the frozen candidate.

## Problem, source and correction

| Matrix row | Confirmed root cause | Bounded correction and independent expectation |
|---|---|---|
| AMD3-014 | Basic/complete one-way detailing and shared continuous/two-way distribution checks retained the base edition's 450 mm absolute maximum. | Amendment 3, August 2007, Cl. 26.3.3(b)(2), controlled PDF112/printed2: distribution maximum `min(5d,300 mm)`. At `d=125 mm`, adequate `14@300` passes spacing while `14@301` and `14@400` fail. At `d=50 mm`, the depth maximum remains 250 mm. Main-bar checks retain `min(3d,300 mm)`. |
| AMD5-022 | The solid-slab shear owner applied the full Table 20 maximum, producing the wrong remediation classification above the slab maximum. | Amendment 5, July 2019, Cl. 40.2.3.1, controlled PDF125/printed5: apply factor 0.5 locally to solid-slab maximum shear. Table 20, PDF74/printed73, M20 value 2.8 N/mm² gives slab maximum 1.4 N/mm². Equality is within this maximum; 2.0 N/mm² exceeds it. Concrete capacity remains a separate check. |

The controlled collection SHA-256 is
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
Source page images and protected prose remain private. Runtime results carry
the amended clause identities. The two-way panel adds an optional `source_refs`
carrier; shared reinforcement-region contracts remain unchanged.

## Applicable consumers and verification

Spacing applies to all three slab family journeys, five composed advanced
exports and the basic `design_one_way_slab_is456` provided-bar export. Shear
applies to those three journeys and five composed exports. The basic one-way
export performs no shear check; the flexure-only basic two-way export performs
neither check. External and built-in coefficient routes keep their existing
case and acceptance restrictions.

The independent boundary fixtures are maintained in
[`test_slab_issued_amendments.py`](../../Python/tests/integration/test_slab_issued_amendments.py).
High-shear fixtures use a short span so flexural capacity does not suppress
the shear composition. Spacing fixtures provide enough steel so spacing
determines the changed detailing outcome. Facade checks retain false
engineering approval. Existing slab and shared flat-slab reinforcement checks
are included in the focused verification batch. Table 20, beam and torsion
numerical owners are unchanged and checked by exact file identities and
focused existing behavior tests.

The local evidence receipt under
`external_data/library-evidence/3101d295/slab-amendment-corrections-20261001/`
binds the exact commits, tree, changed paths, wheel hash, package member
comparison, source test results and isolated installed-wheel consumer results.
Only successful recorded checks count as acceptance evidence. The wheel is a
local candidate at the existing package version; no package publication,
release, push or merge is authorized by this packet.

## Qualifications retained and finite stop

This packet corrects two demonstrated supported-slab outcomes. It does not
close cumulative IS 456 qualification. All matrix HOLDs remain: A1-2 cumulative
mapping; physical material, coating and manufacturer eligibility; above-M60
substantiation; staircase spacing; foundation main/distribution and solid-slab
shear applicability; flat-slab shear applicability; beam placement and
near-support shear bindings; general crack-rule bindings; Amendment 5 formwork
column interpretation; and Amendment 6 unspecified renumbering. Finite creep,
other declared unsupported cases and real installed Windows/ETABS/Excel/XLL
acceptance remain held. Source-use and normalized-data distribution permission
remain passed.

Stop after the scoped edits, independent boundary/caller verification and exact
candidate wheel evidence are frozen for parent review. Any new outcome-changing
finding outside these two provisions requires separate scope coordination.
