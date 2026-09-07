using System.Globalization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public static partial class EtabsCaptureProjector
{
    private sealed record BulkModel(IReadOnlyList<SourceSnapshotPoint> Points, IReadOnlyList<SourceSnapshotMember> Members, SourceSnapshotBulkProjectionEvidence Evidence);

    private static BulkModel ProjectBulkModel(ProjectionInput capture, Func<string, string?, Call> one)
    {
        var context = capture.Context ?? throw new InvalidDataException("Bulk capture lacks its source context.");
        var tables = EtabsBulkTable.Specifications.ToDictionary(spec => spec.Key, spec =>
        {
            var metadata = one("DatabaseTables.GetAllFieldsInTable", spec.Key);
            var data = one(spec.Editing ? "DatabaseTables.GetTableForEditingArray" : "DatabaseTables.GetTableForDisplayArray", spec.Key);
            Need(data.Inputs[spec.Editing ? 1 : 2].GetString() == "All", "Bulk tables must cover the whole source model.");
            if (!spec.Editing) Need(data.Inputs[1].GetRawText() == metadata.Outputs[2].GetRawText(), "The display request must name all source fields.");
            return new EtabsBulkTable(spec, metadata.Outputs, data.Outputs);
        }, StringComparer.Ordinal);
        var frames = one("FrameObj.GetAllFrames", "Global");
        var pointCall = one("PointObj.GetAllPoints", "Global");
        var frameNames = frames.Strings(1); var pointNames = pointCall.Strings(1);
        var frameIndex = frameNames.Select((id, index) => (id, index)).ToDictionary(item => item.id, item => item.index, StringComparer.Ordinal);
        var contextFrames = context.Frames.ToDictionary(item => item.SourceFrameId, StringComparer.Ordinal);
        var contextPoints = context.Points.ToDictionary(item => item.SourcePointId, StringComparer.Ordinal);
        Need(frameNames.ToHashSet(StringComparer.Ordinal).SetEquals(contextFrames.Keys) && pointNames.ToHashSet(StringComparer.Ordinal).SetEquals(contextPoints.Keys),
            "Bulk source inventories differ from the connected context.");
        var points = new Dictionary<string, SourceSnapshotPoint>(StringComparer.Ordinal);
        for (var index = 0; index < pointNames.Length; index++)
        {
            var name = pointNames[index]; var point = contextPoints[name];
            double Coordinate(int column) => pointCall.Outputs[column][index].GetDouble();
            Need(point.Xmm == Coordinate(2) * 1000 && point.Ymm == Coordinate(3) * 1000 && point.Zmm == Coordinate(4) * 1000,
                "A source point differs from the connected context.");
            AddPoint(new("point:" + name, name, Coordinate(2), Coordinate(3), Coordinate(4), tables["Point Object Connectivity"].Required(name).Required("Story")));
        }
        foreach (var (name, index) in frameIndex)
        {
            var frame = contextFrames[name];
            Need(frames.Outputs[2][index].GetString() == frame.SourceSectionId && frames.Outputs[3][index].GetString() == frame.SourceStoryId &&
                frames.Outputs[4][index].GetString() == frame.SourcePoint1Id && frames.Outputs[5][index].GetString() == frame.SourcePoint2Id,
                "A frame assignment differs from the connected context.");
        }
        Need(tables["Beam Object Connectivity"].Rows.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(context.Frames
            .Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam).Select(frame => frame.SourceFrameId)), "Source beam classification changed.");
        var members = new List<SourceSnapshotMember>();
        var elementTable = tables["Objects and Elements - Frames"];
        var elementsByOwner = elementTable.Rows.GroupBy(item => item.Value.Required("ObjName"), StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Select(item => item.Key).ToHashSet(StringComparer.Ordinal), StringComparer.Ordinal);
        foreach (var summary in capture.Members)
        {
            var name = summary.ObjectName;
            var beam = tables["Beam Object Connectivity"].Required(name);
            var frame = contextFrames[name];
            Need(frame.DesignOrientation == EtabsFrameDesignOrientation.Beam && beam.Optional("CurveType") is null &&
                beam.Required("BeamBay") == summary.Label && beam.Required("Story") == summary.Story &&
                beam.Required("UniquePtI") == frame.SourcePoint1Id && beam.Required("UniquePtJ") == frame.SourcePoint2Id &&
                summary.PointNames.SequenceEqual([frame.SourcePoint1Id, frame.SourcePoint2Id]), "The required beam is curved or has changed source identity.");
            var first = points[frame.SourcePoint1Id]; var second = points[frame.SourcePoint2Id];
            var delta = new[] { second.X - first.X, second.Y - first.Y, second.Z - first.Z };
            var length = Math.Sqrt(delta.Sum(value => value * value));
            Need(double.IsFinite(length) && length > 0 && Math.Abs(delta[2]) <= 1e-8, "The bulk member must be a straight horizontal source beam.");
            var section = tables["Frame Assignments - Section Properties"].Required(name);
            Need(section.Required("SectProp") == summary.SectionName && summary.SectionName == frame.SourceSectionId, "The bulk section assignment changed.");
            var transform = one("FrameObj.GetTransformationMatrix", name);
            Need(transform.Inputs[1].GetBoolean(), "The frame transformation must be explicitly global.");
            var matrix = transform.Doubles(0);
            var force = one("Results.FrameForce", name);
            var origins = new Dictionary<string, double>(StringComparer.Ordinal);
            for (var index = 0; index < force.Integer(0); index++)
            {
                var element = force.Outputs[3][index].GetString()!;
                var origin = force.Outputs[2][index].GetDouble() - force.Outputs[4][index].GetDouble();
                if (origins.TryGetValue(element, out var prior)) Need(Math.Abs(prior - origin) <= 1e-8, "An element has inconsistent force station origins.");
                else origins.Add(element, origin);
            }
            Need(elementsByOwner.TryGetValue(name, out var owned) && owned.SetEquals(origins.Keys) && owned.SetEquals(summary.ElementNames),
                "Every source analysis element must have complete force evidence.");
            var ordered = origins.OrderBy(item => item.Value).ToArray();
            Need(ordered.Length > 0 && Math.Abs(ordered[0].Value) <= 1e-8, "Analysis elements do not start at the source object origin.");
            var elements = new List<SourceSnapshotElement>();
            string? previousJ = null;
            for (var index = 0; index < ordered.Length; index++)
            {
                var (elementId, observedOrigin) = ordered[index];
                var start = index == 0 ? 0 : observedOrigin;
                var end = index + 1 == ordered.Length ? length : ordered[index + 1].Value;
                var element = elementTable.Required(elementId);
                var pi = element.Required("ElmJtI"); var pj = element.Required("ElmJtJ");
                Need(element.Required("ObjType") == "Frame" && element.Required("ObjName") == name && end > start && start >= 0 && end <= length &&
                    (index == 0 ? pi == frame.SourcePoint1Id : pi == previousJ) && (index + 1 != ordered.Length || pj == frame.SourcePoint2Id),
                    "Bulk element ownership/connectivity does not form a complete straight object chain.");
                previousJ = pj;
                // Actual ObjStation-ElmStation gives the element origin; the next origin (or object end)
                // gives its end. Interpolation applies only to the proved straight, offset-free object.
                AddPoint(Interpolated(pi, start)); AddPoint(Interpolated(pj, end));
                elements.Add(new(elementId, name, "point:" + pi, "point:" + pj, start / length, end / length, matrix));
            }
            var offsets = tables["Frame Assignments - End Length Offsets"].Required(name);
            var insertion = tables["Frame Assignments - Insertion Point"].Required(name);
            var cardinal = insertion.Required("CardinalPt").Split(' ', 2)[0];
            Need(int.TryParse(cardinal, NumberStyles.None, CultureInfo.InvariantCulture, out var cardinalPoint), "Insertion cardinal point is unresolved.");
            var frameRow = frameIndex[name];
            Need(frames.Outputs[19][frameRow].GetInt32() == cardinalPoint && Enumerable.Range(13, 6).All(column => frames.Outputs[column][frameRow].GetDouble() == 0),
                "Bulk insertion geometry differs or requires an offset transform.");
            var modifierFields = new[] { "AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod", "MMod", "WMod" };
            var modifiers = tables["Frame Assignments - Property Modifiers"].Rows.TryGetValue(name, out var modifierRow)
                ? modifierFields.Select(field => modifierRow.Number(field)).ToArray() : Enumerable.Repeat(1d, 8).ToArray();
            var dofs = new[] { "P", "V2", "V3", "T", "M2", "M3" };
            tables["Frame Assignments - Releases and Partial Fixity"].Rows.TryGetValue(name, out var releases);
            bool[] Released(string end) => dofs.Select(dof => releases?.Boolean(dof + end) ?? false).ToArray();
            double[] Springs(string end) => dofs.Select((dof, index) => releases?.Number(dof + end + "Spring", index < 3 ? "kN/m" : "kN-m/rad", 0) ?? 0).ToArray();
            var offsetMode = offsets.Required("OffsetOpt");
            Need(offsetMode is "Auto" or "User", "The end-offset mode is unqualified.");
            var auto = section.Required("AutoSelect");
            members.Add(new("member:" + name, name, summary.Label, summary.Story, first.Id, second.Id, "section:" + summary.SectionName,
                auto == "N.A." ? null : auto, modifiers, offsetMode == "Auto", offsets.Number("OffsetI", "m"), offsets.Number("OffsetJ", "m"), offsets.Number("RigidFact"),
                Released("I"), Released("J"), Springs("I"), Springs("J"),
                new(cardinalPoint, insertion.Boolean("Mirror2"), insertion.Boolean("Mirror3"), !insertion.Boolean("NoTransform"),
                    new[] { "XI", "YI", "ZI" }.Select(field => insertion.Number(field, "m", 0)).ToArray(),
                    new[] { "XJ", "YJ", "ZJ" }.Select(field => insertion.Number(field, "m", 0)).ToArray(),
                    insertion.Optional("OffsetCSys") ?? "Global"), elements));

            SourceSnapshotPoint Interpolated(string id, double station) => new("point:" + id, id,
                first.X + delta[0] * station / length, first.Y + delta[1] * station / length, first.Z + delta[2] * station / length, summary.Story);
        }
        return new(points.Values.OrderBy(point => point.Id, StringComparer.Ordinal).ToArray(), members,
            new("wp10-bulk-source-projection/v1", elementTable.Rows.Count, elementTable.ContextOnlyRowCount,
                "ObjType=Frame supplies frame meshes; every other row remains in the complete getter payload as source context.",
                "GetTableForEditingArray preserves full numeric assignment values; qualified blank/absent assignment defaults only.",
                "Exact global source points and frame matrices; straight mesh topology from source identities and actual ObjStation-ElmStation origins.", 1e-8));

        void AddPoint(SourceSnapshotPoint point)
        {
            if (points.TryGetValue(point.Name, out var existing))
                Need(Math.Abs(existing.X - point.X) <= 1e-8 && Math.Abs(existing.Y - point.Y) <= 1e-8 && Math.Abs(existing.Z - point.Z) <= 1e-8,
                    "Shared source/analysis point coordinates disagree with straight-object interpolation.");
            else points.Add(point.Name, point);
        }
    }
}
