using ExcelDna.Integration;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Reinforcement;

namespace StructuralEngineering.ExcelDna;

/// <summary>Compatibility names retained as pure projections over native operations.</summary>
public static class LegacyFunctions
{
    [ExcelFunction(Name = "SA.VERSION", Description = "StructAutomate foundation and contract version.", IsThreadSafe = true)]
    public static string Version() => "StructAutomate 0.1.0; contract structural-operation-result/v1";

    [ExcelFunction(Name = "SA.BAR.MASS", Description = "Steel mass in kg from diameter mm, cut length mm, count and density kg/m³.", IsThreadSafe = true)]
    public static object BarMass(object diameterMm, object cutLengthMm, object count, object densityKgPerM3)
    {
        return Run(() =>
        {
            var number = StrictJson.Number(count, "count");
            if (number < 1 || number > int.MaxValue || number != Math.Truncate(number))
                throw new WorksheetInputException("INPUT.RANGE", "count must be a positive whole bar count.");
            var unitMass = ReinforcementOperations.MassPerLength(new(
                "legacy_excel_compatibility",
                StrictJson.Number(diameterMm, "diameter_mm"),
                StrictJson.Number(densityKgPerM3, "density_kg_per_m3")));
            if (unitMass.Outputs is null)
                return ResultSpill.Diagnostic(unitMass.Diagnostics.FirstOrDefault()?.Code ?? "INPUT.INVALID",
                    unitMass.Diagnostics.FirstOrDefault()?.Message ?? "Mass-per-length request was rejected.");
            return unitMass.Outputs.Value * StrictJson.Number(cutLengthMm, "cut_length_mm") / 1000d * number;
        });
    }

    [ExcelFunction(Name = "SA.REBAR.GEOMETRY", Description = "Tension-group bars only: diameter, x from left, y from top (mm). Returns group area, centroid, depth and geometric fit.", IsThreadSafe = true)]
    public static object RebarGeometry(object widthMm, object depthMm, object coverMm, object linkDiameterMm,
        object minClearSpacingMm, string tensionFace, object[,] bars)
    {
        return Run(() =>
        {
            if (bars.GetLength(1) != 3 || bars.GetLength(0) == 0)
                throw new WorksheetInputException("INPUT.RANGE", "Use three numeric columns: diameter, x, y in mm.");
            var face = tensionFace?.ToLowerInvariant() switch
            {
                "top" => Face.Top,
                "bottom" => Face.Bottom,
                _ => throw new WorksheetInputException("INPUT.RANGE", "tensionFace must be top or bottom.")
            };
            var coordinates = new List<BarCoordinate>();
            for (var row = 0; row < bars.GetLength(0); row++)
            {
                coordinates.Add(new(
                    $"B{row + 1}",
                    StrictJson.Number(bars[row, 0], $"bars[{row + 1},1]"),
                    StrictJson.Number(bars[row, 1], $"bars[{row + 1},2]"),
                    StrictJson.Number(bars[row, 2], $"bars[{row + 1},3]"),
                    face));
            }
            var result = ReinforcementOperations.EvaluateGeometry(new(
                "legacy_excel_compatibility",
                StrictJson.Number(widthMm, "width_mm"),
                StrictJson.Number(depthMm, "depth_mm"),
                StrictJson.Number(coverMm, "cover_mm"),
                StrictJson.Number(linkDiameterMm, "link_diameter_mm"),
                StrictJson.Number(minClearSpacingMm, "minimum_clear_spacing_mm"),
                coordinates));
            if (result.Outputs is null || !result.Outputs.Faces.TryGetValue(tensionFace.ToLowerInvariant(), out var geometry))
                return ResultSpill.Diagnostic(result.Diagnostics.FirstOrDefault()?.Code ?? "INPUT.INVALID",
                    result.Diagnostics.FirstOrDefault()?.Message ?? "Reinforcement geometry request was rejected.");
            return new object[,]
            {
                { "Area (mm²)", geometry.AreaMm2 },
                { "Centroid x (mm)", geometry.CentroidXFromLeftMm },
                { "Centroid y (mm)", geometry.CentroidYFromTopMm },
                { "Effective depth (mm)", geometry.EffectiveDepthMm },
                { "Fits", result.Engineering == EngineeringState.Pass },
                { "Fit details", string.Join("; ", result.Diagnostics.Select(diagnostic => diagnostic.Message)) }
            };
        });
    }

    [ExcelFunction(Name = "SA.BEAM.SS.UDL", Description = "Linear simply-supported beam. Inputs L mm, q kN/m, E MPa, I mm⁴. No self-weight is added.", IsThreadSafe = true)]
    public static object SimplySupportedUdl(object lengthMm, object uniformLoadKnPerM, object elasticModulusMpa, object secondMomentMm4)
    {
        return Run(() =>
        {
            var length = StrictJson.Number(lengthMm, "length_mm");
            if (length <= 0)
                throw new WorksheetInputException("INPUT.RANGE", "length_mm must be greater than zero.");
            var result = PlanarBeamSolver.SolveBeamLine(new(
                "legacy_excel_compatibility",
                "legacy_udl",
                [new("A", 0, true, false), new("B", length, true, false)],
                [new("AB", "AB", "A", "B", StrictJson.Number(elasticModulusMpa, "elastic_modulus_mpa"),
                    StrictJson.Number(secondMomentMm4, "second_moment_mm4"),
                    StrictJson.Number(uniformLoadKnPerM, "uniform_load_kn_per_m"))],
                StationIntervals: 2));
            if (result.Outputs is null)
                return ResultSpill.Diagnostic(result.Diagnostics.FirstOrDefault()?.Code ?? "INPUT.INVALID",
                    result.Diagnostics.FirstOrDefault()?.Message ?? "Beam-line request was rejected.");
            var midspan = result.Outputs.Stations.Single(station => Math.Abs(station.XMm - length / 2d) < 1e-9);
            return new object[,]
            {
                { "Left upward reaction (kN)", -result.Outputs.Reactions[0].V2N / 1000d },
                { "Right upward reaction (kN)", -result.Outputs.Reactions[1].V2N / 1000d },
                { "Midspan sagging moment (kNm)", midspan.M3Nmm / 1_000_000d },
                { "Midspan downward deflection (mm)", midspan.VerticalDisplacementMm }
            };
        });
    }

    private static object Run(Func<object> operation)
    {
        try
        {
            return operation();
        }
        catch (WorksheetInputException exception)
        {
            return new object[,] { { "Input error", exception.Message } };
        }
        catch (ArgumentException exception)
        {
            return new object[,] { { "Input error", exception.Message } };
        }
    }
}
