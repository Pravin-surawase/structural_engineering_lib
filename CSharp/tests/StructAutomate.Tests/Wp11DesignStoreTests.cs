using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class Wp11DesignStoreTests
{
    [Fact]
    public async Task StoreAndWorkFreezeReplayAndRejectTampering()
    {
        var snapshot = Snapshot(); var inputs = Inputs(snapshot); var members = snapshot.Members.Select(x => x.MemberId).ToArray();
        var root = Path.Combine(Path.GetTempPath(), "wp11-store-" + Guid.NewGuid().ToString("N"));
        try
        {
            var store = new BaselineDesignStore(root); var request = BaselineReplay.Request(snapshot, inputs, members, new(4));
            var reference = store.SaveRequest(request); var reread = store.ReadRequest(reference);
            Assert.Equal(BaselineReplay.Serialize(request), BaselineReplay.Serialize(reread)); Assert.Equal(reference, store.SaveRequest(request));
            var progress = new List<(int Completed, int Total, string MemberId)>();
            using var work1 = BaselineDesignWork.Start(snapshot, inputs, members, new(4), new InlineProgress(progress));
            using var work2 = BaselineDesignWork.Start(snapshot, inputs, members, new(4));
            Assert.NotEqual(work1.RequestId, work2.RequestId); Assert.Equal(BaselineReplay.Serialize(work1.Request), BaselineReplay.Serialize(work2.Request));
            var originalFirst = members[0]; members[0] = "mutated-caller-selection";
            Assert.Equal(originalFirst, work1.Request.MemberIds[0]);
            var result = await work1.Completion; Assert.Equal(members.Length, result.Members.Count); Assert.Equal(members.Length, progress.Count);
            var resultRef = store.SaveResult(result, reference); Assert.Equal(result.RequestId, store.ReadResult(resultRef).RequestId);
            Assert.All(result.Members, member => Assert.Equal(BaselineRunState.Complete, member.State));
            Assert.Equal(originalFirst, result.Members[0].MemberId);
            Assert.Throws<InvalidDataException>(() => store.SaveResult(result with { Options = new(2) }, reference));
            Assert.Throws<InvalidDataException>(() => store.SaveResult(result with { Members = result.Members.Reverse().ToArray() }, reference));
            Assert.Throws<InvalidDataException>(() => store.SaveResult(result with { AcceptedInputs = inputs with { Project = inputs.Project with { RevisionId = "wrong" } } }, reference));
            Assert.Throws<InvalidDataException>(() => store.SaveResult(result with { Members = result.Members.Select(m => m with { EngineRevisionId = "wrong" }).ToArray() }, reference));
            work2.Cancel();
            try { _ = await work2.Completion; } catch (OperationCanceledException) { }
            work2.Dispose(); work2.Dispose(); work2.Cancel();
            File.AppendAllText(Path.Combine(root, reference.FileName), "x");
            Assert.Throws<InvalidDataException>(() => store.ReadRequest(reference));
            Assert.Throws<InvalidDataException>(() => store.ReadResult(resultRef));
            Assert.Throws<FileNotFoundException>(() => store.ReadResult(resultRef with { FileName = "missing.json" }));
            Assert.Throws<FileNotFoundException>(() => store.ReadResult(resultRef with { RequestFileSha256 = new string('0', 64) }));
        }
        finally { if (Directory.Exists(root)) Directory.Delete(root, true); }
    }

    private static AnalysisSnapshot Snapshot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "CSharp", "tests", "StructuralEngineering.Tests", "Fixtures", "wp11-owned-snapshot.sasnap");
            if (File.Exists(path)) { using var stream = File.OpenRead(path); return Assert.IsType<AnalysisSnapshot>(AnalysisSnapshotTransport.Read(stream).Snapshot); }
            directory = directory.Parent;
        }
        throw new FileNotFoundException("WP11 owned snapshot fixture was not found.");
    }

    private static BaselineProjectInputs Inputs(AnalysisSnapshot snapshot) => new(
        new("wp11-owned-reference", "fixture-engineering-v1", "owned_fixture_engineering_definition", "wp11-owned-baseline-fixture/v1", true, false),
        [new("material:PF9_CONCRETE", 25, 500, 415, 200000)],
        new("reference-catalogue-v1", [12, 16, 20], [8, 10], [250, 200, 150, 100], [2, 3, 4, 6], [1, 2], [6000, 12000], 1000),
        snapshot.Members.Select((member, index) => { var length = 4000 + 250 * index; return new BaselineMemberContext(member.MemberId, member.ObjectId, "span:" + member.MemberId, BaselineSupportCondition.SimplySupported, 500, length - 500, 0, length, length, -465, length + 465, 35, 20, "Mild", false, true, true, true, true, "support-definition-v1", new(BaselineFireRequirement.NotRequired, "owned fixture"), new([0, length], "owned fixture")); }).ToArray(),
        [new("selection-case:WP11_ULS", BaselineSelectionRole.Uls), new("selection-case:WP11_SLS", BaselineSelectionRole.SlsTotal), new("selection-case:WP11_SUSTAINED", BaselineSelectionRole.SlsSustained)]);
    private sealed class InlineProgress(List<(int Completed, int Total, string MemberId)> values) : IProgress<(int Completed, int Total, string MemberId)>
    { public void Report((int Completed, int Total, string MemberId) value) => values.Add(value); }
}
