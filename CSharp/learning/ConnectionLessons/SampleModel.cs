using System.Security.Cryptography;
using System.Text;
using StructuralEngineering.Contracts;
using StructuralEngineering.ExcelDna;

namespace ConnectionLessons;

internal static class SampleModel
{
    public static EtabsConnectionSession Create()
    {
        // Invented identities: passing this codec is not evidence of a live ETABS read.
        var captured = new DateTimeOffset(2026, 9, 6, 12, 0, 0, TimeSpan.Zero);
        var source = new EtabsContextSourceIdentity(
            1234, captured, "C:/LessonOnly/ETABS.exe", Hash("invented executable"),
            "C:/LessonOnly/TeachingModel.edb", 100, captured, Hash("invented model"),
            "23.3.1", true, 6, 6);

        EtabsContextPoint[] points =
        [
            new("P1", 0, 0, 3000),
            new("P2", 4000, 0, 3000),
            new("P3", 8000, 0, 3000),
            new("P4", 4000, 0, 0),
            new("P5", 4000, 0, 3000), // Same coordinates as P2, deliberately a different ID.
            new("P6", 4000, 3000, 3000)
        ];
        EtabsContextSection[] sections = [new("S-BEAM", "DEMO-MATERIAL"), new("S-COLUMN", "DEMO-MATERIAL")];
        EtabsContextFrame[] frames =
        [
            new("B1", "S-BEAM", "L1", "P1", "P2", EtabsFrameDesignOrientation.Beam),
            new("B2", "S-BEAM", "L1", "P2", "P3", EtabsFrameDesignOrientation.Beam),
            new("C1", "S-COLUMN", "L1", "P4", "P2", EtabsFrameDesignOrientation.Column),
            new("X1", "S-BEAM", "L1", "P5", "P6", EtabsFrameDesignOrientation.Beam)
        ];

        const string coverage = "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent";
        var inventory = new EtabsContextInventory(Hash("invented request"), captured, source, points, frames, sections, coverage);
        var artifact = EtabsContextWorkerCodec.CreateArtifact(inventory);
        return new EtabsConnectionSession(artifact, "lesson-only-no-files-written");
    }

    private static string Hash(string value) => Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(value)));
}
