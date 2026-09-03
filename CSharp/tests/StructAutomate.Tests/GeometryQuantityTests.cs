using StructAutomate.Contracts;
using StructAutomate.Engineering;
using Xunit;

namespace StructAutomate.Tests;

public class GeometryQuantityTests
{
    [Fact]
    public void MixedDiameterLayersUseAreaWeightedCentroidAndCorrectTensionFace()
    {
        BarPosition[] bars = [new("B1","L1",20,60,450),new("B2","L1",20,240,450),new("B3","L2",16,150,390)];
        var request = new ReinforcementGeometryRequest("1.0.0",300,500,25,8,25,TensionFace.Bottom,bars);
        var result = ReinforcementGeometry.Evaluate(request);
        Assert.True(result.Fits);
        Assert.Equal(829.3804605477, result.AreaMm2, 8); // Two 20 mm + one 16 mm bar.
        Assert.Equal(150, result.CentroidXFromLeftMm, 8);
        Assert.InRange(result.EffectiveDepthMm, 435.4545454, 435.4545455);
        Assert.Equal(500 - result.EffectiveDepthMm, ReinforcementGeometry.Evaluate(request with { TensionFace = TensionFace.Top }).EffectiveDepthMm, 8);
    }

    [Fact]
    public void InsufficientCoverAndClearSpacingRemainVisible()
    {
        var result = ReinforcementGeometry.Evaluate(new("1.0.0",300,500,25,8,25,TensionFace.Bottom,
            [new("B1","L1",20,20,450),new("B2","L1",20,45,450)]));
        Assert.False(result.Fits);
        Assert.Contains(result.FitProblems, p => p.Code == "bar_cover");
        Assert.Contains(result.FitProblems, p => p.Code == "bar_spacing");
    }

    [Fact]
    public void QuantitiesUseActualBarsAndSelectedContactFaces()
    {
        var result = QuantityCalculator.Calculate(new("1.0.0",7850,
            [new("LONG",20,4,[new("full resolved length",6000)],[])],
            [new("B1",150000,6000)], [new("B1",6000,300,500,500,0,0)],
            new("INR",new(2026,9,3),"example rates",60,6000,500)));
        Assert.Equal(59.18760559, result.SteelMassKg, 7);
        Assert.Equal(.9, result.ConcreteVolumeM3, 10);
        Assert.Equal(7.8, result.FormworkAreaM2, 10);
        Assert.NotNull(result.Cost);
        Assert.Equal(12851.2563356, (double)result.Cost.Total, 5);
    }

    [Fact]
    public void BendLengthUsesCentrelineRadiusAndNoHiddenHookAllowance()
    {
        var result = QuantityCalculator.Calculate(new("1.0.0",7850,
            [new("HOOK",16,1,[new("straight",1000)],[new("90 degree end",90,32)])],[],[]));
        Assert.Equal(1062.8318530718, result.Bars[0].CutLengthEachMm, 8);
        Assert.Null(result.Cost);
    }

    [Fact]
    public void SlabInterfaceAndBulkheadsChangeOnlyExplicitFormworkItems()
    {
        var result = QuantityCalculator.Calculate(new("1.0.0",7850,[],[],
            [new("B1",6000,300,350,350,150000,0)]));
        Assert.Equal(6.15, result.FormworkAreaM2, 10);
    }

    [Fact]
    public void DeductionCannotCreateNegativeFormworkQuantity()
    {
        Assert.Throws<InputValidationException>(() => QuantityCalculator.Calculate(new("1.0.0",7850,[],[],
            [new("B1",6000,300,0,0,0,2000000)])));
    }
}
