---
name: react-validation
description: "Run React build, lint, type-check, and test validation. Use after modifying React components, hooks, or configuration. Catches TypeScript errors, Tailwind issues, and build failures before commit."
argument-hint: "Optional: 'build' | 'lint' | 'types' | 'test' | 'all' (default: all)"
---

# React Validation Skill

Validate React frontend code quality — build, lint, type-check, and test.

## When to Use

- After modifying any file in `react_app/src/`
- After adding new components, hooks, or types
- Before committing any frontend change
- When `npm run build` fails and you need diagnostics

## Full Validation (Default)

```bash
cd react_app && npm run build
```

Build includes TypeScript compilation — catches both type errors and import issues.

## Individual Checks

### TypeScript type-check only:
```bash
cd react_app && npx tsc --noEmit
```

### Lint check:
```bash
cd react_app && npx eslint src/ --max-warnings 0
```

### Run tests:
```bash
cd react_app && npx vitest run
```

### Dev server (manual testing):
```bash
cd react_app && npm run dev
# Opens at http://localhost:5173
```

## Pre-Commit Checklist

Run these in order before committing frontend changes:

1. **Build passes:** `cd react_app && npm run build`
2. **No unused imports:** Check build output for warnings
3. **No duplicate hooks:** `ls react_app/src/hooks/` — verify you didn't recreate an existing hook
4. **No CSS files created:** `find react_app/src -name "*.css" ! -name "index.css"` — should return nothing

## Common Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TS2307: Cannot find module` | Wrong import path | Check if file was moved — use relative paths |
| `TS2339: Property does not exist` | Wrong type or missing field | Check TypeScript types in `types/` |
| `TS2345: Argument not assignable` | Type mismatch in hook/component | Verify Pydantic model matches TS type |
| `Module not found` | Missing dependency | `cd react_app && npm install <pkg>` |
| Tailwind class not applied | Typo in class name | Check Tailwind docs for correct utility name |

## Existing Hooks (DO NOT recreate)

Before creating a new hook, check:
```bash
ls react_app/src/hooks/
```

21 hooks across 11 files already exist. See `frontend.agent.md` for the full list.

## Existing Components

Before creating a new component, check:
```bash
ls react_app/src/components/
ls react_app/src/components/design/
ls react_app/src/components/import/
ls react_app/src/components/viewport/
ls react_app/src/components/ui/
```
