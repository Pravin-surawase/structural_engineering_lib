using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Reinforcement;

public static class BarPathOperations
{
    public const string Operation = "structural.reinforcement_paths.resolve/v1";

    private static readonly Provenance Source = new(
        "reinforcement-geometry-wp06-v1",
        "structural-reinforcement-paths-wp06-v1",
        [
            "PF5 AO18 tangent-straight and bend-arc path contract",
            "WP05 anchorage, lap, curtailment, and arrangement consumers"
        ]);

    public static ResultEnvelope<BarPathOutput> Resolve(BarPathRequest request)
    {
        var normalizedPaths = request.Paths
            .Select(item => item with
            {
                AnchorageRequirementIds = item.AnchorageRequirementIds ?? [],
                SpliceIds = item.SpliceIds ?? []
            })
            .ToArray();
        request = request with { Paths = normalizedPaths };
        var inputs = ResultFactory.Effective(("request", request));
        var coordinateSystem = request.CoordinateSystem;

        if (!AllText(
                request.ProfileId,
                request.ProjectBasisId,
                request.CriteriaRevisionId,
                request.MemberId,
                request.PhysicalSpanId,
                request.TopologyRevisionId,
                request.DetailRevisionId,
                coordinateSystem.DatumId) ||
            coordinateSystem.StationAxis != "member_station_x" ||
            coordinateSystem.SectionHorizontalAxis != "section_x_from_left" ||
            coordinateSystem.SectionVerticalAxis != "section_y_from_top" ||
            !new[]
            {
                request.MemberStartXMm,
                request.MemberEndXMm,
                request.SectionWidthMm,
                request.SectionDepthMm,
                request.GeometryToleranceMm
            }.All(double.IsFinite) ||
            request.MemberStartXMm >= request.MemberEndXMm ||
            !Validation.Positive(request.SectionWidthMm) ||
            !Validation.Positive(request.SectionDepthMm) ||
            !Validation.Positive(request.GeometryToleranceMm))
        {
            return Reject(
                inputs,
                "PATH.CONTEXT_INVALID",
                "Path resolution requires complete revisions, canonical local axes, ordered member limits, positive section dimensions, and tolerance.",
                "request",
                "Correct the member coordinate and revision context.");
        }

        if (request.Paths.Count == 0 ||
            request.StockLengthsMm.Count == 0 ||
            request.StockLengthsMm.Any(value => !Validation.Positive(value)) ||
            request.StockLengthsMm.Distinct().Count() != request.StockLengthsMm.Count)
        {
            return Reject(
                inputs,
                "PATH.CATALOGUE_INVALID",
                "At least one path and unique positive available stock lengths are required.",
                "paths,stock_lengths_mm",
                "Supply the selected detail and versioned stock-length catalogue values.");
        }

        var barIds = request.Paths.Select(item => item.BarId).ToArray();
        if (barIds.Distinct(StringComparer.Ordinal).Count() != barIds.Length)
        {
            return Reject(
                inputs,
                "PATH.BAR_ID_DUPLICATE",
                "Every physical bar path requires a unique bar id.",
                "paths",
                "Correct the physical placement identities.");
        }

        var stockLengths = request.StockLengthsMm.Order().ToArray();
        var resolved = new List<ResolvedBarPath>();
        foreach (var seed in request.Paths)
        {
            var nodes = seed.Nodes;
            var nodeIds = nodes.Select(item => item.NodeId).ToArray();
            var references = (seed.AnchorageRequirementIds ?? [])
                .Concat(seed.SpliceIds ?? [])
                .ToArray();
            var minimumNodes = seed.Closed ? 3 : 2;
            if (!Text(seed.BarId) ||
                !Text(seed.BarMark) ||
                !Enum.IsDefined(seed.Role) ||
                seed.Layer < 1 ||
                !Validation.Positive(seed.DiameterMm) ||
                !Validation.Positive(seed.SteelGradeNPerMm2) ||
                seed.BundleSize is < 1 or > 4 ||
                nodes.Count < minimumNodes ||
                nodeIds.Any(value => !Text(value)) ||
                nodeIds.Distinct(StringComparer.Ordinal).Count() != nodeIds.Length ||
                references.Any(value => !Text(value)) ||
                references.Distinct(StringComparer.Ordinal).Count() != references.Length)
            {
                return Reject(
                    inputs,
                    "PATH.SEED_INVALID",
                    "Each bar requires a unique id, mark, role, layer, diameter, grade, nodes, bundle size, and unique detail references.",
                    $"paths[{seed.BarId}]",
                    "Correct the selected physical bar path.");
            }

            if (nodes.Any(node => !InsideContext(node.Point, request)))
            {
                return Reject(
                    inputs,
                    "PATH.NODE_OUTSIDE_CONTEXT",
                    "Every path node must be finite and lie within the supplied member and section coordinate bounds.",
                    $"paths[{seed.BarId}].nodes",
                    "Correct the actual bar centreline coordinates or member context.");
            }

            try
            {
                resolved.Add(ResolveSeed(
                    seed,
                    request.GeometryToleranceMm,
                    stockLengths));
            }
            catch (PathError exception)
            {
                return Reject(
                    inputs,
                    exception.Code,
                    exception.Message,
                    exception.Field,
                    "Resolve complete non-overlapping tangent and bend geometry.");
            }
        }

        var marks = new List<BarMarkSummary>();
        foreach (var group in resolved
            .GroupBy(item => item.BarMark)
            .OrderBy(item => item.Key, StringComparer.Ordinal))
        {
            var exemplar = group.First();
            if (group.Skip(1).Any(item =>
                    !SameShape(exemplar, item, request.GeometryToleranceMm)))
            {
                return Reject(
                    inputs,
                    "MARK.GEOMETRY_CONFLICT",
                    "One bar mark cannot identify different fabrication geometry or material.",
                    $"paths[mark={group.Key}]",
                    "Assign separate marks to paths with different shapes, roles, diameters, grades, or bundles.");
            }

            marks.Add(new BarMarkSummary(
                group.Key,
                exemplar.Role,
                exemplar.DiameterMm,
                exemplar.SteelGradeNPerMm2,
                exemplar.BundleSize,
                exemplar.Closed,
                group.Select(item => item.BarId).ToArray(),
                group.Count(),
                exemplar.DevelopedCentrelineLengthMm,
                exemplar.CompatibleStockLengthMm));
        }

        var diagnostics = resolved
            .Where(item => item.CompatibleStockLengthMm is null)
            .Select(item => Error(
                "PATH.STOCK_LENGTH_EXCEEDED",
                $"Resolved path {item.BarId} exceeds every supplied stock length.",
                $"paths[{item.BarId}]",
                "Split the physical bar with an explicit checked splice or revise the stock catalogue."))
            .ToArray();
        var passed = diagnostics.Length == 0;
        var output = new BarPathOutput(
            request.ProfileId,
            request.ProjectBasisId,
            request.CriteriaRevisionId,
            request.MemberId,
            request.PhysicalSpanId,
            request.TopologyRevisionId,
            request.DetailRevisionId,
            request.CoordinateSystem,
            resolved,
            marks,
            passed);
        return ResultFactory.Completed(
            Operation,
            inputs,
            output,
            Source,
            passed ? EngineeringState.Pass : EngineeringState.Fail,
            diagnostics);
    }

