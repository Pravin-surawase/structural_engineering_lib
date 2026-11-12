# WP02 shear and torsion reference

WP02 publishes supplied-capacity FO05 and check operations AO07/AO08.

Run the [typed beam checks example](../../../Python/examples/beam_checks_workflow.py)
with `python3 Python/examples/beam_checks_workflow.py` after installing the
current source build. Its shear and torsion calls declare actual bars, link
geometry, axis and concurrent actions; all states remain visible in the output.

Shear capacity is qualified by local axis. It derives concrete strength from
the normalized Table 19 data, the limiting stress from Table 20, and transverse
capacity from the actual link diameter, active legs, spacing, and declared
grade. The output also checks minimum link provision and maximum spacing. A
provided-capacity request without an actual link is `not_evaluated`.

Shear checks retain the signed station demand while comparing its magnitude to
the capacity for the same axis. V2 and V3 may use different resisting widths,
effective depths, and active link legs.

The shear batch requires every supplied capacity and demanded axis to qualify
before returning station checks. Across both axes, rejected input takes
precedence over unsupported scope, which takes precedence over missing
evidence. This priority is independent of capacity order. M45 concrete or
550 N/mm² link steel is outside the WP02 domain: both the capacity and batch
return `not_applicable`, `not_evaluated`, and `complete_for_scope`, retaining
`PROFILE.UNSUPPORTED`. The completeness describes the scope decision; it does
not qualify the design. A supported axis, including an assessed failure,
cannot turn a mixed unsupported batch into an evaluated PASS or FAIL.

Without an unsupported capacity, missing links or a missing demanded-axis
capacity return `unknown`, `not_evaluated`, and `partial` (HOLD). Unsupported
shear is also unevaluated (HOLD), and cannot satisfy the receiving-member
passing gate. The support-transfer caller retains that shear envelope and
reports its receiver-strength qualification as FAIL. Once every required
axis can be evaluated, the shear batch returns engineering PASS or FAIL
and retains each station's capacity result ID; stations sharing one capacity
continue to share that ID.

Torsion accepts one identified `static_concurrent` or `staged_step` action row.
A component envelope is rejected because its shear, torsion, and bending values
may come from different source rows. The WP02 profile evaluates the major-axis
V2/M3 interaction for a solid rectangular beam. Nonzero V3/M2 interaction is
explicitly `not_applicable`; it is never ignored.

The torsion result checks equivalent shear, the required equivalent bending faces,
section stress, actual closed-link area and spacing, and identified perimeter
corner bars. The selected perimeter must resolve left and right bars on both
the physical top and bottom faces inside the same closed link.

Under clause 41.4.2, the opposite face requires a tension check only when
`Mt > |Mu|`. A zero opposite equivalent moment does not invent a second
tension-steel requirement for compression/hanger bars. A positive opposite
moment still receives the full face-specific flexure check. This applies to
both signs of the supplied major-axis moment.

## Packet D corner geometry correction

For nonzero torsion, the operation resolves four aligned longitudinal corner
bars and derives `b1,d1` from their centres. It uses these values in the
Cl. 41.4.3 transverse reinforcement equation and retains the transverse
stirrup dimensions in the pitch limit. Missing or nonrectangular corner
geometry returns `not_evaluated`. Method
`is456-torsion-check-wp02-v3` identifies this source correction.
The response includes the derived corner dimensions and component demands.

Run the source-build station comparison with the public API.

```bash
python -m pip install ./Python
python Python/examples/torsion_station_reference.py
```

The 300 × 400 mm example has four Ø20 corner bars and concurrent
V2/M3/T = 60 kN / 15 kN·m / 15 kN·m. Two Ø8 legs at 100 mm pass;
at 125 mm they fail the required 0.914000831 mm²/mm. Both pitches are
below the 146 mm pitch maximum. The former use of the larger stirrup
rectangle understated this transverse demand.
[Independent reference](../../verification/library-027-torsion-station.json)

The example reports full-member admission HOLD and names the outstanding
support/load-path, tension-anchorage, physical-output and torsional SLS
obligations. The existing flexural crack method supplies flexural evidence.
Cl. 41 supplies torsional collapse checks. An admitted torsion member
also needs its traceable service method and acceptance criteria.
[Revised Packet D plan](../../planning/library-usability-improvement.md#packet-d-revised-work-order-and-evidence-boundary)
