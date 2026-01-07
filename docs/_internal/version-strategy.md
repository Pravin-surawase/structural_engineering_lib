# Version Management Strategy

## Single Source of Truth

**`Python/pyproject.toml`** is the ONLY place where the canonical version is defined.

```toml
version = "0.9.3"
```

## How Each Layer Gets the Version

### Python (Runtime)

| File | Strategy |
|------|----------|
| `api.py` → `get_library_version()` | Uses `importlib.metadata.version()` to read from installed package. Fallback only for dev mode. |
| `__init__.py` | **Remove hardcoded version.** Use `__version__ = get_library_version()` if needed. |

### VBA (Static)

| File | Strategy |
|------|----------|
| `M08_API.bas` → `Get_Library_Version()` | Must be updated by `bump_version.py` (VBA can't read external files). |

### Documentation

| File Type | Strategy |
|-----------|----------|
| Tutorials/Guides | Use phrases like "current version" or link to CHANGELOG. **Never hardcode.** |
| CHANGELOG.md | Historical record — new entries added, never edited. |
| releases.md | Historical record — new entries appended. |
| Snapshots | Version in filename is intentional (frozen baseline). |

## Files to Update on Release

Only 3 files need version updates:

1. **`Python/pyproject.toml`** — Source of truth (manual or script)
2. **`VBA/Modules/M08_API.bas`** — VBA runtime (script only)
3. **`CHANGELOG.md`** — Add new entry (manual)
4. **`docs/releases.md`** — Append entry (manual)

## What to Fix

### Remove Hardcoded Versions

| File | Current | Action |
|------|---------|--------|
| `Python/__init__.py` | `Version: 0.9.3` in docstring | Remove or make dynamic |
| `api.py` fallback | `return "0.9.3"` | Keep (dev mode fallback) but sync via script |
| `docs/*.md` footers | `Version: 0.9.x` | Change to "See CHANGELOG" or remove |

### Keep Version (Script-Updated)

| File | Reason |
|------|--------|
| `pyproject.toml` | Source of truth |
| `M08_API.bas` | VBA runtime needs it |

### Historical (Don't Auto-Update)

| File | Reason |
|------|--------|
| `CHANGELOG.md` | Append-only history |
| `docs/releases.md` | Append-only ledger |
| `Excel/snapshots/*.csv` | Frozen baselines |

## Updated `bump_version.py` Scope

Only update:
1. `pyproject.toml` — version string
2. `M08_API.bas` — VBA Get_Library_Version
3. `api.py` — fallback version (for dev mode)

Remove from script:
- `__init__.py` docstring version
- VBA test file headers (not runtime)
- Any doc files

## Release Workflow

```bash
# 1. Update pyproject.toml manually or:
python scripts/bump_version.py 0.9.4

# 2. Add CHANGELOG.md entry (manual)
# 3. Add releases.md entry (manual)
# 4. Commit and tag
git commit -am "release: v0.9.4"
git tag v0.9.4
```
