using System.Globalization;
using System.Text.RegularExpressions;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Construction;

public static class BbsOperations
{
    public const string Operation = "structural.bbs.create/v1";

    private static readonly Provenance Source = new(
        "construction-data-wp07-v1",
        "structural-bbs-cutting-wp07-v1",
        [
            "PF5 AO19 resolved-path BBS contract",
            "PF7 AR19 schedule, stock, kerf, offcut, and waste reconciliation"
        ]);

    public static ResultEnvelope<BbsOutput> Create(BbsRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var schedule = request.Schedule;
        var convention = request.ShapeConvention;
        var policy = request.StockPolicy;
        var identities = new[]
        {
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.ScheduleResultId,
            request.ScheduleOutputPayloadId,
            convention.ConventionId,
            convention.RevisionId,
            policy.PolicyId,
            policy.RevisionId
        };
        if (identities.Any(value => !Text(value)))
        {
            return Reject(inputs, "BBS.IDENTITY",
                "Complete schedule and policy identities are required.", "request");
        }

        if (schedule.ProfileId != request.ProfileId ||
            schedule.ProjectBasisId != request.ProjectBasisId ||
            schedule.MemberId != request.MemberId ||
            schedule.DetailRevisionId != request.DetailRevisionId ||
            !schedule.Passed)
        {
            return Reject(inputs, "BBS.SCHEDULE_STALE",
                "The BBS request must bind the current passing resolved schedule.",
                "schedule");
        }

        if (request.ScheduleOutputPayloadId !=
            ResultFactory.SemanticId("output_payload_id", schedule))
        {
            return Reject(inputs, "BBS.SCHEDULE_BINDING",
                "The schedule payload does not match its canonical output identity.",
                "schedule_output_payload_id");
        }

        if (!ScheduleReconciles(request))
        {
            return Reject(inputs, "BBS.SCHEDULE_RECONCILIATION",
                "Resolved paths, mark summaries, counts, materials, and lengths must reconcile.",
                "schedule");
        }

        if (convention.LengthBasis != "resolved_centreline_v1")
        {
            return Reject(inputs, "BBS.CONVENTION",
                "WP07 accepts the resolved-centreline fabrication convention only.",
                "shape_convention.length_basis");
        }

        if (!Validation.Positive(request.SteelDensityKgPerM3) ||
            policy.AllocationMethod != "first_fit_decreasing_v1" ||
            policy.StockLengthsMm.Count == 0 ||
            policy.StockLengthsMm.Distinct().Count() != policy.StockLengthsMm.Count ||
            policy.StockLengthsMm.Any(value => !Validation.Positive(value)) ||
            !Validation.Nonnegative(policy.KerfMm) ||
            !Validation.Nonnegative(policy.ReusableOffcutMinMm) ||
            !Validation.Positive(request.StationToleranceMm))
        {
            return Reject(inputs, "BBS.POLICY",
                "Density, stock lengths, kerf, offcut threshold, tolerance, and allocation method must be valid.",
                "stock_policy");
        }

        var spliceRecords = request.SpliceRecords ?? [];
        var referencedSplices = schedule.Paths
            .SelectMany(path => path.SpliceIds)
            .Distinct(StringComparer.Ordinal)
            .Order(StringComparer.Ordinal)
            .ToArray();
        var spliceIds = spliceRecords.Select(item => item.SpliceId).ToArray();
        if (spliceIds.Distinct(StringComparer.Ordinal).Count() != spliceIds.Length ||
            !spliceIds.Order(StringComparer.Ordinal).SequenceEqual(referencedSplices) ||
            spliceRecords.Any(item =>
                !Text(item.SpliceId) ||
                !Enum.IsDefined(item.Kind) ||
                !double.IsFinite(item.StationXMm) ||
                !Text(item.QualificationReference) ||
                item.Kind == BbsSpliceKind.Lap && item.CouplerCount != 0 ||
                item.Kind == BbsSpliceKind.Coupler && item.CouplerCount <= 0))
        {
            return Reject(inputs, "BBS.SPLICE",
                "Every path splice must have exactly one qualified lap or coupler record.",
                "splice_records");
        }

        var zones = request.LinkZones ?? [];
        var zoneIds = zones.Select(item => item.ZoneId).ToArray();
        if (zoneIds.Distinct(StringComparer.Ordinal).Count() != zoneIds.Length ||
            zones.Any(item =>
                !Text(item.ZoneId) ||
                !Text(item.BarMark) ||
                !double.IsFinite(item.StartStationXMm) ||
                !double.IsFinite(item.EndStationXMm) ||
                !double.IsFinite(item.SpacingMm) ||
                item.StartStationXMm > item.EndStationXMm ||
                item.SpacingMm <= 0 ||
                Math.Abs(
                    (item.EndStationXMm - item.StartStationXMm) / item.SpacingMm -
                    Math.Round((item.EndStationXMm - item.StartStationXMm) /
                        item.SpacingMm, MidpointRounding.ToEven)) > request.StationToleranceMm))
        {
            return Reject(inputs, "BBS.LINK_ZONE",
                "Link zones require unique identities, ordered bounds, and positive spacing.",
                "link_zones");
        }

        var placedZones = new List<PlacedLinkZone>();
        var expectedByMark = new Dictionary<string, List<double>>(StringComparer.Ordinal);
        foreach (var zone in zones
            .OrderBy(item => item.BarMark, StringComparer.Ordinal)
            .ThenBy(item => item.StartStationXMm)
            .ThenBy(item => item.ZoneId, StringComparer.Ordinal))
        {
            var stations = ZoneStations(zone, request.StationToleranceMm);
            if (!expectedByMark.TryGetValue(zone.BarMark, out var expected))
            {
                expected = [];
                expectedByMark.Add(zone.BarMark, expected);
            }
            foreach (var station in stations)
            {
                if (expected.Any(prior => Nearly(station, prior, request.StationToleranceMm)))
                {
                    return Reject(inputs, "BBS.LINK_BOUNDARY_DUPLICATE",
                        "Adjacent link zones assign the same physical station more than once.",
                        $"link_zones[{zone.ZoneId}]");
                }
                expected.Add(station);
            }
            placedZones.Add(new PlacedLinkZone(
                zone.ZoneId, zone.BarMark, stations, stations.Count));
        }

        var transverseMarks = schedule.Paths
            .Where(path => path.Role == BarPathRole.TransverseLink)
            .Select(path => path.BarMark)
            .ToHashSet(StringComparer.Ordinal);
        if (!transverseMarks.SetEquals(expectedByMark.Keys))
        {
            return Reject(inputs, "BBS.LINK_ZONE_REQUIRED",
                "Every transverse-link mark requires explicit placement-zone ownership.",
                "link_zones");
        }

        foreach (var (mark, expected) in expectedByMark)
        {
            var actual = schedule.Paths
                .Where(path => path.BarMark == mark &&
                    path.Role == BarPathRole.TransverseLink)
                .Select(path => path.Segments[0].Start.StationXMm)
                .Order()
                .ToArray();
            var expectedSorted = expected.Order().ToArray();
            if (actual.Length != expectedSorted.Length ||
                actual.Where((value, index) =>
                    !Nearly(value, expectedSorted[index], request.StationToleranceMm)).Any())
            {
                return Reject(inputs, "BBS.LINK_PATH_MISMATCH",
                    "Link-zone stations must match resolved physical link paths exactly.",
                    $"link_zones[mark={mark}]");
            }
        }

        var rows = new List<BbsRow>();
        foreach (var summary in schedule.Marks.OrderBy(
            item => item.BarMark, StringComparer.Ordinal))
        {
            var paths = schedule.Paths
                .Where(path => path.BarMark == summary.BarMark)
                .ToArray();
            var exemplar = paths[0];
            var scheduledCount = summary.Count * summary.BundleSize;
            var totalCutLength = summary.DevelopedCentrelineLengthMm * scheduledCount;
            var mass = Math.PI / 4 * summary.DiameterMm * summary.DiameterMm *
                totalCutLength / 1e9 * request.SteelDensityKgPerM3;
            var dimensions = exemplar.Segments.Select(segment => new ShapeDimension(
                segment.SegmentId.Split(':')[^1],
                SegmentKind(segment.Kind),
                segment.CentrelineLengthMm,
                segment.BendRadiusMm,
                segment.BendAngleDegrees)).ToArray();
            rows.Add(new BbsRow(
                summary.BarMark,
                summary.Role,
                summary.DiameterMm,
                summary.SteelGradeNPerMm2,
                summary.BundleSize,
                summary.Count,
                scheduledCount,
                string.Join('-', exemplar.Segments.Select(segment =>
                    segment.Kind == PathSegmentKind.BendArc ? "B" : "S")),
                dimensions,
                summary.DevelopedCentrelineLengthMm,
                summary.DevelopedCentrelineLengthMm,
                totalCutLength,
                mass,
                paths.Select(path => path.BarId).ToArray(),
                paths.SelectMany(path => path.SpliceIds)
                    .Distinct(StringComparer.Ordinal)
                    .Order(StringComparer.Ordinal)
                    .ToArray()));
        }

        var stockPieces = AllocateStock(request, rows);
        if (stockPieces is null)
        {
            return Reject(inputs, "BBS.STOCK_LENGTH",
                "At least one scheduled cut plus kerf exceeds every stock length.",
                "stock_policy.stock_lengths_mm");
        }

        var scheduledLength = rows.Sum(item => item.ScheduledCutLengthMm);
        var stockLength = stockPieces.Sum(item => item.StockLengthMm);
        var kerfLength = stockPieces.Sum(item => item.KerfLengthMm);
        var reusableLength = stockPieces.Sum(item => item.ReusableOffcutLengthMm);
        var wasteLength = stockPieces.Sum(item => item.WasteLengthMm);
        if (!Nearly(stockLength,
            scheduledLength + kerfLength + reusableLength + wasteLength, 1e-6))
        {
            return Reject(inputs, "BBS.RECONCILIATION",
                "Stock length does not reconcile to cuts, kerf, reusable offcuts, and waste.",
                "stock_pieces");
        }

        var purchasedMass = stockPieces.Sum(item =>
            Math.PI / 4 * item.DiameterMm * item.DiameterMm * item.StockLengthMm /
            1e9 * request.SteelDensityKgPerM3);
        var couplers = spliceRecords
            .Where(item => item.Kind == BbsSpliceKind.Coupler)
            .OrderBy(item => item.SpliceId, StringComparer.Ordinal)
            .Select(item => new CouplerItem(item.SpliceId, item.StationXMm,
                item.CouplerCount, item.QualificationReference))
            .ToArray();
        var output = new BbsOutput(
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.ScheduleResultId,
            convention.RevisionId,
            policy.RevisionId,
            rows,
            placedZones,
            stockPieces,
            couplers,
            scheduledLength,
            stockLength,
            kerfLength,
            reusableLength,
            wasteLength,
            rows.Sum(item => item.TheoreticalMassKg),
            purchasedMass,
            "heuristic_first_fit_decreasing",
            true);
        return ResultFactory.Completed(Operation, inputs, output, Source);
    }

