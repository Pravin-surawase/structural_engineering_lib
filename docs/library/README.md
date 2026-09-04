# Structural engineering libraries

The reusable structural engineering product has native Python and .NET
implementations governed by the language-neutral artifacts in
`contracts/structural-engineering`. The library boundary owns typed engineering
inputs, calculations, checks, actual reinforcement geometry, deterministic
identity, diagnostics, and provenance. Application adapters may map Excel,
ETABS, HTTP, or UI data to this boundary, but do not own engineering formulas.

The first implementation milestone is WP01-WP08:

1. common contracts, reinforcement geometry, and flexure;
2. shear and torsion;
3. actions, topology, and bounded beam-line analysis;
4. serviceability;
5. anchorage, laps, curtailment, seismic, and arrangement checks;
6. project/profile and complete member design;
7. fabrication, quantities, cost, and calculation packages;
8. deterministic candidate ranking and optimization.

WP09 adds the standalone Windows Excel application over those same native .NET
operations: pure worksheet functions, versioned workbook commands, a sample,
signed per-user packaging, rollback/freshness, and installed performance
evidence. See the [Excel user and function reference](excel/README.md).

WP10-01 adds the portable AO16 ETABS import boundary to both libraries: strict
request, raw getter evidence, normalized analysis snapshots, canonical
identity, and offline validation. No CSI assembly, COM call, installed ETABS,
or Excel dependency enters the reusable packages.

See [Getting started](getting-started.md), [WP01 reference](reference/wp01-flexure.md),
[WP02 reference](reference/wp02-shear-torsion.md),
[WP03 reference](reference/wp03-actions-analysis-topology.md),
[WP04 reference](reference/wp04-serviceability.md),
[WP05 reference](reference/wp05-detailing-constructability.md),
[WP06 reference](reference/wp06-project-member-paths.md), and
[WP07 reference](reference/wp07-construction-calculation-package.md),
[WP08 reference](reference/wp08-beam-optimization.md),
[WP10-01 reference](reference/wp10-analysis-snapshot.md), plus
[migration guidance](migration/python-and-dotnet.md).
