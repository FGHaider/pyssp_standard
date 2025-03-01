
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
    print()
    test_ssp_file = Path('./embrace.ssp')
    shutil.copy(read_file, test_ssp_file)

    file_to_add = Path('pytest/doc/test.txt')
    with SSP(test_file) as file:
        file_to_remove = file.resources[0]
        file.add_resource(file_to_add)
        file.remove_resource(file_to_remove)

        print(ssp.resources)

    with SSP(test_ssp_file) as ssp:
        assert file_to_add.name in [entry for entry in ssp.resources]
        assert file_to_remove not in [entry for entry in ssp.resources]

    test_ssp_file.unlink()