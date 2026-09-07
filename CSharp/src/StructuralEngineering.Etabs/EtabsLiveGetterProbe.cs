using System.Security.Cryptography;
using System.Text.Json;

namespace StructuralEngineering.Etabs;

public sealed record EtabsLiveGetterProbeRequest(
    string MemberObjectName,
    string ExpectedMemberLabel,
    string ExpectedStory,
    IReadOnlyList<string> SelectedCases,
    IReadOnlyList<string> SelectedCombinations,
    int FinishedCaseStatus,
    int FrameItemTypeElm,
    DateTimeOffset DeadlineUtc);

public sealed record EtabsProtectedState(
    string Sha256,
    string ModelPath,
    long ModelBytes,
    DateTimeOffset ModelModifiedUtc,
    string ModelSha256,
    bool ModelLocked,
    int PresentUnits,
    int DatabaseUnits,
    string ApiVersion,
    IReadOnlyList<string> CaseNames,
    IReadOnlyList<int> CaseStatuses,
    IReadOnlyList<bool> RunCaseFlags,
    IReadOnlyDictionary<string, bool> CaseSelections,
    IReadOnlyDictionary<string, bool> CombinationSelections);

public sealed record EtabsLiveGetterProbeCapture(
    string Verdict,
    DateTimeOffset StartedUtc,
    DateTimeOffset CompletedUtc,
    string GetterMatrixSha256,
    EtabsHostIdentity HostIdentity,
    EtabsLiveGetterProbeRequest Request,
    EtabsProtectedState Preflight,
    EtabsProtectedState Postflight,
    IReadOnlyList<string> PointNames,
    IReadOnlyList<string> ElementNames,
    string SectionName,
    string MaterialName,
    int FrameForceRows,
    IReadOnlyList<EtabsRawGetterCall> Calls);

public sealed class EtabsLiveGetterProbeException(string message) : InvalidOperationException(message);

public static partial class EtabsLiveGetterProbe
{
    public static EtabsLiveGetterProbeCapture Run(
        IEtabsGetterHost host,
        EtabsLiveGetterProbeRequest request,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(host);
        ArgumentNullException.ThrowIfNull(request);
        if (string.IsNullOrWhiteSpace(request.MemberObjectName) ||
            string.IsNullOrWhiteSpace(request.ExpectedMemberLabel) ||
            string.IsNullOrWhiteSpace(request.ExpectedStory))
            throw new ArgumentException("The live getter probe requires exact nonblank member identities.", nameof(request));
        if (request.SelectedCases.Count + request.SelectedCombinations.Count == 0)
            throw new ArgumentException("The live getter probe requires an explicit output selection.", nameof(request));

        var started = DateTimeOffset.UtcNow;
        var adapter = new EtabsGetterAdapter(host);
        var calls = new List<EtabsRawGetterCall>();
        var preflight = CaptureProtectedState(adapter, host, request, calls, cancellationToken);
        ValidateReadiness(preflight, request);

        Call(adapter, request, calls, "Story.GetStories_2", [], cancellationToken);
        var frameNames = Strings(Call(adapter, request, calls, "FrameObj.GetNameList", [], cancellationToken), 1);
        if (!frameNames.Contains(request.MemberObjectName, StringComparer.Ordinal))
            throw new EtabsLiveGetterProbeException(
                $"Requested frame object {request.MemberObjectName} is absent from FrameObj.GetNameList.");

        var member = ReadMember(adapter, request, calls, cancellationToken);

        ReadCatalogue(adapter, request, calls, preflight, cancellationToken);

        var postflight = CaptureProtectedState(adapter, host, request, calls, cancellationToken);
        RequireEqual("protected-state SHA-256", preflight.Sha256, postflight.Sha256);

        return new EtabsLiveGetterProbeCapture(
            "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM",
            started,
            DateTimeOffset.UtcNow,
            EtabsGetterMatrix.Sha256,
            host.Identity,
            request,
            preflight,
            postflight,
            member.PointNames,
            member.ElementNames,
            member.SectionName,
            member.MaterialName,
            member.FrameForceRows,
            calls);
    }

