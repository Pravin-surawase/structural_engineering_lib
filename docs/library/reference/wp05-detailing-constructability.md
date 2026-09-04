# WP05 detailing and constructability

WP05 publishes five reusable operations with matching Python and .NET
semantics. FO06 calculates development length. AO11 checks actual anchorage
paths. AO12 checks laps, mechanical splices, and bar curtailment. AO13 checks a
complete IS 13920 beam detailing context. AO26 checks the full reinforcement
arrangement and its construction fit. None of these operations accesses Excel,
ETABS, HTTP, or a UI host.

The code-data revisions are `is456-amd6-wp05-v1` and
`is13920-2016-amd2-wp05-v1`. The BIS record lists IS 456:2000 as reviewed in
2025 with six amendments. Amendment 6 changes the design bond stress for
fusion-bonded epoxy-coated deformed bars to 80 percent of the corresponding
deformed-bar value. The active BIS amendment listing records Amendment 2:2020
for IS 13920:2016. The normalized constants, source identity, and exclusions
are in `contracts/structural-engineering/code-data/is456/detailing-v1.json`.

Primary source records:

- [BIS IS 456:2000 standard details](https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6IkJqZmJUbm9GK1RlVHlZR1lLejA2VWc9PSIsInZhbHVlIjoiQ09wWjc1UVRxc1pVYlRka0o2RGtwdz09IiwibWFjIjoiMjJlMTFmYTBiNjRhMzNlOTBmYTk3ZjZkMWI2ZTE4ZTkzZGRmZjNjYjgwODg2NzY4Mzk0NDhlNGExOWNlYmI4NyIsInRhZyI6IiJ9)
- [BIS Amendment 6 to IS 456:2000](https://www.services.bis.gov.in/tmp/CED19013804_03062024_1.pdf)
- [BIS amendment listing for IS 13920](https://standardsbis.bsbedge.com/BIS_Amendments.aspx?parentid=13920_2016_AMD2_Reff2021&stdno=IS+13920)

## Development length and anchorage

`development_length` / `Detailing.DevelopmentLength` requires the actual bar
stress, steel strength, concrete grade, diameter, bar surface, tension or
compression state, and bundle size. It reports the plain-bar table value and
every applied modifier before returning:

```text
Ld = bar diameter * bar stress / (4 * design bond stress)
```

The bounded limit-state profile accepts bar stress up to `0.87 fy`. The
deformed-bar factor is 1.6; compression increases design bond stress by 25
percent; epoxy coating applies the Amendment 6 factor of 0.8 to the deformed
bar value. Bundles of two, three, and four bars apply length factors of 1.1,
1.2, and 1.33.

AO11 starts from a named physical critical section and follows the declared
bar direction to the actual path end. A support stores its near face and centre
as separate coordinates. Bend credit requires scheduled 45-degree increments,
is 4 bar diameters per 45 degrees, and is capped at 16 bar diameters. At a
simple support the operation evaluates `Ld <= M1/V + Lo` from a referenced
moment resistance, support shear, source action rows, and the actual anchorage
beyond the support centre.

## Laps, mechanical splices, and curtailment

AO12 receives actual bar marks and start/end stations together with a current
station steel-demand envelope. Tension laps use the greater of development
length and 30 bar diameters. Direct-tension laps use the greater of twice the
development length and 30 bar diameters. Compression laps use the greater of
compression development length and 24 bar diameters. Bars larger than 36 mm do
not qualify for a lap in this profile. Every splice also carries its percentage,
stagger group, and prohibited-zone comparison. A mechanical splice qualifies
only when both qualification and installation references are present.

Each curtailment records its theoretical cutoff, actual end, direction,
explicit required extension, continuing bar ids, and demand station. The
operation reconstructs the remaining steel area from those continuing bars.
Its anchorage result must identify AO11, while shear-at-cutoff and extra-link
evidence must identify the shear-check operation; an unrelated passing result
cannot satisfy either dependency. Extra-link evidence is conditional on the
explicit `extra_links_required` decision. The operation deliberately accepts the
required extension as a reviewed criterion rather than inventing a cutoff rule
from missing project or code context.

## Seismic beam detailing

AO13 first requires an explicit seismic applicability. An ordinary IS 456
member returns a complete not-applicable outcome for this seismic operation. An
IS 13920 member requires the system and design revision, both joint identities
and faces, actual top and bottom bar paths, link zones, splices, four anchorage
results bound to the left/right and top/bottom pairs, one dependent result bound
to each named joint, a shear result, imported analysis shear, probable end
moments, and provided shear capacity. Duplicate or unbound dependency results
are rejected instead of being counted as evidence for another face or joint.

The bounded profile checks 200 mm minimum width, width/depth greater than 0.3,
the minimum ratio `0.24 sqrt(fck)/fy`, a 2.5 percent maximum ratio at both faces,
at least two top and two bottom bars continuous across the clear span, and
closed 135-degree-hook link zones for `2d` from each joint face. End-zone
spacing is limited to the least of `d/4`, six times the smallest longitudinal
bar diameter, and 100 mm; the first hoop is limited to 50 mm from the joint
face.

Both probable sway directions are evaluated with the Amendment 2 capacity
factor of 1.4. The governing shear is the largest absolute imported shear or
either capacity-design case. A complete pass also needs the correctly typed,
current, complete shear, anchorage, and joint result references.

## Full reinforcement arrangement

AO26 receives every top, bottom, side, and corner role selected for the station,
plus all link cages. Supplying only the tension layer is incomplete. The
operation checks:

- cover from each concrete face to the surface of the outermost steel,
  including links;
- every bar circle inside the section and within a supplied link cage;
- pairwise bar overlap and all horizontally or vertically aligned clearances;
- horizontal clear distance against the larger bar diameter and aggregate size
  plus 5 mm;
- vertical clear distance against 15 mm, two-thirds aggregate size, and the
  larger bar diameter;
- physical row spacing after ordering layers by their y coordinates, so
  face-relative layer numbering cannot reverse the check;
- link bend space and closure;
- separate area-weighted centroids for every reinforcement role;
- bar and link clashes with resolved circular obstacles; and
- the selected cage against the supplied placement opening and sequence.

Valid geometry that violates a criterion is a completed engineering failure.
Missing actual bars, both longitudinal faces, joints, demand revisions, or a
required placement plan remains a partial unevaluated result. Malformed
identities, enums, or geometry are rejected input.

## Earlier-library corrections

The earlier scheduling helper remains available to its existing callers, but
WP05 does not reuse its simplified compliance path. That helper labels its bond
table as “Table 5.3,” includes an M15 deformed-bar value outside this profile,
copies tension development length into its compression schedule, rounds values
for schedules, and states that it does not generate curtailment schedules. Its
simple-support helper also derives support anchorage from a support width rather
than receiving resolved near-face, centre, bar path, and source action identity.

WP05 replaces those assumptions at the new semantic boundary. Conformance
vectors cover exact unrounded development length, the Amendment 6 epoxy case,
simple-support anchorage, a passing lap/curtailment schedule, a prohibited lap
zone, complete seismic capacity shear, full arrangement geometry, and the
incomplete tension-only arrangement.
