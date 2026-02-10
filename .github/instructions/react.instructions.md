---
applyTo: "**/react_app/**"
---

# React App Rules

- Check `react_app/src/hooks/` and `react_app/src/components/` BEFORE creating new code
- CSV import: use `useCSVFileImport` hook → API → GenericCSVAdapter (never parse manually)
- 3D geometry: use `useBeamGeometry` hook → API → geometry_3d (never calculate manually)
- State stores: `useDesignStore` (single beam), `useImportedBeamsStore` (imported beams)
- Build check before commit: `cd react_app && npm run build`
