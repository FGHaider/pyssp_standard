from lxml import etree as ET
from typing import TypedDict, List
from lxml.etree import QName

from pyssp_standard.common_content_ssc import Enumerations
from pyssp_standard.parameter_types import ParameterType

from pyssp_standard.unit import BaseUnit, Unit, Units
from pyssp_standard.utils import SSPFile
from pyssp_standard.unit_conversion import generate_base_unit


class Parameter(TypedDict):
    name: str
    type_name: str
    type_value: ParameterType


class SSV(SSPFile):

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
        self.root = ET.Element(QName(self.namespaces['ssv'], 'ParameterSet'),
                               attrib={'version': '1.0', 'name': self.__name})
        self.root = self.top_level_metadata.update_root(self.root)
        self.root = self.base_element.update_root(self.root)

        parameters_entry = ET.SubElement(self.root, QName(self.namespaces['ssv'], 'Parameters'))
        for param in self.__parameters:
            parameter_entry = ET.SubElement(parameters_entry, QName(self.namespaces['ssv'], 'Parameter'),
                                            attrib={'name': param.get('name')})
            parameter_entry.append(param["type_value"].element())

        if not self.__units.is_empty():
            self.root.append(self.__units.element('ssv'))

    def __init__(self, filepath, mode='r', name='unnamed'):
        self.__parameters: List[Parameter] = []
        self.__enumerations: Enumerations() = Enumerations
        self.__units: Units = Units()
        self.__name = name

        super().__init__(file_path=filepath, mode=mode, identifier='ssv')

    @property
    def parameters(self):
        return self.__parameters

    @property
    def units(self):
        return self.__units

    def add_parameter(self, parname: str, ptype: str = 'Real', *, value: float = None, name: str = None, mimetype=None,
                      unit: str = None):
        parameter_dict = {}
        if value is not None:
            parameter_dict['value'] = str(value)
        if name is not None:
            parameter_dict['name'] = name
        if mimetype is not None:
            parameter_dict['mimetype'] = mimetype
        if unit is not None:
            parameter_dict['unit'] = unit
        self.__parameters.append(Parameter(name=parname, type_name=ptype,
                                           type_value=ParameterType(ptype, parameter_dict)))

    def add_unit(self, name: str, base_unit: dict = None):
        """
        Add a unit definition to the .ssv file. If base_unit is None, an attempt is made to automatically generate a BaseUnit.
        :param name: e.g. N or J/kg/K
        :param base_unit: A dictionary declaring the base unit as specified by the SSP standard.
        """
        if base_unit is None:
            base_unit = generate_base_unit(name)
        self.__units.add_unit(Unit(name, base_unit=BaseUnit(base_unit)))