    private static bool ScheduleReconciles(BbsRequest request)
    {
        var schedule = request.Schedule;
        var pathIds = schedule.Paths.Select(item => item.BarId).ToArray();
        var markNames = schedule.Marks.Select(item => item.BarMark).ToArray();
        if (schedule.Paths.Count == 0 || schedule.Marks.Count == 0 ||
            pathIds.Distinct(StringComparer.Ordinal).Count() != pathIds.Length ||
            markNames.Distinct(StringComparer.Ordinal).Count() != markNames.Length)
        {
            return false;
        }

        var tolerance = request.StationToleranceMm;
        foreach (var summary in schedule.Marks)
        {
            var paths = schedule.Paths
                .Where(item => item.BarMark == summary.BarMark)
                .ToArray();
            if (paths.Length == 0 ||
                summary.Count != paths.Length ||
                summary.BarIds.Distinct(StringComparer.Ordinal).Count() !=
                    summary.BarIds.Count ||
                !summary.BarIds.ToHashSet(StringComparer.Ordinal)
                    .SetEquals(paths.Select(item => item.BarId)))
            {
                return false;
            }

            var first = paths[0];
            if (!Enum.IsDefined(summary.Role) ||
                summary.Role != first.Role ||
                !Nearly(summary.DiameterMm, first.DiameterMm, tolerance) ||
                !Nearly(summary.SteelGradeNPerMm2, first.SteelGradeNPerMm2, tolerance) ||
                summary.BundleSize != first.BundleSize ||
                summary.Closed != first.Closed ||
                !Nearly(summary.DevelopedCentrelineLengthMm,
                    first.DevelopedCentrelineLengthMm, tolerance))
            {
                return false;
            }

            foreach (var path in paths)
            {
                if (!Enum.IsDefined(path.Role) ||
                    path.Role != summary.Role ||
                    !Nearly(path.DiameterMm, summary.DiameterMm, tolerance) ||
                    !Nearly(path.SteelGradeNPerMm2,
                        summary.SteelGradeNPerMm2, tolerance) ||
                    path.BundleSize != summary.BundleSize ||
                    path.Closed != summary.Closed ||
                    path.Segments.Count == 0 ||
                    !Nearly(path.Segments.Sum(item => item.CentrelineLengthMm),
                        path.DevelopedCentrelineLengthMm, tolerance) ||
                    path.Segments.Count != first.Segments.Count)
                {
                    return false;
                }

                for (var index = 0; index < path.Segments.Count; index++)
                {
                    var left = path.Segments[index];
                    var right = first.Segments[index];
                    if (!Enum.IsDefined(left.Kind) ||
                        left.Kind != right.Kind ||
                        !Nearly(left.CentrelineLengthMm,
                            right.CentrelineLengthMm, tolerance) ||
                        left.BendKind != right.BendKind ||
                        !NearlyNullable(left.BendRadiusMm, right.BendRadiusMm, tolerance) ||
                        !NearlyNullable(left.BendAngleDegrees,
                            right.BendAngleDegrees, tolerance))
                    {
                        return false;
                    }
                }
            }
        }

        return schedule.Paths.Select(item => item.BarMark)
            .ToHashSet(StringComparer.Ordinal)
            .SetEquals(markNames);
    }

