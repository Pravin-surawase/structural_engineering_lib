# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Synchronize the Mac primary checkout after the Windows Excel + ETABS
- Completed: Fetched GitHub and verified PRs #890–#893 were merged. The Mac repair branch; Switched the primary checkout to `main` and fast-forwarded it from; Added the canonical multi-device default: one active writer device per task
- Git receipt: docs/verification/multi-device-git-sync-guidance-git-handoff-receipt.json | sha256:28753b1a09ca22dc4f8d551980a72532c5ab7cc20bc7134e64e221418bc21a0e | HOLD
- Git identity: codex/multi-device-git-sync-guidance@c959775d9734e5eb26838de99aa722400cf7c276 | upstream=NONE@UNKNOWN | base=origin/main@c959775d9734e5eb26838de99aa722400cf7c276 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` is the immutable current normal software release at merge `e66de6efa3bb80d3ebc54e6151b1d6c29275c502`; GitHub prerelease is false and PyPI selects it normally. |
| **Current** | `ETABS-EXCEL-PILOT-W1` is a software-acceptance PASS on the exact copied, locked, already-analyzed Windows model. Direct FastAPI and installed Excel reconciled exactly for one beam and the bounded five-beam run after repairing the installed `GetAllFrames` COM binding and exact combination-name grammar. Model identity, lock, case status, present units, hash, size, and timestamp remained safe. The tracked receipt excludes proprietary model paths, force payloads, and workbook contents. |
| **Next** | Merge the W1 repair and safe receipt after required checks. Then define a separate reviewed scope before any section proposal, ETABS write-back, analysis rerun, global-response comparison, or bounded optimization; keep qualified structural-engineer review explicit before engineering use. |
| **Held** | Additional ETABS analysis, unlock/save, member-size write-back, iterative whole-model optimization, full frame-solver claims, serviceability/adjacency/congestion/site-practice automation, stable-API guarantee, professional or construction-use approval, release, protected-source mutation, and destructive cleanup. |

## Published release evidence

- Annotated tag `v0.24.0` peels to merge `e66de6ef...`, exact authorized tree
  `e583493e...`, and unchanged reviewed Python tree `d4f1af4f...`.
- Production workflow `33150227524` passed release validation, immutable build,
  clean exact-wheel UAT, SBOM, PyPI publication, and GitHub Release creation.
- Public wheel: 822,111 bytes, SHA-256 `7b5bc0b6...a093`; public sdist:
  685,836 bytes, SHA-256 `d530f10c...6640`. GitHub and PyPI hashes match.
- Exact-wheel UAT passed 29/29 cases across 28 advertised entries, including 15
  CLI and 13 family-facade entries. A fresh isolated PyPI install reported
  `0.24.0` from its own site-packages environment.

## Release logic and claim boundary

- Alpha releases are not selected by ordinary package resolution, which left
  normal users on a materially older version. A final `0.24.0` fixes that
  distribution problem without claiming that the entire roadmap is complete.
- “Normal release” means normal PyPI selection and a non-prerelease GitHub
  Release for the audited supported scope. The project remains pre-1.0/Beta,
  with supported-case limitations and no stable-API promise.
- No practicing-engineer review, professional approval, engineering-use
  approval, or construction-use approval is claimed. The owner continues to
  defer one cumulative practicing-engineer review until the intended integrated
  library is declared complete.

## Preservation rules

- Do not open or mutate the protected Windows evidence clone, Excel, ETABS,
  workbooks, models, older clones, system toolchains, or evidence datasets.
- Preserve every unrelated worktree, staged/dirty/untracked/ignored/stashed
  item, retained source, branch, ref, and archive. The detached dirty `e54a`
  lane remains untouched.
- Do not rebuild an existing public version, rewrite history, bypass checks,
  delete branches/worktrees/refs/data, or broaden the release claims.
- Do not start the deferred practicing-engineer review until the owner declares
  the intended integrated library complete and the cumulative dossier exists.

## Required Reading

1. [W1 installed Windows receipt](../verification/etabs-excel-python-pilot-w1-evidence.json)
2. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
3. [Public v0.24.0 receipt](../verification/release-0240-publication-receipt.json)
4. [Normal-release owner decision](../verification/release-0240-normal-software-owner-decision.json)
5. [Post-R0 cumulative audit](../verification/lib-pro-014-post-r0-cumulative-audit-evidence.json)
6. [Release checklist](pre-release-checklist.md)
7. [Release ledger](../getting-started/releases.md)
8. [Current task board](../TASKS.md)
