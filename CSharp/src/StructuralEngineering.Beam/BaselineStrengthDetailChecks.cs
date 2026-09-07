using System.Text.Json;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reinforcement;

namespace StructuralEngineering.Beam;

internal static class BaselineStrengthDetailChecks
{
    public static void Evaluate(BoundBaselineBeam b, BaselineArrangement a, string profile,
        List<BaselineCheckEvidence> checks, List<ResultEnvelope<JsonElement>> derivations)
    {
        void Add<T>(string rule, CheckScope scope, string id, IReadOnlyList<string> rows, ResultEnvelope<T> result) =>
            checks.Add(new(rule, scope, id, rows, BaselineEvidence.Pack(result)));
        var uls = b.ActionRows.Where(r => r.Role == BaselineSelectionRole.Uls).ToArray();
        var capacityRequest = new FlexuralCapacityRequest(profile, SectionKind.Rectangular, b.WidthMm, b.DepthMm,
            b.ConcreteStrengthNPerMm2, b.SteelYieldStrengthNPerMm2, a.Bars, Face.Bottom);
        var demands = new List<BaselineContinuityDemand>();
        foreach (var row in uls)
        {
            var capacity = capacityRequest with { AxialForceKn = row.PKn };
            var flexure = BeamOperations.CheckFlexure(new(capacity, Math.Max(0, row.M3Knm), Math.Min(0, row.M3Knm)));
            Add("flexure", CheckScope.Station, row.RowId, [row.RowId], flexure);
            var activeFace = row.M3Knm >= 0 ? Face.Bottom : Face.Top;
            var activeBars = a.Bars.Where(bar => bar.Face == activeFace).ToArray();
            var area = activeBars.Sum(bar => Math.PI * bar.DiameterMm * bar.DiameterMm / 4);
            var d = activeFace == Face.Bottom ? a.BottomEffectiveDepthMm : a.TopEffectiveDepthMm;
            Add("shear", CheckScope.Station, row.RowId, [row.RowId], BeamOperations.CheckShear(new(
                [new(profile, ShearAxis.V2, b.WidthMm, d, b.ConcreteStrengthNPerMm2, area, a.Link)],
                [new(row.StationId, ShearAxis.V2, row.V2Kn)])));
            Add("torsion", CheckScope.Station, row.RowId, [row.RowId], BeamOperations.CheckTorsion(new(profile,
                new(row.RowId, row.StationId, ActionBasis.StaticConcurrent, row.V2Kn, row.V3Kn, row.TKnm,
                    row.M2Knm, row.M3Knm, row.SourceIdentity), capacity, a.Link, a.Bars.Select(bar => bar.BarId).ToArray())));
            foreach (var face in new[] { Face.Bottom, Face.Top })
            {
                var required = BaselineFlexure.RequiredSteel(new(profile, b.MemberId, row.RowId, face,
                    b.WidthMm, face == Face.Bottom ? a.BottomEffectiveDepthMm : a.TopEffectiveDepthMm,
                    b.ConcreteStrengthNPerMm2, b.SteelYieldStrengthNPerMm2,
                    face == Face.Bottom ? Math.Max(0, row.M3Knm) : Math.Max(0, -row.M3Knm)));
                derivations.Add(BaselineEvidence.Pack(required));
                if (required.Outputs is { } output)
                    demands.Add(new(row.RowId, row.StationId, row.StationXMm,
                        face == Face.Bottom ? ReinforcementRole.BottomLongitudinal : ReinforcementRole.TopLongitudinal,
                        output.RequiredAreaMm2));
            }
        }
        var cover = b.Context.NominalCoverMm;
        Add("stirrup_anchorage", CheckScope.Member, b.MemberId, [], BaselineStirrupAnchorage.Check(new(profile,
            b.MemberId, a.RevisionId, b.WidthMm, b.DepthMm, cover, a.Link, a.Bars)));
        Add("durability", CheckScope.Member, b.MemberId, [], BaselineEligibility.CheckDurability(new(profile,
            b.MemberId, a.RevisionId, Enum.Parse<ExposureClass>(b.Context.Exposure, true), b.ConcreteStrengthNPerMm2,
            cover, b.WidthMm, b.DepthMm, a.Bars, a.Link)));
        var restraints = b.Context.LateralRestraints!;
        var unrestrained = restraints.RestraintStationsMm.Zip(restraints.RestraintStationsMm.Skip(1), (left, right) => right - left).Max();
        Add("lateral", CheckScope.Member, b.MemberId, [], BaselineEligibility.CheckLateralStability(new(profile,
            b.MemberId, a.RevisionId, b.WidthMm, Math.Max(a.BottomEffectiveDepthMm, a.TopEffectiveDepthMm),
            unrestrained, restraints.EvidenceReference)));
        var linkCentre = cover + a.Link.DiameterMm / 2;
        Add("arrangement", CheckScope.Arrangement, a.RevisionId, [], Detailing.CheckReinforcementArrangement(new(
            profile, b.MemberId, "constant-section", a.RevisionId, b.WidthMm, b.DepthMm, cover,
            b.Context.MaximumAggregateSizeMm, a.Paths,
            [new(a.Link.LinkId, a.Link.DiameterMm, linkCentre, b.WidthMm - linkCentre, linkCentre,
                b.DepthMm - linkCentre, 2 * a.Link.DiameterMm, true)],
            [ReinforcementRole.BottomLongitudinal, ReinforcementRole.TopLongitudinal], 1e-6)));
        var anchorageResults = new List<ResultEnvelope<AnchorageCheckOutput>>();
        foreach (var left in new[] { true, false })
        {
            var end = left ? "left" : "right";
            var face = left ? b.Context.LeftSupportFaceXMm : b.Context.RightSupportFaceXMm;
            var centre = left ? b.Context.LeftSupportCentreXMm : b.Context.RightSupportCentreXMm;
            var endRows = uls.OrderBy(row => Math.Abs(row.StationXMm - centre)).ToArray();
            var nearest = Math.Abs(endRows[0].StationXMm - centre);
            var supportRows = endRows.Where(row => Math.Abs(Math.Abs(row.StationXMm - centre) - nearest) < 1e-6).ToArray();
            var shearN = supportRows.Max(row => Math.Abs(row.V2Kn)) * 1000;
            var simplePaths = new List<AnchoragePath>();
            foreach (var bar in a.Bars)
            {
                var flexural = Flexure.Capacity(capacityRequest with { TensionFace = bar.Face });
                derivations.Add(BaselineEvidence.Pack(flexural));
                simplePaths.Add(new(bar.BarId, end + "-support-face", AnchorageLocation.SimpleSupport,
                    left ? AnchorageDirection.DecreasingX : AnchorageDirection.IncreasingX,
                    b.Context.AnchorageStartXMm, b.Context.AnchorageEndXMm, face, end, face, centre, [], null,
                    new(profile, bar.DiameterMm, .87 * b.SteelYieldStrengthNPerMm2, b.SteelYieldStrengthNPerMm2,
                        b.ConcreteStrengthNPerMm2, BarSurface.Deformed, StressState.Tension),
                    new((flexural.Outputs?.CapacityKnM ?? 0) * 1e6, shearN, supportRows.Select(r => r.RowId).ToArray())));
            }
            var simple = Detailing.CheckAnchorage(new(profile, b.MemberId, a.RevisionId, simplePaths));
            anchorageResults.Add(simple);
            Add("anchorage", CheckScope.BarEnd, end + "-support", supportRows.Select(r => r.RowId).ToArray(), simple);
            // Additional conservative direct-development check at each physical
            // support-face boundary: full Ld must fit in the actual support path.
            var direct = Detailing.CheckAnchorage(new(profile, b.MemberId, a.RevisionId,
                simplePaths.Select(path => path with
                {
                    Location = AnchorageLocation.Discontinuity,
                    SupportId = null,
                    SupportNearFaceXMm = null,
                    SupportCentreXMm = null,
                    SimpleSupportEvidence = null
                }).ToArray()));
            anchorageResults.Add(direct);
            Add("anchorage", CheckScope.BarEnd, end + "-full-development", [], direct);
        }
        var worstAnchorage = anchorageResults.OrderBy(result => BaselineEvidence.Qualified(result))
            .ThenByDescending(result => result.Outputs?.GoverningUtilization ?? double.MaxValue).First();
        var anchorReference = new QualifiedCheckReference(worstAnchorage.OperationSemanticId, worstAnchorage.ResultId,
            worstAnchorage.Execution, worstAnchorage.Applicability, worstAnchorage.Engineering,
            worstAnchorage.Completeness, worstAnchorage.Freshness);
        var stocks = b.Catalogue.StockLengthsMm.Order().Select((length, i) => new AllowedStockLength("stock-" + i, length)).ToArray();
        var selectedStock = stocks.FirstOrDefault(stock => stock.LengthMm >= b.Context.AnchorageEndXMm - b.Context.AnchorageStartXMm) ?? stocks[^1];
        Add("continuity", CheckScope.Member, b.MemberId, uls.Select(row => row.RowId).ToArray(), BaselineContinuity.Check(new(
            profile, b.MemberId, b.PhysicalSpanId, b.EffectiveInputId, a.RevisionId, b.Catalogue.RevisionId,
            b.Context.AnchorageStartXMm, b.Context.AnchorageEndXMm, a.Paths,
            uls.Select(row => new RequiredConcurrentSourceRow(row.RowId, row.StationId, row.StationXMm)).ToArray(),
            [ReinforcementRole.BottomLongitudinal, ReinforcementRole.TopLongitudinal], demands, stocks,
            a.Paths.Select(path => new BarStockPieceAssignment(path.BarId, "piece-" + path.BarId, selectedStock.StockId)).ToArray(), anchorReference)));
        var seeds = a.Paths.Select(path => new BarPathSeed(path.BarId, path.BarMark,
            path.Role == ReinforcementRole.BottomLongitudinal ? BarPathRole.BottomLongitudinal : BarPathRole.TopLongitudinal,
            path.Layer, path.DiameterMm, b.SteelYieldStrengthNPerMm2,
            [new(path.BarId + "-i", new(path.StartStationMm, path.XFromLeftMm, path.YFromTopMm)),
             new(path.BarId + "-j", new(path.EndStationMm, path.XFromLeftMm, path.YFromTopMm))])).ToArray();
        Add("paths", CheckScope.Member, b.MemberId, [], BarPathOperations.Resolve(new(profile, b.EffectiveInputId,
            b.Context.EvidenceRevisionId, b.MemberId, b.PhysicalSpanId, b.Context.EvidenceRevisionId, a.RevisionId,
            new("beam-local", "member_station_x", "section_x_from_left", "section_y_from_top"), b.Context.AnchorageStartXMm,
            b.Context.AnchorageEndXMm, b.WidthMm, b.DepthMm, seeds, b.Catalogue.StockLengthsMm)));
        Add("seismic", CheckScope.Member, b.MemberId, [], Detailing.CheckSeismicDetailing(new(profile, SeismicApplicability.OrdinaryIs456)));
        Add("fire_scope", CheckScope.Member, b.MemberId, [], ResultFactory.NotApplicable<object>(
            BaselineDesignOperations.FireScopeOperation,
            ResultFactory.Effective(("member_id", b.MemberId), ("input_basis_id", b.EffectiveInputId), ("fire_basis", b.Context.FireBasis)),
            new Provenance("project-fire-scope-wp11-v1", "explicit-project-fire-scope-wp11-v1", [b.Context.FireBasis!.DecisionReference]),
            new Diagnostic("FIRE.NOT_REQUIRED_BY_PROJECT", "information", "The accepted project basis specifies no required fire-resistance rating. No fire rating is calculated or certified.", BaselineDesignOperations.FireScopeOperation, "fire_basis")));
    }
}
