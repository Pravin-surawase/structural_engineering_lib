using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineInputMapperTests
{
    [Fact]
    public void AcceptedInputsPreserveEverySourceVectorAndChangeIdentityWithEngineeringEdits()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var inputs = BaselineDesignTests.FixtureInputs(snapshot);
        var id = snapshot.Members[0].MemberId;
        var mapped = BaselineInputMapper.Map(snapshot, inputs, id);
        Assert.Equal(BaselineDesignState.Supported, mapped.State);
        Assert.Equal(51, mapped.Beam!.ActionRows.Count);
        foreach (var row in mapped.Beam.ActionRows)
        {
            var source = snapshot.ActionRows.Single(x => x.RowId == row.RowId);
            Assert.Equal((source.PKn, source.V2Kn, source.V3Kn, source.TKnm, source.M2Knm, source.M3Knm),
                (row.PKn, row.V2Kn, row.V3Kn, row.TKnm, row.M2Knm, row.M3Knm));
            Assert.Equal(source.SelectionId, row.SelectionId);
        }
        var edited = inputs with { MemberContexts = [inputs.MemberContexts[0] with { NominalCoverMm = 40 }, .. inputs.MemberContexts.Skip(1)] };
        Assert.NotEqual(mapped.Beam.EffectiveInputId, BaselineInputMapper.Map(snapshot, edited, id).Beam!.EffectiveInputId);
        Assert.Equal(mapped.Beam.EffectiveInputId, BaselineInputMapper.Map(snapshot, inputs, id).Beam!.EffectiveInputId);
    }

    [Fact]
    public void MissingAndConflictingEngineeringInputsNeverQualify()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var inputs = BaselineDesignTests.FixtureInputs(snapshot);
        var id = snapshot.Members[0].MemberId;
        BaselineProjectInputs[] cases =
        [
            inputs with { Materials = [] },
            inputs with { MemberContexts = [] },
            inputs with { SelectionRoles = inputs.SelectionRoles.Take(1).ToArray() },
            inputs with { Project = inputs.Project with { ValuesAccepted = false, ProfessionalApprovalAccepted = true } },
            inputs with { Materials = [inputs.Materials[0], inputs.Materials[0]] },
            inputs with { Catalogue = inputs.Catalogue with { Layers = [0] } },
            inputs with { Catalogue = inputs.Catalogue with { LinkSpacingsMm = [double.NaN] } },
            inputs with { MemberContexts = [inputs.MemberContexts[0] with { ScreeningPermitted = false }] }
        ];
        foreach (var invalid in cases)
        {
            var result = BaselineInputMapper.Map(snapshot, invalid, id);
            Assert.Equal(BaselineDesignState.NeedsInput, result.State);
            Assert.Null(result.Beam);
            Assert.NotEmpty(result.Diagnostics[0].FieldOrLocation!);
        }
    }

    [Fact]
    public void UnsupportedSupportAndTamperedCaptureCannotObtainPassingBasis()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var inputs = BaselineDesignTests.FixtureInputs(snapshot);
        var id = snapshot.Members[0].MemberId;
        var continuous = inputs with { MemberContexts = [inputs.MemberContexts[0] with { SupportCondition = BaselineSupportCondition.Continuous }] };
        Assert.Equal(BaselineDesignState.Unsupported, BaselineInputMapper.Map(snapshot, continuous, id).State);
        var tampered = snapshot with { ActionRows = [snapshot.ActionRows[0] with { PKn = 10 }, .. snapshot.ActionRows.Skip(1)] };
        var result = BaselineInputMapper.Map(tampered, inputs, id);
        Assert.Null(result.Beam);
        Assert.Equal("SNAPSHOT.INVALID", result.Diagnostics[0].Code);
    }
}