    public static string Serialize(EtabsLiveGetterProbeCapture capture) =>
        JsonSerializer.Serialize(capture, new JsonSerializerOptions { WriteIndented = true });

    private static EtabsProtectedState CaptureProtectedState(
        EtabsGetterAdapter adapter,
        IEtabsGetterHost host,
        EtabsLiveGetterProbeRequest request,
        List<EtabsRawGetterCall> calls,
        CancellationToken cancellationToken)
    {
        var identity = host.InspectIdentity();
        var modelPath = Direct<string>(Call(adapter, request, calls, "SapModel.GetModelFilename", [true], cancellationToken));
        if (!string.Equals(Path.GetFullPath(modelPath), Path.GetFullPath(identity.ModelPath), StringComparison.OrdinalIgnoreCase))
            throw new EtabsLiveGetterProbeException("The getter model path differs from the inspected host identity.");
        var locked = Direct<bool>(Call(adapter, request, calls, "SapModel.GetModelIsLocked", [], cancellationToken));
        var presentUnits = Direct<int>(Call(adapter, request, calls, "SapModel.GetPresentUnits", [], cancellationToken));
        var databaseUnits = Direct<int>(Call(adapter, request, calls, "SapModel.GetDatabaseUnits", [], cancellationToken));
        Call(adapter, request, calls, "SapModel.GetPresentUnits_2", [], cancellationToken);
        Call(adapter, request, calls, "SapModel.GetDatabaseUnits_2", [], cancellationToken);
        var version = Scalar<string>(Call(adapter, request, calls, "SapModel.GetVersion", [], cancellationToken), 0);
        var cases = Strings(Call(adapter, request, calls, "LoadCases.GetNameList", [0], cancellationToken), 1);
        var combinations = Strings(Call(adapter, request, calls, "RespCombo.GetNameList", [], cancellationToken), 1);
        var statusesCall = Call(adapter, request, calls, "Analyze.GetCaseStatus", [], cancellationToken);
        var statusNames = Strings(statusesCall, 1);
        var statuses = Integers(statusesCall, 2);
        var runCall = Call(adapter, request, calls, "Analyze.GetRunCaseFlag", [], cancellationToken);
        var runNames = Strings(runCall, 1);
        var runFlags = Booleans(runCall, 2);
        if (!cases.SequenceEqual(statusNames, StringComparer.Ordinal) ||
            !cases.SequenceEqual(runNames, StringComparer.Ordinal))
            throw new EtabsLiveGetterProbeException("Load-case, status, and run-flag inventories are not identical and ordered.");

        var caseSelections = new SortedDictionary<string, bool>(StringComparer.Ordinal);
        foreach (var name in cases)
            caseSelections[name] = Scalar<bool>(
                Call(adapter, request, calls, "Results.Setup.GetCaseSelectedForOutput", [name], cancellationToken), 0);
        var combinationSelections = new SortedDictionary<string, bool>(StringComparer.Ordinal);
        foreach (var name in combinations)
            combinationSelections[name] = Scalar<bool>(
                Call(adapter, request, calls, "Results.Setup.GetComboSelectedForOutput", [name], cancellationToken), 0);

        var protectedValues = new SortedDictionary<string, object?>(StringComparer.Ordinal)
        {
            ["api_version"] = version,
            ["case_names"] = cases,
            ["case_selections"] = caseSelections,
            ["case_statuses"] = statuses,
            ["combination_selections"] = combinationSelections,
            ["database_units"] = databaseUnits,
            ["model_bytes"] = identity.ModelBytes,
            ["model_locked"] = locked,
            ["model_modified_utc"] = identity.ModelModifiedUtc.UtcDateTime.ToString("O"),
            ["model_path"] = Path.GetFullPath(modelPath),
            ["model_sha256"] = identity.ModelSha256,
            ["present_units"] = presentUnits,
            ["process_executable"] = identity.ExecutablePath,
            ["process_id"] = identity.ProcessId,
            ["process_started_utc"] = identity.ProcessStartedUtc.UtcDateTime.ToString("O"),
            ["run_case_flags"] = runFlags
        };
        var digest = Convert.ToHexStringLower(SHA256.HashData(
            JsonSerializer.SerializeToUtf8Bytes(protectedValues)));
        return new EtabsProtectedState(
            digest,
            modelPath,
            identity.ModelBytes,
            identity.ModelModifiedUtc,
            identity.ModelSha256,
            locked,
            presentUnits,
            databaseUnits,
            version,
            cases,
            statuses,
            runFlags,
            caseSelections,
            combinationSelections);
    }

