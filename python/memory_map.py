from dataclasses import dataclass

import bug_flags

BOOL = 1
BYTE = 8
WORD = 16
DWORD = 32

_ALIGNMENT = {
    BOOL: 1,
    BYTE: 8,
    # BUG_7: loosens Word/DWord alignment to byte-level instead of even-byte
    WORD: 8 if bug_flags.BUG_7 else 16,
    DWORD: 8 if bug_flags.BUG_7 else 16,
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
        self._search_cursor = 0

    @property
    def size_bits(self):
        return self._size_bits

    @property
    def allocations(self):
        return tuple(self._allocations)

    def allocate(self, id, size_bits):
        if bug_flags.BUG_3:
            # BUG_3: silently evicts the existing allocation and re-adds it under the same id instead of raising
            self._allocations = [a for a in self._allocations if a.id != id]
        elif not bug_flags.BUG_4:
            # BUG_4: skips this check entirely, letting two allocations coexist under the same id
            if any(a.id == id for a in self._allocations):
                if bug_flags.BUG_5:
                    # BUG_5: raises the right exception type but with an incorrect message
                    raise ValueError(f"{id} allocation error")
                raise ValueError(f"An allocation named {id} already exists")
        alignment = _ALIGNMENT[size_bits]
        start_bit = self._find_free_slot(size_bits, alignment)
        if start_bit is None and not bug_flags.BUG_8:
            # BUG_8: skips compaction entirely
            self._compact()
            start_bit = self._find_free_slot(size_bits, alignment)
        if start_bit is None:
            if bug_flags.BUG_2:
                # BUG_2: silently drops an allocation that doesn't fit instead of raising
                return
            if bug_flags.BUG_6:
                # BUG_6: raises the wrong exception type when out of memory
                raise MemoryError(f"Not enough memory to allocate {id}")
            raise ValueError(f"Not enough memory to allocate {id}")
        self._allocations.append(Allocation(id, start_bit, size_bits))
        self._search_cursor = start_bit + size_bits

    def deallocate(self, id):
        if not bug_flags.BUG_1:
            # BUG_1: skips this check, so deallocating an unknown id silently no-ops
            if not any(a.id == id for a in self._allocations):
                raise ValueError(f"No allocation named {id} to deallocate")
        self._allocations = [a for a in self._allocations if a.id != id]

    def start_bit_of(self, id):
        for allocation in self._allocations:
            if allocation.id == id:
                return allocation.start_bit
        raise KeyError(f"No allocation with id {id}")

    def _find_free_slot(self, size_bits, alignment):
        candidates = range(0, self._size_bits - size_bits + 1, alignment)
        if bug_flags.BUG_9:
            # BUG_9: resumes searching from the end of the last allocation instead of always starting at the lowest address
            cursor = -(-self._search_cursor // alignment) * alignment
            candidates = [c for c in candidates if c >= cursor] + [c for c in candidates if c < cursor]
        for start_bit in candidates:
            if self._is_free(start_bit, size_bits):
                return start_bit
        return None

    def _is_free(self, start_bit, size_bits):
        end_bit = start_bit + size_bits
        # BUG_11: only checks the most recently added allocation for overlap, ignoring the rest
        others = self._allocations[-1:] if bug_flags.BUG_11 else self._allocations
        return all(
            end_bit <= a.start_bit or a.start_bit + a.size_bits <= start_bit
            for a in others
        )

    def _compact(self):
        # BUG_10: sorts allocations in reverse address order, jumbling the compacted layout
        key = (lambda a: -a.start_bit) if bug_flags.BUG_10 else (lambda a: a.start_bit)
        ordered = sorted(self._allocations, key=key)
        cursor = 0
        compacted = []
        for allocation in ordered:
            alignment = _ALIGNMENT[allocation.size_bits]
            start_bit = -(-cursor // alignment) * alignment
            compacted.append(Allocation(allocation.id, start_bit, allocation.size_bits))
            cursor = start_bit + allocation.size_bits
        if bug_flags.BUG_12 and compacted:
            # BUG_12: drops the last allocation from the compacted result
            compacted = compacted[:-1]
        self._allocations = compacted
