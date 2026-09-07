namespace StructuralEngineering.Contracts;

public sealed record BaselineReplayRequest(string SchemaVersion, string SnapshotId, string SnapshotSha256,
    string EngineRevisionId, BaselineProjectInputs AcceptedInputs, IReadOnlyList<string> MemberIds, BaselineDesignOptions Options);
