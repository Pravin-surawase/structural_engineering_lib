# Architecture

Deep dives into project structure and design decisions.

## Contents

| Document | Purpose |
|----------|---------|
| [Project Overview](project-overview.md) | High-level scope, layers, workflows |
| [Deep Project Map](deep-project-map.md) | Consolidated architecture and data flow |
| [Mission & Principles](mission-and-principles.md) | Core principles and non-negotiables |
| [Visual Architecture Diagrams](visual-architecture.md) | Mermaid diagrams for layers, module groupings, and data flow |
| [Module Dependency Graph](dependencies.md) | Generated dependency graph for `structural_lib` |

## Quick architecture summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         IS 456 DESIGN PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│   CSV/JSON ──► Design ──► Compliance ──► Detailing ──► DXF/Schedule    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key design decisions

- **Deterministic outputs** — Same input → same output
- **Explicit units** — No hidden conversions
- **Python/VBA parity** — Matching behavior where implemented
- **Layer separation** — Core has no I/O dependencies
