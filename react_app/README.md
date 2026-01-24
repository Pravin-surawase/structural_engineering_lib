# Structural Engineering React App

React-based IDE for structural beam design with 3D visualization.

## Features

- **3D Viewport** - React Three Fiber powered beam visualization
- **Design Form** - Input parameters for IS 456 beam design
- **Results Panel** - Live display of flexure/shear calculations
- **IDE Layout** - Dockview-based resizable panels

## Tech Stack

- **React 18** + TypeScript
- **Vite** - Fast dev server and build
- **React Three Fiber** - 3D rendering
- **Dockview** - IDE-style panel layout
- **TanStack Query** - Server state management
- **Zustand** - Client state management

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Development

### Prerequisites

1. FastAPI backend running on `http://localhost:8000`
2. Node.js 18+

### Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Configure:
- `VITE_API_URL` - FastAPI backend URL (default: `http://localhost:8000`)

### Project Structure

```
src/
├── api/
│   └── client.ts       # FastAPI client (types + fetch functions)
├── components/
│   ├── BeamForm.tsx    # Design input form
│   ├── Viewport3D.tsx  # R3F 3D viewport
│   ├── ResultsPanel.tsx # Design results display
│   └── WorkspaceLayout.tsx # Dockview layout
└── store/
    └── designStore.ts  # Zustand state management
```

## Integration with FastAPI

This app connects to the FastAPI backend (`fastapi_app/`) which provides:

- `POST /api/v1/design/beam` - Design calculation
- `GET /api/v1/geometry/beam` - Geometry metrics
- `GET /health` - Health check

## Roadmap

- [ ] WebSocket for live updates (<100ms latency)
- [ ] Multi-beam support with LOD
- [ ] Rebar detail rendering
- [ ] CSV import visualization
- [ ] GLTF export
