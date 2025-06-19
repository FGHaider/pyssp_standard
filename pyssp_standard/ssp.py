import os
import tempfile
import zipfile
import shutil
from pathlib import Path, PosixPath
import warnings
from pyssp_standard.ssd import SSD
from pyssp_standard.ssb import SSB
from pyssp_standard.ssv import SSV
from pyssp_standard.ssm import SSM
from pyssp_standard.fmu import FMU
from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.utils import ZIPFile


class VariantsProxy:
    archive_root: Path
    mode: str

    def __init__(self, archive_root: Path, mode: str):
        self.archive_root = archive_root
        self.mode = mode

    def __len__(self):
        return len(self.archive_root.glob("*.ssd"))

    def __contains__(self, name):
        variant_path = self.archive_root / Path(name).with_suffix(".ssd")
        return variant_path.is_file()

    def __getitem__(self, name):
        if name not in self and self.mode == "r":
            raise KeyError(f"SSD archive has no variant named {name!r}")

        variant_path = self.archive_root / Path(name).with_suffix(".ssd")

        mode = self.mode
        if mode == "a":
            mode = "a" if variant_path.exists() else "w"

        return SSD(variant_path, mode=self.mode)

    def __iter__(self):
        return (path.stem for path in self.archive_root.glob("*.ssd"))


class SSP(ZIPFile):
    def __enter__(self):
        super().__enter__()
        self.ssp_resource_path = self.unpacked_path / "resources"

        return self

    def __init__(self, source_path, target_path=None, mode="a", readonly=None):
        super().__init__(source_path, target_path, mode=mode, readonly=readonly)
        self.ssp_resource_path: Path = None

    def __rep__(self) -> str:
        spacing = "\t\t"
        return f"""{"_" * 100}
SSP:
    Path       {self.file_path}
    Temp_dir:  {self.unpacked_path}
    Resources:
{spacing}{spacing.join([str(r) for r in self.resources])}
{"_" * 100}
"""

    @property
    def system_structure(self):
        self.mark_changed()
        ssd_path = self.get_file_temp_path("SystemStructure.ssd")

        if self.mode == "r" and not ssd_path.exists():
            raise FileNotFoundError("SystemStructure.ssd not found in unpacked archive")

        mode = self.mode
        if mode == "a":
            mode = "a" if ssd_path.exists() else "w"

        return SSD(ssd_path, mode=mode)

    @property
    def variants(self):
        self.mark_changed()
        return VariantsProxy(self.unpacked_path, self.mode)

    @property
    def ssd(self):
        message = (
            "The ssd property is deprecated. Use SSP.system_structure to access the default "
            "variant, and SSP.variants to access other variant SSDs."
        )
        warnings.warn(message, DeprecationWarning)

        self.mark_changed()
        ssd = list(self.unpacked_path.glob("*.ssd"))[0]
        return SSD(ssd)

    @property
    def ssv(self):
        self.mark_changed()
        ssv = list(self.ssp_resource_path.glob("*.ssv"))
        return [SSV(ssv) for ssv in ssv]

    @property
    def ssm(self):
        self.mark_changed()
        ssm = list(self.ssp_resource_path.glob("*.ssm"))
        return [SSM(file) for file in ssm]

    @property
    def ssb(self):
        self.mark_changed()
        ssb = list(self.ssp_resource_path.glob("*.ssb"))
        return [SSB(file) for file in ssb]

    @property
    def fmu(self):
        self.mark_changed()
        fmu = list(self.ssp_resource_path.glob("*.fmu"))
        return [FMU(file) for file in fmu]

    @property
    def resources(self):
        """
        Returns a list of available resources in the ssp folder /resources
        """
        return [f for f in self.get_files(self.ssp_resource_path).keys()]

    def add_resource(self, file: Path):
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
