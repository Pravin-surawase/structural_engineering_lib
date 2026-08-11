# Pre-Release Checklist

**Type:** Reference
**Audience:** All Agents
**Status:** Review
**Importance:** High
**Created:** 2026-03-31
**Last Updated:** 2026-08-11

## Current State

Release-ready source metadata: 0.23.1a1
Current public release: v0.23.1a1 Alpha

- **Release source:** tag `v0.23.1a1` at `95bed5621c2ff6e5bbcf1a25b7ac476f92ae4307`
- **Candidate PR:** #732 merged unchanged at `95bed562`; reviewed head `adb161b8` has the same tree
- **Release target:** v0.23.1a1 Alpha, published 2026-08-11 local time
- **Publication state:** PyPI and GitHub prerelease published; exact public-version UAT green
- **Review policy:** qualified structural-engineering review is required before stable/engineering-use approval, not before this Alpha release

## Next Alpha Readiness Checklist

- [x] Integrate the complete `FOOT-ISO-RC-V1` source head `886871ae` into the candidate ancestry through PR #730
- [x] Pass `./run.sh release footing-inclusion-check` with exact footing-owned files and Python/FastAPI/React integration markers present
- [x] Verify the frozen local wheel through isolated installed-package tests and CLI UAT; retain the inclusion receipt hash in the local rehearsal record

### v0.23.1a1 Release Authorization

- Source: `72d2d9b8ccc1350b46499dc5a5d08df6284fe10f`
- Evidence: [v0.23.1a1 local rehearsal](../verification/alpha-0231-local-prepublication-rehearsal.md)
- Status: owner-authorized Alpha release; TestPyPI and exact-head CI evidence must pass before the production tag
- [x] Owner authorizes the v0.23.1a1 TestPyPI rehearsal
- [x] Owner authorizes the v0.23.1a1 tag, production PyPI publication, and GitHub Release after exact CI evidence passes
- Authorization source: direct owner instruction in the active Codex task on 2026-08-11

### v0.23.1a1 Publication Evidence

- TestPyPI run: `31467980119`, reviewed source `adb161b8`
- Production run: `31468341946`, source/tag `95bed562` / `v0.23.1a1`
- Wheel: 529,982 bytes, SHA-256 `e586db493bbb80c56474a4855f162b9d647911648f68331c950f1ab2deafd622`
- Sdist: 438,007 bytes, SHA-256 `5cd0e1cefe486ed3188a6cca67e728d2df162578cc17eb135583852afd6f4bb4`
- CycloneDX 1.6 SBOM: 61 components, SHA-256 `29810e0e7e0e3e7e4380db635d9808797b6ddc241493616f0764991fa551c3b5`
- Exact public PyPI verification: 5,055 passed, 51 skipped, 2 deselected; installed `job`, `critical`, and `report` workflows green
- GitHub prerelease and its manifest, SBOM, inventories, wheel, and sdist assets are public and digest-matched

## Beta Readiness Checklist

### Required Before Beta

- [x] Core beam design (flexure, shear, detailing) complete
- [x] Beam supported-route regression evidence retained; no blanket formula-certification claim
- [x] FastAPI public-service adoption demonstrated for beam, column, footing and slab
- [x] React frontend with 3D visualization
- [x] CSV/ETABS import pipeline working
- [x] Export pipeline (BBS, DXF, HTML report)
- [x] C3 source commit PR Gate green on all required validation lanes
- [x] Column supported-route correction and focused benchmarks pass
- [x] Column detailing (Cl 26.5.3) and ductile detailing (IS 13920) complete
- [x] IS 13920 seismic ductile detailing integration complete
- [x] Isolated-footing load-transfer slice and legacy A1 correction implemented
- [x] Bounded one-way and two-way slab workflows implemented
- [x] Canonical API facade, compatibility paths and capability registry documented
- [x] Public `clauses.json` contains identifiers/project metadata only
- [x] Protected PDFs and extracted clause/table/formula candidates are local, hash-inventoried and Git-ignored
- [x] Owner-confirmed public-distribution permission for approved-scope normalized IS 456 data is recorded and enforced by release tooling
- [x] Wheel/sdist allowlist and exact-artifact UAT encoded in publish CI
- [x] Exact local wheel/sdist hashes, inventories, protected-content result and SBOM recorded
- [x] Exact local wheel clean-install tests and CLI UAT pass
- [x] CI-built artifact manifest, hashes, inventories and SBOM reviewed
- [x] Exact CI-built wheel UAT evidence reviewed
- [x] Owner authorizes the TestPyPI rehearsal
- [x] Owner authorizes the v0.23.0 tag, production PyPI publication, and GitHub Release after exact CI evidence passes

### v0.23.0 Publication Evidence

- Production run: `31332420554`, source/tag `3f880d5b` / `v0.23.0`
- Wheel: 478,903 bytes, 181 files, SHA-256 `cd56a5301160fc7d62154e9d6e567ba8bf9bb8608827c9454b63161276c5408a`
- Sdist: 395,422 bytes, 206 files, SHA-256 `fe03a86d6c518a5f293c874e825930bb79de984cb53bebaf63a7610c3f042a73`
- Manifest SHA-256: `efadd1e6b0b1e8c3c7e242a057ea83a3bbef19059462a5ccd5ccde5ac2ba9ab5`
- CycloneDX 1.6 SBOM SHA-256: `8c76f919df65e913d0d507d0ac824bb2c077fbb530a53732bc65bed68f482686`
- Exact public PyPI verification: 5,406 passed, 51 skipped, 6 deselected; installed `job`, `critical`, `report`, and help workflows green

### Required Before 1.0

- [ ] Stable API guarantee for every advertised supported route
- [ ] Professional validation by licensed structural engineer
- [ ] Performance benchmarks published
- [ ] Security audit complete (OWASP compliance)
- [ ] User documentation complete with worked examples
- [ ] PyPI stable release published
- [ ] Docker production image optimized
