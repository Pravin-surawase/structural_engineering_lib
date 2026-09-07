using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Beam;

internal sealed class BaselineSnapshotIndex
{
    public AnalysisSnapshot Snapshot { get; }
    public bool Valid { get; }
    public IReadOnlyDictionary<string, SnapshotMember> Members { get; } = new Dictionary<string, SnapshotMember>();
    public IReadOnlyDictionary<string, SnapshotSection> Sections { get; } = new Dictionary<string, SnapshotSection>();
    public IReadOnlyDictionary<string, SnapshotPoint> Points { get; } = new Dictionary<string, SnapshotPoint>();
    public IReadOnlyDictionary<string, SnapshotAxis> Axes { get; } = new Dictionary<string, SnapshotAxis>();
    public ILookup<string, SnapshotActionRow> Actions { get; } = Array.Empty<SnapshotActionRow>().ToLookup(x => x.MemberId);
    public ILookup<string, SnapshotStation> Stations { get; } = Array.Empty<SnapshotStation>().ToLookup(x => x.MemberId);

    public BaselineSnapshotIndex(AnalysisSnapshot snapshot)
    {
        Snapshot = snapshot;
        Valid = AnalysisSnapshotCodec.Validate(snapshot).Snapshot is not null;
        if (!Valid) return;
        Members = snapshot.Members.ToDictionary(x => x.MemberId);
        Sections = snapshot.Sections.ToDictionary(x => x.SectionId);
        Points = snapshot.Points.ToDictionary(x => x.PointId);
        Axes = snapshot.Axes.ToDictionary(x => x.AxisId);
        Actions = snapshot.ActionRows.ToLookup(x => x.MemberId);
        Stations = snapshot.Stations.ToLookup(x => x.MemberId);
    }
}
