using System.Security.Cryptography;
using System.Text;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Pure, conservative interpretation of source-object connectivity.</summary>
public static class EtabsModelInterpreter
{
    public static EtabsModelInterpretation Interpret(EtabsModelInterpretationRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(request.Context);
        if (request.Context.SchemaVersion != EtabsContextWorkerCodec.ArtifactSchemaVersion ||
            request.Context.ArtifactSha256 != EtabsContextWorkerCodec.CreateArtifact(request.Context.Inventory).ArtifactSha256)
            throw new ArgumentException("The context artifact identity is invalid.", nameof(request));
        var context = request.Context.Inventory;
        ValidateInventory(context);
        ValidateSnapshot(context, request.Snapshot);

        var frameById = context.Frames.ToDictionary(frame => frame.SourceFrameId, StringComparer.Ordinal);
        var requested = request.RequestedBeamIds is null
            ? frameById.Values.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam).Select(frame => frame.SourceFrameId).ToArray()
            : request.RequestedBeamIds.ToArray();
        if (requested.Any(string.IsNullOrWhiteSpace) || requested.Distinct(StringComparer.Ordinal).Count() != requested.Length)
            throw new ArgumentException("Requested beam identities must be nonempty and unique.", nameof(request));
        if (request.Snapshot is not null && requested.Any(id => !request.Snapshot.Members.Any(member => member.ObjectId == id)))
            throw new ArgumentException("Each requested snapshot-backed beam must be present in the accepted snapshot.", nameof(request));

