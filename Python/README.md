# structural-lib-is456

IS 456 RC Beam Design Library (Python package).

For full project overview and usage examples, see the repository root `README.md`.

## Quick Start: CLI Usage

The library provides a unified command-line interface:

```bash
# Run beam design from CSV input
python -m structural_lib design input.csv -o results.json

# Generate bar bending schedule
python -m structural_lib bbs results.json -o bbs.csv

# Generate DXF drawings (requires ezdxf)
python -m structural_lib dxf results.json -o drawings.dxf

# Run complete job from specification
python -m structural_lib job job.json -o output/
```

Run `python -m structural_lib --help` for more options.
