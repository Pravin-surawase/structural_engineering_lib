# Session Issues and Fixes

Purpose: capture recurring friction points and the fixes so we do not repeat them.

---

## 🔍 Mistake Review (Run at Session Start)

**Run `./scripts/agent_mistakes_report.sh` at the start of each session** to see:
- Pre-commit failures (files changed by hooks after staging)
- Missing commit messages (empty or placeholder messages)
- Policy blocks (manual git blocked by hooks)

**What to do with this data:**
1. **High pre-commit failures?** → Run `black` and `ruff` before committing
2. **Policy blocks?** → You or another agent tried manual git - always use `ai_commit.sh`
3. **Missing messages?** → Write meaningful commit messages describing the change

**Automatic logging (OPS-01):**
- Git hooks now log all blocked manual git attempts to `logs/git_workflow.log`
- The `agent_mistakes_report.sh` script parses these logs
- Review patterns weekly to identify training/documentation gaps

---

## 2025-12-29 (v0.11.0 release)

### Issues Seen
- **Release script rewrote doc stamps** and introduced trailing whitespace in “Last Updated” lines, which caused pre-commit hooks to fail.
- **`gh pr checks --watch` timed out** on the first attempt (10s default), even though checks were still running.
- **Dependabot PR was behind `main`** and could not be merged until the branch was updated.
- **PyPI verification used an already-installed venv**, so it did not prove new-package availability.

### Fixes Applied
- **Doc stamp formatting:** switch “Last Updated” lines to `...<br>` instead of trailing spaces; update `scripts/bump_version.py` to output `<br>` (no whitespace).
- **Checks timeout:** re-run `gh pr checks <num> --watch` with a longer timeout when needed.
- **Update-behind PRs:** run `gh pr update-branch <num>` then re-check CI before merging.
- **Clean-venv verify:** use a fresh venv for `pip install structural-lib-is456==X.Y.Z`.

### Process Notes
- After running `scripts/release.py`, always check `git status -sb` and review diffs.
- Do not tag or push tags unless the working tree is clean.

---

## 2025-12-30 (Main Branch Guard)

### Issue Seen
- **Main Branch Guard failed** with `Direct commit to main detected (SHA...)` even though changes came from properly merged PRs.

### Cause (Corrected 2025-12-31)
- **GitHub API eventual consistency**: The `listPullRequestsAssociatedWithCommit` API sometimes returns an empty array immediately after a PR merge, then populates the association seconds/minutes later.
- This is a **race condition**, not a local commit issue. All failed commits (e.g., #220, #223, #224, #227) were proper PR merges.
- Verification: `gh api repos/.../commits/<SHA>/pulls` now returns the correct PR for all failed commits.

### Fix Applied
- Updated `.github/workflows/main-branch-guard.yml` to add a **commit message fallback**: if the API returns no PRs, check the commit message for `(#NNN)` pattern (which GitHub adds to all PR merge commits).

### Prevention
- The workflow now handles API delays gracefully.
- No workflow behavior change needed from users—PRs merged via `gh pr merge` or GitHub UI will pass.
