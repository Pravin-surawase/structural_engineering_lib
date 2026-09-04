# WP06 project, complete member, and reinforcement paths

WP06 publishes three reusable operations with matching Python and .NET
semantics. AO14 creates an immutable project and design profile. AO17
aggregates the profile-derived complete member result. AO18 resolves every
physical reinforcement bar into exact tangent straights and bend arcs. These
operations are host-free: Excel, ETABS, HTTP, storage, and rendering remain
adapters around the library.

The language-neutral signatures and optional-field rules are defined in
`contracts/structural-engineering/schemas/wp06.schema.json`. Every optional
value is represented explicitly by a nullable field or an empty array. Zero is
always a supplied number, never a missing value.

## AO14: create a beam project

`create_beam_project` / `BeamProjectOperations.Create` receives:

- immutable project id, name, and revision;
- the canonical `mm`, `N`, `Nmm`, and `N/mm2` unit basis;
- named code-data revisions and optional catalogue revisions, each with its
  source reference;
- an immutable profile id and revision, selected design code, and ordinary IS
  456 or IS 13920 seismic profile;
- uniquely named design criteria with values, units, and sources; and
- required-check rules containing the operation semantic id, topology scope,
  expected applicability, source, and optional code-data binding.

An ordinary profile must include exactly one seismic rule marked
`not_applicable`; an IS 13920 profile must include it as `applicable`. The
operation rejects missing revisions, unsupported unit bases, duplicate or
conflicting rules, unknown code-data bindings, and criteria without units or
sources. A valid request returns a deterministic `project_basis_id` derived
from the complete normalized request.

```python
from structural_lib.beam import (
    ApplicabilityState,
    BeamDesignProfile,
    BeamProjectDefinition,
    BeamProjectRequest,
    CheckScope,
    DesignCheckRule,
    DesignCriterion,
    RevisionBinding,
    SeismicDesignProfile,
    StructuralUnitBasis,
    create_beam_project,
)

request = BeamProjectRequest(
    BeamProjectDefinition("P1", "Office beams", "project-r1"),
    StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
    (RevisionBinding("is456", "is456-r1", "approved code-data set"),),
    BeamDesignProfile(
        "ordinary-beam",
        "profile-r1",
        "IS 456:2000",
        SeismicDesignProfile.ORDINARY_IS456,
        (
            DesignCheckRule(
                "flexure",
                "is456.beam.flexure.check/v1",
                CheckScope.MEMBER,
                ApplicabilityState.APPLICABLE,
                "project design basis",
                "is456",
            ),
            DesignCheckRule(
                "seismic",
                "is456.beam.seismic_detailing.check/v1",
                CheckScope.MEMBER,
                ApplicabilityState.NOT_APPLICABLE,
                "ordinary frame profile",
                "is456",
            ),
        ),
        (DesignCriterion("nominal-cover", 25, "mm", "durability basis"),),
    ),
)
result = create_beam_project(request)
assert result.engineering == "pass"
```

## AO17: design a complete member

AO17 does not accept a caller-provided list of required check names. It derives
the expected leaves from the frozen project rules and supplied topology scope
instances. A member rule creates one member leaf; a station, span, face, axis,
bar-end, or arrangement rule creates one leaf for every supplied instance of
that scope. The stable leaf id is `<rule_id>@<scope_id>`.

Each leaf evidence record retains its operation and result identities,
execution, applicability, engineering, completeness and freshness states,
code-data and method revisions, normalized-input and calculation identities,
diagnostic codes, optional required/selected/supplied values, unit, and
governing utilization. A profile-expected not-applicable leaf qualifies only
when it is completed, complete, current, and carries the exact operation and
revision binding with engineering state `not_evaluated`.

