namespace StructuralEngineering.Etabs;

public sealed record EtabsMemberCaptureSummary(
    string ObjectName, string Label, string Story, IReadOnlyList<string> PointNames,
    IReadOnlyList<string> ElementNames, string SectionName, string MaterialName, int FrameForceRows);

public static partial class EtabsLiveGetterProbe
{
    private sealed class SharedCaptureCache
    {
        public HashSet<string> Points { get; } = new(StringComparer.Ordinal);
        public HashSet<string> Materials { get; } = new(StringComparer.Ordinal);
        public HashSet<string> SourcePointNames { get; } = new(StringComparer.Ordinal);
        public HashSet<string> AnalysisPoints { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, string> MaterialBySection { get; } = new(StringComparer.Ordinal);
    }

    private static EtabsMemberCaptureSummary ReadMember(EtabsGetterAdapter adapter,
        EtabsLiveGetterProbeRequest request, List<EtabsRawGetterCall> calls,
        CancellationToken cancellationToken, SharedCaptureCache? cache = null)
    {
        var label = Call(adapter, request, calls, "FrameObj.GetLabelFromName", [request.MemberObjectName], cancellationToken);
        if (!string.IsNullOrEmpty(request.ExpectedMemberLabel)) RequireEqual("frame label", request.ExpectedMemberLabel, Scalar<string>(label, 0));
        RequireEqual("frame story", request.ExpectedStory, Scalar<string>(label, 1));

        var pointsCall = Call(adapter, request, calls, "FrameObj.GetPoints", [request.MemberObjectName], cancellationToken);
        var pointNames = new[] { Scalar<string>(pointsCall, 0), Scalar<string>(pointsCall, 1) };

        var sectionCall = Call(adapter, request, calls, "FrameObj.GetSection", [request.MemberObjectName], cancellationToken);
        var sectionName = Scalar<string>(sectionCall, 0);
        Call(adapter, request, calls, "FrameObj.GetModifiers", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetEndLengthOffset", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetInsertionPoint_1", [request.MemberObjectName], cancellationToken);
        Call(adapter, request, calls, "FrameObj.GetReleases", [request.MemberObjectName], cancellationToken);
        var frameAxes = Call(adapter, request, calls, "FrameObj.GetLocalAxes", [request.MemberObjectName], cancellationToken);
        if (Scalar<bool>(frameAxes, 1))
            throw new EtabsLiveGetterProbeException("Advanced frame local axes are outside the frozen WP10-02 definition.");

        var frameForce = Call(
            adapter,
            request,
            calls,
            "Results.FrameForce",
            [request.MemberObjectName, request.FrameItemTypeElm],
            cancellationToken);
        var frameForceRows = Scalar<int>(frameForce, 0);
        var resultObjects = Strings(frameForce, 1);
        var elementNames = Strings(frameForce, 3).Distinct(StringComparer.Ordinal).ToArray();
        if (frameForceRows == 0 || elementNames.Length == 0)
            throw new EtabsLiveGetterProbeException(
                "Results.FrameForce returned no object/element mapping rows for the explicit member and output selection.");
        if (resultObjects.Any(name => !string.Equals(name, request.MemberObjectName, StringComparison.Ordinal)))
            throw new EtabsLiveGetterProbeException(
                "Results.FrameForce returned a row owned by a different frame object.");
        var expectedResultCases = request.SelectedCases
            .Concat(request.SelectedCombinations)
            .Distinct(StringComparer.Ordinal)
            .Order(StringComparer.Ordinal)
            .ToArray();
        var actualResultCases = Strings(frameForce, 5)
            .Distinct(StringComparer.Ordinal)
            .Order(StringComparer.Ordinal)
            .ToArray();
        if (!actualResultCases.SequenceEqual(expectedResultCases, StringComparer.Ordinal))
            throw new EtabsLiveGetterProbeException(
                "Results.FrameForce load-case rows differ from the exact frozen output selection.");

        foreach (var pointName in pointNames.Distinct(StringComparer.Ordinal).Where(name => cache is null || cache.Points.Add(name)))
            ReadSourcePoint(adapter, request, calls, pointName, cancellationToken);

        var elementPoints = new List<(string Point1, string Point2)>();
        foreach (var elementName in elementNames)
        {
            var owner = Call(adapter, request, calls, "LineElm.GetObj", [elementName], cancellationToken);
            RequireEqual("analysis-element owner", request.MemberObjectName, Scalar<string>(owner, 0));
            var elementPointCall = Call(adapter, request, calls, "LineElm.GetPoints", [elementName], cancellationToken);
            elementPoints.Add((Scalar<string>(elementPointCall, 0), Scalar<string>(elementPointCall, 1)));
            Call(adapter, request, calls, "LineElm.GetLocalAxes", [elementName], cancellationToken);
            Call(adapter, request, calls, "LineElm.GetTransformationMatrix", [elementName], cancellationToken);
        }
        ValidateElementTopology(pointNames, elementPoints);
        if (cache is not null)
            foreach (var point in elementPoints.SelectMany(pair => new[] { pair.Point1, pair.Point2 }).Distinct(StringComparer.Ordinal))
            {
                if (cache.SourcePointNames.Contains(point))
                {
                    if (cache.Points.Add(point)) ReadSourcePoint(adapter, request, calls, point, cancellationToken);
                }
                else if (cache.AnalysisPoints.Add(point))
                    Call(adapter, request, calls, "PointElm.GetCoordCartesian", [point, "Global"], cancellationToken);
            }

        if (cache is null || !cache.MaterialBySection.ContainsKey(sectionName))
        {
            var materialCall = Call(adapter, request, calls, "PropFrame.GetMaterial", [sectionName], cancellationToken);
            var material = Scalar<string>(materialCall, 0);
            var rectangleCall = Call(adapter, request, calls, "PropFrame.GetRectangle", [sectionName], cancellationToken);
            RequireEqual("section material", material, Scalar<string>(rectangleCall, 1));
            Call(adapter, request, calls, "PropFrame.GetSectProps", [sectionName], cancellationToken);
            Call(adapter, request, calls, "PropFrame.GetModifiers", [sectionName], cancellationToken);
            if (cache is null || cache.Materials.Add(material))
            {
                Call(adapter, request, calls, "PropMaterial.GetMPIsotropic", [material, 0d], cancellationToken);
                Call(adapter, request, calls, "PropMaterial.GetWeightAndMass", [material, 0d], cancellationToken);
            }
            if (cache is not null) cache.MaterialBySection[sectionName] = material;
        }
        var materialName = cache is not null ? cache.MaterialBySection[sectionName]
            : Scalar<string>(calls.Last(call => call.Operation == "PropFrame.GetMaterial"), 0);
        return new(request.MemberObjectName, Scalar<string>(label, 0), Scalar<string>(label, 1), pointNames,
            elementNames, sectionName, materialName, frameForceRows);
    }

    private static void ReadSourcePoint(EtabsGetterAdapter adapter, EtabsLiveGetterProbeRequest request,
        List<EtabsRawGetterCall> calls, string pointName, CancellationToken cancellationToken)
    {
        Call(adapter, request, calls, "PointObj.GetCoordCartesian", [pointName, "Global"], cancellationToken);
        Call(adapter, request, calls, "PointObj.GetLabelFromName", [pointName], cancellationToken);
        Call(adapter, request, calls, "PointObj.GetRestraint", [pointName], cancellationToken);
        var axes = Call(adapter, request, calls, "PointObj.GetLocalAxes", [pointName], cancellationToken);
        if (Scalar<bool>(axes, 3)) throw new EtabsLiveGetterProbeException("Advanced point local axes are outside the qualified source policy.");
        Call(adapter, request, calls, "PointObj.GetTransformationMatrix", [pointName, true], cancellationToken);
    }
}
