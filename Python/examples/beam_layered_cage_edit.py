"""Run the bounded FLOW03 layered-cage bar-edit evidence cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam


def _request_payload(frozen: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """Build the current layered-cage request for one frozen edit case."""
    base = frozen["base_request"]
    member = dict(base["member"])
    if "current_analysis_revision" in case:
        member["current_analysis_revision"] = case["current_analysis_revision"]
    layered_cage = {
        "placement": case.get("placement", frozen["placement"]),
        "cross_tie": case.get("cross_tie", frozen["cross_tie"]),
        "service": {
            "uniform_load_kn_per_m": frozen["base_expected"]["service"][
                "unfactored_udl_kn_per_m_per_span"
            ],
            "analysis_revision": base["member"]["analysis_revision"],
            "source_reference": frozen["base_expected"]["service"]["source_reference"],
        },
    }
    return {
        **base,
        "member": member,
        "layered_cage": layered_cage,
    }


def _write_outputs(
    directory: Path,
    serialized: str,
    result: Any,
) -> None:
    """Write the current report and remove drawing/BBS files no longer eligible."""
    directory.mkdir(parents=True, exist_ok=True)
    # Recheck returns the edited request, whose identity is the sole eligible
    # source for physical outputs (not the pre-edit current request).
    drawing = beam.render_continuous_detailing_svg(result, current=result.request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=result.request)
    outputs = (("member.svg", drawing), ("bbs.csv", schedule))
    for name, _ in outputs:
        (directory / name).unlink(missing_ok=True)
    (directory / "result.json").write_text(serialized, encoding="utf-8")
    (directory / "report.html").write_text(
        beam.render_continuous_detailing_html(result, current=result.request),
        encoding="utf-8",
    )
    for name, content in outputs:
        if content is not None:
            (directory / name).write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--case", default="edited", help="base or a frozen case key")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if not args.reference.is_file():
        parser.error("--reference must name the frozen FLOW03 fixture.")
    frozen = json.loads(args.reference.read_text(encoding="utf-8"))
    cases = frozen["cases"]
    if args.case != "base" and args.case not in cases:
        parser.error(f"Unknown case {args.case}. Choices: base, {', '.join(cases)}.")
    case = {} if args.case == "base" else cases[args.case]
    try:
        request = beam.load_continuous_detailing(_request_payload(frozen, case))
    except InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    # A changed placement/cross-tie is part of the current basis, not merely a
    # rendering option; check it before applying the one-bar edit.  The base
    # result remains the deliberately old result for the stale-action control.
    if "placement" in case or "cross_tie" in case:
        previous = beam.check_continuous_detailing(request)
    else:
        base_request = beam.load_continuous_detailing(_request_payload(frozen, {}))
        previous = beam.check_continuous_detailing(base_request)
    if args.case == "base":
        result = previous
    else:
        result = beam.recheck_continuous_bar_edit(
            request,
            previous,
            beam.BeamBarEditV1.model_validate(case["edit"]),
            analysis_basis=case["analysis_basis"],
        )
    serialized = json.dumps(result.to_dict(), allow_nan=False) + "\n"
    if args.output_dir is not None:
        _write_outputs(args.output_dir, serialized, result)
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
