using System.Security.Cryptography;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10BulkCaptureTests
{
    [Theory]
    [InlineData(null)]
    [InlineData("mesh")]
    [InlineData("metric-database")]
    [InlineData("case-only")]
    public async Task BulkPreservesEverySignedActionAndMesh(string? variant)
    {
        var host = new BulkHost(variant);
        var directory = Path.Combine(Path.GetTempPath(), "wp10-bulk-" + Guid.NewGuid().ToString("N"));
        try
        {
            var result = await Capture(host, directory);
            Assert.True(result.State == EtabsContextWorkerState.Completed, result.Message);
            var bytes = File.ReadAllBytes(result.EvidencePath);
            var normalized = EtabsCaptureProjector.Normalize(bytes, Convert.ToHexStringLower(SHA256.HashData(bytes)), Wp10SyntheticCapture.Options);
            Assert.True(normalized.Snapshot is not null, string.Join("; ", normalized.Diagnostics.Select(item => item.Message)));
            var snapshot = normalized.Snapshot!;
            Assert.Equal(2, snapshot.Members.Count); Assert.Equal(6, snapshot.ActionRows.Count);
            if (variant == "case-only") Assert.Empty(snapshot.LoadCombinations);
            Assert.Equal(variant == "mesh" ? 3 : 2, snapshot.Members.Sum(member => member.AnalysisElementIds.Count));
            Assert.Equal(new[] { -80d, -60d, -40d, -40d, -30d, -20d }, snapshot.ActionRows.Select(row => row.PKn).Order().ToArray());
            Assert.Equal(2, snapshot.ActionRows.Select(row => row.Provenance.CallId).Distinct().Count());
            Assert.DoesNotContain(result.Artifact!.Content.Capture.Calls, call => call.Operation.StartsWith("LineElm.", StringComparison.Ordinal));
            Assert.Equal(2, result.Artifact.Content.Capture.Calls.Count(call => call.Operation == "Results.FrameForce"));
            Assert.All(result.Artifact.Content.Capture.Calls, call => Assert.False(call.Operation.Split('.')[^1].StartsWith("Set", StringComparison.Ordinal)));
            var model = EtabsModelInterpreter.Interpret(new(EtabsContextWorkerCodec.CreateArtifact(host.Context), snapshot));
            Assert.Equal(2, model.Beams.Count);
            Assert.All(model.BeamReadiness, row => Assert.Equal(EtabsBeamReadinessDisposition.NeedsSupportFacesAndPhysicalSpanMapping, row.Disposition));
        }
        finally { if (Directory.Exists(directory)) Directory.Delete(directory, true); }
    }

    [Theory]
    [InlineData("wrong-unit", true)]
    [InlineData("wrong-database-components", true)]
    [InlineData("truncated-table", false)]
    [InlineData("curved", false)]
    [InlineData("duplicate-frame-element", false)]
    public async Task UnsupportedOrIncompleteSourceNeverProducesAcceptedSnapshot(string fault, bool captureCompletes)
    {
        var host = new BulkHost(fault);
        var directory = Path.Combine(Path.GetTempPath(), "wp10-bulk-reject-" + Guid.NewGuid().ToString("N"));
        try
        {
            var result = await Capture(host, directory);
            Assert.True(result.CleanupCompleted);
            Assert.Equal(captureCompletes, result.State == EtabsContextWorkerState.Completed);
            if (captureCompletes)
            {
                var bytes = File.ReadAllBytes(result.EvidencePath);
                var normalized = EtabsCaptureProjector.Normalize(bytes, Convert.ToHexStringLower(SHA256.HashData(bytes)), Wp10SyntheticCapture.Options);
                Assert.Null(normalized.Snapshot);
            }
            else Assert.Null(result.Artifact);
        }
        finally { if (Directory.Exists(directory)) Directory.Delete(directory, true); }
    }

    private static async Task<EtabsBatchBrokerResult> Capture(BulkHost host, string directory)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(30);
        var handle = new EtabsBatchOperationBroker().Start(new("bulk", host.Identity.ProcessId, deadline, Path.Combine(directory, "capture.json")),
            () => host, (source, token) => EtabsLiveGetterProbe.RunBulk(source, new("bound-request", host.Context, ["beam", "beam2"], deadline), token),
            TestContext.Current.CancellationToken, EtabsBulkGetterMatrix.Sha256);
        var result = await handle.Completion; await handle.Quiescence; return result;
    }

    private sealed class BulkHost(string? variant) : IEtabsGetterHost
    {
        private readonly Wp10BatchCaptureTests.BatchHost _reference = new(variant == "mesh" ? "mesh" : null);
        public EtabsHostIdentity Identity => _reference.Identity with { ProcessId = 94102 };
        public EtabsContextInventory Context => _reference.Context with { Source = _reference.Context.Source with { ProcessId = 94102, DatabaseUnits = variant is "metric-database" or "wrong-database-components" ? 9 : 6 },
            Coverage = "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent" };
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
        {
            if (variant is "metric-database" or "wrong-database-components")
            {
                if (definition.Operation == "SapModel.GetDatabaseUnits") return new(9, []);
                if (definition.Operation == "SapModel.GetDatabaseUnits_2") return new(0, variant == "metric-database" ? [3, 4, 2] : [4, 6, 2]);
            }
            if (variant == "case-only")
            {
                if (definition.Operation == "RespCombo.GetNameList") return new(0, [0, Array.Empty<string>()]);
                if (definition.Operation == "Results.Setup.GetCaseSelectedForOutput") return new(0, [true]);
                if (definition.Operation == "Results.FrameForce")
                {
                    var call = _reference.Invoke(definition, inputs, token);
                    var outputs = call.Outputs.ToArray(); outputs[5] = Enumerable.Repeat("case", (int)outputs[0]!).ToArray();
                    return new(call.ReturnValue, outputs);
                }
            }
            if (definition.Operation == "FrameObj.GetTransformationMatrix") return new(0, [new[] { 0d, 0d, 1d, 1d, 0d, 0d, 0d, 1d, 0d }]);
            if (!definition.Operation.StartsWith("DatabaseTables.", StringComparison.Ordinal)) return _reference.Invoke(definition, inputs, token);
            var key = (string)inputs[0]!;
            var (fields, units, rows, version) = Table(key);
            if (definition.Operation == "DatabaseTables.GetAllFieldsInTable")
                return new(0, [version, fields.Length, fields, fields, fields, units, fields.Select(_ => true).ToArray()]);
            var flat = rows.SelectMany(row => row).ToArray();
            if (variant == "truncated-table" && key == "Frame Assignments - Section Properties") flat = flat[..^1];
            return definition.Operation == "DatabaseTables.GetTableForEditingArray"
                ? new(0, [version, fields, rows.Length, flat])
                : new(0, [inputs[1], version, fields, rows.Length, flat]);
        }
        public void Dispose() => _reference.Dispose();

        private (string[] Fields, string[] Units, string[][] Rows, int Version) Table(string key)
        {
            string[] fields; string[][] rows; var version = 1;
            switch (key)
            {
                case "Beam Object Connectivity":
                    fields = ["UniqueName", "Story", "BeamBay", "CurveType", "UniquePtI", "UniquePtJ"];
                    rows = [["beam", "story", "B", variant == "curved" ? "Circular" : "", "pI", "pJ"], ["beam2", "story", "B", "", "pJ", "pK"]]; version = 2; break;
                case "Point Object Connectivity":
                    fields = ["UniqueName", "Story"]; rows = [["pI", "story"], ["pJ", "story"], ["pK", "story"]]; break;
                case "Objects and Elements - Frames":
                    fields = ["ElmName", "ObjType", "ObjName", "ElmJtI", "ElmJtJ"];
                    rows = variant == "mesh"
                        ? [["element", "Frame", "beam", "pI", "mesh-point"], ["element-mid", "Frame", "beam", "mesh-point", "pJ"], ["element2", "Frame", "beam2", "pJ", "pK"]]
                        : [["element", "Frame", "beam", "pI", "pJ"], ["element2", "Frame", "beam2", "pJ", "pK"]];
                    rows = [.. rows, ["shell-line", "Shell", "slab", "pI", "pJ"], ["shell-line", "Shell", "slab", "pI", "pK"]];
                    if (variant == "duplicate-frame-element") rows = [.. rows, rows[0]]; break;
                case "Frame Assignments - Property Modifiers":
                    fields = ["UniqueName", "AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod", "MMod", "WMod"]; rows = []; break;
                case "Frame Assignments - Releases and Partial Fixity":
                    fields = ["UniqueName", .. new[] { "P", "V2", "V3", "T", "M2", "M3" }.SelectMany(dof => new[] { dof + "I", dof + "J" }),
                        .. new[] { "P", "V2", "V3", "T", "M2", "M3" }.SelectMany(dof => new[] { dof + "ISpring", dof + "JSpring" })]; rows = []; break;
                case "Frame Assignments - Insertion Point":
                    fields = ["UniqueName", "CardinalPt", "Mirror2", "Mirror3", "OffsetCSys", "XI", "YI", "ZI", "XJ", "YJ", "ZJ", "NoTransform"];
                    rows = [["beam", "8 (Top Center)", "No", "No", "", "", "", "", "", "", "", "Yes"], ["beam2", "8 (Top Center)", "No", "No", "", "", "", "", "", "", "", "Yes"]]; break;
                case "Frame Assignments - End Length Offsets":
                    fields = ["UniqueName", "OffsetOpt", "OffsetI", "OffsetJ", "RigidFact"]; rows = [["beam", "Auto", "0.2", "0.3", "0"], ["beam2", "Auto", "0.2", "0.3", "0"]]; break;
                case "Frame Assignments - Section Properties":
                    fields = ["UniqueName", "AutoSelect", "SectProp"]; rows = [["beam", "N.A.", "section"], ["beam2", "N.A.", "section"]]; break;
                case "Joint Assignments - Restraints": fields = ["UniqueName", "UX", "UY", "UZ", "RX", "RY", "RZ"]; rows = []; break;
                default: throw new InvalidOperationException(key);
            }
            var units = fields.Select(field => field switch
            {
                "OffsetI" or "OffsetJ" => variant == "wrong-unit" ? "mm" : "m",
                "XI" or "YI" or "ZI" or "XJ" or "YJ" or "ZJ" => "m",
                _ when field.EndsWith("Spring", StringComparison.Ordinal) => field.StartsWith('T') || field.StartsWith('M') ? "kN-m/rad" : "kN/m",
                _ => ""
            }).ToArray();
            return (fields, units, rows, version);
        }
    }
}
