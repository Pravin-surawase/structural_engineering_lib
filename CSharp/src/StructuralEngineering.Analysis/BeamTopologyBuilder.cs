using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Analysis;

public static class BeamTopologyBuilder
{
    public static ResultEnvelope<BeamTopologyDefinitionOutput> Define(BeamTopologyDefinitionRequest request)
    {
        const string operation = "structural.beam_topology.define/v1";
        var inputs = ResultFactory.Effective(("request", request)); var provenance = new Provenance("structural-analysis-wp03-v1", "beam-topology-wp03-v1", ["support face and analysis-element topology"]);
        try
        {
            if (string.IsNullOrWhiteSpace(request.MemberId) || request.Supports.Count < 2 || request.Spans.Count != request.Supports.Count - 1) throw new ArgumentException("Member, ordered supports, and one span per support pair are required.");
            if (string.IsNullOrWhiteSpace(request.LocalAxes.AxisId)) throw new ArgumentException("Local axis identity is required.");
            ActionNormalizer.ValidateAxes(new(request.LocalAxes.E1.X, request.LocalAxes.E1.Y, request.LocalAxes.E1.Z, request.LocalAxes.E2.X, request.LocalAxes.E2.Y, request.LocalAxes.E2.Z, request.LocalAxes.E3.X, request.LocalAxes.E3.Y, request.LocalAxes.E3.Z));
            if (request.Supports.Select(x => x.SupportId).Distinct().Count() != request.Supports.Count || request.Spans.Select(x => x.SpanId).Distinct().Count() != request.Spans.Count || request.Supports.Zip(request.Supports.Skip(1)).Any(x => x.Second.CentreMm <= x.First.CentreMm)) throw new ArgumentException("Support identities must be unique and centres ordered.");
            foreach (var support in request.Supports) if (string.IsNullOrWhiteSpace(support.SupportId) || !double.IsFinite(support.LeftFaceMm) || !double.IsFinite(support.CentreMm) || !double.IsFinite(support.RightFaceMm) || !(support.LeftFaceMm < support.CentreMm && support.CentreMm < support.RightFaceMm)) throw new ArgumentException("Each support requires an identity and ordered finite left-face, centre, and right-face stations.");
            var spanIds = request.Spans.Select(span => span.SpanId).ToHashSet(StringComparer.Ordinal);
            if (request.AnalysisElements.Any(element => !spanIds.Contains(element.PhysicalSpanId) || string.IsNullOrWhiteSpace(element.AnalysisElementId)) || request.AnalysisElements.Select(element => element.AnalysisElementId).Distinct(StringComparer.Ordinal).Count() != request.AnalysisElements.Count) throw new ArgumentException("Analysis-element identities must be unique and reference a declared span.");
            var regions = request.Spans.SelectMany(span => span.SectionRegions).ToArray();
            if (regions.Any(region => string.IsNullOrWhiteSpace(region.RegionId) || string.IsNullOrWhiteSpace(region.SectionId)) || regions.Select(region => region.RegionId).Distinct(StringComparer.Ordinal).Count() != regions.Length) throw new ArgumentException("Section-region identities must be complete and unique.");
            var output = new List<DefinedPhysicalSpan>();
            for (var i = 0; i < request.Spans.Count; i++)
            {
                var span = request.Spans[i]; var a = request.Supports[i]; var b = request.Supports[i + 1];
                if (span.StartSupportId != a.SupportId || span.EndSupportId != b.SupportId || span.EffectiveDepthMm <= 0 || !double.IsFinite(span.EffectiveDepthMm)) throw new ArgumentException("Each span must join its adjacent supports and specify effective depth.");
                var centre = b.CentreMm - a.CentreMm; var clear = b.LeftFaceMm - a.RightFaceMm; if (clear <= 0) throw new ArgumentException("Support faces leave no clear span.");
                var elements = request.AnalysisElements.Where(e => e.PhysicalSpanId == span.SpanId).OrderBy(e => e.StartMm).ToArray();
                ValidateCoverage(span.SectionRegions.OrderBy(r => r.StartMm).Select(r => (r.StartMm, r.EndMm)).ToArray(), a.CentreMm, b.CentreMm, "section regions");
                ValidateCoverage(elements.Select(e => (e.StartMm, e.EndMm)).ToArray(), a.CentreMm, b.CentreMm, "analysis mappings");
                output.Add(new(span.SpanId, a.SupportId, b.SupportId, a.RightFaceMm, b.LeftFaceMm, centre, clear, Math.Min(centre, clear + span.EffectiveDepthMm), span.SectionRegions, elements));
            }
            var identity = new { request.MemberId, request.LocalAxes, request.Supports, request.Spans, request.AnalysisElements };
            return ResultFactory.Completed(operation, inputs, new BeamTopologyDefinitionOutput(ResultFactory.NormalizedInputId(identity).Replace("normalized_input_id", "beam_topology_id"), request.MemberId, request.LocalAxes, request.Supports, output), provenance);
        }
        catch (ArgumentException e) { var code = e.Message.Contains("cover", StringComparison.OrdinalIgnoreCase) ? "REGION.COVERAGE" : "TOPOLOGY.INVALID"; return ResultFactory.Rejected<BeamTopologyDefinitionOutput>(operation, inputs, provenance, new Diagnostic(code, "error", e.Message, operation, "request", "structural-analysis")); }
    }

