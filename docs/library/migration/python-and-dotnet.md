# Python and .NET migration

Existing Python APIs remain available. New requirements-first work should call
the semantic operations under `structural_lib.beam`; compatibility wrappers may
translate older scalar inputs only when physical meaning is unambiguous.

The corresponding .NET namespaces begin with `StructuralEngineering.*`.
`StructuralEngineering.ExcelDna` is the canonical Windows Excel adapter over
those packages. The earlier `StructAutomate.Excel` project has been replaced;
its four `SA.*` worksheet names remain compatibility delegates in the canonical
XLL. Application code should move by semantic operation identifier rather than
by similarly named helper.

Migration requires callers to resolve previously implicit information:

- `span` becomes a declared clear, effective, physical, or analysis length;
- `steel area` becomes required, provided, selected, or scheduled steel;
- bars carry physical face, coordinates, layer, diameter, and identifier;
- density and other defaults carry their origin and revision;
- bending demands retain their signs while face selection stays physical;
- results retain independent execution, applicability, engineering,
  completeness, freshness, and approval states.

Do not convert a rejected or unsupported calculation into a false engineering
failure or pass. Persist the semantic ID, normalized input ID, calculation ID,
code-data revision, and diagnostics with every migrated result.
