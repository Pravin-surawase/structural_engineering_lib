# IS 456 Library-First Evidence and Claim Crosswalk

**Type:** Reference
**Audience:** Developers
**Status:** Review
**Importance:** Critical
**Created:** 2026-08-09
**Last Updated:** 2026-08-11
**Date:** 2026-08-11
**State:** C0-C4 complete; v0.23.0 Alpha published; approved-scope normalized-data public-distribution permission confirmed; qualified review deferred to final stable/engineering-use approval

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

The corpus manifest's non-distribution flag continues to protect the source
PDFs, extracted pages, prose, and images. It is not the authority for derived
normalized code data. On 2026-08-11 the owner confirmed source/licensing
permission for public distribution of normalized IS 456 data within approved
feature scopes. The canonical, release-validated record is
[`is456-public-distribution-permission.json`](is456-public-distribution-permission.json).

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

## Production release evidence

The owner-authorized v0.23.0 Alpha release was built from tag `v0.23.0` at
source commit `3f880d5bbc338baefc4aec8ed472cafe840a5c99` by protected production
run `31332420554`. The publish workflow, exact-wheel UAT, PyPI upload, and
GitHub prerelease creation all passed.

| Artifact | Size | SHA-256 | Inventory |
|---|---:|---|---:|
| `structural_lib_is456-0.23.0-py3-none-any.whl` | 478,903 | `cd56a5301160fc7d62154e9d6e567ba8bf9bb8608827c9454b63161276c5408a` | 181 files |
| `structural_lib_is456-0.23.0.tar.gz` | 395,422 | `fe03a86d6c518a5f293c874e825930bb79de984cb53bebaf63a7610c3f042a73` | 206 files |

Both content allowlist and protected-content gates passed. The exact manifest
SHA-256 is `efadd1e6b0b1e8c3c7e242a057ea83a3bbef19059462a5ccd5ccde5ac2ba9ab5`;
the CycloneDX 1.6 SBOM SHA-256 is
`8c76f919df65e913d0d507d0ac824bb2c077fbb530a53732bc65bed68f482686`.
PyPI and GitHub Release assets match these filenames, byte sizes, and hashes.

The exact public PyPI version passed 5,406 tests with 51 optional-dependency
skips and 6 deselections, followed by installed `job`, `critical`, `report`,
and CLI-help workflows. This proves the published artifact identity and
software behavior; it is not professional design approval.

## Release evidence contract

The production decision must use the exact CI-built artifacts, not a local
candidate. The `release-evidence` artifact must contain:

- source commit SHA and ref;
- wheel and sdist filename, byte size and SHA-256;
- wheel and sdist inventories;
- allowlist and protected-content gate results;
- CycloneDX SBOM;
- installed-site-packages UAT for beam, column, footing, slab, capability
  discovery and CLI help.

TestPyPI, version/tag selection, GitHub release and production PyPI upload
remain owner-only actions for future releases.

## Local prepublication rehearsal

This is the C3 local candidate built from frozen source commit `9be6eb35` on
draft PR #696. It is prepublication evidence only; it is not the CI release
identity:

| Artifact | Size | SHA-256 | Inventory |
|---|---:|---|---:|
| `structural_lib_is456-0.23.0-py3-none-any.whl` | 478,970 | `08377c11fa63bc01ce1493cfaf0ea5115966c5c3c5f5405782bb85fb032d8875` | 181 files |
| `structural_lib_is456-0.23.0.tar.gz` | 398,319 | `f3c6da86581c9dc06b2d69baf130095682d0dd09086321167036e466ea4cbac3` | 206 files |

Twine and the maintained candidate checker passed. Both inventories contained
zero private-source, research, migration-fixture, ACI, Eurocode, test, example,
script or docs entries. Packaged `clauses.json` records both protected-content
flags as false and contains no protected `text` or `data` keys.

Exact-wheel verification passed 5,404 tests with 51 optional-dependency skips
and 6 deselections, then completed the installed `job`, `critical`, `report`
and CLI-help workflows. The current-candidate preflight passed a clean install,
5,452 source tests with 3 skips and 6 deselections, the Node 24 React build,
version surfaces, release docs and release checks with zero preflight warnings.

The local CycloneDX 1.6 environment SBOM contains 196 components, is 239,585
bytes, and has SHA-256
`810b1be2f09c34f28358e1c1815a213f8d1ddda8b9adc474be3689701a9f0eb7`.
CI must regenerate its own SBOM and artifact manifest in the clean publish job;
the final release record must not substitute these local hashes for exact
CI-built artifact hashes.

The first clean build attempt was rejected because stale ignored
`structural_lib_is456.egg-info/SOURCES.txt` reintroduced excluded namespaces
despite correct package-discovery excludes. C3 fixed the root cause by pruning
those namespaces in `MANIFEST.in`, regression-checking the directives, and
updating the release skill to remove generated build, dist and egg-info state
before the exact build. An optional-DXF test was also corrected to follow the
installed environment instead of assuming the extra was present.

## C4 frozen review scope

The owner's 2026-08-10 request to finish this named bounded plan is the scope-
freeze instruction for C4. The frozen packet covers the controlled source IDs,
documented beam/column/isolated-footing/solid-slab cases, explicit units,
benchmarks, safe and unsafe outcomes, package boundaries, local artifact
identities, public claim limits, and unresolved holds recorded here and in the
master-plan ledger.

No new capability, multi-code namespace, excluded structural system or
protected source content is part of that scope. C4 does not record qualified
structural-engineering approval and does not authorize merge, tag, TestPyPI,
PyPI, GitHub Release, issue closure or branch deletion.
