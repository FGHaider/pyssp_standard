import pytest
from pathlib import Path
from ssv import SSV


@pytest.fixture
def read_file():
    return Path("../embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv")


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception
    error = None
    try:
        with SSV(read_file) as file:
            pass

    except Exception as e:
        error = e
    assert error is None