    private static void ValidateReadiness(EtabsProtectedState state, EtabsLiveGetterProbeRequest request, bool allowMetricDatabase = false)
    {
        if (!state.ModelLocked)
            throw new EtabsLiveGetterProbeException("The exact ETABS model is not locked.");
        if (state.PresentUnits != 6 || (state.DatabaseUnits != 6 && !(allowMetricDatabase && state.DatabaseUnits == 9)))
            throw new EtabsLiveGetterProbeException("The frozen getter probe requires ETABS unit enum 6 (kN/m/C).");
        if (state.CaseStatuses.Count == 0 || state.CaseStatuses.Any(value => value != request.FinishedCaseStatus))
            throw new EtabsLiveGetterProbeException("Every analysis case must have the exact finished status before force access.");
        var actualCases = state.CaseSelections.Where(item => item.Value).Select(item => item.Key).ToArray();
        var actualCombinations = state.CombinationSelections.Where(item => item.Value).Select(item => item.Key).ToArray();
        if (!actualCases.SequenceEqual(request.SelectedCases.Order(StringComparer.Ordinal), StringComparer.Ordinal) ||
            !actualCombinations.SequenceEqual(request.SelectedCombinations.Order(StringComparer.Ordinal), StringComparer.Ordinal))
            throw new EtabsLiveGetterProbeException("The output selections differ from the exact frozen request.");
    }

    private static EtabsRawGetterCall Call(
        EtabsGetterAdapter adapter,
        EtabsLiveGetterProbeRequest request,
        List<EtabsRawGetterCall> calls,
        string operation,
        IReadOnlyList<object?> inputs,
        CancellationToken cancellationToken)
    {
        var result = adapter.Read(operation, inputs, request.DeadlineUtc, cancellationToken);
        if (result.State is not EtabsGetterState.Completed || result.RawCall is null)
            throw new EtabsLiveGetterProbeException(
                $"{result.DiagnosticCode ?? "ETABS.CALL_FAILED"}: {result.Message ?? operation}");
        calls.Add(result.RawCall);
        return result.RawCall;
    }

    private static T Direct<T>(EtabsRawGetterCall call) =>
        call.DirectValue is T value
            ? value
            : throw new EtabsLiveGetterProbeException($"{call.Operation} direct value is not {typeof(T).Name}.");

    private static T Scalar<T>(EtabsRawGetterCall call, int index) =>
        call.Outputs[index] is T value
            ? value
            : throw new EtabsLiveGetterProbeException(
                $"{call.Operation} output {index} is not {typeof(T).Name}.");

    private static string[] Strings(EtabsRawGetterCall call, int index) =>
        ArrayValues(call, index).Select(value => value as string
            ?? throw new EtabsLiveGetterProbeException($"{call.Operation} contains a non-string array value.")).ToArray();

    private static int[] Integers(EtabsRawGetterCall call, int index) =>
        ArrayValues(call, index).Select(value => value is int item
            ? item
            : throw new EtabsLiveGetterProbeException($"{call.Operation} contains a non-Int32 array value.")).ToArray();

    private static bool[] Booleans(EtabsRawGetterCall call, int index) =>
        ArrayValues(call, index).Select(value => value is bool item
            ? item
            : throw new EtabsLiveGetterProbeException($"{call.Operation} contains a non-Boolean array value.")).ToArray();

