---
name: user-acceptance-test
description: "Verify an exact built or published package in the canonical clean environment and exercise its installed-package and CLI main process."
---

# User Acceptance Test

Use the canonical release verifier instead of copying API examples into this skill. Public signatures change; the verifier and API discovery are the maintained sources of truth.

## When to Use

- Before a release is approved
- After package metadata, exports, or installed CLI behavior changes
- After publishing, to verify the exact PyPI version

## Preconditions

- Run from the workspace root.
- Identify the exact version and source being accepted.
- For a wheel, build it first with `.venv/bin/python -m build Python` and confirm the versioned artifact exists in `Python/dist/`.
- Do not accept evidence from a different commit or version.

## Pre-Release Wheel UAT

```bash
./run.sh release verify --version <version> --source wheel
```

The verifier creates a unique temporary virtual environment, installs the exact wheel, validates the installed package, runs its core checks, and exercises the CLI job → critical → report flow. Temporary state is cleaned automatically.

Do not pass `--skip-cli` unless the approved scope explicitly excludes the CLI. A convenience failure that does not affect the installed-package or CLI main process is not a UAT blocker.

## Post-Publication UAT

```bash
./run.sh release verify --version <version> --source pypi
```

This must use the exact published version. Passing a local wheel does not prove the PyPI artifact works.

## API-Specific Follow-Up

If UAT fails at a public function call, discover the live signature before diagnosing or changing code:

```bash
./run.sh find --api <function_name>
```

Do not repair UAT by hardcoding a second copy of the signature in this skill.

## Report Format

```
## User Acceptance Test Report

| Evidence | Status | Notes |
|----------|--------|-------|
| Exact package installed | ✅/❌ | [wheel filename or PyPI version] |
| Package checks | ✅/❌ | [first failing command, if any] |
| CLI main process | ✅/❌ | [job/critical/report result] |

**Verdict:** ALL PASS / FAILURES FOUND
**Blockers:** [only failures that change the accepted user process]
```

## Who Runs This

- **@tester** runs installed-artifact acceptance
- **@ops** selects the exact artifact/source and preserves release approvals
- **@reviewer** verifies that the evidence matches the release commit and version
