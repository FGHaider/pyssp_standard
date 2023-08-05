from dataclasses import dataclass, asdict
from lxml import etree as ET
from lxml.etree import QName

from pyssp_standard.utils import SSPElement
from pyssp_standard.standard import SSPStandard


@dataclass
class BaseUnit:
    kg: int = None
    m: int = None
    s: int = None
    A: int = None
    K: int = None
    mol: int = None
    cd: int = None
    rad: int = None
    factor: float = None
    offset: float = None

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


class Unit(SSPElement, SSPStandard):

    def __init__(self, unit, base_unit: BaseUnit = None):

        self.__root = None
        self.__name = None
        self.__base_unit = None

        if type(unit) is ET.Element:
            self.from_element(unit)
        else:
            self.__name = unit
            self.__base_unit = base_unit

    def to_element(self):
        unit_entry = ET.Element(QName(self.namespaces['ssc'], 'Unit'), attrib={'name': self.__name})
        unit_entry.append(ET.Element(QName(self.namespaces['ssc'], 'BaseUnit'), attrib=self.__base_unit.to_dict()))
        return unit_entry

    def from_element(self, element):
        self.__name = element.attrib.get('name')
        base_unit = element.findall('BaseUnit')[0]
        self.__base_unit = BaseUnit(base_unit.attrib)


class Units(SSPStandard):

    def __init__(self, element: ET.Element = None):
        self.__units = []
        self.__root = None

        if element is not None:
            units = element.findall('Unit', self.namespaces)
            for unit in units:
                self.__units.append(Unit(unit))

    def add_unit(self, unit: Unit):
        self.__units.append(unit)

    def element(self, parent_type='ssc'):
        self.__root = ET.Element(QName(self.namespaces[parent_type], 'Units'))
        for unit in self.__units:
            self.__root.append(unit.to_element())
        return self.__root

    def is_empty(self):
        return True if len(self.__units) == 0 else False
