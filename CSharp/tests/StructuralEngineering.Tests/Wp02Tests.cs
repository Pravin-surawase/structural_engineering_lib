using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp02Tests
{
    private static TransverseLink Link(bool closed = true, double spacingMm = 100) =>
        new("L1", 8, 2, 2, spacingMm, 415, closed, 230, 420);

    private static ShearCapacityRequest ShearRequest(ShearAxis axis = ShearAxis.V2, TransverseLink? link = null) =>
        new("IS456-WP02", axis, 300, 450, 25, 942.4777960769379, link ?? Link());

    private static BarCoordinate[] Bars =>
    [
        new("TL", 20, 60, 45, Face.Top), new("TM", 20, 150, 45, Face.Top),
        new("TR", 20, 240, 45, Face.Top), new("BL", 20, 60, 450, Face.Bottom),
        new("BM", 20, 150, 450, Face.Bottom), new("BR", 20, 240, 450, Face.Bottom)
    ];

    private static FlexuralCapacityRequest FlexureRequest() =>
        new("IS456-WP02", SectionKind.Rectangular, 300, 500, 25, 415, Bars, Face.Bottom);

    private static ConcurrentActionRow Action(ActionBasis basis = ActionBasis.StaticConcurrent) =>
        new("R1", "S1", basis, 50, 0, 5, 0, 50, "analysis:one");

    [Fact]
    public void ShearCapacityUsesActualLinkAndTableValues()
    {
        var result = Shear.Capacity(ShearRequest());
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(0.5534021442552741, result.Outputs!.TauCNPerMm2, 12);
        Assert.Equal(3.1, result.Outputs.TauCMaxNPerMm2, 12);
        Assert.Equal(100.53096491487338, result.Outputs.LinkAreaMm2, 10);
        Assert.True(result.Outputs.SpacingPass);
        Assert.True(result.Outputs.MinimumLinkPass);
    }

    [Fact]
    public void ShearCheckHandlesBothAxesAndStationSigns()
    {
        var result = BeamOperations.CheckShear(new ShearCheckRequest(
            [ShearRequest(ShearAxis.V2), ShearRequest(ShearAxis.V3)],
            [new("S1", ShearAxis.V2, -100), new("S1", ShearAxis.V3, 80)]));
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal([ShearAxis.V2, ShearAxis.V3], result.Outputs!.Checks.Select(check => check.Axis));
        Assert.True(result.Outputs.GoverningUtilization > 0);
    }

    [Fact]
    public void MissingActualLinkIsNotEvaluated()
    {
        var request = new ShearCapacityRequest("IS456-WP02", ShearAxis.V2, 300, 450, 25,
            942.4777960769379, null);
        var result = Shear.Capacity(request);
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(CompletenessState.Partial, result.Completeness);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "REINFORCEMENT.REQUIRED");
    }

    [Theory]
    [InlineData(1, 0, true)]
    [InlineData(-1, 0, true)]
    [InlineData(1, 5, true)]
    [InlineData(-1, 5, true)]
    [InlineData(1, 50, false)]
    [InlineData(-1, 50, false)]
    public void OppositeTensionSteelIsOnlyRequiredForPositiveEquivalentMoment(int sign, double torsion, bool passed)
    {
        var active = sign > 0 ? Face.Bottom : Face.Top;
        var bars = Bars.Select(bar => bar.Face == active ? bar : bar with { DiameterMm = 8 }).ToArray();
        var result = BeamOperations.CheckTorsion(new("IS456-WP02",
            Action() with { M3KnM = sign * 50, TorsionKnM = torsion },
            FlexureRequest() with { Bars = bars }, Link(), ["TL", "TR", "BL", "BR"]));
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(passed, result.Outputs!.LongitudinalPass);
        Assert.Equal(passed ? EngineeringState.Pass : EngineeringState.Fail, result.Engineering);
    }

    [Fact]
    public void TorsionRejectsComponentEnvelope()
    {
        var request = new TorsionCheckRequest("IS456-WP02", Action(ActionBasis.ComponentEnvelope),
            FlexureRequest(), Link(), ["TL", "TR", "BL", "BR"]);
        var result = BeamOperations.CheckTorsion(request);
        Assert.Equal(ExecutionState.RejectedInput, result.Execution);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "ACTION.CONCURRENCY");
    }

    [Fact]
    public void TorsionDoesNotIgnoreMinorAxisInteraction()
    {
        var action = new ConcurrentActionRow("R1", "S1", ActionBasis.StaticConcurrent,
            50, 4, 5, 3, 50, "analysis:one");
        var request = new TorsionCheckRequest("IS456-WP02", action, FlexureRequest(), Link(),
            ["TL", "TR", "BL", "BR"]);
        var result = BeamOperations.CheckTorsion(request);
        Assert.Equal(ApplicabilityState.NotApplicable, result.Applicability);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "PROFILE.UNSUPPORTED");
    }

    [Fact]
    public void TorsionChecksEquivalentActionsLinksAndPerimeterBars()
    {
        var request = new TorsionCheckRequest("IS456-WP02", Action(), FlexureRequest(), Link(),
            ["TL", "TR", "BL", "BR"]);
        var result = BeamOperations.CheckTorsion(request);
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(76.66666666666667, result.Outputs!.EquivalentShearKn, 10);
        Assert.True(result.Outputs.TransversePass);
        Assert.True(result.Outputs.LongitudinalPass);
        Assert.True(result.Outputs.PerimeterPass);
    }

    [Fact]
    public void OpenLinkIsCompletedEngineeringFailure()
    {
        var request = new TorsionCheckRequest("IS456-WP02", Action(), FlexureRequest(), Link(false),
            ["TL", "TR", "BL", "BR"]);
        var result = BeamOperations.CheckTorsion(request);
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "TORSION.CLOSED_LINK_REQUIRED");
    }

    [Theory]
    [InlineData(100, true)]
    [InlineData(125, false)]
    public void TorsionUsesLongitudinalCornerCentres(double spacingMm, bool passed)
    {
        BarCoordinate[] bars =
        [
            new("TL", 20, 50, 50, Face.Top), new("TR", 20, 250, 50, Face.Top),
            new("BL", 20, 50, 350, Face.Bottom), new("BR", 20, 250, 350, Face.Bottom)
        ];
        var section = new FlexuralCapacityRequest(
            "LIB-027-D-STATION", SectionKind.Rectangular, 300, 400, 25, 415, bars, Face.Bottom);
        var action = new ConcurrentActionRow(
            "ULS-1", "interior", ActionBasis.StaticConcurrent, 60, 0, 15, 0, 15, "independent-static-row");
        var link = new TransverseLink("S8", 8, 2, 2, spacingMm, 415, true, 242, 342);
        var result = BeamOperations.CheckTorsion(new(
            "LIB-027-D-STATION", action, section, link, ["TL", "TR", "BL", "BR"]));
        Assert.Equal(passed ? EngineeringState.Pass : EngineeringState.Fail, result.Engineering);
        Assert.Equal(0.9140008309098463, result.Outputs!.RequiredLinkAreaPerSpacingMm, 12);
        Assert.Equal(140, result.Outputs.EquivalentShearKn, 10);
        Assert.Equal(146, result.Outputs.MaximumSpacingMm, 10);
        Assert.Equal(200, result.Outputs.CornerWidthMm!.Value, 10);
        Assert.Equal(300, result.Outputs.CornerDepthMm!.Value, 10);
        Assert.Equal(0.6924248719013987, result.Outputs.TorsionAreaPerSpacingMm!.Value, 12);
        Assert.Equal(0.2215759590084476, result.Outputs.ShearAreaPerSpacingMm!.Value, 12);
        Assert.True(result.Outputs.LongitudinalPass);
        Assert.Equal(passed, result.Outputs.TransversePass);
    }

    [Fact]
    public void TorsionRequiresResolvedRectangularCornerCentres()
    {
        var result = BeamOperations.CheckTorsion(new(
            "IS456-WP02", Action(), FlexureRequest(), Link(), ["TL", "TR", "BL"]));
        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Contains(result.Diagnostics, item => item.Code == "TORSION.CORNER_GEOMETRY_REQUIRED");
    }

    [Theory]
    [InlineData(45)]
    [InlineData(55)]
    public void ZeroTorsionRetainsExistingPerimeterCheck(double topLeftDepthMm)
    {
        var bars = Bars.Select(bar => bar.BarId == "TL" ? bar with { YFromTopMm = topLeftDepthMm } : bar).ToArray();
        var result = BeamOperations.CheckTorsion(new(
            "IS456-WP02", Action() with { TorsionKnM = 0 },
            FlexureRequest() with { Bars = bars }, Link(), ["TL", "TR", "BL", "BR"]));
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.True(result.Outputs!.PerimeterPass);
        Assert.Null(result.Outputs.CornerWidthMm);
        Assert.Equal("is456-torsion-check-wp02-v2", result.Provenance.MethodRevisionId);
    }
}
