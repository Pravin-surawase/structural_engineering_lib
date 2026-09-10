using System.Security.Cryptography;
using System.Text.Json;

namespace StructuralEngineering.Etabs;

public sealed record EtabsInspectionGap(string Operation, string Code, string Reason, EtabsInvocation? RawInvocation = null);
public sealed record EtabsInspectionCapture(string Scope, string ProtectedStateSha256,
    int FrameCount, int PointCount, int AreaCount, IReadOnlyList<string> SampleFrames,
    IReadOnlyList<EtabsRawGetterCall> Calls, IReadOnlyList<EtabsInspectionGap> Gaps);

public static class EtabsInspectionReader
{
    public const int MaximumFrameCatalog = 20_000;
    public const int MaximumSelections = 500;
    public const int MaximumSample = 20;
    public const string OverviewScope = "model_overview;geometry=not_read;forces=not_read;design_support=not_evaluated";

    public static EtabsInspectionCapture Read(IEtabsGetterHost host, DateTimeOffset deadlineUtc,
        bool includeSample, CancellationToken token = default, bool overviewOnly = false)
    {
        if (overviewOnly && includeSample) throw new ArgumentException("An overview cannot include frame definitions.");
        var observedHost = new ObservedHost(host);
        var adapter = new EtabsGetterAdapter(observedHost, EtabsInspectionGetterMatrix.Allowed);
        var calls = new List<EtabsRawGetterCall>();
        var gaps = new List<EtabsInspectionGap>();
        var protectedReads = new List<(string Operation, object?[] Inputs, string Shape)>();
        EtabsRawGetterCall? Read(string operation, object?[] inputs, bool required = true, bool protect = false)
        {
            token.ThrowIfCancellationRequested();
            observedHost.LastInvocation = null;
            var result = adapter.Read(operation, inputs, deadlineUtc, token);
            if (result.RawCall is null)
            {
                if (required || result.DiagnosticCode == "ETABS.CALL_TIMEOUT")
                    throw new InvalidOperationException($"{operation}: {result.DiagnosticCode}: {result.Message}");
                gaps.Add(new(operation, result.DiagnosticCode ?? "ETABS.CALL_FAILED", result.Message ?? "Getter unavailable.", observedHost.LastInvocation));
                return null;
            }
            var call = result.RawCall with { GetterMatrixSha256 = EtabsInspectionGetterMatrix.Sha256 };
            calls.Add(call);
            if (protect) protectedReads.Add((operation, inputs, Shape(call)));
            return call;
        }

        var model = Read("SapModel.GetModelFilename", [true], protect: true)!;
        if (!string.Equals(Path.GetFullPath((string)model.DirectValue!), Path.GetFullPath(host.Identity.ModelPath), StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("The live model differs from the exact discovered source.");
        foreach (var operation in new[] { "SapModel.GetModelIsLocked", "SapModel.GetPresentUnits", "SapModel.GetDatabaseUnits", "SapModel.GetVersion" })
            Read(operation, [], protect: true);
        int Count(string operation, object?[] inputs)
        {
            var count = (int)Read(operation, inputs, protect: true)!.DirectValue!;
            return count >= 0 ? count : throw new InvalidOperationException($"{operation} returned a negative count.");
        }
        var frameCount = Count("FrameObj.Count", ["All"]);
        var pointCount = Count("PointObj.Count", []);
        var areaCount = Count("AreaObj.Count", []);
        Read("Story.GetStories_2", [], protect: true);
        Read("LoadPatterns.GetNameList", [], protect: true);
        var cases = Read("LoadCases.GetNameList", [0], protect: true)!;
        var combos = Read("RespCombo.GetNameList", [], protect: true)!;
        Read("Analyze.GetCaseStatus", [], protect: true);
        Read("Analyze.GetRunCaseFlag", [], protect: true);
        foreach (var operation in new[] { "DesignConcrete.GetCode", "DesignConcrete.GetResultsAvailable" })
            Read(operation, [], required: false, protect: true);
        if (!overviewOnly)
        {
            foreach (var kind in new[] { "LoadCases", "LoadCombinations", "LoadPatterns" })
                Read($"DatabaseTables.Get{kind}SelectedForDisplay", [], required: false, protect: true);
            Read("DatabaseTables.GetAllTables", [], required: false);
            if ((int)cases.Outputs[0]! + (int)combos.Outputs[0]! <= MaximumSelections)
            {
                foreach (var name in Strings(cases, 1))
                {
                    Read("Results.Setup.GetCaseSelectedForOutput", [name], protect: true);
                    Read("LoadCases.GetTypeOAPI", [name], protect: true);
                }
                foreach (var name in Strings(combos, 1))
                {
                    Read("Results.Setup.GetComboSelectedForOutput", [name], protect: true);
                    Read("RespCombo.GetTypeOAPI", [name], protect: true);
                }
            }
            else gaps.Add(new("output selections", "ETABS.INSPECTION_LIMIT", "More than 500 cases plus combinations; per-name selections and types were not read."));
        }

        var samples = new List<string>();
        if (includeSample && frameCount is > 0 and <= MaximumFrameCatalog)
        {
            var frames = Read("FrameObj.GetAllFrames", ["Global"], protect: true)!;
            if ((int)frames.Outputs[0]! != frameCount) throw new InvalidOperationException("Frame count and catalog disagree.");
            var names = Strings(frames, 1); var sections = Strings(frames, 2); var stories = Strings(frames, 3);
            if (names.Any(string.IsNullOrWhiteSpace) || names.Distinct(StringComparer.Ordinal).Count() != frameCount)
                throw new InvalidOperationException("Frame catalog has blank or duplicate names.");
            // First diversify story/section pairs, then fill from the remaining catalog in a deterministic order.
            var ordered = Enumerable.Range(0, frameCount).OrderBy(i => stories[i], StringComparer.Ordinal)
                .ThenBy(i => sections[i], StringComparer.Ordinal).ThenBy(i => names[i], StringComparer.Ordinal).ToArray();
            var strata = ordered.GroupBy(i => (stories[i], sections[i])).Select(g => g.First()).ToArray();
            var chosen = Enumerable.Range(0, Math.Min(MaximumSample, strata.Length))
                .Select(i => strata[(int)((long)i * strata.Length / Math.Min(MaximumSample, strata.Length))])
                .Concat(ordered).Distinct().Take(MaximumSample).ToArray();
            var sectionSeen = new HashSet<string>(StringComparer.Ordinal);
            var materialSeen = new HashSet<string>(StringComparer.Ordinal);
            var pointSeen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var i in chosen)
            {
                var name = names[i]; samples.Add(name);
                foreach (var operation in new[] { "FrameObj.GetDesignOrientation", "FrameObj.GetLabelFromName", "FrameObj.GetSection",
                    "FrameObj.GetModifiers", "FrameObj.GetEndLengthOffset", "FrameObj.GetInsertionPoint_1", "FrameObj.GetReleases", "FrameObj.GetLocalAxes" })
                    Read(operation, [name], required: false, protect: true);
                var points = Read("FrameObj.GetPoints", [name], protect: true)!;
                foreach (var point in points.Outputs.Cast<string>())
                    if (pointSeen.Add(point)) Read("PointObj.GetRestraint", [point], required: false, protect: true);
                if (!sectionSeen.Add(sections[i])) continue;
                var material = Read("PropFrame.GetMaterial", [sections[i]], required: false, protect: true);
                Read("PropFrame.GetSectProps", [sections[i]], required: false, protect: true);
                Read("PropFrame.GetModifiers", [sections[i]], required: false, protect: true);
                if (material?.Outputs[0] is string materialName && materialSeen.Add(materialName))
                {
                    Read("PropMaterial.GetMPIsotropic", [materialName, 0d], required: false, protect: true);
                    Read("PropMaterial.GetWeightAndMass", [materialName, 0d], required: false, protect: true);
                }
            }
        }
        else if (includeSample) gaps.Add(new("frame sample", "ETABS.INSPECTION_LIMIT", $"Frame count {frameCount} is outside 1..{MaximumFrameCatalog}; no frame catalog or sample was retrieved."));

        foreach (var (operation, inputs, shape) in protectedReads)
            if (Shape(Read(operation, inputs)!) != shape)
                throw new InvalidOperationException($"Protected state changed: {operation}.");
        // Fence the final live filename after all definition checks, as disk identity cannot see a model switch.
        if (Shape(Read("SapModel.GetModelFilename", [true])!) != Shape(model))
            throw new InvalidOperationException("The live model changed at final postflight.");
        var stateHash = Convert.ToHexStringLower(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(
            protectedReads.Select(x => new { x.Operation, x.Inputs, x.Shape }))));
        return new(overviewOnly ? OverviewScope : "inventory_and_optional_definition_sample;forces=not_read;design_support=not_evaluated", stateHash,
            frameCount, pointCount, areaCount, samples, calls, gaps);
    }

    private static string[] Strings(EtabsRawGetterCall call, int index) => call.Outputs[index] is Array values
        ? values.Cast<object?>().Select(x => (string)x!).ToArray() : [];
    private static string Shape(EtabsRawGetterCall call) => Convert.ToHexStringLower(SHA256.HashData(
        JsonSerializer.SerializeToUtf8Bytes(new { call.DirectValue, call.Outputs, call.CsiReturnCode })));

    private sealed class ObservedHost(IEtabsGetterHost inner) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity => inner.Identity;
        public EtabsInvocation? LastInvocation { get; set; }
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token) =>
            LastInvocation = inner.Invoke(definition, inputs, token);
        public void Dispose() { }
    }
}
