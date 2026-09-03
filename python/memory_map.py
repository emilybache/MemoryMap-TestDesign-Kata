from dataclasses import dataclass

BOOL = 1
BYTE = 8
WORD = 16
DWORD = 32

_ALIGNMENT = {
    BOOL: 1,
    BYTE: 8,
    WORD: 16,
    DWORD: 16,
}


@dataclass(frozen=True)
class Allocation:
    id: str
    start_bit: int
    size_bits: int


class MemoryMap:
    def __init__(self, size_bytes):
        self._size_bits = size_bytes * 8
        self._allocations = []

    @property
    def size_bits(self):
        return self._size_bits

    @property
    def allocations(self):
        return tuple(self._allocations)

    def allocate(self, id, size_bits):
        alignment = _ALIGNMENT[size_bits]
        start_bit = self._find_free_slot(size_bits, alignment)
        if start_bit is None:
            self._compact()
            start_bit = self._find_free_slot(size_bits, alignment)
        if start_bit is None:
            raise ValueError(f"Not enough memory to allocate {id}")
        self._allocations.append(Allocation(id, start_bit, size_bits))

    def deallocate(self, id):
        self._allocations = [a for a in self._allocations if a.id != id]

    def _find_free_slot(self, size_bits, alignment):
        for start_bit in range(0, self._size_bits - size_bits + 1, alignment):
            if self._is_free(start_bit, size_bits):
                return start_bit
        return None

    def _is_free(self, start_bit, size_bits):
        end_bit = start_bit + size_bits
        return all(
            end_bit <= a.start_bit or a.start_bit + a.size_bits <= start_bit
            for a in self._allocations
        )

    def _compact(self):
        ordered = sorted(self._allocations, key=lambda a: a.start_bit)
        cursor = 0
        compacted = []
        for allocation in ordered:
            alignment = _ALIGNMENT[allocation.size_bits]
            start_bit = -(-cursor // alignment) * alignment
            compacted.append(Allocation(allocation.id, start_bit, allocation.size_bits))
            cursor = start_bit + allocation.size_bits
        self._allocations = compacted
