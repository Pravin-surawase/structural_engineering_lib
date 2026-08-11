# Pre-Release Checklist

**Type:** Reference
**Audience:** All Agents
**Status:** Review
**Importance:** High
**Created:** 2026-03-31
**Last Updated:** 2026-08-11

## Current State

Installed metadata version: 0.23.1a1

- **Release source:** tag `v0.23.0` at `3f880d5bbc338baefc4aec8ed472cafe840a5c99`
- **Implementation PR:** #693 merged at `cc99e610`
- **Closeout PR:** #696 merged at `71e74a7e`; CI portability fix #697 merged at `3f880d5b`
- **Release target:** v0.23.0 Alpha, published 2026-08-10 local time
- **Publication state:** PyPI and GitHub prerelease published; exact public-version UAT green
- **Review policy:** qualified structural-engineering review is required before stable/engineering-use approval, not before this Alpha release

## Next Alpha Readiness Checklist

- [ ] Integrate the complete `FOOT-ISO-RC-V1` source head `886871ae` (or an explicitly reviewed successor) into the release branch
- [ ] Pass `./run.sh release footing-inclusion-check` with exact footing-owned files and Python/FastAPI/React integration markers present
- [ ] Verify the clean built wheel imports the concentric isolated-footing service; retain the inclusion receipt hash in the CI artifact manifest

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
