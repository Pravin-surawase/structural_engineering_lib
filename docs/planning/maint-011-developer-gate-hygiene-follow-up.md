---
owner: Main Agent
status: draft
last_updated: 2026-08-22
doc_type: spec
complexity: advanced
tags: [maintenance, pre-commit, ci, tooling, git, developer-experience]
---

# MAINT-011 Developer Gate Hygiene Follow-up

## Purpose

Preserve the tooling and process defects encountered during `LIB-PRO-005` for
one separate maintenance session. None of these items changes the safety
packet's runtime result, and none should be repaired opportunistically in that
candidate.

## Confirmed issue register

| ID | Symptom and impact | Confirmed root cause | Evidence | Required next-session outcome |
|---|---|---|---|---|
| M11-01 | `pre-commit run --all-files` changed 1,738 files outside the task, mostly vendored ETABS HTML, legacy archives, and frozen golden fixtures. This makes an ordinary safety commit look like a repository-wide rewrite. | `end-of-file-fixer` and `trailing-whitespace` exclude only `VBA/` and `Excel/`; the documented all-file command therefore normalizes historical/vendor content that the active gates otherwise accept. | The hook changed the dirty-path count from 60 intended paths to 1,798. Reversing only the generated out-of-scope patch restored exactly 60 task paths. | Decide and encode explicit preservation exclusions, or perform a separately reviewed one-time normalization. Prove all-file mode is read-only on an unchanged checkout and never rewrites vendored/frozen evidence silently. |
| M11-02 | The all-file `check-json` hook fails on `react_app/tsconfig.app.json` and `react_app/tsconfig.node.json`, so the repository's own documented manual command cannot pass on current `main`. | Both TypeScript configs use JSON-with-comments/trailing-comma syntax, while the generic hook treats every `.json` file as strict JSON. | `check-json` reports decode errors at the existing commented/trailing-comma locations. | Exclude the deliberate JSONC files or convert/rename them through an impact-reviewed React configuration change. Add a regression proving strict project JSON is still checked. |
| M11-03 | All-file Bandit fails on three core findings and five FastAPI example/test findings even though the cumulative repository gate is green. This makes the advertised hook command non-decisive. | Bandit scans the complete matching trees in all-file mode without a maintained baseline or path/severity disposition; the findings predate this packet and include research fallback loops plus example/test code. | Core: three `B112` low-severity findings. FastAPI: two `B113` medium/low-confidence findings and three `B110` low-severity findings. | Review each finding, repair outcome-changing production behavior, and explicitly scope or baseline non-production examples/tests without weakening security coverage. Prove the chosen all-file command exits zero on unchanged `main`. |
| M11-04 | The hook's mypy phase found an in-scope BOQ type error only after the broad product/repository suites had passed. | The new resolver reused `fck` as an integer mapping key and later as an `object` iterable item; mypy retained the first loop variable's inferred type. | `boq.py:111` reported incompatible assignment. Renaming and narrowing `required_fck` corrects the ownership boundary without changing behavior. | Keep mypy in the staged commit path and add a small contributor note that loop-variable reuse across differently typed iterables is rejected. |
| M11-05 | Active instructions say the full gate has 30 checks, while the live gate runs 31. | A new enforced check was added without synchronizing `AGENTS.md` and `docs/guidelines/ai-token-efficiency.md`. | `./run.sh check` printed `31/31`; the two active documents still contain “currently 30 checks.” | Update count-bearing active instructions through the maintained synchronizer or remove brittle hard-coded counts where the live command is authoritative. |
| M11-06 | Several safe inspection attempts failed because command names/options were inferred from old patterns: `check_tasks.py`, active `generate_folder_index.py`, and `sync_numbers.py --check`. | The maintained commands are `check_tasks_format.py`, `generate_enhanced_index.py`, and the synchronizer's default read-only mode; archived tools and inconsistent CLI conventions make guessing easy. | Exact-path reruns passed. The global documentation index also required a separate explicit `--write` before the parent index refresh. | Improve `./run.sh find` discoverability and command help, add aliases only where ambiguity is safe, and document the leaf-to-parent/global index refresh sequence in one current location. |
| M11-07 | A fresh linked worktree could not run React/Vitest until dependencies were installed locally. | Ignored `node_modules` is worktree-local, and ESM resolves Vite relative to the worktree even when a binary exists elsewhere. | Exact-lockfile `npm ci` restored the 17/17 React hook run; pinned Node 24 was used. | Add a read-only dependency-readiness probe that gives one exact remediation command before tests begin; do not copy dependency trees between worktrees. |
| M11-08 | zsh aborted unmatched globs, executed unescaped backticks in inspection text, and interpreted an unquoted wheel `[pmm]` extra as shell syntax. | Interactive zsh glob/command-substitution rules differ from literal argument intent. | Exact paths and safely quoted literals resolved inspections; quoting the complete wheel requirement made the clean PMM-extra install pass with NumPy 2.4.6. | Add shell-safe examples for globs, literal backticks, and wheel extras to the terminal guidance; prefer discovered exact paths over speculative globs. |
| M11-09 | Compact audit output initially made a real documentation failure look like the permitted 405-file soft-budget warning. | The readiness aggregator retained the tail of combined checker output, so the decisive invalid-frontmatter message was outside the compact excerpt. | Running the documentation checker directly exposed invalid `doc_type: plan`; changing it to allowed `spec` made readiness 22/23 with only the expected input warning. | Make aggregated failure summaries retain the first decisive error and the final context, with a regression containing both a hard failure and a later warning. |
| M11-10 | A pre-commit handoff receipt is expected to become stale during a long verification/hosted-CI session and cannot serve as final merge evidence. | The Git contract intentionally separates the time-bound dirty-tree transition receipt from the post-merge exact-tree observation. | The workflow single source says never rewrite a historical transition receipt merely to make it current. | Ensure session closeout clearly accepts the historical transition artifact and records final PR/check/tree facts in a successor external closeout observation, without mutating the reviewed candidate. |
| M11-11 | Excel CI can show a skipped path-specific job even when the required PR Gate is green, which can be misread as missing validation. | Excel path classification is intentionally selective; local Excel tests and the required aggregate gate own different evidence. | `LIB-PRO-005` local Excel suite is 21/21; no Excel implementation path changed. | Document path-filtered skip semantics next to the required-check contract and preserve the local-suite requirement for cross-product safety packets. |
| M11-12 | The standalone performance comment/baseline workflow is parked, while FastAPI load tests already enforce runtime thresholds. The audit wording made this sound like no performance thresholds existed. | Performance evidence is split between intentionally parked workflow automation and executable test assertions. | Current FastAPI load tests pass; no flaky microbenchmark PR gate was added. | Reword the readiness item to distinguish “parked standalone reporting” from “executable threshold tests,” and identify the exact authority for each. |

## Constraints for the maintenance session

- Start from the then-current clean `main` in a new `codex/maint-011-*` lane.
- Do not combine hook normalization with safety, formula, release, ETABS, or
  Excel feature work.
- Preserve vendored ETABS content and frozen fixtures unless a dedicated byte
  review explicitly approves normalization.
- Do not silence Bandit or JSON validation broadly just to obtain green output;
  keep production/security coverage decisive.
- Test both normal staged-file hooks and the documented all-file command in a
  disposable clean worktree.
- Update active instructions/counts only after the final live command inventory
  is known.

## Exit criteria

1. A clean checkout remains byte-clean after the documented all-file hook run.
2. Normal staged hooks and all-file hooks both exit zero without bypass flags.
3. JSONC, Bandit, vendor/frozen-file, and index behaviors have explicit tests or
   machine-checked exclusions.
4. `./run.sh check --quick`, the live full gate, and required hosted checks pass.
5. The session log records each retained/changed disposition and exact evidence.
