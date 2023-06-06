import xml.etree.cElementTree as ET
from typing import TypedDict, List
from parameter_types import ParameterType, Real, Integer, String, Binary, Enumeration, Boolean
from dataclasses import dataclass, asdict
import xmlschema
from utils import SSPStandard, SSPFile


class Parameter(TypedDict):
    name: str
    type_name: str
    type_value: ParameterType


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
        for field_name, field_type in self.__annotations__.items():
            value = base_unit.get(field_name)
            if value is not None:
                if not isinstance(value, field_type):
                    try:
                        value = field_type(value)
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid value type for {field_name}. Expected {field_type}.")
                setattr(self, field_name, value)

    def to_dict(self):
        return {k: str(v) for k, v in asdict(self).items() if v is not None}


class Unit(TypedDict):
    name: str
    base_unit: BaseUnit


class SSV(SSPStandard, SSPFile):

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
            self.__parameters.append(Parameter(name=name, type_name=param_type, type_value=param_attr))

        units = self.__root.findall('Units', self.namespaces)
        unit_set = units[0].findall('Unit', self.namespaces)
        for unit in unit_set:
            name = unit.attrib.get('name')
            base_unit = unit.findall('BaseUnit')[0]
            base_unit_obj = BaseUnit(base_unit.attrib)
            self.__units.append(Unit(name=name, base_unit=base_unit_obj))

    def __write__(self):
        self.__root = ET.Element('ssv:ParameterSet', attrib={'version': '1.0',
                                                             'xlmns:ssv': self.namespaces['ssv'],
                                                             'xlmns:ssc': self.namespaces['ssc']})
        for prefix, url in self.namespaces.items():
            ET.register_namespace(prefix, url)

        parameters_entry = ET.SubElement(self.__root, 'ssv:Parameters')
        for param in self.__parameters:
            parameter_entry = ET.SubElement(parameters_entry, 'ssv:Parameter', attrib={'name': param.get('name')})
            value_entry = ET.SubElement(parameter_entry, f'ssv:{param["type_name"]}', attrib=param["type_value"])

        units_entry = ET.SubElement(self.__root, 'ssv:Units')
        for unit in self.__units:
            unit_entry = ET.SubElement(units_entry, 'ssv:Unit', attrib={'name': unit.get('name')})
            base_unit_entry = ET.SubElement(unit_entry, 'ssv:BaseUnit', attrib=unit.get('base_unit').to_dict())

    @staticmethod
    def __create_parameter__(ptype, attributes):
        value = attributes.get('value')
        name = attributes.get('name')
        unit = attributes.get('unit')
        mimetype = attributes.get('mem-type')

        parameter_types = {
            'Real': lambda: Real(value=value, unit=unit),
            'Integer': lambda: Integer(value=value),
            'Boolean': lambda: Boolean(value=value),
            'String': lambda: String(value=value),
            'Enumeration': lambda: Enumeration(value=value, name=name),
            'Binary': lambda: Binary(value=value, mimetype=mimetype)
        }

        return parameter_types.get(ptype, lambda: None)()

    def __init__(self, *args):
        self.__parameters: List[Parameter] = []
        self.__enumerations = []
        self.__units: List[Unit] = []
        self.__annotations = []

        super().__init__(*args)

    @property
    def parameters(self):
        return self.__parameters

    @property
    def units(self):
        return self.__units

    def add_parameter(self, name: str, ptype: str = 'Real', value: dict = None):
        self.__parameters.append(Parameter(name=name, type_name=ptype,
                                           type_value=self.__create_parameter__(ptype, value)))

    def add_unit(self, name: str, base_unit: dict):
        self.__units.append(Unit(name=name, base_unit=BaseUnit(base_unit)))

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssv'])
