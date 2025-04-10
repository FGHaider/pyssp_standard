import tempfile
from pathlib import Path
import shutil

import pytest

from pyssp_standard.ssp import SSP


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace.ssp")


@pytest.fixture
def write_file():
    with tempfile.NamedTemporaryFile(delete_on_close=False) as f:
        f.close()
        yield f.name


def test_unpacking(read_file):
    with SSP(read_file) as file:
        pass


def test_add_resource(read_file):
    print()
    test_ssp_file = Path("./embrace.ssp")
    shutil.copy(read_file, test_ssp_file)

    file_to_add = Path("pytest/doc/test.txt")
    with SSP(test_ssp_file) as ssp:
        file_to_remove = ssp.resources[0]
        print(file_to_remove)
        ssp.add_resource(file_to_add)
        ssp.remove_resource(file_to_remove)

        print(ssp.resources)

    with SSP(test_ssp_file) as ssp:
        assert file_to_add.name in [entry for entry in ssp.resources]
        assert file_to_remove not in [entry for entry in ssp.resources]

    test_ssp_file.unlink()


def test_create_ssp(write_file):
    with SSP(write_file, mode="w") as ssp:
        assert isinstance(ssp, SSP)
