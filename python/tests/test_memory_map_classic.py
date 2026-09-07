from memory_map import MemoryMap, BYTE, WORD, DWORD


def test_allocate_reuses_space_freed_by_earlier_deallocation():
    memory = MemoryMap(size_bytes=8)

    memory.allocate("A", DWORD)
    memory.allocate("B", BYTE)
    memory.deallocate("A")
    memory.allocate("C", WORD)

    assert memory.start_bit_of("C") == 0, "C should reuse the space freed by deallocating A, not sit after B"
