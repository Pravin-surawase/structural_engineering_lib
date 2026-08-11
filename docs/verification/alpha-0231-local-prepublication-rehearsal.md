# v0.23.1a1 Local Prepublication Rehearsal

**Status:** LOCAL PREPUBLICATION REHEARSAL

**Authority:** Local evidence only; not a CI artifact identity, tag, or publication approval

**Artifact source:** `72d2d9b8ccc1350b46499dc5a5d08df6284fe10f`

## Preserved artifacts

| Artifact | Bytes | Members | SHA-256 |
|---|---:|---:|---|
| `structural_lib_is456-0.23.1a1-py3-none-any.whl` | 529,982 | 195 | `9c986920ceb43e341d01c6411c873605fec3321486d862a847e2083c36156aa7` |
| `structural_lib_is456-0.23.1a1.tar.gz` | 439,405 | 220 | `9f7ebf55afa8232eeeb3f35449450a4bc8aca5d835c9f017f308052c979f1de6` |

The artifacts were not rebuilt during verifier repair. The wheel/sdist allowlist
check found no excluded research, migration-fixture, alternate-code, test,
example, script, or documentation content. Packaged `clauses.json` records both
protected-standard-text and protected-table-values flags as `false`.

## Bound receipts

| Receipt | Identity | SHA-256 |
|---|---|---|
| Public distribution | `IS456-PUBLIC-DISTRIBUTION-001` | `539ba5deb682367a3f9069186a9b34d22a53ab9c1707eb9f2f0f8d054e270660` |
| Footing inclusion | `FOOT-ISO-RC-V1-RELEASE-INCLUSION`, source `886871ae` | `e15f6ebeb79030d822e6dd5979d5fe2fd41aca2aa1c3fa685c61e1203dfc7029` |

## Installed-wheel evidence

- Maintained command: `./run.sh release verify --version 0.23.1a1 --source wheel`
- Dependency boundary: unchanged wheel with `[dev,validation]` plus
  `httpx>=0.27`; no root `requirements.txt` installation.
- Import boundary: `structural_lib.__file__` was asserted inside the disposable
  venv `site-packages` before and after pytest.
- Test result: 5,055 passed, 51 skipped, 2 deselected, 29 warnings.
- Installed CLI: `job`, `critical`, and HTML `report` workflows passed.
- Local reproducible CycloneDX 1.6 environment SBOM: 195 components, 239,491
  bytes, SHA-256
  `82c7560a8a0137cf8989e594ab5c9668fd88f3699b03fcea460a738f2b6856a1`.

## Authority boundary

The local SBOM and archive identities support review of this rehearsal only.
The current manual `publish.yml` path proceeds to TestPyPI and was not
dispatched. Any future authorized publication must produce and review its own
CI manifest, inventories, SBOM, hashes, and installed-artifact UAT. No tag,
TestPyPI/PyPI upload, GitHub Release, Pages activation, or engineering-use
approval is claimed here.
