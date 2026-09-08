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
}