    private static IReadOnlyList<double> ZoneStations(
        LinkPlacementZone zone, double tolerance)
    {
        var stations = new List<double>();
        for (var index = 0;
            zone.StartStationXMm + index * zone.SpacingMm <=
                zone.EndStationXMm + tolerance;
            index++)
        {
            var station = zone.StartStationXMm + index * zone.SpacingMm;
            stations.Add(Math.Min(station, zone.EndStationXMm));
        }
        if (stations.Count > 0 && !zone.IncludeStart &&
            Nearly(stations[0], zone.StartStationXMm, tolerance))
        {
            stations.RemoveAt(0);
        }
        if (stations.Count > 0 && !zone.IncludeEnd &&
            Nearly(stations[^1], zone.EndStationXMm, tolerance))
        {
            stations.RemoveAt(stations.Count - 1);
        }
        return stations;
    }

    private static IReadOnlyList<StockPiece>? AllocateStock(
        BbsRequest request, IReadOnlyList<BbsRow> rows)
    {
        var policy = request.StockPolicy;
        var stockLengths = policy.StockLengthsMm.Order().ToArray();
        var cuts = rows.SelectMany(row => Enumerable.Range(1, row.ScheduledBarCount)
            .Select(index => new PendingCut(
                row.FabricationCutLengthEachMm,
                row.BarMark,
                row.DiameterMm,
                row.SteelGradeNPerMm2,
                $"{row.BarMark}:{index:0000}")))
            .OrderByDescending(item => item.LengthMm)
            .ThenBy(item => item.BarMark, StringComparer.Ordinal)
            .ThenBy(item => item.CutId, StringComparer.Ordinal)
            .ToArray();
        var opened = new List<OpenStock>();
        foreach (var cut in cuts)
        {
            var piece = opened.FirstOrDefault(candidate =>
                candidate.DiameterMm == cut.DiameterMm &&
                candidate.SteelGradeNPerMm2 == cut.SteelGradeNPerMm2 &&
                candidate.UsedLengthMm + candidate.Cuts.Count * policy.KerfMm +
                    cut.LengthMm + policy.KerfMm <= candidate.StockLengthMm + 1e-9);
            if (piece is null)
            {
                var stockLength = stockLengths.Cast<double?>().FirstOrDefault(value =>
                    cut.LengthMm + policy.KerfMm <= value + 1e-9);
                if (stockLength is null)
                {
                    return null;
                }
                piece = new OpenStock(
                    cut.DiameterMm, cut.SteelGradeNPerMm2, stockLength.Value);
                opened.Add(piece);
            }
            piece.Cuts.Add(new StockCut(cut.CutId, cut.BarMark, cut.LengthMm));
        }

        return opened.Select((piece, index) =>
        {
            var kerf = piece.Cuts.Count * policy.KerfMm;
            var remainder = piece.StockLengthMm - piece.UsedLengthMm - kerf;
            var reusable = remainder + 1e-9 >= policy.ReusableOffcutMinMm
                ? remainder
                : 0;
            var waste = reusable == 0 ? remainder : 0;
            return new StockPiece(
                $"STOCK-{index + 1:0000}",
                piece.DiameterMm,
                piece.SteelGradeNPerMm2,
                piece.StockLengthMm,
                piece.Cuts,
                kerf,
                reusable,
                waste);
        }).ToArray();
    }

