from utils import SSPStandard
import tempfile
import zipfile
from pathlib import Path, PosixPath
import shutil


class SSP(SSPStandard):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir)

    def __init__(self, file_path, mode='r'):
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = file_path

    def __read__(self):

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

    def __write__(self):
        pass

    def __save__(self):
        pass
