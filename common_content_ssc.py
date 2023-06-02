import datetime
from typing import TypedDict
import xml.etree.cElementTree as ET


class ID:
    pass


class BaseElement(TypedDict):
    id: ID
    description: str


class Annotation(TypedDict):
    type: str
    entry: ET.Element


class TopLevelMetaData(TypedDict):
    author: str
    file_version: str
    copyright: str
    license: str
    generation_tool: str
    generation_date_and_time: datetime.datetime