    private static string SegmentKind(PathSegmentKind kind) => kind switch
    {
        PathSegmentKind.TangentStraight => "tangent_straight",
        PathSegmentKind.BendArc => "bend_arc",
        _ => throw new ArgumentOutOfRangeException(nameof(kind))
    };

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);
    private static bool Nearly(double left, double right, double tolerance) =>
        Math.Abs(left - right) <= tolerance;
    private static bool NearlyNullable(double? left, double? right, double tolerance) =>
        left is null && right is null ||
        left is not null && right is not null && Nearly(left.Value, right.Value, tolerance);

    private static ResultEnvelope<BbsOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field) => ResultFactory.Rejected<BbsOutput>(
            Operation, inputs, Source,
            new Diagnostic(code, "error", message, Operation, field,
                "construction-bbs"));

    private sealed record PendingCut(
        double LengthMm,
        string BarMark,
        double DiameterMm,
        double SteelGradeNPerMm2,
        string CutId);

    private sealed class OpenStock(
        double diameterMm,
        double steelGradeNPerMm2,
        double stockLengthMm)
    {
        public double DiameterMm { get; } = diameterMm;
        public double SteelGradeNPerMm2 { get; } = steelGradeNPerMm2;
        public double StockLengthMm { get; } = stockLengthMm;
        public List<StockCut> Cuts { get; } = [];
        public double UsedLengthMm => Cuts.Sum(item => item.LengthMm);
    }
}

