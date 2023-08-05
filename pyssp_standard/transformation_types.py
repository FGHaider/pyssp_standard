from typing import TypedDict
from lxml import etree as ET
from lxml.etree import QName

from pyssp_standard.standard import SSPStandard


class Transformation(SSPStandard):

    def __init__(self, transformation_type=None, attributes=None, transformation: ET.Element = None):

        self.transformation_type = None
        self.transformation = None
        if transformation is not None:
            self.transformation_type = transformation.tag.split('}')[-1]
            self.transformation = self.__create_transformation__(self.transformation_type, transformation.attrib)
        elif transformation_type is not None and attributes is not None:
            self.transformation_type = transformation_type
            self.transformation = self.__create_transformation__(transformation_type, attributes)

    def element(self):
        if self.transformation_type is not None:
            converted_transformation = {key: str(value) for key, value in self.transformation.items()}
            return ET.Element(QName(self.namespaces['ssc'], self.transformation_type), attrib=converted_transformation)
        return None

    @staticmethod
    def __create_transformation__(ttype, attributes):
        source = attributes.get('source')
        target = attributes.get('target')
        factor = attributes.get('factor')
        offset = attributes.get('offset')

        transformation_types = {
            'LinearTransformation': lambda: LinearTransformation(factor=factor, offset=offset),
            'BooleanMappingTransformation': lambda: BooleanMappingTransformation(target=target, source=source),
            'EnumerationMappingTransformation': lambda: EnumerationMappingTransformation(target=target, source=source),
            'IntegerMappingTransformation': lambda: IntegerMappingTransformation(target=target, source=source)
        }

        return transformation_types.get(ttype, lambda: None)()


class TransformationType(TypedDict):
    pass


class LinearTransformation(TransformationType):
    factor: float  # default 1.0
    offset: float  # default 0.0


class BooleanMappingTransformation(TransformationType):
    source: bool
    target: bool


class IntegerMappingTransformation(TransformationType):
    source: int
    target: int


class EnumerationMappingTransformation(TransformationType):
    source: str
    target: str

