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
- Know the exact target version in PEP 440 `X.Y.ZaN` form for Alpha releases (or the exact stable `X.Y.Z` form for stable releases).
- Preserve unrelated work; preflight requires a clean working tree.
- The `PR Gate` for the release candidate must pass on its current commit.
- The maintained preflight runs Python, FastAPI, and React gates. Do not replace
  it with a Python-only result or assume local success covers FastAPI CI.

## Release Candidate Flow

### 1. Select the preflight mode

Before version mutation, validate that the proposed version is a real upgrade:

```bash
./run.sh release preflight <target-version>
```

If the source tree is already bumped to the frozen target version, do not pass
that equal version as the positional argument; it is defined as the *next*
version and will correctly fail the upgrade check. Build the exact artifact in
step 3, then establish the final green current-candidate preflight with:

```bash
./run.sh release preflight --wheel <exact-wheel-path>
```

A prepared candidate must retain explicit unpublished/on-hold CHANGELOG,
release-ledger, and CITATION wording. Do not pre-check tag or publication
authorization in `docs/planning/pre-release-checklist.md` before the immutable
review. Run the exact PR and Weekly checks once on that frozen candidate.

After review, make one bounded publication packet containing all final release
state together: the dated `CITATION.cff`, dated `CHANGELOG.md`, one appended
authorized entry in `docs/getting-started/releases.md`, and the maintained
authorization JSON. These are the only publication-metadata paths accepted after
the reviewed candidate; the Python tree must remain identical. Before committing
the packet, run:

```bash
./run.sh release publication-surface-check --version <target-version>
```

After the clean commit, run `authorization-check` for each requested target.
That command revalidates the same final metadata before any publication workflow
can spend time on release tests. Do not rerun Weekly verification for this
bounded metadata packet. Any other post-review path change invalidates the exact
candidate and requires a new review/hosted decision.

This is read-only. Run it once. If local resource checks fail and Docker is the intended fallback, start Colima and run the Docker variant instead of running both full paths:

```bash
colima start --cpu 4 --memory 4
./run.sh release preflight <target-version> --docker
```

Repair failures by rerunning only their narrow command, then establish one
final green preflight. Do not run both the pre-bump and current-candidate forms
for an already-bumped branch.

When recording local evidence, use a governance-safe filename such as
`alpha-0231-local-prepublication-rehearsal.md`. Do not place dotted package
versions in documentation filenames. Run metadata validation through the
consolidated command found by `./run.sh find "doc metadata"`.

### 2. Prepare the release changes

`./run.sh release run <target-version>` changes version-controlled files and is owner-approved release work. Do not run it during a review-only task or without authorization to prepare the release.

After the version change, review the diff and complete the release notes required by the printed checklist. Codex performs the scoped commit and PR update; do not tag, merge, or publish yet.

### 3. Build one exact artifact

From the workspace root:

```bash
./scripts/python_runtime.sh -m build Python
```

Before building, inspect and recoverably remove only the generated
`Python/build`, `Python/dist`, and `Python/*.egg-info` targets that exist. The
safe-file-ops scripts are for tracked source files, not generated output. Never
use an unresolved glob or a recursive delete for this cleanup; prove every
target is generated, ignored, inside `Python/`, and contains no links first.

Confirm that `Python/dist/` contains the wheel for the exact target version. Do not verify an unversioned wildcard when several wheels exist.

### 4. Verify the installed artifact

```bash
./run.sh release verify --version <target-version> --source wheel
```

This creates and removes a unique temporary environment, installs the exact wheel, verifies the package, runs the installed-package checks, and exercises the CLI workflow. Do not create or delete a fixed `/tmp` directory manually.

The verifier must prove `structural_lib.__file__` is inside the disposable
environment before and after tests. It installs only the wheel's declared test
extras plus explicitly documented generated-client requirements; broad root
requirements are not acceptable artifact evidence.

After publication, first compare the public artifact hashes with the exact
publication manifest. When the publication workflow already recorded the full
installed-package UAT for those bytes, verify only the public package identity;
do not repeat the same UAT:

```bash
./run.sh release verify --version <target-version> --source pypi --identity-only
```

The verifier waits up to 90 seconds for the exact version to appear on the PyPI
simple index and retries only that install. It does not retry a real install
failure or rerun tests. Run the full public-source verifier only when the
publication workflow lacks exact installed-package UAT evidence or the public
artifact identity differs from the recorded manifest.

### 5. Owner-only actions

Codex may merge the in-scope release PR without additional approval after
verifying its reviewed head, required checks, conflicts, and blockers.
Creating or pushing a tag, publishing to PyPI, creating the GitHub release, and
closing release issues still require explicit user approval. A green preflight
does not authorize those release actions.

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
**Owner approval still required:** [tag/publish/release/issue-close actions]
```

## Integration

- **@ops** runs the release automation and preserves approval boundaries
- **@reviewer** checks that evidence belongs to the current release commit
- **@tester** runs the installed-artifact verification when requested
