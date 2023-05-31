
import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List
from parameter_types import ParameterType


class Parameter(TypedDict):
    name: str
    value: ParameterType


class BaseUnit(TypedDict):
    kg: int
    m: int
    s: int
    A: int
    K: int
    mol: int
    cd: int
    rad: int
    factor: float
    offset: float


class Unit(TypedDict):
    name: str
    base_unit: BaseUnit


class SSPStandard:

    parameter_types = ['Real', 'Integer', 'Boolean', 'String', 'Enumeration', 'Binary']

    namespaces = {'ssc': 'http://ssp-standard.org/SSP1/SystemStructureCommon',
                  'ssv': 'http://ssp-standard.org/SSP1/SystemStructureParameterValues',
                  'ssb': 'http://ssp-standard.org/SSP1/SystemStructureSignalDictionary',
                  'ssm': 'http://ssp-standard.org/SSP1/SystemStructureParameterMapping',
                  'ssd': 'http://ssp-standard.org/SSP1/SystemStructureDescription'}


class SSV(SSPStandard):

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mode in ['w', 'a']:
            self.__save__()

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.__root = self.__tree.getroot()

    def __write__(self):
        pass

    def __save__(self):
        pass

    def __init__(self, file_path, mode='r'):
        self.__mode = mode
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.file_path = file_path

        self.__tree = None
        self.__root = None

        self.__parameters: List[Parameter] = []
        self.__enumerations = []
        self.__units: List[Unit] = []
        self.__annotations = []

        match mode:
            case 'r':
                self.__read__()
            case 'w':
                self.__write__()
            case 'a':
                self.__read__()

    @property
    def parameters(self):
        return self.__parameters

    @property
    def units(self):
        return self.__units

    def add_parameter(self, name, value, unit):
        pass

    def add_unit(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
