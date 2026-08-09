# Pre-Release Checklist

**Type:** Reference
**Audience:** All Agents
**Status:** Review
**Importance:** High
**Created:** 2026-03-31
**Last Updated:** 2026-08-10

## Current State

Installed metadata version: 0.23.0

- **Branch:** `codex/release-v0.23.0`
- **Implementation PR:** #693 merged at `cc99e610`
- **Closeout PR:** draft #696; C3 artifact source commit `9be6eb35`
- **Release target:** v0.23.0 selected; publication paused by the owner before tag or upload
- **Publication state:** C0-C4 bounded software/evidence scope frozen; qualified review, exact CI artifact evidence and post-PyPI UAT pending

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
- [x] Wheel/sdist allowlist and exact-artifact UAT encoded in publish CI
- [x] Exact local wheel/sdist hashes, inventories, protected-content result and SBOM recorded
- [x] Exact local wheel clean-install tests and CLI UAT pass
- [ ] CI-built artifact manifest, hashes, inventories and SBOM reviewed
- [ ] Exact CI-built wheel UAT evidence reviewed
- [ ] Owner approves TestPyPI upload, if desired
- [ ] Owner re-authorizes the final tag and production PyPI publication

### Required Before 1.0

- [ ] Stable API guarantee for every advertised supported route
- [ ] Professional validation by licensed structural engineer
- [ ] Performance benchmarks published
- [ ] Security audit complete (OWASP compliance)
- [ ] User documentation complete with worked examples
- [ ] PyPI stable release published
- [ ] Docker production image optimized
