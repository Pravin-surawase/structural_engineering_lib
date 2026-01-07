# CHANGELOG Template for Deprecations

This template guides you when adding deprecation entries to `CHANGELOG.md`.

---

## Where to Add

Deprecations go under the **`### Deprecated`** section for the **current unreleased version**.

If the section doesn't exist, add it under `## [Unreleased]`:

```markdown
## [Unreleased]

### Added
...

### Changed
...

### Deprecated
- Item 1
- Item 2

### Removed
...

### Fixed
...
```

---

## Template Format

### For Functions

```markdown
### Deprecated

- **`module.function_name()`** — Deprecated since vX.Y.0, will be removed in vZ.0.0.
  Use `module.new_function()` instead. Reason: [brief explanation]. (#PR_NUMBER)
```

**Example:**

```markdown
### Deprecated

- **`flexure.calculate_moment_old()`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  Use `flexure.calculate_moment()` instead. Reason: Explicit unit naming reduces errors. (#254)
```

### For Dataclass Fields

```markdown
### Deprecated

- **`DataClassName.field_name`** — Deprecated since vX.Y.0, will be removed in vZ.0.0.
  Use `DataClassName.new_field` instead. Reason: [brief explanation]. (#PR_NUMBER)
```

**Example:**

```markdown
### Deprecated

- **`FlexureResult.error_message`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  Use `FlexureResult.errors` list instead. Reason: Structured error handling. (#254)
```

### For Parameters

```markdown
### Deprecated

- **`function_name()` parameter `param_name`** — Deprecated since vX.Y.0, will be removed in vZ.0.0.
  [Explanation of what changed]. (#PR_NUMBER)
```

**Example:**

```markdown
### Deprecated

- **`api.design_beam_is456()` parameter `units`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  All calculations now use IS 456 units by default. The parameter is ignored. (#254)
```

### For Classes

```markdown
### Deprecated

- **`module.ClassName`** — Deprecated since vX.Y.0, will be removed in vZ.0.0.
  Use `module.NewClassName` instead. Reason: [brief explanation]. (#PR_NUMBER)
```

**Example:**

```markdown
### Deprecated

- **`data_types.OldBeamResult`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  Use `data_types.BeamDesignResult` instead. Reason: Unified result type. (#254)
```

### For Modules

```markdown
### Deprecated

- **`old_module_name` module** — Deprecated since vX.Y.0, will be removed in vZ.0.0.
  Functionality moved to `new_module_name`. (#PR_NUMBER)
```

---

## Full Example

Here's a complete deprecation section:

```markdown
## [Unreleased]

### Added
- Deprecation utilities (`utilities.deprecated`, `utilities.deprecated_field`) (#254)
- Deprecation policy documentation (`docs/reference/deprecation-policy.md`) (#254)

### Deprecated
- **`flexure.calculate_moment_old()`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  Use `flexure.calculate_moment()` instead. Reason: Explicit unit naming. (#254)
- **`FlexureResult.error_message`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  Use `FlexureResult.errors` list instead. Reason: Structured error handling. (#254)
- **`api.design_beam_is456()` parameter `units`** — Deprecated since v0.14.0, will be removed in v1.0.0.
  All calculations use IS 456 units by default. Parameter ignored. (#254)
```

---

## When Removing Deprecated Features

When actually **removing** a deprecated feature (e.g., in v1.0.0), move the entry to `### Removed`:

```markdown
## [1.0.0] - 2026-XX-XX

### Removed
- **`flexure.calculate_moment_old()`** — Removed (deprecated since v0.14.0).
  Use `flexure.calculate_moment()`. (#301)
- **`FlexureResult.error_message`** — Removed (deprecated since v0.14.0).
  Use `FlexureResult.errors`. (#301)
```

---

## Checklist

When deprecating a feature:

- [ ] Add `@deprecated` decorator to the function/method
- [ ] Add deprecation entry to CHANGELOG.md under `### Deprecated`
- [ ] Update function docstring with `.. deprecated::` directive
- [ ] Update API documentation to mark as deprecated
- [ ] Add tests that verify deprecation warning is emitted
- [ ] Document migration path in release notes
- [ ] Reference PR number in CHANGELOG entry

---

## References

- Main CHANGELOG: `../../CHANGELOG.md`
- Deprecation Policy: `../reference/deprecation-policy.md`
- Keep a Changelog format: https://keepachangelog.com/
