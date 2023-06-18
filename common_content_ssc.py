import datetime
from typing import TypedDict, List
import xml.etree.cElementTree as ET
from dataclasses import dataclass, asdict, fields


class Annotation:

    def __init__(self, type_declaration: str):
        """
        The SSP standard allows for the addition of annotations, when created they must contain at least one annotation.
        An annotation may contain anything, however to ease its use the pyssp provides tools to add text, attributes
        elements and ET.Element.
        :param type_declaration: normalized string
        """
        self.root = ET.Element('ssc:Annotation', attrib={"type": type_declaration})

    def add_element(self, element: ET.Element):
        self.root.append(element)

    def add_text(self, text: str):
        self.root.text = text

    def add_dict(self, name: str, attributes: dict):
        self.root.append(ET.Element(name, attrib=attributes))


class Annotations:

    def __init__(self):
        self.__count = 0
        self.root = ET.Element('ssc:Annotations')

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


@dataclass
class TopLevelMetaData:
    author: str = ""
    file_version: str = ""
    copyright: str = ""
    license: str = ""
    generation_tool: str = ""
    generation_date_and_time: datetime.datetime = datetime.datetime.now()

    def __repr__(self):
        base_txt = ""
        for field in fields(self):
            reformatted_text = field.name.replace('_', ' ')
            reformatted_text = reformatted_text.capitalize()
            base_txt += f"{reformatted_text}: {getattr(self, field.name)}\n"
        return base_txt

    def update(self, attributes: dict):
        for key, value in attributes.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def dict(self):
        return {key: str(value) for key, value in asdict(self).items()}


class Item(TypedDict):
    name: str
    value: int


class Enumeration(TypedDict):
    base_element: BaseElement
    name: str
    items: List[Item]
    annotations: Annotations


class Enumerations:

    def __init__(self, enumerations: List[Enumeration] = None):
        self.__root = ET.Element('ssc:Enumerations')
        if enumerations is not None:
            for enum in enumerations:
                self.__root.append(enum)

    def add_enumeration(self, enum: Enumeration):
        self.__root.append(enum)
