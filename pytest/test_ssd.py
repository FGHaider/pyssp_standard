import pytest
from pathlib import Path
from pyssp_standard.ssd import SSD, Connection
import shutil


@pytest.fixture
def read_file():
    return Path("doc/embrace/SystemStructure.ssd")


@pytest.fixture
def modify_file():
    source_path = Path("doc/embrace/SystemStructure.ssd")
    test_file = Path("./test.ssd")
    shutil.copy(source_path, test_file)
    yield test_file
    test_file.unlink()


def test_compliance_check(read_file):
    # Reference file is known to be good, no error should be raised.
    with SSD(read_file) as file:
        file.__check_compliance__()


def test_list_connectors(read_file):
    with SSD(read_file) as file:
        found = file.list_connectors(parent='Consumer')
    assert len(found) == 1


def test_modify(modify_file):
    with SSD(modify_file, 'a') as file:
        file.add_connection(Connection(start_element="house", start_connector="garage",
                                       end_element="work", end_connector="parking"))

        file.remove_connection(Connection(start_element="Atmos", start_connector="Tamb",
                                          end_element="Consumer", end_connector="Tamb"))
        file.__check_compliance__()
