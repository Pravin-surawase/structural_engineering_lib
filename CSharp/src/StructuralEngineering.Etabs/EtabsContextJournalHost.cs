using System.Text.Json;

namespace StructuralEngineering.Etabs;

/// <summary>Durable before/after records for the context-only whitelist; the broker owns the underlying host.</summary>
internal sealed class EtabsContextJournalHost(IEtabsGetterHost inner, string path, string operationId) : IEtabsGetterHost
{
    private readonly FileStream _stream = new(path, FileMode.CreateNew, FileAccess.Write, FileShare.Read, 4096, FileOptions.WriteThrough);
    private int _sequence;
    public int ReturnedCalls { get; private set; }
    public EtabsHostIdentity Identity => inner.Identity;
    public EtabsHostIdentity InspectIdentity() => inner.InspectIdentity();
    public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
    {
        if (!EtabsContextGetterMatrix.Allowed.TryGetValue(definition.Operation, out var accepted) || accepted != definition)
            throw new InvalidOperationException("The context journal accepts only its fixed getter profile.");
        var call = Guid.NewGuid().ToString("N");
        Write(new
        {
            sequence = ++_sequence,
            operationId,
            call,
            stage = "started",
            method = definition.Operation,
            profile = EtabsContextGetterMatrix.Sha256,
            inputs,
            source = Identity,
            utc = DateTimeOffset.UtcNow
        });
        EtabsOperationBroker.StaMessagePump.Drain();
        var result = inner.Invoke(definition, inputs, token);
        EtabsOperationBroker.StaMessagePump.Drain();
        Write(new
        {
            sequence = ++_sequence,
            operationId,
            call,
            stage = "returned",
            method = definition.Operation,
            profile = EtabsContextGetterMatrix.Sha256,
            result,
            utc = DateTimeOffset.UtcNow
        });
        ReturnedCalls++;
        return result;
    }
    private void Write(object record)
    {
        _stream.Write(JsonSerializer.SerializeToUtf8Bytes(record));
        _stream.WriteByte((byte)'\n');
        _stream.Flush(true);
    }
    public void Dispose() => _stream.Dispose();
}
