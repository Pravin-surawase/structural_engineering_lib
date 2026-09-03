using StructAutomate.Contracts;

namespace StructAutomate.Engineering;

public static class ReinforcementGeometry
{
    public static ReinforcementGeometryResult Evaluate(ReinforcementGeometryRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        Require.Version(request.SchemaVersion);
        Require.Positive(request.WidthMm, "widthMm");
        Require.Positive(request.DepthMm, "depthMm");
        Require.Nonnegative(request.NominalCoverMm, "nominalCoverMm");
        Require.Nonnegative(request.LinkDiameterMm, "linkDiameterMm");
        Require.Nonnegative(request.MinimumClearSpacingMm, "minimumClearSpacingMm");
        Require.That(Enum.IsDefined(request.TensionFace), "tensionFace", "Select top or bottom.");
        ArgumentNullException.ThrowIfNull(request.TensionBars);
        Require.That(request.TensionBars.Count > 0, "tensionBars", "Provide the actual bars in the tension group.");
        Require.Unique(request.TensionBars.Select(b => b.Id), "tensionBars.id");
        var problems = new List<InputProblem>();
        double area = 0, weightedX = 0, weightedY = 0;
        double? minimum = null;
        var inset = request.NominalCoverMm + request.LinkDiameterMm;
        for (int i = 0; i < request.TensionBars.Count; i++)
        {
            var bar = request.TensionBars[i];
            var path = $"tensionBars[{i}]";
            Require.Text(bar.LayerId, path + ".layerId");
            Require.Positive(bar.DiameterMm, path + ".diameterMm");
            Require.Finite(bar.XFromLeftMm, path + ".xFromLeftMm");
            Require.Finite(bar.YFromTopMm, path + ".yFromTopMm");
            double r = bar.DiameterMm / 2;
            if (bar.XFromLeftMm - r < inset || bar.XFromLeftMm + r > request.WidthMm - inset ||
                bar.YFromTopMm - r < inset || bar.YFromTopMm + r > request.DepthMm - inset)
                problems.Add(new("bar_cover", path, "Bar crosses the clear rectangle inside cover and links."));
            double a = Math.PI * r * r;
            area += a;
            weightedX += a * bar.XFromLeftMm;
            weightedY += a * bar.YFromTopMm;
            for (int j = 0; j < i; j++)
            {
                var other = request.TensionBars[j];
                double dx = bar.XFromLeftMm - other.XFromLeftMm;
                double dy = bar.YFromTopMm - other.YFromTopMm;
                double gap = Math.Sqrt(dx * dx + dy * dy) - (bar.DiameterMm + other.DiameterMm) / 2;
                minimum = minimum is null ? gap : Math.Min(minimum.Value, gap);
                if (gap < request.MinimumClearSpacingMm)
                    problems.Add(new("bar_spacing", path, $"Clear gap to {other.Id} is {gap:G8} mm; required {request.MinimumClearSpacingMm:G8} mm."));
            }
        }
        var centroidY = weightedY / area;
        var depth = request.TensionFace == TensionFace.Bottom ? centroidY : request.DepthMm - centroidY;
        return new(area, weightedX / area, centroidY, depth, minimum, problems.ToArray());
    }
}
