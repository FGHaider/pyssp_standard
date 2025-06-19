from dataclasses import dataclass, asdict
from lxml import etree as ET
from lxml.etree import QName

from pyssp_standard.utils import SSPElement
from pyssp_standard.standard import ModelicaStandard


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


class Unit(SSPElement, ModelicaStandard):

    def __init__(self, unit, base_unit: BaseUnit = None):
        self.name = None
        self.base_unit = None

        if isinstance(unit, ET._Element):
            self.from_element(unit)
        else:
            self.name = unit
            self.base_unit = base_unit

    def to_element(self, namespace="ssc"):
        ns = "" if not namespace else f"{{{self.namespaces[namespace]}}}"

        unit_entry = ET.Element(f"{ns}Unit", attrib={'name': self.name})

        if namespace == "ssc" and self.base_unit is None:
            self.base_unit = BaseUnit({})  # In FMI BaseUnit is optional, in SSP it is required

        if self.base_unit is not None:
            ET.SubElement(
                unit_entry,
                f"{ns}BaseUnit",
                **self.base_unit.to_dict()
            )

        return unit_entry

    def from_element(self, element):
        self.name = element.attrib.get('name')
        ns = QName(element.tag).namespace
        tag_name = "ssc:BaseUnit" if ns is not None else "BaseUnit"

        base_unit = element.find(tag_name, self.namespaces)
        if base_unit is not None:  # Base unit is optional
            self.base_unit = BaseUnit(base_unit.attrib)


class Units(ModelicaStandard):

    def __init__(self, element: ET.Element = None):
        self.units = []

        if element is not None:
            namespace = "ssc:"
            if element.tag == "UnitDefinitions":  # Detect FMI ModelDefinition
                namespace = ""

            units = element.findall(f"{namespace}Unit", self.namespaces)
            for unit in units:
                self.units.append(Unit(unit, namespace))

    def add_unit(self, unit: Unit):
        self.units.append(unit)

    def element(self, parent_type='ssc'):
        if parent_type == "fmi":
            elem_name = "UnitDefinitions"
            child_ns = None
        else:
            elem_name = QName(self.namespaces[parent_type], "Units")
            child_ns = "ssc"

        root = ET.Element(elem_name)
        root.extend(unit.to_element(namespace=child_ns) for unit in self.units)

        return root

    def __len__(self):
        return len(self.units)

    def __getitem__(self, idx):
        return self.units[idx]

    def is_empty(self):
        return True if len(self.units) == 0 else False