    private static ResolvedBarPath ResolveSeed(
        BarPathSeed seed,
        double tolerance,
        IReadOnlyList<double> stockLengths)
    {
        var nodes = seed.Nodes;
        var bends = new BendGeometry?[nodes.Count];
        if (!seed.Closed &&
            (nodes[0].BendRadiusMm is not null ||
             nodes[0].BendKind is not null ||
             nodes[^1].BendRadiusMm is not null ||
             nodes[^1].BendKind is not null))
        {
            throw new PathError(
                "BEND.ENDPOINT",
                "Open-path endpoints cannot carry bend data; model the hook with an interior tangent vertex and terminal tail.",
                $"paths[{seed.BarId}].nodes");
        }

        var firstBendIndex = seed.Closed ? 0 : 1;
        var lastBendExclusive = seed.Closed ? nodes.Count : nodes.Count - 1;
        for (var index = firstBendIndex; index < lastBendExclusive; index++)
        {
            bends[index] = BendAt(
                nodes[(index - 1 + nodes.Count) % nodes.Count],
                nodes[index],
                nodes[(index + 1) % nodes.Count],
                tolerance);
        }

        var edgeCount = seed.Closed ? nodes.Count : nodes.Count - 1;
        for (var index = 0; index < edgeCount; index++)
        {
            var following = (index + 1) % nodes.Count;
            var available = Distance(nodes[index].Point, nodes[following].Point);
            var used = (bends[index]?.TangentOffsetMm ?? 0) +
                (bends[following]?.TangentOffsetMm ?? 0);
            if (used + tolerance >= available)
            {
                throw new PathError(
                    "BEND.OVERLAP",
                    "Adjacent bend tangencies consume the complete straight between path nodes.",
                    $"paths[{seed.BarId}].nodes[{index}:{following}]");
            }
        }

        var segments = new List<ResolvedPathSegment>();
        var sequence = 1;
        for (var index = 0; index < edgeCount; index++)
        {
            var following = (index + 1) % nodes.Count;
            var start = bends[index]?.TangentOut ?? nodes[index].Point;
            var end = bends[following]?.TangentIn ?? nodes[following].Point;
            segments.Add(new ResolvedPathSegment(
                $"{seed.BarId}:{sequence++:000}",
                PathSegmentKind.TangentStraight,
                start,
                end,
                Distance(start, end)));

            if (bends[following] is not { } bend)
                continue;
            var angleDegrees = bend.AngleRadians * 180 / Math.PI;
            segments.Add(new ResolvedPathSegment(
                $"{seed.BarId}:{sequence++:000}",
                PathSegmentKind.BendArc,
                bend.TangentIn,
                bend.TangentOut,
                bend.RadiusMm * bend.AngleRadians,
                BendCentre: bend.Centre,
                BendRadiusMm: bend.RadiusMm,
                BendAngleDegrees: angleDegrees,
                BendPlaneNormal: bend.PlaneNormal,
                BendSweepDegrees: angleDegrees,
                BendKind: bend.Kind));
        }

        var developedLength = segments.Sum(item => item.CentrelineLengthMm);
        var compatibleStockLength = stockLengths
            .Cast<double?>()
            .FirstOrDefault(value => value + tolerance >= developedLength);
        return new ResolvedBarPath(
            seed.BarId,
            seed.BarMark,
            seed.Role,
            seed.Layer,
            seed.DiameterMm,
            seed.SteelGradeNPerMm2,
            seed.BundleSize,
            seed.Closed,
            nodes.Select(item => item.NodeId).ToArray(),
            segments,
            developedLength,
            compatibleStockLength,
            seed.AnchorageRequirementIds ?? [],
            seed.SpliceIds ?? []);
    }

