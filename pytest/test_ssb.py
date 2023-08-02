from pyssp_standard.ssb import SSB
import pytest
from pathlib import Path


@pytest.fixture
def write_file():
    test_file = Path('./test.ssb')
    yield test_file
    test_file.unlink()


def test_create_ssb(write_file):
    with SSB(write_file, 'w') as file:
        file.add_dictionary_entry('test_a', ptype='Integer', value={"value": "10"})
        file.__check_compliance__()
