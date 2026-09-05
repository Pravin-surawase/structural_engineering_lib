using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class Wp10AssumptionTests
{
    [Fact]
    public void CanonicalPresetMapsToExplicitDemoInputsWithoutProjectApproval()
    {
        var input = OfflineAssumptions.Read(Defaults());
        Assert.False(input.ProductionIssuanceAllowed);
        Assert.All(input.Values, value => Assert.Equal("demo_default", value.Origin));
        Assert.Equal("30", input.Values.Single(value => value.Key.EndsWith("nominal_cover_to_outermost_reinforcement_mm", StringComparison.Ordinal)).Value);
        Assert.Equal("25", input.Values.Single(value => value.Key.EndsWith("concrete_strength_n_per_mm2", StringComparison.Ordinal)).Value);
        Assert.Contains(input.Values, value => value.Unit == "N/mm²" && value.Value == "500");
        Assert.Equal(input.Revision, OfflineAssumptions.Read(Defaults()).Revision);
    }

    [Fact]
    public void EditedInputChangesIdentityAndOriginButNeverBecomesImportedFact()
    {
        var original = OfflineAssumptions.Read(Defaults());
        var values = Defaults(); values[5] = "40";
        var edited = OfflineAssumptions.Read(values);
        Assert.NotEqual(original.Revision, edited.Revision);
        Assert.Equal("engineer_edit_demo_basis", edited.Values[5].Origin);
        Assert.False(edited.ProductionIssuanceAllowed);
    }

    [Fact]
    public void BlankIsNotZeroAndExplicitZeroRateIsAccepted()
    {
        var values = Defaults(); values[^1] = "";
        Assert.Contains("blank is not zero", Assert.Throws<ArgumentException>(() => OfflineAssumptions.Read(values)).Message);
        values[^1] = "0";
        Assert.Equal("0", OfflineAssumptions.Read(values).Values[^1].Value);
        values[5] = "0";
        Assert.Contains("Nominal cover", Assert.Throws<ArgumentException>(() => OfflineAssumptions.Read(values)).Message);
    }

    [Theory]
    [InlineData("NaN")]
    [InlineData("Infinity")]
    [InlineData("-1")]
    public void NonphysicalNumericInputsIdentifyTheEditableCell(string invalid)
    {
        var values = Defaults(); values[2] = invalid;
        Assert.Contains("Assumptions!B8", Assert.Throws<ArgumentException>(() => OfflineAssumptions.Read(values)).Message);
    }

    [Fact]
    public void InvalidBarListCannotBecomeAnAcceptedCatalogue()
    {
        var values = Defaults(); values[9] = "12, 0, 16";
        Assert.Throws<ArgumentException>(() => OfflineAssumptions.Read(values));
        values[9] = "12, 12";
        Assert.Throws<ArgumentException>(() => OfflineAssumptions.Read(values));
    }

    private static string?[] Defaults() => OfflineAssumptions.Definitions.Select(value => (string?)value.DefaultValue).ToArray();
}
