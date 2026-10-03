"""Inspect native member-readiness evidence with the installed public Python API.

Example from a source checkout (the fixture is a frozen offline control):
    python3 Python/examples/member_readiness_workflow.py \
        contracts/structural-engineering/conformance/beam-readiness-v1.gz

Python validates transport and bindings; native Assess owns readiness rules.
Stored readiness never supplies current bindings or professional approval.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

from structural_lib.analysis_snapshot import parse_analysis_snapshot_json
from structural_lib.beam_readiness import (
    beam_readiness_freshness,
    parse_beam_readiness_json,
)
from structural_lib.core.freshness import FreshnessState


def _read(path: Path) -> bytes:
    payload = path.read_bytes()
    return gzip.decompress(payload) if path.suffix == ".gz" else payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path, help="Native readiness JSON or .gz")
    parser.add_argument("--current-snapshot", type=Path)
    parser.add_argument("--current-ledger-revision")
    parser.add_argument("--current-request-id")
    parser.add_argument("--current-engine-identity")
    args = parser.parse_args(argv)
    bindings = (
        args.current_snapshot,
        args.current_ledger_revision,
        args.current_request_id,
        args.current_engine_identity,
    )
    if any(value is not None for value in bindings) and not all(bindings):
        parser.error("Supply all four current bindings, or omit all for inspection.")
    try:
        document = parse_beam_readiness_json(_read(args.document))
        freshness = FreshnessState.UNBOUND
        if args.current_snapshot is not None:
            parsed = parse_analysis_snapshot_json(_read(args.current_snapshot))
            if parsed.snapshot is None:
                raise ValueError(
                    "Current snapshot failed its schema or evidence validation."
                )
            freshness = beam_readiness_freshness(
                document,
                current_snapshot=parsed.snapshot,
                current_ledger_revision=args.current_ledger_revision,
                current_request_id=args.current_request_id,
                current_engine_identity=args.current_engine_identity,
            )
        print(
            json.dumps(
                {
                    "cohort_id": document.request.cohort_id,
                    "document_id": document.document_id,
                    "request_id": document.request_id,
                    "profile_id": document.profile_id,
                    "policy_revision": document.policy_revision,
                    "engine_identity": document.engine_identity,
                    "ledger_revision": (
                        document.ledger.revision if document.ledger else None
                    ),
                    "requested_member_count": len(document.request.member_ids),
                    "freshness": freshness.value,
                    "members": [
                        {
                            "member_id": member.member_id,
                            "recorded_state": member.state,
                            "recorded_ready_for_selected_profile": (
                                member.ready_for_selected_profile
                            ),
                            "diagnostics": [x.code for x in member.diagnostics],
                        }
                        for member in document.members
                    ],
                    "engineering": document.engineering,
                    "approval": document.approval,
                    "source_qualification": document.source_qualification,
                },
                indent=2,
                allow_nan=False,
            )
        )
        return 2 if freshness is FreshnessState.STALE else 0
    except (OSError, ValueError) as error:
        print(f"Readiness input rejected: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
