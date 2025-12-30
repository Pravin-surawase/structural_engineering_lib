# Session Issues and Fixes

Purpose: capture recurring friction points and the fixes so we do not repeat them.

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
- **Main Branch Guard failed** with `Direct commit to main detected (SHA...)` even though changes came from a PR.

### Cause
- The merge created a **local squash commit on `main`** that was **not associated with a PR** in GitHub’s API. The guard checks `listPullRequestsAssociatedWithCommit`, and this commit had no PR link.

### Fix Applied
- **Revert the commit via a PR**, then **re-apply the changes through a fresh PR merge** (server-side) so the new commit is associated with a PR.

### Prevention
- **Never create commits on `main` locally.** Use `gh pr merge` or the GitHub UI to merge PRs so the merge commit is created server-side and linked to the PR.