public static class QuantityOperations
{
    public const string Operation =
        "structural.construction_quantities.calculate/v1";

    private static readonly Provenance Source = new(
        "construction-data-wp07-v1",
        "structural-construction-quantities-wp07-v1",
        [
            "PF7 AR04 independent mass, volume, and contact-area arithmetic",
            "PF7 AR20 explicit net segments and formwork contact faces"
        ]);

    public static ResultEnvelope<ConstructionQuantityOutput> Calculate(
        ConstructionQuantityRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var bbs = request.Bbs;
        var identities = new[]
        {
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.BbsResultId,
            request.BbsOutputPayloadId,
            request.ConcreteOverlapPolicyId,
            request.FormworkMeasurementPolicyId
        };
        if (identities.Any(value => !Text(value)))
        {
            return Reject(inputs, "QUANTITY.IDENTITY",
                "Complete quantity, detail, and measurement policy identities are required.",
                "request");
        }

        if (bbs.ProfileId != request.ProfileId ||
            bbs.ProjectBasisId != request.ProjectBasisId ||
            bbs.MemberId != request.MemberId ||
            bbs.DetailRevisionId != request.DetailRevisionId ||
            !bbs.Passed)
        {
            return Reject(inputs, "QUANTITY.BBS_STALE",
                "Quantities must bind the current passing BBS for the same detail.",
                "bbs");
        }

        if (request.BbsOutputPayloadId !=
            ResultFactory.SemanticId("output_payload_id", bbs))
        {
            return Reject(inputs, "QUANTITY.BBS_BINDING",
                "The BBS payload does not match its canonical output identity.",
                "bbs_output_payload_id");
        }

        var segmentIds = request.ConcreteSegments.Select(item => item.SegmentId).ToArray();
        var segmentOwners = request.ConcreteSegments.Select(item => item.OwnershipId).ToArray();
        var volumeDeductions = request.ConcreteSegments
            .SelectMany(item => item.Deductions ?? [])
            .ToArray();
        var deductionIds = volumeDeductions.Select(item => item.DeductionId).ToArray();
        var deductionOwners = volumeDeductions.Select(item => item.OwnershipId).ToArray();
        if (request.ConcreteSegments.Count == 0 ||
            HasDuplicates(segmentIds) ||
            HasDuplicates(segmentOwners) ||
            HasDuplicates(deductionIds) ||
            HasDuplicates(deductionOwners) ||
            segmentOwners.Intersect(deductionOwners, StringComparer.Ordinal).Any() ||
            request.ConcreteSegments.Any(item =>
                !Text(item.SegmentId) || !Text(item.MemberId) ||
                !Text(item.MaterialId) || !Text(item.OwnershipId) ||
                item.MemberId != request.MemberId ||
                !Validation.Positive(item.CrossSectionAreaMm2) ||
                !Validation.Positive(item.PhysicalLengthMm) ||
                (item.Deductions ?? []).Any(deduction =>
                    !Text(deduction.DeductionId) || !Text(deduction.OwnershipId) ||
                    !Text(deduction.Reason) ||
                    !Validation.Nonnegative(deduction.VolumeM3))))
        {
            return Reject(inputs, "QUANTITY.CONCRETE_OWNERSHIP",
                "Concrete segments and deductions require unique, explicit physical ownership.",
                "concrete_segments");
        }

        var concreteItems = new List<ConcreteQuantity>();
        foreach (var segment in request.ConcreteSegments)
        {
            var gross = segment.CrossSectionAreaMm2 * segment.PhysicalLengthMm / 1e9;
            var deduction = (segment.Deductions ?? []).Sum(item => item.VolumeM3);
            if (deduction > gross + 1e-12)
            {
                return Reject(inputs, "QUANTITY.CONCRETE_DEDUCTION",
                    "Concrete deductions cannot exceed gross segment volume.",
                    $"concrete_segments[{segment.SegmentId}]");
            }
            concreteItems.Add(new ConcreteQuantity(
                segment.SegmentId,
                segment.MaterialId,
                segment.OwnershipId,
                gross,
                deduction,
                gross - deduction,
                segment.OwnsMonolithicInterface));
        }

        var faceIds = request.FormworkFaces.Select(item => item.FaceId).ToArray();
        var faceOwners = request.FormworkFaces.Select(item => item.OwnershipId).ToArray();
        var areaDeductions = request.FormworkFaces
            .SelectMany(item => item.Deductions ?? [])
            .ToArray();
        var areaDeductionIds = areaDeductions.Select(item => item.DeductionId).ToArray();
        var areaDeductionOwners = areaDeductions.Select(item => item.OwnershipId).ToArray();
        if (request.FormworkFaces.Count == 0 ||
            HasDuplicates(faceIds) ||
            HasDuplicates(faceOwners) ||
            HasDuplicates(areaDeductionIds) ||
            HasDuplicates(areaDeductionOwners) ||
            faceOwners.Intersect(areaDeductionOwners, StringComparer.Ordinal).Any() ||
            request.FormworkFaces.Any(item =>
                !Text(item.FaceId) || !Text(item.MemberId) || !Text(item.OwnershipId) ||
                item.MemberId != request.MemberId ||
                !Enum.IsDefined(item.Category) ||
                !Enum.IsDefined(item.MeasurementState) ||
                !Validation.Nonnegative(item.GrossAreaMm2) ||
                item.MeasurementState == FormworkMeasurementState.Excluded &&
                    !Text(item.ExclusionReason) ||
                item.MeasurementState == FormworkMeasurementState.Included &&
                    item.ExclusionReason is not null ||
                (item.Deductions ?? []).Any(deduction =>
                    !Text(deduction.DeductionId) || !Text(deduction.OwnershipId) ||
                    !Text(deduction.Reason) ||
                    !Validation.Nonnegative(deduction.AreaMm2))))
        {
            return Reject(inputs, "QUANTITY.FORMWORK_OWNERSHIP",
                "Formwork faces and deductions require unique ownership and inclusion state.",
                "formwork_faces");
        }

        var formworkItems = new List<FormworkQuantity>();
        foreach (var face in request.FormworkFaces)
        {
            var gross = face.GrossAreaMm2 / 1e6;
            var deduction = (face.Deductions ?? []).Sum(item => item.AreaMm2) / 1e6;
            if (deduction > gross + 1e-12)
            {
                return Reject(inputs, "QUANTITY.FORMWORK_DEDUCTION",
                    "Formwork deductions cannot exceed the gross contact face.",
                    $"formwork_faces[{face.FaceId}]");
            }
            formworkItems.Add(new FormworkQuantity(
                face.FaceId,
                face.Category,
                face.OwnershipId,
                face.MeasurementState,
                gross,
                deduction,
                face.MeasurementState == FormworkMeasurementState.Included
                    ? gross - deduction
                    : 0,
                face.ExclusionReason));
        }

        var steelItems = bbs.Rows.Select(row => new QuantitySteelItem(
            row.BarMark,
            row.DiameterMm,
            row.SteelGradeNPerMm2,
            row.ScheduledBarCount,
            row.ScheduledCutLengthMm,
            row.TheoreticalMassKg)).ToArray();
        var output = new ConstructionQuantityOutput(
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.BbsResultId,
            request.ConcreteOverlapPolicyId,
            request.FormworkMeasurementPolicyId,
            steelItems,
            concreteItems,
            formworkItems,
            new WasteLedger(
                bbs.KerfLengthMm,
                bbs.ReusableOffcutLengthMm,
                bbs.WasteLengthMm),
            bbs.ScheduledSteelMassKg,
            bbs.PurchasedStockMassKg,
            concreteItems.Sum(item => item.NetVolumeM3),
            formworkItems.Sum(item => item.NetAreaM2),
            bbs.Couplers.Sum(item => item.Count));
        return ResultFactory.Completed(Operation, inputs, output, Source);
    }

