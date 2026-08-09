# IS 456 Library-First Evidence and Claim Crosswalk

**Type:** Reference
**Audience:** Developers
**Status:** Review
**Importance:** Critical
**Created:** 2026-08-09
**Last Updated:** 2026-08-10
**Date:** 2026-08-10
**State:** software evidence complete for the task branch; engineering review and publication approval remain separate

## Controlled sources

| Source | SHA-256 | Pages | Use |
|---|---|---:|---|
| IS 456:2000 consolidated through Amendment 5, reaffirmed 2021 | `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264` | 127 | Primary controlled calculation source |
| IS 456 Amendment 6, June 2024 | `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | 3 | Route-specific amendment review |

The protected source corpus is local under
`private_sources/is456_library_first/`, covered by `.gitignore`, and excluded
from package discovery. Its manifest records two PDFs, 130 extracted pages,
1,208,170 extracted characters, seven imported Structautomate reference
artifacts, and automated candidates for clauses, tables, formulas and figures.
Those candidates remain `UNREVIEWED_SOURCE_CORPUS`; counts do not certify the
interpretation or completeness of any formula/table normalization.

The packaged `clauses.json` contains identifiers and project-authored metadata
only. It contains no protected standard text or table values.

## Claim-to-evidence crosswalk

| Public claim | Software evidence | Allowed wording | Held wording |
|---|---|---|---|
| Beam | Existing route tests plus P3 capability audit | Primary combined route covers rectangular flexure and shear; torsion is separate | Complete beam design or automatic combined torsion |
| Column | Corrected two-axis slenderness, minimum eccentricity, focused core/service/FastAPI tests | Bounded rectangular/symmetric workflows | General circular/asymmetric/arbitrary reinforcement design |
| Isolated footing | Existing bearing/flexure/shear tests plus independent Cl. 34.4 transfer benchmark | Supported square/rectangular checks and bounded concentric transfer | Combined/strap/raft/pile-cap, settlement or geotechnical design |
| Solid one-way slab | P6-P8 contracts, flexure and supplied-bar benchmark | Simply supported solid rectangular one-way strip | Continuity, direct deflection or modification-factor completion |
| Solid two-way slab | P9-P10 external-coefficient contract and benchmark | One interior four-edge-continuous flexure case with accepted external coefficients | Built-in coefficient truth, edge/corner panels or complete detailing |
| Public package | API entrypoint integration, manifest, clean-build inventory and installed-wheel UAT definition | Supported-case development preview | Whole-standard compliance or professional approval |

Passing tests and artifact gates establish software evidence only. Construction
use still requires source-page verification, independent calculations,
project-specific checks and qualified professional approval.

## C2 final product UAT

The 2026-08-10 C2 UAT exercised the bounded source and live product paths. The
focused pure-library/service matrix passed, 58 selected FastAPI cases passed,
16 selected React batch/export cases passed, and the Node 24 production build
passed. The matrix covered the public facade/capability contract, beam, column,
isolated-footing transfer, one-way and bounded two-way slabs, batch/report
status normalization, the maintained 422 envelope, and export endpoints.

The initial live React batch failed before FastAPI because local development
uses the Vite proxy and `react_app/vite.config.ts` did not proxy `/stream`.
Adding that missing proxy entry repaired the root cause. The repeated live path
imported a safe beam and a 600 kN unsafe-shear beam, received coherent SSE
`PASS`/`FAIL` results, rendered `1 passed`/`1 failed`, and applied only the safe
result; the unsafe beam remained pending with its original 600 kN shear.

Live requests through port 5173 also proved the maintained column, isolated-
footing, one-way-slab, and 422-envelope paths. Export response bytes were
validated rather than inferred from HTTP success:

| Artifact | Size | SHA-256 | Byte evidence |
|---|---:|---|---|
| BBS CSV | 959 | `c34cb245d3ead57e5035c19f7590c6c92122b2399da44b5cf7f384779f5f8067` | `bar_mark`, `diameter_mm`, `total_weight_kg` headers |
| Beam DXF | 48,522 | `037a879e294cac659710530c54c3862ee79421b260dde01da8ea9ac88dc50134` | `SECTION` and `EOF` records |
| Unsafe HTML report | 8,725 | `1524c1abc27eaa2544f5414c717ba0130e601f9846b1a70baec3f7a12ed77f8a` | overall `FAIL`; no promoted overall PASS |

These are source-tree/live-development artifacts, not C3 release identities.

## Release evidence required from CI

The production decision must use the exact CI-built artifacts, not a local
candidate. The `release-evidence` artifact must contain:

- source commit SHA and ref;
- wheel and sdist filename, byte size and SHA-256;
- wheel and sdist inventories;
- allowlist and protected-content gate results;
- CycloneDX SBOM;
- installed-site-packages UAT for beam, column, footing, slab, capability
  discovery and CLI help.

TestPyPI, the final version, tag, GitHub release and production PyPI upload are
owner-only actions.

## Local prepublication rehearsal

This is local candidate evidence only; it is not the release identity:

| Artifact | SHA-256 | Inventory |
|---|---|---:|
| `structural_lib_is456-0.21.6-py3-none-any.whl` | `685118b6afc29d4ef49dad91c93ec25ae4c34a186e678636d40b174a016b7e04` | 181 files |
| `structural_lib_is456-0.21.6.tar.gz` | `ef144405b47133a9f7324707e051762472002ab6586d33cf2bc91b8c864b9450` | 206 files |

The clean wheel install passed beam, column, isolated-footing transfer,
one-way/two-way slab, capability-discovery and CLI UAT. Package inventories
contained no private sources, research modules, migration fixtures, or empty
ACI/Eurocode placeholder namespaces. The final release record must replace
these local hashes with the exact CI-built artifact hashes.
