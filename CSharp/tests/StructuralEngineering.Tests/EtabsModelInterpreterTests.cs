using System.Text.Json.Nodes;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class EtabsModelInterpreterTests
{
    [Fact]
    public void InterpretsEverySourceFrameAndExactSharedPointConnectivityWithoutInventingSpans()
    {
        var result = EtabsModelInterpreter.Interpret(new(Artifact()));

        Assert.Equal(["b1", "b2", "c1", "x1"], result.Frames.Select(item => item.SourceFrameId));
        Assert.Equal(["b1", "b2", "c1", "x1"], result.PointAdjacency.Single(item => item.SourcePointId == "p2").ConnectedFrameIds);
        var beam = result.Beams.Single(item => item.SourceBeamId == "b1");
        Assert.Equal(["b2"], beam.NeighbourBeamIds);
        Assert.Equal(["c1"], beam.ConnectedColumnIds);
        Assert.All(result.BeamReadiness, item => Assert.Equal(EtabsBeamReadinessDisposition.NeedsSupportFacesAndPhysicalSpanMapping, item.Disposition));
        Assert.All(result.BeamReadiness, item => Assert.Contains(item.MissingFacts, fact => fact.Contains("Physical-span", StringComparison.Ordinal)));
    }

    [Fact]
    public void BranchAtSamePointIsPreservedAndRequestedUnknownBeamIsVisible()
    {
        var result = EtabsModelInterpreter.Interpret(new(Artifact(), RequestedBeamIds: ["b1", "missing"]));

        Assert.Equal(["b2"], Assert.Single(result.Beams).NeighbourBeamIds);
        var missing = result.BeamReadiness.Single(item => item.SourceBeamId == "missing");
        Assert.Equal(EtabsBeamReadinessDisposition.RequestedBeamMissing, missing.Disposition);
    }

    [Fact]
    public void SourceConnectivityNeverBecomesAnAnalysisMeshOrPhysicalSpan()
    {
        var result = EtabsModelInterpreter.Interpret(new(Artifact(), RequestedBeamIds: ["b1"]));

        var beam = Assert.Single(result.Beams);
        Assert.Equal("p1", beam.StartPointId);
        Assert.Equal("p2", beam.EndPointId);
        var readiness = Assert.Single(result.BeamReadiness);
        Assert.Equal(EtabsBeamReadinessDisposition.NeedsSupportFacesAndPhysicalSpanMapping, readiness.Disposition);
        Assert.Contains(readiness.MissingFacts, fact => fact.Contains("Physical-span mapping", StringComparison.Ordinal));
    }

    [Fact]
    public void RejectsAcceptedSnapshotBoundToAnotherSourceModel()
    {
        var snapshot = AnalysisSnapshotCodec.ParseAndValidate(Fixture()["valid_snapshot"]!.ToJsonString()).Snapshot!;
        Assert.Throws<ArgumentException>(() => EtabsModelInterpreter.Interpret(new(Artifact(), snapshot)));
    }

    [Fact]
    public void ProjectorFormatProcessIdentityRejectsLegacySameModelIdentity()
    {
        var snapshot = AnalysisSnapshotCodec.ParseAndValidate(Fixture()["valid_snapshot"]!.ToJsonString()).Snapshot!;
        Assert.Throws<ArgumentException>(() => EtabsModelInterpreter.Interpret(new(Artifact(snapshot), snapshot, ["object-b1"])));
        Assert.Throws<ArgumentException>(() => EtabsModelInterpreter.Interpret(new(Artifact(snapshot, processId: 999), snapshot, ["object-b1"])));
    }

    private static EtabsContextArtifact Artifact()
    {
        var identity = new EtabsContextSourceIdentity(42, DateTimeOffset.Parse("2026-09-07T00:00:00Z"), "C:/ETABS.exe", new string('a', 64), "C:/model.edb", 1, DateTimeOffset.Parse("2026-09-07T00:00:00Z"), new string('b', 64), "v1", true, 6, 6);
        var inventory = new EtabsContextInventory("request", DateTimeOffset.Parse("2026-09-07T00:00:00Z"), identity,
            [new("p1", 0, 0, 0), new("p2", 1000, 0, 0), new("p3", 2000, 0, 0), new("p4", 1000, 0, 3000), new("p5", 1000, 1000, 0)],
            [new("b1", "s", "L1", "p1", "p2", EtabsFrameDesignOrientation.Beam), new("b2", "s", "L1", "p2", "p3", EtabsFrameDesignOrientation.Beam), new("c1", "s", "L1", "p2", "p4", EtabsFrameDesignOrientation.Column), new("x1", "s", "L1", "p2", "p5", EtabsFrameDesignOrientation.Brace)],
            [new("s", "m")], "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent");
        return EtabsContextWorkerCodec.CreateArtifact(inventory);
    }

    private static EtabsContextArtifact Artifact(AnalysisSnapshot snapshot, int processId = 4242)
    {
        var identity = new EtabsContextSourceIdentity(processId, DateTimeOffset.Parse("2026-09-04T11:59:00Z"), "C:/ETABS.exe", new string('a', 64), "C:/model.edb", 1, DateTimeOffset.Parse("2026-09-04T11:59:00Z"), snapshot.SourceIdentity.ModelFileSha256.Value!, snapshot.SourceIdentity.SourceVersion, true, 6, 6);
        var points = snapshot.Points.Select(point => new EtabsContextPoint(point.SourceName, point.XMm, point.YMm, point.ZMm)).ToArray();
        var frames = snapshot.Members.Select(member => new EtabsContextFrame(member.ObjectId, snapshot.Sections.Single(section => section.SectionId == member.SectionId).SourceName, member.StoryId,
            snapshot.Points.Single(point => point.PointId == member.PointIId).SourceName, snapshot.Points.Single(point => point.PointId == member.PointJId).SourceName, EtabsFrameDesignOrientation.Beam)).ToArray();
        var sections = snapshot.Sections.Select(section => new EtabsContextSection(section.SourceName, section.MaterialId)).ToArray();
        return EtabsContextWorkerCodec.CreateArtifact(new("request", DateTimeOffset.Parse("2026-09-04T12:00:00Z"), identity, points, frames, sections,
            "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent"));
    }


    private static JsonObject Fixture()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "contracts", "structural-engineering", "conformance", "wp10-vectors.json");
            if (File.Exists(path)) return JsonNode.Parse(File.ReadAllText(path))!.AsObject();
            directory = directory.Parent;
        }
        throw new FileNotFoundException();
    }
}
