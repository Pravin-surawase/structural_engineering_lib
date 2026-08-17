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

- Build-anchor head: `a115b16efbb85db0459c79836f55b6c43a586470`
- Build-anchor tree: `a1d8a3cb06127bf3914438de82624baf89ca896f`
- Python tree: `25aa0468135c07d3c260eca43776fb451865f833`
- Base: `970a78c1931a3aa0439f487e6892a888bb113962`
- Runtime diagnosis: `source_bound=true`

The evidence record and other final closeout documents are outside the Python
package tree. Their later addition does not change the Python tree or rebuild
the artifact.

## Exact artifacts

| Artifact | Bytes | Members | SHA-256 |
|---|---:|---:|---|
| `structural_lib_is456-0.23.1a2-py3-none-any.whl` | 665,658 | 239 | `34892d867845d044249236f32b700ab5e10ec558225407a47717fe3c3c2614bb` |
| `structural_lib_is456-0.23.1a2.tar.gz` | 551,207 | 271 | `2684aa80ab2d56ace0fe4bc7c3af2b5ebe8cd1a63bb4f87251a69410cf985297` |

Maintained build command:

```bash
./scripts/python_runtime.sh -m build Python
```

The earlier generated artifacts were inspected as ignored directories with no
symbolic links, moved recoverably out of the worktree, and replaced by one
cleanly built wheel and its matching sdist. Both generated paths are ignored
and the tracked worktree remained clean.

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

Owner authorization is recorded for TestPyPI, PyPI, and GitHub Releases,
conditional on the repaired exact candidate passing required PR checks,
exact-head Weekly Verification, independent exact-candidate review, and the
final exact-wheel publication preflight. The authorization does not include
professional approval.
