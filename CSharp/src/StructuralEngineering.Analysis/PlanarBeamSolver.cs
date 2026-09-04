using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Analysis;

/// <summary>Linear Euler-Bernoulli solver for local V2 displacement and M3 rotation only.</summary>
public static class PlanarBeamSolver
{
    public static PlanarBeamSolveResult Solve(PlanarBeamSolveRequest request)
    {
        if (request.Topology is null || request.Nodes is null || request.Nodes.Count < 2) throw new ArgumentException("Topology and at least two nodes are required.", nameof(request));
        if (request.Topology.Elements.Count == 0) throw new NotSupportedException("A planar model needs mapped analysis elements.");
        var original = request.Nodes.OrderBy(n => n.StationMm).ToArray();
        if (original.Any(n => string.IsNullOrWhiteSpace(n.NodeId) || !double.IsFinite(n.StationMm)) || original.Select(n => n.NodeId).Distinct().Count() != original.Length) throw new ArgumentException("Node identities and stations must be finite and unique.", nameof(request));
        var points = request.PointLoads ?? [];
        var meshStations = original.Select(n => n.StationMm).Concat(points.Select(p => Element(request.Topology, p.ElementId).StartStationMm + p.DistanceFromElementStartMm)).Distinct().OrderBy(x => x).ToArray();
        if (meshStations.Length < 2 || meshStations.Zip(meshStations.Skip(1)).Any(pair => pair.Second <= pair.First)) throw new ArgumentException("Nodes must be ordered.", nameof(request));
        foreach (var point in points)
        {
            var e = Element(request.Topology, point.ElementId);
            if (!double.IsFinite(point.V2N) || point.DistanceFromElementStartMm <= 0 || point.DistanceFromElementStartMm >= e.EndStationMm - e.StartStationMm) throw new NotSupportedException("Point loads must be finite and strictly interior to their element.");
        }
        var dof = meshStations.Length * 2; var k = new double[dof, dof]; var f = new double[dof];
        foreach (var segment in meshStations.Zip(meshStations.Skip(1)))
        {
            var mid = (segment.First + segment.Second) / 2; var e = ElementAt(request.Topology, mid);
            var region = request.Topology.SectionRegions.Single(r => r.RegionId == e.SectionRegionId);
            var l = segment.Second - segment.First; var ei = region.ElasticModulusNPerMm2 * region.MajorAxisInertiaMm4;
            var a = Array.IndexOf(meshStations, segment.First) * 2; var b = a + 2;
            var c = ei / (l * l * l);
            double[,] local = { { 12*c, 6*l*c, -12*c, 6*l*c }, { 6*l*c, 4*l*l*c, -6*l*c, 2*l*l*c }, { -12*c, -6*l*c, 12*c, -6*l*c }, { 6*l*c, 2*l*l*c, -6*l*c, 4*l*l*c } };
            var ids = new[] { a, a + 1, b, b + 1 };
            for (var i = 0; i < 4; i++) for (var j = 0; j < 4; j++) k[ids[i], ids[j]] += local[i, j];
            var q = (request.UniformLoads ?? []).Where(x => x.ElementId == e.ElementId).Sum(x => x.V2NPerMm);
            // Consistent load vector; positive V2 is positive displacement and positive M3 is sagging.
            f[a] += q * l / 2; f[a + 1] += q * l * l / 12; f[b] += q * l / 2; f[b + 1] -= q * l * l / 12;
        }
        foreach (var load in points) { var station = Element(request.Topology, load.ElementId).StartStationMm + load.DistanceFromElementStartMm; f[2 * Array.IndexOf(meshStations, station)] += load.V2N; }
        foreach (var load in request.NodalLoads ?? []) { var node = original.SingleOrDefault(n => n.NodeId == load.NodeId) ?? throw new ArgumentException("Nodal load references an unknown node."); var i = Array.IndexOf(meshStations, node.StationMm) * 2; f[i] += load.V2N; f[i + 1] += load.M3Nmm; }
        var restrained = original.Where(n => n.RestrainV2 || n.RestrainRotationM3).SelectMany(n => new[] { n.RestrainV2 ? 2 * Array.IndexOf(meshStations, n.StationMm) : -1, n.RestrainRotationM3 ? 2 * Array.IndexOf(meshStations, n.StationMm) + 1 : -1 }).Where(i => i >= 0).ToHashSet();
        if (restrained.Count == 0) throw new InvalidOperationException("Model is unstable: no restraints.");
        var free = Enumerable.Range(0, dof).Where(i => !restrained.Contains(i)).ToArray();
        var displacement = new double[dof];
        foreach (var n in original) { var baseDof = 2 * Array.IndexOf(meshStations, n.StationMm); if (n.RestrainV2) displacement[baseDof] = n.PrescribedV2DisplacementMm; if (n.RestrainRotationM3) displacement[baseDof + 1] = n.PrescribedRotationRad; }
        try { var solution = Gaussian(free.Select(i => free.Select(j => k[i, j]).ToArray()).ToArray(), free.Select(i => f[i] - restrained.Sum(j => k[i, j] * displacement[j])).ToArray()); for (var i = 0; i < free.Length; i++) displacement[free[i]] = solution[i]; }
        catch (InvalidOperationException exception) { throw new InvalidOperationException("Model is unstable or has insufficient restraints.", exception); }
        var residual = Multiply(k, displacement).Zip(f).Select(x => x.First - x.Second).ToArray();
        var reactions = original.Where(n => n.RestrainV2 || n.RestrainRotationM3).Select(n => { var i = 2 * Array.IndexOf(meshStations, n.StationMm); return new PlanarBeamReaction(n.NodeId, n.RestrainV2 ? residual[i] : 0, n.RestrainRotationM3 ? residual[i + 1] : 0); }).ToArray();
        var stations = original.Select(n =>
        {
            var i = 2 * Array.IndexOf(meshStations, n.StationMm);
            var e = ElementAt(request.Topology, Math.Clamp(n.StationMm == meshStations[^1] ? n.StationMm - 1e-6 : n.StationMm + 1e-6, meshStations[0] + 1e-6, meshStations[^1] - 1e-6));
            // Recover section actions from equilibrium of the material to the left of the station.
            // Positive M3 is sagging; a negative V2 UDL is downward.
            var v = 0d; var m = 0d;
            foreach (var reaction in reactions)
            {
                var rn = original.Single(node => node.NodeId == reaction.NodeId);
                if (rn.StationMm <= n.StationMm + 1e-8) { v += reaction.V2N; m += reaction.V2N * (n.StationMm - rn.StationMm) + reaction.M3Nmm; }
            }
            foreach (var load in request.NodalLoads ?? [])
            {
                var ln = original.Single(node => node.NodeId == load.NodeId);
                if (ln.StationMm < n.StationMm - 1e-8) { v += load.V2N; m += load.V2N * (n.StationMm - ln.StationMm) + load.M3Nmm; }
            }
            foreach (var load in request.UniformLoads ?? [])
            {
                var ue = Element(request.Topology, load.ElementId); var end = Math.Min(n.StationMm, ue.EndStationMm);
                if (end > ue.StartStationMm) { var length = end - ue.StartStationMm; v += load.V2NPerMm * length; m += load.V2NPerMm * length * (n.StationMm - ue.StartStationMm - length / 2); }
            }
            foreach (var load in points)
            {
                var pe = Element(request.Topology, load.ElementId); var station = pe.StartStationMm + load.DistanceFromElementStartMm;
                if (station < n.StationMm - 1e-8) { v += load.V2N; m += load.V2N * (n.StationMm - station); }
            }
            return new PlanarBeamStationResult(n.NodeId, e.PhysicalSpanId, e.ElementId, n.StationMm, displacement[i], displacement[i + 1], v, m);
        }).ToArray();
        var globalForce = Enumerable.Range(0, meshStations.Length).Sum(node => residual[2 * node] + f[2 * node]);
        var globalMoment = Enumerable.Range(0, meshStations.Length).Sum(node => residual[2 * node] * meshStations[node] + residual[2 * node + 1] + f[2 * node] * meshStations[node] + f[2 * node + 1]);
        var freeForceResidual = free.Where(index => index % 2 == 0).Select(index => Math.Abs(residual[index])).DefaultIfEmpty().Max();
        var freeMomentResidual = free.Where(index => index % 2 == 1).Select(index => Math.Abs(residual[index])).DefaultIfEmpty().Max();
        return new(reactions, stations, globalForce, globalMoment, freeForceResidual, freeMomentResidual);
    }
    private static AnalysisElementMapping Element(BeamTopology t, string id) => t.Elements.SingleOrDefault(e => e.ElementId == id) ?? throw new ArgumentException("Unknown analysis element: " + id);
    private static AnalysisElementMapping ElementAt(BeamTopology t, double station) => t.Elements.SingleOrDefault(e => station >= e.StartStationMm - 1e-8 && station <= e.EndStationMm + 1e-8) ?? throw new NotSupportedException("Every node must lie in a mapped element.");
    private static double[] Multiply(double[,] a, double[] x) => Enumerable.Range(0, x.Length).Select(i => Enumerable.Range(0, x.Length).Sum(j => a[i, j] * x[j])).ToArray();
    private static double[] Gaussian(double[][] a, double[] b)
    {
        for (var p = 0; p < b.Length; p++) { var max = Enumerable.Range(p, b.Length - p).MaxBy(i => Math.Abs(a[i][p])); if (Math.Abs(a[max][p]) < 1e-10) throw new InvalidOperationException("Singular stiffness matrix."); (a[p], a[max]) = (a[max], a[p]); (b[p], b[max]) = (b[max], b[p]); for (var i = p + 1; i < b.Length; i++) { var q = a[i][p] / a[p][p]; for (var j = p; j < b.Length; j++) a[i][j] -= q * a[p][j]; b[i] -= q * b[p]; } }
        var x = new double[b.Length]; for (var i = b.Length - 1; i >= 0; i--) x[i] = (b[i] - Enumerable.Range(i + 1, b.Length - i - 1).Sum(j => a[i][j] * x[j])) / a[i][i]; return x;
    }

