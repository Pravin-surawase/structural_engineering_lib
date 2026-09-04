using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp05Tests
{
    private static DevelopmentLengthRequest Development(BarSurface surface = BarSurface.Deformed) =>
        new("IS456-WP05", 20, .87 * 415, 415, 20, surface, StressState.Tension);

    private static QualifiedCheckReference Qualified(string operation) =>
        new(operation, "result:" + operation, ExecutionState.Completed,
            ApplicabilityState.Applicable, EngineeringState.Pass,
            CompletenessState.CompleteForScope, FreshnessState.Current);

    private static LongitudinalBarPath Bar(string id, ReinforcementRole role, double x, double y,
        double diameter = 20, int layer = 1, double start = 0, double end = 6000) =>
        new(id, "MARK-" + id, role, diameter, layer, x, y, start, end, .87 * 415);

    [Fact]
    public void DevelopmentLengthPreservesAmendmentSixEpoxyFactorAndRejectsOverstress()
    {
        var deformed = Detailing.DevelopmentLength(Development());
        var epoxy = Detailing.DevelopmentLength(Development(BarSurface.FusionBondedEpoxyDeformed));
        var overstress = Detailing.DevelopmentLength(Development() with { BarStressNPerMm2 = .9 * 415 });

        Assert.Equal(1.92, deformed.Outputs!.DesignBondStressNPerMm2, 12);
        Assert.Equal(940.234375, deformed.Outputs.RequiredDevelopmentLengthMm, 12);
        Assert.Equal(1.28, epoxy.Outputs!.SurfaceFactor, 12);
        Assert.Equal(1175.29296875, epoxy.Outputs.RequiredDevelopmentLengthMm, 12);
        Assert.Equal(ExecutionState.RejectedInput, overstress.Execution);
        Assert.Equal("STRESS.OUTSIDE_PROFILE", overstress.Diagnostics[0].Code);
    }

    [Fact]
    public void AnchorageUsesPhysicalFaceAndMomentOverShearPlusLo()
    {
        var valid = Detailing.CheckAnchorage(new(
            "IS456-WP05", "B1", "reinforcement:R1",
            [new("B1", "right-face", AnchorageLocation.SimpleSupport,
                AnchorageDirection.IncreasingX, 0, 6000, 5800, "SUP-R", 5800, 5900,
                [], null, Development(), new(85_000_000, 100_000, ["action:ULS-right"]))]));
        var invalid = Detailing.CheckAnchorage(new(
            "IS456-WP05", "B1", "reinforcement:R1",
            [new("B1", "centreline", AnchorageLocation.ContinuousSupport,
                AnchorageDirection.IncreasingX, 0, 6000, 5900, "SUP-R", 5800, 5900,
                [], null, Development())]));

        var check = Assert.Single(valid.Outputs!.Checks);
        Assert.Equal(EngineeringState.Pass, valid.Engineering);
        Assert.Equal(850, check.MomentShearContributionMm, 12);
        Assert.Equal(100, check.AnchorageBeyondSupportCentreMm, 12);
        Assert.Equal("SUPPORT.FACE_REQUIRED", invalid.Diagnostics[0].Code);
    }

    [Fact]
    public void LapCurtailmentRequiresQualifiedOperationSpecificEvidence()
    {
        var bars = new[]
        {
            Bar("B1", ReinforcementRole.BottomLongitudinal, 60, 440),
            Bar("B2", ReinforcementRole.BottomLongitudinal, 150, 440),
            Bar("B3", ReinforcementRole.BottomLongitudinal, 240, 440, end: 5000)
        };
        LapCurtailmentCheckRequest Request(QualifiedCheckReference anchorage) => new(
            "IS456-WP05", "B1", "SPAN-1", "demand:R1", "reinforcement:R1", 0, 6000,
            450, 20, 415, BarSurface.Deformed, bars,
            [new("D-4000", 4000, ReinforcementRole.BottomLongitudinal, 600, 80_000, 120_000, "action:ULS-4000")],
            [new("SP-1", SpliceKind.Lap, ["B1", "B2"], 2500, 3500, StressState.Tension, false, 50, "STAGGER-A")],
            [new("CUT-1", "B3", 4000, 5000, AnchorageDirection.IncreasingX, "D-4000", 600,
                ["B1", "B2"], anchorage, Qualified("is456.beam.shear.check/v1"),
                ExtraLinksRequired: true, ExtraLinksCheck: Qualified("is456.beam.shear.check/v1"))]);

        var valid = Detailing.CheckLapsAndCurtailment(Request(Qualified("is456.beam.anchorage.check/v1")));
        var wrongReference = Detailing.CheckLapsAndCurtailment(Request(Qualified("another.operation/v1")));

        Assert.Equal(EngineeringState.Pass, valid.Engineering);
        Assert.Equal(940.234375, valid.Outputs!.SpliceChecks[0].RequiredLengthMm!.Value, 12);
        Assert.Equal(628.3185307179587, valid.Outputs.CurtailmentChecks[0].ContinuingAreaMm2, 12);
        Assert.Equal(EngineeringState.Fail, wrongReference.Engineering);
        Assert.False(wrongReference.Outputs!.CurtailmentChecks[0].AnchorageOk);
    }

    [Fact]
    public void SeismicDetailingUsesCapacityShearAndCompleteEvidence()
    {
        var bars = new[]
        {
            Bar("T1", ReinforcementRole.TopLongitudinal, 60, 60), Bar("T2", ReinforcementRole.TopLongitudinal, 240, 60),
            Bar("B1", ReinforcementRole.BottomLongitudinal, 60, 440), Bar("B2", ReinforcementRole.BottomLongitudinal, 240, 440)
        };
        var context = new SeismicBeamContext("SMRF-1", "seismic:R1", "B1", "SPAN-1", "J-L", "J-R",
            200, 5800, 300, 500, 450, 30, 415, bars,
            [new("L-END", 200, 1100, 100, 10, true, 135, 50), new("R-END", 4900, 5800, 100, 10, true, 135, 50)],
            [], 60_000, 20_000, 100_000_000, 100_000_000, 100_000_000, 100_000_000, 100_000,
            Qualified("is456.beam.shear.check/v1"),
            [
                new(BeamEnd.Left, ReinforcementRole.TopLongitudinal,
                    Qualified("is456.beam.anchorage.check/v1")),
                new(BeamEnd.Left, ReinforcementRole.BottomLongitudinal,
                    Qualified("is456.beam.anchorage.check/v1")),
                new(BeamEnd.Right, ReinforcementRole.TopLongitudinal,
                    Qualified("is456.beam.anchorage.check/v1")),
                new(BeamEnd.Right, ReinforcementRole.BottomLongitudinal,
                    Qualified("is456.beam.anchorage.check/v1"))
            ],
            [
                new("J-L", Qualified("joint:left")),
                new("J-R", Qualified("joint:right"))
            ]);
        var complete = Detailing.CheckSeismicDetailing(new("IS13920-WP05", SeismicApplicability.Is13920_2016, context));
        var partial = Detailing.CheckSeismicDetailing(new("IS13920-WP05", SeismicApplicability.Is13920_2016));
        var ordinary = Detailing.CheckSeismicDetailing(new("IS456-WP05", SeismicApplicability.OrdinaryIs456));

        Assert.Equal(EngineeringState.Pass, complete.Engineering);
        Assert.Equal(70_000, complete.Outputs!.GoverningShearN, 12);
        Assert.Contains(complete.Outputs.RuleChecks, r => r.RuleId == "CAPACITY_SHEAR" && r.Passed);
        Assert.Equal(EngineeringState.NotEvaluated, partial.Engineering);
        Assert.Equal(CompletenessState.Partial, partial.Completeness);
        Assert.Equal(ApplicabilityState.NotApplicable, ordinary.Applicability);

        var duplicateFace = Detailing.CheckSeismicDetailing(new(
            "IS13920-WP05",
            SeismicApplicability.Is13920_2016,
            context with
            {
                AnchorageChecks =
                [
                    context.AnchorageChecks[0],
                    context.AnchorageChecks[0],
                    context.AnchorageChecks[2],
                    context.AnchorageChecks[3]
                ]
            }));
        var duplicateJoint = Detailing.CheckSeismicDetailing(new(
            "IS13920-WP05",
            SeismicApplicability.Is13920_2016,
            context with
            {
                DependentJointChecks =
                [
                    context.DependentJointChecks[0],
                    context.DependentJointChecks[0]
                ]
            }));

        Assert.Equal(ExecutionState.RejectedInput, duplicateFace.Execution);
        Assert.Equal("DEPENDENCY.BINDING_INVALID", duplicateFace.Diagnostics[0].Code);
        Assert.Equal(ExecutionState.RejectedInput, duplicateJoint.Execution);
        Assert.Equal("DEPENDENCY.BINDING_INVALID", duplicateJoint.Diagnostics[0].Code);
    }

    [Fact]
    public void ArrangementRequiresTopAndBottomAndChecksLinkObstacleGeometry()
    {
        ReinforcementArrangementCheckRequest Request(IReadOnlyList<ReinforcementRole> roles, IReadOnlyList<CircularObstacle>? obstacles = null) => new(
            "IS456-WP05", "B1", "SPAN-1@MID", "reinforcement:R1", 300, 500, 25, 20,
            [Bar("T1", ReinforcementRole.TopLongitudinal, 60, 60, 16), Bar("T2", ReinforcementRole.TopLongitudinal, 240, 60, 16),
             Bar("B1", ReinforcementRole.BottomLongitudinal, 60, 440, 16), Bar("B2", ReinforcementRole.BottomLongitudinal, 240, 440, 16)],
            [new("L1", 8, 29, 271, 29, 471, 16, true)], roles, 10, obstacles,
            new("PO-1", 260, 460, "sequence:R1"), true);
        var valid = Detailing.CheckReinforcementArrangement(Request([ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal]));
        var partial = Detailing.CheckReinforcementArrangement(Request([ReinforcementRole.TopLongitudinal]));
        var linkClash = Detailing.CheckReinforcementArrangement(Request(
            [ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal],
            [new("JOINT", 29, 250, 10, 1)]));

        Assert.Equal(EngineeringState.Pass, valid.Engineering);
        Assert.Equal(25, valid.Outputs!.LinkChecks[0].SurfaceCoversMm["left"], 12);
        Assert.Equal(250, valid.Outputs.PlacementCheck!.RequiredWidthMm, 12);
        Assert.Equal(EngineeringState.NotEvaluated, partial.Engineering);
        Assert.Equal(EngineeringState.Fail, linkClash.Engineering);
        Assert.Contains(linkClash.Outputs!.ObstacleChecks, check =>
            check.ReinforcementKind == "link_segment" && check.SegmentIndex == 4 && !check.Passed);
    }

    [Fact]
    public void CouplersMayExceedLapDiameterLimitAndMalformedSchedulesAreRejected()
    {
        var bars = new[]
        {
            Bar("C1", ReinforcementRole.BottomLongitudinal, 60, 440, 40),
            Bar("C2", ReinforcementRole.BottomLongitudinal, 240, 440, 40)
        };
        LapCurtailmentCheckRequest Request(SpliceDetail splice) => new(
            "IS456-WP05", "B1", "S1", "demand:R1", "reinforcement:R1", 0, 6000,
            450, 20, 415, BarSurface.Deformed, bars,
            [new("D1", 3000, ReinforcementRole.BottomLongitudinal, 0, 0, 0, "action:1")],
            [splice], []);
        var coupler = Detailing.CheckLapsAndCurtailment(Request(new(
            "CP1", SpliceKind.QualifiedCoupler, ["C1", "C2"], 2500, 2600,
            StressState.Tension, false, 50, "A", "qualification:1", "installation:1")));
        var malformed = Detailing.CheckLapsAndCurtailment(Request(new(
            "LP1", SpliceKind.Lap, ["C1", "C2"], 2500, 2600,
            StressState.Compression, true, 50, "A")));

        Assert.Equal(EngineeringState.Pass, coupler.Engineering);
        Assert.True(coupler.Outputs!.SpliceChecks[0].LapPermittedForDiameter);
        Assert.Equal(ExecutionState.RejectedInput, malformed.Execution);
        Assert.Equal("SPLICE.INVALID", malformed.Diagnostics[0].Code);
    }

    [Fact]
    public void ArrangementUsesFaceRelativePhysicalLayerOrdering()
    {
        var result = Detailing.CheckReinforcementArrangement(new(
            "IS456-WP05", "B1", "S1", "reinforcement:R1", 300, 500, 25, 20,
            [Bar("T1", ReinforcementRole.TopLongitudinal, 60, 60, 16), Bar("T2", ReinforcementRole.TopLongitudinal, 240, 60, 16),
             Bar("B-upper", ReinforcementRole.BottomLongitudinal, 60, 380, 16, layer: 2),
             Bar("B-lower", ReinforcementRole.BottomLongitudinal, 60, 440, 16, layer: 1)],
            [new("L1", 8, 29, 271, 29, 471, 16, true)],
            [ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal], 10,
            PlacementOpening: new("PO1", 260, 460, "sequence:1"), RequirePlacementPlan: true));

        var physicalGap = Assert.Single(result.Outputs!.VerticalClearanceChecks,
            check => check.Kind == "physical_layer_gap" && check.Role == ReinforcementRole.BottomLongitudinal);
        Assert.Equal(2, physicalGap.UpperLayer);
        Assert.Equal(1, physicalGap.LowerLayer);
    }

    [Fact]
    public void CurtailmentRequiresExtraLinkResultOnlyWhenDeclared()
    {
        var bars = new[]
        {
            Bar("B1", ReinforcementRole.BottomLongitudinal, 60, 440),
            Bar("B2", ReinforcementRole.BottomLongitudinal, 150, 440),
            Bar("B3", ReinforcementRole.BottomLongitudinal, 240, 440, end: 5000)
        };
        var cutoff = new CurtailmentDetail(
            "CUT", "B3", 4000, 5000, AnchorageDirection.IncreasingX, "D", 600,
            ["B1", "B2"], Qualified("is456.beam.anchorage.check/v1"),
            Qualified("is456.beam.shear.check/v1"), ExtraLinksRequired: false);
        var request = new LapCurtailmentCheckRequest(
            "IS456-WP05", "B1", "S1", "demand:R1", "reinforcement:R1", 0, 6000,
            450, 20, 415, BarSurface.Deformed, bars,
            [new("D", 4000, ReinforcementRole.BottomLongitudinal, 600, 0, 0, "action:1")],
            [], [cutoff]);

        var notRequired = Detailing.CheckLapsAndCurtailment(request);
        var requiredMissing = Detailing.CheckLapsAndCurtailment(request with
        {
            Curtailments = [cutoff with { ExtraLinksRequired = true }]
        });

        Assert.Equal(EngineeringState.Pass, notRequired.Engineering);
        Assert.Equal(EngineeringState.Fail, requiredMissing.Engineering);
        Assert.Null(requiredMissing.Outputs!.CurtailmentChecks[0].ExtraLinksResultId);
        Assert.False(requiredMissing.Outputs.CurtailmentChecks[0].ExtraLinksOk);
    }
}
