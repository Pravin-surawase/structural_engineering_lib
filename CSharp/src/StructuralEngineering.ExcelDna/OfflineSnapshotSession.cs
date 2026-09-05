using System.Collections.ObjectModel;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>
/// Read-only in-memory selection view over one already-validated offline snapshot.
/// </summary>
public sealed class OfflineSnapshotSession
{
    private readonly IReadOnlyDictionary<string, IReadOnlyList<SnapshotActionRow>> _actionsByMember;
    private readonly IReadOnlyDictionary<string, SnapshotMember> _membersById;

    public OfflineSnapshotSession(OfflineSnapshotReference reference, AnalysisSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(reference);
        ArgumentNullException.ThrowIfNull(snapshot);
        OfflineSnapshotStore.ValidateReference(reference);
        var validation = AnalysisSnapshotCodec.Validate(snapshot);
        if (validation.Snapshot is null)
            throw new InvalidDataException("An offline session requires an accepted portable snapshot.");
        if (!string.Equals(reference.ProjectId, snapshot.Metadata.ProjectId, StringComparison.Ordinal) ||
            !string.Equals(reference.SnapshotId, snapshot.SnapshotId, StringComparison.Ordinal) ||
            !string.Equals(reference.SnapshotSha256, snapshot.SnapshotSha256, StringComparison.Ordinal))
            throw new ArgumentException("The offline snapshot reference does not identify the supplied snapshot.", nameof(reference));

        Reference = reference;
        Snapshot = snapshot;
        StationsById = new ReadOnlyDictionary<string, SnapshotStation>(snapshot.Stations.ToDictionary(station => station.StationId, StringComparer.Ordinal));
        _membersById = new ReadOnlyDictionary<string, SnapshotMember>(snapshot.Members.ToDictionary(member => member.MemberId, StringComparer.Ordinal));
        var actionGroups = snapshot.ActionRows
            .GroupBy(action => action.MemberId, StringComparer.Ordinal)
            .ToDictionary(
                group => group.Key,
                group => (IReadOnlyList<SnapshotActionRow>)group.ToList().AsReadOnly(),
                StringComparer.Ordinal);
        _actionsByMember = new ReadOnlyDictionary<string, IReadOnlyList<SnapshotActionRow>>(
            snapshot.Members.ToDictionary(
                member => member.MemberId,
                member => actionGroups.TryGetValue(member.MemberId, out var rows)
                    ? rows
                    : Array.Empty<SnapshotActionRow>(),
                StringComparer.Ordinal));
    }

    public OfflineSnapshotReference Reference { get; }
    public AnalysisSnapshot Snapshot { get; }
    public IReadOnlyDictionary<string, SnapshotStation> StationsById { get; }
    public IReadOnlyDictionary<string, SnapshotMember> MembersById => _membersById;

    /// <summary>Returns the snapshot's retained action rows for a known member without any I/O.</summary>
    public IReadOnlyList<SnapshotActionRow> ActionsForMember(string memberId)
    {
        if (string.IsNullOrWhiteSpace(memberId) || !_actionsByMember.TryGetValue(memberId, out var rows))
            throw new KeyNotFoundException($"Member '{memberId}' is not present in this offline snapshot session.");
        return rows;
    }
}
