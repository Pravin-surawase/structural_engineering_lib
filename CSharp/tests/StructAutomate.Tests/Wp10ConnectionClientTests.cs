using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10ConnectionClientTests
{
    [Fact]
    public void ResponseMustBelongToExactRequestAndBeQuiescedBeforeCompletion()
    {
        var response = new EtabsContextWorkerResponse("a", new string('a', 64), EtabsContextWorkerState.Completed, null, null, "context.json", new string('b', 64), true, true);
        var bytes = EtabsContextWorkerCodec.CanonicalResponseJsonBytes(response);
        Assert.Equal(response, EtabsContextWorkerCodec.ParseAndValidateResponse(bytes, "a", new string('a', 64)));
        Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseAndValidateResponse(bytes, "b", new string('a', 64)));
        Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseAndValidateResponse(bytes, "a", new string('b', 64)));
        Assert.Throws<ArgumentException>(() => EtabsContextWorkerCodec.CanonicalResponseJsonBytes(response with { Quiesced = false }));
    }

    [Fact]
    public void MissingOrChangedWorkerIsRejectedBeforeLaunch()
    {
        var directory = Path.Combine(Path.GetTempPath(), "wp10-package-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try
        {
            byte[] worker = [1, 2, 3];
            File.WriteAllText(Path.Combine(directory, "manifest.json"), JsonSerializer.Serialize(new { worker = new { name = "StructAutomate.EtabsWorker.exe", sha256 = Convert.ToHexStringLower(SHA256.HashData(worker)) } }));
            Assert.Throws<InvalidDataException>(() => EtabsConnectionClient.ValidateWorkerPackage(directory));
            var path = Path.Combine(directory, "StructAutomate.EtabsWorker.exe");
            File.WriteAllBytes(path, worker);
            Assert.Equal(path, EtabsConnectionClient.ValidateWorkerPackage(directory));
            File.WriteAllBytes(path, [1, 2, 4]);
            Assert.Throws<InvalidDataException>(() => EtabsConnectionClient.ValidateWorkerPackage(directory));
            Assert.Equal(0, EtabsConnectionClient.ActiveWorkerCount);
        }
        finally { Directory.Delete(directory, true); }
    }

    [Fact]
    public void SourceIdsControlAdjacencyAndContextNeverInfersSupportFromProximity()
    {
        var session = new EtabsConnectionSession(EtabsContextWorkerCodec.CreateArtifact(Inventory()), "unused");
        Assert.Equal(["column"], session.Neighbours("beam"));
        Assert.DoesNotContain("nearby", session.Neighbours("beam"));
        Assert.Contains("supports=absent", session.Artifact.Inventory.Coverage, StringComparison.Ordinal);
        Assert.Equal(2500, session.Points["p2"].Xmm);
    }

    [Fact]
    public void ChangedCoordinatesAndWrongTargetCannotEnterAcceptedContext()
    {
        var original = EtabsContextWorkerCodec.CreateArtifact(Inventory());
        var changed = original with { Inventory = original.Inventory with { Points = [new("p1", 999, 0, 0), .. original.Inventory.Points.Skip(1)] } };
        Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseAndValidateArtifact(JsonSerializer.SerializeToUtf8Bytes(changed)));
        Assert.Throws<InvalidDataException>(() => EtabsContextWorkerCodec.ParseAndValidateArtifact(EtabsContextWorkerCodec.CanonicalArtifactJsonBytes(original),
            new EtabsProcessTarget(999, original.Inventory.Source.ProcessStartedUtc, "ETABS.exe", new string('a', 64))));
    }

    private static EtabsContextInventory Inventory() => new("request", DateTimeOffset.UtcNow,
        new(123, DateTimeOffset.Parse("2026-09-05T00:00:00Z"), "ETABS.exe", new string('a', 64), "model.EDB", 10, DateTimeOffset.UtcNow,
            new string('b', 64), "23.3.1", false, 6, 6),
        [new("p1", 0, 0, 0), new("p2", 2500, 0, 0), new("p3", 2500, 0, 3000), new("near-p2", 2500, 0, 0), new("p4", 5000, 0, 0)],
        [new("beam", "s", "floor", "p1", "p2", EtabsFrameDesignOrientation.Beam),
         new("column", "s", "floor", "p2", "p3", EtabsFrameDesignOrientation.Column),
         new("nearby", "s", "floor", "near-p2", "p4", EtabsFrameDesignOrientation.Beam)],
        [new("s", "material")], "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent");
}