The aggregate remains partial and not evaluated when a required leaf is
missing, rejected, cancelled, unsupported, not evaluated, incomplete, stale,
unbound, bound to the wrong operation or code-data revision, or has the wrong
applicability. A current complete leaf failure produces a complete member
engineering failure. Partial and stale evidence remains in the output but
cannot become the governing utilization.

Effective-depth iteration is also explicit. Iterations are sequential and bind
the calculated depth to the dependent result ids and reinforcement revision.
The member qualifies only when the final iteration is converged against the
current physical reinforcement revision.

## AO18: resolve reinforcement paths

AO18 uses a named member-local coordinate contract:

- `member_station_x` along the physical member;
- `section_x_from_left` across the section; and
- `section_y_from_top` down the section.

Every physical bar has its own id, mark, role, layer, diameter, steel grade,
bundle size, ordered nodes, anchorage requirement ids, and splice ids. Open
paths need at least two nodes. Closed paths, including links, need at least
three. Every direction change requires a positive centreline bend radius and
a bend kind: standard bend, hook, or transition.

The resolver replaces each sharp vertex with exact incoming and outgoing
tangent points and a circular centreline arc. It reports segment ids, endpoints,
bend centre, radius, angle, member-local plane normal, and positive sweep about
that normal. The normal is the unit cross product of the incoming and outgoing
path directions. The output also retains unrounded centreline length. It rejects zero
edges, 180-degree reversals, bend data on an open endpoint, bend data on a
collinear node, missing bend evidence, and overlapping adjacent tangencies.
Closed paths are continuous through their final-to-first edge.

Bars may share one mark only when their fabrication geometry, ordered relative
bend planes, role, diameter, grade, bundle, and closed/open state match within
the declared geometry tolerance. This comparison is invariant to translation
and rigid rotation, while different multi-plane shapes receive different
marks. Their physical positions can differ. AO18 reports the smallest
available stock length that can contain each developed centreline path. A path
that exceeds every stock length is a completed engineering failure. Cutting,
offcut allocation, bend allowances for fabrication schedules, BBS rows,
quantities, and costing are produced from these paths in WP07.

```python
from structural_lib.beam import (
    BarPathRequest,
    BarPathRole,
    BarPathSeed,
    BendKind,
    MemberLocalCoordinateSystem,
    PathNode,
    PathPoint,
    resolve_bar_paths,
)

bar = BarPathSeed(
    "B1-T1",
    "T1",
    BarPathRole.TOP_LONGITUDINAL,
    1,
    20,
    415,
    (
        PathNode("N1", PathPoint(0, 50, 50)),
        PathNode("N2", PathPoint(1000, 50, 50), 100, BendKind.HOOK),
        PathNode("N3", PathPoint(1000, 50, 250)),
    ),
)
request = BarPathRequest(
    "ordinary-beam",
    "project-basis-r1",
    "criteria-r1",
    "B1",
    "SPAN-1",
    "topology-r1",
    "detail-r1",
    MemberLocalCoordinateSystem(
        "B1-local",
        "member_station_x",
        "section_x_from_left",
        "section_y_from_top",
    ),
    0,
    6000,
    300,
    500,
    (bar,),
    (12000,),
)
result = resolve_bar_paths(request)
assert result.outputs["reinforcement_schedule"]["paths"][0][
    "developed_centreline_length_mm"
] > 0
```

## Earlier-library corrections

The older candidate evaluator and visualization helpers infer reinforcement as
full-span straight lines and can copy a single-layer required-area selection
across the member. Those representations cannot establish anchorage, cutoff,
lap, hook, transition, link closure, fabrication length, or mark equivalence.
WP06 keeps each physical path and its dependent detail identities explicit.

The earlier design flow also allowed the application to pass a list of checks.
That makes completeness depend on the caller remembering every applicable
leaf. WP06 moves the required-check set into the versioned design profile and
derives its scope instances from frozen topology evidence. The complete-member
result therefore shows every required, failed, inapplicable, missing, partial,
or stale leaf instead of silently dropping it.
