using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Interprets modelled geometry only. Does not choose a member's engineering support or role.</summary>
public static class EtabsTopologyQualification
{
    public const string ProfileId = "etabs-topology-geometry/v1";
    public const int MaximumAdjacentObjects = 200;
    public const int MaximumAreaVertices = 40;
    // Fixed 0.001 mm admission tolerance for imported reference geometry, not construction accuracy.
    private const double LengthTolerance = 1e-3;
    private const double DirectionTolerance = 1e-8;

    public static EtabsTopologyFacts Interpret(EtabsSourceFacts source, EtabsTopologyGeometry geometry)
    {
        EtabsSourceQualification.ValidateScope(source.Scope);
        var frames = geometry.Frames.ToDictionary(f => f.Name, StringComparer.Ordinal);
        var areas = geometry.Areas.ToDictionary(a => a.Name, StringComparer.Ordinal);
        var points = geometry.Points.ToDictionary(p => p.Name, StringComparer.Ordinal);
        var sourcePoints = source.Points.ToDictionary(p => p.Name, StringComparer.Ordinal);
        var analysisPoints = geometry.AnalysisPoints.ToDictionary(p => p.Name, StringComparer.Ordinal);
        return new(ProfileId, source.Members.Select(Member).ToArray(),
            "modelled_reference_line_envelopes_only;physical_support_behavior=unqualified;member_intent=unqualified;effective_span=not_evaluated;design=not_evaluated");

        EtabsMemberTopology Member(EtabsSourceMember member)
        {
            var restrictions = new List<EtabsSourceRestriction>
            {
                new("TOPOLOGY.ENGINEERING_ROLE_REQUIRED", member.Name, "Source orientation and modifiers do not establish physical member purpose or support behavior."),
                new("TOPOLOGY.REFERENCE_LINE_ONLY", member.Name, "Envelope intersections use the object reference line; cardinal placement, releases, end offsets and rigidity do not define IS effective span.")
            };
            frames.TryGetValue(member.Name, out var frame);
            var role = new EtabsMemberRoleEvidence(member.DesignOrientation, frame?.ObjectModifiers, frame?.SectionModifiers,
                ZeroModifier(frame, 6), ZeroModifier(frame, 7), "project_intent_required");
            if (role.ZeroMassModifier == true || role.ZeroWeightModifier == true)
                restrictions.Add(new("TOPOLOGY.ZERO_MODIFIER_REVIEW", member.Name, "A source mass/weight modifier is zero; retain the member and require its intended role."));
            if (frame is null || member.EndpointNames.Count != 2 ||
                !Point(member.EndpointNames[0], out var first) || !Point(member.EndpointNames[1], out var second))
                return Missing("TOPOLOGY.ENDPOINT_UNAVAILABLE", "The requested object has no complete source endpoints.");
            var delta = Subtract(second, first); var length = Norm(delta);
            if (!double.IsFinite(length) || length <= LengthTolerance)
                return Missing("TOPOLOGY.ZERO_LENGTH", "The object reference line is degenerate.");
            var direction = Scale(delta, 1 / length);
            var axisState = ValidAxes(frame.GlobalTransformation, direction) ? "qualified_global_axes" : "unqualified";
            if (axisState != "qualified_global_axes")
                restrictions.Add(new("TOPOLOGY.AXES_UNQUALIFIED", member.Name, "The global matrix is not right-handed orthonormal with local 1 along the I-to-J line."));
            var lineBasis = frame.CurveType == 0 ? "explicit_straight_object" :
                frame.CurveType is null && StraightMesh(member, first, direction, length) ? "collinear_complete_analysis_mesh" : "unqualified";
            var admissible = lineBasis != "unqualified" && Math.Abs(direction[2]) <= DirectionTolerance &&
                ZeroOffsets(frame.Assignments) && axisState == "qualified_global_axes" && member.DesignOrientation == 2;
            if (!admissible)
                restrictions.Add(new("TOPOLOGY.BEAM_LINE_UNQUALIFIED", member.Name, "The envelope profile requires a straight horizontal source beam, qualified axes and zero joint offsets."));
            var endI = Endpoint(member.EndpointNames[0], first, direction, member.Assignments.EndOffsetIMm);
            var endJ = Endpoint(member.EndpointNames[1], second, Scale(direction, -1), member.Assignments.EndOffsetJMm);
            double? clear = admissible && endI.ModelledFaceDistanceMm is { } i && endJ.ModelledFaceDistanceMm is { } j ? length - i - j : null;
            if (clear is <= LengthTolerance)
            {
                clear = null;
                restrictions.Add(new("TOPOLOGY.ENVELOPES_OVERLAP", member.Name, "Endpoint envelopes overlap or leave no positive reference-line clear length."));
            }
            return new(member.Name, role, axisState, lineBasis, length, endI, endJ, clear, restrictions);

            EtabsMemberTopology Missing(string code, string message)
            {
                restrictions.Add(new(code, member.Name, message));
                return new(member.Name, role, "unqualified", "unqualified", null, null, null, null, restrictions);
            }

            EtabsEndpointTopology Endpoint(string pointName, double[] origin, double[] inward, double? reported)
            {
                var connections = sourcePoints.TryGetValue(pointName, out var point) ? point.Connections : [];
                var envelopes = connections.Where(c => c.ObjectType != 2 || c.ObjectName != member.Name)
                    .Select(Connection).ToArray();
                var distances = envelopes.Where(e => e.State == "qualified_modelled_envelope").Select(e => e.InwardExitMm!.Value).ToArray();
                double? face = admissible && distances.Length > 0 && envelopes.All(e => e.State is "qualified_modelled_envelope" or "connection_context")
                    ? distances.Max() : null;
                return new(pointName, connections, envelopes, face, face is { } value ? Add(origin, Scale(inward, value)) : null,
                    reported, reported is { } offset && face is { } distance ? offset - distance : null,
                    face is null ? "restricted" : "modelled_envelope_only");

                EtabsSupportEnvelope Connection(EtabsSourceConnection connection)
                {
                    var kind = connection.ObjectType == 2 ? "frame" : connection.ObjectType == 5 ? "area" : "object:" + connection.ObjectType;
                    if (connection.ObjectType == 2 && frames.TryGetValue(connection.ObjectName, out var adjacent))
                    {
                        if (!HasPoint(adjacent.EndpointNames, connection.PointNumber, pointName))
                            return Rejected("TOPOLOGY.CONNECTIVITY_CONFLICT", "Point connectivity and reverse frame endpoint identity disagree.");
                        if (adjacent.DesignOrientation is 2 or 3 or 4 or 5) return Context();
                        if (!ColumnBox(adjacent, out var box)) return Rejected("TOPOLOGY.COLUMN_GEOMETRY_UNQUALIFIED", "Column geometry requires a straight vertical centred rectangular section with qualified axes and zero joint offsets.");
                        return Intersect(box);
                    }
                    if (connection.ObjectType == 5 && areas.TryGetValue(connection.ObjectName, out var area))
                    {
                        if (!HasPoint(area.PointNames, connection.PointNumber, pointName))
                            return Rejected("TOPOLOGY.CONNECTIVITY_CONFLICT", "Point connectivity and reverse area vertex identity disagree.");
                        if (area.IsOpening == true || area.DesignOrientation == 2) return Context();
                        if (!WallBox(area, out var box)) return Rejected("TOPOLOGY.WALL_GEOMETRY_UNQUALIFIED",
                            "Wall envelope requires a vertical rectangle, specified uniform thickness and proved centred placement without overwrites.");
                        return Intersect(box);
                    }
                    return Rejected("TOPOLOGY.CONNECTION_UNAVAILABLE", "The connected object's geometry/type is outside the acquired profile.");

                    EtabsSupportEnvelope Context() => new(kind, connection.ObjectName, "connection_context", null, null, []);
                    EtabsSupportEnvelope Rejected(string code, string message) => new(kind, connection.ObjectName, "restricted", null, null,
                        [new(code, connection.ObjectName, message)]);
                    EtabsSupportEnvelope Intersect(Box box)
                    {
                        var exit = RayExit(box, origin, inward);
                        return exit is { } value ? new(kind, connection.ObjectName, "qualified_modelled_envelope", value,
                            Add(origin, Scale(inward, value)), []) : Rejected("TOPOLOGY.NO_INWARD_ENVELOPE", "The reference point lies outside the connected modelled envelope.");
                    }
                }
            }
        }

        bool StraightMesh(EtabsSourceMember member, double[] origin, double[] direction, double length)
        {
            if (member.Elements.Count == 0 || member.Restrictions.Any(r => r.Code == "SOURCE.ELEMENT_MAPPING_CONFLICT")) return false;
            var segments = new List<(double Start, double End)>();
            foreach (var element in member.Elements)
            {
                if (element.ReverseObjectName != member.Name || element.MappingSource != "Objects and Elements - Frames/v1" ||
                    element.AnalysisPointI is null || element.AnalysisPointJ is null ||
                    !analysisPoints.TryGetValue(element.AnalysisPointI, out var i) || !analysisPoints.TryGetValue(element.AnalysisPointJ, out var j) ||
                    i.GlobalCoordinatesMm is not { Count: 3 } a || j.GlobalCoordinatesMm is not { Count: 3 } b ||
                    a.Concat(b).Any(v => !double.IsFinite(v))) return false;
                var da = Subtract(a, origin); var db = Subtract(b, origin);
                var start = Dot(da, direction); var end = Dot(db, direction);
                if (end - start <= LengthTolerance || Norm(Subtract(da, Scale(direction, start))) > LengthTolerance ||
                    Norm(Subtract(db, Scale(direction, end))) > LengthTolerance) return false;
                segments.Add((start, end));
            }
            var cursor = 0d;
            foreach (var segment in segments.OrderBy(s => s.Start))
            {
                if (Math.Abs(segment.Start - cursor) > LengthTolerance) return false;
                cursor = segment.End;
            }
            return Math.Abs(cursor - length) <= LengthTolerance;
        }

        bool Point(string name, out double[] coordinate)
        {
            coordinate = points.TryGetValue(name, out var point) && point.GlobalCoordinatesMm is { Count: 3 } values &&
                values.All(double.IsFinite) ? values.ToArray() : [];
            return coordinate.Length == 3;
        }

        bool ColumnBox(EtabsTopologyFrame frame, out Box box)
        {
            box = default!;
            if (frame.DesignOrientation != 1 || frame.CurveType != 0 || frame.SectionType != 8 ||
                frame.WidthMm is not > 0 || frame.DepthMm is not > 0 || frame.EndpointNames.Count != 2 ||
                frame.Assignments.CardinalPoint is not (5 or 10) || !ZeroOffsets(frame.Assignments) ||
                !Point(frame.EndpointNames[0], out var i) || !Point(frame.EndpointNames[1], out var j)) return false;
            var delta = Subtract(j, i); var length = Norm(delta);
            if (length <= LengthTolerance || Math.Abs(delta[0]) > LengthTolerance || Math.Abs(delta[1]) > LengthTolerance ||
                !ValidAxes(frame.GlobalTransformation, Scale(delta, 1 / length))) return false;
            var matrix = frame.GlobalTransformation!;
            box = new(Scale(Add(i, j), .5), [Axis(matrix, 0), Axis(matrix, 1), Axis(matrix, 2)],
                [length / 2, frame.DepthMm.Value / 2, frame.WidthMm.Value / 2]);
            return true;
        }

        bool WallBox(EtabsTopologyArea area, out Box box)
        {
            box = default!;
            if (area.DesignOrientation != 1 || area.IsOpening != false || area.WallPropertyType != 1 ||
                area.ShellType is not (1 or 2 or 3) || area.ThicknessMm is not > 0 ||
                area.PlacementBasis != "centred_uniform_no_overwrites" || area.PointNames.Count != 4 ||
                area.ProviderOffsets is not { Count: 4 } offsets || offsets.Any(v => v != 0)) return false;
            var vertices = new List<double[]>();
            foreach (var name in area.PointNames) { if (!Point(name, out var value)) return false; vertices.Add(value); }
            var edges = Enumerable.Range(0, 4).Select(i => Subtract(vertices[(i + 1) % 4], vertices[i])).ToArray();
            if (edges.Any(e => Norm(e) <= LengthTolerance)) return false;
            var vertical = edges.Where(e => Math.Abs(e[0]) <= LengthTolerance && Math.Abs(e[1]) <= LengthTolerance).ToArray();
            var horizontal = edges.Where(e => Math.Abs(e[2]) <= LengthTolerance).ToArray();
            if (vertical.Length != 2 || horizontal.Length != 2 || Norm(Add(edges[0], edges[2])) > LengthTolerance ||
                Norm(Add(edges[1], edges[3])) > LengthTolerance) return false;
            var along = Scale(horizontal[0], 1 / Norm(horizontal[0])); var up = new[] { 0d, 0d, 1d };
            var centre = Scale(vertices.Aggregate(new double[3], Add), .25);
            box = new(centre, [along, up, Cross(along, up)], [Norm(horizontal[0]) / 2, Norm(vertical[0]) / 2, area.ThicknessMm.Value / 2]);
            return true;
        }
    }

