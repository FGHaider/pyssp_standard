import pytest
from pathlib import Path
from py_ssp.ssv import SSV


@pytest.fixture
def read_file():
    return Path("doc/embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv")


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception

    with SSV(read_file) as file:
        print(file)
        file.__check_compliance__()


def test_creation():

    with SSV('./test.ssv', 'w') as file:
        file.add_parameter(name='Cats', ptype='Integer', value={"value": "10"})
        file.add_parameter(name='Weight', ptype='Real', value={"value": "20.4", "unit": "kg"})
        file.add_unit("kg", {"kg": 1})
        file.__check_compliance__()
