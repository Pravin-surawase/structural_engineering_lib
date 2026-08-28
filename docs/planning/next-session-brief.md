# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-28
- Focus: Apply the external-user review of the published
- Completed: Kept the typed family facade as the recommended integration route and added; Documented the `beam_id` versus `case_id` distinction, standardized current; Corrected stale Alpha-era labels, clarified that FastAPI/React are exact-head
- Git receipt: docs/verification/external-docs-polish-git-handoff-receipt.json | sha256:b67b11a97c962c477ed768e89d4351b60cc87c032e309b007aeb394fb4308358 | HOLD
- Git identity: codex/external-docs-polish@bda7dec0dc65f96ba8fada55960e3682cd3b80cb | upstream=origin/main@bda7dec0dc65f96ba8fada55960e3682cd3b80cb | base=origin/main@bda7dec0dc65f96ba8fada55960e3682cd3b80cb | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` is the immutable current normal software release at merge `e66de6efa3bb80d3ebc54e6151b1d6c29275c502`; GitHub prerelease is false and PyPI selects it normally. |
| **Current** | Release publication and public identity verification are complete. The package remains pre-1.0/Beta and the supported-scope limitations remain authoritative. |
| **Next** | No later release or engineering packet is selected. Wait for the repository owner to choose the next bounded scope; do not infer a v0.24.1/v0.25 candidate. |
| **Held** | Stable-API guarantee, complete IS 456 coverage, professional approval, engineering-use/construction-use approval, Windows/Excel/ETABS acceptance, protected-source mutation, and destructive cleanup. |

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
