using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests
{
    public sealed class EtabsApiDiscoveryTests
    {
        [Fact]
        public void DiscoveryPreservesReturnAndParameterSemanticsWithoutCallingTheTarget()
        {
            var capabilities = new[]
            {
                Candidate(typeof(DiscoveryFixture), nameof(DiscoveryFixture.Available)),
                Candidate(typeof(DiscoveryFixture), nameof(DiscoveryFixture.Path)),
                Candidate(typeof(DiscoveryFixture), nameof(DiscoveryFixture.Read))
            };
            var result = EtabsApiDiscovery.Inspect(typeof(DiscoveryFixture).Assembly, capabilities);
            Assert.Equal(0, result.TargetMethodsInvoked);
            Assert.Contains("not_live_qualification", result.EvidenceScope, StringComparison.Ordinal);
            Assert.All(result.Members, member => Assert.Equal("available_unqualified", member.Status));
            Assert.Equal("System.Boolean", Method("Available").ReturnType);
            Assert.Equal("System.String", Method("Path").ReturnType);
            var read = Method("Read");
            Assert.Equal("System.Int32", read.ReturnType);
            Assert.Equal("ref", read.Parameters[0].Direction);
            Assert.Equal("out", read.Parameters[1].Direction);
            Assert.True(read.Parameters[2].Optional);
            Assert.Equal("2", Assert.Single(Assert.Single(result.Enums).Values, x => x.Name == "Group").Value);

            EtabsApiMethod Method(string name) => Assert.Single(Assert.Single(result.Members,
                x => x.Capability.Member == name).Methods);
        }

        [Fact]
        public void MissingGetterDoesNotBecomeAvailableBecauseItsSetterExists()
        {
            var result = EtabsApiDiscovery.Inspect(typeof(DiscoveryFixture).Assembly,
                [Candidate(typeof(DiscoveryFixture), "GetComboStrength"), Candidate(typeof(DiscoveryFixture), "SetComboStrength")]);
            Assert.Equal("missing", Assert.Single(result.Members, x => x.Capability.Member == "GetComboStrength").Status);
            Assert.Empty(Assert.Single(result.Members, x => x.Capability.Member == "GetComboStrength").Methods);
            Assert.Equal("available_unqualified", Assert.Single(result.Members, x => x.Capability.Member == "SetComboStrength").Status);
        }

        [Fact]
        public void MaintainedGetterSignaturesDistinguishMatchFromDrift()
        {
            var result = EtabsApiDiscovery.Inspect(typeof(ETABSv1.cSapModel).Assembly,
                [Candidate(typeof(ETABSv1.cSapModel), "GetModelFilename"), Candidate(typeof(ETABSv1.cSapModel), "GetModelIsLocked")]);
            var matched = Assert.Single(result.Members, x => x.Capability.Member == "GetModelFilename");
            Assert.Equal("registered_signature_match", matched.Status);
            Assert.NotEmpty(matched.RegisteredGetters);
            Assert.All(matched.RegisteredGetters, x => Assert.True(x.Matches));
            var changed = Assert.Single(result.Members, x => x.Capability.Member == "GetModelIsLocked");
            Assert.Equal("registered_signature_mismatch", changed.Status);
            Assert.All(changed.RegisteredGetters, x => Assert.False(x.Matches));
        }

        [Fact]
        public void CatalogueIdentityIsOrderIndependentAndChangesWithDeclaredScope()
        {
            var first = Candidate(typeof(DiscoveryFixture), "Available");
            var second = Candidate(typeof(DiscoveryFixture), "Read");
            var assembly = typeof(DiscoveryFixture).Assembly;
            Assert.Equal(EtabsApiDiscovery.Inspect(assembly, [first, second]).CatalogueSha256,
                EtabsApiDiscovery.Inspect(assembly, [second, first]).CatalogueSha256);
            Assert.NotEqual(EtabsApiDiscovery.Inspect(assembly, [first]).CatalogueSha256,
                EtabsApiDiscovery.Inspect(assembly, [first with { Effect = "write" }]).CatalogueSha256);
            Assert.Throws<ArgumentException>(() => EtabsApiDiscovery.Inspect(assembly, [first, first]));
        }

        [Fact]
        public void FullDiscoveryKeepsUnknownEffectsAndMissingCandidatesWithoutCallingOrAdmittingThem()
        {
            var result = EtabsApiDiscovery.InspectAll(typeof(ETABSv1.cUnmapped).Assembly);
            var unknown = Assert.Single(result.Members, x => x.Capability.InterfaceType == typeof(ETABSv1.cUnmapped).FullName);
            Assert.Equal("GetAndChangeState", unknown.Capability.Member);
            Assert.Equal("unclassified", unknown.Capability.Effect);
            Assert.Equal("available_unqualified", unknown.Status);
            Assert.Empty(unknown.RegisteredGetters);
            Assert.DoesNotContain(result.Members, x => x.Capability.Member == "get_Label");
            Assert.Equal("missing", Assert.Single(result.Members, x => x.Capability.Member == "GetComboStrength").Status);
            Assert.Equal(0, result.TargetMethodsInvoked);
            Assert.Equal("application_lifecycle", Assert.Single(result.Members, x => x.Capability.Member == "ApplicationExit").Capability.Effect);
            Assert.Equal("external_file_write", Assert.Single(result.Members, x => x.Capability.Member == "GetTableForDisplayCSVFile").Capability.Effect);
            var registered = Assert.Single(result.Members, x => x.Capability.InterfaceType == typeof(ETABSv1.cFrameObj).FullName && x.Capability.Member == "GetNameList");
            Assert.Equal("registered_getter", registered.Capability.Area);
            Assert.Equal("read", registered.Capability.Effect);
            Assert.Equal("registered_signature_match", registered.Status);
        }

        [Fact]
        public void InspectionOnlyGetterIsReportedAsRegisteredWithItsExactSignature()
        {
            var result = EtabsApiDiscovery.Inspect(typeof(ETABSv1.cFrameObj).Assembly,
                [Candidate(typeof(ETABSv1.cFrameObj), "Count")]);
            var member = Assert.Single(result.Members);
            Assert.Equal("registered_signature_match", member.Status);
            var binding = Assert.Single(member.RegisteredGetters);
            Assert.Equal("inspection", binding.Profile);
            Assert.Equal("FrameObj.Count", binding.Operation);
            Assert.True(binding.Matches);
        }

        private static EtabsApiCapability Candidate(Type type, string method) => new("test", type.FullName!, method, "read");
    }

    public enum DiscoveryScope { Object = 0, Group = 2 }

    public sealed class DiscoveryFixture
    {
        public DiscoveryFixture() => throw new InvalidOperationException("Discovery must not construct the target.");
        public bool Available() => throw new InvalidOperationException("Discovery must not call the target.");
        public string Path() => throw new InvalidOperationException("Discovery must not call the target.");
        public int Read(ref DiscoveryScope scope, out double[] values, bool include = true) => throw new InvalidOperationException("Discovery must not call the target.");
        public int SetComboStrength(string name, bool selected) => throw new InvalidOperationException("Discovery must not call the target.");
    }
}

namespace ETABSv1
{
    // Deliberate fake SDK: filename matches the real registered signature; lock return type does not.
    public interface cSapModel
    {
        string GetModelFilename(bool IncludePath);
        int GetModelIsLocked();
    }

    public interface cFrameObj
    {
        int Count(string MyType);
        int GetNameList(ref int NumberNames, ref string[] MyName);
    }

    public interface cUnmapped
    {
        string Label { get; }
        int GetAndChangeState();
    }
}
