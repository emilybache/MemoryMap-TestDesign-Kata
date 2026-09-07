import pytest

from memory_map import MemoryMap, BOOL, BYTE, WORD, DWORD


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


def test_allocations_never_overlap():
    memory = MemoryMap(size_bytes=8)

    memory.allocate("A", DWORD)
    memory.allocate("B", BYTE)
    memory.allocate("C", BOOL)
    memory.allocate("D", WORD)

    # |0        1        2        3        4        5        6        7        |  Bytes
    # |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
    # |Aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa Bbbbbbbb C------- Dddddddd dddddddd |  Memory usage
    assert memory.start_bit_of("A") == 0, "A should start at bit 0 of empty memory"
    assert memory.start_bit_of("B") == 32, "B should start right after A ends, at bit 32"
    assert memory.start_bit_of("C") == 40, "C should start right after B ends, at bit 40"
    assert memory.start_bit_of("D") == 48, "D should skip ahead to the next even byte (bit 48) rather than pack right after C"


def test_word_is_allocated_at_even_byte_address():
    memory = MemoryMap(size_bytes=8)
    memory.allocate("A", BOOL)

    memory.allocate("B", WORD)

    # |0        1        2        3        4        5        6        7        |  Bytes
    # |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
    # |A------- -------- Bbbbbbbb bbbbbbbb -------- -------- -------- -------- |  Memory usage
    assert memory.start_bit_of("B") == 16, "Word allocations must start at an even byte address, so B should skip ahead of the Bool to bit 16"


def test_dword_is_allocated_at_even_byte_address():
    memory = MemoryMap(size_bytes=8)
    memory.allocate("A", BOOL)

    memory.allocate("B", DWORD)

    # |0        1        2        3        4        5        6        7        |  Bytes
    # |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
    # |A------- -------- Bbbbbbbb bbbbbbbb bbbbbbbb bbbbbbbb -------- -------- |  Memory usage
    assert memory.start_bit_of("B") == 16, "DWord allocations must start at an even byte address, so B should skip ahead of the Bool to bit 16"


def test_allocation_that_does_not_fit_raises_error():
    memory = MemoryMap(size_bytes=2)

    with pytest.raises(ValueError) as error:
        memory.allocate("A", DWORD)

    assert str(error.value) == "Not enough memory to allocate A", "allocating into a page too small to ever fit should raise a clear error"


def test_allocating_an_id_that_is_already_allocated_raises_error():
    memory = MemoryMap(size_bytes=8)
    memory.allocate("A", BYTE)

    with pytest.raises(ValueError) as error:
        memory.allocate("A", BYTE)

    assert str(error.value) == "An allocation named A already exists", "allocating a duplicate id should raise rather than overwrite the existing allocation"


def test_deallocating_an_id_that_is_not_allocated_raises_error():
    memory = MemoryMap(size_bytes=8)

    with pytest.raises(ValueError) as error:
        memory.deallocate("A")

    assert str(error.value) == "No allocation named A to deallocate", "deallocating an unknown id should raise rather than silently doing nothing"


def test_fragmented_memory_is_compacted_before_allocation():
    memory = MemoryMap(size_bytes=4)
    memory.allocate("A", BYTE)
    memory.allocate("B", BYTE)
    memory.allocate("C", BYTE)
    memory.deallocate("B")

    memory.allocate("D", WORD)

    # |0        1        2        3        |  Bytes
    # |01234567 01234567 01234567 01234567 |  Bits
    # |Aaaaaaaa Cccccccc Dddddddd dddddddd |  Memory usage
    assert memory.start_bit_of("C") == 8, "C should be shifted down to close the gap left by deallocating B"
    assert memory.start_bit_of("D") == 16, "D should fit in the single contiguous block that compaction frees up"


def test_severely_fragmented_memory_requires_moving_multiple_allocations():
    memory = MemoryMap(size_bytes=8)
    memory.allocate("A", BYTE)
    memory.allocate("B", BYTE)
    memory.allocate("C", BYTE)
    memory.allocate("D", BYTE)
    memory.allocate("E", BYTE)
    memory.allocate("F", BYTE)
    memory.deallocate("B")
    memory.deallocate("D")

    memory.allocate("G", DWORD)

    # |0        1        2        3        4        5        6        7        |  Bytes
    # |01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
    # |Aaaaaaaa Cccccccc Eeeeeeee Ffffffff Gggggggg gggggggg gggggggg gggggggg |  Memory usage
    assert memory.start_bit_of("C") == 8, "C should move down to close the first gap"
    assert memory.start_bit_of("E") == 16, "E should move down to close the second gap"
    assert memory.start_bit_of("F") == 24, "F should move down right after E"
    assert memory.start_bit_of("G") == 32, "G should fit in the single contiguous block freed by compacting every allocation after the first gap"
