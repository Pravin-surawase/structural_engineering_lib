using System.Reflection;
using System.Security.Cryptography;
using System.Text;

namespace StructuralEngineering.Etabs;

public sealed record EtabsApiCapability(string Area, string InterfaceType, string Member, string Effect);
public sealed record EtabsApiParameter(string Name, string Type, string Direction, bool Optional);
public sealed record EtabsApiMethod(string Signature, string ReturnType, IReadOnlyList<EtabsApiParameter> Parameters);
public sealed record EtabsApiEnumValue(string Name, string Value);
public sealed record EtabsApiEnum(string Type, IReadOnlyList<EtabsApiEnumValue> Values);
public sealed record EtabsApiGetterBinding(string Profile, string Operation, string ExpectedSignature, bool Matches);
public sealed record EtabsApiMemberDiscovery(EtabsApiCapability Capability, string Status,
    IReadOnlyList<EtabsApiMethod> Methods, IReadOnlyList<EtabsApiGetterBinding> RegisteredGetters);
public sealed record EtabsApiInventory(string SchemaVersion, string CatalogueSha256, string AssemblyIdentity,
    string EvidenceScope, int TargetMethodsInvoked, IReadOnlyList<EtabsApiMemberDiscovery> Members,
    IReadOnlyList<EtabsApiEnum> Enums);

/// <summary>Metadata discovery only. This catalogue grants no permission to invoke a target method.</summary>
public static class EtabsApiDiscovery
{
    public const string SchemaVersion = "structural.etabs_api_inventory/v1";
    public static IReadOnlyList<EtabsApiCapability> Capabilities { get; } = CreateCatalogue();

    public static EtabsApiInventory Inspect(Assembly assembly, IReadOnlyList<EtabsApiCapability>? capabilities = null)
    {
        ArgumentNullException.ThrowIfNull(assembly);
        var selected = (capabilities ?? Capabilities).OrderBy(x => x.InterfaceType, StringComparer.Ordinal)
            .ThenBy(x => x.Member, StringComparer.Ordinal).ToArray();
        if (selected.Any(x => string.IsNullOrWhiteSpace(x.InterfaceType) || string.IsNullOrWhiteSpace(x.Member)) ||
            selected.Select(x => (x.InterfaceType, x.Member)).Distinct().Count() != selected.Length)
            throw new ArgumentException("Discovery requires unique, explicit interface/member identities.", nameof(capabilities));

        var profiles = new (string Name, IReadOnlyDictionary<string, EtabsGetterDefinition> Definitions)[]
        {
            ("retained", EtabsGetterMatrix.Allowed), ("context", EtabsContextGetterMatrix.Allowed),
            ("forces", EtabsForceGetterMatrix.Allowed), ("bulk", EtabsBulkGetterMatrix.Allowed),
            ("group", EtabsGroupGetterMatrix.Allowed)
        };
        var enums = new Dictionary<string, EtabsApiEnum>(StringComparer.Ordinal);
        var members = new List<EtabsApiMemberDiscovery>();
        foreach (var capability in selected)
        {
            var type = assembly.GetType(capability.InterfaceType, throwOnError: false);
            var methods = (type?.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static) ?? [])
                .Where(x => x.Name == capability.Member).OrderBy(x => x.ToString(), StringComparer.Ordinal).ToArray();
            var signatures = methods.Select(x => x.ToString()!).ToHashSet(StringComparer.Ordinal);
            var bindings = profiles.SelectMany(profile => profile.Definitions.Values
                .Where(x => x.InterfaceType == capability.InterfaceType && x.Member == capability.Member)
                .Select(x => new EtabsApiGetterBinding(profile.Name, x.Operation, x.ManagedSignature,
                    signatures.Contains(x.ManagedSignature)))).ToArray();
            var status = methods.Length == 0 ? "missing" : bindings.Length == 0 ? "available_unqualified" :
                bindings.Any(x => !x.Matches) ? "registered_signature_mismatch" : "registered_signature_match";
            var descriptions = methods.Select(method =>
            {
                AddEnum(method.ReturnType);
                var parameters = method.GetParameters().Select(parameter =>
                {
                    AddEnum(parameter.ParameterType);
                    return new EtabsApiParameter(parameter.Name ?? string.Empty, TypeName(parameter.ParameterType),
                        parameter.IsOut ? "out" : parameter.ParameterType.IsByRef ? "ref" : "in", parameter.IsOptional);
                }).ToArray();
                return new EtabsApiMethod(method.ToString()!, TypeName(method.ReturnType), parameters);
            }).ToArray();
            members.Add(new(capability, status, descriptions, bindings));
        }
        var catalogueBytes = Encoding.UTF8.GetBytes(string.Join('\n', selected.Select(x =>
            string.Join('|', x.Area, x.InterfaceType, x.Member, x.Effect))));
        return new(SchemaVersion, Convert.ToHexStringLower(SHA256.HashData(catalogueBytes)),
            assembly.FullName ?? assembly.GetName().Name ?? string.Empty, "static_metadata_only;not_live_qualification", 0,
            members, enums.Values.OrderBy(x => x.Type, StringComparer.Ordinal).ToArray());

