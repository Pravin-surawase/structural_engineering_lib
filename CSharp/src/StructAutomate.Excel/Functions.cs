using ExcelDna.Integration;
using StructAutomate.Contracts;
using StructAutomate.Engineering;

namespace StructAutomate.Excel;

public static class Functions
{
    [ExcelFunction(Name = "SA.VERSION", Description = "StructAutomate foundation and contract version.", IsThreadSafe = true)]
    public static string Version() => "StructAutomate 0.1.0; contract " + ContractJson.SchemaVersion;

    [ExcelFunction(Name = "SA.BAR.MASS", Description = "Steel mass in kg from diameter mm, cut length mm, count and density kg/m³.", IsThreadSafe = true)]
    public static object BarMass(object diameterMm, object cutLengthMm, object count, object densityKgPerM3)
    {
        return Run(() =>
        {
            var n = Number(count, "count");
            Require.That(n >= 1 && n <= int.MaxValue && n == Math.Truncate(n), "count", "Enter a positive whole bar count.");
            var result = QuantityCalculator.Calculate(new(ContractJson.SchemaVersion, Number(densityKgPerM3, "densityKgPerM3"),
                [new("B1", Number(diameterMm, "diameterMm"), (int)n, [new("resolved cut length", Number(cutLengthMm, "cutLengthMm"))], [])], [], []));
            return result.SteelMassKg;
        });
    }

    [ExcelFunction(Name = "SA.REBAR.GEOMETRY", Description = "Tension-group bars only: diameter, x from left, y from top (mm). Returns group area, centroid, depth and geometric fit.", IsThreadSafe = true)]
    public static object RebarGeometry(object widthMm, object depthMm, object coverMm, object linkDiameterMm,
        object minClearSpacingMm, string tensionFace, object[,] bars)
    {
        return Run(() =>
        {
            Require.That(bars.GetLength(1) == 3 && bars.GetLength(0) > 0, "bars", "Use three numeric columns: diameter, x, y in mm.");
            Require.That(string.Equals(tensionFace, "top", StringComparison.OrdinalIgnoreCase) || string.Equals(tensionFace, "bottom", StringComparison.OrdinalIgnoreCase), "tensionFace", "Enter top or bottom.");
            var positions = new List<BarPosition>();
            for (int i = 0; i < bars.GetLength(0); i++)
            {
                for (int j = 0; j < 3; j++) Require.That(bars[i, j] is double v && double.IsFinite(v), $"bars[{i + 1},{j + 1}]", "Enter a finite number; blank cells are not zero.");
                positions.Add(new($"B{i+1}", $"L{i+1}", (double)bars[i,0], (double)bars[i,1], (double)bars[i,2]));
            }
            var face = string.Equals(tensionFace, "top", StringComparison.OrdinalIgnoreCase) ? TensionFace.Top : TensionFace.Bottom;
            var result = ReinforcementGeometry.Evaluate(new(ContractJson.SchemaVersion, Number(widthMm,"widthMm"), Number(depthMm,"depthMm"), Number(coverMm,"coverMm"), Number(linkDiameterMm,"linkDiameterMm"), Number(minClearSpacingMm,"minClearSpacingMm"), face, positions));
            return new object[,] {
                { "Area (mm²)", result.AreaMm2 }, { "Centroid x (mm)", result.CentroidXFromLeftMm },
                { "Centroid y (mm)", result.CentroidYFromTopMm }, { "Effective depth (mm)", result.EffectiveDepthMm },
                { "Fits", result.Fits }, { "Fit details", string.Join("; ", result.FitProblems.Select(p => p.Message)) }
            };
        });
    }

    [ExcelFunction(Name = "SA.BEAM.SS.UDL", Description = "Linear simply-supported beam. Inputs L mm, q kN/m, E MPa, I mm⁴. No self-weight is added.", IsThreadSafe = true)]
    public static object SimplySupportedUdl(object lengthMm, object uniformLoadKnPerM, object elasticModulusMpa, object secondMomentMm4)
    {
        return Run(() =>
        {
            var length = Number(lengthMm,"lengthMm");
            Require.Positive(length, "lengthMm");
            var result = BeamLineSolver.Solve(new(ContractJson.SchemaVersion,
                [new("A", 0, 0), new("B", length, 0)],
                [new("AB", "A", "B", Number(elasticModulusMpa,"elasticModulusMpa"), Number(secondMomentMm4,"secondMomentMm4"), Number(uniformLoadKnPerM,"uniformLoadKnPerM"), [length/2])]));
            var mid = result.Stations.Single(s => s.FromStartMm == length / 2);
            return new object[,] {
                { "Left upward reaction (kN)", -result.Nodes[0].SupportForceKn },
                { "Right upward reaction (kN)", -result.Nodes[1].SupportForceKn },
                { "Midspan sagging moment (kNm)", mid.SaggingMomentKnM },
                { "Midspan downward deflection (mm)", mid.DisplacementMm }
            };
        });
    }

    private static double Number(object value, string path)
    {
        Require.That(value is double v && double.IsFinite(v), path, "Enter a finite number; blank cells are not zero.");
        return (double)value;
    }

    private static object Run(Func<object> operation)
    {
        try { return operation(); }
        catch (InputValidationException ex) { return new object[,] { { "Input error", ex.Message } }; }
        catch (ArgumentException ex) { return new object[,] { { "Input error", ex.Message } }; }
    }
}
