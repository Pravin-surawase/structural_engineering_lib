using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class Wp10NormalizationTests
{
    [Fact]
    public void PortableScientificNumbersUseFrozenPythonSpelling()
    {
        var json = System.Text.Encoding.UTF8.GetString(AnalysisSnapshotCodec.CanonicalJsonBytes(
            new[] { -0d, 1d, 0.00001, 5.50000004295725e-6, 1e16 }));
        Assert.Equal("[0,1,1e-05,5.50000004295725e-06,1e+16]", json);
        using var document = JsonDocument.Parse("[1.0,1E-05,-0.0]");
        Assert.Equal("[1,1e-05,0]", System.Text.Encoding.UTF8.GetString(AnalysisSnapshotCodec.CanonicalJsonBytes(document.RootElement)));
    }

    [Fact]
    public void SourceDimensionsAndAllSixSignedComponentsHaveIndependentExpectedValues()
    {
        var snapshot = Accepted(AnalysisSnapshotNormalizer.Normalize(Raw()));
        var section = Assert.Single(snapshot.Sections);
        Assert.Equal(80000, section.AreaMm2);
        Assert.Equal(730000000, section.TorsionalConstantMm4, 3);
        Assert.Equal(266666666.6666667, section.Inertia2Mm4, 3);
        Assert.Equal(1066666666.6666667, section.Inertia3Mm4, 3);
        Assert.Equal(30000, Assert.Single(snapshot.Materials).ElasticModulusNPerMm2);
        Assert.Equal(2400, Assert.Single(snapshot.Materials).MassDensityKgPerM3);
        var station = snapshot.Stations.Single(item => item.ObjectStationMm == 200);
        Assert.Equal(200, station.PhysicalStationMm);
        Assert.Equal(0.05, station.NormalizedRatio);
        var row = snapshot.ActionRows.Single(item => item.Provenance.SourceRowIndex == 1);
        Assert.Equal(new[] { -30d, 2d, 4d, -0.4, 2.5, -9d }, new[] { row.PKn, row.V2Kn, row.V3Kn, row.TKnm, row.M2Knm, row.M3Knm });
        Assert.Null(row.StepNumber);
        Assert.Equal(200, Assert.Single(snapshot.Members).Offsets.EndIMm);
        Assert.Equal(300, Assert.Single(snapshot.Members).Offsets.EndJMm);
        Assert.Equal(0.8, Assert.Single(snapshot.Members).Modifiers.Inertia2);
        var rawSection = snapshot.RawCapture.ModelRecords.Single(item => item.RecordKind == RawModelRecordKind.Section);
        Assert.Equal(0.7, rawSection.Fields["data"].GetProperty("modifiers")[4].GetDouble());
        var rawMember = snapshot.RawCapture.ModelRecords.Single(item => item.RecordKind == RawModelRecordKind.Member);
        Assert.Equal(8, rawMember.Fields["data"].GetProperty("insertion").GetProperty("cardinal_point").GetInt32());
    }

    [Fact]
    public void NormalizerEnforcesConservationWithoutCallerAccounting()
    {
        var raw = Raw();
        var missingModel = Rehash(raw with { ModelRecords = raw.ModelRecords.Where(item => item.RecordKind != RawModelRecordKind.Section).ToArray() });
        var missingForce = Rehash(raw with { ForceRows = raw.ForceRows.Skip(1).ToArray() });
        var missingEvidence = Edit(raw, RawModelRecordKind.ModelMetadata, data => data["projection"]!["getter_evidence"]!.AsArray().RemoveAt(0));
        var changedForce = Rehash(raw with { ForceRows = raw.ForceRows.Select((row, index) => index == 1 ? row with { M3 = 999 } : row).ToArray() });
        foreach (var input in new[] { missingModel, missingForce, missingEvidence, changedForce })
        {
            var result = AnalysisSnapshotNormalizer.Normalize(input);
            Assert.Null(result.Snapshot);
            Assert.Contains(result.Diagnostics, item => item.Code is "ETABS.ROW_ACCOUNTING" or "ETABS.COVERAGE_INCOMPLETE");
        }
    }

    [Theory]
    [InlineData("transpose")]
    [InlineData("station-origin")]
    [InlineData("envelope")]
    [InlineData("cycle")]
    [InlineData("material")]
    [InlineData("offset")]
    [InlineData("units")]
    public void RequiredAmbiguityWithholdsTheWholeSnapshot(string fault)
    {
        var raw = Raw();
        raw = fault switch
        {
            "transpose" => Edit(raw, RawModelRecordKind.Member, data => data["elements"]![0]!["local_to_global"] = JsonSerializer.SerializeToNode(new[] { 0d, 1d, 0d, 0d, 0d, 1d, 1d, 0d, 0d })),
            "station-origin" => Edit(raw, RawModelRecordKind.Station, data => data["object_station"] = 0),
            "envelope" => Edit(raw, RawModelRecordKind.LoadCombination, data => data["kind"] = "envelope"),
            "cycle" => Edit(raw, RawModelRecordKind.LoadCombination, data => { data["factors"]![0]!["source_kind"] = "load_combination"; data["factors"]![0]!["source_id"] = "combo:combo"; }),
            "material" => Edit(raw, RawModelRecordKind.ModelMetadata, data => data["context"]!["material_classifications"] = new JsonObject()),
            "offset" => Edit(raw, RawModelRecordKind.Member, data => data["insertion"]!["offset_i"]![1] = 0.1),
            "units" => Rehash(raw with { SourceUnits = raw.SourceUnits with { Force = "N" } }),
            _ => raw
        };
        var result = AnalysisSnapshotNormalizer.Normalize(raw);
        Assert.Null(result.Snapshot);
        Assert.NotEmpty(result.Diagnostics);
    }

    [Fact]
    public void ReversingMemberDirectionChangesGlobalAxesAndPreservesViewingConvention()
    {
        var raw = Raw();
        raw = Edit(raw, RawModelRecordKind.Point, data => data["y"] = data["name"]!.GetValue<string>() == "pI" ? 6d : 2d, all: true);
        raw = Edit(raw, RawModelRecordKind.Member, data => data["elements"]![0]!["local_to_global"] = JsonSerializer.SerializeToNode(new[] { 0d, 0d, -1d, -1d, 0d, 0d, 0d, 1d, 0d }));
        var axis = Assert.Single(Accepted(AnalysisSnapshotNormalizer.Normalize(raw)).Axes);
        Assert.Equal(new SnapshotVector3(0, -1, 0), axis.E1);
        Assert.Equal(new SnapshotVector3(-1, 0, 0), axis.E3);
        Assert.Equal(SnapshotLocal3Face.NegativeLocal3, axis.PhysicalLeftFace);
    }

    [Fact]
    public void MeshedElementStationUsesItsOwnOriginAndPhysicalMemberLength()
    {
        var raw = Raw();
        var mid = new RawSnapshotModelRecord(RawModelRecordKind.Point, "source:point:pM",
            new Dictionary<string, JsonElement> { ["data"] = AnalysisSnapshotNormalizer.SourceData(new SourceSnapshotPoint("point:pM", "pM", 1, 4, 3, "story")) });
        raw = raw with { ModelRecords = raw.ModelRecords.Append(mid).OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray() };
        raw = Edit(raw, RawModelRecordKind.Member, data =>
        {
            var element = data["elements"]![0]!.DeepClone();
            var first = element.DeepClone();
            first["id"] = "element-a"; first["point_j_id"] = "point:pM"; first["relative_j"] = 0.5;
            element["id"] = "element-b"; element["point_i_id"] = "point:pM"; element["relative_i"] = 0.5;
            data["elements"] = new JsonArray(first, element);
        });
        raw = Edit(raw, RawModelRecordKind.Station, data =>
        {
            var position = data["object_station"]!.GetValue<double>();
            data["element_id"] = position < 2 ? "element-a" : "element-b";
            data["element_station"] = position < 2 ? position : position - 2;
        }, all: true);
        raw = raw with
        {
            ForceRows = raw.ForceRows.Select(row => row with
            {
                AnalysisElementId = row.ObjectStation < 2 ? "element-a" : "element-b",
                ElementStation = row.ObjectStation < 2 ? row.ObjectStation : row.ObjectStation - 2
            }).ToArray()
        };
        raw = Edit(raw, RawModelRecordKind.ModelMetadata, data =>
        {
            data["projection"]!["model_records"] = JsonSerializer.SerializeToNode(raw.ModelRecords.Select(item =>
                new { source_record_id = item.SourceRecordId, record_kind = item.RecordKind == RawModelRecordKind.Point ? "point" : Token(item.RecordKind) }));
            var force = data["projection"]!["getter_evidence"]!.AsArray().Single(item => item!["operation"]!.GetValue<string>() == "Results.FrameForce")!;
            force["outputs"]![3] = JsonSerializer.SerializeToNode(raw.ForceRows.Select(row => row.AnalysisElementId));
            force["outputs"]![4] = JsonSerializer.SerializeToNode(raw.ForceRows.Select(row => row.ElementStation));
        });
        var snapshot = Accepted(AnalysisSnapshotNormalizer.Normalize(Rehash(raw)));
        var last = snapshot.Stations.Single(item => item.ObjectStationMm == 3700);
        Assert.Equal(1700, last.ElementStationMm, 6);
        Assert.Equal(3700, last.PhysicalStationMm);
        Assert.Equal(0.925, last.NormalizedRatio, 12);
        Assert.Equal(2, Assert.Single(snapshot.Members).AnalysisElementIds.Count);
    }

    [Fact]
    public void SharedSyntheticVectorReplaysWithExactCanonicalIdentity()
    {
        var fixture = Fixture();
        var snapshot = Accepted(AnalysisSnapshotCodec.ParseAndValidate(fixture["valid_snapshot"]!.ToJsonString()));
        Assert.Equal(fixture["expected"]!["snapshot_id"]!.GetValue<string>(), snapshot.SnapshotId);
        Assert.Equal(fixture["expected"]!["canonical_json_sha256"]!.GetValue<string>(),
            Convert.ToHexStringLower(SHA256.HashData(AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot))));
        Assert.Equal(snapshot.SnapshotId, Accepted(AnalysisSnapshotNormalizer.Normalize(snapshot.RawCapture)).SnapshotId);
        Assert.All(snapshot.RawCapture.CallLedger.Records, record => Assert.EndsWith("Z", record.RecordedAtUtc));
    }

    private static string Token(RawModelRecordKind kind) => AnalysisSnapshotNormalizer.SourceData(kind).GetString()!;
    private static RawAnalysisCapture Raw() => Accepted(AnalysisSnapshotCodec.ParseAndValidate(Fixture()["valid_snapshot"]!.ToJsonString())).RawCapture;
    private static RawAnalysisCapture Edit(RawAnalysisCapture raw, RawModelRecordKind kind, Action<JsonObject> edit, bool all = false)
    {
        var changed = false;
        var records = raw.ModelRecords.Select(item =>
        {
            if (item.RecordKind != kind || changed && !all) return item;
            var data = JsonNode.Parse(item.Fields["data"].GetRawText())!.AsObject();
            edit(data); changed = true;
            return item with { Fields = new Dictionary<string, JsonElement> { ["data"] = JsonSerializer.SerializeToElement(data) } };
        }).ToArray();
        return Rehash(raw with { ModelRecords = records });
    }
    private static RawAnalysisCapture Rehash(RawAnalysisCapture raw)
    {
        var sha = AnalysisSnapshotCodec.RawCaptureSha256(raw);
        return raw with { RawCaptureSha256 = sha, RawCaptureId = $"raw_capture_id:{AnalysisSnapshotCodec.CanonicalizationVersion}:{sha}" };
    }
    private static AnalysisSnapshot Accepted(EtabsSnapshotResult result)
    {
        Assert.True(result.OperationState == SnapshotOperationState.Completed, string.Join(" | ", result.Diagnostics.Select(item => $"{item.Code}: {item.Message}")));
        return Assert.IsType<AnalysisSnapshot>(result.Snapshot);
    }
    private static JsonObject Fixture()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null)
        {
            var path = Path.Combine(root.FullName, "contracts", "structural-engineering", "conformance", "wp10-normalization-vectors.json");
            if (File.Exists(path)) return JsonNode.Parse(File.ReadAllText(path))!.AsObject();
            root = root.Parent;
        }
        throw new FileNotFoundException("WP10 normalization vector is missing.");
    }
}
