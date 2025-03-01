import os
import tempfile
import zipfile
import shutil
from pathlib import Path, PosixPath

from pyssp_standard.ssd import SSD
from pyssp_standard.ssb import SSB
from pyssp_standard.ssv import SSV
from pyssp_standard.ssm import SSM
from pyssp_standard.fmu import FMU
from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.utils import ZIPFile


class SSP(ZIPFile):

    def __enter__(self):
        super().__enter__()
        self.ssp_resource_path = self.unpacked_path / 'resources'

        return self

    def __init__(self, source_path, target_path=None, readonly=False):
        super().__init__(source_path, target_path, readonly)
        self.ssp_resource_path :Path = None

    def __rep__(self) -> str:
        spacing = "\t\t"
        return \
f"""{'_'*100}
SSP:
    Path       {self.file_path}
    Temp_dir:  {self.unpacked_path}
    Resources:
{spacing}{spacing.join([str(r) for r in self.resources])}
{'_'*100}
"""

    @property
    def ssd(self):
        ssd = list(self.unpacked_path.glob('*.ssd'))[0]
        return SSD(ssd)

    @property
    def ssv(self):
        ssv = list(self.ssp_resource_path.glob('*.ssv'))
        return [SSV(ssv) for ssv in ssv]

    @property
    def ssm(self):
        ssm = list(self.ssp_resource_path.glob('*.ssm'))
        return [SSM(file) for file in ssm]

    @property
    def ssb(self):
        ssb = list(self.ssp_resource_path.glob('*.ssb'))
        return [SSB(file) for file in ssb]

    @property
    def fmu(self):
        fmu = list(self.ssp_resource_path.glob('*.fmu'))
        return [FMU(file) for file in fmu]

    @property
    def resources(self):
        """ 
        Returns a list of available resources in the ssp folder /resources
        """
        return [f for f in self.get_files(self.ssp_resource_path).keys()]

    def add_resource(self, file :Path):
        """
        Add something to the resource folder of the ssp.
        :param resource: filepath of the object to add.
        """
        self.add_file(file, "resources")

    def remove_resource(self, resource_name):
        """
        Remove resource
        """
        if type(resource_name) is not str:
            resource_name = resource_name.name

        self.remove_file(f"resources/{resource_name}")
        