using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class EtabsTopologyReaderTests
{
    private static readonly EtabsSourceScope Scope = new(["B1", "B2"], ["Dead"], []);

    [Theory]
    [InlineData(6)]
    [InlineData(9)]
    public void NativeGeometryAndVersionedShellAssignmentsProduceEquivalentEnvelopeFacts(int units)
    {
        using var host = new Host(units);
        var capture = EtabsTopologyReader.Read(host, Scope, DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken);
        Assert.Empty(capture.Gaps); Assert.Empty(capture.SourceCapture.Gaps);
        Assert.Equal(4, capture.Geometry.Areas.Count);
        Assert.All(capture.Facts.Members, member =>
        {
            Assert.Equal(5800, member.ModelledClearLengthMm);
            Assert.Equal(50, member.EndI!.ReportedMinusModelledMm);
            Assert.Equal("project_intent_required", member.Role.State);
            Assert.Equal("collinear_complete_analysis_mesh", member.ReferenceLineBasis);
        });
        Assert.All(capture.Geometry.Areas, area => Assert.Equal("centred_uniform_no_overwrites", area.PlacementBasis));
        Assert.All(capture.Geometry.Frames, frame =>
        {
            Assert.Null(frame.CurveType);
            Assert.Equal("beam_connectivity_curvature_not_returned", frame.CurveBasis);
        });
        Assert.DoesNotContain("FrameObj.GetCurved_2", host.Operations);
        Assert.DoesNotContain("Results.FrameForce", host.Operations);
        Assert.Equal(2, host.Operations.Count(op => op == "AreaObj.GetProperty:B1-I-wall"));
    }

    [Fact]
    public void AFailedWallGetterRetainsBothMembersAndTheIndependentCompletePeer()
    {
        using var host = new Host(9) { MissingWall = true };
        var capture = EtabsTopologyReader.Read(host, Scope, DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken);
        Assert.Null(capture.Facts.Members[0].ModelledClearLengthMm);
        Assert.Equal(5800, capture.Facts.Members[1].ModelledClearLengthMm);
        var gap = Assert.Single(capture.Gaps);
        Assert.Equal(7, gap.RawInvocation!.ReturnValue);
        Assert.Equal("AreaObj.GetProperty", gap.Operation);
    }

    [Fact]
    public void SourceFactsStayProtectedUntilTheWholeTopologyReadEnds()
    {
        using var host = new Host(9) { DriftSourceAfterTopology = true };
        var failure = Assert.Throws<InvalidOperationException>(() => EtabsTopologyReader.Read(host, Scope,
            DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken));
        Assert.Contains("PropFrame.GetModifiers", failure.Message);
    }

    [Fact]
    public void ExcessiveFanoutStopsBeforeAdjacentObjectGetters()
    {
        using var host = new Host(9) { ExcessiveConnections = true };
        Assert.Throws<InvalidOperationException>(() => EtabsTopologyReader.Read(host, Scope,
            DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken));
        Assert.DoesNotContain(host.Operations, op => op.StartsWith("AreaObj.", StringComparison.Ordinal));
    }

    [Fact]
    public async Task BrokerPublishesOnlyAfterCleanupAndInvalidScopeNeverAttaches()
    {
        using var host = new Host(9);
        var path = Path.Combine(Path.GetTempPath(), "topology-" + Guid.NewGuid().ToString("N"), "capture.json");
        var attached = false;
        Assert.Throws<ArgumentException>(() => EtabsTopologyBroker.Start(new("bad", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMinutes(1), path),
            new([], ["Dead"], []), () => { attached = true; return host; }, TestContext.Current.CancellationToken));
        Assert.False(attached);
        try
        {
            var handle = EtabsTopologyBroker.Start(new("topology", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMinutes(1), path), Scope, () => host, TestContext.Current.CancellationToken);
            var result = await handle.Completion; await handle.Quiescence;
            Assert.Equal("completed", result.State); Assert.True(result.CleanupCompleted); Assert.True(host.Disposed);
            using var artifact = JsonDocument.Parse(File.ReadAllBytes(path));
            Assert.Equal("structural.etabs_topology/v1", artifact.RootElement.GetProperty("SchemaVersion").GetString());
            Assert.Equal("STA", artifact.RootElement.GetProperty("Cleanup").GetProperty("ApartmentState").GetString());
            Assert.True(File.Exists(path + ".journal.jsonl"));
        }
        finally { if (Directory.Exists(Path.GetDirectoryName(path))) Directory.Delete(Path.GetDirectoryName(path)!, true); }
    }

    private sealed class Host(int units) : IEtabsGetterHost
    {
        private readonly EtabsSourceReaderTests.Host _source = new(units);
        private bool _topology;
        public EtabsHostIdentity Identity => _source.Identity;
        public bool Disposed { get; private set; }
        public bool MissingWall { get; init; }
        public bool DriftSourceAfterTopology { get; init; }
        public bool ExcessiveConnections { get; init; }
        public List<string> Operations { get; } = [];
        private double L(double mm) => units == 6 ? mm / 1000 : mm;

        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
        {
            var op = definition.Operation; var name = inputs.FirstOrDefault() as string ?? "";
            Operations.Add(op); Operations.Add(op + ":" + name);
            if (op == "FrameObj.Count") return new(2, []);
            if (MissingWall && op == "AreaObj.GetProperty" && name == "B1-I-wall") return new(7, []);
            if (DriftSourceAfterTopology && _topology && op == "PropFrame.GetModifiers") return new(0, [new double[] { 2, 1, 1, 1, 1, 1, 1, 1 }]);
            if (op == "FrameObj.GetAllFrames")
            {
                _topology = true;
                object?[] values = [2, new[] { "B1", "B2" }, new[] { "R300x600", "R300x600" }, new[] { "L1", "L1" },
                    new[] { "B1-I", "B2-I" }, new[] { "B1-J", "B2-J" }];
                return new(0, [.. values, .. Enumerable.Range(6, 13).Select(i => (object)new[] { i == 9 ? L(6000) : i is 8 or 11 ? L(3000) : 0, i == 9 ? L(6000) : i is 8 or 11 ? L(3000) : 0 }), new[] { 8, 8 }]);
            }
            if (op.StartsWith("DatabaseTables.", StringComparison.Ordinal) && (name.StartsWith("Area Assignments", StringComparison.Ordinal) || name == "Beam Object Connectivity"))
            {
                var insertion = name == "Area Assignments - Insertion Point"; var beam = name == "Beam Object Connectivity";
                string[] fields = insertion ? ["UniqueName", "CardinalPt", "CoordSys", "PointNumber", "Offset1", "Offset2", "Offset3", "Transform"] :
                    beam ? ["UniqueName", "UniquePtI", "UniquePtJ", "Story", "CurveType"] : ["UniqueName", "PointNumber", "Thickness"];
                var version = insertion || beam ? 2 : 1;
                if (op == "DatabaseTables.GetAllFieldsInTable")
                    return new(0, [version, fields.Length, fields, fields, fields, fields.Select(f => f.StartsWith("Offset", StringComparison.Ordinal) || f == "Thickness" ? units == 6 ? "m" : "mm" : "").ToArray(), fields.Select(_ => true).ToArray()]);
                if (beam) return new(0, [inputs[1], version, fields, 2, new[] { "B1", "B1-I", "B1-J", "L1", "", "B2", "B2-I", "B2-J", "L1", "" }]);
                string[] cells = insertion ? new[] { "B1-I-wall", "B1-J-wall", "B2-I-wall", "B2-J-wall" }
                    .SelectMany(w => new[] { w, "Middle", "", "", "", "", "", "Yes" }).ToArray() : [];
                return new(0, [version, fields, insertion ? 4 : 0, cells]);
            }
            if (op == "PointObj.GetConnectivity")
            {
                if (ExcessiveConnections) return new(0, [201, Enumerable.Repeat(5, 201).ToArray(), Enumerable.Range(0, 201).Select(i => "A" + i).ToArray(), Enumerable.Repeat(1, 201).ToArray()]);
                return new(0, [2, new[] { 2, 5 }, new[] { name[..2], name + "-wall" }, new[] { name.EndsWith("-I", StringComparison.Ordinal) ? 1 : 2, 1 }]);
            }
            object?[]? output = op switch
            {
                "FrameObj.GetTransformationMatrix" => [new double[] { 1, 0, 0, 0, 0, -1, 0, 1, 0 }],
                "AreaObj.GetPoints" => [4, new[] { name[..^5], name[..^5] + "-a", name[..^5] + "-b", name[..^5] + "-c" }],
                "AreaObj.GetDesignOrientation" => [1],
                "AreaObj.GetOpening" => [false],
                "AreaObj.GetProperty" => ["W200"],
                "AreaObj.GetOffsets3" => [4, new double[4]],
                "PropArea.GetWall" => [1, 1, "C30", L(200), 0, "", "guid"],
                "PointObj.GetCoordCartesian" or "PointElm.GetCoordCartesian" => [L(name.Contains("-J", StringComparison.Ordinal) ? 6000 : 0),
                    L(name.EndsWith("-a", StringComparison.Ordinal) || name.EndsWith("-b", StringComparison.Ordinal) ? 1000 : 0),
                    L(name.EndsWith("-b", StringComparison.Ordinal) || name.EndsWith("-c", StringComparison.Ordinal) ? 0 : 3000)],
                _ => null
            };
            return output is null ? _source.Invoke(definition, inputs, token) : new(0, output);
        }
        public void Dispose() { Disposed = true; _source.Dispose(); }
    }
}
