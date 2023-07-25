
import pytest
from pathlib import Path
from pyssp.ssp import SSP


@pytest.fixture
def read_file():
    return Path("doc/embrace.ssp")


def test_unpacking(read_file):
    with SSP(read_file) as file:
        pass
