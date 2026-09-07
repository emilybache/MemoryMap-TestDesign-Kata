using MemoryMap;

namespace MemoryMapTests;

public class MemoryPageApprovalTests
{
    [Test]
    public Task ReadmeScenario()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Describe(
            "This is the example scenario from the kata README: allocate a DWord, " +
            "allocate a Byte, deallocate the DWord, then allocate a Word. Each " +
            "allocation should land exactly where the README diagram shows.");

        scenario.Allocate("A", MemoryUnit.DWord);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Deallocate("A");
        scenario.Allocate("C", MemoryUnit.Word);

        return Verify(scenario.Text());
    }

    [Test]
    public Task AllocationsNeverOverlap()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Describe(
            "Allocating a DWord, a Byte, a Bool, and a Word in sequence must never " +
            "place two allocations over the same memory: each diagram below should " +
            "show every allocation occupying its own distinct region, with no " +
            "overlap between the previous allocations and the new one.");

        scenario.Allocate("A", MemoryUnit.DWord);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Allocate("C", MemoryUnit.Bool);
        scenario.Allocate("D", MemoryUnit.Word);

        return Verify(scenario.Text());
    }

    [Test]
    public Task WordIsAllocatedAtEvenByteAddress()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Allocate("A", MemoryUnit.Bool);
        scenario.Describe(
            "Word allocations must always start at an even byte address. " +
            "Allocating a Bool first leaves memory offset by a single bit, but the " +
            "Word that follows should still skip ahead to the next even byte " +
            "rather than packing right after it.");

        scenario.Allocate("B", MemoryUnit.Word);

        return Verify(scenario.Text());
    }

    [Test]
    public Task DwordIsAllocatedAtEvenByteAddress()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Allocate("A", MemoryUnit.Bool);
        scenario.Describe(
            "DWord allocations must always start at an even byte address. " +
            "Allocating a Bool first leaves memory offset by a single bit, but the " +
            "DWord that follows should still skip ahead to the next even byte " +
            "rather than packing right after it.");

        scenario.Allocate("B", MemoryUnit.DWord);

        return Verify(scenario.Text());
    }

    [Test]
    public Task AllocationThatDoesNotFitRaisesError()
    {
        var scenario = new Scenario(sizeBytes: 2);
        scenario.Describe(
            "Allocating a DWord into a memory page too small to ever hold it " +
            "should raise an error rather than silently failing or corrupting " +
            "memory.");

        scenario.Allocate("A", MemoryUnit.DWord);

        return Verify(scenario.Text());
    }

    [Test]
    public Task AllocatingAnIdThatIsAlreadyAllocatedRaisesError()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Allocate("A", MemoryUnit.Byte);
        scenario.Describe(
            "Allocating an id that already has a current allocation should raise " +
            "an error rather than creating a duplicate or silently overwriting it.");

        scenario.Allocate("A", MemoryUnit.Byte);

        return Verify(scenario.Text());
    }

    [Test]
    public Task DeallocatingAnIdThatIsNotAllocatedRaisesError()
    {
        var scenario = new Scenario(sizeBytes: 8);
        scenario.Describe(
            "Deallocating an id that has no current allocation should raise an " +
            "error rather than silently doing nothing.");

        scenario.Deallocate("A");

        return Verify(scenario.Text());
    }

    [Test]
    public Task FragmentedMemoryIsCompactedBeforeAllocation()
    {
        var scenario = new Scenario(sizeBytes: 4);
        scenario.Describe(
            "When memory is fragmented into gaps that are individually too small " +
            "for a new allocation, existing allocations should be moved (compacted) " +
            "to open up a single contiguous, aligned block. Here, freeing the " +
            "middle Byte leaves two small gaps too small to fit a Word on their " +
            "own, so allocating a Word should shift the last Byte down to free up " +
            "enough contiguous space.");

        scenario.Allocate("A", MemoryUnit.Byte);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Allocate("C", MemoryUnit.Byte);
        scenario.Deallocate("B");
        scenario.Allocate("D", MemoryUnit.Word);

        return Verify(scenario.Text());
    }

    [Test]
    public Task SeverelyFragmentedMemoryRequiresMovingMultipleAllocations()
    {
        var scenario = new Scenario(sizeBytes: 8);

        // set up severely fragmented memory
        scenario.Allocate("A", MemoryUnit.Byte);
        scenario.Allocate("B", MemoryUnit.Byte);
        scenario.Allocate("C", MemoryUnit.Byte);
        scenario.Allocate("D", MemoryUnit.Byte);
        scenario.Allocate("E", MemoryUnit.Byte);
        scenario.Allocate("F", MemoryUnit.Byte);
        scenario.Deallocate("B");
        scenario.Deallocate("D");

        scenario.Describe(
            "Memory can end up fragmented into several small gaps at once, none of " +
            "which is big enough alone, and no single move can open up enough " +
            "space either - only shifting every allocation after the first gap " +
            "down by one byte closes all the gaps at once. Here, there are two " +
            "one-byte gaps plus two untouched Bytes at the end, for exactly " +
            "four free bytes in total - just enough for a DWord, but only if C, " +
            "E, and F all move down to consolidate every gap into one block.");
        scenario.Allocate("G", MemoryUnit.DWord);

        return Verify(scenario.Text());
    }
}
