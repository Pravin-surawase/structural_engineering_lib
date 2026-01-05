"""Inspect DXF layers and entity counts."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

import ezdxf  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
path = OUTPUT_DIR / "test_beam_1.dxf"

print(f"Inspecting: {path}")

doc = ezdxf.readfile(path)

layers = [layer.dxf.name for layer in doc.layers]
print("Layers:", ", ".join(layers))

msp = doc.modelspace()
entity_counts = {}
for entity in msp:
    etype = entity.dxftype()
    entity_counts[etype] = entity_counts.get(etype, 0) + 1

print("Entity counts:")
for etype, count in sorted(entity_counts.items()):
    print(f"  {etype}: {count}")
