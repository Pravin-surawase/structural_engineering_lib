using StructAutomate.Application;
using StructAutomate.Contracts;
using Xunit;

namespace StructAutomate.Tests;

public class ForceAndRankingTests
{
    private static EtabsForceBatch Batch() => new("1.0.0",new("MODEL","revision-1","analysis-1",new string('a',64),"fixture",new(2026,9,3,0,0,0,TimeSpan.Zero)),true,
        ForceUnit.Newton,LengthUnit.Metre,MomentUnit.NewtonMillimetre,
        new Dictionary<string,LocalAxes> { ["F1"] = new(new(1,0,0),new(0,1,0),new(0,0,1)) },
        [new(0,"B1","F1",1.5,"E1",.25,new("ULS1",SelectionKind.Combination,"ULS1"),"ULS1","Max",1,-10000,20000,-30000,4000000,-5000000,6000000),
         new(1,"B1","F1",1.5,"E1",.25,new("ULS1",SelectionKind.Combination,"ULS1"),"ULS1","Min",1,5000,-80000,2000,-7000000,9000000,-1000000)]);

    [Fact]
    public void NormalizeRetainsConcurrentSignedComponentsAndBothStations()
    {
        var result = ForceNormalizer.Normalize(Batch());
        Assert.Equal(2,result.Count);
        var first = result[0];
        Assert.Equal(1500,first.ObjectStationMm);
        Assert.Equal(250,first.ElementStationMm);
        Assert.Equal(new double[] {-10,20,-30,4,-5,6}, new[] {first.PKn,first.V2Kn,first.V3Kn,first.TKnM,first.M2KnM,first.M3KnM});
        Assert.Equal(-80,result[1].V2Kn);
        Assert.Equal(4,first.TKnM); // Not replaced by another row's torsion envelope.
        Assert.NotEqual(first.RowId,result[1].RowId);
        Assert.Equal(first.RowId,ForceNormalizer.Normalize(Batch())[0].RowId);
    }

    [Fact]
    public void ActionIdentityChangesWhenAxesOrRevisionChanges()
    {
        var batch = Batch();
        var original = ForceNormalizer.Normalize(batch)[0].RowId;
        Assert.NotEqual(original, ForceNormalizer.Normalize(batch with { Source = batch.Source with { AnalysisRevision = "analysis-2" } })[0].RowId);
        Assert.NotEqual(original, ForceNormalizer.Normalize(batch with { ObjectAxes = new Dictionary<string,LocalAxes> { ["F1"] = new(new(1,0,0),new(0,0,1),new(0,-1,0)) } })[0].RowId);
    }

    [Fact]
    public void StaleResultsAndLeftHandedAxesCannotBecomeCurrentActions()
    {
        Assert.Throws<InputValidationException>(() => ForceNormalizer.Normalize(Batch() with { IsAnalysisCurrent = false }));
        Assert.Throws<InputValidationException>(() => ForceNormalizer.Normalize(Batch() with { ObjectAxes = new Dictionary<string,LocalAxes> { ["F1"] = new(new(1,0,0),new(0,1,0),new(0,0,-1)) } }));
    }

    private static CheckResult Check(string id, CheckOutcome outcome) => new(id,outcome,"explicit fixture basis",null,null,null,null,null,[]);
    private static EvaluatedCandidate Candidate(string id,double cost,params CheckResult[] checks) => new(id,new string('b',64),"analysis-1",cost,checks);

    [Fact]
    public void MissingServiceabilityCannotWinEvenWhenCheapest()
    {
        var result = CandidateRanker.Rank(new("1.0.0","analysis-1",["flexure","sls"],["A","B","C"],
            [Candidate("A",10,Check("flexure",CheckOutcome.Pass)),
             Candidate("B",20,Check("flexure",CheckOutcome.Pass),Check("sls",CheckOutcome.Fail)),
             Candidate("C",30,Check("flexure",CheckOutcome.Pass),Check("sls",CheckOutcome.Pass))]));
        Assert.Equal("C",result.BestFeasibleCandidateId);
        Assert.False(result.IsCompleteEnumeration);
        Assert.Equal(["A"],result.UnevaluatedCandidateIds);
        Assert.Equal(["B"],result.InfeasibleCandidateIds);
    }

    [Fact]
    public void RequiredCheckCannotBeWaivedWithNotApplicable()
    {
        var result = CandidateRanker.Rank(new("1.0.0","analysis-1",["sls"],["A"],
            [Candidate("A",1,Check("sls",CheckOutcome.NotApplicable))]));
        Assert.Empty(result.FeasibleCandidates);
        Assert.False(result.IsCompleteEnumeration);
    }

    [Fact]
    public void CompleteDomainUsesDeterministicTieBreakAndRejectsStaleCandidate()
    {
        var request = new CandidateRankingRequest("1.0.0","analysis-1",["flexure"],["B","A"],
            [Candidate("B",10,Check("flexure",CheckOutcome.Pass)),Candidate("A",10,Check("flexure",CheckOutcome.Pass))]);
        var result = CandidateRanker.Rank(request);
        Assert.True(result.IsCompleteEnumeration);
        Assert.Equal("A",result.BestFeasibleCandidateId);
        Assert.Throws<InputValidationException>(() => CandidateRanker.Rank(request with { AnalysisRevision = "analysis-2" }));
    }
}
