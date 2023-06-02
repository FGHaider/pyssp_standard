import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List
from parameter_types import ParameterType, Real, Integer, String, Binary, Enumeration, Boolean
from dataclasses import dataclass, fields

from utils import SSPStandard


class Parameter(TypedDict):
    name: str
    value: ParameterType


@dataclass
class BaseUnit:
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

    def __init__(self, base_unit: dict):
        for field_obj in fields(self):
            field_name = field_obj.name
            if field_name in base_unit:
                value = base_unit[field_name]
                field_type = field_obj.type
                if not isinstance(value, field_type):
                    try:
                        value = field_type(value)
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid value type for {field_name}. Expected {field_type}.")
                setattr(self, field_name, value)
            else:
                setattr(self, field_name, None)

    def to_dict(self):
        data_dict = {}
        for field_obj in fields(self):
            field_name = field_obj.name
            value = getattr(self, field_name)
            if value is not None:
                value = str(value)
                data_dict[field_name] = value
        return data_dict


class Unit(TypedDict):
    name: str
    base_unit: BaseUnit


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
            param_attr = self.__create_parameter__(param_type, param.attrib)
            self.__parameters.append(Parameter(name=name, value=param_attr))

        units = self.__root.findall('Units', self.namespaces)
        unit_set = units[0].findall('Unit', self.namespaces)
        for unit in unit_set:
            name = unit.attrib.get('name')
            base_unit = unit.findall('BaseUnit')[0]
            base_unit_obj = BaseUnit(base_unit.attrib)
            self.__units.append(Unit(name=name, base_unit=base_unit_obj))

    def __write__(self):
        pass

    def __save__(self):
        pass

    @staticmethod
    def __create_parameter__(ptype, attributes):
        value = attributes.get('value')
        name = attributes.get('name')
        unit = attributes.get('unit')
        mimetype = attributes.get('mem-type')
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

    def add_parameter(self, name: str, ptype: str = 'Real', value: dict = None):
        self.__parameters.append(Parameter(name=name, value=self.__create_parameter__(ptype, value)))

    def add_unit(self, name: str, base_unit: dict):
        self.__units.append(Unit(name=name, base_unit=BaseUnit(base_unit)))