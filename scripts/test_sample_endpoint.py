#!/usr/bin/env python3
"""Quick test of the sample data endpoint."""

import json
import urllib.request

url = "http://localhost:8000/api/v1/import/sample"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())

print(f"Success: {data['success']}")
print(f"Message: {data['message']}")
print(f"Count: {data['beam_count']}")
print(f"Format: {data.get('format_detected', 'MISSING')}")
print(f"Warnings: {data.get('warnings', 'MISSING')}")
print(f"Beams with point1: {sum(1 for b in data['beams'] if b.get('point1'))}")
print(f"Beams with story: {sum(1 for b in data['beams'] if b.get('story'))}")
bad = [
    b for b in data["beams"] if b.get("width_mm", 0) <= 0 or b.get("depth_mm", 0) <= 0
]
print(f"Beams with bad dimensions: {len(bad)}")
zero_mu = [b for b in data["beams"] if b.get("mu_knm", 0) == 0]
print(f"Beams with zero moment: {len(zero_mu)}")
zero_vu = [b for b in data["beams"] if b.get("vu_kn", 0) == 0]
print(f"Beams with zero shear: {len(zero_vu)}")
stories = sorted(set(b.get("story", "None") for b in data["beams"]))
print(f"Stories: {stories}")

# Verify first beam mapping would work
b = data["beams"][0]
print("\nFirst beam:")
print(
    f"  id={b['id']} story={b.get('story')} width_mm={b['width_mm']} depth_mm={b['depth_mm']}"
)
print(f"  span_mm={b['span_mm']} mu_knm={b['mu_knm']} vu_kn={b['vu_kn']}")
print(f"  fck_mpa={b['fck_mpa']} fy_mpa={b['fy_mpa']} cover_mm={b['cover_mm']}")
print(f"  point1={b.get('point1')} point2={b.get('point2')}")

# Simulate mapSampleBeamsToRows mapping
mapped = {
    "id": b["id"],
    "story": b.get("story"),
    "b": b["width_mm"],
    "D": b["depth_mm"],
    "span": b["span_mm"],
    "fck": b["fck_mpa"],
    "fy": b["fy_mpa"],
    "Mu_mid": b["mu_knm"],
    "Vu_start": b["vu_kn"],
    "cover": b["cover_mm"],
    "point1": b.get("point1"),
    "point2": b.get("point2"),
}
print(f"\nMapped to store format: {json.dumps(mapped, indent=2)}")
