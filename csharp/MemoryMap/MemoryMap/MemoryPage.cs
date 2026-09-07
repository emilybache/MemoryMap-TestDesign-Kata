namespace MemoryMap;

public sealed class MemoryPage
{
    private readonly List<Allocation> _allocations = [];

    public MemoryPage(int sizeBytes)
    {
        SizeBits = sizeBytes * 8;
    }

    public int SizeBits { get; }

    public IReadOnlyList<Allocation> Allocations => _allocations.AsReadOnly();

    public void Allocate(string id, int sizeBits)
    {
        var startBit = FindFreeSlot(sizeBits);
        if (startBit is null)
        {
            throw new InvalidOperationException($"Not enough memory to allocate {id}");
        }

        _allocations.Add(new Allocation(id, startBit.Value, sizeBits));
    }

    public void Deallocate(string id)
    {
        _allocations.RemoveAll(a => a.Id == id);
    }

    public int StartBitOf(string id)
    {
        foreach (var allocation in _allocations)
        {
            if (allocation.Id == id)
            {
                return allocation.StartBit;
            }
        }

        throw new KeyNotFoundException($"No allocation with id {id}");
    }

    private int? FindFreeSlot(int sizeBits)
    {
        for (var startBit = 0; startBit <= SizeBits - sizeBits; startBit++)
        {
            if (IsFree(startBit, sizeBits))
            {
                return startBit;
            }
        }

        return null;
    }

    private bool IsFree(int startBit, int sizeBits)
    {
        var endBit = startBit + sizeBits;
        return _allocations.All(a => endBit <= a.StartBit || a.StartBit + a.SizeBits <= startBit);
    }
}
