# IS 456 Library-First Evidence and Claim Crosswalk

**Type:** Reference
**Audience:** Developers
**Status:** Review
**Importance:** Critical
**Created:** 2026-08-09
**Last Updated:** 2026-08-09
**Date:** 2026-08-09
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
