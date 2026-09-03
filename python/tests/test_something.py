import pytest
from approvaltests import verify

from memory_map import *

def test_something():
    assert True == False

def test_verify():
    verify("Hello World")
