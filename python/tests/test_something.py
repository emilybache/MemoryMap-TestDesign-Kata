import pytest
from approvaltests import verify

from memory_map import *

def test_classic():
    assert "Hello World"

def test_verify():
    verify("Hello World")
