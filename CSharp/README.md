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

The packed add-in is `src/StructAutomate.Excel/bin/Release/net10.0-windows/publish/StructAutomate.Excel-AddIn64-packed.xll`. It contains managed dependencies and requires 64-bit Windows Excel and the matching .NET 10 Desktop Runtime. Compiler and numerical tests verify this build. Loading in Excel, installation/signing, workbook save/reopen and ETABS compatibility have separate application tests. The solution does not currently connect to ETABS or implement the full IS-code member design operations.

Worksheet examples:

```excel
=SA.VERSION()
=SA.BAR.MASS(20,6000,4,7850)
=SA.BEAM.SS.UDL(6000,10,25000,3125000000)
=SA.REBAR.GEOMETRY(300,500,25,8,25,"bottom",A2:C4)
```

`A2:C4` contains tension-group bar diameter, x from left and y from top, all in mm. Use one tension group per geometry call. Blank cells produce a field error; an entered zero remains zero. Array functions spill labelled results, so leave the output range clear. Functions are pure and perform no model, workbook or file mutations.

## Contracts and boundaries

| Component | Working API | Meaning |
| --- | --- | --- |
| Contracts | Typed records and strict JSON | Explicit units, version 1.0.0, unknown fields rejected; constructor requirements retained |
| Application | `ForceNormalizer.Normalize` | Explicit source units to mm/kN/kNm; same-row signed P/V2/V3/T/M2/M3, both stations, axes and source identity retained |
| Engineering | `ReinforcementGeometry.Evaluate` | Area-weighted centroid/depth of one tension group; cover rectangle and uniform pairwise clear gap |
| Engineering | `QuantityCalculator.Calculate` | Resolved straight/arc bar lengths and mass; explicit net concrete and formwork faces; optional dated direct rates |
| Engineering | `BeamLineSolver.Solve` | Planar Euler–Bernoulli bending, prismatic elements, UDL and nodal forces/moments, springs and settlements |
| Application | `CandidateRanker.Rank` | Feasibility and deterministic minimum-objective ranking of evaluated candidates from one fixed analysis revision |

Compiled request types generate the five schemas in [schemas](schemas). Export after a deliberate contract change with `dotnet run --project tools/StructAutomate.Examples -c Release --no-build -- schemas schemas`. Schemas validate structure; engineering services validate values, geometry and identities. A schema-valid payload alone does not establish engineering suitability.

Forces stay in the supplied right-handed local basis. Normalization does not map axes to physical top/bottom faces or verify the supplied export hash against a live ETABS model. The acquisition adapter owns those observations. Hashes identify these .NET-serialized records; they are not a cross-language canonical JSON standard.

The beam-line model has 2–201 ordered nodes, with one element per adjacent interval. Add nodes at point loads, stiffness changes and supports. Positive displacement/load is downward; rotation is dw/dx and reported moment is sagging-positive. Internal stiffness uses N and mm; API loads are kN, kNm and kN/m. UDL includes whatever self weight the caller selected; the solver adds none. Stations include requested positions, element ends and interior zero-shear points. Deflections include the exact prismatic UDL interior correction. Deflection extrema between requested stations are not automatically searched.

This linear bending model does not include shear deformation, axial/torsional response, internal hinges, nonlinearity, cracking/creep, load combinations or global-building effects. Those calculations require their own declared methods; the product specification defines associated inputs and checks.

Geometry fit here is a group calculation. Full member fit additionally evaluates opposing/side groups, horizontal versus vertical clearances, link bend corners and joints. Bar-path quantities assume tangent lengths and centreline arcs are already resolved; they do not infer development lengths or convert arbitrary shape dimensions. Concrete segments already account for overlap. Ranking does not calculate engineering checks: every required check must pass, and a missing or not-applicable required check remains unevaluated. Only a complete finite domain establishes enumeration completeness.

## Dependencies and architecture

`Contracts` has no engineering formulas or host dependencies. `Engineering` references Contracts and Math.NET Numerics. `Application` composes pure services. `Excel` references Application and Excel-DNA. Tests cover library behavior and Excel argument conversion; the command-line example runner references Application. CSI references belong in an adapter project, keeping version and apartment constraints out of the pure kernel.

Versions are pinned in `global.json` and `Directory.Packages.props`; package content is recorded by each `packages.lock.json`. Runtime packages are Excel-DNA 1.9.0 and Math.NET Numerics 5.0.0. xUnit v3 4.0.0 uses Microsoft.Testing.Platform. No optimization package is installed yet: finite candidate evaluation/ranking is deterministic, and a search engine should be added for a demonstrated search problem. See [dependency decisions](dependencies.json).
