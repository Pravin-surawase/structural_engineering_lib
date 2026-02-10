---
applyTo: "**/react_app/**"
---

# React App Rules

## Folder Structure

```
react_app/src/
├── components/          # UI components (grouped by feature)
│   ├── design/          # Beam design (DesignView, BeamForm, ResultsPanel, CrossSectionView)
│   ├── import/          # Data import (ImportView, CSVImportPanel, BeamTable)
│   ├── viewport/        # 3D visualization (Viewport3D, WorkspaceLayout, LandingView)
│   ├── layout/          # App shell (TopBar, ModernAppLayout)
│   ├── pages/           # Route-level pages (Home, ModeSelect, Building, BeamDetail)
│   ├── ui/              # Shared primitives (BentoGrid, FileDropZone, Toast, etc.)
│   └── CommandPalette.tsx # Global overlay
├── hooks/               # Custom hooks (CSV import, geometry, live design)
├── store/               # Zustand stores (design, imported beams)
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── App.tsx              # Root component
└── main.tsx             # Entry point
```

## Styling: Tailwind Only

- All components use Tailwind utility classes — **no custom CSS files**
- Dockview theme vars are in `index.css` (the only non-Tailwind CSS)
- Never create `.css` files for components — use Tailwind classes inline

## Key Patterns — Check BEFORE Creating New Code

- `react_app/src/hooks/` and `react_app/src/components/` — check for existing code
- CSV import: use `useCSVFileImport` hook → API → GenericCSVAdapter (never parse manually)
- 3D geometry: use `useBeamGeometry` hook → API → geometry_3d (never calculate manually)
- State stores: `useDesignStore` (single beam), `useImportedBeamsStore` (imported beams)

## Migration Scripts

- **Move a component:** `.venv/bin/python scripts/migrate_react_component.py <src> <dst> --dry-run`
- Co-located CSS files are moved automatically

## Build & Test

- Build check before commit: `cd react_app && npm run build`
- Dev server: `cd react_app && npm run dev` (port 5173)
