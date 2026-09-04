# StructAutomate C# foundation

The Windows Excel product uses .NET 10 and Excel-DNA 1.9.0. This solution contains working force normalization, reinforcement geometry, bar-path quantities, planar beam analysis and candidate ranking. The [complete automation specification](../docs/planning/xll-product/automation/README.md) defines the member-design and ETABS workflow built on these components.

## Build and use

Run from `CSharp` with the .NET 10.0.400 SDK:

```powershell
dotnet restore StructAutomate.slnx --locked-mode
dotnet build StructAutomate.slnx -c Release --no-restore
dotnet test --project tests/StructAutomate.Tests/StructAutomate.Tests.csproj -c Release --no-build
dotnet run --project tools/StructAutomate.Examples -c Release --no-build -- beam examples/beam-line.json
dotnet run --project tools/StructAutomate.Examples -c Release --no-build -- benchmark
```

The packed add-in is `src/StructuralEngineering.ExcelDna/bin/Release/net10.0-windows/publish/StructuralEngineering.ExcelDna-AddIn64-packed.xll`. It contains its managed dependencies and requires 64-bit Windows Excel and the matching .NET 10 Desktop Runtime. The WP09 packaging scripts under `packaging/excel` create a signed, checksummed distribution and exercise per-user preflight, installation, repair, installed Excel acceptance, and uninstall. The solution does not connect to ETABS yet; the reusable native packages and standalone workbook implement the bounded WP01-WP08 beam workflow.

Worksheet examples:

```excel
=STR.INFO.VERSION()
=STR.REBAR.AREA(20)
=STR.REBAR.MASS_PER_LENGTH(20,7850)
=STR.IS456.DETAIL.DEVELOPMENT_LENGTH(A2)
```

Complex functions accept one strict `snake_case` JSON request and spill labelled result states, identities, provenance, output, and diagnostics. Blank cells produce a field error; an entered zero remains zero. Functions are pure and perform no model, workbook, file, process, network, or ETABS mutation. The four earlier `SA.*` names remain compatibility delegates. See the [Excel user and function reference](../docs/library/excel/README.md) and the shipped [20-member sample workbook](samples/StructAutomate-Standalone-Beam.xlsx).

## Contracts and boundaries

| Component | Working API | Meaning |
| --- | --- | --- |
| Contracts | Typed records and strict JSON | Explicit units, version 1.0.0, unknown fields rejected; constructor requirements retained |
| Application | `ForceNormalizer.Normalize` | Explicit source units to mm/kN/kNm; same-row signed P/V2/V3/T/M2/M3, both stations, axes and source identity retained |
| Engineering | `ReinforcementGeometry.Evaluate` | Area-weighted centroid/depth of one tension group; cover rectangle and uniform pairwise clear gap |
| Engineering | `QuantityCalculator.Calculate` | Resolved straight/arc bar lengths and mass; explicit net concrete and formwork faces; optional dated direct rates |
| Engineering | `BeamLineSolver.Solve` | Planar Euler–Bernoulli bending, prismatic elements, UDL and nodal forces/moments, springs and settlements |
| Application | `CandidateRanker.Rank` | Feasibility and deterministic minimum-objective ranking of evaluated candidates from one fixed analysis revision |
| Native optimization | `CandidateRankingOperations.Rank`, `BeamOptimizationOperations.Optimize` | Profile-derived complete evidence, bounded physical domains, fixed/coupled analysis semantics, and completeness-supported claims |

Compiled request types generate the five schemas in [schemas](schemas). Export after a deliberate contract change with `dotnet run --project tools/StructAutomate.Examples -c Release --no-build -- schemas schemas`. Schemas validate structure; engineering services validate values, geometry and identities. A schema-valid payload alone does not establish engineering suitability.

Forces stay in the supplied right-handed local basis. Normalization does not map axes to physical top/bottom faces or verify the supplied export hash against a live ETABS model. The acquisition adapter owns those observations. The native `StructuralEngineering.*` packages use the shared PF4 canonical JSON identity contract; the earlier `StructAutomate.*` schemas retain their existing .NET serialization identities.

The beam-line model has 2–201 ordered nodes, with one element per adjacent interval. Add nodes at point loads, stiffness changes and supports. Positive displacement/load is downward; rotation is dw/dx and reported moment is sagging-positive. Internal stiffness uses N and mm; API loads are kN, kNm and kN/m. UDL includes whatever self weight the caller selected; the solver adds none. Stations include requested positions, element ends and interior zero-shear points. Deflections include the exact prismatic UDL interior correction. Deflection extrema between requested stations are not automatically searched.

This linear bending model does not include shear deformation, axial/torsional response, internal hinges, nonlinearity, cracking/creep, load combinations or global-building effects. Those calculations require their own declared methods; the product specification defines associated inputs and checks.

Geometry fit here is a group calculation. Full member fit additionally evaluates opposing/side groups, horizontal versus vertical clearances, link bend corners and joints. Bar-path quantities assume tangent lengths and centreline arcs are already resolved; they do not infer development lengths or convert arbitrary shape dimensions. Concrete segments already account for overlap. Ranking does not calculate engineering checks: every required check must pass, and a missing or not-applicable required check remains unevaluated. Only a complete finite domain establishes enumeration completeness.

## Dependencies and architecture

`StructAutomate.Contracts` has no engineering formulas or host dependencies. `StructAutomate.Engineering` references those contracts and Math.NET Numerics, while `StructAutomate.Application` composes the earlier services. The reusable requirements-first implementation lives in the `StructuralEngineering.*` projects. `StructuralEngineering.ExcelDna` references the native operation packages and Excel-DNA; host effects enter only through its command/table/file adapters. Tests cover library behavior, strict Excel projection, workbook transactions, freshness, packaging, and native operation dispatch. CSI references belong in a later adapter project, keeping version and apartment constraints out of the pure kernel.

Versions are pinned in `global.json` and `Directory.Packages.props`; every project records resolved package content in its NuGet lock file. Runtime packages are Excel-DNA 1.9.0 and Math.NET Numerics 5.0.0. xUnit v3 4.0.0 uses Microsoft.Testing.Platform. WP08 implements bounded deterministic candidate enumeration and ranking directly, with no external optimization dependency. See [dependency decisions](dependencies.json).
