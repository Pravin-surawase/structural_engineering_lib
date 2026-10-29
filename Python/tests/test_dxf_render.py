"""Printed drawing previews must preserve CAD data and be readable on white."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


def test_dxf_print_render_is_monochrome_without_mutating_cad(tmp_path: Path) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    pytest.importorskip("matplotlib")
    image_module = pytest.importorskip("PIL.Image")
    source = tmp_path / "cad-colors.dxf"
    output = tmp_path / "print.png"
    doc = ezdxf.new()
    model = doc.modelspace()
    model.add_line((0, 0), (500, 0), dxfattribs={"color": 3})
    model.add_text("B1 300x500 mm", dxfattribs={"height": 25, "color": 2})
    model.add_text(
        "d = 444 mm", dxfattribs={"height": 25, "color": 4, "insert": (0, 60)}
    )
    doc.saveas(source)
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    script = Path(__file__).resolve().parents[2] / "scripts/dxf_render.py"
    result = subprocess.run(
        [sys.executable, str(script), str(source), "-o", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original
    with image_module.open(output).convert("RGB") as image:
        raw = image.tobytes()
        pixels = list(zip(raw[0::3], raw[1::3], raw[2::3], strict=True))
    assert sum(max(pixel) < 100 for pixel in pixels) > 100
    assert all(max(pixel) - min(pixel) <= 1 for pixel in pixels)
