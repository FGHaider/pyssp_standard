
import tempfile
import zipfile
import shutil
from pathlib import Path, PosixPath

from pyssp_standard.ssd import SSD
from pyssp_standard.ssb import SSB
from pyssp_standard.ssv import SSV
from pyssp_standard.ssm import SSM
from pyssp_standard.fmu import FMU
from pyssp_standard.utils import SSPStandard


class SSP(SSPStandard):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir)

    def __init__(self, file_path):
        self.temp_dir = tempfile.mkdtemp()
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.file_path = file_path

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        ssp_unpacked_path = Path(self.temp_dir) / self.file_path.stem
        ssp_resource_path = ssp_unpacked_path / 'resources'

        self.__ssd = list(ssp_unpacked_path.glob('*.ssd'))[0]
        self.__ssv = list(ssp_resource_path.glob('*.ssv'))
        self.__ssm = list(ssp_resource_path.glob('*.ssm'))
        self.__ssb = list(ssp_resource_path.glob('*.ssb'))
        self.__fmu = list(ssp_resource_path.glob('*.fmu'))

    @property
    def ssd(self):
        return SSD(self.__ssd)

    @property
    def ssv(self):
        return [SSV(ssv) for ssv in self.__ssv]

    @property
    def ssm(self):
        return [SSM(file) for file in self.__ssm]

    @property
    def ssb(self):
        return [SSB(file) for file in self.__ssb]

    @property
    def fmu(self):
        return [FMU(file) for file in self.__fmu]
