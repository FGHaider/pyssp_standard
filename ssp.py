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

        self.__ssd = None
        self.__ssv = None
        self.__ssm = None
        self.__ssb = None
        self.__fmu = None

    def __read__(self):

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

    def __write__(self):
        pass

    def __save__(self):
        pass

    @property
    def ssd(self):
        return self.__ssd

    @property
    def ssv(self):
        return self.__ssv

    @property
    def ssm(self):
        return self.__ssm

    @property
    def ssb(self):
        return self.__ssb

    @property
    def fmu(self):
        return self.__fmu