    public static bool ValidAxes(IReadOnlyList<double>? matrix, IReadOnlyList<double> direction)
    {
        if (matrix is not { Count: 9 } || matrix.Any(v => !double.IsFinite(v)) || direction.Count != 3) return false;
        // CSI's row-major matrix maps local components to global components: columns are local axes.
        var e1 = Axis(matrix, 0); var e2 = Axis(matrix, 1); var e3 = Axis(matrix, 2);
        return Math.Abs(Norm(e1) - 1) <= DirectionTolerance && Math.Abs(Norm(e2) - 1) <= DirectionTolerance &&
            Math.Abs(Norm(e3) - 1) <= DirectionTolerance && Math.Abs(Dot(e1, e2)) <= DirectionTolerance &&
            Norm(Subtract(Cross(e1, e2), e3)) <= DirectionTolerance && Norm(Subtract(e1, direction)) <= DirectionTolerance;
    }

    private static bool? ZeroModifier(EtabsTopologyFrame? frame, int index) =>
        frame?.ObjectModifiers is { Count: 8 } a && frame.SectionModifiers is { Count: 8 } b ? a[index] == 0 || b[index] == 0 : null;
    private static bool HasPoint(IReadOnlyList<string> points, int number, string name) => number >= 1 && number <= points.Count && points[number - 1] == name;
    private static bool ZeroOffsets(EtabsSourceAssignments assignments) =>
        assignments.InsertionOffsetIMm is { Count: 3 } i && assignments.InsertionOffsetJMm is { Count: 3 } j && i.Concat(j).All(v => v == 0);
    private static double[] Axis(IReadOnlyList<double> matrix, int column) => [matrix[column], matrix[column + 3], matrix[column + 6]];
    private sealed record Box(double[] Centre, double[][] Axes, double[] HalfSizes);
    private static double? RayExit(Box box, double[] origin, double[] inward)
    {
        var relative = Subtract(origin, box.Centre); var exit = double.PositiveInfinity;
        for (var axis = 0; axis < 3; axis++)
        {
            var position = Dot(relative, box.Axes[axis]); var speed = Dot(inward, box.Axes[axis]); var half = box.HalfSizes[axis];
            if (!double.IsFinite(half) || half <= 0 || Math.Abs(position) > half + LengthTolerance) return null;
            if (Math.Abs(speed) > DirectionTolerance) exit = Math.Min(exit, (Math.CopySign(half, speed) - position) / speed);
        }
        return double.IsFinite(exit) && exit >= -LengthTolerance ? Math.Max(0, exit) : null;
    }
    private static double[] Add(IReadOnlyList<double> a, IReadOnlyList<double> b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
    private static double[] Subtract(IReadOnlyList<double> a, IReadOnlyList<double> b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    private static double[] Scale(IReadOnlyList<double> a, double scale) => [a[0] * scale, a[1] * scale, a[2] * scale];
    private static double Dot(IReadOnlyList<double> a, IReadOnlyList<double> b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    private static double Norm(IReadOnlyList<double> a) => Math.Sqrt(Dot(a, a));
    private static double[] Cross(IReadOnlyList<double> a, IReadOnlyList<double> b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
}
