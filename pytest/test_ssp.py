
import pytest
from pathlib import Path
from pyssp_standard.ssp import SSP
import shutil


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace.ssp")


def test_unpacking(read_file):
    with SSP(read_file) as file:
        pass


def test_add_resource(read_file):
    test_file = Path('./embrace.ssp')
    shutil.copy(read_file, test_file)

    file_to_add = Path('pytest/doc/test.txt')
    with SSP(test_file) as file:
        file_to_remove = file.resources[0]
        file.add_resource(file_to_add)
        file.remove_resource(file_to_remove)

    with SSP(test_file) as file:
        assert file_to_add.name in [entry.name for entry in file.resources]
        assert file_to_remove.name not in [entry.name for entry in file.resources]

    test_file.unlink()