# WP03 actions, topology, and beam-line analysis

WP03 publishes three host-free operations. AO01 normalizes an immutable action
snapshot, AO15 defines beam topology, and AO02 solves a bounded planar beam
line. Excel and ETABS adapters can create these requests later; none of the
operations accesses either application.

## Action snapshots

`normalize_action_snapshot` / `ActionNormalizer.NormalizeSnapshot` accepts a
declared source, model, analysis epoch, result epoch, unit basis, right-handed
local axes, and one or more source rows. Each row retains its source row,
member, physical span, object, analysis element, object station, element
station, case, step, concurrency, and P/V2/V3/T/M2/M3 values.

The normalized boundary uses mm, N, and Nmm. Component and design envelopes
are preserved because that classification is evidence about the source row.
They do not thereby become concurrent action vectors suitable for an
interaction check. Each row and snapshot receives a deterministic PF4 semantic
identity.

## Beam topology

`define_beam_topology` / `BeamTopologyBuilder.Define` receives physical support
left faces, centrelines, and right faces. A physical span identifies its two
supports, effective depth, and section regions. Analysis elements separately
map analysis coordinates to that physical span.

Section regions and analysis mappings must cover each centreline span exactly,
without gaps or overlaps. The result reports centreline length, clear length,
and the design effective span:

```text
effective span = min(centreline span, clear span + effective depth)
```

The mapping is independent of load sign. It gives later design and detailing
operations a stable way to relate solver stations, support faces, section
changes, and physical spans.

## Bounded beam-line solver

`solve_beam_line` / `PlanarBeamSolver.SolveBeamLine` implements a linear
Euler-Bernoulli direct-stiffness model for local V2 displacement and M3
rotation. Its internal units and outputs are mm, N, Nmm, and radians. Positive
V2 force and displacement are upward, positive rotation is counterclockwise,
and positive M3 is sagging.

The profile supports 2 to 20 ordered nodes, prismatic elements between adjacent
nodes, vertical and rotational restraints, prescribed support displacement and
rotation, nodal forces and moments, uniform element loads, strictly interior
point loads, and 2 to 100 station intervals per element. Point-load stations
have explicit left and right shear rows. Results retain both analysis-element
and physical-span identities and include global and free-degree equilibrium
residuals.

The solver does not evaluate axial response, minor-axis response, torsion,
shear deformation, nonlinear response, a global frame, or a building model.
An unstable system is `rejected_input` with an analysis diagnostic. A successful
analysis has engineering state `not_evaluated` because analysis response is not
itself a design-code pass.

The conformance corpus includes a closed-form simply supported UDL response,
a point-load shear jump, prescribed support settlement, equilibrium, invalid
axes, invalid topology coverage, and unstable restraints.
