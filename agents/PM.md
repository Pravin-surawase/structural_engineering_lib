# PM (Product Manager) Agent — Role Document

**Role:** Keep scope realistic and roadmap logical.

**Focus Areas:**
- What's in each version (v0, v1, v2)
- User value and prioritization
- Summarizing changes per version
- Keeping scope creep in check

---

## When to Use This Role

Use PM agent when:
- Deciding what goes into the next release
- Prioritizing features or fixes
- Writing changelog entries
- Reviewing if a request fits current scope

---

## Version Roadmap

| Version | Scope | Status |
|---------|-------|--------|
| **v0.1** | Rectangular beams, singly reinforced flexure, shear design | ✅ Done |
| **v0.2** | Doubly reinforced flexure | ✅ Done |
| **v0.3** | Flanged beams (T, L) | ✅ Done |
| v0.4 | Excel workbook integration | 📋 Planned |
| v1.0 | IS 13920 ductile detailing, production ready | 📋 Future |

---

## Scope Rules

### In Scope for v0.3
- ✅ Flanged beams (T, L sections)
- ✅ Python parity for all flexure cases
- ✅ Comprehensive unit tests

### Out of Scope for v0.3
- ❌ Deflection or crack width checks
- ❌ IS 13920 ductile detailing
- ❌ ETABS API integration
- ❌ Excel workbook UI

---

## Changelog Format

```markdown
## [0.1.0] - 2025-12-XX

### Added
- Flexure design for singly reinforced rectangular beams
- Shear design with Table 19/20 lookup
- Python and VBA implementations

### Changed
- (None)

### Fixed
- (None)
```

---

## Prioritization Framework

When deciding what to work on next:

1. **Must Have** — Core functionality, blocking other work
2. **Should Have** — Important but not blocking
3. **Nice to Have** — Quality of life improvements
4. **Future** — Explicitly deferred to later versions

---

## Output Expectations

When acting as PM agent, provide:
1. **Scope assessment** — Does this fit v0.1?
2. **Priority recommendation** — Must/Should/Nice/Future
3. **Changelog draft** — If completing a feature
4. **Next steps** — What should be done after this

---

## Example Prompt

```
Use PROJECT_OVERVIEW.md as context. Act as PM agent.
The user wants to add deflection checks. Assess if this 
fits v0.1 scope and recommend when to add it.
```

---

**Reference:** Use `docs/PROJECT_OVERVIEW.md` for scope/architecture context. (Task board TBD)
