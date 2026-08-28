# Pre-Release Checklist

**Type:** Reference
**Audience:** All Agents
**Status:** Review
**Importance:** High
**Created:** 2026-03-31
**Last Updated:** 2026-08-28

## Current State

Current source metadata: 0.24.0a1 (later development source)
Current public Alpha: v0.24.0a1

- **Published source:** tag `v0.24.0a1` at `71b7065216d4266d63ad6b31bd39bba81fa16efc`
- **Published wheel:** 774,739 bytes; SHA-256 `b5e0df7b561e8c715f37c602200eaae2c369ec5dc992eec87110a77c1026201a`
- **Published sdist:** 652,423 bytes; SHA-256 `8c1d6b762a779686be5d17ed0dd9719f7155a5863a764e943a0e1ba9aeb0a53b`
- **Publication state:** `RELEASED_ALPHA` on PyPI and GitHub on 2026-08-24
- **Current main boundary:** B0/F0 and later external-preview work merged after the tag and are not part of the published artifact
- **Review policy:** qualified structural-engineering review is required before stable/engineering-use approval, not before this Alpha release

## v0.24.0a1 Published Alpha State

- [x] Owner authorizes preparation of v0.24.0a1 without tag or publication
- [x] Base the release lane on synchronized `main` at `b3309260686a05b4cbb9c9358c89d6218a700357`
- [x] Repair the stale footing inclusion receipt and inclusive 4.0% column-ratio boundary
- [x] Pass the pre-bump gate: 7,035 Python tests, 492 FastAPI tests, and React build
- [x] Freeze and build one exact v0.24.0a1 wheel/sdist pair
- [x] Pass source-free installed-package UAT and bounded benchmark/hand-calculation replays; this is not an engineering check
- [x] Pass required hosted checks on the immutable candidate; the owner recorded the bounded independent software-review waiver
- [x] Obtain the separate owner decision for the tag, PyPI upload, and GitHub prerelease
- [x] Publish the unchanged wheel/sdist pair and digest-matched GitHub assets

This historical publication does not authorize rebuilding the same version,
publishing later `main`, a stable claim, professional approval, or engineering
use. `v0.23.1a2` remains a prior immutable Alpha recorded below.

## v0.23.1a2 Historical Release State

- [x] Owner authorizes preparation of v0.23.1a2 without tag or publication
- [x] Base the release lane on synchronized `main` at `970a78c1931a3aa0439f487e6892a888bb113962`
- [x] Run the canonical version preparation gate and update maintained release surfaces
- [x] Build and verify one exact v0.23.1a2 wheel from the frozen Python tree
- [x] Pass required PR checks, exact-head Weekly Verification, and independent candidate review
- [x] Record the refreshed exact review receipt after the repaired candidate passes hosted checks
- [x] Owner authorizes the v0.23.1a2 TestPyPI rehearsal, tag, production PyPI publication, and GitHub Release after exact CI evidence passes

The owner granted the target-specific authorization in the active Codex task on
2026-08-17. The exact Alpha was subsequently tagged and published. This
authorization remains bounded to that immutable artifact and does not grant
professional approval or authorize republishing the same version from later
source.

### v0.23.1a2 Local Candidate Evidence

- Evidence: [v0.23.1a2 local rehearsal](../verification/alpha-0231a2-local-prepublication-rehearsal.md)
- Build-anchor source: `a115b16efbb85db0459c79836f55b6c43a586470`
- Python tree: `25aa0468135c07d3c260eca43776fb451865f833`
- Wheel: 665,658 bytes, SHA-256 `34892d867845d044249236f32b700ab5e10ec558225407a47717fe3c3c2614bb`
- Installed verification: 5,553 passed, 51 skipped, 2 deselected; installed CLI workflows green
- Exact candidate UAT: 29/29 cases across 12/12 advertised commands
- State: historical local candidate evidence; the public CI-built artifact was
  subsequently published with the distinct hashes recorded above

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
