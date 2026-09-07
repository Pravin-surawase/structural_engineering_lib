using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BaselineReplay
{
    public const string SchemaVersion = "native.baseline-design-request/v1";
    private static readonly JsonSerializerOptions Options = CreateOptions();

    public static BaselineReplayRequest Request(AnalysisSnapshot snapshot, BaselineProjectInputs inputs,
        IReadOnlyList<string> memberIds, BaselineDesignOptions? options = null) =>
        new(SchemaVersion, snapshot.SnapshotId, snapshot.SnapshotSha256, BaselineDesignOperations.EngineIdentity,
            inputs, memberIds, options ?? new());

    public static byte[] Serialize(BaselineReplayRequest request) => ResultFactory.CanonicalJsonBytes(request);

    public static BaselineReplayRequest Parse(ReadOnlySpan<byte> bytes) =>
        JsonSerializer.Deserialize<BaselineReplayRequest>(bytes, Options) ?? throw new JsonException("A replay request is required.");

    public static BaselineBatchDesignResult Run(BaselineReplayRequest request, AnalysisSnapshot? snapshot,
        CancellationToken cancellationToken = default)
    {
        if (request.SchemaVersion != SchemaVersion || request.EngineRevisionId != BaselineDesignOperations.EngineIdentity)
            return Missing(BaselineRunState.Stale, "REPLAY.VERSION_UNAVAILABLE", "The recorded request requires a different schema or engine revision.");
        if (snapshot is null || snapshot.SnapshotId != request.SnapshotId || snapshot.SnapshotSha256 != request.SnapshotSha256)
            return Missing(BaselineRunState.NeedsInput, "REPLAY.SNAPSHOT_REQUIRED", "The exact external snapshot identified by this request is required.");
        return BaselineDesignOperations.Design(snapshot, request.AcceptedInputs, request.MemberIds, request.Options, cancellationToken);

        BaselineBatchDesignResult Missing(BaselineRunState state, string code, string message) =>
            new(ResultFactory.SemanticId("baseline_replay", request), request.SnapshotId, request.AcceptedInputs, request.Options,
                request.MemberIds.Select(id => new BaselineMemberDesignResult(id, string.Empty, BaselineDesignOperations.EngineIdentity,
                    state, 0, 0, null, [new(code, "error", message, "native.baseline.replay/v1", "snapshot/engine")])).ToArray());
    }

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
            RespectRequiredConstructorParameters = true
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower, allowIntegerValues: false));
        return options;
    }
}
