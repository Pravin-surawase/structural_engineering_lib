using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

internal static class BaselineArrangements
{
    private sealed record FaceOption(double Diameter, int Count, int Layers, IReadOnlyList<BarCoordinate> Bars);

    public static IEnumerable<BaselineArrangement> Enumerate(BoundBaselineBeam beam)
    {
        var c = beam.Catalogue;
        foreach (var linkDiameter in c.LinkDiametersMm.Order())
        {
            var bottom = Faces(beam, linkDiameter, Face.Bottom).ToArray();
            var top = Faces(beam, linkDiameter, Face.Top).ToArray();
            foreach (var pair in (from b in bottom from t in top select (b, t))
                .OrderBy(p => p.b.Count * p.b.Diameter * p.b.Diameter + p.t.Count * p.t.Diameter * p.t.Diameter)
                .ThenBy(p => p.b.Count + p.t.Count).ThenBy(p => p.b.Diameter).ThenBy(p => p.t.Diameter)
                .ThenBy(p => p.b.Layers).ThenBy(p => p.t.Layers))
                foreach (var spacing in c.LinkSpacingsMm.OrderDescending())
                {
                    var bars = pair.b.Bars.Concat(pair.t.Bars).ToArray();
                    var link = new TransverseLink("link-full-span", linkDiameter, 2, 2, spacing,
                        beam.LinkSteelYieldStrengthNPerMm2, true,
                        beam.WidthMm - 2 * beam.Context.NominalCoverMm - linkDiameter,
                        beam.DepthMm - 2 * beam.Context.NominalCoverMm - linkDiameter);
                    var paths = bars.Select(bar => new LongitudinalBarPath(bar.BarId, bar.BarId,
                        bar.Face == Face.Bottom ? ReinforcementRole.BottomLongitudinal : ReinforcementRole.TopLongitudinal,
                        bar.DiameterMm, bar.Layer, bar.XFromLeftMm, bar.YFromTopMm,
                        beam.Context.AnchorageStartXMm, beam.Context.AnchorageEndXMm, .87 * beam.SteelYieldStrengthNPerMm2)).ToArray();
                    var revision = ResultFactory.SemanticId("reinforcement_revision", new { beam.EffectiveInputId, bars, paths, link });
                    yield return new(revision, bars, paths, link,
                        pair.b.Bars.Average(b => b.YFromTopMm), beam.DepthMm - pair.t.Bars.Average(b => b.YFromTopMm),
                        bars.Sum(b => Math.PI * b.DiameterMm * b.DiameterMm / 4), pair.b.Count, pair.t.Count,
                        pair.b.Diameter, pair.t.Diameter, pair.b.Layers, pair.t.Layers);
                }
        }
    }

    private static IEnumerable<FaceOption> Faces(BoundBaselineBeam beam, double link, Face face)
    {
        foreach (var diameter in beam.Catalogue.LongitudinalDiametersMm.Order())
            foreach (var count in beam.Catalogue.BarCounts.Order())
                foreach (var layers in beam.Catalogue.Layers.Order())
                {
                    // Frozen first-layout policy: equal, vertically aligned rows with at
                    // least two bars per row. Other count/layer pairs are outside this domain.
                    if (count % layers != 0 || count / layers < 2 || diameter > 4 * link) continue;
                    var perLayer = count / layers;
                    var edge = beam.Context.NominalCoverMm + 3 * link;
                    var stepX = (beam.WidthMm - 2 * edge) / (perLayer - 1);
                    var clear = Math.Max(diameter, beam.Context.MaximumAggregateSizeMm + 5);
                    if (stepX - diameter < clear) continue;
                    var ordinaryStep = diameter + Math.Max(15, Math.Max(diameter, 2 * beam.Context.MaximumAggregateSizeMm / 3));
                    var hookClearStep = 8.5 * link / Math.Sqrt(2) + (diameter + link) / 2;
                    var stepY = Math.Max(ordinaryStep, hookClearStep);
                    var deepest = edge + (layers - 1) * stepY;
                    if (deepest >= beam.DepthMm / 2) continue;
                    var bars = new List<BarCoordinate>();
                    for (var layer = 0; layer < layers; layer++)
                        for (var index = 0; index < perLayer; index++)
                        {
                            var fromFace = edge + layer * stepY;
                            bars.Add(new($"{face}-L{layer + 1}-B{index + 1}", diameter, edge + index * stepX,
                                face == Face.Bottom ? beam.DepthMm - fromFace : fromFace, face, layer + 1));
                        }
                    yield return new(diameter, count, layers, bars);
                }
    }
}
