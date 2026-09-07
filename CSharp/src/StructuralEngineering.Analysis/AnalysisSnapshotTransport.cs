using System.IO.Compression;
using System.Buffers.Binary;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Versioned compressed transport of unchanged canonical snapshot-v1 JSON. Limits are admission ceilings, not PF9 qualification.</summary>
public static class AnalysisSnapshotTransport
{
    public const string SchemaVersion = "structural.analysis_snapshot_gzip/v1";
    public const string CompactSchemaVersion = "structural.analysis_snapshot_rows/v1";
    public const int MaximumEncodedBytes = 64 * 1024 * 1024;
    public const int MaximumExpandedBytes = 256 * 1024 * 1024;
    private static readonly byte[] Header = "STRUCTSNAP-GZIP-1\n"u8.ToArray();
    private static readonly byte[] CompactHeader = "STRUCTSNAP-ROWS-1\n"u8.ToArray();

    public static bool IsCompressed(ReadOnlySpan<byte> prefix) => prefix.StartsWith(Header) || prefix.StartsWith(CompactHeader);

    public static string? GetSchemaVersion(ReadOnlySpan<byte> prefix) => prefix.StartsWith(CompactHeader)
        ? CompactSchemaVersion : prefix.StartsWith(Header) ? SchemaVersion : null;

    public static void Write(Stream destination, AnalysisSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(destination); ArgumentNullException.ThrowIfNull(snapshot);
        using var encoded = new LimitedStream(destination, MaximumEncodedBytes);
        encoded.Write(Header);
        using var gzip = new GZipStream(encoded, CompressionLevel.Fastest, leaveOpen: true);
        using var expanded = new LimitedStream(gzip, MaximumExpandedBytes);
        AnalysisSnapshotCodec.WriteCanonicalJson(expanded, snapshot);
    }

    /// <summary>Writes rows-1: ordinary snapshot containers with compact positional repeated records.</summary>
    public static void WriteCompact(Stream destination, AnalysisSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(destination); ArgumentNullException.ThrowIfNull(snapshot);
        using var encoded = new LimitedStream(destination, MaximumEncodedBytes);
        encoded.Write(CompactHeader);
        using var gzip = new GZipStream(encoded, CompressionLevel.Fastest, leaveOpen: true);
        using var expanded = new LimitedStream(gzip, MaximumExpandedBytes);
        AnalysisSnapshotCodec.WritePackedJson(expanded, snapshot);
    }

    public static EtabsSnapshotResult Read(Stream source)
    {
        ArgumentNullException.ThrowIfNull(source);
        using var encoded = new LimitedStream(source, MaximumEncodedBytes, retainTail: true);
        Span<byte> header = stackalloc byte[Header.Length];
        encoded.ReadExactly(header);
        var compact = header.SequenceEqual(CompactHeader);
        if (!compact && !header.SequenceEqual(Header)) throw new InvalidDataException("Unsupported snapshot transport header.");
        using var gzip = new GZipStream(encoded, CompressionMode.Decompress, leaveOpen: true);
        using var expanded = new LimitedStream(gzip, MaximumExpandedBytes, checksum: true);
        var result = compact
            ? AnalysisSnapshotCodec.ParseAndValidatePackedStream(expanded, MaximumExpandedBytes)
            : AnalysisSnapshotCodec.ParseAndValidateStream(expanded, MaximumExpandedBytes);
        // GZipStream may return a complete JSON root after a truncated footer.
        // Check the single gzip member's CRC32 and ISIZE explicitly.
        if (result.Snapshot is not null && (encoded.Position < Header.Length + 18 ||
            BinaryPrimitives.ReadUInt32LittleEndian(encoded.Tail[..4]) != expanded.Crc32 ||
            BinaryPrimitives.ReadUInt32LittleEndian(encoded.Tail[4..]) != expanded.Position))
            return AnalysisSnapshotCodec.RejectTransport("The snapshot gzip footer is incomplete or does not match its complete payload.");
        if (result.Snapshot is { } snapshot && (snapshot.Members.Count > 1000 || snapshot.ActionRows.Count > 100_000))
            throw new InvalidDataException("The compressed snapshot exceeds its member or action-row limit.");
        return result;
    }

    internal sealed class LimitedStream(Stream source, long maximumBytes, bool checksum = false, bool retainTail = false) : Stream
    {
        private long _count;
        private uint _crc = uint.MaxValue;
        private readonly byte[] _tail = new byte[8];
        internal ReadOnlySpan<byte> Tail => _tail;
        internal uint Crc32 => ~_crc;
        public override int Read(byte[] buffer, int offset, int count) => Read(buffer.AsSpan(offset, count));
        public override int Read(Span<byte> buffer)
        {
            var read = source.Read(buffer);
            _count = checked(_count + read);
            if (_count > maximumBytes) throw new InvalidDataException("Snapshot input exceeds its bounded byte limit.");
            var bytes = buffer[..read];
            if (checksum)
                foreach (var value in bytes) _crc = (_crc >> 8) ^ CrcTable[(_crc ^ value) & 255];
            if (retainTail && read > 0)
            {
                if (read >= 8) bytes[^8..].CopyTo(_tail);
                else { _tail.AsSpan(read).CopyTo(_tail); bytes.CopyTo(_tail.AsSpan(8 - read)); }
            }
            return read;
        }
        public override bool CanRead => source.CanRead;
        public override bool CanSeek => false;
        public override bool CanWrite => source.CanWrite;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => _count; set => throw new NotSupportedException(); }
        public override void Flush() => source.Flush();
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => Write(buffer.AsSpan(offset, count));
        public override void Write(ReadOnlySpan<byte> buffer)
        {
            _count = checked(_count + buffer.Length);
            if (_count > maximumBytes) throw new InvalidDataException("Snapshot output exceeds its bounded byte limit.");
            source.Write(buffer);
        }
        // Ownership of the source remains with the caller.
    }

    private static readonly uint[] CrcTable = BuildCrcTable();
    private static uint[] BuildCrcTable()
    {
        var table = new uint[256];
        for (uint index = 0; index < table.Length; index++)
        {
            var value = index;
            for (var bit = 0; bit < 8; bit++) value = (value >> 1) ^ ((value & 1) == 0 ? 0 : 0xedb88320u);
            table[index] = value;
        }
        return table;
    }
}
