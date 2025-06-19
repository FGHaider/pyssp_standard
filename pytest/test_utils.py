

from pathlib import Path

from pyssp_standard.utils import ZIPFile


def test_zipfile():
    print()
    source_file = Path("pytest/doc/embrace.ssp")
    target_file = Path('./temp_embrace.ssp')

    file_to_add = Path("pytest/test_fmu.py")
    file_to_remove = "resources/0002_ECS_SW.fmu"

    with ZIPFile(source_path=source_file, target_path=target_file) as zf:
        zf.add_file(file_to_add)
        zf.add_file(file_to_add, "resources")
        zf.remove_file(file_to_remove)

    with ZIPFile(source_path=target_file, mode="r") as zf:
        files = zf.files_rel

        assert file_to_add.name in files
        assert str(Path(f"resources/{file_to_add.name}")) in files
        assert file_to_remove not in [k for k in files]

    target_file.unlink()
