---
description: Rules for editing React app files
globs: react_app/**
---

# React App Rules

## Folder Structure

```
react_app/src/
├── components/          # UI components (grouped by feature)
│   ├── design/          # Beam design (DesignView, BeamForm, ResultsPanel)
│   ├── import/          # Data import (ImportView, CSVImportPanel, BeamTable)
│   ├── viewport/        # 3D visualization (Viewport3D, WorkspaceLayout)
│   ├── layout/          # App shell (TopBar, ModernAppLayout)
│   ├── pages/           # Route-level pages (Home, ModeSelect, Building)
│   └── ui/              # Shared primitives (BentoGrid, FileDropZone, Toast)
├── hooks/               # Custom hooks (CSV import, geometry, live design)
├── store/               # Zustand stores (design, imported beams)
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── App.tsx              # Root component
└── main.tsx             # Entry point
```

## Styling: Tailwind Only

- All components use Tailwind utility classes — **no custom CSS files**
- Never create `.css` files for components — use Tailwind classes inline

## NEVER duplicate hooks or components

Check what exists BEFORE creating anything new:
```bash
ls react_app/src/hooks/       # All custom hooks
ls react_app/src/components/  # All components
```

Key hooks you MUST reuse (not reinvent):
- CSV import: `useCSVFileImport`, `useDualCSVImport`, `useBatchDesign` (useCSVImport.ts)
- 3D geometry: `useBeamGeometry` (useBeamGeometry.ts)
- Live design: `useLiveDesign`, `useAutoDesign`
- Building viz: `useBuildingGeometry`, `useCrossSectionGeometry` (useGeometryAdvanced.ts)

Key components:
- 3D viewport: `Viewport3D` (Viewport3D.tsx)
- Beam editor: `BuildingEditorPage` (pages/BuildingEditorPage.tsx)
- File upload: `FileDropZone` (ui/FileDropZone.tsx)

## All data flows through FastAPI

```
WRONG: Parse CSV in React, calculate geometry in JS
RIGHT: useCSVFileImport → POST /api/v1/import/csv → GenericCSVAdapter
RIGHT: useBeamGeometry → POST /api/v1/geometry/beam/full → geometry_3d
```

## State stores (Zustand)

- `useDesignStore` — Single beam design inputs/results
- `useImportedBeamsStore` — Imported CSV beams + selection

## Migration Scripts

- **Move a component:** `.venv/bin/python scripts/migrate_react_component.py <src> <dst> --dry-run`
- Co-located CSS files are moved automatically

## Build check before commit

```bash
cd react_app && npm run build
```
