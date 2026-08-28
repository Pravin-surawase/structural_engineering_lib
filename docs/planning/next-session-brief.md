# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-28
- Focus: Prepare, verify, and publish exact v0.24.0 as the normal software release
- Completed: Selected v0.24.0; split normal distribution status from professional claims; prepared consistent metadata, policy, workflow support, and one exact local wheel/sdist pair
- Git receipt: docs/verification/release-0240-preparation-git-handoff-receipt.json | sha256:63eba2cf0529ce9a3b01651d0070f40ab7e6ef0b69205332ad65d9fb82b0e85c | HOLD
- Git identity: codex/release-0240-stable-software@e7956f78cc849f1c0cd26fed7c82e9f3cdce9e19 | upstream=origin/main@e7956f78cc849f1c0cd26fed7c82e9f3cdce9e19 | base=origin/main@e7956f78cc849f1c0cd26fed7c82e9f3cdce9e19 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0a1` remains the immutable public Alpha at `71b7065216d4266d63ad6b31bd39bba81fa16efc`. |
| **Current** | Accepted post-R0 audit PR #885 merged at `e7956f78cc849f1c0cd26fed7c82e9f3cdce9e19`, tree `7849482826f564023829bd9f9d71377654302dac`. The owner selected exact `v0.24.0` as the next normal software release. |
| **Next** | Freeze the tracked release preparation, run the clean exact-wheel preflight, push one PR, pass required hosted checks and exact-head Weekly Verification, bind the owner review waiver and exact publication authorization, merge unchanged, then tag/publish/verify. |
| **Held** | Stable-API guarantee, complete IS 456 coverage, professional approval, engineering-use/construction-use approval, Windows/Excel/ETABS acceptance, protected-source mutation, and destructive cleanup. |

## Prepared release evidence

- Normal PEP 440 final version: `0.24.0`; GitHub prerelease flag `false`;
  maturity classifier `Development Status :: 4 - Beta`.
- Local wheel: 822,111 bytes, SHA-256
  `64343a33f02ff1231dda5c2552bbee4cb58046d2f679c0b3c6178fd5239e40d1`.
- Local sdist: 688,176 bytes, SHA-256
  `32fb86a0a90a9cdcc3c00170c3dc32099fc7695cb0cc0cf220aae3bebb18322c`.
- Twine, clean installed import/version/CLI, 29/29 exact-wheel UAT cases, 28
  advertised entries, 15 CLI entries, 13 family-facade entries, both public
  examples, 152 focused release controls, and quick 10/10 pass.
- The first full gate found only the version-bound generated API classification
  projection. Its maintained generator refreshed the registry and compatibility
  ledger; the frozen tracked-state rerun passes 32/32 with 15 unaffected checks
  reused.

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

## Required Reading

1. [Normal-release owner decision](../verification/release-0240-normal-software-owner-decision.json)
2. [Local prepublication evidence](../verification/release-0240-local-prepublication-evidence.json)
3. [Post-R0 cumulative audit](../verification/lib-pro-014-post-r0-cumulative-audit-evidence.json)
4. [Release checklist](pre-release-checklist.md)
5. [Release ledger](../getting-started/releases.md)
6. [Current task board](../TASKS.md)
