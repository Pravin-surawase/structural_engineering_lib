using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Source-ID indexes over one accepted context; frame selection never calls ETABS.</summary>
public sealed class EtabsConnectionSession
{
    public EtabsConnectionSession(EtabsContextArtifact artifact, string operationDirectory)
    {
        Artifact = artifact; OperationDirectory = operationDirectory;
        Frames = artifact.Inventory.Frames.ToDictionary(frame => frame.SourceFrameId, StringComparer.Ordinal);
        Points = artifact.Inventory.Points.ToDictionary(point => point.SourcePointId, StringComparer.Ordinal);
        Sections = artifact.Inventory.Sections.ToDictionary(section => section.SourceSectionId, StringComparer.Ordinal);
        FramesAtPoint = artifact.Inventory.Frames.SelectMany(frame => new[] { (Point: frame.SourcePoint1Id, Frame: frame.SourceFrameId), (Point: frame.SourcePoint2Id, Frame: frame.SourceFrameId) })
            .GroupBy(item => item.Point, StringComparer.Ordinal).ToDictionary(group => group.Key, group => group.Select(item => item.Frame).ToArray(), StringComparer.Ordinal);
    }
    public EtabsContextArtifact Artifact { get; }
    public string OperationDirectory { get; }
    public IReadOnlyDictionary<string, EtabsContextFrame> Frames { get; }
    public IReadOnlyDictionary<string, EtabsContextPoint> Points { get; }
    public IReadOnlyDictionary<string, EtabsContextSection> Sections { get; }
    public IReadOnlyDictionary<string, string[]> FramesAtPoint { get; }
    public IReadOnlyList<string> Neighbours(string frameId)
    {
        var frame = Frames[frameId];
        return FramesAtPoint[frame.SourcePoint1Id].Concat(FramesAtPoint[frame.SourcePoint2Id]).Where(id => id != frameId).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
    }
}
