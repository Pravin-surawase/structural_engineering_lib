# Git & GitHub Governance Guide

**Status:** Active
**Owner:** DEVOPS Agent
**Purpose:** Define strict, professional standards for version control, branching, and repository management to ensure long-term maintainability and collaboration.

---

## 1. Repository Philosophy

We treat this repository as a **professional open-source product**, not a personal scratchpad.
*   **Source of Truth:** The code in the repo is the truth. Excel files (`.xlsm`) are *artifacts* generated from the code, not the source itself.
*   **Clean History:** We value a linear, readable commit history.
*   **Traceability:** Every change must link to a Task or Issue.

---

## 2. Branching Strategy (Trunk-Based Development)

We use a simplified **Trunk-Based Development** model suitable for a small, high-velocity team (Human + AI Agents).

### 2.1 Branches
*   **`main` (Protected):**
    *   The "Golden Master". Always deployable.
    *   Contains only tested, verified code.
*   **Rule:** No direct commits to `main`.
        * If you need to change docs, use a PR like everything else.
        * Release tags are created on the merge commit.
*   **`feat/task-ID-description`:**
    *   Feature branches for specific tasks.
    *   Naming convention: `feat/task-017-etabs-import`, `fix/task-012-shear-bug`.
    *   **Lifespan:** Short (1-2 sessions max). Merge back to `main` quickly.

### 2.2 Workflow
1.  **Start:** `git checkout -b feat/task-018-schedule`
2.  **Work:** Edit files, run tests.
3.  **Commit:** Frequent, atomic commits.
4.  **Verify:** Run full test suite.
5.  **Merge:** Squash and Merge into `main` (or Rebase and Merge).
6.  **Delete:** Delete the feature branch.

### 2.3 Branch Protection Baseline (GitHub Settings)

This repo prefers **low-maintenance security**: enforce safety at the repo-settings layer instead of complex workflow tricks.

Recommended protection rule for `main`:
* Require a pull request before merging
* Require status checks to pass before merging
    * Prefer "Require branches to be up to date" (prevents merging stale PRs)
* Do not allow force pushes
* Do not allow deletions

Solo default:
* Leave "Include administrators" OFF to keep an emergency escape hatch
* Skip "Restrict who can push" and "Require reviews" unless collaborating

Supply-chain stance:
* Avoid high-maintenance hardening (e.g., pinning every GitHub Action to a commit SHA) unless there is a clear need.

---

## 3. Commit Message Convention (Conventional Commits)

We follow [Conventional Commits](https://www.conventionalcommits.org/) to enable automated changelogs.

**Format:** `<type>(<scope>): <description>`

### Types
*   **`feat`**: A new feature (corresponds to `MINOR` in SemVer).
*   **`fix`**: A bug fix (corresponds to `PATCH` in SemVer).
*   **`docs`**: Documentation only changes.
*   **`style`**: Formatting, missing semi-colons, etc; no code change.
*   **`refactor`**: A code change that neither fixes a bug nor adds a feature.
*   **`test`**: Adding missing tests or correcting existing tests.
*   **`chore`**: Build process, auxiliary tools, library upgrades.

### Examples
*   `feat(core): implement doubly reinforced beam logic`
*   `fix(shear): correct tau_c interpolation for M40`
*   `docs(readme): update installation instructions`
*   `test(integration): add regression snapshot for B1`

---

## 4. Versioning (SemVer)

We follow **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

*   **MAJOR (v1.0.0):** Breaking changes (e.g., changing function signatures in `M08_API`).
*   **MINOR (v0.5.0):** New features in a backward-compatible manner (e.g., adding Schedule generation).
*   **PATCH (v0.5.1):** Backward-compatible bug fixes.

**Release Process:**
1.  PM approval for version bump (no auto-bumps).
2.  Append to `docs/RELEASES.md` (immutable ledger; never edit past entries).
3.  Update `CHANGELOG.md` (append-only).
4.  Tag the commit: `git tag -a v0.5.0 -m "Release v0.5.0"`
5.  Push tag: `git push origin v0.5.0`

---

## 5. Excel & VBA Specifics

Git handles text well, but hates binary files (`.xlsm`, `.xlam`).

### 5.1 The "Export Rule"
*   **NEVER** rely on the code inside `.xlsm` as the backup.
*   **ALWAYS** export VBA modules to `.bas` / `.cls` files in `VBA/Modules/` before committing.
*   **Why?** You cannot diff a binary Excel file. You *can* diff a `.bas` file.

### 5.2 Binary File Management
*   Treat `.xlsm` files as **binary artifacts**.
*   Commit them only when the structure changes (e.g., new sheets, named ranges).
*   Do not commit them for simple code changes (since the code lives in `VBA/Modules`).
*   `.xlam` outputs live under `VBA/Build/` (whitelisted); other add-ins stay ignored.

---

## 6. Documentation Standards

*   **README.md:** The landing page. Must answer "What is this?", "How do I install it?", "How do I use it?".
*   **CHANGELOG.md:** User-facing history of changes.
*   **docs/**: Technical documentation.
    *   Keep it close to the code.
    *   Update docs *in the same PR* as the code change.

---

## 7. UI/UX Guidelines (for GitHub)

*   **Issues:** Use Issues to track Tasks (`TASK-001`). Label them (`enhancement`, `bug`, `documentation`).
*   **Pull Requests:**
    *   Title: Matches the commit message convention.
    *   Description: Reference the Task ID. Explain *what* changed and *why*.
    *   Screenshots: Mandatory for UI changes (Excel sheets).

---

## 8. Emergency Recovery

If `main` breaks:
1.  **Revert:** `git revert <bad-commit-hash>`
2.  **Fix:** Create a `fix/` branch, repair, test, and merge.
3.  **Post-Mortem:** Document what happened in `logs/` to prevent recurrence.

---

## 9. Pre-Merge Checklist (Agents)

- **Link to Task:** Every PR references a TASK ID and the agent role (DEV/TESTER/etc.).
- **Tests:** Run `python3 -m pytest Python/tests -q`; for Excel, run the integration harness or note “not run” with reason.
- **Docs:** Update relevant docs (README/API_REFERENCE/CHANGELOG/RELEASES/TASKS) in the same PR.
- **Artifacts:** Do not commit `.xlsm`/`.xlam` unless structure changed; export `.bas`/`.cls` instead.
- **Diff sanity:** Ensure no generated or local config files are included.
- **Branch hygiene:** Keep feature branches short-lived; rebase on `main` before merge if needed.

---

## 10. Release Governance (PM Rules)

- `docs/RELEASES.md` is append-only and is the ledger of truth. Past entries are immutable.
- Version bumps require explicit PM approval and a tag.
- If `CHANGELOG.md` and `RELEASES.md` conflict, `RELEASES.md` wins.
- Keep `main` deployable; if a release fails validation, revert instead of force-pushing.
