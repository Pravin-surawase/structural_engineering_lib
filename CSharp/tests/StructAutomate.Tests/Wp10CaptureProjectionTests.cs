using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10CaptureProjectionTests
{
    [Fact]
    public void SyntheticCompleteCaptureNormalizesDeterministically()
    {
        var artifact = Wp10SyntheticCapture.Create();
        var first = Normalize(artifact);
        var second = Normalize(artifact);
        var snapshot = Accepted(first);
        Assert.Equal(AnalysisSnapshotCodec.CanonicalJson(snapshot), AnalysisSnapshotCodec.CanonicalJson(Accepted(second)));
        Assert.Equal(12, snapshot.RawCapture.ModelRecords.Count);
        Assert.Equal(3, snapshot.ActionRows.Count);
        Assert.Equal(15, snapshot.RowLedger.AcceptedCount);
        Assert.Equal(0, snapshot.RowLedger.ApprovedExclusionCount);
        Assert.Equal(48, snapshot.RawCapture.CallLedger.Records.Select(item => item.Method).Distinct().Count());
        Assert.Equal(2400, Assert.Single(snapshot.Materials).MassDensityKgPerM3);
        Assert.Equal(30000, Assert.Single(snapshot.Materials).ElasticModulusNPerMm2);
        Assert.Equal(80000, Assert.Single(snapshot.Sections).AreaMm2);
        Assert.Equal(200, Assert.Single(snapshot.Sections).WidthMm);
        Assert.Equal(400, Assert.Single(snapshot.Sections).DepthMm);
        Assert.Equal(SnapshotLocal2Face.PositiveLocal2, Assert.Single(snapshot.Axes).PhysicalTopFace);
        Assert.Equal(SnapshotLocal3Face.NegativeLocal3, Assert.Single(snapshot.Axes).PhysicalLeftFace);
        var output = Environment.GetEnvironmentVariable("WP10_SYNTHETIC_OUTPUT");
        if (!string.IsNullOrWhiteSpace(output))
            File.WriteAllBytes(output, AnalysisSnapshotCodec.CanonicalJsonBytes(new
            {
                schema_version = "wp10-normalization-conformance/v1",
                valid_snapshot = snapshot,
                expected = new { snapshot.SnapshotId, snapshot.RawCapture.RawCaptureId, canonical_json_sha256 = Sha(AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot)) }
            }));
    }

    [Theory]
    [InlineData("missing-getter")]
    [InlineData("truncated-force")]
    [InlineData("nonzero-step")]
    [InlineData("failed-call")]
    [InlineData("cleanup")]
    [InlineData("host-drift")]
    [InlineData("unit-components")]
    [InlineData("selection")]
    [InlineData("envelope")]
    [InlineData("initial-case")]
    [InlineData("spring")]
    [InlineData("transpose")]
    public void InvalidSourceNeverExposesPartialSnapshot(string fault)
    {
        var artifact = Wp10SyntheticCapture.Create();
        var content = artifact.Content;
        var calls = content.Capture.Calls.ToList();
        void Change(string operation, int output, object? value)
        {
            var index = calls.FindIndex(item => item.Operation == operation);
            var values = calls[index].Outputs.ToArray();
            values[output] = value;
            calls[index] = calls[index] with { Outputs = values };
        }
        switch (fault)
        {
            case "missing-getter": calls.RemoveAll(item => item.Operation == "LoadPatterns.GetLoadType"); break;
            case "truncated-force": Change("Results.FrameForce", 8, new[] { 1d }); break;
            case "nonzero-step": Change("Results.FrameForce", 7, new[] { 1d, 0d, 0d }); break;
            case "failed-call": calls[10] = calls[10] with { CsiReturnCode = 1 }; break;
            case "cleanup": content = content with { Cleanup = content.Cleanup with { HostDisposed = false } }; break;
            case "host-drift": calls[10] = calls[10] with { HostIdentity = calls[10].HostIdentity with { ModelSha256 = new('f', 64) } }; break;
            case "unit-components": Change("SapModel.GetPresentUnits_2", 0, 3); break;
            case "selection": Change("Results.Setup.GetComboSelectedForOutput", 0, false); break;
            case "envelope": Change("RespCombo.GetTypeOAPI", 0, 1); break;
            case "initial-case": Change("LoadCases.StaticLinear.GetInitialCase", 0, "nonlinear-initial"); break;
            case "spring": Change("FrameObj.GetReleases", 2, new[] { 0d, 0d, 0d, 0d, 5d, 0d }); break;
            case "transpose": Change("LineElm.GetTransformationMatrix", 0, new[] { 0d, 1d, 0d, 0d, 0d, 1d, 1d, 0d, 0d }); break;
        }
        var result = Normalize(Wp10SyntheticCapture.Rebind(content with { Capture = content.Capture with { Calls = calls } }));
        Assert.Null(result.Snapshot);
        Assert.NotEmpty(result.Diagnostics);
    }

    [Fact]
    public void ExactBytesAndExplicitMaterialEvidenceAreRequired()
    {
        var bytes = EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(Wp10SyntheticCapture.Create());
        Assert.Null(EtabsCaptureProjector.Normalize(bytes, new('0', 64), Wp10SyntheticCapture.Options).Snapshot);
        var result = EtabsCaptureProjector.Normalize(bytes, Sha(bytes), Wp10SyntheticCapture.Options with { MaterialClassifications = new Dictionary<string, SnapshotMaterialClassification>() });
        Assert.Null(result.Snapshot);
        Assert.Equal("MATERIAL.CLASSIFICATION_REQUIRED", Assert.Single(result.Diagnostics).Code);
    }

    [Fact]
    public void DurableV1EncodingPreservesExistingNumericSpelling()
    {
        var bytes = EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(Wp10SyntheticCapture.Create());
        var text = System.Text.Encoding.UTF8.GetString(bytes);
        Assert.Contains("1E-05", text);
        var replay = EtabsAcquisitionArtifactCodec.ParseAndValidate(text);
        Assert.Equal(bytes, EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(replay));
        Assert.Contains("1e-05", AnalysisSnapshotCodec.CanonicalJson(Accepted(Normalize(replay))));
    }

    public static bool RetainedArtifactConfigured => !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("WP10_OFFLINE_ARTIFACT"));

    [Fact(Skip = "Requires explicit external offline artifact, digest and new output path.", SkipUnless = nameof(RetainedArtifactConfigured))]
    public void RetainedArtifactNormalizesWithoutHostAccess()
    {
        var path = Environment.GetEnvironmentVariable("WP10_OFFLINE_ARTIFACT")!;
        var expected = Environment.GetEnvironmentVariable("WP10_OFFLINE_SHA256");
        var output = Environment.GetEnvironmentVariable("WP10_OFFLINE_OUTPUT");
        Assert.False(string.IsNullOrWhiteSpace(expected));
        Assert.False(string.IsNullOrWhiteSpace(output));
        Assert.NotEqual(Path.GetFullPath(path), Path.GetFullPath(output!));
        var bytes = File.ReadAllBytes(path);
        Assert.Equal(bytes, EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(
            EtabsAcquisitionArtifactCodec.ParseAndValidate(System.Text.Encoding.UTF8.GetString(bytes))));
        var options = new EtabsNormalizationOptions("wp10-evidence-project", "wp10-normalizer/v1",
            "WP10-04 owner material declaration and delegated normalization policy 2026-09-05",
            new Dictionary<string, SnapshotMaterialClassification> { ["M25FE500"] = new("concrete", "owner-declared 2026-09-05; not captured material enum") });
        var snapshot = Accepted(EtabsCaptureProjector.Normalize(bytes, expected!, options));
        var repeat = Accepted(EtabsCaptureProjector.Normalize(bytes, expected!, options));
        Assert.Equal(AnalysisSnapshotCodec.CanonicalJson(snapshot), AnalysisSnapshotCodec.CanonicalJson(repeat));
        Assert.Equal(97, snapshot.RawCapture.ModelRecords.Count);
        Assert.Equal(13, snapshot.ActionRows.Count);
        Assert.Equal(110, snapshot.RowLedger.AcceptedCount);
        Assert.Equal(820, snapshot.RawCapture.CallLedger.RecordCount);
        Assert.Equal(15, snapshot.LoadCases.Count);
        Assert.Equal(62, snapshot.LoadCombinations.Count);
        Assert.Equal(expected, Sha(File.ReadAllBytes(path)));
        using var stream = new FileStream(output!, FileMode.CreateNew, FileAccess.Write);
        stream.Write(AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot));
    }

    private static EtabsSnapshotResult Normalize(EtabsDurableRawArtifact artifact)
    {
        var bytes = EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(artifact);
        return EtabsCaptureProjector.Normalize(bytes, Sha(bytes), Wp10SyntheticCapture.Options);
    }
    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private static AnalysisSnapshot Accepted(EtabsSnapshotResult result)
    {
        Assert.True(result.OperationState == SnapshotOperationState.Completed, string.Join(" | ", result.Diagnostics.Select(item => $"{item.Code}: {item.Message}")));
        return Assert.IsType<AnalysisSnapshot>(result.Snapshot);
    }
}
