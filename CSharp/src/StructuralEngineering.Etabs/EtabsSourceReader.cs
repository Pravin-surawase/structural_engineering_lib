using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsSourceGap(string Operation, IReadOnlyList<object?> Inputs,
    string Code, string Message, EtabsInvocation? RawInvocation);
public sealed record EtabsSourceCapture(EtabsSourceFacts Facts, string ProtectedStateSha256,
    IReadOnlyList<EtabsRawGetterCall> Calls, IReadOnlyList<EtabsSourceGap> Gaps);

/// <summary>Native-unit definition capture. No force, setter, model-open, save, or analysis operation.</summary>
public static class EtabsSourceReader
{
    public static EtabsSourceCapture Read(IEtabsGetterHost host, EtabsSourceScope scope,
        DateTimeOffset deadlineUtc, CancellationToken token = default)
    {
        EtabsSourceQualification.ValidateScope(scope);
        var observed = new ObservedHost(host);
        var adapter = new EtabsGetterAdapter(observed, EtabsSourceGetterMatrix.Allowed);
        var calls = new List<EtabsRawGetterCall>();
        var gaps = new List<EtabsSourceGap>();
        var cache = new Dictionary<string, EtabsRawGetterCall?>(StringComparer.Ordinal);
        var protectedCalls = new List<EtabsRawGetterCall>();
        EtabsRawGetterCall? Get(string operation, object?[] inputs, bool required = false)
        {
            token.ThrowIfCancellationRequested();
            var key = operation + JsonSerializer.Serialize(inputs);
            if (cache.TryGetValue(key, out var cached)) return cached;
            observed.Last = null;
            var result = adapter.Read(operation, inputs, deadlineUtc, token);
            if (result.RawCall is null)
            {
                if (required || result.DiagnosticCode is "ETABS.CALL_TIMEOUT" or "ETABS.IDENTITY_DRIFT")
                    throw new InvalidOperationException($"{operation}: {result.DiagnosticCode}: {result.Message}");
                gaps.Add(new(operation, inputs, result.DiagnosticCode ?? "ETABS.CALL_FAILED", result.Message ?? "Unavailable getter.", observed.Last));
                cache.Add(key, null); return null;
            }
            var call = result.RawCall with { GetterMatrixSha256 = EtabsSourceGetterMatrix.Sha256 };
            calls.Add(call); protectedCalls.Add(call); cache.Add(key, call); return call;
        }

        var model = Get("SapModel.GetModelFilename", [true], true)!;
        if (!string.Equals(Path.GetFullPath((string)model.DirectValue!), Path.GetFullPath(host.Identity.ModelPath), StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Live model differs from the bound saved source.");
        var present = (int)Get("SapModel.GetPresentUnits", [], true)!.DirectValue!;
        var database = (int)Get("SapModel.GetDatabaseUnits", [], true)!.DirectValue!;
        var units = EtabsSourceQualification.Units(present, database);
        Get("SapModel.GetModelIsLocked", [], true); Get("SapModel.GetVersion", [], true);
        var frameCount = (int)Get("FrameObj.Count", ["All"], true)!.DirectValue!;
        if (frameCount is < 1 or > 20_000) throw new InvalidOperationException("Source table capture requires a model with 1..20000 frames.");
        Get("DatabaseTables.GetAllTables", [], true);
        var tables = new Dictionary<string, EtabsBulkTable>(StringComparer.Ordinal);
        foreach (var spec in new[] { new EtabsBulkTableSpec("Frame Assignments - Material Overwrites", true, 1, "UniqueName"),
            EtabsBulkTable.Specifications.Single(s => s.Key == "Objects and Elements - Frames") })
        {
            var key = spec.Key;
            var metadata = Get("DatabaseTables.GetAllFieldsInTable", [key]);
            if (metadata is null) continue;
            var data = spec.Editing ? Get("DatabaseTables.GetTableForEditingArray", [key, "All"]) :
                Get("DatabaseTables.GetTableForDisplayArray", [key, new[] { "ElmName", "ObjType", "ObjName", "ElmJtI", "ElmJtJ" }, "All"]);
            if (data is null) continue;
            var shift = spec.Editing ? 0 : 1;
            if ((int)data.Outputs[shift + 2]! > 200_000 || Array<string>(data, shift + 3).Length > 1_000_000)
                throw new InvalidOperationException("Source assignment/mapping table exceeds 200000 records or 1000000 cells; no partial table is accepted.");
            try { tables.Add(key, new(spec, JsonSerializer.SerializeToElement(metadata.Outputs), JsonSerializer.SerializeToElement(data.Outputs))); }
            catch (InvalidDataException exception) { gaps.Add(new("source table " + key, [key], "SOURCE.TABLE_SCHEMA_UNQUALIFIED", exception.Message, null)); }
        }
        var mappings = tables.TryGetValue("Objects and Elements - Frames", out var mappingTable)
            ? mappingTable.Rows.GroupBy(row => row.Value.Required("ObjName"), StringComparer.Ordinal).ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal)
            : new Dictionary<string, KeyValuePair<string, EtabsBulkTable.Row>[]>(StringComparer.Ordinal);
        var statuses = Get("Analyze.GetCaseStatus", [], true)!;
        Get("Analyze.GetRunCaseFlag", [], true);
        var caseStates = Array<string>(statuses, 1).Zip(Array<int>(statuses, 2))
            .ToDictionary(p => p.First, p => p.Second, StringComparer.Ordinal);
        var points = new Dictionary<string, EtabsSourcePoint>(StringComparer.Ordinal);
        var materials = new Dictionary<string, EtabsSourceMaterial>(StringComparer.Ordinal);
        var members = scope.FrameNames.Select(Member).ToArray();
        var loadNodes = new Dictionary<string, EtabsSourceLoadNode>(StringComparer.Ordinal);
        foreach (var name in scope.CaseNames) Load("case", name);
        foreach (var name in scope.CombinationNames) Load("combination", name);
        var facts = new EtabsSourceFacts(EtabsSourceQualification.SchemaVersion, units, scope, members,
            points.Values.OrderBy(p => p.Name, StringComparer.Ordinal).ToArray(),
            materials.Values.OrderBy(m => m.Name, StringComparer.Ordinal).ToArray(),
            loadNodes.Values.OrderBy(n => EtabsSourceQualification.Id(n.Kind, n.Name), StringComparer.Ordinal).ToArray(),
            EtabsSourceQualification.ResolveLoads(scope, loadNodes.Values.ToArray()),
            "source_definitions_only;applied_loads=not_read;physical_supports=unqualified;force_stations=not_read;design=not_evaluated;Fc_is_not_IS_fck",
            tables.Values.Select(t => new EtabsSourceTableSummary(t.Key, 1, t.SourceRowCount, t.Rows.Count, t.ContextOnlyRowCount)).ToArray());

        foreach (var before in protectedCalls)
        {
            var after = adapter.Read(before.Operation, before.Inputs, deadlineUtc, token).RawCall;
            if (after is null || Shape(before) != Shape(after))
                throw new InvalidOperationException($"Protected source fact changed or became unavailable: {before.Operation}.");
            calls.Add(after with { GetterMatrixSha256 = EtabsSourceGetterMatrix.Sha256 });
        }
        var finalModel = adapter.Read("SapModel.GetModelFilename", [true], deadlineUtc, token).RawCall;
        if (finalModel is null || Shape(model) != Shape(finalModel)) throw new InvalidOperationException("Live model changed at final source postflight.");
        calls.Add(finalModel with { GetterMatrixSha256 = EtabsSourceGetterMatrix.Sha256 });
        var digest = Convert.ToHexStringLower(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(
            protectedCalls.Select(c => new { c.Operation, c.Inputs, Shape = Shape(c) }))));
        return new(facts, digest, calls, gaps);

        EtabsSourceMember Member(string name)
        {
            var restrictions = new List<EtabsSourceRestriction>();
            var subjects = new HashSet<string>(StringComparer.Ordinal) { name };
            void Restrict(string code, string message) => restrictions.Add(new(code, name, message));
            var label = Get("FrameObj.GetLabelFromName", [name]);
            var orientation = Value<int>(Get("FrameObj.GetDesignOrientation", [name]), 0);
            var sectionCall = Get("FrameObj.GetSection", [name]);
            var section = Text(sectionCall, 0); var auto = Text(sectionCall, 1);
            var endpointsCall = Get("FrameObj.GetPoints", [name]);
            var endpoints = endpointsCall is null ? [] : endpointsCall.Outputs.Cast<string>().ToArray();
            foreach (var point in endpoints) { subjects.Add(point); Point(point); }
            Get("FrameObj.GetModifiers", [name]);
            var offsets = Get("FrameObj.GetEndLengthOffset", [name]);
            var insertion = Get("FrameObj.GetInsertionPoint_1", [name]);
            var releases = Get("FrameObj.GetReleases", [name]);
            var axes = Get("FrameObj.GetLocalAxes", [name]);
            var assignments = new EtabsSourceAssignments(Value<bool>(offsets, 0), Length(offsets, 1), Length(offsets, 2), Value<double>(offsets, 3),
                Value<int>(insertion, 0), Value<bool>(insertion, 1), Value<bool>(insertion, 2), Value<bool>(insertion, 3), Text(insertion, 6),
                LengthArray(insertion, 4), LengthArray(insertion, 5), OptionalArray<bool>(releases, 0), OptionalArray<bool>(releases, 1),
                OptionalArray<double>(releases, 2), OptionalArray<double>(releases, 3), Value<double>(axes, 0), Value<bool>(axes, 1));
            if (assignments.AdvancedLocalAxes == true) Restrict("SOURCE.ADVANCED_AXES_UNQUALIFIED", "Advanced frame axes are retained without physical-face interpretation.");
            if (assignments.AutomaticEndOffsets == true) Restrict("SOURCE.AUTO_OFFSETS_UNQUALIFIED", "Automatic offsets do not establish qualified physical support faces.");
            if (orientation != 2) Restrict("SOURCE.NOT_BEAM", "Source design orientation is not beam; no name-based role inference.");
            string? sectionMaterial = null, effectiveMaterial = null;
            int? sectionType = null; double? width = null, depth = null;
            string? overwrite = null;
            var materialBasis = "overwrite_table_unavailable";
            var overwriteTableAvailable = tables.TryGetValue("Frame Assignments - Material Overwrites", out var overwriteTable);
            if (overwriteTableAvailable)
            {
                overwrite = overwriteTable!.Rows.TryGetValue(name, out var row) ? row.Optional("Material") : null;
                materialBasis = overwriteTable.Rows.ContainsKey(name) ? "explicit_material_overwrite_table_row" : "complete_material_overwrite_table_has_no_object_row";
                if (overwriteTable.Rows.ContainsKey(name) && string.IsNullOrWhiteSpace(overwrite))
                    materialBasis = "blank_material_overwrite_row_unqualified";
            }
            if (!string.IsNullOrWhiteSpace(section))
            {
                subjects.Add(section);
                sectionType = Value<int>(Get("PropFrame.GetTypeOAPI", [section]), 0);
                sectionMaterial = Text(Get("PropFrame.GetMaterial", [section]), 0);
                Get("PropFrame.GetModifiers", [section]);
                if (sectionType == 8)
                {
                    var rectangle = Get("PropFrame.GetRectangle", [section]);
                    depth = Length(rectangle, 2); width = Length(rectangle, 3);
                    if (rectangle is not null && Text(rectangle, 1) != sectionMaterial)
                        Restrict("SOURCE.MATERIAL_CONFLICT", "Section shape and material getter disagree.");
                }
                else Restrict("SOURCE.SECTION_UNQUALIFIED", "Only rectangular section dimensions are projected by this source profile; the source type is retained.");
            }
            if (!string.IsNullOrWhiteSpace(sectionMaterial)) { subjects.Add(sectionMaterial); Material(sectionMaterial); }
            if (!string.IsNullOrWhiteSpace(overwrite))
            {
                subjects.Add(overwrite); var material = Material(overwrite);
                if (material.MaterialType is not null) effectiveMaterial = overwrite;
            }
            else if (materialBasis == "complete_material_overwrite_table_has_no_object_row" && sectionMaterial is not null && materials.TryGetValue(sectionMaterial, out var declared) && declared.MaterialType is not null)
                effectiveMaterial = sectionMaterial;
            if (effectiveMaterial is null) Restrict("SOURCE.MATERIAL_OVERWRITE_UNRESOLVED", "The complete overwrite table and material getters do not establish an effective material identity; retain the section material without assuming an undocumented sentinel.");
            if (width is <= 0 || depth is <= 0) Restrict("SOURCE.SECTION_DIMENSION_INVALID", "Source section dimensions are not positive.");
            var elements = new List<EtabsSourceElement>();
            if (mappings.TryGetValue(name, out var mapped))
            {
                if (mapped.Length > 200)
                    Restrict("SOURCE.ELEMENT_MAPPING_UNAVAILABLE", "Element identities exceed the 200-per-frame bound or are not unique/nonblank; no element getters were issued.");
                else foreach (var mapping in mapped)
                {
                    var id = mapping.Key;
                    subjects.Add(id);
                    var reverse = Get("LineElm.GetObj", [id]); var elementPoints = Get("LineElm.GetPoints", [id]);
                    var pointI = mapping.Value.Required("ElmJtI"); var pointJ = mapping.Value.Required("ElmJtJ");
                    elements.Add(new(id, Text(reverse, 0), Value<int>(reverse, 1), Value<double>(reverse, 2), Value<double>(reverse, 3),
                        pointI, pointJ, OptionalArray<double>(Get("LineElm.GetTransformationMatrix", [id]), 0), "Objects and Elements - Frames/v1"));
                    if (reverse is null || Text(reverse, 0) != name || Text(elementPoints, 0) != pointI || Text(elementPoints, 1) != pointJ)
                        Restrict("SOURCE.ELEMENT_MAPPING_CONFLICT", "Mapping table and reverse object/element ownership or endpoint identities disagree.");
                }
            }
            if (elements.Count == 0) Restrict("SOURCE.ELEMENT_MAPPING_UNAVAILABLE", "No accepted analysis-element mappings are available.");
            Restrict("SOURCE.ELEMENT_COORDINATE_SEMANTICS_UNQUALIFIED", "RDI/RDJ are preserved as provider coordinates; their unit/relative-distance semantics are not inferred from undocumented names.");
            var stationCall = Get("FrameObj.GetOutputStations", [name]);
            EtabsSourceStations? stations = stationCall is null ? null : new((int)stationCall.Outputs[0]!, (double)stationCall.Outputs[1]!,
                Length(stationCall, 1)!.Value, (int)stationCall.Outputs[2]!, (bool)stationCall.Outputs[3]!, (bool)stationCall.Outputs[4]!);
            if (stations is not null && (stations.Type is not (1 or 2) || stations.Type == 1 && stations.MaximumSpacingMm <= 0 || stations.Type == 2 && stations.MinimumStations < 2))
                Restrict("SOURCE.STATION_SETTINGS_INVALID", "Configured output station type/spacing/count is outside its documented range.");
            foreach (var point in endpoints)
                if (points[point].GlobalCoordinatesMm is null || points[point].LocalRestraints is null || points[point].GlobalTransformation is null)
                    Restrict("SOURCE.ENDPOINT_UNAVAILABLE", "An endpoint coordinate, restraint or axis fact is unavailable.");
            restrictions.AddRange(gaps.Where(g => g.Inputs.OfType<string>().Any(subjects.Contains))
                .Select(g => new EtabsSourceRestriction("SOURCE.GETTER_UNAVAILABLE", name, g.Operation + ": " + g.Code)));
            Restrict("SOURCE.PHYSICAL_SUPPORT_UNQUALIFIED", "Endpoint connectivity, restraints and releases are source facts; physical support faces and spans require a separate interpretation profile.");
            return new(name, Text(label, 1), orientation, section, sectionType, auto, sectionMaterial, overwrite, effectiveMaterial,
                width, depth, endpoints, elements, stations, assignments, restrictions.Distinct().ToArray(), materialBasis);
        }

        void Point(string name)
        {
            if (points.ContainsKey(name)) return;
            var coordinate = Get("PointObj.GetCoordCartesian", [name, "Global"]);
            var native = coordinate?.Outputs.Cast<double>().ToArray();
            var connections = Get("PointObj.GetConnectivity", [name]);
            var ids = Array<string>(connections, 2); var kinds = Array<int>(connections, 1); var numbers = Array<int>(connections, 3);
            points.Add(name, new(name, native, native?.Select(v => EtabsSourceQualification.ConvertFinite(v, units.LengthToMm)).ToArray(),
                OptionalArray<bool>(Get("PointObj.GetRestraint", [name]), 0),
                OptionalArray<double>(Get("PointObj.GetTransformationMatrix", [name, true]), 0),
                ids.Select((id, i) => new EtabsSourceConnection(kinds[i], id, numbers[i])).ToArray()));
        }

        EtabsSourceMaterial Material(string name)
        {
            if (materials.TryGetValue(name, out var existing)) return existing;
            var kind = Value<int>(Get("PropMaterial.GetTypeOAPI", [name]), 0);
            var elastic = kind is null ? null : Get("PropMaterial.GetMPIsotropic", [name, 0d]);
            var concrete = kind == 2 ? Get("PropMaterial.GetOConcrete", [name, 0d]) : null;
            var result = new EtabsSourceMaterial(name, kind, Value<double>(elastic, 0), Stress(elastic, 0),
                Value<double>(concrete, 0), Stress(concrete, 0), Value<bool>(concrete, 1));
            materials.Add(name, result); return result;
        }

        void Load(string kind, string name)
        {
            var id = EtabsSourceQualification.Id(kind, name);
            if (loadNodes.ContainsKey(id)) return;
            if (loadNodes.Count >= EtabsSourceQualification.MaximumNodes) throw new InvalidOperationException("Source graph exceeds 500 nodes.");
            // Reserve before recursion, retaining cycles for the pure closure evaluator.
            loadNodes.Add(id, new(kind, name, null, null, null, null, [], []));
            var restrictions = new List<EtabsSourceRestriction>();
            var terms = new List<EtabsSourceLoadTerm>();
            int? providerType = null, status = null, subtype = null; bool? selected = null; string? initial = null; double? selfWeight = null;
            if (kind == "case")
            {
                var type = Get("LoadCases.GetTypeOAPI", [name]); providerType = Value<int>(type, 0); subtype = Value<int>(type, 1);
                status = caseStates.TryGetValue(name, out var observedStatus) ? observedStatus : null;
                selected = Value<bool>(Get("Results.Setup.GetCaseSelectedForOutput", [name]), 0);
                if (providerType == 1)
                {
                    initial = Text(Get("LoadCases.StaticLinear.GetInitialCase", [name]), 0);
                    var loads = Get("LoadCases.StaticLinear.GetLoads", [name]);
                    var names = Array<string>(loads, 2); var types = Array<string>(loads, 1); var factors = Array<double>(loads, 3);
                    for (var i = 0; i < names.Length; i++) terms.Add(new(types[i] == "Load" ? "pattern" : "unqualified:" + types[i], names[i], factors[i]));
                }
            }
            else if (kind == "combination")
            {
                providerType = Value<int>(Get("RespCombo.GetTypeOAPI", [name]), 0);
                selected = Value<bool>(Get("Results.Setup.GetComboSelectedForOutput", [name]), 0);
                var list = Get("RespCombo.GetCaseList", [name]);
                var names = Array<string>(list, 2); var kinds = Array<int>(list, 1); var factors = Array<double>(list, 3);
                for (var i = 0; i < names.Length; i++) terms.Add(new(kinds[i] == 0 ? "case" : kinds[i] == 1 ? "combination" : "unqualified:" + kinds[i], names[i], factors[i]));
            }
            else if (kind == "pattern")
            {
                providerType = Value<int>(Get("LoadPatterns.GetLoadType", [name]), 0);
                selfWeight = Value<double>(Get("LoadPatterns.GetSelfWTMultiplier", [name]), 0);
            }
            if (terms.Count > EtabsSourceQualification.MaximumTerms) throw new InvalidOperationException("Source node exceeds 500 dependency terms.");
            restrictions.AddRange(gaps.Where(g => g.Operation.StartsWith(kind == "combination" ? "RespCombo." : kind == "pattern" ? "LoadPatterns." : "LoadCases.", StringComparison.Ordinal) && g.Inputs.Contains(name))
                .Select(g => new EtabsSourceRestriction("SOURCE.DEFINITION_UNAVAILABLE", id, g.Operation + ": " + g.Code)));
            loadNodes[id] = new(kind, name, providerType, status, selected, initial, terms, restrictions, selfWeight, subtype);
            foreach (var term in terms) Load(term.Kind, term.Name);
            if (kind == "case" && !string.IsNullOrWhiteSpace(initial) && initial != "None") Load("case", initial);
        }

        double? Length(EtabsRawGetterCall? call, int index) => Scale(call, index, units.LengthToMm);
        double? Stress(EtabsRawGetterCall? call, int index) => Scale(call, index, units.StressToNPerMm2);
        double[]? LengthArray(EtabsRawGetterCall? call, int index) => OptionalArray<double>(call, index)?
            .Select(v => EtabsSourceQualification.ConvertFinite(v, units.LengthToMm)).ToArray();
    }

    private static double? Scale(EtabsRawGetterCall? call, int index, double factor) => Value<double>(call, index) is double value ? EtabsSourceQualification.ConvertFinite(value, factor) : null;
    private static string? Text(EtabsRawGetterCall? call, int index) => call?.Outputs[index] as string;
    private static T? Value<T>(EtabsRawGetterCall? call, int index) where T : struct => call?.Outputs[index] is T value ? value : null;
    private static T[] Array<T>(EtabsRawGetterCall? call, int index) => call?.Outputs[index] is System.Array array ? array.Cast<T>().ToArray() : [];
    private static T[]? OptionalArray<T>(EtabsRawGetterCall? call, int index) => call is null ? null : Array<T>(call, index);
    private static string Shape(EtabsRawGetterCall call) => JsonSerializer.Serialize(new { call.DirectValue, call.Outputs, call.CsiReturnCode });

    private sealed class ObservedHost(IEtabsGetterHost inner) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity => inner.Identity;
        public EtabsInvocation? Last { get; set; }
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token) => Last = inner.Invoke(definition, inputs, token);
        public void Dispose() { }
    }
}
