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
        self._narrating = False

    def describe(self, text):
        self._narrating = True
        self.story.append(text)
        size_bytes = self.memory.size_bits // 8
        if self.memory.allocations:
            self._show(f"Starting point with maximum {size_bytes} Bytes:")
        else:
            self._show(f"Empty memory page of maximum {size_bytes} Bytes:")

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
                usage[bit] = allocation.id[-1].lower()
        usage_bytes = ["".join(usage[i:i + 8]) for i in range(0, len(usage), 8)]
        usage_line = "|" + " ".join(usage_bytes) + " |  Memory usage"
        self.story.append("\n".join([bytes_header, bits_header, usage_line]))

    def _show(self, label):
        if self._narrating:
            self._separate()
            self.story.append(label)
            self._print_memory()

    def allocate(self, name, type):
        error = None
        try:
            self.memory.allocate(name, type)
        except Exception as caught:
            if not self._narrating:
                raise
            error = caught
        self._show(f"Allocate {name} of type {TYPE_NAMES[type]}")
        self._report_error(error)

    def deallocate(self, name):
        error = None
        try:
            self.memory.deallocate(name)
        except Exception as caught:
            if not self._narrating:
                raise
            error = caught
        self._show(f"Deallocate {name}")
        self._report_error(error)

    def _report_error(self, error: Exception | None):
        if self._narrating and error:
            self.story.append(f"{error.__class__.__name__}: {error}")

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


def test_word_is_allocated_at_even_byte_address(scenario):
    scenario.allocate("A", BOOL)
    scenario.describe(
        "Word allocations must always start at an even byte address. "
        "Allocating a Bool first leaves memory offset by a single bit, but the "
        "Word that follows should still skip ahead to the next even byte "
        "rather than packing right after it."
    )

    scenario.allocate("B", WORD)

    verify(scenario.text())


def test_dword_is_allocated_at_even_byte_address(scenario):
    scenario.allocate("A", BOOL)
    scenario.describe(
        "DWord allocations must always start at an even byte address. "
        "Allocating a Bool first leaves memory offset by a single bit, but the "
        "DWord that follows should still skip ahead to the next even byte "
        "rather than packing right after it."
    )

    scenario.allocate("B", DWORD)

    verify(scenario.text())


def test_allocation_that_does_not_fit_raises_error():
    scenario = Scenario(size_bytes=2)
    scenario.describe(
        "Allocating a DWord into a memory page too small to ever hold it "
        "should raise an error rather than silently failing or corrupting "
        "memory."
    )

    scenario.allocate("A", DWORD)

    verify(scenario.text())


def test_allocating_an_id_that_is_already_allocated_raises_error(scenario):
    scenario.allocate("A", BYTE)
    scenario.describe(
        "Allocating an id that already has a current allocation should raise "
        "an error rather than creating a duplicate or silently overwriting it."
    )

    scenario.allocate("A", BYTE)

    verify(scenario.text())


def test_deallocating_an_id_that_is_not_allocated_raises_error(scenario):
    scenario.describe(
        "Deallocating an id that has no current allocation should raise an "
        "error rather than silently doing nothing."
    )

    scenario.deallocate("A")

    verify(scenario.text())


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


def test_severely_fragmented_memory_requires_moving_multiple_allocations(scenario):
    # set up severely fragmented memory
    scenario.allocate("A", BYTE)
    scenario.allocate("B", BYTE)
    scenario.allocate("C", BYTE)
    scenario.allocate("D", BYTE)
    scenario.allocate("E", BYTE)
    scenario.allocate("F", BYTE)
    scenario.deallocate("B")
    scenario.deallocate("D")

    scenario.describe(
        "Memory can end up fragmented into several small gaps at once, none of "
        "which is big enough alone, and no single move can open up enough "
        "space either - only shifting every allocation after the first gap "
        "down by one byte closes all the gaps at once. Here, there are two "
        "one-byte gaps plus two untouched Bytes at the end, for exactly "
        "four free bytes in total - just enough for a DWord, but only if C, "
        "E, and F all move down to consolidate every gap into one block."
    )
    scenario.allocate("G", DWORD)

    verify(scenario.text())
