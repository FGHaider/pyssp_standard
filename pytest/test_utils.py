import tempfile
from pathlib import Path

import pytest

from pyssp_standard.utils import ZIPFile


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace.ssp")


@pytest.fixture
def target_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()
        yield Path(f.name)

        Path(f.name).unlink()


@pytest.fixture
def file_one():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "example"
        with open(path, "w") as f:
            f.write("file one")

        yield path


@pytest.fixture
def file_two():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "example"
        with open(path, "w") as f:
            f.write("file two")

        yield path


def test_zipfile(read_file, target_file, file_one, file_two):
    print()

    file_to_remove = "resources/0002_ECS_SW.fmu"

    with ZIPFile(source_path=read_file, target_path=target_file) as zf:
        zf.add_file(file_one)
        zf.add_file(file_one, "resources")
        zf.add_file(file_one, "resources")

        with pytest.raises(FileExistsError):
            zf.add_file(file_two)

        zf.add_file(file_two, overwrite=True)

        zf.remove_file(file_to_remove)

    with ZIPFile(source_path=target_file, mode="r") as zf:
        files = zf.files_rel

        assert file_two.name in files
        assert str(Path(f"resources/{file_two.name}")) in files
        assert file_to_remove not in files
