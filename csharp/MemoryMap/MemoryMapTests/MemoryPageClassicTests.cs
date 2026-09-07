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

    [Test]
    public void AllocationsNeverOverlap()
    {
        var memory = new MemoryPage(sizeBytes: 8);

        memory.Allocate("A", MemoryUnit.DWord);
        memory.Allocate("B", MemoryUnit.Byte);
        memory.Allocate("C", MemoryUnit.Bool);
        memory.Allocate("D", MemoryUnit.Word);

        // |0        1        2        3        4        5        6        7        |  Bytes
        // |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
        // |Aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa Bbbbbbbb C------- Dddddddd dddddddd |  Memory usage
        Assert.That(memory.StartBitOf("A"), Is.EqualTo(0), "A should start at bit 0 of empty memory");
        Assert.That(memory.StartBitOf("B"), Is.EqualTo(32), "B should start right after A ends, at bit 32");
        Assert.That(memory.StartBitOf("C"), Is.EqualTo(40), "C should start right after B ends, at bit 40");
        Assert.That(memory.StartBitOf("D"), Is.EqualTo(48),
            "D should skip ahead to the next even byte (bit 48) rather than pack right after C");
    }

    [Test]
    public void WordIsAllocatedAtEvenByteAddress()
    {
        var memory = new MemoryPage(sizeBytes: 8);
        memory.Allocate("A", MemoryUnit.Bool);

        memory.Allocate("B", MemoryUnit.Word);

        // |0        1        2        3        4        5        6        7        |  Bytes
        // |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
        // |A------- -------- Bbbbbbbb bbbbbbbb -------- -------- -------- -------- |  Memory usage
        Assert.That(memory.StartBitOf("B"), Is.EqualTo(16),
            "Word allocations must start at an even byte address, so B should skip ahead of the Bool to bit 16");
    }

    [Test]
    public void DwordIsAllocatedAtEvenByteAddress()
    {
        var memory = new MemoryPage(sizeBytes: 8);
        memory.Allocate("A", MemoryUnit.Bool);

        memory.Allocate("B", MemoryUnit.DWord);

        // |0        1        2        3        4        5        6        7        |  Bytes
        // |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
        // |A------- -------- Bbbbbbbb bbbbbbbb bbbbbbbb bbbbbbbb -------- -------- |  Memory usage
        Assert.That(memory.StartBitOf("B"), Is.EqualTo(16),
            "DWord allocations must start at an even byte address, so B should skip ahead of the Bool to bit 16");
    }

    [Test]
    public void AllocationThatDoesNotFitRaisesError()
    {
        var memory = new MemoryPage(sizeBytes: 2);

        var error = Assert.Throws<ArgumentException>(() => memory.Allocate("A", MemoryUnit.DWord));

        Assert.That(error!.Message, Is.EqualTo("Not enough memory to allocate A"),
            "allocating into a page too small to ever fit should raise a clear error");
    }

    [Test]
    public void AllocatingAnIdThatIsAlreadyAllocatedRaisesError()
    {
        var memory = new MemoryPage(sizeBytes: 8);
        memory.Allocate("A", MemoryUnit.Byte);

        var error = Assert.Throws<InvalidOperationException>(() => memory.Allocate("A", MemoryUnit.Byte));

        Assert.That(error!.Message, Is.EqualTo("An allocation named A already exists"),
            "allocating a duplicate id should raise rather than overwrite the existing allocation");
    }

    [Test]
    public void DeallocatingAnIdThatIsNotAllocatedRaisesError()
    {
        var memory = new MemoryPage(sizeBytes: 8);

        var error = Assert.Throws<InvalidOperationException>(() => memory.Deallocate("A"));

        Assert.That(error!.Message, Is.EqualTo("No allocation named A to deallocate"),
            "deallocating an unknown id should raise rather than silently doing nothing");
    }

    [Test]
    public void FragmentedMemoryIsCompactedBeforeAllocation()
    {
        var memory = new MemoryPage(sizeBytes: 4);
        memory.Allocate("A", MemoryUnit.Byte);
        memory.Allocate("B", MemoryUnit.Byte);
        memory.Allocate("C", MemoryUnit.Byte);
        memory.Deallocate("B");

        memory.Allocate("D", MemoryUnit.Word);

        // |0        1        2        3        |  Bytes
        // |01234567 01234567 01234567 01234567 |  Bits
        // |Aaaaaaaa Cccccccc Dddddddd dddddddd |  Memory usage
        Assert.That(memory.StartBitOf("C"), Is.EqualTo(8), "C should be shifted down to close the gap left by deallocating B");
        Assert.That(memory.StartBitOf("D"), Is.EqualTo(16), "D should fit in the single contiguous block that compaction frees up");
    }

    [Test]
    public void SeverelyFragmentedMemoryRequiresMovingMultipleAllocations()
    {
        var memory = new MemoryPage(sizeBytes: 8);
        memory.Allocate("A", MemoryUnit.Byte);
        memory.Allocate("B", MemoryUnit.Byte);
        memory.Allocate("C", MemoryUnit.Byte);
        memory.Allocate("D", MemoryUnit.Byte);
        memory.Allocate("E", MemoryUnit.Byte);
        memory.Allocate("F", MemoryUnit.Byte);
        memory.Deallocate("B");
        memory.Deallocate("D");

        memory.Allocate("G", MemoryUnit.DWord);

        // |0        1        2        3        4        5        6        7        |  Bytes
        // |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
        // |Aaaaaaaa Cccccccc Eeeeeeee Ffffffff Gggggggg gggggggg gggggggg gggggggg |  Memory usage
        Assert.That(memory.StartBitOf("C"), Is.EqualTo(8), "C should move down to close the first gap");
        Assert.That(memory.StartBitOf("E"), Is.EqualTo(16), "E should move down to close the second gap");
        Assert.That(memory.StartBitOf("F"), Is.EqualTo(24), "F should move down right after E");
        Assert.That(memory.StartBitOf("G"), Is.EqualTo(32),
            "G should fit in the single contiguous block freed by compacting every allocation after the first gap");
    }
}
