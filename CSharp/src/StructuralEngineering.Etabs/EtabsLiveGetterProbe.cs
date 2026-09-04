using System.Diagnostics;
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

public static class EtabsLiveGetterProbe
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
        var preflight = CaptureProtectedState(adapter, host.Identity, request, calls, cancellationToken);
        ValidateReadiness(preflight, request);

        Call(adapter, request, calls, "Story.GetStories_2", [], cancellationToken);
        var frameNames = Strings(Call(adapter, request, calls, "FrameObj.GetNameList", [], cancellationToken), 1);
        if (!frameNames.Contains(request.MemberObjectName, StringComparer.Ordinal))
            throw new EtabsLiveGetterProbeException(
                $"Requested frame object {request.MemberObjectName} is absent from FrameObj.GetNameList.");

        var label = Call(adapter, request, calls, "FrameObj.GetLabelFromName", [request.MemberObjectName], cancellationToken);
        RequireEqual("frame label", request.ExpectedMemberLabel, Scalar<string>(label, 0));
        RequireEqual("frame story", request.ExpectedStory, Scalar<string>(label, 1));

        var pointsCall = Call(adapter, request, calls, "FrameObj.GetPoints", [request.MemberObjectName], cancellationToken);
        var pointNames = new[] { Scalar<string>(pointsCall, 0), Scalar<string>(pointsCall, 1) };

        var sectionCall = Call(adapter, request, calls, "FrameObj.GetSection", [request.MemberObjectName], cancellationToken);
        var sectionName = Scalar<string>(sectionCall, 0);
        Call(adapter, request, calls, "FrameObj.GetModifiers", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetEndLengthOffset", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetInsertionPoint_1", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetReleases", [request.MemberObjectName], cancellationToken);
        var frameAxes = Call(adapter, request, calls, "FrameObj.GetLocalAxes", [request.MemberObjectName], cancellationToken);
        if (Scalar<bool>(frameAxes, 1))
            throw new EtabsLiveGetterProbeException("Advanced frame local axes are outside the frozen WP10-02 definition.");

        var frameForce = Call(
            adapter,
            request,
            calls,
            "Results.FrameForce",
            [request.MemberObjectName, request.FrameItemTypeElm],
            cancellationToken);
        var frameForceRows = Scalar<int>(frameForce, 0);
        var elementNames = Strings(frameForce, 3).Distinct(StringComparer.Ordinal).ToArray();
        if (frameForceRows == 0 || elementNames.Length == 0)
            throw new EtabsLiveGetterProbeException(
                "Results.FrameForce returned no object/element mapping rows for the explicit member and output selection.");

        foreach (var pointName in pointNames.Distinct(StringComparer.Ordinal))
        {
            Call(adapter, request, calls, "PointObj.GetCoordCartesian", [pointName, "Global"], cancellationToken);
            Call(adapter, request, calls, "PointObj.GetLabelFromName", [pointName], cancellationToken);
            Call(adapter, request, calls, "PointObj.GetRestraint", [pointName], cancellationToken);
            var pointAxes = Call(adapter, request, calls, "PointObj.GetLocalAxes", [pointName], cancellationToken);
            if (Scalar<bool>(pointAxes, 3))
                throw new EtabsLiveGetterProbeException("Advanced point local axes are outside the frozen WP10-02 definition.");
            Call(adapter, request, calls, "PointObj.GetTransformationMatrix", [pointName, true], cancellationToken);
        }

        foreach (var elementName in elementNames)
        {
            var owner = Call(adapter, request, calls, "LineElm.GetObj", [elementName], cancellationToken);
            RequireEqual("analysis-element owner", request.MemberObjectName, Scalar<string>(owner, 0));
            Call(adapter, request, calls, "LineElm.GetPoints", [elementName], cancellationToken);
            Call(adapter, request, calls, "LineElm.GetLocalAxes", [elementName], cancellationToken);
            Call(adapter, request, calls, "LineElm.GetTransformationMatrix", [elementName], cancellationToken);
        }

        var materialCall = Call(adapter, request, calls, "PropFrame.GetMaterial", [sectionName], cancellationToken);
        var materialName = Scalar<string>(materialCall, 0);
        Call(adapter, request, calls, "PropFrame.GetRectangle", [sectionName], cancellationToken);
        Call(adapter, request, calls, "PropFrame.GetSectProps", [sectionName], cancellationToken);
        Call(adapter, request, calls, "PropFrame.GetModifiers", [sectionName], cancellationToken);
        Call(adapter, request, calls, "PropMaterial.GetMPIsotropic", [materialName, 0d], cancellationToken);
        Call(adapter, request, calls, "PropMaterial.GetWeightAndMass", [materialName, 0d], cancellationToken);

        var loadPatterns = Strings(Call(adapter, request, calls, "LoadPatterns.GetNameList", [], cancellationToken), 1);
        foreach (var name in loadPatterns)
        {
            Call(adapter, request, calls, "LoadPatterns.GetLoadType", [name], cancellationToken);
            Call(adapter, request, calls, "LoadPatterns.GetSelfWTMultiplier", [name], cancellationToken);
        }

        foreach (var name in preflight.CaseNames)
        {
            Call(adapter, request, calls, "LoadCases.GetTypeOAPI", [name], cancellationToken);
            var type = Call(adapter, request, calls, "LoadCases.GetTypeOAPI_1", [name], cancellationToken);
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

        var postflight = CaptureProtectedState(adapter, host.Identity, request, calls, cancellationToken);
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
            pointNames,
            elementNames,
            sectionName,
            materialName,
            frameForceRows,
            calls);
    }

    public static string Serialize(EtabsLiveGetterProbeCapture capture) =>
        JsonSerializer.Serialize(capture, new JsonSerializerOptions { WriteIndented = true });

    private static EtabsProtectedState CaptureProtectedState(
        EtabsGetterAdapter adapter,
        EtabsHostIdentity identity,
        EtabsLiveGetterProbeRequest request,
        List<EtabsRawGetterCall> calls,
        CancellationToken cancellationToken)
    {
        var modelPath = Direct<string>(Call(adapter, request, calls, "SapModel.GetModelFilename", [true], cancellationToken));
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

        var model = new FileInfo(modelPath);
        var modelHash = Sha256File(modelPath);
        using var process = Process.GetProcessById(identity.ProcessId);
        var protectedValues = new SortedDictionary<string, object?>(StringComparer.Ordinal)
        {
            ["api_version"] = version,
            ["case_names"] = cases,
            ["case_selections"] = caseSelections,
            ["case_statuses"] = statuses,
            ["combination_selections"] = combinationSelections,
            ["database_units"] = databaseUnits,
            ["model_bytes"] = model.Length,
            ["model_locked"] = locked,
            ["model_modified_utc"] = model.LastWriteTimeUtc.ToString("O"),
            ["model_path"] = Path.GetFullPath(modelPath),
            ["model_sha256"] = modelHash,
            ["present_units"] = presentUnits,
            ["process_executable"] = process.MainModule?.FileName,
            ["process_id"] = process.Id,
            ["process_started_utc"] = process.StartTime.ToUniversalTime().ToString("O"),
            ["run_case_flags"] = runFlags
        };
        var digest = Convert.ToHexStringLower(SHA256.HashData(
            JsonSerializer.SerializeToUtf8Bytes(protectedValues)));
        return new EtabsProtectedState(
            digest,
            modelPath,
            model.Length,
            new DateTimeOffset(model.LastWriteTimeUtc, TimeSpan.Zero),
            modelHash,
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

    private static void ValidateReadiness(EtabsProtectedState state, EtabsLiveGetterProbeRequest request)
    {
        if (!state.ModelLocked)
            throw new EtabsLiveGetterProbeException("The exact ETABS model is not locked.");
        if (state.PresentUnits != 6 || state.DatabaseUnits != 6)
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

    private static object?[] ArrayValues(EtabsRawGetterCall call, int index) =>
        call.Outputs[index] as object?[]
        ?? throw new EtabsLiveGetterProbeException($"{call.Operation} output {index} is not an array.");

    private static string Sha256File(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    private static void RequireEqual<T>(string label, T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
            throw new EtabsLiveGetterProbeException(
                $"Exact {label} mismatch: expected {expected}; observed {actual}.");
    }
}
