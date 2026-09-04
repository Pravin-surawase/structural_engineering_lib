using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reinforcement;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp01Tests
{
    private static BarCoordinate[] Bars =>
    [
        new("T1", 16, 75, 42, Face.Top),
        new("T2", 16, 225, 42, Face.Top),
        new("B1", 20, 65, 450, Face.Bottom),
        new("B2", 20, 150, 450, Face.Bottom),
        new("B3", 20, 235, 450, Face.Bottom)
    ];

    private static FlexuralCapacityRequest Capacity(SectionKind kind = SectionKind.Rectangular) =>
        new("IS456-WP01", kind, 300, 500, 25, 415, Bars, Face.Bottom,
            kind == SectionKind.Rectangular ? null : 800,
            kind == SectionKind.Rectangular ? null : 100);

    [Fact]
    public void FoundationValuesHaveExplicitUnitsInputsAndCrossLanguageIdentity()
    {
        var area = ReinforcementOperations.BarArea(new("IS456-WP01", 16));
        var mass = ReinforcementOperations.MassPerLength(new("IS456-WP01", 16, 7850));
        Assert.Equal(201.06192982974676, area.Outputs!.Value, 11);
        Assert.Equal(1.5783361491635123, mass.Outputs!.Value, 11);
        Assert.Equal("structural-operation-result/v1", area.SchemaVersion);
        Assert.Equal(7850d, mass.EffectiveInputs["density_kg_per_m3"].Value);
        Assert.Equal("normalized_input_id:pf4-canonical-json-v1:b65de276c207ad0a818944f9a935abd8e31643419f247dbbd9e9840b8468865a", area.NormalizedInputId);
        Assert.Equal("normalized_input_id:pf4-canonical-json-v1:69cd9b640c8a651f32385cd3daa093271d7880efdb8d4b842a29e488bae8ea22", mass.NormalizedInputId);
        Assert.StartsWith("calculation_id:pf4-canonical-json-v1:", area.CalculationId);
        Assert.StartsWith("result_id:pf4-canonical-json-v1:", area.ResultId);
        Assert.Equal(area.CalculationId, ReinforcementOperations.BarArea(new("IS456-WP01", 16)).CalculationId);
    }

    [Fact]
    public void CanonicalJsonUsesSortedCompactUtf8AndKnownHash()
    {
        var value = new Dictionary<string, int> { ["b"] = 2, ["a"] = 1 };
        Assert.Equal("{\"a\":1,\"b\":2}", System.Text.Encoding.UTF8.GetString(ResultFactory.CanonicalJsonBytes(value)));
        Assert.Equal("normalized_input_id:pf4-canonical-json-v1:43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777", ResultFactory.NormalizedInputId(value));
    }

    [Fact]
    public void GeometryUsesActualFacesLayersAndCoordinates()
    {
        var bars = Bars.Concat([
            new BarCoordinate("B4", 16, 110, 405, Face.Bottom, 2),
            new BarCoordinate("B5", 16, 190, 405, Face.Bottom, 2)]).ToArray();
        var request = new GeometryRequest("IS456-WP01", 300, 500, 25, 8, 25, bars);
        var result = ReinforcementOperations.EvaluateGeometry(request);
        Assert.Equal(7, result.Outputs!.BarCount);
        Assert.True(result.Outputs.Faces.ContainsKey("top"));
        Assert.True(result.Outputs.Faces.ContainsKey("bottom"));
        Assert.Equal(EngineeringState.Pass, result.Engineering);
        var depth = ReinforcementOperations.EffectiveDepth(request, Face.Bottom);
        Assert.Equal(result.Outputs.Faces["bottom"].EffectiveDepthMm, depth.Outputs!.EffectiveDepthMm, 10);
    }

    [Fact]
    public void OverlappingBarsCompleteWithEngineeringFailure()
    {
        BarCoordinate[] bars = [new("B1", 20, 100, 450, Face.Bottom), new("B2", 20, 110, 450, Face.Bottom)];
        var result = ReinforcementOperations.EvaluateGeometry(new("IS456-WP01", 300, 500, 25, 8, 25, bars));
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "GEOMETRY.SPACING");
    }

    [Fact]
    public void RectangularSinglyAndDoublyReinforcedCapacityIsCalculated()
    {
        var singlyRequest = Capacity() with { Bars = Bars.Where(bar => bar.Face == Face.Bottom).ToArray() };
        var singly = Flexure.Capacity(singlyRequest);
        var doubly = Flexure.Capacity(Capacity());
        Assert.Equal(EngineeringState.Pass, singly.Engineering);
        Assert.Equal(EngineeringState.Pass, doubly.Engineering);
        Assert.True(doubly.Outputs!.CompressionSteelAreaMm2 > 0);
        Assert.True(doubly.Outputs.CapacityKnM > singly.Outputs!.CapacityKnM);
    }

    [Fact]
    public void IndependentRectangularCapacityVectorMatches()
    {
        BarCoordinate[] bars =
        [
            new("B1", 20, 80, 450, Face.Bottom),
            new("B2", 20, 220, 450, Face.Bottom)
        ];
        var result = Flexure.Capacity(Capacity() with { Bars = bars });
        Assert.Equal(94.07913916844615, result.Outputs!.CapacityKnM, 9);
        Assert.Equal(84.02015019100702, result.Outputs.EquilibriumNeutralAxisDepthMm, 9);
    }

    [Fact]
    public void FlangedPositiveUsesFlangeAndNegativeUsesWeb()
    {
        var request = Capacity(SectionKind.TBeam);
        var positive = Flexure.Capacity(request);
        var negative = Flexure.Capacity(request with { TensionFace = Face.Top });
        Assert.True(positive.Outputs!.UsesCompressionFlange);
        Assert.False(negative.Outputs!.UsesCompressionFlange);
        Assert.True(positive.Outputs.CapacityKnM > negative.Outputs.CapacityKnM);
    }

    [Fact]
    public void FlexureChecksBothSignsAgainstPhysicalFaces()
    {
        var result = BeamOperations.CheckFlexure(new(Capacity(), 100, -50));
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal([Face.Bottom, Face.Top], result.Outputs!.Checks.Select(check => check.TensionFace));
        Assert.True(result.Outputs.GoverningUtilization > 0);
    }

    [Fact]
    public void InvalidAndUnsupportedInputsRemainIndependentStates()
    {
        var invalid = ReinforcementOperations.BarArea(new("IS456-WP01", 0));
        var unsupported = Flexure.Capacity(Capacity() with { AxialForceKn = 10 });
        Assert.Equal(ExecutionState.RejectedInput, invalid.Execution);
        Assert.Equal(EngineeringState.NotEvaluated, invalid.Engineering);
        Assert.Equal(ApplicabilityState.NotApplicable, unsupported.Applicability);
        Assert.Equal(CompletenessState.CompleteForScope, unsupported.Completeness);
    }

    [Fact]
    public void OverReinforcedSupplyCannotPass()
    {
        var bars = Enumerable.Range(0, 4)
            .Select(index => new BarCoordinate($"B{index}", 25, 55 + index * 63, 450, Face.Bottom))
            .ToArray();
        var result = BeamOperations.CheckFlexure(new(Capacity() with { Bars = bars }, 10));
        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "FLEXURE.OVER_REINFORCED");
    }
}
