# Git Commit Message Conventions

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-16
**Last Updated:** 2026-01-16

---

## Quick Reference

```
<type>(<scope>): <subject>
                                    ← blank line
<body>                              ← optional
                                    ← blank line
<footer>                            ← optional
```

## Length Limits

| Component | Limit | Reason |
|-----------|-------|--------|
| **Subject line** | **72 characters** | GitHub truncates at 72, git log displays well |
| **Body lines** | **72 characters** | Terminal readability, git log wrapping |
| **Scope** | ~20 characters | Keep it concise |

## Type Prefixes (Required)

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(api): add beam analysis endpoint` |
| `fix` | Bug fix | `fix: resolve division by zero in shear calc` |
| `docs` | Documentation | `docs: update IS456 clause references` |
| `style` | Code style (no logic change) | `style: format with black` |
| `refactor` | Code refactoring | `refactor: extract validation to separate module` |
| `perf` | Performance improvement | `perf: optimize rebar computation loop` |
| `test` | Tests | `test: add edge cases for flexure module` |
| `build` | Build system | `build: update pyproject.toml dependencies` |
| `ci` | CI/CD changes | `ci: add coverage reporting to workflow` |
| `chore` | Maintenance | `chore: clean up unused imports` |
| `revert` | Revert previous commit | `revert: undo feat(api): add endpoint` |

## Scope (Optional)

The scope indicates the affected area:

```bash
# Good scopes
feat(api): ...           # API module
fix(flexure): ...        # Flexure calculations
docs(readme): ...        # README file
test(shear): ...         # Shear tests
ci(workflows): ...       # GitHub workflows
```

## Subject Line Rules

1. **Max 72 characters** (including type and scope)
2. **Imperative mood**: "add" not "added" or "adds"
3. **No period at end**
4. **Lowercase after colon** (conventional)

### Good Examples

```bash
feat(api): add beam design result export
fix: handle zero shear force edge case
docs: clarify installation prerequisites
refactor(flexure): extract moment capacity calculation
```

### Bad Examples

```bash
# ❌ Too long (93 chars)
feat(visualization): add comprehensive 3D beam rendering with stirrup placement and rebar paths

# ✅ Better (52 chars)
feat(visualization): add 3D beam rendering module

# ❌ Wrong tense
fixed the bug in shear calculation

# ✅ Better
fix: resolve shear calculation for zero force

# ❌ Ends with period
docs: update the readme.

# ✅ Better
docs: update readme installation section
```

## Body (Optional)

Use the body to explain **what** and **why**, not **how**:

```bash
fix: resolve division by zero in shear capacity

The shear capacity calculation could fail when the
applied shear force was exactly zero, causing an
unhandled ZeroDivisionError in the utilization ratio
computation.

This fix adds a zero-check before the division and
returns a 0% utilization for zero shear cases.

Fixes #234
```

## Footer (Optional)

Reference issues, breaking changes, or co-authors:

```bash
feat(api)!: redesign beam result structure

BREAKING CHANGE: BeamResult.reinforcement is now a
nested object instead of flat attributes.

Fixes #456
Co-authored-by: Team Member <team@example.com>
```

## Multi-Line Messages with ai_commit.sh

The `ai_commit.sh` script supports multi-line messages:

```bash
# Single line (most common)
./scripts/ai_commit.sh "feat(api): add new endpoint"

# For longer descriptions, edit commit message after:
git commit --amend  # Opens editor for full message
```

## Enforcement

### Install Commit Message Hook

```bash
./scripts/install_hooks.sh
```

This installs `.git/hooks/commit-msg` which validates:
- Subject line length (≤72 chars)
- Type prefix present
- No trailing period
- Body line length (≤72 chars)

### Bypass (Not Recommended)

```bash
git commit --no-verify -m "emergency fix"
```

## Common Patterns

### Feature with Scope

```bash
feat(visualization): add 3D beam preview component
```

### Bug Fix with Issue Reference

```bash
fix(flexure): handle negative moment values

The flexure calculation failed when moment values were
negative (indicating tension on the opposite face).

Fixes #789
```

### Documentation Update

```bash
docs: add API reference for shear module
```

### Breaking Change

```bash
feat(api)!: change return type of design_beam

BREAKING CHANGE: design_beam() now returns BeamDesignResult
instead of a dictionary. Update all callers to use the new
result object.
```

## Integration with CI

Commit message validation is enforced locally via the commit-msg hook.
CI validation is not currently configured in this repo.

---

## Related Documents

- [CONTRIBUTING.md](/CONTRIBUTING.md) - Overall contribution guidelines
- [Git Automation Guide](/docs/git-automation/README.md) - Git workflow automation
- [Agent Workflow Guide](/docs/agents/guides/agent-workflow-master-guide.md) - AI agent git usage
