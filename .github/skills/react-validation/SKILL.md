---
name: react-validation
description: "Validate changed React behavior with the Node version pinned by .nvmrc, root-stable npm commands, narrow tests while editing, and one production build."
argument-hint: "Changed hook, component, route, or user flow"
---

# React Validation

Run from the workspace root. Commands use `npm --prefix react_app` so later terminal commands do not inherit a hidden `react_app/` working directory.

## Select the Pinned Runtime

```bash
./run.sh frontend runtime
```

The repository selector verifies the `.nvmrc` major without assuming `nvm` is installed. If no healthy pinned runtime is available, follow `docs/getting-started/mac-mini-setup.md`; do not install a different major as an adjacent change.

## While Editing

Run the narrowest applicable command:

```bash
./run.sh frontend lint
./run.sh frontend test <test-pattern>
```

Before adding a hook or component, search the live tree rather than relying on a hardcoded count:

```bash
rg --files react_app/src/hooks
rg -n "<concept>" react_app/src/hooks react_app/src/components
```

## Stable Frontend Check

```bash
./run.sh frontend build
```

The build performs TypeScript compilation and the production Vite build. Do not add a separate `npx tsc` run unless diagnosing the TypeScript phase specifically, and do not download tooling through `npx`.

## User-Flow Verification

When the change affects a visible main process, start the canonical stack:

```bash
./run.sh dev
```

Verify the exact browser input → FastAPI request → rendered result or downloaded bytes. A successful build alone does not prove that flow. Clean up only the listeners started for this task with `./run.sh dev --kill-only`.

## Closeout

Run `./run.sh check --quick` before commit and `./run.sh check` once at stable implementation closeout. Do not run browser, Docker, coverage, or release checks when they are outside the changed user process.

For review-only work, report only confirmed failures that change the scoped user outcome; do not add tests or generic frontend cleanup.
