# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-28
- Focus: Add and document a bounded Windows Office.js -> localhost FastAPI/
- Completed: Added the optional `structural-lib-is456[etabs]` dependency extra and a; Added typed status, connect, and beam-pilot REST operations. The pilot selects; Extended the existing macro-free Office.js pane with an ETABS surface that is
- Git receipt: docs/verification/excel-etabs-python-bridge-pilot-git-handoff-receipt.json | sha256:404a1248fb9c2f13fd61f46f3e98f8a0ddfd06593770c1fac9645e082f2e7756 | HOLD
- Git identity: codex/excel-etabs-python-bridge-pilot@683760a4aef1c384aa475df6842c791eada85959 | upstream=NONE@UNKNOWN | base=origin/main@683760a4aef1c384aa475df6842c791eada85959 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` is the immutable current normal software release at merge `e66de6efa3bb80d3ebc54e6151b1d6c29275c502`; GitHub prerelease is false and PyPI selects it normally. |
| **Current** | `codex/excel-etabs-python-bridge-pilot` contains the locally verified read-only Office.js -> FastAPI/Python -> already-open ETABS beam pilot. Broad Python/FastAPI/Office.js tests and the 32/32 repository gate pass; this is not yet installed Windows ETABS evidence or a release. |
| **Next** | Run the documented exact-current installed Windows Excel + ETABS acceptance against a saved copied model, reconcile at least one beam's station forces/design independently, and record unit restoration. Do not start ETABS write-back or optimization before that gate passes. |
| **Held** | ETABS analysis execution, unlock/save, member-size write-back, iterative whole-model optimization, full frame-solver claims, serviceability/adjacency/congestion/site-practice automation, stable-API guarantee, professional or construction-use approval, release, protected-source mutation, and destructive cleanup. |

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

1. [Public v0.24.0 receipt](../verification/release-0240-publication-receipt.json)
2. [Normal-release owner decision](../verification/release-0240-normal-software-owner-decision.json)
3. [Post-R0 cumulative audit](../verification/lib-pro-014-post-r0-cumulative-audit-evidence.json)
4. [Release checklist](pre-release-checklist.md)
5. [Release ledger](../getting-started/releases.md)
6. [Current task board](../TASKS.md)
