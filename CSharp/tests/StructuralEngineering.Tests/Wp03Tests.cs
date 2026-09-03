using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp03Tests
{
    private static LocalAxes Axes => new(1, 0, 0, 0, 1, 0, 0, 0, 1);
    private static AnalysisActionIdentity Identity => new("source", "model", "case", "step", "member", "span", "object", "element", "station", "concurrent-row");
    private static BeamTopology Topology() => BeamTopologyBuilder.Build(new(
        [new("A", 0, 0), new("B", 5000, 5000)],
        [new("R", "span-1", 0, 5000, 200000, 1_000_000_000)], 500));

    [Fact]
    public void NormalizationConvertsAndPreservesSixComponentsAndIdentity()
    {
        var normalized = ActionNormalizer.Normalize(new(Identity, ActionBasis.StaticConcurrent, Axes, 1, 2, 3, 4, 5, 6));
        Assert.Equal(1000, normalized.PNewton); Assert.Equal(2000, normalized.V2Newton); Assert.Equal(3000, normalized.V3Newton);
        Assert.Equal(4_000_000, normalized.TNewtonMm); Assert.Equal(5_000_000, normalized.M2NewtonMm); Assert.Equal(6_000_000, normalized.M3NewtonMm);
        Assert.Equal(Identity, normalized.Identity);
    }
    [Fact]
    public void SnapshotNormalizationMatchesWp03RowConformanceIdentity()
    {
        var snapshot = new RawActionSnapshot("source-1", "model-1", "analysis-epoch-1", "result-epoch-1", ForceUnit.Kilonewton, MomentUnit.KilonewtonMetre, StationUnit.Metre,
            [new SnapshotLocalAxes("local-123", new(1, 0, 0), new(0, 1, 0), new(0, 0, 1))],
            [new RawActionRow("source-row-1", "member-1", "span-1", "object-1", "element-1", "local-123", 2.5, .5, "ULS-1", "maximum", 1, ActionConcurrency.ComponentEnvelope, 1, 2, 3, 4, 5, 6)]);
        var result = ActionNormalizer.NormalizeSnapshot(snapshot);
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal("action_row_id:pf4-canonical-json-v1:2667bdfe26231eea46cf6f1ad5bfaf585b42470997ef6a2427a76e29c6f14c38", result.Outputs!.Rows[0].RowId);
        Assert.Equal("action_snapshot_id:pf4-canonical-json-v1:c9f8fd88900595bc769f6c4750ede9879adc24e3c89271f069213d80fc5a9612", result.Outputs.SnapshotId);
    }
    [Fact]
    public void InvalidAxesAreRejected() => Assert.Throws<ArgumentException>(() => ActionNormalizer.Normalize(new(Identity, ActionBasis.StaticConcurrent, new(1, 0, 0, 1, 0, 0, 0, 0, 1), 0, 0, 0, 0, 0, 0)));
    [Fact]
    public void TopologyBuildsTwoSpansAndRejectsGap()
    {
        var valid = BeamTopologyBuilder.Build(new([new("A", 0, 0), new("B", 5000, 4800), new("C", 10000, 9600)], [new("R1", "span-1", 0, 5000, 200000, 1e9), new("R2", "span-2", 5000, 10000, 200000, 1e9)], 500));
        Assert.Equal(2, valid.PhysicalSpans.Count); Assert.Equal(5000, valid.PhysicalSpans[0].DesignLengthMm);
        Assert.Throws<ArgumentException>(() => BeamTopologyBuilder.Build(new([new("A", 0, 0), new("B", 5000, 5500)], [])));
    }
    [Fact]
    public void SimplySupportedUdlHasExpectedReactionsMomentAndDeflection()
    {
        var result = PlanarBeamSolver.Solve(new(Topology(), [new("A", 0, true), new("mid", 2500), new("B", 5000, true)], [new("element-1", -10)], [], []));
        Assert.Equal(25_000, result.Reactions.Single(r => r.NodeId == "A").V2N, 6);
        Assert.Equal(25_000, result.Reactions.Single(r => r.NodeId == "B").V2N, 6);
        // Exact Euler-Bernoulli midspan deflection: 5wL^4/(384EI), downward for a negative V2 load.
        var mid = result.Stations.Single(s => s.NodeId == "mid");
        Assert.Equal(-0.4069010416666667, mid.V2DisplacementMm, 5);
        Assert.Equal(31_250_000, mid.M3Nmm, 5);
        Assert.Equal(50_000, result.Reactions.Sum(r => r.V2N), 6);
    }
    [Fact]
    public void EnvelopeBeamLineSolverProducesActualMidspanUdlResponse()
    {
        var result = PlanarBeamSolver.SolveBeamLine(new("model", "case", [new("A", 0, true, false), new("B", 5000, true, false)], [new("E1", "span-1", "A", "B", 200000, 1e9, -10)], StationIntervals: 20));
        Assert.Equal(ExecutionState.Completed, result.Execution); Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        var mid = result.Outputs!.Stations.Single(x => x.XMm == 2500 && x.Side == "continuous");
        Assert.Equal(-.4069010416666667, mid.VerticalDisplacementMm, 5); Assert.Equal(31_250_000, mid.M3Nmm, 4);
        Assert.Equal(0, result.Outputs.VerticalForceResidualN, 5); Assert.Equal(0, result.Outputs.MomentResidualNmm, 2);
    }
    [Fact]
    public void SnapshotNormalizerRejectsLeftHandedAxesWithSharedDiagnostic()
    {
        var snapshot = new RawActionSnapshot("source", "model", "analysis", "result", ForceUnit.Newton, MomentUnit.NewtonMillimetre, StationUnit.Millimetre,
            [new SnapshotLocalAxes("axis", new(1, 0, 0), new(0, 1, 0), new(0, 0, -1))],
            [new RawActionRow("row", "member", "span", "object", "element", "axis", 0, 0, "case", "step", null, ActionConcurrency.StaticConcurrent, 0, 0, 0, 0, 0, 0)]);
        var result = ActionNormalizer.NormalizeSnapshot(snapshot);
        Assert.Equal(ExecutionState.RejectedInput, result.Execution); Assert.Contains(result.Diagnostics, item => item.Code == "AXIS.INVALID");
    }
    [Fact]
    public void TopologyDefinitionUsesBothSupportFacesAndRejectsCoverageGap()
    {
        var axes = new SnapshotLocalAxes("axis", new(1, 0, 0), new(0, 1, 0), new(0, 0, 1));
        var supports = new[] { new PhysicalSupport("A", 0, -200, 200), new PhysicalSupport("B", 5000, 4800, 5200), new PhysicalSupport("C", 10000, 9800, 10200) };
        var spans = new[] { new TopologySpan("S1", "A", "B", 300, [new("R1", "SEC1", 0, 5000)]), new TopologySpan("S2", "B", "C", 450, [new("R2", "SEC2", 5000, 10000)]) };
        var elements = new[] { new TopologyElementMapping("E1", "S1", 0, 5000), new TopologyElementMapping("E2", "S2", 5000, 10000) };
        var result = BeamTopologyBuilder.Define(new("M1", axes, supports, spans, elements));
        Assert.Equal(ExecutionState.Completed, result.Execution); Assert.Equal(4600, result.Outputs!.Spans[0].ClearSpanMm); Assert.Equal(4900, result.Outputs.Spans[0].EffectiveSpanMm);
        var gap = BeamTopologyBuilder.Define(new("M1", axes, supports, [spans[0] with { SectionRegions = [new("R1", "SEC1", 10, 5000)] }, spans[1]], elements));
        Assert.Equal(ExecutionState.RejectedInput, gap.Execution); Assert.Contains(gap.Diagnostics, item => item.Code == "REGION.COVERAGE");
    }
    [Fact]
    public void EnvelopeSolverReportsPointLoadJumpAndSupportSettlement()
    {
        var point = PlanarBeamSolver.SolveBeamLine(new("model", "point", [new("A", 0, true, false), new("B", 5000, true, false)], [new("E1", "S1", "A", "B", 200000, 1e9)], [new("E1", 2500, -10000)], 10));
        var jump = point.Outputs!.Stations.Where(item => item.XMm == 2500).OrderBy(item => item.Side).ToArray();
        Assert.Equal(2, jump.Length); Assert.Equal(10000, Math.Abs(jump[0].V2N - jump[1].V2N), 6);

        var settlement = PlanarBeamSolver.SolveBeamLine(new("model", "settlement",
            [new("A", 0, true, false), new("B", 5000, true, false, -10), new("C", 10000, true, false)],
            [new("E1", "S1", "A", "B", 200000, 1e9), new("E2", "S2", "B", "C", 200000, 1e9)], StationIntervals: 10));
        Assert.Equal(ExecutionState.Completed, settlement.Execution);
        Assert.All(settlement.Outputs!.Stations.Where(item => item.XMm == 5000), item => Assert.Equal(-10, item.VerticalDisplacementMm, 8));
        Assert.Equal(new[] { 48_000d, -96_000d, 48_000d }, settlement.Outputs.Reactions.Select(item => Math.Round(item.V2N, 6)));
        Assert.Equal(0, settlement.Outputs.Reactions.Sum(item => item.V2N), 5);
    }
    [Fact]
    public void UnstableModelIsRejected() => Assert.Throws<InvalidOperationException>(() => PlanarBeamSolver.Solve(new(Topology(), [new("A", 0), new("B", 5000)], [], [], [])));
    [Fact]
    public void EnvelopeBeamLineSolverRejectsUnstableModelWithTypedState()
    {
        var result = PlanarBeamSolver.SolveBeamLine(new("model", "case", [new("A", 0, false, false), new("B", 5000, false, false)], [new("E1", "span-1", "A", "B", 200000, 1e9)], StationIntervals: 2));
        Assert.Equal(ExecutionState.RejectedInput, result.Execution); Assert.Contains(result.Diagnostics, x => x.Code == "ANALYSIS.UNSTABLE");
    }
}
