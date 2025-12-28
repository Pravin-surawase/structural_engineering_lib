#!/usr/bin/env python3
"""
Render DXF drawings to PNG or PDF using ezdxf + matplotlib.

Example:
  python scripts/dxf_render.py drawings.dxf -o drawings.png
  python scripts/dxf_render.py drawings.dxf -o drawings.pdf --dpi 200
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


def _resolve_output_path(output: str, fmt: Optional[str]) -> Path:
    path = Path(output)
    suffix = path.suffix.lower().lstrip(".")

    if fmt:
        fmt = fmt.lower()
        if fmt not in {"png", "pdf"}:
            raise ValueError("format must be png or pdf")
        if suffix != fmt:
            path = path.with_suffix(f".{fmt}")
    elif not suffix:
        path = path.with_suffix(".png")

    return path


def _require_ezdxf():
    try:
        import ezdxf  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Missing ezdxf. Install with: pip install \"structural-lib-is456[dxf]\""
        ) from exc


def _require_matplotlib():
    try:
        import matplotlib  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Missing matplotlib. Install with: pip install matplotlib"
        ) from exc


def render_dxf(input_path: Path, output_path: Path, dpi: int, pad_mm: float) -> None:
    _require_ezdxf()
    _require_matplotlib()

    import ezdxf
    from ezdxf.addons import drawing
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    doc = ezdxf.readfile(str(input_path))
    msp = doc.modelspace()

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")

    ctx = drawing.RenderContext(doc)
    backend = MatplotlibBackend(ax)
    frontend = drawing.Frontend(ctx, backend)
    frontend.draw_layout(msp)
    backend.finalize()
    ax.autoscale()

    pad_inches = pad_mm / 25.4
    fig.savefig(
        str(output_path),
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=pad_inches,
    )
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a DXF file to PNG or PDF.",
    )
    parser.add_argument("input", help="Path to DXF file")
    parser.add_argument("-o", "--output", required=True, help="Output PNG/PDF path")
    parser.add_argument(
        "--format",
        choices=["png", "pdf"],
        help="Force output format (default: inferred from output path)",
    )
    parser.add_argument("--dpi", type=int, default=200, help="Output DPI (default: 200)")
    parser.add_argument(
        "--pad-mm",
        type=float,
        default=2.0,
        help="Padding in mm around the drawing (default: 2.0)",
    )

    args = parser.parse_args()
    try:
        output_path = _resolve_output_path(args.output, args.format)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        render_dxf(Path(args.input), output_path, dpi=args.dpi, pad_mm=args.pad_mm)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    print(f"Rendered: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
