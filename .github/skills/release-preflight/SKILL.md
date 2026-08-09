---
name: release-preflight
description: "Prepare and verify a release candidate through the canonical release CLI: one preflight, one exact wheel build, one clean-install UAT, and explicit approval for publishing actions."
---

# Release Preflight

Use this only for an actual release candidate. The canonical automation owns resource checks, test/build selection, document/version checks, clean temporary environments, and cleanup. Do not copy those checks into shell snippets.

## When to Use

- Before creating or approving a release PR
- After packaging or public-entry-point changes when release readiness is requested
- Before publishing a version to PyPI

## Preconditions

- Run from the workspace root on the intended release branch.
- Know the exact target version in `X.Y.Z` form.
- Preserve unrelated work; preflight requires a clean working tree.
- The `PR Gate` for the release candidate must pass on its current commit.

## Release Candidate Flow

### 1. Preflight before version mutation

```bash
./run.sh release preflight <target-version>
```

This is read-only. Run it once. If local resource checks fail and Docker is the intended fallback, start Colima and run the Docker variant instead of running both full paths:

```bash
colima start --cpu 4 --memory 4
./run.sh release preflight <target-version> --docker
```

Repair failures by rerunning only their narrow command, then establish one final green preflight.

### 2. Prepare the release changes

`./run.sh release run <target-version>` changes version-controlled files and is owner-approved release work. Do not run it during a review-only task or without authorization to prepare the release.

After the version change, review the diff and complete the release notes required by the printed checklist. Commit through `./scripts/ai_commit.sh`; do not tag, merge, or publish yet.

### 3. Build one exact artifact

From the workspace root:

```bash
.venv/bin/python -m build Python
```

Confirm that `Python/dist/` contains the wheel for the exact target version. Do not verify an unversioned wildcard when several wheels exist.

### 4. Verify the installed artifact

```bash
./run.sh release verify --version <target-version> --source wheel
```

This creates and removes a unique temporary environment, installs the exact wheel, verifies the package, runs the installed-package checks, and exercises the CLI workflow. Do not create or delete a fixed `/tmp` directory manually.

After publication, verify the exact public version separately:

```bash
./run.sh release verify --version <target-version> --source pypi
```

### 5. Owner-only actions

Merging the release PR, creating/pushing a tag, publishing to PyPI, creating the GitHub release, and closing release issues require explicit user approval. A green preflight does not authorize any of them.

## Report Format

```
## Release Preflight: v{VERSION}

| Evidence | Status | Details |
|----------|--------|---------|
| Preflight | ✅/❌ | [command, commit] |
| Exact artifact | ✅/❌ | [wheel filename] |
| Clean-install UAT | ✅/❌ | [wheel/PyPI source] |
| PR Gate | ✅/❌ | [current commit] |

**Verdict:** READY / NOT READY
**Blockers:** [confirmed release-outcome failures only]
**Owner approval still required:** [merge/tag/publish actions]
```

## Integration

- **@ops** runs the release automation and preserves approval boundaries
- **@reviewer** checks that evidence belongs to the current release commit
- **@tester** runs the installed-artifact verification when requested
