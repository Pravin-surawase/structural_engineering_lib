using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsBatchCaptureRequest(string RequestSha256, EtabsContextInventory Context,
    IReadOnlyList<string> MemberObjectNames, DateTimeOffset DeadlineUtc);

public sealed record EtabsBatchCapture(
    string ProfileId, string RequestSha256, string GetterMatrixSha256,
    DateTimeOffset StartedUtc, DateTimeOffset CompletedUtc, EtabsHostIdentity HostIdentity,
    EtabsContextInventory Context, EtabsProtectedState Preflight, EtabsProtectedState Postflight,
    IReadOnlyList<EtabsMemberCaptureSummary> Members, IReadOnlyList<EtabsRawGetterCall> Calls);

public static partial class EtabsLiveGetterProbe
{
    /// <summary>One shared source boundary and catalogue; no cached invocation is represented as an actual getter.</summary>
    public static EtabsBatchCapture RunBatch(IEtabsGetterHost host, EtabsBatchCaptureRequest request,
        CancellationToken cancellationToken = default, Action<int, int>? progress = null)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.MemberObjectNames.Count is < 1 or > 1000 ||
            request.MemberObjectNames.Distinct(StringComparer.Ordinal).Count() != request.MemberObjectNames.Count ||
            string.IsNullOrWhiteSpace(request.RequestSha256))
            throw new ArgumentException("A batch requires 1-1000 unique, explicitly identified members and a bound request.");
        var source = request.Context.Source;
        var identity = host.InspectIdentity();
        if (source.ProcessId != identity.ProcessId || source.ProcessStartedUtc != identity.ProcessStartedUtc ||
            source.ExecutableSha256 != identity.ExecutableSha256 || source.ModelPath != identity.ModelPath ||
            source.ModelSha256 != identity.ModelSha256 || source.ModelBytes != identity.ModelBytes ||
            source.ModelModifiedUtc != identity.ModelModifiedUtc || source.EtabsApiVersion != identity.EtabsApiVersion ||
            source.PresentUnits != identity.PresentUnits)
            throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: reconnect to the current model before reading forces.");

        var started = DateTimeOffset.UtcNow;
        var adapter = new EtabsGetterAdapter(host, EtabsForceGetterMatrix.Allowed);
        var calls = new List<EtabsRawGetterCall>();
        var seed = new EtabsLiveGetterProbeRequest(request.MemberObjectNames[0], "", "", [], [], 4, 0, request.DeadlineUtc);
        var preflight = CaptureProtectedState(adapter, host, seed, calls, cancellationToken);
        seed = seed with
        {
            SelectedCases = preflight.CaseSelections.Where(pair => pair.Value).Select(pair => pair.Key).ToArray(),
            SelectedCombinations = preflight.CombinationSelections.Where(pair => pair.Value).Select(pair => pair.Key).ToArray()
        };
        ValidateReadiness(preflight, seed, allowMetricDatabase: true);
        if (seed.SelectedCases.Count + seed.SelectedCombinations.Count == 0)
            throw new EtabsLiveGetterProbeException("ETABS.SELECTION_EMPTY: select the required output cases/combinations in ETABS.");

        var bulkFrames = Call(adapter, seed, calls, "FrameObj.GetAllFrames", ["Global"], cancellationToken);
        var bulkPoints = Call(adapter, seed, calls, "PointObj.GetAllPoints", ["Global"], cancellationToken);
        ValidateContext(request.Context, bulkFrames, bulkPoints);
        Call(adapter, seed, calls, "Story.GetStories_2", [], cancellationToken);
        var frameNames = Strings(Call(adapter, seed, calls, "FrameObj.GetNameList", [], cancellationToken), 1).ToHashSet(StringComparer.Ordinal);
        ReadCatalogue(adapter, seed, calls, preflight, cancellationToken);
        ValidateSelectedStaticSources(seed, calls);

        var contextFrames = request.Context.Frames.ToDictionary(item => item.SourceFrameId, StringComparer.Ordinal);
        var cache = new SharedCaptureCache();
        cache.SourcePointNames.UnionWith(request.Context.Points.Select(point => point.SourcePointId));
        var summaries = new List<EtabsMemberCaptureSummary>();
        var rowCount = 0;
        foreach (var member in request.MemberObjectNames.Order(StringComparer.Ordinal))
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (!frameNames.Contains(member) || !contextFrames.TryGetValue(member, out var contextFrame) ||
                contextFrame.DesignOrientation != EtabsFrameDesignOrientation.Beam)
                throw new EtabsLiveGetterProbeException("ETABS.SCOPE_UNSUPPORTED: every requested member must be a captured source beam.");
            var memberRequest = seed with { MemberObjectName = member, ExpectedStory = contextFrame.SourceStoryId };
            var orientation = Call(adapter, memberRequest, calls, "FrameObj.GetDesignOrientation", [member], cancellationToken);
            if (Scalar<int>(orientation, 0) != (int)EtabsFrameDesignOrientation.Beam)
                throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: a requested frame's design orientation changed.");
            var summary = ReadMember(adapter, memberRequest, calls, cancellationToken, cache);
            rowCount = checked(rowCount + summary.FrameForceRows);
            if (rowCount > 100_000) throw new EtabsLiveGetterProbeException("ETABS.SCOPE_LIMIT: this profile supports at most 100,000 complete force rows.");
            summaries.Add(summary);
            progress?.Invoke(summaries.Count, request.MemberObjectNames.Count);
        }
        foreach (var material in cache.Materials.Order(StringComparer.Ordinal))
            Call(adapter, seed, calls, "PropMaterial.GetTypeOAPI", [material], cancellationToken);

        var finalFrames = Call(adapter, seed, calls, "FrameObj.GetAllFrames", ["Global"], cancellationToken);
        var finalPoints = Call(adapter, seed, calls, "PointObj.GetAllPoints", ["Global"], cancellationToken);
        if (AnalysisSnapshotNormalizer.Digest(bulkFrames.Outputs) != AnalysisSnapshotNormalizer.Digest(finalFrames.Outputs) ||
            AnalysisSnapshotNormalizer.Digest(bulkPoints.Outputs) != AnalysisSnapshotNormalizer.Digest(finalPoints.Outputs))
            throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: source geometry changed during the force batch.");
        var postflight = CaptureProtectedState(adapter, host, seed, calls, cancellationToken);
        RequireEqual("protected-state SHA-256", preflight.Sha256, postflight.Sha256);
        RequireEqual("source identity", identity, host.InspectIdentity());
        return new(EtabsForceGetterMatrix.ProfileId, request.RequestSha256, EtabsForceGetterMatrix.Sha256,
            started, DateTimeOffset.UtcNow, identity, request.Context, preflight, postflight, summaries, calls);
    }

    private static void ValidateContext(EtabsContextInventory context, EtabsRawGetterCall frames, EtabsRawGetterCall points)
    {
        var names = Strings(frames, 1); var pointNames = Strings(points, 1);
        var contextFrames = context.Frames.ToDictionary(item => item.SourceFrameId, StringComparer.Ordinal);
        var contextPoints = context.Points.ToDictionary(item => item.SourcePointId, StringComparer.Ordinal);
        if (names.Length != contextFrames.Count || names.Distinct(StringComparer.Ordinal).Count() != names.Length ||
            pointNames.Length != contextPoints.Count || pointNames.Distinct(StringComparer.Ordinal).Count() != pointNames.Length)
            throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: the source frame/point inventory changed.");
        var sections = Strings(frames, 2); var stories = Strings(frames, 3);
        var first = Strings(frames, 4); var second = Strings(frames, 5);
        for (var i = 0; i < names.Length; i++)
            if (!contextFrames.TryGetValue(names[i], out var frame) || frame.SourceSectionId != sections[i] ||
                frame.SourceStoryId != stories[i] || frame.SourcePoint1Id != first[i] || frame.SourcePoint2Id != second[i])
                throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: a frame's source assignment or connectivity changed.");
        for (var i = 0; i < pointNames.Length; i++)
            if (!contextPoints.TryGetValue(pointNames[i], out var point) ||
                point.Xmm != (double)ArrayValues(points, 2)[i]! * 1000 ||
                point.Ymm != (double)ArrayValues(points, 3)[i]! * 1000 ||
                point.Zmm != (double)ArrayValues(points, 4)[i]! * 1000)
                throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: a source point moved.");
    }

    private static void ValidateSelectedStaticSources(EtabsLiveGetterProbeRequest request, List<EtabsRawGetterCall> calls)
    {
        var byKey = calls.Where(call => call.Inputs.Count > 0 && call.Inputs[0] is string)
            .GroupBy(call => (call.Operation, Name: (string)call.Inputs[0]!)).ToDictionary(group => group.Key, group => group.First());
        bool Static(string name, bool combo, HashSet<string> visiting)
        {
            if (!combo)
                return byKey.TryGetValue(("LoadCases.GetTypeOAPI", name), out var kind) && Scalar<int>(kind, 0) == 1 && Scalar<int>(kind, 1) == 0 &&
                    byKey.TryGetValue(("LoadCases.GetTypeOAPI_1", name), out var extended) && Scalar<int>(extended, 4) == 0 &&
                    byKey.TryGetValue(("LoadCases.StaticLinear.GetInitialCase", name), out var initial) && Scalar<string>(initial, 0) is "" or "None";
            if (!visiting.Add(name) || !byKey.TryGetValue(("RespCombo.GetTypeOAPI", name), out var type) || Scalar<int>(type, 0) != 0 ||
                !byKey.TryGetValue(("RespCombo.GetCaseList", name), out var terms) || Scalar<int>(terms, 0) == 0) return false;
            var types = Integers(terms, 1); var names = Strings(terms, 2);
            var valid = types.Select((value, index) => value is 0 or 1 && Static(names[index], value == 1, visiting)).All(value => value);
            visiting.Remove(name);
            return valid;
        }
        if (request.SelectedCases.Any(name => !Static(name, false, new(StringComparer.Ordinal))) ||
            request.SelectedCombinations.Any(name => !Static(name, true, new(StringComparer.Ordinal))))
            throw new EtabsLiveGetterProbeException("ETABS.SELECTION_UNSUPPORTED: current output selections include an unqualified automatic, dynamic, envelope or initial-state case. Select the required ordinary static cases/combinations in ETABS. No forces were read.");
    }
}