        void AddEnum(Type enumType)
        {
            while (enumType.HasElementType) enumType = enumType.GetElementType()!;
            if (!enumType.IsEnum || enums.ContainsKey(TypeName(enumType))) return;
            enums.Add(TypeName(enumType), new(TypeName(enumType), enumType.GetFields(BindingFlags.Public | BindingFlags.Static)
                .OrderBy(x => x.Name, StringComparer.Ordinal).Select(field => new EtabsApiEnumValue(field.Name,
                    Convert.ToString(field.GetRawConstantValue(), System.Globalization.CultureInfo.InvariantCulture)!)).ToArray()));
        }
    }

    private static string TypeName(Type type) => type.FullName ?? type.Name;

    private static IReadOnlyList<EtabsApiCapability> CreateCatalogue()
    {
        var result = new List<EtabsApiCapability>();
        Add("source", "cHelper", "attachment", "GetObjectProcess");
        Add("source", "cSapModel", "read", "GetVersion GetModelFilename GetModelIsLocked GetPresentUnits GetPresentUnits_2 GetDatabaseUnits");
        Add("source", "cSapModel", "write", "SetPresentUnits SetModelIsLocked");
        Add("beam_topology", "cFrameObj", "read", "GetAllFrames GetDesignOrientation GetPoints GetElm GetSupports GetMaterialOverwrite GetOutputStations GetInsertionPoint_1 GetEndLengthOffset GetReleases GetTransformationMatrix GetModifiers GetSection");
        Add("candidate_update", "cFrameObj", "write", "SetSection");
        Add("connectivity", "cPointObj", "read", "GetAllPoints GetConnectivity GetRestraint");
        Add("support_geometry", "cAreaObj", "read", "GetAllAreas GetPoints GetProperty");
        Add("support_geometry", "cPropArea", "read", "GetWall GetSlab");
        Add("section_material", "cPropFrame", "read", "GetTypeOAPI GetRectangle GetTee GetTee_1 GetMaterial GetRebarBeam GetSectProps");
        Add("section_material", "cPropMaterial", "read", "GetOConcrete GetORebar GetTypeOAPI");
        Add("loading", "cCombo", "read", "GetNameList GetCaseList GetCaseList_1 GetTypeCombo");
        Add("loading", "cLoadCases", "read", "GetNameList GetTypeOAPI");
        Add("analysis", "cAnalyze", "read", "GetCaseStatus GetRunCaseFlag");
        Add("analysis", "cAnalyze", "write", "RunAnalysis");
        Add("forces", "cAnalysisResults", "read", "FrameForce");
        Add("forces", "cAnalysisResultsSetup", "read", "GetCaseSelectedForOutput GetComboSelectedForOutput");
        Add("forces", "cAnalysisResultsSetup", "write", "SetCaseSelectedForOutput SetComboSelectedForOutput");
        Add("scope", "cGroup", "read", "GetAssignments GetNameList");
        Add("bulk_tables", "cDatabaseTables", "read", "GetAvailableTables GetAllFieldsInTable GetTableForDisplayArray GetTableForEditingArray");
        Add("design_reference", "cDesignConcrete", "read", "GetCode GetResultsAvailable GetSummaryResultsBeam GetDesignSection GetComboStrength");
        Add("design_reference", "cDesignConcrete", "write", "SetComboStrength StartDesign");
        Add("candidate_file", "cFile", "write", "Save OpenFile");
        return result.AsReadOnly();

        void Add(string area, string type, string effect, string names)
        {
            foreach (var name in names.Split(' ', StringSplitOptions.RemoveEmptyEntries))
                result.Add(new(area, "ETABSv1." + type, name, effect));
        }
    }
}