    private static bool HasDuplicates(IEnumerable<string> values)
    {
        var items = values.ToArray();
        return items.Distinct(StringComparer.Ordinal).Count() != items.Length;
    }

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static ResultEnvelope<ConstructionQuantityOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field) => ResultFactory.Rejected<ConstructionQuantityOutput>(
            Operation, inputs, Source,
            new Diagnostic(code, "error", message, Operation, field,
                "construction-quantities"));
}

public static class CostOperations
{
    public const string Operation = "structural.construction_cost.estimate/v1";

    private static readonly Provenance Source = new(
        "construction-cost-wp07-v1",
        "structural-construction-cost-wp07-v1",
        [
            "PF5 AO20 dated explicit rate profile",
            "PF7 AR20 direct cost, overhead, tax, and waste scope"
        ]);

    private static readonly Regex DecimalPattern = new(
        "^(?:0|[0-9]+)(?:\\.[0-9]+)?$",
        RegexOptions.CultureInvariant | RegexOptions.NonBacktracking);

    public static ResultEnvelope<ConstructionCostOutput> Estimate(
        ConstructionCostRequest request)
    {
        var inputs = ResultFactory.Effective(("request", request));
        var quantities = request.Quantities;
        var profile = request.RateProfile;
        var identities = new[]
        {
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.QuantityResultId,
            request.QuantityOutputPayloadId,
            profile.ProfileId,
            profile.RevisionId,
            profile.Currency,
            profile.ValuationDate,
            profile.TimeZone,
            profile.Geography,
            profile.Source
        };
        if (identities.Any(value => !Text(value)) || profile.Currency.Length != 3)
        {
            return Reject(inputs, "COST.IDENTITY",
                "Costing requires complete currency, date, geography, source, profile, and result identities.",
                "request");
        }

        if (!DateOnly.TryParseExact(profile.ValuationDate, "yyyy-MM-dd",
            CultureInfo.InvariantCulture, DateTimeStyles.None, out _))
        {
            return Reject(inputs, "COST.DATE",
                "Valuation date must be an ISO calendar date.",
                "rate_profile.valuation_date");
        }

        if (quantities.ProfileId != request.ProfileId ||
            quantities.ProjectBasisId != request.ProjectBasisId ||
            quantities.MemberId != request.MemberId ||
            quantities.DetailRevisionId != request.DetailRevisionId)
        {
            return Reject(inputs, "COST.QUANTITY_STALE",
                "Cost must bind current quantities for the same project, member, and detail.",
                "quantities");
        }

        if (request.QuantityOutputPayloadId !=
            ResultFactory.SemanticId("output_payload_id", quantities))
        {
            return Reject(inputs, "COST.QUANTITY_BINDING",
                "The quantity payload does not match its canonical output identity.",
                "quantity_output_payload_id");
        }

        var included = profile.Scope.IncludedCategories;
        var excluded = profile.Scope.ExcludedCategories;
        var allCategories = Enum.GetValues<CostCategory>().ToHashSet();
        if (included.Any(item => !Enum.IsDefined(item)) ||
            excluded.Any(item => !Enum.IsDefined(item)) ||
            included.Distinct().Count() != included.Count ||
            excluded.Distinct().Count() != excluded.Count ||
            included.Intersect(excluded).Any() ||
            !included.Concat(excluded).ToHashSet().SetEquals(allCategories))
        {
            return Reject(inputs, "COST.SCOPE",
                "Every direct-cost category must be included or excluded exactly once.",
                "rate_profile.scope");
        }

        if (profile.Rates.Count == 0 || included.Any(category =>
            profile.Rates.All(rate => rate.Category != category)))
        {
            return Reject(inputs, "COST.RATE_MISSING",
                "Every included cost category requires at least one explicit rate.",
                "rate_profile.rates");
        }

        if (profile.Rates.Select(item => item.RateId)
                .Distinct(StringComparer.Ordinal).Count() != profile.Rates.Count ||
            profile.Rates.Select(item => (item.Category, item.Basis))
                .Distinct().Count() != profile.Rates.Count)
        {
            return Reject(inputs, "COST.RATE_DUPLICATE",
                "Rate identities and category/basis pairs must be unique.",
                "rate_profile.rates");
        }

        var parsedRates = new Dictionary<string, decimal>(StringComparer.Ordinal);
        foreach (var rate in profile.Rates)
        {
            if (!Text(rate.RateId) || !Text(rate.Description) ||
                !Text(rate.SourceReference) || !Enum.IsDefined(rate.Category) ||
                !Enum.IsDefined(rate.Basis) || !included.Contains(rate.Category) ||
                !TryDecimal(rate.UnitRateDecimal, out var value))
            {
                return Reject(inputs, "COST.RATE_INVALID",
                    "Rates require an included category, supported basis, nonnegative decimal rate, description, and source.",
                    "rate_profile.rates");
            }
            parsedRates.Add(rate.RateId, value);
        }

        if (profile.Rates.Any(rate => !Permitted(rate.Category, rate.Basis)))
        {
            return Reject(inputs, "COST.RATE_SCOPE",
                "A cost category may price only its declared physical quantity basis.",
                "rate_profile.rates");
        }

        if (!Enum.IsDefined(profile.WastePricingBasis))
        {
            return Reject(inputs, "COST.WASTE_POLICY",
                "A supported steel waste pricing basis is required.",
                "rate_profile.waste_pricing_basis");
        }
        var forbidden = profile.WastePricingBasis == WastePricingBasis.ScheduledSteel
            ? CostBasis.SteelStockMassKg
            : CostBasis.SteelScheduledMassKg;
        if (profile.Rates.Any(item => item.Basis == forbidden))
        {
            return Reject(inputs, "COST.WASTE_DOUBLE_COUNT",
                "The selected steel waste basis conflicts with a supplied steel rate basis.",
                "rate_profile.rates");
        }

        var steelBasis = profile.WastePricingBasis == WastePricingBasis.ScheduledSteel
            ? CostBasis.SteelScheduledMassKg
            : CostBasis.SteelStockMassKg;
        var suppliedPairs = profile.Rates.Select(item => (item.Category, item.Basis))
            .ToHashSet();
        var requiredPairs = new[]
        {
            (CostCategory.Material, steelBasis),
            (CostCategory.Material, CostBasis.ConcreteVolumeM3),
            (CostCategory.Formwork, CostBasis.FormworkAreaM2),
            (CostCategory.Coupler, CostBasis.CouplerCount)
        };
        if (requiredPairs.Any(pair => included.Contains(pair.Item1) &&
            !suppliedPairs.Contains(pair)))
        {
            return Reject(inputs, "COST.RATE_COVERAGE",
                "The included material, formwork, or coupler scope is missing a required physical quantity rate.",
                "rate_profile.rates");
        }

        if (!TryDecimal(profile.OverheadPercentDecimal, out var overheadPercent) ||
            !TryDecimal(profile.TaxPercentDecimal, out var taxPercent))
        {
            return Reject(inputs, "COST.PERCENT",
                "Overhead and tax require explicit nonnegative decimal percentages.",
                "rate_profile");
        }

        var lines = new List<CostLine>();
        foreach (var rate in profile.Rates.OrderBy(
            item => item.RateId, StringComparer.Ordinal))
        {
            var quantity = Quantity(rate.Basis, quantities);
            var unitRate = parsedRates[rate.RateId];
            var amount = Money(quantity * unitRate);
            lines.Add(new CostLine(
                rate.RateId,
                rate.Category,
                rate.Basis,
                rate.Description,
                request.QuantityResultId,
                quantity.ToString("0.############################", CultureInfo.InvariantCulture),
                Unit(rate.Basis),
                unitRate.ToString("0.############################", CultureInfo.InvariantCulture),
                MoneyText(amount)));
        }

        var subtotal = lines.Sum(item =>
            decimal.Parse(item.AmountDecimal, CultureInfo.InvariantCulture));
        var overhead = Money(subtotal * overheadPercent / 100m);
        var preTax = subtotal + overhead;
        var tax = Money(preTax * taxPercent / 100m);
        var total = preTax + tax;
        var output = new ConstructionCostOutput(
            request.ProfileId,
            request.ProjectBasisId,
            request.MemberId,
            request.DetailRevisionId,
            request.QuantityResultId,
            profile.ProfileId,
            profile.RevisionId,
            profile.Currency.ToUpperInvariant(),
            profile.ValuationDate,
            profile.Geography,
            profile.Source,
            lines,
            included,
            excluded,
            MoneyText(subtotal),
            MoneyText(overhead),
            MoneyText(preTax),
            MoneyText(tax),
            MoneyText(total));
        return ResultFactory.Completed(Operation, inputs, output, Source);
    }

