# structural_engineering_lib

IS 456 RC Beam Design Library for structural engineers.

## Features

- **Flexure Design** — IS 456:2000 compliant beam design
- **Shear Design** — Stirrup spacing and shear capacity
- **Detailing** — Rebar arrangement per IS 456 Ch. 26
- **BBS Export** — Bar bending schedule (CSV/Excel)
- **DXF Export** — AutoCAD-compatible drawings
- **3D Visualization** — React Three Fiber interactive viewer
- **Cost Optimization** — Multi-objective beam optimization

## Quick Install

```bash
pip install -e Python/
```

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + R3F + Tailwind |
| Backend | FastAPI (38 endpoints) |
| Core | Python structural_lib (IS 456:2000) |

## Documentation

- [Getting Started](getting-started/python-quickstart.md)
- [API Reference](reference/api.md)
- [Architecture](architecture/project-overview.md)
- [Contributing](contributing/development-guide.md)
