# Release Artifact Evidence Template

**Type:** Reference
**Audience:** Developers
**Status:** Review
**Importance:** Critical
**Created:** 2026-08-09
**Last Updated:** 2026-08-11

Complete this record from the CI run that built the exact candidate.

| Field | Value |
|---|---|
| Version | `<owner-approved-version>` |
| Source commit SHA | `<40-hex-sha>` |
| Source ref/tag | `<ref>` |
| GitHub Actions run | `<url>` |
| Wheel filename | `<filename.whl>` |
| Wheel SHA-256 | `<sha256>` |
| Wheel size | `<bytes>` |
| Sdist filename | `<filename.tar.gz>` |
| Sdist SHA-256 | `<sha256>` |
| Sdist size | `<bytes>` |
| Content allowlist | `PASS/HOLD` |
| Protected-content gate | `PASS/HOLD` |
| Public-distribution permission record | `record ID and SHA-256` |
| Public-distribution permission gate | `PASS/HOLD` |
| Footing release-inclusion record | `record ID, source head and SHA-256` |
| Footing release-inclusion gate | `PASS/HOLD` |
| Exact-wheel installed UAT | `PASS/HOLD` |
| CLI UAT | `PASS/HOLD` |
| SBOM | `<artifact path and SHA-256>` |
| TestPyPI decision | `<owner decision>` |
| Production decision | `<owner decision>` |

Attach the CI-generated `artifact-manifest.json`, both inventories and SBOM.
Never substitute locally rebuilt artifacts after evidence capture.
