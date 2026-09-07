from memory_map import MemoryMap, BYTE, WORD, DWORD



def test_readme_scenario():
    memory = MemoryMap(size_bytes=8)

    memory.allocate("A", DWORD)
    memory.allocate("B", BYTE)
    memory.deallocate("A")
    memory.allocate("C", WORD)

    # |0        1        2        3        4        5        6        7        |  Bytes
    # |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
    # |Cccccccc cccccccc -------- -------- Bbbbbbbb -------- -------- -------- |  Memory usage
    assert memory.start_bit_of("C") == 0, "C should reuse the space freed by deallocating A, not sit after B"
