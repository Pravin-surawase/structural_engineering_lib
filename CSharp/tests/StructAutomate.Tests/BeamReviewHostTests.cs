using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class BeamReviewHostTests
{
    private static AnalysisSnapshot Snapshot()
    {
        using var stream = typeof(BeamReviewWork).Assembly.GetManifestResourceStream("StructAutomate.ReviewExample.sasnap")!;
        return AnalysisSnapshotTransport.Read(stream).Snapshot!;
    }

    [Fact]
    public void SharedProjectionUsesActualResolvedValuesAndPreservesInvalidEnteredText()
    {
        var snapshot = Snapshot(); var id = snapshot.Members[0].MemberId;
        var resolved = BeamReviewResolver.Resolve(snapshot, [id], BeamReviewInputProjection.Preset(), edits:
        [BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "project", null, "40", 1),
         BeamReviewResolver.Edit("detailing.bars", BeamInputScope.Project, "project", null, "20", 2)]);
        var cells = BeamReviewInputProjection.SharedDesignInputs(snapshot, resolved, BaselineInputSheet.Create(snapshot));
        Assert.Equal("40", Value(cells, id, "nominal_cover_mm"));
        Assert.Equal("20", Value(cells, "catalogue", "longitudinal_diameters_mm"));
        Assert.Equal("60", Value(cells, id, "fire_required_minutes"));
        Assert.Equal("required", Value(cells, id, "fire_requirement").ToLowerInvariant());
        var invalid = BeamReviewResolver.Resolve(snapshot, [id], BeamReviewInputProjection.Preset(), resolved.Ledger,
            BeamReviewResolver.ApplyEdit(resolved.Ledger.Edits, BeamReviewResolver.Edit("design.cover", BeamInputScope.Member, id,
                BeamReviewResolver.ModelBinding(snapshot), "=9+9", 3)));
        cells = BeamReviewInputProjection.SharedDesignInputs(snapshot, invalid, cells);
        Assert.Equal("=9+9", Value(cells, id, "nominal_cover_mm"));
        Assert.Equal(40, invalid.Members[0].Inputs.MemberContexts[0].NominalCoverMm);
        var projection = BeamReviewInputProjection.Inputs(invalid.Ledger);
        Assert.Contains("=9+9", projection.Cast<object>().Select(x => x?.ToString()));
    }

    [Fact]
    public async Task WorkerFreezesInputsAndStoreRoundTripsExactReviewIncludingEffectiveOrigins()
    {
        var snapshot = Snapshot(); var resolved = BeamReviewResolver.Resolve(snapshot, [snapshot.Members[0].MemberId], BeamReviewInputProjection.Preset());
        var root = Path.Combine(Path.GetTempPath(), "beam-review-host-" + Guid.NewGuid().ToString("N"));
        try
        {
            using var work = BeamReviewWork.Start(snapshot, resolved);
            var result = await work.Completion.WaitAsync(TestContext.Current.CancellationToken);
            var store = new BaselineDesignStore(root); var reference = store.SaveReview(result);
            var first = store.ReadReview(reference); var second = store.ReadReview(reference);
            Assert.Equal(ResultFactory.CanonicalJsonBytes(result), ResultFactory.CanonicalJsonBytes(second));
            Assert.Equal(first.Ledger.Revision, second.Ledger.Revision);
            Assert.All(first.Members, x => Assert.Null(x.FullDesign));
            Assert.Equal(BeamReviewAvailability.Example, first.Members[0].Cost!.Availability);
            var state = new OfflineDocumentState("structural-excel-offline/v1", Guid.NewGuid().ToString("N"), true, null, null, 0, null, null,
                Review: new(JsonSerializer.Serialize(resolved)));
            Assert.Equal(state, JsonSerializer.Deserialize<OfflineDocumentState>(JsonSerializer.Serialize(state)));
            Assert.Throws<InvalidDataException>(() => store.ReadReview(reference with { LedgerRevision = "wrong" }));
            File.AppendAllText(Path.Combine(root, reference.FileName), "tamper");
            Assert.Throws<InvalidDataException>(() => store.ReadReview(reference));
        }
        finally { if (Directory.Exists(root)) Directory.Delete(root, true); }
    }

    private static string Value(object[,] cells, string source, string field)
    {
        for (var r = 1; r < cells.GetLength(0); r++)
            if ((string)cells[r, 1] == source && (string)cells[r, 2] == field) return (string)cells[r, 3];
        throw new InvalidOperationException("Missing field " + field);
    }
}
