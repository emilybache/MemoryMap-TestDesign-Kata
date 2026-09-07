namespace MemoryMap;

public sealed class MemoryPage
{
    private static readonly IReadOnlyDictionary<int, int> Alignment = new Dictionary<int, int>
    {
        [MemoryUnit.Bool] = 1,
        [MemoryUnit.Byte] = 8,
        // BUG_7: loosens Word/DWord alignment to byte-level instead of even-byte
        [MemoryUnit.Word] = BugFlags.Bug7 ? 8 : 16,
        [MemoryUnit.DWord] = BugFlags.Bug7 ? 8 : 16,
    };

    private List<Allocation> _allocations = [];
    private int _searchCursor;

    public MemoryPage(int sizeBytes)
    {
        SizeBits = sizeBytes * 8;
    }

    public int SizeBits { get; }

    public IReadOnlyList<Allocation> Allocations => _allocations.AsReadOnly();

    public void Allocate(string id, int sizeBits)
    {
        if (BugFlags.Bug3)
        {
            // BUG_3: silently evicts the existing allocation and re-adds it under the same id instead of raising
            _allocations = _allocations.Where(a => a.Id != id).ToList();
        }
        else if (!BugFlags.Bug4)
        {
            // BUG_4: skips this check entirely, letting two allocations coexist under the same id
            if (_allocations.Any(a => a.Id == id))
            {
                if (BugFlags.Bug5)
                {
                    // BUG_5: raises the right exception type but with an incorrect message
                    throw new InvalidOperationException($"{id} allocation error");
                }

                throw new InvalidOperationException($"An allocation named {id} already exists");
            }
        }

        var alignment = Alignment[sizeBits];
        var startBit = FindFreeSlot(sizeBits, alignment);
        if (startBit is null && !BugFlags.Bug8)
        {
            // BUG_8: skips compaction entirely
            Compact();
            startBit = FindFreeSlot(sizeBits, alignment);
        }

        if (startBit is null)
        {
            if (BugFlags.Bug2)
            {
                // BUG_2: silently drops an allocation that doesn't fit instead of raising
                return;
            }

            if (BugFlags.Bug6)
            {
                // BUG_6: raises the wrong exception type when out of memory
                throw new OutOfMemoryException($"Not enough memory to allocate {id}");
            }

            throw new ArgumentException($"Not enough memory to allocate {id}");
        }

        _allocations.Add(new Allocation(id, startBit.Value, sizeBits));
        _searchCursor = startBit.Value + sizeBits;
    }

    public void Deallocate(string id)
    {
        if (!BugFlags.Bug1)
        {
            // BUG_1: skips this check, so deallocating an unknown id silently no-ops
            if (!_allocations.Any(a => a.Id == id))
            {
                throw new InvalidOperationException($"No allocation named {id} to deallocate");
            }
        }

        _allocations = _allocations.Where(a => a.Id != id).ToList();
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

    private int? FindFreeSlot(int sizeBits, int alignment)
    {
        var candidates = new List<int>();
        for (var start = 0; start <= SizeBits - sizeBits; start += alignment)
        {
            candidates.Add(start);
        }

        if (BugFlags.Bug9)
        {
            // BUG_9: resumes searching from the end of the last allocation instead of always starting at the lowest address
            var cursor = RoundUpToAlignment(_searchCursor, alignment);
            candidates = candidates.Where(c => c >= cursor)
                .Concat(candidates.Where(c => c < cursor))
                .ToList();
        }

        foreach (var start in candidates)
        {
            if (IsFree(start, sizeBits))
            {
                return start;
            }
        }

        return null;
    }

    private bool IsFree(int startBit, int sizeBits)
    {
        var endBit = startBit + sizeBits;
        // BUG_11: only checks the most recently added allocation for overlap, ignoring the rest
        IEnumerable<Allocation> others = BugFlags.Bug11
            ? (_allocations.Count > 0 ? [_allocations[^1]] : [])
            : _allocations;
        return others.All(a => endBit <= a.StartBit || a.StartBit + a.SizeBits <= startBit);
    }

    private void Compact()
    {
        // BUG_10: sorts allocations in reverse address order, jumbling the compacted layout
        var ordered = BugFlags.Bug10
            ? _allocations.OrderByDescending(a => a.StartBit)
            : _allocations.OrderBy(a => a.StartBit);

        var cursor = 0;
        var compacted = new List<Allocation>();
        foreach (var allocation in ordered)
        {
            var alignment = Alignment[allocation.SizeBits];
            var startBit = RoundUpToAlignment(cursor, alignment);
            compacted.Add(new Allocation(allocation.Id, startBit, allocation.SizeBits));
            cursor = startBit + allocation.SizeBits;
        }

        if (BugFlags.Bug12 && compacted.Count > 0)
        {
            // BUG_12: drops the last allocation from the compacted result
            compacted.RemoveAt(compacted.Count - 1);
        }

        _allocations = compacted;
    }

    private static int RoundUpToAlignment(int value, int alignment) => (value + alignment - 1) / alignment * alignment;
}
