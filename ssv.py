import xml.etree.cElementTree as ET
from typing import TypedDict, List
from parameter_types import ParameterType, Real, Integer, String, Binary, Enumeration, Boolean
import xmlschema

from unit import BaseUnit, Unit
from utils import SSPStandard, SSPFile


class Parameter(TypedDict):
    name: str
    type_name: str
    type_value: ParameterType


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
            param_attr = ParameterType(param_type, param.attrib)
            self.__parameters.append(Parameter(name=name, type_name=param_type, type_value=param_attr))

        units = self.__root.findall('Units', self.namespaces)
        unit_set = units[0].findall('Unit', self.namespaces)
        for unit in unit_set:
            self.__units.append(Unit(unit))

    def __write__(self):
        self.__root = ET.Element('ssv:ParameterSet', attrib={'version': '1.0',
                                                             'xlmns:ssv': self.namespaces['ssv'],
                                                             'xlmns:ssc': self.namespaces['ssc']})
        for prefix, url in self.namespaces.items():
            ET.register_namespace(prefix, url)

        parameters_entry = ET.SubElement(self.__root, 'ssv:Parameters')
        for param in self.__parameters:
            parameter_entry = ET.SubElement(parameters_entry, 'ssv:Parameter', attrib={'name': param.get('name')})
            parameter_entry.append(param["type_value"].element())

        units_entry = ET.SubElement(self.__root, 'ssv:Units')
        for unit in self.__units:
            units_entry.append(unit.to_element())

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
                                           type_value=ParameterType(ptype, value)))

    def add_unit(self, name: str, base_unit: dict):
        self.__units.append(Unit(name, base_unit=BaseUnit(base_unit)))

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssv'])
