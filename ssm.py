import xmlschema
from transformation_types import Transformation
from utils import SSPStandard, SSPFile
import xml.etree.cElementTree as ET
from typing import TypedDict, List

# TODO - handle transformation entry and read


class EmptyElement(ET.Element):

    def __init__(self, tag, attrib=None, **kwargs):
        super().__init__(tag, attrib, **kwargs)

    def __repr__(self):
        return ET.tostring(self, encoding='utf-8', short_empty_elements=True)


class Annotations:
    pass


class MappingEntry(TypedDict):
    source: str
    target: str
    suppress_unit_conversion: bool
    annotations: Annotations
    transformation: Transformation


class SSM(SSPStandard, SSPFile):

    def __init__(self, *args):
        self.__mappings: List[MappingEntry] = []
        self.__annotations = []

        super().__init__(*args)

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.__root = self.__tree.getroot()

        mappings = self.__root.findall('ssm:MappingEntry', self.namespaces)
        for entry in mappings:
            self.__mappings.append(MappingEntry(source=entry.attrib.get('source'), target=entry.attrib.get('target'),
                                                suppress_unit_conversion=False, annotations=Annotations(),
                                                transformation=Transformation()))

    def __write__(self):
        self.__root = ET.Element('ssm:ParameterMapping', attrib={'version': '1.0',
                                                                 'xlmns:ssm': self.namespaces['ssm'],
                                                                 'xlmns:ssc': self.namespaces['ssc']})
        for mapping in self.__mappings:
            mapping_entry = ET.SubElement(self.__root, 'ssm:MappingEntry', attrib={'target': mapping.get('target'),
                                                                                   'source': mapping.get('source')})

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssv'])

    @property
    def mappings(self):
        return self.__mappings

    def add_mapping(self, source, target, suppress_unit_conversion=False, transformation=None, annotations=None):
        self.__mappings.append(MappingEntry(source=source, target=target,
                                            suppress_unit_conversion=suppress_unit_conversion,
                                            annotations=Annotations(),
                                            transformation=Transformation()))

    def edit_mapping(self, edit_target=True, *, target=None, source=None, transformation=None):
        # TODO possibly merge to one single function under add_mapping?
        found = False
        for idx, entry in enumerate(self.__mappings):
            if edit_target and entry.get('target') == target:
                found = True
                break
            elif not edit_target and entry.get('source') == source:
                found = True
                break

        if found:
            pass
        else:
            raise Exception("The target or source was not found, there is nothing to edit")