    private static BendGeometry? BendAt(
        PathNode previous,
        PathNode node,
        PathNode following,
        double tolerance)
    {
        var incoming = Unit(Subtract(node.Point, previous.Point), tolerance);
        var outgoing = Unit(Subtract(following.Point, node.Point), tolerance);
        var angle = Math.Acos(Math.Clamp(Dot(incoming, outgoing), -1, 1));
        var hasBendData = node.BendRadiusMm is not null || node.BendKind is not null;
        if (angle <= 1e-10)
        {
            if (hasBendData)
            {
                throw new PathError(
                    "BEND.UNNEEDED",
                    "A collinear path node cannot carry bend radius or bend kind.",
                    $"nodes[{node.NodeId}]");
            }
            return null;
        }

        if (Math.PI - angle <= 1e-10)
        {
            throw new PathError(
                "BEND.REVERSAL",
                "A reinforcement path cannot reverse direction through a 180-degree vertex.",
                $"nodes[{node.NodeId}]");
        }

        if (node.BendRadiusMm is not { } radius ||
            !Validation.Positive(radius) ||
            node.BendKind is not { } kind ||
            !Enum.IsDefined(kind))
        {
            throw new PathError(
                "BEND.EVIDENCE_REQUIRED",
                "Every direction change requires a positive centreline bend radius and bend kind.",
                $"nodes[{node.NodeId}]");
        }

        var tangentOffset = radius * Math.Tan(angle / 2);
        var tangentIn = AddScaled(node.Point, incoming, -tangentOffset);
        var tangentOut = AddScaled(node.Point, outgoing, tangentOffset);
        var bisector = Unit(
            new Vector(
                -incoming.X + outgoing.X,
                -incoming.Y + outgoing.Y,
                -incoming.Z + outgoing.Z),
            tolerance);
        var centre = AddScaled(node.Point, bisector, radius / Math.Cos(angle / 2));
        var normal = Unit(Cross(incoming, outgoing), tolerance);
        return new BendGeometry(
            tangentIn,
            tangentOut,
            centre,
            radius,
            angle,
            new MemberLocalVector(normal.X, normal.Y, normal.Z),
            kind,
            tangentOffset);
    }