    private static bool Permitted(CostCategory category, CostBasis basis) =>
        category switch
        {
            CostCategory.Material => basis is
                CostBasis.SteelScheduledMassKg or
                CostBasis.SteelStockMassKg or
                CostBasis.ConcreteVolumeM3,
            CostCategory.Formwork => basis == CostBasis.FormworkAreaM2,
            CostCategory.Coupler => basis == CostBasis.CouplerCount,
            CostCategory.Labour or CostCategory.Plant => Enum.IsDefined(basis),
            _ => false
        };

    private static decimal Quantity(
        CostBasis basis, ConstructionQuantityOutput quantities) => basis switch
    {
        CostBasis.SteelScheduledMassKg => (decimal)quantities.SteelScheduledMassKg,
        CostBasis.SteelStockMassKg => (decimal)quantities.SteelStockMassKg,
        CostBasis.ConcreteVolumeM3 => (decimal)quantities.ConcreteVolumeM3,
        CostBasis.FormworkAreaM2 => (decimal)quantities.FormworkAreaM2,
        CostBasis.CouplerCount => quantities.CouplerCount,
        _ => throw new ArgumentOutOfRangeException(nameof(basis))
    };

    private static string Unit(CostBasis basis) => basis switch
    {
        CostBasis.SteelScheduledMassKg or CostBasis.SteelStockMassKg => "kg",
        CostBasis.ConcreteVolumeM3 => "m3",
        CostBasis.FormworkAreaM2 => "m2",
        CostBasis.CouplerCount => "count",
        _ => throw new ArgumentOutOfRangeException(nameof(basis))
    };

    private static decimal Money(decimal value) =>
        decimal.Round(value, 2, MidpointRounding.ToEven);

    private static string MoneyText(decimal value) =>
        Money(value).ToString("0.00", CultureInfo.InvariantCulture);

    private static bool TryDecimal(string value, out decimal result)
    {
        result = 0;
        return value is not null && DecimalPattern.IsMatch(value) &&
            decimal.TryParse(value, NumberStyles.AllowDecimalPoint,
                CultureInfo.InvariantCulture, out result) && result >= 0;
    }

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);

    private static ResultEnvelope<ConstructionCostOutput> Reject(
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        string code,
        string message,
        string field) => ResultFactory.Rejected<ConstructionCostOutput>(
            Operation, inputs, Source,
            new Diagnostic(code, "error", message, Operation, field,
                "construction-cost"));
}
