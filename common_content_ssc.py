import datetime
from typing import TypedDict
import xml.etree.cElementTree as ET


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
        self.__root = ET.Element('ssc:Annotations')

    def add_annotation(self, annotation: Annotation):
        self.__count += 1
        self.__root.append(annotation.root)

    def is_empty(self):
        return True if self.__count == 0 else False


class ID:
    pass


class BaseElement(TypedDict):
    id: ID
    description: str


class TopLevelMetaData(TypedDict):
    author: str
    file_version: str
    copyright: str
    license: str
    generation_tool: str
    generation_date_and_time: datetime.datetime
