import pytest
from pathlib import Path
from ssd import SSD


@pytest.fixture
def read_file():
    return Path("../embrace/SystemStructure.ssd")


def test_compliance_check(read_file):
    # Reference file is known to be good, no error should be raised.
    with SSD(read_file) as file:
        file.__check_compliance__()


def test_list_connectors(read_file):

    with SSD(read_file) as file:
        found = file.list_connectors(parent='Consumer')
    assert len(found) == 1
