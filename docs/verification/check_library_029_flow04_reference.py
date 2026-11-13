"""Reconcile the frozen synthetic ETABS rows independently of the package."""

import json
from decimal import Decimal
from pathlib import Path


def main() -> None:
    reference = json.loads(
        Path(__file__).with_name("library-029-flow04-paired-intake.json").read_text(),
        parse_float=Decimal,
    )
    for member in reference["members"].values():
        source = member["components_kn_knm"]
        expected = member["expected_n_nmm"]
        assert len(source) == len(expected) == 6
        converted = [value * 1000 for value in source[:3]]
        converted += [value * 1000000 for value in source[3:]]
        assert converted == expected
        station_m = Decimal(member["station_mm"]) / 1000
        assert station_m * 1000 == member["station_mm"]
        assert 0 < member["station_mm"] < member["length_mm"]
    assert len(reference["combinations"]) == 4
    print("Independent FLOW04 reference: two members, four combinations each")


if __name__ == "__main__":
    main()
