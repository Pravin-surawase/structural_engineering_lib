using System.Buffers;
using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

public static partial class AnalysisSnapshotCodec
{
    internal static EtabsSnapshotResult RejectTransport(string message) => Rejected("INPUT.SCHEMA", "$", message,
        "Restore a complete supported snapshot within the transport limits.");

    internal static EtabsSnapshotResult ParseAndValidateStream(Stream source, int maximumBytes)
    {
        try
        {
            using var bounded = new AnalysisSnapshotTransport.LimitedStream(source, maximumBytes);
            using var checkedJson = new DuplicateCheckingStream(bounded);
            var snapshot = JsonSerializer.Deserialize<AnalysisSnapshot>(checkedJson, JsonOptions)
                ?? throw new JsonException("Snapshot cannot be null.");
            checkedJson.RequireEnd();
            return Validate(snapshot);
        }
        catch (Exception exception) when (exception is JsonException or ArgumentException or InvalidOperationException or NullReferenceException or IOException or InvalidDataException)
        {
            return Rejected("INPUT.SCHEMA", "$", $"The compressed snapshot does not match the strict bounded version-1 schema: {exception.Message}",
                "Restore a complete supported snapshot within the transport limits.");
        }
    }

    /// <summary>Checks duplicate keys incrementally while the typed serializer consumes the same bytes.</summary>
    private sealed class DuplicateCheckingStream(Stream source) : Stream
    {
        private byte[] _pending = ArrayPool<byte>.Shared.Rent(64 * 1024);
        private int _length;
        private JsonReaderState _state;
        private readonly Stack<HashSet<string>> _objects = new();
        private bool _ended;

        public override int Read(byte[] buffer, int offset, int count) => Read(buffer.AsSpan(offset, count));
        public override int Read(Span<byte> buffer)
        {
            if (buffer.IsEmpty) return 0;
            var read = source.Read(buffer);
            Scan(buffer[..read], read == 0);
            return read;
        }

        private void Scan(ReadOnlySpan<byte> bytes, bool final)
        {
            if (_ended) return;
            var required = checked(_length + bytes.Length);
            if (required > _pending.Length)
            {
                var replacement = ArrayPool<byte>.Shared.Rent(required);
                _pending.AsSpan(0, _length).CopyTo(replacement);
                ArrayPool<byte>.Shared.Return(_pending); _pending = replacement;
            }
            bytes.CopyTo(_pending.AsSpan(_length)); _length = required;
            var reader = new Utf8JsonReader(_pending.AsSpan(0, _length), final, _state);
            while (reader.Read())
            {
                if (reader.TokenType == JsonTokenType.StartObject) _objects.Push(new(StringComparer.Ordinal));
                else if (reader.TokenType == JsonTokenType.EndObject) _objects.Pop();
                else if (reader.TokenType == JsonTokenType.PropertyName && !_objects.Peek().Add(reader.GetString()!))
                    throw new JsonException("Duplicate snapshot JSON property.");
            }
            _state = reader.CurrentState;
            var consumed = checked((int)reader.BytesConsumed);
            _pending.AsSpan(consumed, _length - consumed).CopyTo(_pending);
            _length -= consumed; _ended = final;
            if (final && (_length != 0 || _objects.Count != 0)) throw new JsonException("Snapshot JSON is incomplete.");
        }

        internal void RequireEnd()
        {
            Span<byte> extra = stackalloc byte[1];
            if (!_ended && Read(extra) != 0) throw new JsonException("Trailing snapshot content is not permitted.");
        }
        protected override void Dispose(bool disposing)
        {
            if (disposing && _pending.Length != 0) { ArrayPool<byte>.Shared.Return(_pending); _pending = []; }
            base.Dispose(disposing);
        }
        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
    }
}
