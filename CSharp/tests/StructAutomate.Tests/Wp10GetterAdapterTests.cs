using System.Collections.ObjectModel;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10GetterAdapterTests
{
    private static readonly DateTimeOffset Deadline = DateTimeOffset.UtcNow.AddMinutes(5);

    [Fact]
    public void FrozenMatrixContainsOnlyExactGettersAndNoVendorReference()
    {
        Assert.Equal(48, EtabsGetterMatrix.Allowed.Count);
        Assert.All(EtabsGetterMatrix.Allowed, item =>
        {
            Assert.Equal(item.Key, item.Value.Operation);
            Assert.StartsWith("ETABSv1.", item.Value.InterfaceType, StringComparison.Ordinal);
            Assert.True(
                item.Value.Member.StartsWith("Get", StringComparison.Ordinal) ||
                item.Value.Member == "FrameForce");
        });
        Assert.Contains("Results.FrameForce", EtabsGetterMatrix.Allowed.Keys);
        Assert.DoesNotContain("FrameObj.GetElm", EtabsGetterMatrix.Allowed.Keys);
        Assert.Equal(64, EtabsGetterMatrix.Sha256.Length);
        Assert.Contains("*.Set*", EtabsGetterMatrix.DeniedMutationFamilies);
        var mutableView = Assert.IsAssignableFrom<IDictionary<string, EtabsGetterDefinition>>(
            EtabsGetterMatrix.Allowed);
        Assert.IsType<ReadOnlyDictionary<string, EtabsGetterDefinition>>(EtabsGetterMatrix.Allowed);
        Assert.Throws<NotSupportedException>(() =>
            mutableView["SapModel.GetPresentUnits"] = EtabsGetterMatrix.Allowed["SapModel.GetPresentUnits"]);
        Assert.Equal(
            [6],
            EtabsGetterMatrix.Allowed["Story.GetStories_2"].NullableStringArrays);
        Assert.DoesNotContain(
            typeof(EtabsGetterAdapter).Assembly.GetReferencedAssemblies(),
            reference => reference.Name?.Contains("ETABS", StringComparison.OrdinalIgnoreCase) is true);
    }

    [Fact]
    public void FakeScalarAndCountedListAreAcceptedWithoutRetry()
    {
        using var fake = new FakeHost((definition, _) => definition.Operation switch
        {
            "SapModel.GetPresentUnits" => new EtabsInvocation(6, []),
            "FrameObj.GetNameList" => new EtabsInvocation(0, [2, new object?[] { "82", "83" }]),
            _ => throw new InvalidOperationException(definition.Operation)
        });
        var adapter = new EtabsGetterAdapter(fake);

        var scalar = adapter.Read("SapModel.GetPresentUnits", [], Deadline, TestContext.Current.CancellationToken);
        var list = adapter.Read("FrameObj.GetNameList", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Completed, scalar.State);
        Assert.Equal(6, scalar.RawCall!.DirectValue);
        Assert.Equal(EtabsGetterState.Completed, list.State);
        Assert.Equal(2, list.RawCall!.Outputs[0]);
        Assert.Equal(2, fake.CallCount);
    }

    [Fact]
    public void FakeFrameForceRetainsAllParallelSameRowArrays()
    {
        object?[] strings = ["a", "b"];
        object?[] doubles = [1d, 2d];
        var arrays = new object?[]
        {
            strings, doubles, strings, doubles, strings, strings, doubles,
            doubles, doubles, doubles, doubles, doubles, doubles
        };
        using var fake = new FakeHost((_, _) => new EtabsInvocation(0, [2, .. arrays]));

        var result = new EtabsGetterAdapter(fake).Read(
            "Results.FrameForce", ["82", 0], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Completed, result.State);
        Assert.Equal(14, result.RawCall!.Outputs.Count);
        Assert.All(result.RawCall.Outputs.Skip(1), output => Assert.Equal(2, Assert.IsType<object?[]>(output).Length));
        Assert.Equal(0, result.RawCall.CsiReturnCode);
        Assert.Equal(1, fake.CallCount);
    }

    [Fact]
    public void NonzeroCsiReturnRejectsAllRawOutput()
    {
        using var fake = new FakeHost((_, _) => new EtabsInvocation(7, [1, new object?[] { "82" }]));

        var result = new EtabsGetterAdapter(fake).Read(
            "FrameObj.GetNameList", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Rejected, result.State);
        Assert.Equal("ETABS.CSI_RETURN_CODE", result.DiagnosticCode);
        Assert.Null(result.RawCall);
        Assert.Equal(1, fake.CallCount);
    }

    [Fact]
    public void UnequalParallelArraysRejectAllRawOutput()
    {
        using var fake = new FakeHost((_, _) => new EtabsInvocation(
            0,
            [2, new object?[] { "DEAD", "LIVE" }, new object?[] { 4 }]));

        var result = new EtabsGetterAdapter(fake).Read(
            "Analyze.GetCaseStatus", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Rejected, result.State);
        Assert.Equal("ETABS.ARRAY_LENGTH_MISMATCH", result.DiagnosticCode);
        Assert.Null(result.RawCall);
    }

    [Fact]
    public void WrongScalarOrArrayElementTypeRejectsAllRawOutput()
    {
        using var scalarFake = new FakeHost((_, _) => new EtabsInvocation("6", []));
        using var arrayFake = new FakeHost((_, _) => new EtabsInvocation(
            0,
            [2, new object?[] { "DEAD", "LIVE" }, new object?[] { 4, "4" }]));

        var scalar = new EtabsGetterAdapter(scalarFake).Read(
            "SapModel.GetPresentUnits", [], Deadline, TestContext.Current.CancellationToken);
        var array = new EtabsGetterAdapter(arrayFake).Read(
            "Analyze.GetCaseStatus", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal("ETABS.RETURN_TYPE_INVALID", scalar.DiagnosticCode);
        Assert.Equal("ETABS.RETURN_TYPE_INVALID", array.DiagnosticCode);
        Assert.Null(scalar.RawCall);
        Assert.Null(array.RawCall);
    }

    [Fact]
    public void ManagedStringArrayRetainsNullReferenceElements()
    {
        using var fake = new FakeHost((_, _) => new EtabsInvocation(
            0,
            [
                0d,
                2,
                new object?[] { "Ground", "First" },
                new object?[] { 0d, 3d },
                new object?[] { 3d, 3d },
                new object?[] { true, false },
                new object?[] { null, "Ground" },
                new object?[] { false, false },
                new object?[] { 0d, 0d },
                new object?[] { 1, 2 }
            ]));

        var result = new EtabsGetterAdapter(fake).Read(
            "Story.GetStories_2", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Completed, result.State);
        Assert.Null(Assert.IsType<object?[]>(result.RawCall!.Outputs[6])[0]);
    }

    [Fact]
    public void TimeoutIsNotRetriedAndReturnsNoPartialCall()
    {
        using var fake = new FakeHost((_, _) => throw new TimeoutException("bounded fake timeout"));

        var result = new EtabsGetterAdapter(fake).Read(
            "SapModel.GetModelIsLocked", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Rejected, result.State);
        Assert.Equal("ETABS.CALL_TIMEOUT", result.DiagnosticCode);
        Assert.Null(result.RawCall);
        Assert.Equal(1, fake.CallCount);
    }

    [Fact]
    public void IdentityDriftRejectsCompletedProviderOutput()
    {
        using var fake = new FakeHost((_, _) => new EtabsInvocation(true, []))
        {
            DriftAfterCall = true
        };

        var result = new EtabsGetterAdapter(fake).Read(
            "SapModel.GetModelIsLocked", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal(EtabsGetterState.Rejected, result.State);
        Assert.Equal("ETABS.IDENTITY_DRIFT", result.DiagnosticCode);
        Assert.Null(result.RawCall);
    }

    [Fact]
    public void ExpiredDeadlineAndUnknownOperationDispatchNothing()
    {
        using var fake = new FakeHost((_, _) => throw new InvalidOperationException("must not dispatch"));
        var adapter = new EtabsGetterAdapter(fake);

        var expired = adapter.Read(
            "SapModel.GetModelIsLocked", [], DateTimeOffset.UtcNow.AddSeconds(-1), TestContext.Current.CancellationToken);
        var denied = adapter.Read(
            "Analyze.RunAnalysis", [], Deadline, TestContext.Current.CancellationToken);

        Assert.Equal("ETABS.CALL_TIMEOUT", expired.DiagnosticCode);
        Assert.Equal("ETABS.CALL_NOT_ALLOWED", denied.DiagnosticCode);
        Assert.Equal(0, fake.CallCount);
    }

    private static EtabsHostIdentity Identity() => new(
        7316,
        DateTimeOffset.Parse("2026-09-04T16:14:10.0327597Z"),
        "ETABS.exe",
        "23.3.1.4563",
        269168,
        new string('d', 64),
        "ETABSv1.dll",
        "ETABSv1, Version=1.0.0.0",
        "2.16.0.0",
        new string('a', 64),
        "ETABSv1.tlb",
        316292,
        new string('e', 64),
        "model.EDB",
        100,
        DateTimeOffset.Parse("2026-09-04T16:23:41.1819254Z"),
        new string('b', 64),
        "23.3.1",
        true,
        6);

    private sealed class FakeHost(
        Func<EtabsGetterDefinition, IReadOnlyList<object?>, EtabsInvocation> invoke) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity { get; private set; } = Wp10GetterAdapterTests.Identity();
        public int CallCount { get; private set; }
        public bool DriftAfterCall { get; init; }

        public EtabsInvocation Invoke(
            EtabsGetterDefinition definition,
            IReadOnlyList<object?> inputs,
            CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            CallCount++;
            var result = invoke(definition, inputs);
            if (DriftAfterCall)
                Identity = Identity with { ModelSha256 = new string('c', 64) };
            return result;
        }

        public void Dispose()
        {
        }
    }
}
