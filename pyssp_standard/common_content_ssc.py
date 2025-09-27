import datetime
from typing import TypedDict, List
from abc import ABC, abstractmethod
from lxml import etree as ET

from lxml.etree import QName
from dataclasses import dataclass, asdict, fields, field

from pyssp_standard.standard import ModelicaStandard


class Annotation(ModelicaStandard):  # TODO needs to read and not just create
    def __init__(self, type_declaration):
        """
        The SSP standard allows for the addition of annotations, when created they must contain at least one annotation.
        An annotation may contain anything, however to ease its use the pyssp_standard provides tools to add text, attributes
        elements and ET.Element.
        :param type_declaration: normalized string
        """
        if type(type_declaration) is str:
            self.root = ET.Element(
                QName(self.namespaces["ssc"], "Annotation"), attrib={"type": type_declaration}
            )
        elif type(type_declaration) is ET._Element:
            self.root = type_declaration

    def add_element(self, element: ET.Element):
        self.root.append(element)

    def add_text(self, text: str):
        self.root.text = text

    def add_dict(self, name: str, attributes: dict):
        self.root.append(ET.Element(name, attrib=attributes))


class Annotations(ModelicaStandard):
    def __init__(self, namespace="ssc"):
        self.__count = 0
        self.root = ET.Element(QName(self.namespaces[namespace], "Annotations"))

    def add_annotation(self, annotation: Annotation):
        self.__count += 1
        self.root.append(annotation.root)

    def element(self):
        return self.root

    def is_empty(self):
        return True if self.__count == 0 else False


@dataclass
class BaseElement:
    id: str = ""
    description: str = ""

    def __repr__(self):
        return f"ID: {self.id} \nDescription: {self.description}"

    def update(self, attributes: dict):
        for key, value in attributes.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def dict(self):
        return {key: str(value) for key, value in asdict(self).items()}

    def update_root(self, root: ET.Element):
        for key, value in self.dict().items():
            if value != "":
                root.set(key, value)
        return root


@dataclass
class TopLevelMetaData:
    author: str = ""
    fileversion: str = ""
    copyright: str = ""
    license: str = ""
    generationTool: str = "pyssp_standard"
    generationDateAndTime: datetime.datetime = datetime.datetime.now().isoformat()

    def __repr__(self):
        base_txt = ""
        for field in fields(self):
            reformatted_text = field.name.replace("_", " ")
            reformatted_text = reformatted_text.capitalize()
            base_txt += f"{reformatted_text}: {getattr(self, field.name)}\n"
        return base_txt

    def update(self, attributes: dict):
        for key, value in attributes.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def dict(self):
        return {key: str(value) for key, value in asdict(self).items()}

    def update_root(self, root):
        for key, value in self.dict().items():
            if value != "":
                root.set(key, value)
        return root


@dataclass
class Item(ModelicaStandard):
    name: str
    value: int

    @classmethod
    def from_xml(cls, elem):
        return cls(elem.get("name"), int(elem.get("value")))

    def to_xml(self):
        return ET.Element(
            QName(self.namespaces["ssc"], "Item"), name=self.name, value=str(self.value)
        )


@dataclass
class Enumeration(ModelicaStandard):
    name: str
    items: List[Item]
    base_element: BaseElement = field(default_factory=BaseElement)
    annotations: Annotations | None = None

    @classmethod
    def from_xml(cls, elem):
        base_elem = BaseElement()
        base_elem.update(elem.attrib)

        name = elem.get("name")
        items = [Item.from_xml(el) for el in elem.findall("ssc:Item", cls.namespaces)]
        # TODO: Annotations

        return cls(name, items, base_elem, None)

    def to_xml(self):
        elem = ET.Element(QName(self.namespaces["ssc"], "Enumeration"), name=self.name)
        self.base_element.update_root(elem)
        elem.extend(item.to_xml() for item in self.items)

        return elem


