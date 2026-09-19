using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class EtabsSourceReaderTests
{
    private static readonly EtabsSourceScope Scope = new(["B1", "B2"], ["Dead"], []);

    [Theory]
    [InlineData(6)]
    [InlineData(9)]
    public void NativeSourceValuesReachTheSameTypedFactsWithoutChangingUnits(int units)
    {
        using var host = new Host(units);
        var capture = EtabsSourceReader.Read(host, Scope, DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken);
        Assert.Equal(2, capture.Facts.Members.Count);
        Assert.All(capture.Facts.Members, member =>
        {
            Assert.Equal(300, member.WidthMm); Assert.Equal(600, member.DepthMm);
            Assert.Equal("C30", member.EffectiveMaterial);
            Assert.Equal("complete_material_overwrite_table_has_no_object_row", member.MaterialResolutionBasis);
            Assert.Equal(150, member.Assignments.EndOffsetIMm);
            Assert.Equal(250, member.Stations!.MaximumSpacingMm);
            Assert.Equal(member.Name, Assert.Single(member.Elements).ReverseObjectName);
            Assert.Contains(member.Restrictions, r => r.Code == "SOURCE.PHYSICAL_SUPPORT_UNQUALIFIED");
        });
        var material = Assert.Single(capture.Facts.Materials);
        Assert.Equal(30, material.ConcreteFcNPerMm2);
        Assert.Equal(30000, material.ElasticModulusNPerMm2);
        Assert.Equal("complete_static_source", Assert.Single(capture.Facts.SelectedLoads).State);
        Assert.DoesNotContain(host.Operations, op => op.Contains("Set", StringComparison.Ordinal) && !op.Contains("Setup", StringComparison.Ordinal) || op == "Results.FrameForce");
        Assert.All(capture.Calls, call => Assert.Equal(EtabsSourceGetterMatrix.Sha256, call.GetterMatrixSha256));
        Assert.Equal(2, host.Operations.Count(op => op == "PropMaterial.GetOConcrete"));
        Assert.Empty(capture.Gaps);
    }

    [Fact]
    public void ExplicitMaterialTableRowOverridesOnlyItsAssignedMember()
    {
        using var host = new Host(9) { KnownOverwrite = true };
        var capture = EtabsSourceReader.Read(host, Scope, DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken);
        Assert.Equal("C30", capture.Facts.Members[0].SectionMaterial);
        Assert.Equal("C40", capture.Facts.Members[0].EffectiveMaterial);
        Assert.Equal("explicit_material_overwrite_table_row", capture.Facts.Members[0].MaterialResolutionBasis);
        Assert.Equal("C30", capture.Facts.Members[1].EffectiveMaterial);
        Assert.Equal(40, Assert.Single(capture.Facts.Materials, m => m.Name == "C40").ConcreteFcNPerMm2);
        Assert.Equal(30, Assert.Single(capture.Facts.Materials, m => m.Name == "C30").ConcreteFcNPerMm2);
        Assert.Empty(capture.Gaps);
    }

    [Fact]
    public void MissingOneFrameGetterAndUnqualifiedOverwriteRowDoNotErasePeers()
    {
        using var host = new Host(9) { MissingB2Section = true, UnknownOverwrite = true };
        var capture = EtabsSourceReader.Read(host, Scope, DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken);
        Assert.Equal(2, capture.Facts.Members.Count);
        Assert.Equal(300, capture.Facts.Members[0].WidthMm);
        Assert.Null(capture.Facts.Members[1].WidthMm);
        Assert.All(capture.Facts.Members, member =>
        {
            Assert.Null(member.EffectiveMaterial);
            Assert.Contains(member.Restrictions, r => r.Code == "SOURCE.MATERIAL_OVERWRITE_UNRESOLVED");
        });
        Assert.Contains(capture.Gaps, gap => gap.Operation == "FrameObj.GetSection" && gap.RawInvocation!.ReturnValue is 7);
        Assert.Equal("C30", capture.Facts.Members[0].SectionMaterial);
    }

    [Fact]
    public void ProtectedUnitDriftRejectsTheArtifactAndInvalidScopeNeverCallsTheHost()
    {
        using var host = new Host(9) { DriftUnits = true };
        Assert.Throws<InvalidOperationException>(() => EtabsSourceReader.Read(host, Scope,
            DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken));
        using var untouched = new Host(9);
        Assert.Throws<ArgumentException>(() => EtabsSourceReader.Read(untouched, new([], ["Dead"], []),
            DateTimeOffset.UtcNow.AddMinutes(1), TestContext.Current.CancellationToken));
        Assert.Empty(untouched.Operations);
        Assert.DoesNotContain(EtabsSourceGetterMatrix.Allowed.Keys, op => op == "Results.FrameForce" || op.StartsWith("File.", StringComparison.Ordinal));
    }

    [Fact]
    public async Task SourceBrokerUsesTheSharedLeaseJournalAndPostCleanupPublication()
    {
        var directory = Path.Combine(Path.GetTempPath(), "source-qualification-" + Guid.NewGuid().ToString("N"));
        var path = Path.Combine(directory, "source.json");
        var host = new Host(9);
        try
        {
            var handle = EtabsSourceBroker.Start(new("source-test", host.Identity.ProcessId, DateTimeOffset.UtcNow.AddMinutes(1), path),
                Scope, () => host, TestContext.Current.CancellationToken);
            var result = await handle.Completion; await handle.Quiescence;
            Assert.Equal("completed", result.State); Assert.True(result.CleanupCompleted); Assert.True(host.Disposed);
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            Assert.Equal(EtabsSourceBroker.ArtifactSchema, document.RootElement.GetProperty("SchemaVersion").GetString());
            Assert.Equal(EtabsSourceGetterMatrix.Sha256, document.RootElement.GetProperty("GetterMatrixSha256").GetString());
            Assert.Equal(host.Operations.Count * 2, File.ReadLines(path + ".journal.jsonl").Count());
        }
        finally { if (Directory.Exists(directory)) Directory.Delete(directory, true); }
    }

    internal sealed class Host(int units) : IEtabsGetterHost
    {
        private readonly Wp10InspectionTests.Host _base = new() { Units = units };
        public EtabsHostIdentity Identity => _base.Identity;
        public List<string> Operations { get; } = [];
        public bool MissingB2Section { get; init; }
        public bool UnknownOverwrite { get; init; }
        public bool KnownOverwrite { get; init; }
        public bool DriftUnits { get; init; }
        public bool Disposed { get; private set; }

        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
        {
            var op = definition.Operation; Operations.Add(op);
            var name = inputs.FirstOrDefault() as string ?? "";
            double L(double mm) => units == 6 ? mm / 1000 : mm;
            double S(double stress) => units == 6 ? stress * 1000 : stress;
            if (DriftUnits && op == "SapModel.GetPresentUnits" && Operations.Count(x => x == op) > 1) return new(6, []);
            if (MissingB2Section && op == "FrameObj.GetSection" && name == "B2" || name == "UndocumentedDefault" && op.StartsWith("PropMaterial.", StringComparison.Ordinal)) return new(7, []);
            if (op == "DatabaseTables.GetAllFieldsInTable")
            {
                var fields = name == "Frame Assignments - Material Overwrites" ? new[] { "UniqueName", "Material" } : new[] { "ElmName", "ObjType", "ObjName", "ElmJtI", "ElmJtJ" };
                return new(0, [1, fields.Length, fields, fields, fields, fields.Select(_ => "").ToArray(), fields.Select(_ => true).ToArray()]);
            }
            if (op == "DatabaseTables.GetTableForEditingArray")
                return new(0, [1, new[] { "UniqueName", "Material" }, UnknownOverwrite ? 2 : KnownOverwrite ? 1 : 0,
                    UnknownOverwrite ? new[] { "B1", "UndocumentedDefault", "B2", "UndocumentedDefault" } : KnownOverwrite ? new[] { "B1", "C40" } : System.Array.Empty<string>()]);
            if (op == "DatabaseTables.GetTableForDisplayArray")
                return new(0, [inputs[1], 1, inputs[1], 2,
                    new[] { "B1-E", "Frame", "B1", "B1-I", "B1-J", "B2-E", "Frame", "B2", "B2-I", "B2-J" }]);
            object?[]? outputs = op switch
            {
                "FrameObj.GetLabelFromName" => [name, "L1"],
                "FrameObj.GetSection" => ["R300x600", ""],
                "FrameObj.GetPoints" => [name + "-I", name + "-J"],
                "FrameObj.GetDesignOrientation" => [2],
                "FrameObj.GetEndLengthOffset" => [false, L(150), L(150), 0.5d],
                "FrameObj.GetInsertionPoint_1" => [8, false, false, false, new double[] { 0, 0, 0 }, new double[] { 0, 0, 0 }, "Global"],
                "FrameObj.GetOutputStations" => [1, L(250), 3, false, false],
                "PointObj.GetCoordCartesian" => [L(name.EndsWith("-J", StringComparison.Ordinal) ? 6000 : 0), 0d, L(3000)],
                "PointObj.GetConnectivity" => [1, new[] { 2 }, new[] { name[..2] }, new[] { name.EndsWith("-I", StringComparison.Ordinal) ? 1 : 2 }],
                "PointObj.GetTransformationMatrix" or "LineElm.GetTransformationMatrix" => [new double[] { 1, 0, 0, 0, 1, 0, 0, 0, 1 }],
                "LineElm.GetObj" => [name[..2], 2, 0d, 1d],
                "LineElm.GetPoints" => [name[..2] + "-I", name[..2] + "-J"],
                "PropFrame.GetMaterial" => ["C30"],
                "PropFrame.GetTypeOAPI" => [8],
                "PropFrame.GetRectangle" => ["", "C30", L(600), L(300), 0, "", "guid"],
                "PropMaterial.GetTypeOAPI" => [2, 0],
                "PropMaterial.GetMPIsotropic" => [S(30000), 0.2d, 0.00001d, S(12500)],
                "PropMaterial.GetOConcrete" => [S(name == "C40" ? 40 : 30), false, 1d, 1, 2, 0.002d, 0.0035d, 0d, 0d],
                "LoadCases.GetTypeOAPI" => [1, 0],
                "LoadCases.StaticLinear.GetInitialCase" => [""],
                "LoadCases.StaticLinear.GetLoads" => [1, new[] { "Load" }, new[] { "Dead" }, new double[] { 1 }],
                "LoadPatterns.GetLoadType" => [1],
                "LoadPatterns.GetSelfWTMultiplier" => [1d],
                "Results.Setup.GetCaseSelectedForOutput" => [true],
                _ => null
            };
            return outputs is null ? _base.Invoke(definition, inputs, token) : new(0, outputs);
        }
        public void Dispose() { Disposed = true; _base.Dispose(); }
    }
}
