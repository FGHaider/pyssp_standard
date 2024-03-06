

import shutil
import pytest
import os
from pathlib import Path


from pyssp_standard.utils import ZipFile


def test_zipfile():
    print()
    source_file = Path("./doc/embrace.ssp")
    target_file = Path('./temp_embrace.ssp')

    file_to_add = Path("./test_fmu.py")
    file_to_remove = "embrace/resources/0002_ECS_SW.fmu"

    with ZipFile(file_path=source_file, save_path=target_file) as zf:
        zf.add_file(file_to_add, "embrace")
        zf.add_file(file_to_add, "embrace/resources/")
        zf.remove_file(file_to_remove)

    with ZipFile(file_path=target_file, readonly=True) as zf:
        files = zf.files

        assert f"embrace/{file_to_add.name}" in files.keys()
        assert f"embrace/resources/{file_to_add.name}" in files.keys()
        assert file_to_remove not in [k for k in files.keys()]
    
    target_file.unlink()