        var framesAtPoint = context.Points.ToDictionary(point => point.SourcePointId, _ => new List<string>(), StringComparer.Ordinal);
        foreach (var frame in context.Frames)
        {
            framesAtPoint[frame.SourcePoint1Id].Add(frame.SourceFrameId);
            framesAtPoint[frame.SourcePoint2Id].Add(frame.SourceFrameId);
        }
        var adjacency = framesAtPoint.OrderBy(item => item.Key, StringComparer.Ordinal)
            .Select(item => new EtabsSourcePointAdjacency(item.Key, item.Value.Order(StringComparer.Ordinal).ToArray())).ToArray();
        var connectedByPoint = adjacency.ToDictionary(item => item.SourcePointId, StringComparer.Ordinal);
        var connectivity = new List<EtabsBeamSourceConnectivity>();
        var readiness = new List<EtabsBeamReadiness>();
        foreach (var id in requested.Order(StringComparer.Ordinal))
        {
            if (!frameById.TryGetValue(id, out var frame) || frame.DesignOrientation != EtabsFrameDesignOrientation.Beam)
            {
                readiness.Add(new(id, EtabsBeamReadinessDisposition.RequestedBeamMissing, ["The requested source frame is absent or is not classified as a beam."]));
                continue;
            }
            var connected = connectedByPoint[frame.SourcePoint1Id].ConnectedFrameIds
                .Concat(connectedByPoint[frame.SourcePoint2Id].ConnectedFrameIds).Where(other => other != id)
                .Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
            connectivity.Add(new(id, frame.SourcePoint1Id, frame.SourcePoint2Id,
                connected.Where(other => frameById[other].DesignOrientation == EtabsFrameDesignOrientation.Beam).ToArray(),
                connected.Where(other => frameById[other].DesignOrientation == EtabsFrameDesignOrientation.Column).ToArray()));
            var missing = new List<string> { "Authoritative support faces are absent from the source context.", "Physical-span mapping is absent from the source context.", "End fixity and construction uniform-size grouping are absent from the source context." };
            if (request.Snapshot is null) missing.Add("Offsets and releases are absent because no accepted analysis snapshot is bound.");
            readiness.Add(new(id, EtabsBeamReadinessDisposition.NeedsSupportFacesAndPhysicalSpanMapping, missing));
        }
        var sourceRevision = SourceRevision(context);
        var identity = new { request.Context.ArtifactSha256, SourceRevision = sourceRevision, SnapshotId = request.Snapshot?.SnapshotId, SnapshotSha256 = request.Snapshot?.SnapshotSha256, Requested = requested.Order(StringComparer.Ordinal).ToArray() };
        var interpretationId = "etabs_source_interpretation:" + Convert.ToHexStringLower(SHA256.HashData(AnalysisSnapshotCodec.CanonicalJsonBytes(identity)));
        return new(interpretationId, request.Context.ArtifactSha256, sourceRevision, request.Snapshot?.SnapshotId, request.Snapshot?.SnapshotSha256,
            adjacency, connectivity, readiness, context.Frames.OrderBy(frame => frame.SourceFrameId, StringComparer.Ordinal).ToArray());
    }

    private static void ValidateInventory(EtabsContextInventory context)
    {
        if (context.Points.Select(point => point.SourcePointId).Distinct(StringComparer.Ordinal).Count() != context.Points.Count ||
            context.Source.PresentUnits != 6 || context.Source.DatabaseUnits != 6 ||
            context.Points.Any(point => !double.IsFinite(point.Xmm) || !double.IsFinite(point.Ymm) || !double.IsFinite(point.Zmm)) ||
            context.Frames.Select(frame => frame.SourceFrameId).Distinct(StringComparer.Ordinal).Count() != context.Frames.Count ||
            context.Frames.Any(frame => !context.Points.Any(point => point.SourcePointId == frame.SourcePoint1Id) || !context.Points.Any(point => point.SourcePointId == frame.SourcePoint2Id)))
            throw new ArgumentException("The context inventory does not conserve unique source point/frame identities.");
    }

    private static void ValidateSnapshot(EtabsContextInventory context, AnalysisSnapshot? snapshot)
    {
        if (snapshot is null) return;
        if (AnalysisSnapshotCodec.Validate(snapshot).Snapshot is null)
            throw new ArgumentException("The supplied analysis snapshot is not accepted.");
        var source = snapshot.SourceIdentity;
        var rawUnits = snapshot.RawCapture.SourceUnits;
        if (source.SourceSystem != "etabs" || source.ModelFileSha256.State != OptionalEvidenceState.Supplied ||
            !string.Equals(source.ModelFileSha256.Value, context.Source.ModelSha256, StringComparison.OrdinalIgnoreCase) ||
            source.ProcessIdentity.State != OptionalEvidenceState.Supplied || source.ProcessIdentity.Value != ProcessIdentity(context) ||
            source.SourceVersion != context.Source.EtabsApiVersion || source.ModelRevisionId != $"model-file-sha256:{context.Source.ModelSha256}" ||
            snapshot.Units.OriginalSourceUnits != rawUnits ||
            snapshot.Units.Length != "mm" || snapshot.Units.Force != "kN" || snapshot.Units.Moment != "kNm" ||
            snapshot.Units.Stress != "N/mm2" || snapshot.Units.MassDensity != "kg/m3")
            throw new ArgumentException("The supplied snapshot is not bound to this ETABS source model, process evidence, and qualified units.");
        var pointBySourceName = snapshot.Points.ToDictionary(point => point.SourceName, StringComparer.Ordinal);
        var frameByObject = context.Frames.ToDictionary(frame => frame.SourceFrameId, StringComparer.Ordinal);
        foreach (var member in snapshot.Members)
        {
            if (!frameByObject.TryGetValue(member.ObjectId, out var frame) || !pointBySourceName.TryGetValue(frame.SourcePoint1Id, out var start) ||
                !pointBySourceName.TryGetValue(frame.SourcePoint2Id, out var end) || member.PointIId != start.PointId || member.PointJId != end.PointId ||
                !CoordinatesMatch(context, frame.SourcePoint1Id, start) || !CoordinatesMatch(context, frame.SourcePoint2Id, end))
                throw new ArgumentException("The supplied snapshot member connectivity or endpoint geometry differs from the context inventory.");
        }
    }

    private static bool CoordinatesMatch(EtabsContextInventory context, string sourcePointId, SnapshotPoint snapshotPoint)
    {
        var point = context.Points.Single(item => item.SourcePointId == sourcePointId);
        return point.Xmm == snapshotPoint.XMm && point.Ymm == snapshotPoint.YMm && point.Zmm == snapshotPoint.ZMm;
    }

    private static string ProcessIdentity(EtabsContextInventory context) => $"{context.Source.ProcessId}@{context.Source.ProcessStartedUtc.UtcDateTime:O}";

    private static string SourceRevision(EtabsContextInventory context)
    {
        var basis = new { context.RequestSha256, context.Source.ProcessId, context.Source.ProcessStartedUtc, context.Source.ExecutableSha256, context.Source.ModelSha256, context.Source.ModelBytes, context.Source.ModelModifiedUtc, context.Source.PresentUnits, context.Source.DatabaseUnits };
        return "etabs_source_revision:" + Convert.ToHexStringLower(SHA256.HashData(AnalysisSnapshotCodec.CanonicalJsonBytes(basis)));
    }
}