class Enumerations(ModelicaStandard):
    enumerations: list[Enumeration]
    namespace: str

    def __init__(self, enumerations: List[Enumeration] | ET.ElementBase = None, namespace="ssc"):
        self.enumerations = []
        self.namespace = namespace
        if isinstance(enumerations, ET._Element):
            self.__read__(enumerations)
        elif enumerations is not None:
            self.enumerations.extend(enumerations)

    def __read__(self, element):
        self.enumerations.extend(Enumeration.from_xml(elem) for elem in element)

    def as_element(self):
        elem = ET.Element(QName(self.namespaces[self.namespace], "Enumerations"))
        for enum in self.enumerations:
            elem.append(enum.to_xml())

        return elem

    def add_enumeration(self, enum: Enumeration):
        self.enumerations.append(enum)


_prefix = f"{{{ModelicaStandard.namespaces['ssc']}}}"


class TypeChoice(ABC, ModelicaStandard):
    XPATH_SSP = ET.ETXPath(
        "|".join(
            _prefix + type_ for type_ in ["Real", "Integer", "Boolean", "String", "Enumeration"]
        )
    )

    XPATH_FMI = "Real|Integer|Boolean|String|Enumeration"

    @abstractmethod
    def to_xml(self, namespace="ssc"): ...

    @classmethod
    def from_xml(cls, elem):
        name = QName(elem.tag).localname
        if name == "Real":
            return TypeReal.from_xml(elem)
        elif name == "Integer":
            return TypeInteger.from_xml(elem)
        elif name == "Boolean":
            return TypeBoolean.from_xml(elem)
        elif name == "String":
            return TypeString.from_xml(elem)
        elif name == "Enumeration":
            return TypeEnumeration.from_xml(elem)
        else:
            raise ValueError("Element is not a valid type choice element.")


class TypeReal(TypeChoice):
    def __init__(self, unit, min=None, max=None, start=None):
        self.unit = unit
        self.min = min
        self.max = max
        self.start = start

    def to_xml(self, namespace="ssc"):
        if namespace:
            ns = f"{{{self.namespaces[namespace]}}}"
        else:
            ns = ""

        elem = ET.Element(f"{ns}Real")
        if self.unit is not None:
            elem.set("unit", self.unit)

        if namespace == "":  # fmi
            if self.min is not None:
                elem.set("min", str(self.min))

            if self.max is not None:
                elem.set("max", str(self.max))

            if self.start is not None:
                elem.set("start", str(self.start))

        return elem

    @classmethod
    def from_xml(cls, elem):
        keys = ("min", "max", "start")

        return cls(
            unit=elem.get("unit"),
            **{key: float(v) for key in keys if (v := elem.get(key)) is not None},
        )


class TypeInteger(TypeChoice):
    def __init__(self):
        pass

    def to_xml(self, namespace="ssc"):
        if namespace:
            ns = f"{{{self.namespaces[namespace]}}}"
        else:
            ns = ""

        return ET.Element(f"{ns}Integer")

    @classmethod
    def from_xml(cls, elem):
        return cls()


class TypeBoolean(TypeChoice):
    def __init__(self):
        pass

    def to_xml(self, namespace="ssc"):
        if namespace:
            ns = f"{{{self.namespaces[namespace]}}}"
        else:
            ns = ""

        return ET.Element(f"{ns}Boolean")

    @classmethod
    def from_xml(cls, elem):
        return cls()


class TypeString(TypeChoice):
    def __init__(self):
        pass

    def to_xml(self, namespace="ssc"):
        if namespace:
            ns = f"{{{self.namespaces[namespace]}}}"
        else:
            ns = ""

        return ET.Element(f"{ns}String")

    @classmethod
    def from_xml(cls, elem):
        return cls()


class TypeEnumeration(TypeChoice):
    def __init__(self, name):
        self.name = name

    def to_xml(self, namespace="ssc"):
        if namespace:
            ns = f"{{{self.namespaces[namespace]}}}"
        else:
            ns = ""

        return ET.Element(f"{ns}Enumeration", name=self.name)

    @classmethod
    def from_xml(cls, elem):
        return cls(elem.get("name"))
