using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class EtabsSourceQualificationTests
{
    private static readonly EtabsSourceScope Scope = new(["B1"], [], ["ULS"]);

    [Fact]
    public void NativeUnitBasesProduceTheSamePhysicalDimensionsAndStress()
    {
        var metres = EtabsSourceQualification.Units(6, 9);
        var millimetres = EtabsSourceQualification.Units(9, 9);
        Assert.Equal(6250, EtabsSourceQualification.ConvertFinite(6.25, metres.LengthToMm));
        Assert.Equal(6250, EtabsSourceQualification.ConvertFinite(6250, millimetres.LengthToMm));
        Assert.Equal(30, EtabsSourceQualification.ConvertFinite(30_000, metres.StressToNPerMm2));
        Assert.Equal(30, EtabsSourceQualification.ConvertFinite(30, millimetres.StressToNPerMm2));
        Assert.Equal(9, metres.DatabaseUnits);
        Assert.Throws<ArgumentException>(() => EtabsSourceQualification.Units(5, 9));
        Assert.Throws<ArgumentException>(() => EtabsSourceQualification.ConvertFinite(double.MaxValue, 1000));
    }

    [Fact]
    public void NestedStaticClosureKeepsFactorsAndDoesNotAdmitUnrelatedDynamicCases()
    {
        EtabsSourceLoadNode[] nodes = [
            Combo("ULS", [new("combination", "Gravity", 1.5), new("case", "Live", -0.25)]),
            Combo("Gravity", [new("case", "Dead", 1), new("case", "Live", 0.5)]),
            Case("Dead"), Case("Live"), Pattern("Dead"), Pattern("Live"),
            new("case", "UnrelatedSpectrum", 4, 4, true, null, [], [])];
        var closure = Assert.Single(EtabsSourceQualification.ResolveLoads(Scope, nodes));
        Assert.Equal("complete_static_source", closure.State);
        Assert.Equal(6, closure.DependencyIds.Count);
        Assert.DoesNotContain("case:UnrelatedSpectrum", closure.DependencyIds);
        Assert.Equal(-0.25, nodes[0].Terms[1].Factor);
        Assert.Equal(1.5, nodes[0].Terms[0].Factor);
        Assert.Empty(closure.Restrictions);
    }

    [Fact]
    public void ASelectedDynamicDependencyDoesNotEraseTheCompletePeerRoot()
    {
        var scope = new EtabsSourceScope(["B1"], ["Dead", "Spectrum"], []);
        EtabsSourceLoadNode[] nodes = [Case("Dead"), Pattern("Dead"), new("case", "Spectrum", 4, 4, true, null, [], [])];
        var result = EtabsSourceQualification.ResolveLoads(scope, nodes);
        Assert.Equal(2, result.Count);
        Assert.Equal("complete_static_source", result[0].State);
        Assert.Equal("unsupported", result[1].State);
        Assert.Contains(result[1].Restrictions, r => r.Code == "SOURCE.CASE_UNSUPPORTED");
    }

    [Fact]
    public void CycleMissingTermAndInitialCaseRetainTheirExactDependencies()
    {
        EtabsSourceLoadNode[] nodes = [Combo("ULS", [new("combination", "ULS", 1), new("case", "Missing", 1), new("case", "Dead", 1)]),
            Case("Dead") with { InitialCase = "PDelta" }, Pattern("Dead"), new("case", "PDelta", 2, 4, false, "", [], [])];
        var result = Assert.Single(EtabsSourceQualification.ResolveLoads(Scope, nodes));
        Assert.Contains("case:PDelta", result.DependencyIds);
        Assert.Contains(result.Restrictions, r => r.Code == "SOURCE.DEPENDENCY_CYCLE");
        Assert.Contains(result.Restrictions, r => r.Code == "SOURCE.DEPENDENCY_UNAVAILABLE");
        Assert.Contains(result.Restrictions, r => r.Code == "SOURCE.INITIAL_CASE_UNSUPPORTED");
    }

    [Theory]
    [InlineData(0, 1)]
    [InlineData(21, 1)]
    [InlineData(1, 0)]
    [InlineData(1, 33)]
    public void ScopeBoundsRejectUnboundedOrEmptyRequests(int frames, int roots) =>
        Assert.Throws<ArgumentException>(() => EtabsSourceQualification.ValidateScope(new(
            Enumerable.Range(0, frames).Select(i => "b" + i).ToArray(),
            Enumerable.Range(0, roots).Select(i => "c" + i).ToArray(), [])));

    [Fact]
    public void UnselectedRootCannotBecomeAQualifiedSource()
    {
        var result = Assert.Single(EtabsSourceQualification.ResolveLoads(new(["B1"], ["Dead"], []),
            [Case("Dead") with { SelectedForOutput = false }, Pattern("Dead")]));
        Assert.Equal("unavailable", result.State);
        Assert.Contains(result.Restrictions, r => r.Code == "SOURCE.SELECTION_UNAVAILABLE");
    }

    private static EtabsSourceLoadNode Case(string name) => new("case", name, 1, 4, true, "", [new("pattern", name, 1)], []);
    private static EtabsSourceLoadNode Pattern(string name) => new("pattern", name, 1, null, null, null, [], [], 1);
    private static EtabsSourceLoadNode Combo(string name, EtabsSourceLoadTerm[] terms) => new("combination", name, 0, null, true, null, terms, []);
}
