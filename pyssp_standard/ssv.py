from dataclasses import dataclass, field, fields
from typing import TypedDict, List
from operator import attrgetter

from lxml.etree import QName
from lxml import etree as ET

from pyssp_standard.common_content_ssc import Enumerations, BaseElement, TopLevelMetaData
from pyssp_standard.parameter_types import ParameterType

from pyssp_standard.unit import BaseUnit, Unit, Units
from pyssp_standard.utils import ModelicaXMLFile
from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.unit_conversion import generate_base_unit


class Parameter(TypedDict):
    name: str
    type_name: str
    type_value: ParameterType


@dataclass
class SSVElem(ModelicaStandard):
    name: str = "default"
    version: str = "1.0"
    parameters: list[Parameter] = field(default_factory=list)
    units: Units | None = field(default_factory=Units)
    enumerations: Enumerations | None = field(default_factory=Enumerations)
    base_element: BaseElement = field(default_factory=BaseElement)
    top_level_metadata: TopLevelMetaData = field(default_factory=TopLevelMetaData)

    @classmethod
    def from_xml(cls, elem):
        parameters = []

        parameters_elem = elem.find('ssv:Parameters', cls.namespaces)
        if parameters_elem is not None:
            parameter_elems = parameters_elem.findall('ssv:Parameter', cls.namespaces)
            for parameter in parameter_elems:
                name = parameter.get('name')
                param = parameter[0]
                param_type = QName(param.tag).localname
                param_attr = ParameterType(param_type, param.attrib)
                parameters.append(Parameter(name=name, type_name=param_type, type_value=param_attr))

        version = elem.get("version")
        name = elem.get("name")
        base_element = BaseElement()
        top_level_metadata = TopLevelMetaData()

        base_element.update(elem.attrib)
        top_level_metadata.update(elem.attrib)

        units_elem = elem.find('ssv:Units', cls.namespaces)
        units = Units(units_elem) if units_elem is not None else None

        enums_elem = elem.find("ssv:Enumerations", cls.namespaces)
        enumerations = Enumerations(enums_elem, namespace="ssv") if enums_elem is not None else None

        return cls(name, version, parameters, units, enumerations)

    def to_xml(self):
        namespaces = ["ssv", "ssc"]
        nsmap = {k: self.namespaces[k] for k in namespaces}
        root = ET.Element(
            QName(self.namespaces['ssv'], 'ParameterSet'),
            nsmap=nsmap,
            attrib={'version': self.version, 'name': self.name}
        )
        self.base_element.update(root.attrib)
        self.top_level_metadata.update(root.attrib)

        parameters_entry = ET.SubElement(root, QName(self.namespaces['ssv'], 'Parameters'))
        for param in self.parameters:
            parameter_entry = ET.SubElement(parameters_entry, QName(self.namespaces['ssv'], 'Parameter'),
                                            attrib={'name': param.get('name')})
            parameter_entry.append(param["type_value"].element())

        if not self.units.is_empty():
            root.append(self.units.element('ssv'))

        if self.enumerations is not None and not self.enumerations.is_empty():
            root.append(self.enumerations.as_element())

        return root


def wraps_dataclass(wrapped_class, local_name):
    def decorator(cls):
        for field_ in fields(wrapped_class):
            name = field_.name

            def setter(self, value):
                setattr(self, f"{local_name}.{name}", value)

            setattr(cls, name, property(attrgetter(f"{local_name}.{name}"), setter))

        return cls

    return decorator


@wraps_dataclass(SSVElem, local_name="ssv_elem")
class SSV(ModelicaXMLFile):
    name: str
    version: str
    parameters: list[Parameter]
    units: Units | None
    enumerations: Enumerations | None

    def __read__(self):
        tree = ET.parse(str(self.file_path))
        self.root = tree.getroot()
        self.ssv_elem = SSVElem.from_xml(self.root)

    def __write__(self):
        self.root = self.ssv_elem.to_xml()

    def __init__(self, filepath, mode='r', name='unnamed'):
        self.ssv_elem = SSVElem()
        super().__init__(file_path=filepath, mode=mode, identifier='ssv')

    @property
    def identifier(self):
        if self.version == "2.0":
            return "ssv2"
        else:
            return "ssv"

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
        p = Parameter(name=parname, type_name=ptype, type_value=ParameterType(ptype, parameter_dict))
        self.parameters.append(p)

    def add_unit(self, name: str, base_unit: dict = None):
        """
        Add a unit definition to the .ssv file. If base_unit is None, an attempt is made to automatically generate a BaseUnit.
        :param name: e.g. N or J/kg/K
        :param base_unit: A dictionary declaring the base unit as specified by the SSP standard.
        """
        if base_unit is None:
            base_unit = generate_base_unit(name)
        self.units.add_unit(Unit(name, base_unit=BaseUnit(base_unit)))
