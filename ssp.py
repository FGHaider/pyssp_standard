
import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List
from parameter_types import ParameterType, Real, Integer, String, Binary, Enumeration, Boolean


class Parameter(TypedDict):
    name: str
    value: ParameterType


class BaseUnit(TypedDict):
    kg: str#int
    m: str#int
    s: str#int
    A: str#int
    K: str#int
    mol: str#int
    cd: str#int
    rad: str#int
    factor: str#float
    offset: str#float


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

        parameters = self.__root.findall('ssv:Parameters', self.namespaces)
        parameter_set = parameters[0].findall('ssv:Parameter', self.namespaces)
        for parameter in parameter_set:
            name = parameter.attrib.get('name')
            param = list(parameter)[0]
            param_type = param.tag.split('}')[-1]
            param_value = param.attrib.get('value')
            param_unit = param.attrib.get('unit')
            param_name = param.attrib.get('name')
            param_mimetype = param.attrib.get('mime-type')
            param_attr = self.__create_parameter__(param_type, param_value, param_unit, param_name, param_mimetype)
            self.__parameters.append(Parameter(name=name, value=param_attr))

        units = self.__root.findall('Units', self.namespaces)
        unit_set = units[0].findall('Unit', self.namespaces)
        for unit in unit_set:
            name = unit.attrib.get('name')
            base_unit = unit.findall('BaseUnit')[0]
            base_unit_obj = BaseUnit(kg=base_unit.attrib.get('kg'), m=base_unit.attrib.get('m'),
                                     s=base_unit.attrib.get('s'), A=base_unit.attrib.get('A'),
                                     K=base_unit.attrib.get('K'), mol=base_unit.attrib.get('mol'),
                                     cd=base_unit.attrib.get('cd'), rad=base_unit.attrib.get('rad'),
                                     factor=base_unit.attrib.get('factor'), offset=base_unit.attrib.get('offset'))
            self.__units.append(Unit(name=name, base_unit=base_unit_obj))

    def __write__(self):
        pass

    def __save__(self):
        pass

    @staticmethod
    def __create_parameter__(ptype, value, unit, name, mimetype):
        if ptype == 'Real':
            return Real(value=value, unit=unit)
        if ptype == 'Integer':
            return Integer(value=value)
        if ptype == 'Boolean':
            return Boolean(value=value)
        if ptype == 'String':
            return String(value=value)
        if ptype == 'Enumeration':
            return Enumeration(value=value, name=name)
        if ptype == 'Binary':
            return Binary(value=value, mimetype=mimetype)


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

        if mode == 'r' or mode == 'a':
            self.__read__()
        elif mode == 'w':
            self.__write__()

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
