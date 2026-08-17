# v0.23.1a2 Local Prepublication Rehearsal

**Type:** Reference
**Audience:** Maintainers
**Status:** Complete
**Importance:** Critical
**Created:** 2026-08-17
**Last Updated:** 2026-08-17

**Evidence boundary:** Local prepared-candidate evidence only. This is not a PR
check receipt, exact-head Weekly Verification, independent review, target
authorization, tag, upload, GitHub Release, or professional approval.

## Source identity

- Build-anchor head: `c71e4e27749a9da58fe0d689bc1a1ba8b396f14d`
- Build-anchor tree: `f0b1730c8880147b1019d5df90a64a530475fdcb`
- Python tree: `501fac1360f06ff2be4f6aea3b5e167f956ce840`
- Base: `970a78c1931a3aa0439f487e6892a888bb113962`
- Runtime diagnosis: `source_bound=true`

The evidence record and other final closeout documents are outside the Python
package tree. Their later addition does not change the Python tree or rebuild
the artifact.

## Exact artifacts

| Artifact | Bytes | Members | SHA-256 |
|---|---:|---:|---|
| `structural_lib_is456-0.23.1a2-py3-none-any.whl` | 665,658 | 239 | `5bca57ba12a35803715ad581420fa6ea5be32a0cd736fd42246b9a026584cc19` |
| `structural_lib_is456-0.23.1a2.tar.gz` | 551,149 | 271 | `5e25b42d8a78f14b5ce915d1ef26d0680257336c7da07033b5afe8ef74a9a479` |

Maintained build command:

```bash
./scripts/python_runtime.sh -m build Python
```

No earlier artifact or generated build directory existed in this fresh
worktree. The command built one wheel and its matching sdist. Both generated
paths are ignored and the tracked worktree remained clean.

## Installed-wheel verification

Maintained command:

```bash
./run.sh release verify --version 0.23.1a2 --source wheel
```

- The disposable Python 3.11 environment imported
  `structural_lib==0.23.1a2` from its own `site-packages` before and after the
  test run, never from the checkout.
- Dependency boundary: wheel `[dev,validation]` extras plus the documented
  generated-client requirement `httpx>=0.27`; no root requirements install.
- Result: 5,553 passed, 51 skipped, 2 deselected, 29 warnings.
- Installed `job`, `critical`, and HTML `report` workflows passed.

## Exact candidate and advertised-command UAT

Maintained command:

```bash
./run.sh release candidate-check --version 0.23.1a2 \
  --wheel Python/dist/structural_lib_is456-0.23.1a2-py3-none-any.whl
```

- Candidate check passed the bounded public-distribution and complete isolated-
  footing inclusion controls, source/release version surfaces, wheel filename,
  wheel metadata, excluded-content check, clean install, package origin,
  installed `structural_lib --help`, public examples, and installed release
  UAT.
- Release matrix: 29 cases; SHA-256
  `dd52015061a443e16f93bb5828016b5e96a580e3e0ebe4516e31a29db88c7757`.
- Advertised entry-point inventory: 12 commands; SHA-256
  `29e8cb68cbdbfae98bd0a2fec035ad0e291581dccdabf3c35f05399f78cbcbd1`.
- The candidate check reported the same wheel SHA-256 recorded above.

## Bound standing controls

| Record | Identity | SHA-256 |
|---|---|---|
| Public distribution | `IS456-PUBLIC-DISTRIBUTION-001` | `539ba5deb682367a3f9069186a9b34d22a53ab9c1707eb9f2f0f8d054e270660` |
| Footing inclusion | `FOOT-ISO-RC-V1-RELEASE-INCLUSION` | `875437cf59a078e1b170f636484a230efd1031f140f2bec5c4eee1df17e89a48` |

## Verdict and remaining holds

**Local verdict:** `CANDIDATE_TECHNICALLY_READY`

**Publication state:** `HOLD`

Remaining gates are the final candidate commit, required PR checks, exact-head
Weekly Verification, independent exact-candidate review, a version-specific
review receipt, and separate owner authorization for each requested target.
The final exact-wheel publication preflight is reserved for that reviewed and
authorized identity so its target verdict is not duplicated or misleading.