    private static bool SameShape(
        ResolvedBarPath first,
        ResolvedBarPath second,
        double tolerance)
    {
        if (first.Role != second.Role ||
            Math.Abs(first.DiameterMm - second.DiameterMm) > tolerance ||
            Math.Abs(first.SteelGradeNPerMm2 - second.SteelGradeNPerMm2) > tolerance ||
            first.BundleSize != second.BundleSize ||
            first.Closed != second.Closed ||
            first.Segments.Count != second.Segments.Count)
            return false;

        var segmentsMatch = first.Segments.Zip(second.Segments).All(pair =>
            pair.First.Kind == pair.Second.Kind &&
            Math.Abs(pair.First.CentrelineLengthMm -
                pair.Second.CentrelineLengthMm) <= tolerance &&
            pair.First.BendKind == pair.Second.BendKind &&
            NullableNear(pair.First.BendRadiusMm, pair.Second.BendRadiusMm, tolerance) &&
            NullableNear(pair.First.BendAngleDegrees,
                pair.Second.BendAngleDegrees, tolerance) &&
            NullableNear(pair.First.BendSweepDegrees,
                pair.Second.BendSweepDegrees, tolerance));
        if (!segmentsMatch)
            return false;

        var firstNormals = first.Segments
            .Where(item => item.BendPlaneNormal is not null)
            .Select(item => item.BendPlaneNormal!)
            .ToArray();
        var secondNormals = second.Segments
            .Where(item => item.BendPlaneNormal is not null)
            .Select(item => item.BendPlaneNormal!)
            .ToArray();
        if (firstNormals.Length != secondNormals.Length)
            return false;

        for (var left = 0; left < firstNormals.Length; left++)
        {
            for (var right = left + 1; right < firstNormals.Length; right++)
            {
                if (Math.Abs(
                        NormalDot(firstNormals[left], firstNormals[right]) -
                        NormalDot(secondNormals[left], secondNormals[right])) >
                    tolerance)
                    return false;
            }
        }

        for (var firstIndex = 0; firstIndex < firstNormals.Length; firstIndex++)
        {
            for (var secondIndex = firstIndex + 1;
                 secondIndex < firstNormals.Length;
                 secondIndex++)
            {
                for (var thirdIndex = secondIndex + 1;
                     thirdIndex < firstNormals.Length;
                     thirdIndex++)
                {
                    if (Math.Abs(
                            NormalTriple(
                                firstNormals[firstIndex],
                                firstNormals[secondIndex],
                                firstNormals[thirdIndex]) -
                            NormalTriple(
                                secondNormals[firstIndex],
                                secondNormals[secondIndex],
                                secondNormals[thirdIndex])) > tolerance)
                        return false;
                }
            }
        }
        return true;
    }

