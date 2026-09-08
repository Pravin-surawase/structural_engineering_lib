using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public class Wp11InputSheetTests
{
    [Fact]
    public void CompleteOwnedLikeRowsReadDeterministicallyAcrossOneBasedMatrices()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot);
        var oneBased = (object[,])Array.CreateInstance(typeof(object),
            [cells.GetLength(0), cells.GetLength(1)], [1, 1]);
        for (var r = 0; r < cells.GetLength(0); r++) for (var c = 0; c < cells.GetLength(1); c++) oneBased[r + 1, c + 1] = cells[r, c];
        var first = BaselineInputSheet.Read(snapshot, cells);
        var second = BaselineInputSheet.Read(snapshot, oneBased);
        Assert.Empty(first.Issues); Assert.Equal(first.Revision, second.Revision);
        Assert.True(first.Inputs.Project.ValuesAccepted); Assert.False(first.Inputs.Project.ProfessionalApprovalAccepted);
        Assert.Equal(snapshot.Members.Count, first.MemberIds.Count);
        var designed = BaselineDesignOperations.Design(snapshot, first.Inputs, first.MemberIds, cancellationToken: TestContext.Current.CancellationToken);
        Assert.All(designed.Members, member => Assert.Equal(BaselineRunState.Complete, member.State));
    }

    [Fact]
    public void MissingSelectedMemberIsReportedWithoutDiscardingCompletePeer()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot);
        Set(cells, "Member", snapshot.Members[1].MemberId, "nominal_cover_mm", "");
        var result = BaselineInputSheet.Read(snapshot, cells);
        Assert.Contains(result.Issues, issue => issue.Contains(snapshot.Members[1].MemberId, StringComparison.Ordinal));
        Assert.Contains(snapshot.Members[1].MemberId, result.MemberIds);
        Assert.Contains(snapshot.Members[0].MemberId, result.MemberIds);
        var designed = BaselineDesignOperations.Design(snapshot, result.Inputs, result.MemberIds, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Equal(BaselineRunState.Complete, designed.Members[0].State);
        Assert.Equal(BaselineRunState.NeedsInput, designed.Members[1].State);
        Assert.Equal(BaselineRunState.Complete, designed.Members[2].State);
        Assert.Contains(result.Issues, issue => issue.StartsWith("Design Inputs!D", StringComparison.Ordinal));
    }

    [Fact]
    public void BlankIsNotZeroAndImmutableSourceFactsCannotBeEdited()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot);
        Set(cells, "Member", snapshot.Members[0].MemberId, "left_support_face_x_mm", "0");
        Assert.DoesNotContain("left_support_face_x_mm is required", BaselineInputSheet.Read(snapshot, cells).Issues);
        Set(cells, "Source", snapshot.Members[0].MemberId, "source_object_id", "tampered");
        Assert.Contains("snapshot source fact changed", Assert.Throws<ArgumentException>(() => BaselineInputSheet.Read(snapshot, cells)).Message);
    }

    [Fact]
    public void SnakeCaseAndOriginNormalizationAreExplicit()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot);
        Set(cells, "Catalogue", "catalogue", "revision_id", "engineer-catalogue-r2");
        var normalized = BaselineInputSheet.NormalizeOrigins(snapshot, cells);
        Assert.Equal("engineer input — accepted revision", normalized[5, 5]);
        Assert.Empty(BaselineInputSheet.Read(snapshot, cells).Issues);
    }

    [Theory]
    [InlineData("cracking_harmful")]
    [InlineData("ordinary_seismic")]
    [InlineData("screening_permitted")]
    [InlineData("horizontal")]
    [InlineData("top_mapping_normal")]
    public void MissingRequiredBooleanKeepsSelectedMemberButOmitsItsContext(string field)
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot); var member = snapshot.Members[1];
        Set(cells, "Member", member.MemberId, field, "");
        var read = BaselineInputSheet.Read(snapshot, cells); var result = BaselineDesignOperations.Design(snapshot, read.Inputs, read.MemberIds, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Contains(member.MemberId, read.MemberIds); Assert.DoesNotContain(read.Inputs.MemberContexts, x => x.MemberId == member.MemberId);
        Assert.Equal(BaselineRunState.NeedsInput, result.Members.Single(x => x.MemberId == member.MemberId).State);
        Assert.Equal(BaselineRunState.Complete, result.Members.Single(x => x.MemberId == snapshot.Members[0].MemberId).State);
    }

    [Fact]
    public void BlankFireIsUnspecifiedAndNeedsInputRatherThanUnsupported()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot); var member = snapshot.Members[0];
        Set(cells, "Member", member.MemberId, "fire_requirement", ""); Set(cells, "Member", member.MemberId, "fire_decision_reference", "");
        var read = BaselineInputSheet.Read(snapshot, cells); var context = Assert.Single(read.Inputs.MemberContexts, x => x.MemberId == member.MemberId);
        Assert.Equal(BaselineFireRequirement.Unspecified, context.FireBasis!.Requirement);
        var state = BaselineDesignOperations.Design(snapshot, read.Inputs, read.MemberIds, cancellationToken: TestContext.Current.CancellationToken).Members[0].State;
        Assert.Equal(BaselineRunState.NeedsInput, state);
    }

    [Theory]
    [InlineData("support_condition", "not-a-support")]
    [InlineData("fire_requirement", "not-a-fire")]
    public void InvalidMemberEnumsNeverQualify(string field, string value)
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot); Set(cells, "Member", snapshot.Members[0].MemberId, field, value);
        var read = BaselineInputSheet.Read(snapshot, cells); var outcome = BaselineDesignOperations.Design(snapshot, read.Inputs, read.MemberIds, cancellationToken: TestContext.Current.CancellationToken);
        Assert.NotEqual(BaselineRunState.Complete, outcome.Members[0].State);
    }

    [Fact]
    public void InvalidRoleNeverQualifies()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot); Set(cells, "Role", snapshot.ActionRows[0].SelectionId, "role", "not-a-role");
        var read = BaselineInputSheet.Read(snapshot, cells); var outcome = BaselineDesignOperations.Design(snapshot, read.Inputs, read.MemberIds, cancellationToken: TestContext.Current.CancellationToken);
        Assert.Contains(read.Issues, x => x.Contains("Role", StringComparison.Ordinal)); Assert.All(outcome.Members, x => Assert.NotEqual(BaselineRunState.Complete, x.State));
    }

    [Fact]
    public void DistinctOmittedFieldsInOneMemberGroupChangeRevisionEvenWhenBothNeedInput()
    {
        var snapshot = Snapshot(); var first = BaselineInputSheet.Create(snapshot); var second = BaselineInputSheet.Create(snapshot); Fill(first, snapshot); Fill(second, snapshot);
        Set(first, "Member", snapshot.Members[0].MemberId, "nominal_cover_mm", ""); Set(second, "Member", snapshot.Members[0].MemberId, "maximum_aggregate_size_mm", "");
        var a = BaselineInputSheet.Read(snapshot, first); var b = BaselineInputSheet.Read(snapshot, second);
        Assert.NotEqual(a.Revision, b.Revision); Assert.Contains(a.Issues, x => x.Contains("nominal_cover_mm", StringComparison.Ordinal)); Assert.Contains(b.Issues, x => x.Contains("maximum_aggregate_size_mm", StringComparison.Ordinal));
    }

    [Fact]
    public void OneBasedOriginsNormalizeForWriterAndPreserveImmutableSourceOrigin()
    {
        var snapshot = Snapshot(); var cells = BaselineInputSheet.Create(snapshot); Fill(cells, snapshot); Set(cells, "Catalogue", "catalogue", "revision_id", "edited-r2");
        var one = (object[,])Array.CreateInstance(typeof(object), [cells.GetLength(0), cells.GetLength(1)], [1, 1]); for (var r = 0; r < cells.GetLength(0); r++) for (var c = 0; c < cells.GetLength(1); c++) one[r + 1, c + 1] = cells[r, c];
        var normalized = BaselineInputSheet.NormalizeOrigins(snapshot, one);
        Assert.Equal(0, normalized.GetLowerBound(0)); Assert.Equal(0, normalized.GetLowerBound(1)); Assert.Equal("engineer input — accepted revision", normalized[5, 5]);
        var sourceRows = Enumerable.Range(1, normalized.GetLength(0) - 1).Where(r => (string)normalized[r, 0] == "Source").ToArray(); Assert.NotEmpty(sourceRows); Assert.All(sourceRows, r => Assert.Equal("snapshot read-only", normalized[r, 5]));
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
        throw new FileNotFoundException("Owned WP11 snapshot fixture is required.");
    }
    private static void Fill(object[,] cells, AnalysisSnapshot snapshot)
    {
        Set(cells, "Project", "project", "project_id", "wp11-sheet-test"); Set(cells, "Project", "project", "revision_id", "r1"); Set(cells, "Project", "project", "origin", "test"); Set(cells, "Project", "project", "evidence_reference", "test-evidence");
        foreach (var material in snapshot.Materials) { Set(cells, "Material", material.MaterialId, "concrete_strength_n_per_mm2", "25"); Set(cells, "Material", material.MaterialId, "steel_yield_strength_n_per_mm2", "500"); Set(cells, "Material", material.MaterialId, "link_steel_yield_strength_n_per_mm2", "415"); Set(cells, "Material", material.MaterialId, "steel_modulus_n_per_mm2", "200000"); }
        var actionSelections = snapshot.ActionRows.Select(row => row.SelectionId).ToHashSet(StringComparer.Ordinal); foreach (var selection in snapshot.ResultSelections.Where(selection => actionSelections.Contains(selection.SelectionId))) Set(cells, "Role", selection.SelectionId, "role", selection.SelectionId.Contains("SUSTAINED", StringComparison.OrdinalIgnoreCase) ? "sls_sustained" : selection.SelectionId.Contains("SLS", StringComparison.OrdinalIgnoreCase) ? "sls_total" : "uls");
        foreach (var pair in snapshot.Members.Select((member, index) => (member, index))) { var m = pair.member; var length = 4000 + 250 * pair.index; Set(cells, "Member", m.MemberId, "physical_span_id", "span:" + m.MemberId); Set(cells, "Member", m.MemberId, "support_condition", "simply_supported"); foreach (var field in new[] { "left_support_face_x_mm", "right_support_face_x_mm", "left_support_centre_x_mm", "right_support_centre_x_mm", "effective_span_mm", "anchorage_start_x_mm", "anchorage_end_x_mm", "nominal_cover_mm", "maximum_aggregate_size_mm" }) Set(cells, "Member", m.MemberId, field, field switch { "left_support_face_x_mm" => "500", "right_support_face_x_mm" => (length - 500).ToString(), "left_support_centre_x_mm" => "0", "right_support_centre_x_mm" => length.ToString(), "effective_span_mm" => length.ToString(), "anchorage_start_x_mm" => "-465", "anchorage_end_x_mm" => (length + 465).ToString(), "nominal_cover_mm" => "35", _ => "20" }); Set(cells, "Member", m.MemberId, "exposure", "mild"); foreach (var field in new[] { "cracking_harmful", "ordinary_seismic", "screening_permitted", "horizontal", "top_mapping_normal" }) Set(cells, "Member", m.MemberId, field, field == "cracking_harmful" ? "false" : "true"); Set(cells, "Member", m.MemberId, "evidence_revision_id", "support-r1"); Set(cells, "Member", m.MemberId, "fire_requirement", "not_required"); Set(cells, "Member", m.MemberId, "fire_decision_reference", "test-no-fire"); Set(cells, "Member", m.MemberId, "lateral_restraint_positions_mm", "0," + length); Set(cells, "Member", m.MemberId, "lateral_restraint_evidence_reference", "test-restraints"); }
    }
    private static void Set(object[,] cells, string category, string id, string field, string value) { for (var r = 1; r < cells.GetLength(0); r++) if ((string)cells[r, 0] == category && (string)cells[r, 1] == id && (string)cells[r, 2] == field) { cells[r, 3] = value; return; } throw new InvalidOperationException(field); }
}