    private static void ValidateCoverage((double Start, double End)[] values, double start, double end, string label)
    {
        const double tolerance = 1e-6;
        if (values.Length == 0 || values.Any(x => !double.IsFinite(x.Start) || !double.IsFinite(x.End) || x.End <= x.Start) || Math.Abs(values[0].Start - start) > tolerance || Math.Abs(values[^1].End - end) > tolerance || values.Zip(values.Skip(1)).Any(x => Math.Abs(x.First.End - x.Second.Start) > tolerance)) throw new ArgumentException($"{label} must cover the centreline span exactly without gaps or overlaps.");
    }
    public static BeamTopology Build(BeamTopologyRequest request)
    {
        if (request.SupportFaces is null || request.SupportFaces.Count < 2) throw new ArgumentException("At least two support faces are required.", nameof(request));
        var supports = request.SupportFaces.OrderBy(x => x.CentrelineStationMm).ToArray();
        if (supports.Any(x => string.IsNullOrWhiteSpace(x.SupportId) || !double.IsFinite(x.CentrelineStationMm) || !double.IsFinite(x.ClearFaceStationMm)) || supports.Select(x => x.SupportId).Distinct().Count() != supports.Length) throw new ArgumentException("Support identities and stations must be finite and unique.", nameof(request));
        var spans = new List<PhysicalSpan>();
        for (var i = 0; i < supports.Length - 1; i++)
        {
            var centre = supports[i + 1].CentrelineStationMm - supports[i].CentrelineStationMm;
            var clear = supports[i + 1].ClearFaceStationMm - supports[i].ClearFaceStationMm;
            if (centre <= 0 || clear <= 0 || clear > centre + 1e-9) throw new ArgumentException("Support faces must define ordered, non-overlapping physical spans.", nameof(request));
            if (!double.IsFinite(request.DesignEffectiveDepthMm) || request.DesignEffectiveDepthMm < 0) throw new ArgumentException("Design effective depth must be finite and nonnegative.", nameof(request));
            spans.Add(new($"span-{i + 1}", supports[i].SupportId, supports[i + 1].SupportId, centre, clear, Math.Min(centre, clear + request.DesignEffectiveDepthMm)));
        }
        var regions = request.SectionRegions ?? throw new ArgumentException("Section regions are required.", nameof(request));
        var elements = new List<AnalysisElementMapping>();
        foreach (var region in regions)
        {
            if (!spans.Any(s => s.SpanId == region.PhysicalSpanId) || string.IsNullOrWhiteSpace(region.RegionId) || region.EndStationMm <= region.StartStationMm || region.ElasticModulusNPerMm2 <= 0 || region.MajorAxisInertiaMm4 <= 0) throw new ArgumentException("Section regions must be positive and belong to a physical span.", nameof(request));
            elements.Add(new($"element-{elements.Count + 1}", region.PhysicalSpanId, region.RegionId, region.StartStationMm, region.EndStationMm));
        }
        return new(spans, elements, supports, regions);
    }
}
