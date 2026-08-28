# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-28
- Focus: Repair the Windows-blocking ETABS COM result-container mismatch and
- Completed: The common ETABS COM decoder now accepts only the two observed outer result; The existing connection and full beam-pilot tests now run against both outer
- Git receipt: docs/verification/etabs-com-list-compat-git-handoff-receipt.json | sha256:a84a498879cbc8d9dc512b1b80d42e8ca19d91ca8659e3928f03c1284ca17fda | HOLD
- Git identity: codex/etabs-com-list-compat@d6e83cfd53d444b11637bb0e85f5b314a92333cc | upstream=origin/main@d6e83cfd53d444b11637bb0e85f5b314a92333cc | base=origin/main@d6e83cfd53d444b11637bb0e85f5b314a92333cc | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` is the immutable current normal software release at merge `e66de6efa3bb80d3ebc54e6151b1d6c29275c502`; GitHub prerelease is false and PyPI selects it normally. |
| **Current** | The exact copied Windows model has current locked analysis results. W1 reached `/connect` and exposed a tuple-only COM decoder defect; `codex/etabs-com-list-compat` contains the bounded repair with tuple/list connection and full-pilot regressions. This remains an unpublished repair candidate, not completed installed-Windows acceptance or a release. |
| **Next** | Freeze and publish the repair candidate, require its hosted checks, then deploy that exact commit to the existing Windows evidence lane. Reuse the analyzed copied model and run `/connect`, one-beam `/beam-pilot`, Excel, and bounded five-beam evidence without rerunning analysis. |
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

1. [Public v0.24.0 receipt](../verification/release-0240-publication-receipt.json)
2. [Normal-release owner decision](../verification/release-0240-normal-software-owner-decision.json)
3. [Post-R0 cumulative audit](../verification/lib-pro-014-post-r0-cumulative-audit-evidence.json)
4. [Release checklist](pre-release-checklist.md)
5. [Release ledger](../getting-started/releases.md)
6. [Current task board](../TASKS.md)
