#!/usr/bin/env python3
"""
End-to-end test of all import paths.
Simulates what the React app does for each import flow.
Tests: sample data, single CSV, dual CSV, batch design.
"""

import json
import urllib.request
import urllib.error
import sys
from pathlib import Path

API = "http://localhost:8000"
BASE = Path(__file__).parent.parent
PASS = 0
FAIL = 0


def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  PASS  {name}")
        PASS += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        FAIL += 1


def api_get(path):
    with urllib.request.urlopen(f"{API}{path}") as r:
        return json.loads(r.read())


def api_post_json(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def api_post_form(path, fields, files):
    """Multipart form POST."""

    boundary = "----TestBoundary12345"
    body_parts = []
    for k, v in fields.items():
        body_parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
        )
    for k, (filename, content) in files.items():
        body_parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'
            f"Content-Type: text/csv\r\n\r\n{content}\r\n"
        )
    body_parts.append(f"--{boundary}--\r\n")
    body = "".join(body_parts).encode()
    req = urllib.request.Request(
        f"{API}{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def simulate_store_mapping(beam_from_api, has_3d=False):
    """Simulates the onSuccess mapping in useCSVImport.ts / sampleData.ts."""
    mapped = {
        "id": beam_from_api["id"],
        "story": beam_from_api.get("story"),
        "b": beam_from_api["width_mm"],
        "D": beam_from_api["depth_mm"],
        "span": beam_from_api["span_mm"],
        "fck": beam_from_api["fck_mpa"],
        "fy": beam_from_api["fy_mpa"],
        "Mu_mid": beam_from_api["mu_knm"],
        "Vu_start": beam_from_api["vu_kn"],
        "Vu_end": beam_from_api["vu_kn"],
        "cover": beam_from_api["cover_mm"],
    }
    if has_3d:
        mapped["point1"] = beam_from_api.get("point1")
        mapped["point2"] = beam_from_api.get("point2")
    return mapped


print("=" * 60)
print("IMPORT PIPELINE E2E TESTS")
print("=" * 60)

# ─── 1. HEALTH CHECK ───
print("\n1. Health Check")


def test_health():
    d = api_get("/health")
    assert d["status"] == "healthy", f"Got: {d}"


test("FastAPI is healthy", test_health)

# ─── 2. SAMPLE DATA ───
print("\n2. Sample Data Flow (/import/sample)")
sample = None


def test_sample():
    global sample
    sample = api_get("/api/v1/import/sample")
    assert sample["success"], f"Not successful: {sample.get('message')}"
    assert sample["beam_count"] == 153, f"Expected 153, got {sample['beam_count']}"
    assert len(sample["beams"]) == 153


test("GET /import/sample returns 153 beams", test_sample)


def test_sample_fields():
    b = sample["beams"][0]
    required = [
        "id",
        "story",
        "width_mm",
        "depth_mm",
        "span_mm",
        "mu_knm",
        "vu_kn",
        "fck_mpa",
        "fy_mpa",
        "cover_mm",
        "point1",
        "point2",
    ]
    missing = [f for f in required if f not in b]
    assert not missing, f"Missing fields: {missing}"


test("Sample beam has all required fields", test_sample_fields)


def test_sample_mapping():
    mapped = simulate_store_mapping(sample["beams"][0], has_3d=True)
    assert mapped["b"] > 0, f"Invalid width: {mapped['b']}"
    assert mapped["D"] > 0, f"Invalid depth: {mapped['D']}"
    assert mapped["span"] > 0, f"Invalid span: {mapped['span']}"
    assert mapped["Mu_mid"] > 0, f"Invalid moment: {mapped['Mu_mid']}"
    assert mapped["point1"] is not None, "Missing point1"


test("Sample beam maps to store format correctly", test_sample_mapping)


def test_sample_response_shape():
    expected_keys = {
        "success",
        "message",
        "beam_count",
        "beams",
        "format_detected",
        "warnings",
    }
    actual_keys = set(sample.keys())
    assert (
        expected_keys == actual_keys
    ), f"Key diff: expected={expected_keys}, got={actual_keys}"


test("Sample response has exact expected keys", test_sample_response_shape)


def test_sample_all_3d():
    beams_with_3d = [b for b in sample["beams"] if b.get("point1") and b.get("point2")]
    assert len(beams_with_3d) == 153, f"Only {len(beams_with_3d)}/153 have 3D"


test("All 153 sample beams have 3D positions", test_sample_all_3d)


def test_sample_all_stories():
    beams_with_story = [b for b in sample["beams"] if b.get("story")]
    assert len(beams_with_story) == 153, f"Only {len(beams_with_story)}/153 have story"


test("All 153 sample beams have story", test_sample_all_stories)

# ─── 3. SINGLE CSV IMPORT ───
print("\n3. Single CSV Import (/import/csv)")
forces_csv = BASE / "Etabs_CSV" / "beam_forces.csv"
single_result = None


def test_single_csv():
    global single_result
    content = forces_csv.read_text(encoding="utf-8-sig")
    single_result = api_post_form(
        "/api/v1/import/csv", {"format": "auto"}, {"file": ("beam_forces.csv", content)}
    )
    assert single_result["success"], f"Not successful: {single_result.get('message')}"
    assert (
        single_result["beam_count"] == 153
    ), f"Expected 153, got {single_result['beam_count']}"


test("POST /import/csv returns 153 beams", test_single_csv)


def test_single_csv_shape():
    expected_keys = {
        "success",
        "message",
        "beam_count",
        "beams",
        "format_detected",
        "warnings",
    }
    actual_keys = set(single_result.keys())
    assert (
        expected_keys == actual_keys
    ), f"Key diff: expected={expected_keys}, got={actual_keys}"


test(
    "Single CSV response has exact expected keys (no column_mapping)",
    test_single_csv_shape,
)


def test_single_csv_mapping():
    b = single_result["beams"][0]
    mapped = simulate_store_mapping(b)
    assert mapped["b"] > 0 and mapped["D"] > 0


test("Single CSV beam maps to store format", test_single_csv_mapping)

# ─── 4. DUAL CSV IMPORT ───
print("\n4. Dual CSV Import (/import/dual-csv)")
geometry_csv = BASE / "Etabs_CSV" / "frames_geometry.csv"
dual_result = None


def test_dual_csv():
    global dual_result
    geom_content = geometry_csv.read_text(encoding="utf-8-sig")
    forces_content = forces_csv.read_text(encoding="utf-8-sig")
    dual_result = api_post_form(
        "/api/v1/import/dual-csv?format_hint=auto",
        {},
        {
            "geometry_file": ("frames_geometry.csv", geom_content),
            "forces_file": ("beam_forces.csv", forces_content),
        },
    )
    assert dual_result["success"], f"Not successful: {dual_result.get('message')}"
    assert dual_result["beam_count"] > 0, "Got 0 beams"


test("POST /import/dual-csv returns beams", test_dual_csv)


def test_dual_csv_shape():
    expected_keys = {
        "success",
        "message",
        "beam_count",
        "beams",
        "format_detected",
        "warnings",
        "unmatched_beams",
        "unmatched_forces",
    }
    actual_keys = set(dual_result.keys())
    assert (
        expected_keys == actual_keys
    ), f"Key diff: expected={expected_keys}, got={actual_keys}"


test("Dual CSV response has exact expected keys", test_dual_csv_shape)


def test_dual_csv_3d():
    beams_with_3d = [
        b for b in dual_result["beams"] if b.get("point1") and b.get("point2")
    ]
    assert (
        len(beams_with_3d) == dual_result["beam_count"]
    ), f"Only {len(beams_with_3d)}/{dual_result['beam_count']} have 3D"


test("Dual CSV beams have 3D positions", test_dual_csv_3d)


def test_dual_csv_mapping():
    b = dual_result["beams"][0]
    mapped = simulate_store_mapping(b, has_3d=True)
    assert mapped["b"] > 0 and mapped["D"] > 0
    assert mapped["point1"] is not None


test("Dual CSV beam maps to store format with 3D", test_dual_csv_mapping)

# ─── 5. BATCH DESIGN ───
print("\n5. Batch Design (/import/batch-design)")
batch_result = None


def test_batch_design():
    global batch_result
    payload = [
        {
            "id": "B1",
            "width_mm": 230,
            "depth_mm": 450,
            "span_mm": 5000,
            "mu_knm": 100,
            "vu_kn": 50,
            "fck_mpa": 25,
            "fy_mpa": 500,
            "cover_mm": 40,
        },
        {
            "id": "B2",
            "width_mm": 300,
            "depth_mm": 500,
            "span_mm": 6000,
            "mu_knm": 200,
            "vu_kn": 80,
            "fck_mpa": 30,
            "fy_mpa": 500,
            "cover_mm": 40,
        },
    ]
    batch_result = api_post_json("/api/v1/import/batch-design", payload)
    assert batch_result["success"], f"Not successful: {batch_result.get('message')}"
    assert batch_result["total"] == 2


test("POST /import/batch-design designs 2 beams", test_batch_design)


def test_batch_design_shape():
    expected_keys = {"success", "message", "total", "passed", "failed", "results"}
    actual_keys = set(batch_result.keys())
    assert (
        expected_keys == actual_keys
    ), f"Key diff: expected={expected_keys}, got={actual_keys}"


test("Batch design response has 'passed' not 'successful'", test_batch_design_shape)


def test_batch_result_shape():
    r = batch_result["results"][0]
    expected = {
        "beam_id",
        "success",
        "ast_required",
        "asc_required",
        "stirrup_spacing",
        "is_safe",
        "utilization_ratio",
        "error",
    }
    actual = set(r.keys())
    assert expected == actual, f"Key diff: expected={expected}, got={actual}"


test(
    "Batch result has correct flat shape (not nested DesignedBeam)",
    test_batch_result_shape,
)


def test_batch_result_values():
    r = batch_result["results"][0]
    assert r["ast_required"] > 0, f"Zero ast: {r}"
    assert 0 < r["utilization_ratio"] < 5, f"Bad util: {r['utilization_ratio']}"


test("Batch design returns valid design values", test_batch_result_values)

# ─── SUMMARY ───
print(f"\n{'=' * 60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
print(f"{'=' * 60}")
sys.exit(1 if FAIL else 0)
