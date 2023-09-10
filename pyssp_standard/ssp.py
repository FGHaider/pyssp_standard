import tempfile
import zipfile
import shutil
from pathlib import Path, PosixPath

from pyssp_standard.ssd import SSD
from pyssp_standard.ssb import SSB
from pyssp_standard.ssv import SSV
from pyssp_standard.ssm import SSM
from pyssp_standard.fmu import FMU
from pyssp_standard.standard import SSPStandard


class SSP(SSPStandard):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__changed:
            temp_resources = Path(self.temp_dir) / self.file_path.stem / 'resources'
            current_resources = list(temp_resources.glob('*'))
            for resource in self.__resources:
                if resource not in current_resources and resource.parent != temp_resources:
                    shutil.copy(resource, temp_resources)
            for resource in current_resources:
                if resource not in self.__resources and resource.parent == temp_resources:
                    resource.unlink()
            filepath = self.file_path.parent / self.file_path.stem
            filepath_zip = Path(str(filepath) + '.zip')
            filepath_ssp = Path(str(filepath) + '.ssp')
            shutil.make_archive(filepath, 'zip', self.temp_dir)
            if filepath_ssp.exists():
                filepath_ssp.unlink()
            filepath_zip.rename(filepath_ssp)
        shutil.rmtree(self.temp_dir)

    def __init__(self, file_path):
        self.__changed = False
        self.temp_dir = tempfile.mkdtemp()
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.file_path = file_path

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        ssp_unpacked_path = Path(self.temp_dir) / self.file_path.stem
        ssp_resource_path = ssp_unpacked_path / 'resources'

        all_resource_files = set(ssp_resource_path.glob('*'))
        self.__ssd = list(ssp_unpacked_path.glob('*.ssd'))[0]
        self.__ssv = list(ssp_resource_path.glob('*.ssv'))
        self.__ssm = list(ssp_resource_path.glob('*.ssm'))
        self.__ssb = list(ssp_resource_path.glob('*.ssb'))
        self.__fmu = list(ssp_resource_path.glob('*.fmu'))

        self.__resources = list(all_resource_files)

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

    @property
    def resources(self):
        """ Returns a list of available resources in the ssp folder /resources"""
        return self.__resources

    def add_resource(self, resource):
        """
        Add something to the resource folder of the ssp.
        :param resource: filepath of the object to add.
        """
        self.__changed = True
        self.__resources.append(resource)

    def remove_resource(self, resource_name):
        self.__changed = True
        if type(resource_name) is not str:
            resource_name = resource_name.name
        self.__resources = [path for path in self.__resources if path.name != resource_name]
