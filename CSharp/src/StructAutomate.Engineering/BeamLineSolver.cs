using MathNet.Numerics.LinearAlgebra;
using StructAutomate.Contracts;

namespace StructAutomate.Engineering;

public static class BeamLineSolver
{
    private sealed record ElementAssembly(BeamElement Element, int StartIndex, double Length, double Ei,
        Matrix<double> Stiffness, Vector<double> Load);

    public static BeamLineResult Solve(BeamLineRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        Require.Version(request.SchemaVersion);
        ArgumentNullException.ThrowIfNull(request.Nodes);
        ArgumentNullException.ThrowIfNull(request.Elements);
        Require.That(request.Nodes.Count is >= 2 and <= 201, "nodes", "Use 2 to 201 ordered nodes for this planar beam-line solver.");
        Require.That(request.Elements.Count == request.Nodes.Count - 1, "elements", "Connect every adjacent node with exactly one element.");
        Require.Unique(request.Nodes.Select(n => n.Id), "nodes.id");
        Require.Unique(request.Elements.Select(e => e.Id), "elements.id");
        var nodes = request.Nodes;
        int size = nodes.Count * 2;
        var stiffness = Matrix<double>.Build.Dense(size, size);
        var force = Vector<double>.Build.Dense(size);
        var displacement = Vector<double>.Build.Dense(size);
        var fixedDof = new bool[size];
        var spring = new double[size];
        var verticalRestraints = new List<double>();
        bool rotationRestrained = false;
        for (int i = 0; i < nodes.Count; i++)
        {
            var node = nodes[i]; var path = $"nodes[{i}]";
            Require.Finite(node.XMm, path + ".xMm");
            if (i > 0) Require.That(node.XMm > nodes[i - 1].XMm, path + ".xMm", "Node positions must increase from left to right.");
            Require.Nonnegative(node.VerticalSpringNPerMm, path + ".verticalSpringNPerMm");
            Require.Nonnegative(node.RotationalSpringNmmPerRad, path + ".rotationalSpringNmmPerRad");
            Require.Finite(node.ForceKn, path + ".forceKn");
            Require.Finite(node.MomentKnM, path + ".momentKnM");
            if (node.PrescribedDisplacementMm is double w)
            {
                Require.Finite(w, path + ".prescribedDisplacementMm");
                fixedDof[2 * i] = true; displacement[2 * i] = w;
            }
            if (node.PrescribedRotationRad is double r)
            {
                Require.Finite(r, path + ".prescribedRotationRad");
                fixedDof[2 * i + 1] = true; displacement[2 * i + 1] = r;
            }
            spring[2 * i] = node.VerticalSpringNPerMm;
            spring[2 * i + 1] = node.RotationalSpringNmmPerRad;
            if (fixedDof[2 * i] || spring[2 * i] > 0) verticalRestraints.Add(node.XMm);
            rotationRestrained |= fixedDof[2 * i + 1] || spring[2 * i + 1] > 0;
            force[2 * i] = node.ForceKn * 1000;
            force[2 * i + 1] = node.MomentKnM * 1e6;
        }
        Require.That(verticalRestraints.Count >= 2 || (verticalRestraints.Count >= 1 && rotationRestrained), "nodes", "Restrain rigid translation and rotation using supports or springs.", "unstable_beam");
        var assembly = new List<ElementAssembly>();
        Require.Unique(request.Elements.Select(e => e.StartNodeId), "elements.startNodeId");
        var byStart = request.Elements.ToDictionary(e => e.StartNodeId, StringComparer.Ordinal);
        Require.That(byStart.Count == request.Elements.Count, "elements", "Each interval needs one element.");
        for (int i = 0; i < nodes.Count - 1; i++)
        {
            Require.That(byStart.TryGetValue(nodes[i].Id, out var e) && e.EndNodeId == nodes[i + 1].Id, "elements", "Elements must connect adjacent ordered nodes.");
            var element = e!; var path = $"elements.{element.Id}";
            Require.Positive(element.ElasticModulusMpa, path + ".elasticModulusMpa");
            Require.Positive(element.SecondMomentMm4, path + ".secondMomentMm4");
            Require.Finite(element.UniformLoadKnPerM, path + ".uniformLoadKnPerM");
            ArgumentNullException.ThrowIfNull(element.StationsFromStartMm);
            var length = nodes[i + 1].XMm - nodes[i].XMm;
            Require.Positive(length, path + ".lengthMm");
            foreach (var x in element.StationsFromStartMm)
                Require.That(double.IsFinite(x) && x >= 0 && x <= length, path + ".stationsFromStartMm", "Station lies outside its element.");
            Require.That(element.StationsFromStartMm.Distinct().Count() == element.StationsFromStartMm.Count, path + ".stationsFromStartMm", "Stations must be unique.");
            var ei = element.ElasticModulusMpa * element.SecondMomentMm4;
            Require.Positive(ei, path + ".ei");
            double l = length, l2 = l * l;
            var k = Matrix<double>.Build.DenseOfArray(new[,] {
                { 12d, 6*l, -12d, 6*l }, { 6*l, 4*l2, -6*l, 2*l2 },
                { -12d, -6*l, 12d, -6*l }, { 6*l, 2*l2, -6*l, 4*l2 }
            }) * (ei / (l2 * l));
            // 1 kN/m = 1 N/mm; consistent nodal loads use the same downward sign.
            double q = element.UniformLoadKnPerM;
            var f = Vector<double>.Build.DenseOfArray([q*l/2, q*l2/12, q*l/2, -q*l2/12]);
            for (int a = 0; a < 4; a++)
            {
                force[2 * i + a] += f[a];
                for (int b = 0; b < 4; b++) stiffness[2 * i + a, 2 * i + b] += k[a, b];
            }
            assembly.Add(new(element, i, l, ei, k, f));
        }
        for (int i = 0; i < size; i++) stiffness[i, i] += spring[i];
        var free = Enumerable.Range(0, size).Where(i => !fixedDof[i]).ToArray();
        var fixedIndices = Enumerable.Range(0, size).Where(i => fixedDof[i]).ToArray();
        if (free.Length > 0)
        {
            var reduced = Matrix<double>.Build.Dense(free.Length, free.Length, (i, j) => stiffness[free[i], free[j]]);
            var rhs = Vector<double>.Build.Dense(free.Length, i => force[free[i]] - fixedIndices.Sum(j => stiffness[free[i], j] * displacement[j]));
            // Diagonal scaling avoids mixing millimetre and radian stiffness magnitudes.
            var scale = Vector<double>.Build.Dense(free.Length, i => 1 / Math.Sqrt(reduced[i, i]));
            var scaled = Matrix<double>.Build.Dense(free.Length, free.Length, (i, j) => reduced[i, j] * scale[i] * scale[j]);
            Vector<double> solution;
            try { solution = scaled.Cholesky().Solve(rhs.PointwiseMultiply(scale)).PointwiseMultiply(scale); }
            catch (ArgumentException) { throw new InputValidationException(new InputProblem("unstable_beam", "nodes", "Review supports and stiffness; the beam matrix could not be solved.")); }
            for (int i = 0; i < free.Length; i++)
            {
                Require.Finite(solution[i], "solution");
                displacement[free[i]] = solution[i];
            }
        }
        var residual = stiffness * displacement - force;
        var responses = new List<NodeResponse>();
        for (int i = 0; i < nodes.Count; i++)
        {
            // All support actions include spring forces; prescribed support reactions add residual.
            double reaction = (fixedDof[2 * i] ? residual[2 * i] : 0) - spring[2 * i] * displacement[2 * i];
            double momentReaction = (fixedDof[2 * i + 1] ? residual[2 * i + 1] : 0) - spring[2 * i + 1] * displacement[2 * i + 1];
            responses.Add(new(nodes[i].Id, displacement[2 * i], displacement[2 * i + 1], reaction / 1000, momentReaction / 1e6));
        }
        var stations = new List<StationResponse>();
        foreach (var item in assembly)
        {
            var d = displacement.SubVector(2 * item.StartIndex, 4);
            var endForce = item.Stiffness * d - item.Load;
            double l = item.Length, q = item.Element.UniformLoadKnPerM;
            var points = item.Element.StationsFromStartMm.Append(0).Append(l).ToHashSet();
            if (q != 0)
            {
                var zeroShear = -endForce[0] / q;
                if (zeroShear > 0 && zeroShear < l) points.Add(zeroShear);
            }
            foreach (var x in points.Order())
            {
                var s = x / l;
                var w = (1 - 3*s*s + 2*s*s*s) * d[0] + l*(s - 2*s*s + s*s*s) * d[1]
                    + (3*s*s - 2*s*s*s) * d[2] + l*(-s*s + s*s*s) * d[3]
                    + q * x*x * (l-x)*(l-x) / (24 * item.Ei);
                // The quartic UDL term restores exact interior deflection for a prismatic element.
                stations.Add(new(item.Element.Id, x, nodes[item.StartIndex].XMm + x,
                    (-endForce[0] - q*x) / 1000, (endForce[1] - endForce[0]*x - q*x*x/2) / 1e6, w));
            }
        }
        double origin = nodes[0].XMm;
        double forceResidual = responses.Sum(n => n.SupportForceKn) + nodes.Sum(n => n.ForceKn)
            + assembly.Sum(e => e.Element.UniformLoadKnPerM * e.Length / 1000);
        double momentResidual = responses.Select((r, i) => r.SupportForceKn * (nodes[i].XMm - origin) / 1000 + r.SupportMomentKnM).Sum()
            + nodes.Sum(n => n.ForceKn * (n.XMm - origin) / 1000 + n.MomentKnM)
            + assembly.Sum(e => e.Element.UniformLoadKnPerM * e.Length / 1000 * (nodes[e.StartIndex].XMm + e.Length / 2 - origin) / 1000);
        Require.That(Math.Abs(forceResidual) <= 1e-7 * Math.Max(1, force.L1Norm() / 1000) && Math.Abs(momentResidual) <= 1e-7 * Math.Max(1, force.L1Norm()), "solution", "Equilibrium residual exceeds numerical tolerance.", "numerical_resolution");
        return new(responses.ToArray(), stations.ToArray(), forceResidual, momentResidual);
    }
}
