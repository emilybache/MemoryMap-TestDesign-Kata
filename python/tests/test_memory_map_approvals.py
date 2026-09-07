from approvaltests import verify

from memory_map import BOOL, BYTE, WORD, DWORD
from .conftest import Scenario

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
