using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsTopologyCapture(EtabsSourceCapture SourceCapture, EtabsTopologyGeometry Geometry,
    EtabsTopologyFacts Facts, string ProtectedStateSha256, IReadOnlyList<EtabsRawGetterCall> Calls,
    IReadOnlyList<EtabsSourceGap> Gaps, IReadOnlyList<EtabsSourceTableSummary> Tables);

public static class EtabsTopologyReader
{
    public static EtabsTopologyCapture Read(IEtabsGetterHost host, EtabsSourceScope scope,
        DateTimeOffset deadlineUtc, CancellationToken token = default)
    {
        EtabsSourceQualification.ValidateScope(scope);
        var source = EtabsSourceReader.Read(host, scope, deadlineUtc, token);
        var observed = new ObservedHost(host);
        var adapter = new EtabsGetterAdapter(observed, EtabsTopologyGetterMatrix.Allowed);
        var before = source.Calls.GroupBy(Key, StringComparer.Ordinal).Select(g => g.First() with
        { GetterMatrixSha256 = EtabsTopologyGetterMatrix.Sha256 }).ToList();
        var cache = before.ToDictionary(Key, c => (EtabsRawGetterCall?)c, StringComparer.Ordinal);
        var gaps = new List<EtabsSourceGap>();
        var units = source.Facts.Units;
        var points = source.Facts.Points.ToDictionary(p => p.Name, p => new EtabsTopologyPoint(p.Name, p.GlobalCoordinatesMm), StringComparer.Ordinal);
        var frames = new Dictionary<string, EtabsTopologyFrame>(StringComparer.Ordinal);
        var areas = new Dictionary<string, EtabsTopologyArea>(StringComparer.Ordinal);
        var analysisPoints = new Dictionary<string, EtabsTopologyPoint>(StringComparer.Ordinal);
        var sourceMembers = source.Facts.Members.ToDictionary(m => m.Name, StringComparer.Ordinal);
        var connections = source.Facts.Points.SelectMany(p => p.Connections)
            .Where(c => c.ObjectType is 2 or 5).Select(c => (c.ObjectType, c.ObjectName)).Distinct().ToArray();
        if (connections.Count(c => c.ObjectType != 2 || !scope.FrameNames.Contains(c.ObjectName, StringComparer.Ordinal)) > EtabsTopologyQualification.MaximumAdjacentObjects)
            throw new InvalidOperationException("Connected geometry exceeds the 200-object bound; no partial topology is accepted.");
        var inventory = Get("FrameObj.GetAllFrames", ["Global"], true)!;
        var count = (int)inventory.Outputs[0]!;
        var names = Array<string>(inventory, 1);
        if (count != (int)Get("FrameObj.Count", ["All"], true)!.DirectValue! || names.Any(string.IsNullOrWhiteSpace) ||
            names.Distinct(StringComparer.Ordinal).Count() != count)
            throw new InvalidOperationException("Full frame inventory count/identity differs from the source.");
        var indices = names.Select((n, i) => (n, i)).ToDictionary(p => p.n, p => p.i, StringComparer.Ordinal);
        foreach (var member in source.Facts.Members)
        {
            if (!indices.TryGetValue(member.Name, out var index) ||
                member.Story is not null && member.Story != Array<string>(inventory, 3)[index] ||
                member.SectionName is not null && member.SectionName != Array<string>(inventory, 2)[index] ||
                member.EndpointNames.Count == 2 && !member.EndpointNames.SequenceEqual(new[] { Array<string>(inventory, 4)[index], Array<string>(inventory, 5)[index] }))
                throw new InvalidOperationException("Requested source membership differs from the complete frame inventory.");
        }
        var tables = new Dictionary<string, EtabsBulkTable>(StringComparer.Ordinal);
        foreach (var spec in new[]
        {
            new EtabsBulkTableSpec("Area Assignments - Insertion Point", true, 2, "UniqueName"),
            new EtabsBulkTableSpec("Area Assignments - Thickness Overwrites", true, 1, "UniqueName"),
            EtabsBulkTable.Specifications.Single(s => s.Key == "Beam Object Connectivity")
        })
        {
            var tableName = spec.Key;
            var metadata = Get("DatabaseTables.GetAllFieldsInTable", [tableName]);
            var data = metadata is null ? null : spec.Editing ? Get("DatabaseTables.GetTableForEditingArray", [tableName, "All"]) :
                Get("DatabaseTables.GetTableForDisplayArray", [tableName, new[] { "UniqueName", "UniquePtI", "UniquePtJ", "Story", "CurveType" }, "All"]);
            if (data is null) continue;
            var shift = spec.Editing ? 0 : 1;
            if ((int)data.Outputs[shift + 2]! > 200_000 || Array<string>(data, shift + 3).Length > 1_000_000)
                throw new InvalidOperationException("Area assignment table exceeds the source row/cell bound.");
            try
            {
                tables.Add(tableName, new(spec,
                    JsonSerializer.SerializeToElement(metadata!.Outputs), JsonSerializer.SerializeToElement(data.Outputs)));
            }
            catch (InvalidDataException exception)
            {
                gaps.Add(new("topology table " + tableName, [tableName], "TOPOLOGY.TABLE_UNQUALIFIED", exception.Message, null));
            }
        }
        foreach (var name in scope.FrameNames.Concat(connections.Where(c => c.ObjectType == 2).Select(c => c.ObjectName)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))
            Frame(name);
        foreach (var name in connections.Where(c => c.ObjectType == 5).Select(c => c.ObjectName).Order(StringComparer.Ordinal))
            Area(name);
        foreach (var name in source.Facts.Members.SelectMany(m => m.Elements).SelectMany(e => new[] { e.AnalysisPointI, e.AnalysisPointJ })
            .Where(n => !string.IsNullOrWhiteSpace(n)).Cast<string>().Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))
        {
            var coordinate = Get("PointElm.GetCoordCartesian", [name, "Global"]);
            analysisPoints.Add(name, new(name, coordinate?.Outputs.Cast<double>().Select(Length).ToArray()));
        }
        var geometry = new EtabsTopologyGeometry(frames.Values.ToArray(), areas.Values.ToArray(),
            points.Values.OrderBy(p => p.Name, StringComparer.Ordinal).ToArray(), analysisPoints.Values.ToArray());
        var facts = EtabsTopologyQualification.Interpret(source.Facts, geometry);
        var calls = new List<EtabsRawGetterCall>(before);
        foreach (var initial in before)
        {
            var final = adapter.Read(initial.Operation, initial.Inputs, deadlineUtc, token).RawCall;
            if (final is null || Shape(initial) != Shape(final))
                throw new InvalidOperationException("Source/topology fact changed or became unavailable: " + initial.Operation);
            calls.Add(final with { GetterMatrixSha256 = EtabsTopologyGetterMatrix.Sha256 });
        }
        var finalModel = adapter.Read("SapModel.GetModelFilename", [true], deadlineUtc, token).RawCall;
        if (finalModel is null || Shape(before[0]) != Shape(finalModel))
            throw new InvalidOperationException("Live source changed at final topology postflight.");
        calls.Add(finalModel with { GetterMatrixSha256 = EtabsTopologyGetterMatrix.Sha256 });
        return new(source, geometry, facts,
            Convert.ToHexStringLower(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(before.Select(c => new { c.Operation, c.Inputs, Shape = Shape(c) })))),
            calls, gaps, tables.Values.Select(t => new EtabsSourceTableSummary(t.Key,
                t.Key == "Area Assignments - Thickness Overwrites" ? 1 : 2, t.SourceRowCount, t.Rows.Count, t.ContextOnlyRowCount)).ToArray());

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
                    throw new InvalidOperationException(operation + ": " + result.Message);
                gaps.Add(new(operation, inputs, result.DiagnosticCode ?? "ETABS.CALL_FAILED", result.Message ?? "Unavailable getter.", observed.Last));
                cache.Add(key, null); return null;
            }
            var call = result.RawCall with { GetterMatrixSha256 = EtabsTopologyGetterMatrix.Sha256 };
            before.Add(call); cache.Add(key, call); return call;
        }

        void Point(string name)
        {
            if (points.ContainsKey(name)) return;
            var coordinate = Get("PointObj.GetCoordCartesian", [name, "Global"]);
            points.Add(name, new(name, coordinate?.Outputs.Cast<double>().Select(Length).ToArray()));
        }

        void Frame(string name)
        {
            sourceMembers.TryGetValue(name, out var member);
            var section = member?.SectionName ?? Text(Get("FrameObj.GetSection", [name]), 0);
            var endpoints = member?.EndpointNames ?? Get("FrameObj.GetPoints", [name])?.Outputs.Cast<string>().ToArray() ?? [];
            foreach (var point in endpoints) Point(point);
            var orientation = member?.DesignOrientation ?? Value<int>(Get("FrameObj.GetDesignOrientation", [name]), 0);
            var sectionType = member?.SectionType ?? (section is null ? null : Value<int>(Get("PropFrame.GetTypeOAPI", [section]), 0));
            var rectangle = sectionType == 8 && section is not null ? Get("PropFrame.GetRectangle", [section]) : null;
            var curve = orientation != 2 ? Get("FrameObj.GetCurved_2", [name]) : null;
            if (curve is not null && (int)curve.Outputs[2]! > EtabsTopologyQualification.MaximumAreaVertices)
                throw new InvalidOperationException("Frame curve exceeds the 40-point topology bound.");
            var curveType = Value<int>(curve, 0);
            var curveBasis = curve is null ? "unavailable" : "explicit_getter";
            if (orientation == 2 && tables.TryGetValue("Beam Object Connectivity", out var beams) &&
                beams.Rows.TryGetValue(name, out var beam) && endpoints.Count == 2)
            {
                if (beam.Required("UniquePtI") != endpoints[0] || beam.Required("UniquePtJ") != endpoints[1])
                    throw new InvalidOperationException("Beam table and direct endpoint identities disagree.");
                curveType = beam.Optional("CurveType") switch { "Straight" => 0, "Circular" => 1, "Multilinear" => 2, "Bezier" => 3, "Spline" => 4, _ => null };
                curveBasis = curveType is null ? "beam_connectivity_curvature_not_returned" : "Beam Object Connectivity/v2/explicit_CurveType";
            }
            frames.Add(name, new(name, orientation, section, sectionType,
                member?.WidthMm ?? Dimension(rectangle, 3), member?.DepthMm ?? Dimension(rectangle, 2), endpoints,
                curveType, OptionalArray<double>(Get("FrameObj.GetTransformationMatrix", [name, true]), 0),
                OptionalArray<double>(Get("FrameObj.GetModifiers", [name]), 0),
                section is null ? null : OptionalArray<double>(Get("PropFrame.GetModifiers", [section]), 0),
                member?.Assignments ?? Assignments(name), curveBasis));
        }

        EtabsSourceAssignments Assignments(string name)
        {
            var offsets = Get("FrameObj.GetEndLengthOffset", [name]); var insertion = Get("FrameObj.GetInsertionPoint_1", [name]);
            var releases = Get("FrameObj.GetReleases", [name]); var axes = Get("FrameObj.GetLocalAxes", [name]);
            return new(Value<bool>(offsets, 0), Dimension(offsets, 1), Dimension(offsets, 2), Value<double>(offsets, 3),
                Value<int>(insertion, 0), Value<bool>(insertion, 1), Value<bool>(insertion, 2), Value<bool>(insertion, 3), Text(insertion, 6),
                OptionalArray<double>(insertion, 4)?.Select(Length).ToArray(), OptionalArray<double>(insertion, 5)?.Select(Length).ToArray(),
                OptionalArray<bool>(releases, 0), OptionalArray<bool>(releases, 1), OptionalArray<double>(releases, 2), OptionalArray<double>(releases, 3),
                Value<double>(axes, 0), Value<bool>(axes, 1));
        }

        void Area(string name)
        {
            var pointNames = Array<string>(Get("AreaObj.GetPoints", [name]), 1);
            if (pointNames.Length > EtabsTopologyQualification.MaximumAreaVertices || pointNames.Any(string.IsNullOrWhiteSpace) ||
                pointNames.Distinct(StringComparer.Ordinal).Count() != pointNames.Length)
                throw new InvalidOperationException("Area points are duplicated/blank or exceed the 40-vertex bound.");
            foreach (var point in pointNames) Point(point);
            var orientation = Value<int>(Get("AreaObj.GetDesignOrientation", [name]), 0);
            var property = Text(Get("AreaObj.GetProperty", [name]), 0);
            var wall = orientation == 1 && property is not null ? Get("PropArea.GetWall", [property]) : null;
            var offsets = OptionalArray<double>(Get("AreaObj.GetOffsets3", [name]), 1);
            string? cardinal = null; bool? transform = null;
            var placement = "unqualified_shell_placement";
            if (tables.TryGetValue("Area Assignments - Insertion Point", out var insertions) &&
                tables.TryGetValue("Area Assignments - Thickness Overwrites", out var thickness) &&
                insertions.Rows.TryGetValue(name, out var row))
            {
                cardinal = row.Optional("CardinalPt");
                transform = row.Optional("Transform") switch { "Yes" => true, "No" => false, _ => null };
                var explicitNoJointOffsets = row.Optional("PointNumber") is null && row.Optional("CoordSys") is null &&
                    new[] { "Offset1", "Offset2", "Offset3" }.All(field => row.Optional(field) is null);
                if (cardinal == "Middle" && transform is not null && explicitNoJointOffsets && !thickness.Rows.ContainsKey(name) &&
                    offsets is not null && offsets.Length == pointNames.Length && offsets.All(v => v == 0))
                    placement = "centred_uniform_no_overwrites";
            }
            areas.Add(name, new(name, orientation, Value<bool>(Get("AreaObj.GetOpening", [name]), 0), property, pointNames,
                Value<int>(wall, 0), Value<int>(wall, 1), Dimension(wall, 3), offsets, placement, cardinal, transform));
        }

        double Length(double native) => EtabsSourceQualification.ConvertFinite(native, units.LengthToMm);
        double? Dimension(EtabsRawGetterCall? call, int index) => Value<double>(call, index) is { } value ? Length(value) : null;
    }

    private static string Key(EtabsRawGetterCall call) => call.Operation + JsonSerializer.Serialize(call.Inputs);
    private static string Shape(EtabsRawGetterCall call) => JsonSerializer.Serialize(new { call.DirectValue, call.Outputs, call.CsiReturnCode });
    private static string? Text(EtabsRawGetterCall? call, int index) => call?.Outputs[index] as string;
    private static T? Value<T>(EtabsRawGetterCall? call, int index) where T : struct => call?.Outputs[index] is T value ? value : null;
    private static T[] Array<T>(EtabsRawGetterCall? call, int index) => call?.Outputs[index] is System.Array array ? array.Cast<T>().ToArray() : [];
    private static T[]? OptionalArray<T>(EtabsRawGetterCall? call, int index) => call is null ? null : Array<T>(call, index);
    private sealed class ObservedHost(IEtabsGetterHost inner) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity => inner.Identity;
        public EtabsInvocation? Last { get; set; }
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token) => Last = inner.Invoke(definition, inputs, token);
        public void Dispose() { }
    }
}
