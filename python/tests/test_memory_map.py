import pytest
from approvaltests import verify

from memory_map import MemoryMap, BOOL, BYTE, WORD, DWORD

TYPE_NAMES = {
    BOOL: "Bool",
    BYTE: "Byte",
    WORD: "Word",
    DWORD: "DWord",
}


class Scenario:
    def __init__(self, size_bytes):
        self.memory = MemoryMap(size_bytes=size_bytes)
        self.story = []

    def describe(self, text):
        self.story.append(text)
        size_bytes = self.memory.size_bits // 8
        self._show(f"Provide empty memory page of maximum {size_bytes} Bytes:")

    def _separate(self):
        if self.story and self.story[-1] != "":
            self.story.append("")

    def _print_memory(self):
        size_bytes = self.memory.size_bits // 8
        bytes_header = "|" + "".join(f"{byte:<9}" for byte in range(size_bytes)) + "|  Bytes"
        bits_header = "|" + "01234567 " * size_bytes + "|  Bits"
        usage = ["-"] * self.memory.size_bits
        for allocation in self.memory.allocations:
            usage[allocation.start_bit] = allocation.id[-1]
            for bit in range(allocation.start_bit + 1, allocation.start_bit + allocation.size_bits):
                usage[bit] = "x"
        usage_bytes = ["".join(usage[i:i + 8]) for i in range(0, len(usage), 8)]
        usage_line = "|" + " ".join(usage_bytes) + " |  Memory usage"
        self.story.append("\n".join([bytes_header, bits_header, usage_line]))

    def _show(self, label):
        self._separate()
        self.story.append(label)
        self._print_memory()

    def allocate(self, name, type):
        self.memory.allocate(name, type)
        self._show(f"Allocate {name} of type {TYPE_NAMES[type]}")

    def deallocate(self, name):
        self.memory.deallocate(name)
        self._show(f"Deallocate {name}")

    def text(self):
        return "\n".join(self.story)


@pytest.fixture
def scenario():
    return Scenario(size_bytes=8)


def test_readme_scenario(scenario):
    scenario.describe(
        "This is the example scenario from the kata README: allocate a DWord, "
        "allocate a Byte, deallocate the DWord, then allocate a Word. Each "
        "allocation should land exactly where the README diagram shows."
    )

    scenario.allocate("A", DWORD)
    scenario.allocate("B", BYTE)
    scenario.deallocate("A")
    scenario.allocate("C", WORD)

    verify(scenario.text())


def test_allocations_never_overlap(scenario):
    scenario.describe(
        "Allocating a DWord, a Byte, a Bool, and a Word in sequence must never "
        "place two allocations over the same memory: each diagram below should "
        "show every allocation occupying its own distinct region, with no "
        "overlap between the previous allocations and the new one."
    )

    scenario.allocate("A", DWORD)
    scenario.allocate("B", BYTE)
    scenario.allocate("C", BOOL)
    scenario.allocate("D", WORD)

    verify(scenario.text())


def test_word_and_dword_are_allocated_at_even_byte_addresses(scenario):
    scenario.describe(
        "Word and DWord allocations must always start at an even byte address. "
        "Allocating a Bool first leaves memory offset by a single bit, but the "
        "Word and DWord that follow should still skip ahead to the next even "
        "byte rather than packing right after it."
    )

    scenario.allocate("A", BOOL)
    scenario.allocate("B", WORD)
    scenario.allocate("C", DWORD)

    verify(scenario.text())


def test_allocation_that_does_not_fit_raises_error():
    memory = MemoryMap(size_bytes=2)

    with pytest.raises(ValueError):
        memory.allocate("A", DWORD)


def test_fragmented_memory_is_compacted_before_allocation():
    scenario = Scenario(size_bytes=4)
    scenario.describe(
        "When memory is fragmented into gaps that are individually too small "
        "for a new allocation, existing allocations should be moved (compacted) "
        "to open up a single contiguous, aligned block. Here, freeing the "
        "middle Byte leaves two small gaps too small to fit a Word on their "
        "own, so allocating a Word should shift the last Byte down to free up "
        "enough contiguous space."
    )

    scenario.allocate("A", BYTE)
    scenario.allocate("B", BYTE)
    scenario.allocate("C", BYTE)
    scenario.deallocate("B")
    scenario.allocate("D", WORD)

    verify(scenario.text())
