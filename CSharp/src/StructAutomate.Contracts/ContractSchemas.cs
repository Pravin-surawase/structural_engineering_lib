using System.Text.Json.Nodes;
using System.Text.Json.Schema;

namespace StructAutomate.Contracts;

public static class ContractSchemas
{
    public static IReadOnlyDictionary<string, JsonNode> ExportRequests()
    {
        Type[] types = [typeof(EtabsForceBatch), typeof(ReinforcementGeometryRequest), typeof(QuantityRequest), typeof(BeamLineRequest), typeof(CandidateRankingRequest)];
        var result = new Dictionary<string, JsonNode>();
        var options = ContractJson.CreateOptions();
        foreach (var type in types)
        {
            var schema = options.GetJsonSchemaAsNode(type, new JsonSchemaExporterOptions { TreatNullObliviousAsNonNullable = true });
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema";
            schema["title"] = type.Name;
            schema["properties"]!["schemaVersion"]!["const"] = ContractJson.SchemaVersion;
            result[type.Name] = schema;
        }
        return result;
    }
}
