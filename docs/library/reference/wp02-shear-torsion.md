# WP02 shear and torsion reference

WP02 publishes supplied-capacity FO05 and check operations AO07/AO08.

Shear capacity is qualified by local axis. It derives concrete strength from
the normalized Table 19 data, the limiting stress from Table 20, and transverse
capacity from the actual link diameter, active legs, spacing, and declared
grade. The output also checks minimum link provision and maximum spacing. A
provided-capacity request without an actual link is `not_evaluated`.

Shear checks retain the signed station demand while comparing its magnitude to
the capacity for the same axis. V2 and V3 may use different resisting widths,
effective depths, and active link legs.

Torsion accepts one identified `static_concurrent` or `staged_step` action row.
A component envelope is rejected because its shear, torsion, and bending values
may come from different source rows. The WP02 profile evaluates the major-axis
V2/M3 interaction for a solid rectangular beam. Nonzero V3/M2 interaction is
explicitly `not_applicable`; it is never ignored.

The torsion result checks equivalent shear, both equivalent bending faces,
section stress, actual closed-link area and spacing, and identified perimeter
corner bars. The selected perimeter must resolve left and right bars on both
the physical top and bottom faces inside the same closed link.
