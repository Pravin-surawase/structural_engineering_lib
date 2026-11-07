"""Replay Packet D's station check while preserving full-member admission HOLD."""

from __future__ import annotations

import json

from structural_lib import beam


def station_request(spacing_mm: float) -> beam.TorsionCheckRequest:
    bars = tuple(
        beam.BarPosition(name, 20, x, y, face)
        for name, x, y, face in (
            ("TL", 50, 50, beam.Face.TOP),
            ("TR", 250, 50, beam.Face.TOP),
            ("BL", 50, 350, beam.Face.BOTTOM),
            ("BR", 250, 350, beam.Face.BOTTOM),
        )
    )
    return beam.TorsionCheckRequest(
        "LIB-027-D-STATION",
        beam.ConcurrentActionRow(
            "ULS-1",
            "interior",
            beam.ActionBasis.STATIC_CONCURRENT,
            60,
            0,
            15,
            0,
            15,
            "independently frozen concurrent row",
        ),
        beam.FlexuralCapacityRequest(
            "LIB-027-D-STATION",
            beam.SectionKind.RECTANGULAR,
            300,
            400,
            25,
            415,
            bars,
            beam.Face.BOTTOM,
        ),
        beam.TransverseLink("S8", 8, 2, 2, spacing_mm, 415, True, 242, 342),
        ("TL", "TR", "BL", "BR"),
    )


def main() -> None:
    results = {
        name: beam.check_torsion(station_request(spacing)).to_dict()
        for name, spacing in (
            ("adequate_links", 100),
            ("corner_geometry_shortfall", 125),
        )
    }
    print(
        json.dumps(
            {
                "member_admission": "HOLD",
                "member_requirements": [
                    "Current torsional support and load-path evidence",
                    "Face-by-face tension anchorage, continuity and physical fit",
                    "Torsional serviceability method and acceptance criteria",
                    "All required member leaves and reconciled paths, BBS and report",
                ],
                "station_results": results,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
