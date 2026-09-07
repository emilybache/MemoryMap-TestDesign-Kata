import pytest

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
