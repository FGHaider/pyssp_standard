from lxml import etree as ET
from typing import TypedDict, List

from lxml.etree import QName

from common_content_ssc import BaseElement, TopLevelMetaData
from parameter_types import ParameterType
import xmlschema

from unit import BaseUnit, Unit, Units
from utils import SSPStandard, SSPFile


class Parameter(TypedDict):
    name: str
    type_name: str
    type_value: ParameterType


class SSV(SSPStandard, SSPFile):

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.root = self.__tree.getroot()

        parameters = self.root.findall('ssv:Parameters', self.namespaces)
        parameter_set = parameters[0].findall('ssv:Parameter', self.namespaces)
        for parameter in parameter_set:
            name = parameter.attrib.get('name')
            param = list(parameter)[0]
            param_type = param.tag.split('}')[-1]
            param_attr = ParameterType(param_type, param.attrib)
            self.__parameters.append(Parameter(name=name, type_name=param_type, type_value=param_attr))

        units = self.root.findall('ssv:Units', self.namespaces)
        if len(units) > 0:
            self.__units = Units(units[0])

    def __write__(self):
        self.root = ET.Element(QName(self.namespaces['ssv'], 'ParameterSet'), attrib={'version': '1.0', 'name': 'nan'})
        self.root = self.__top_level_metadata.update_root(self.root)
        self.root = self.__base_element.update_root(self.root)

        parameters_entry = ET.SubElement(self.root, QName(self.namespaces['ssv'], 'Parameters'))
        for param in self.__parameters:
            parameter_entry = ET.SubElement(parameters_entry, QName(self.namespaces['ssv'], 'Parameter'), attrib={'name': param.get('name')})
            parameter_entry.append(param["type_value"].element())

        if not self.__units.is_empty():
            self.root.append(self.__units.element('ssv'))

    def __init__(self, *args):
        self.__base_element: BaseElement = BaseElement()
        self.__top_level_metadata: TopLevelMetaData = TopLevelMetaData()
        self.__parameters: List[Parameter] = []
        self.__enumerations = []
        self.__units: Units = Units()
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
        self.__units.add_unit(Unit(name, base_unit=BaseUnit(base_unit)))

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssv'])
