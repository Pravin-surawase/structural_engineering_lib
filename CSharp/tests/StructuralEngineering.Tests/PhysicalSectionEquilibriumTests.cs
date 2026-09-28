using System.Text.Json;
using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using Xunit;

namespace StructuralEngineering.Tests;

public class PhysicalSectionEquilibriumTests
{
    public static IEnumerable<object[]> ReferenceVectors()
    {
        using var stream = typeof(PhysicalSectionEquilibriumTests).Assembly
            .GetManifestResourceStream("Wp01PerBarVectors.json")!;
        using var document = JsonDocument.Parse(stream);
        foreach (var vector in document.RootElement.GetProperty("vectors").EnumerateArray())
            yield return [vector.GetProperty("id").GetString()!, vector.GetProperty("input").GetRawText(),
                vector.GetProperty("expected").GetRawText()];
    }

    [Theory]
    [MemberData(nameof(ReferenceVectors))]
    public void PerBarSectionMatchesIndependentReference(string id, string inputJson, string expectedJson)
    {
        using var inputDocument = JsonDocument.Parse(inputJson);
        using var expectedDocument = JsonDocument.Parse(expectedJson);
        var input = inputDocument.RootElement;
        var expected = expectedDocument.RootElement;
        double Value(string key) => input.GetProperty(key).GetDouble();
        var bars = input.GetProperty("bars").EnumerateArray().Select(bar => new BarCoordinate(
            bar.GetProperty("bar_id").GetString()!, bar.GetProperty("diameter_mm").GetDouble(),
            bar.GetProperty("x_from_left_mm").GetDouble(), bar.GetProperty("y_from_top_mm").GetDouble(),
            bar.GetProperty("face").GetString() == "bottom" ? Face.Bottom : Face.Top,
            bar.GetProperty("layer").GetInt32())).ToArray();
        var kind = input.GetProperty("section_kind").GetString() switch
        {
            "t_beam" => SectionKind.TBeam,
            "l_beam" => SectionKind.LBeam,
            _ => SectionKind.Rectangular
        };
        var face = input.GetProperty("tension_face").GetString() == "bottom" ? Face.Bottom : Face.Top;
        var request = new FlexuralCapacityRequest(id, kind, Value("web_width_mm"), Value("depth_mm"),
            Value("concrete_strength_n_per_mm2"), Value("steel_yield_strength_n_per_mm2"), bars, face,
            kind == SectionKind.Rectangular ? null : Value("flange_width_mm"),
            kind == SectionKind.Rectangular ? null : Value("flange_thickness_mm"));
        var result = Flexure.Capacity(request);
        var actual = result.Outputs!;
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(expected.GetProperty("engineering").GetString(), result.Engineering.ToString().ToLowerInvariant());
        Assert.Equal("is456-flexural-capacity-wp01-v3", result.Provenance.MethodRevisionId);
        Assert.InRange(Math.Abs(actual.EquilibriumNeutralAxisDepthMm - expected.GetProperty("neutral_axis_depth_mm").GetDouble()), 0, 1e-7);
        Assert.InRange(Math.Abs(actual.CapacityKnM - expected.GetProperty("capacity_knm").GetDouble()), 0, 1e-7);
        Assert.InRange(Math.Abs(actual.ForceResidualN), 0, 1e-6);
        Assert.Equal(actual.EquilibriumNeutralAxisDepthMm, actual.CapacityNeutralAxisDepthMm);
        Assert.Equal(expected.GetProperty("maximum_tension_strain").GetDouble(), actual.MaximumTensionStrain, 12);
        Assert.Equal(expected.GetProperty("minimum_tension_strain").GetDouble(), actual.MinimumTensionStrain, 12);
        var referenceBars = expected.GetProperty("bar_responses").EnumerateArray().ToArray();
        Assert.Equal(referenceBars.Length, actual.BarResponses.Count);
        for (var i = 0; i < referenceBars.Length; i++)
        {
            var reference = referenceBars[i];
            var bar = actual.BarResponses[i];
            Assert.Equal(reference.GetProperty("bar_id").GetString(), bar.BarId);
            foreach (var (field, value) in new[]
                     {
                         ("depth_from_compression_face_mm", bar.DepthFromCompressionFaceMm), ("area_mm2", bar.AreaMm2),
                         ("strain", bar.Strain), ("steel_stress_n_per_mm2", bar.SteelStressNPerMm2),
                         ("displaced_concrete_stress_n_per_mm2", bar.DisplacedConcreteStressNPerMm2), ("net_force_n", bar.NetForceN)
                     })
                Assert.InRange(Math.Abs(value - reference.GetProperty(field).GetDouble()), 0, 1e-6);
        }
        if (result.Engineering == EngineeringState.Fail)
        {
            var demand = new FlexureCheckRequest(request, face == Face.Bottom ? 1 : null, face == Face.Top ? -1 : null);
            Assert.Equal(EngineeringState.Fail, BeamOperations.CheckFlexure(demand).Engineering);
        }
    }
}