    private static object?[] ArrayValues(EtabsRawGetterCall call, int index) => call.Outputs[index] switch
    {
        object?[] values => values,
        Array values => values.Cast<object?>().ToArray(),
        // The adapter accepts a null parallel array only after proving its source count is zero.
        null => [],
        _ => throw new EtabsLiveGetterProbeException($"{call.Operation} output {index} is not an array.")
    };

    private static void ValidateElementTopology(
        IReadOnlyList<string> framePoints,
        IReadOnlyList<(string Point1, string Point2)> elementPoints)
    {
        if (framePoints.Count != 2 || framePoints.Any(string.IsNullOrWhiteSpace))
            throw new EtabsLiveGetterProbeException("The frame object must have two exact nonblank endpoint names.");

        var adjacency = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        foreach (var (point1, point2) in elementPoints)
        {
            if (string.IsNullOrWhiteSpace(point1) || string.IsNullOrWhiteSpace(point2))
                throw new EtabsLiveGetterProbeException("An analysis element returned a blank endpoint name.");
            if (!adjacency.TryGetValue(point1, out var point1Links))
                adjacency[point1] = point1Links = new HashSet<string>(StringComparer.Ordinal);
            if (!adjacency.TryGetValue(point2, out var point2Links))
                adjacency[point2] = point2Links = new HashSet<string>(StringComparer.Ordinal);
            point1Links.Add(point2);
            point2Links.Add(point1);
        }

        if (!adjacency.ContainsKey(framePoints[0]) || !adjacency.ContainsKey(framePoints[1]))
            throw new EtabsLiveGetterProbeException(
                "The force-returned analysis elements do not include both frame-object endpoints.");

        var visited = new HashSet<string>(StringComparer.Ordinal) { framePoints[0] };
        var pending = new Queue<string>();
        pending.Enqueue(framePoints[0]);
        while (pending.TryDequeue(out var point))
        {
            foreach (var neighbor in adjacency[point])
            {
                if (visited.Add(neighbor))
                    pending.Enqueue(neighbor);
            }
        }
        if (!visited.Contains(framePoints[1]) || visited.Count != adjacency.Count)
            throw new EtabsLiveGetterProbeException(
                "The force-returned analysis-element topology is disconnected from the frame object.");
    }

    private static void RequireEqual<T>(string label, T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
            throw new EtabsLiveGetterProbeException(
                $"Exact {label} mismatch: expected {expected}; observed {actual}.");
    }
    private static void ReadCatalogue(EtabsGetterAdapter adapter, EtabsLiveGetterProbeRequest request,
        List<EtabsRawGetterCall> calls, EtabsProtectedState preflight, CancellationToken cancellationToken)
    {
        var loadPatterns = Strings(Call(adapter, request, calls, "LoadPatterns.GetNameList", [], cancellationToken), 1);
        foreach (var name in loadPatterns)
        {
            Call(adapter, request, calls, "LoadPatterns.GetLoadType", [name], cancellationToken);
            Call(adapter, request, calls, "LoadPatterns.GetSelfWTMultiplier", [name], cancellationToken);
        }

        foreach (var name in preflight.CaseNames)
        {
            var basicType = Call(adapter, request, calls, "LoadCases.GetTypeOAPI", [name], cancellationToken);
            var type = Call(adapter, request, calls, "LoadCases.GetTypeOAPI_1", [name], cancellationToken);
            RequireEqual("load-case type", Scalar<int>(basicType, 0), Scalar<int>(type, 0));
            RequireEqual("load-case subtype", Scalar<int>(basicType, 1), Scalar<int>(type, 1));
            if (Scalar<int>(type, 0) == 1)
            {
                Call(adapter, request, calls, "LoadCases.StaticLinear.GetInitialCase", [name], cancellationToken);
                Call(adapter, request, calls, "LoadCases.StaticLinear.GetLoads", [name], cancellationToken);
            }
        }

        foreach (var name in preflight.CombinationSelections.Keys)
        {
            Call(adapter, request, calls, "RespCombo.GetTypeOAPI", [name], cancellationToken);
            Call(adapter, request, calls, "RespCombo.GetCaseList", [name], cancellationToken);
        }

    }
}