    private static bool InsideContext(PathPoint point, BarPathRequest request) =>
        new[]
        {
            point.StationXMm,
            point.SectionXFromLeftMm,
            point.SectionYFromTopMm
        }.All(double.IsFinite) &&
        point.StationXMm >= request.MemberStartXMm - request.GeometryToleranceMm &&
        point.StationXMm <= request.MemberEndXMm + request.GeometryToleranceMm &&
        point.SectionXFromLeftMm >= -request.GeometryToleranceMm &&
        point.SectionXFromLeftMm <= request.SectionWidthMm + request.GeometryToleranceMm &&
        point.SectionYFromTopMm >= -request.GeometryToleranceMm &&
        point.SectionYFromTopMm <= request.SectionDepthMm + request.GeometryToleranceMm;

    private static bool NullableNear(double? first, double? second, double tolerance) =>
        first is null
            ? second is null
            : second is not null && Math.Abs(first.Value - second.Value) <= tolerance;

    private static Vector Subtract(PathPoint first, PathPoint second) => new(
        first.StationXMm - second.StationXMm,
        first.SectionXFromLeftMm - second.SectionXFromLeftMm,
        first.SectionYFromTopMm - second.SectionYFromTopMm);

    private static Vector Cross(Vector first, Vector second) => new(
        first.Y * second.Z - first.Z * second.Y,
        first.Z * second.X - first.X * second.Z,
        first.X * second.Y - first.Y * second.X);

    private static double Dot(Vector first, Vector second) =>
        first.X * second.X + first.Y * second.Y + first.Z * second.Z;

    private static double NormalDot(
        MemberLocalVector first,
        MemberLocalVector second) =>
        first.StationComponent * second.StationComponent +
        first.SectionHorizontalComponent * second.SectionHorizontalComponent +
        first.SectionVerticalComponent * second.SectionVerticalComponent;

    private static double NormalTriple(
        MemberLocalVector first,
        MemberLocalVector second,
        MemberLocalVector third)
    {
        var cross = Cross(
            new Vector(
                first.StationComponent,
                first.SectionHorizontalComponent,
                first.SectionVerticalComponent),
            new Vector(
                second.StationComponent,
                second.SectionHorizontalComponent,
                second.SectionVerticalComponent));
        return cross.X * third.StationComponent +
            cross.Y * third.SectionHorizontalComponent +
            cross.Z * third.SectionVerticalComponent;
    }

    private static Vector Unit(Vector vector, double tolerance)
    {
        var length = Math.Sqrt(Dot(vector, vector));
        if (length <= tolerance)
        {
            throw new PathError(
                "PATH.ZERO_LENGTH",
                "Adjacent path nodes must define a nonzero centreline segment.",
                "nodes");
        }
        return new Vector(vector.X / length, vector.Y / length, vector.Z / length);
    }

    private static PathPoint AddScaled(PathPoint point, Vector vector, double scale) =>
        new(
            point.StationXMm + vector.X * scale,
            point.SectionXFromLeftMm + vector.Y * scale,
            point.SectionYFromTopMm + vector.Z * scale);

    private static double Distance(PathPoint first, PathPoint second)
    {
        var vector = Subtract(first, second);
        return Math.Sqrt(Dot(vector, vector));
    }

    private static ResultEnvelope<BarPathOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field,
        string remediation) =>
        ResultFactory.Rejected<BarPathOutput>(
            Operation,
            inputs,
            Source,
            Error(code, message, field, remediation));

    private static Diagnostic Error(
        string code,
        string message,
        string field,
        string remediation) => new(
            code,
            "error",
            message,
            Operation,
            field,
            "reinforcement-paths",
            remediation);

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static bool AllText(params string?[] values) => values.All(Text);

    private readonly record struct Vector(double X, double Y, double Z);

    private sealed record BendGeometry(
        PathPoint TangentIn,
        PathPoint TangentOut,
        PathPoint Centre,
        double RadiusMm,
        double AngleRadians,
        MemberLocalVector PlaneNormal,
        BendKind Kind,
        double TangentOffsetMm);

    private sealed class PathError(
        string code,
        string message,
        string field) : Exception(message)
    {
        public string Code { get; } = code;
        public string Field { get; } = field;
    }
}
