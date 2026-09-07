using MemoryMap;

namespace MemoryMapTests;

public class MemoryPageClassicTests
{
    [Test]
    public void ReadmeScenario()
    {
        var memory = new MemoryPage(sizeBytes: 8);

        memory.Allocate("A", MemoryUnit.DWord);
        memory.Allocate("B", MemoryUnit.Byte);
        memory.Deallocate("A");
        memory.Allocate("C", MemoryUnit.Word);

        // |0        1        2        3        4        5        6        7        |  Bytes
        // |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
        // |Cccccccc cccccccc -------- -------- Bbbbbbbb -------- -------- -------- |  Memory usage
        Assert.That(memory.StartBitOf("C"), Is.EqualTo(0),
            "C should reuse the space freed by deallocating A, not sit after B");
    }
}