    public static ResultEnvelope<BeamLineOutput> SolveBeamLine(BeamLineRequest request)
    {
        const string operation = "structural.beam_line.solve/v1";
        var inputs = ResultFactory.Effective(("request", request)); var provenance = new Provenance("structural-analysis-wp03-v1", "euler-bernoulli-direct-stiffness-wp03-v1", ["Euler-Bernoulli direct stiffness, N/mm internal units"]);
        try
        {
            if (string.IsNullOrWhiteSpace(request.ModelId) || string.IsNullOrWhiteSpace(request.LoadCaseId) || request.Nodes.Count is < 2 or > 20 || request.Elements.Count != request.Nodes.Count - 1 || request.StationIntervals is < 2 or > 100 || request.UnitBasis != "mm_n_nmm_rad" || request.SolverIdentity != "euler_bernoulli_direct_stiffness_v1") throw new ArgumentException("PROFILE.UNSUPPORTED");
            if (request.Nodes.Any(n => string.IsNullOrWhiteSpace(n.NodeId) || !double.IsFinite(n.XMm) || !double.IsFinite(n.VerticalDisplacementMm) || !double.IsFinite(n.PrescribedRotationRad) || !double.IsFinite(n.NodalForceN) || !double.IsFinite(n.NodalMomentNmm) || !n.VerticalRestraint && n.VerticalDisplacementMm != 0 || !n.RotationRestraint && n.PrescribedRotationRad != 0) || request.Nodes.Select(n => n.NodeId).Distinct(StringComparer.Ordinal).Count() != request.Nodes.Count || request.Nodes.Zip(request.Nodes.Skip(1)).Any(x => x.Second.XMm <= x.First.XMm)) throw new ArgumentException("PROFILE.UNSUPPORTED");
            if (request.Elements.Any(e => string.IsNullOrWhiteSpace(e.AnalysisElementId) || string.IsNullOrWhiteSpace(e.PhysicalSpanId) || !double.IsFinite(e.ElasticModulusNPerMm2) || e.ElasticModulusNPerMm2 <= 0 || !double.IsFinite(e.SecondMomentMm4) || e.SecondMomentMm4 <= 0 || !double.IsFinite(e.UniformLoadNPerMm)) || request.Elements.Select(e => e.AnalysisElementId).Distinct(StringComparer.Ordinal).Count() != request.Elements.Count) throw new ArgumentException("PROFILE.UNSUPPORTED");
            for (var i = 0; i < request.Elements.Count; i++) if (request.Elements[i].StartNodeId != request.Nodes[i].NodeId || request.Elements[i].EndNodeId != request.Nodes[i + 1].NodeId) throw new ArgumentException("PROFILE.UNSUPPORTED");
            var regions = request.Elements.Select(e => new SectionRegion(e.AnalysisElementId, e.PhysicalSpanId, request.Nodes.Single(n => n.NodeId == e.StartNodeId).XMm, request.Nodes.Single(n => n.NodeId == e.EndNodeId).XMm, e.ElasticModulusNPerMm2, e.SecondMomentMm4)).ToArray();
            var topology = new BeamTopology([], request.Elements.Select(e => new AnalysisElementMapping(e.AnalysisElementId, e.PhysicalSpanId, e.AnalysisElementId, request.Nodes.Single(n => n.NodeId == e.StartNodeId).XMm, request.Nodes.Single(n => n.NodeId == e.EndNodeId).XMm)).ToArray(), [], regions);
            var meshNodes = request.Nodes.Select(n => new PlanarNode(n.NodeId, n.XMm, n.VerticalRestraint, n.RotationRestraint, n.VerticalDisplacementMm, n.PrescribedRotationRad)).ToList();
            foreach (var element in request.Elements)
            {
                var a = request.Nodes.Single(n => n.NodeId == element.StartNodeId).XMm; var b = request.Nodes.Single(n => n.NodeId == element.EndNodeId).XMm;
                for (var interval = 1; interval < request.StationIntervals; interval++) meshNodes.Add(new PlanarNode($"{element.AnalysisElementId}:station:{interval}", a + (b - a) * interval / request.StationIntervals));
            }
            foreach (var point in request.PointLoads ?? [])
            {
                var element = request.Elements.Single(e => e.AnalysisElementId == point.AnalysisElementId); var a = request.Nodes.Single(n => n.NodeId == element.StartNodeId).XMm;
                meshNodes.Add(new PlanarNode($"{point.AnalysisElementId}:point:{point.DistanceFromStartMm:R}", a + point.DistanceFromStartMm));
            }
            var uniqueNodes = meshNodes.GroupBy(n => n.StationMm).Select(g => g.First()).ToArray();
            var legacy = Solve(new(topology, uniqueNodes, request.Elements.Where(e => e.UniformLoadNPerMm != 0).Select(e => new UniformLoad(e.AnalysisElementId, e.UniformLoadNPerMm)).ToArray(), request.Nodes.Where(n => n.NodalForceN != 0 || n.NodalMomentNmm != 0).Select(n => new NodalLoad(n.NodeId, n.NodalForceN, n.NodalMomentNmm)).ToArray(), (request.PointLoads ?? []).Select(p => new PointLoad(p.AnalysisElementId, "point", p.DistanceFromStartMm, p.VerticalForceN)).ToArray()));
            var stations = new List<BeamLineStation>();
            foreach (var element in request.Elements)
            {
                var startNode = request.Nodes.Single(n => n.NodeId == element.StartNodeId); var endNode = request.Nodes.Single(n => n.NodeId == element.EndNodeId);
                var start = legacy.Stations.Single(s => Math.Abs(s.StationMm - startNode.XMm) < 1e-8); var end = legacy.Stations.Single(s => Math.Abs(s.StationMm - endNode.XMm) < 1e-8);
                var length = endNode.XMm - startNode.XMm; var ei = element.ElasticModulusNPerMm2 * element.SecondMomentMm4; var c = ei / (length * length * length);
                double[,] local = { { 12*c, 6*length*c, -12*c, 6*length*c }, { 6*length*c, 4*length*length*c, -6*length*c, 2*length*length*c }, { -12*c, -6*length*c, 12*c, -6*length*c }, { 6*length*c, 2*length*length*c, -6*length*c, 4*length*length*c } };
                var elementPoints = (request.PointLoads ?? []).Where(p => p.AnalysisElementId == element.AnalysisElementId).ToArray();
                var equivalent = new[] { element.UniformLoadNPerMm * length / 2, element.UniformLoadNPerMm * length * length / 12, element.UniformLoadNPerMm * length / 2, -element.UniformLoadNPerMm * length * length / 12 };
                foreach (var point in elementPoints)
                {
                    var ratio = point.DistanceFromStartMm / length;
                    var shape = new[] { 1 - 3 * ratio * ratio + 2 * ratio * ratio * ratio, length * (ratio - 2 * ratio * ratio + ratio * ratio * ratio), 3 * ratio * ratio - 2 * ratio * ratio * ratio, length * (-ratio * ratio + ratio * ratio * ratio) };
                    for (var i = 0; i < 4; i++) equivalent[i] += point.VerticalForceN * shape[i];
                }
                var endDisplacements = new[] { start.V2DisplacementMm, start.RotationRad, end.V2DisplacementMm, end.RotationRad };
                var endActions = Enumerable.Range(0, 4).Select(i => Enumerable.Range(0, 4).Sum(j => local[i, j] * endDisplacements[j]) - equivalent[i]).ToArray();
                var positions = Enumerable.Range(0, request.StationIntervals + 1).Select(i => length * i / request.StationIntervals).Concat(elementPoints.Select(p => p.DistanceFromStartMm)).Distinct().Order().ToArray();
                foreach (var x in positions)
                {
                    var moment = -endActions[1] + endActions[0] * x + element.UniformLoadNPerMm * x * x / 2;
                    var rotation = start.RotationRad + (-endActions[1] * x + endActions[0] * x * x / 2 + element.UniformLoadNPerMm * x * x * x / 6) / ei;
                    var vertical = start.V2DisplacementMm + start.RotationRad * x + (-endActions[1] * x * x / 2 + endActions[0] * x * x * x / 6 + element.UniformLoadNPerMm * x * x * x * x / 24) / ei;
                    var shear = endActions[0] + element.UniformLoadNPerMm * x;
                    foreach (var point in elementPoints)
                    {
                        var delta = Math.Max(0, x - point.DistanceFromStartMm); moment += point.VerticalForceN * delta; rotation += point.VerticalForceN * delta * delta / (2 * ei); vertical += point.VerticalForceN * delta * delta * delta / (6 * ei);
                        if (point.DistanceFromStartMm < x) shear += point.VerticalForceN;
                    }
                    var atPoints = elementPoints.Where(p => p.DistanceFromStartMm == x).ToArray();
                    if (atPoints.Length == 0) stations.Add(new(element.PhysicalSpanId, element.AnalysisElementId, x, startNode.XMm + x, "continuous", vertical, rotation, shear, moment));
                    else
                    {
                        stations.Add(new(element.PhysicalSpanId, element.AnalysisElementId, x, startNode.XMm + x, "left", vertical, rotation, shear, moment));
                        stations.Add(new(element.PhysicalSpanId, element.AnalysisElementId, x, startNode.XMm + x, "right", vertical, rotation, shear + atPoints.Sum(p => p.VerticalForceN), moment));
                    }
                }
            }
            if (Math.Abs(legacy.GlobalForceResidualN) > 1e-5 || Math.Abs(legacy.GlobalMomentResidualNmm) > 1e-2 || legacy.MaxFreeForceResidualN > 1e-5 || legacy.MaxFreeMomentResidualNmm > 1e-2) throw new InvalidOperationException("ANALYSIS.EQUILIBRIUM");
            return ResultFactory.Completed(operation, inputs, new BeamLineOutput(request.SolverIdentity, "bounded_planar_major_axis", request.UnitBasis, legacy.GlobalForceResidualN, legacy.GlobalMomentResidualNmm, legacy.MaxFreeForceResidualN, legacy.MaxFreeMomentResidualNmm, legacy.Reactions, stations), provenance, EngineeringState.NotEvaluated);
        }
        catch (Exception e) when (e is ArgumentException or InvalidOperationException or NotSupportedException) { var code = e.Message.Contains("unstable", StringComparison.OrdinalIgnoreCase) ? "ANALYSIS.UNSTABLE" : e.Message.Contains("EQUILIBRIUM", StringComparison.Ordinal) ? "ANALYSIS.EQUILIBRIUM" : "PROFILE.UNSUPPORTED"; return ResultFactory.Rejected<BeamLineOutput>(operation, inputs, provenance, new Diagnostic(code, "error", e.Message, operation, "request", "structural-analysis")); }
    }
}
