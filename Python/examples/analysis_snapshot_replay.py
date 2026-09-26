"""Validate a portable analysis snapshot offline, without contacting ETABS.

Run ``python3 Python/examples/analysis_snapshot_replay.py snapshot.json``.
With no path, use the repository's maintained synthetic conformance fixture.
Successful replay establishes capture consistency, not live-model freshness or
engineering approval. The Python API does not acquire or normalize live ETABS
data; see the WP10 reference for the separate native adapter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.analysis_snapshot import (
    canonical_analysis_snapshot_json,
    parse_analysis_snapshot_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", type=Path)
    args = parser.parse_args()
    if args.snapshot is None:
        fixture_path = (
            Path(__file__).resolve().parents[2]
            / "contracts/structural-engineering/conformance/wp10-vectors.json"
        )
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload = json.dumps(fixture["valid_snapshot"]).encode("utf-8")
    else:
        payload = args.snapshot.read_bytes()

    result = parse_analysis_snapshot_json(payload)
    summary = result.model_dump(mode="json", exclude={"snapshot"})
    if result.snapshot is not None:
        snapshot = result.snapshot
        canonical = canonical_analysis_snapshot_json(snapshot)
        replayed = parse_analysis_snapshot_json(canonical)
        assert replayed.snapshot == snapshot
        summary["snapshot"] = {
            "snapshot_id": snapshot.snapshot_id,
            "sha256": snapshot.snapshot_sha256,
            "members": len(snapshot.members),
            "action_rows": len(snapshot.action_rows),
            "canonical_round_trip": True,
        }
    print(json.dumps(summary, indent=2))
    return 0 if result.snapshot is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
