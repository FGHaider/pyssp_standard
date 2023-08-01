import xmlschema

from pyssp_standard.parameter_types import ParameterType
from pyssp_standard.common_content_ssc import Annotations, Enumerations, Annotation, Enumeration
from pyssp_standard.unit import Unit, Units
from pyssp_standard.utils import SSPStandard, SSPFile
from lxml import etree as ET
from lxml.etree import QName
from typing import TypedDict, List


class DictionaryEntry(TypedDict):
    name: str
    type_entry: ParameterType
    annotations: Annotations


class DictionaryEntryList(list):

    def __repr__(self):
        print_out = """"""
        for item in self:
            print_out += f"""
        ___________________________________________________________________________________________
        Name: {item['name']}
        Type: {item['type_entry']}
            """
        return print_out


class SSB(SSPStandard, SSPFile):

    def __init__(self, *args):
        self.version = None
        self.base_element = None
        self.top_level_meta_data = None

        self.__annotations: Annotations = Annotations()
        self.__dictionary_entry: DictionaryEntryList = DictionaryEntryList()
        self.__enumerations: Enumerations = Enumerations()
        self.__units: Units = Units()

        super().__init__(*args)

    def __read__(self):
        self.__tree = ET.parse(self.file_path, parser=ET.XMLParser(encoding='utf-8'))
        self.root = self.__tree.getroot()

        self.version = self.root.get('version')
        dictionary_entries = self.root.findall('ssb:DictionaryEntry', self.namespaces)
        for entry in dictionary_entries:
            name = entry.get('name')
            self.__dictionary_entry.append(DictionaryEntry(name=name, type_entry=ParameterType(),
                                                           annotations=Annotations()))

    def __write__(self):
        self.root = ET.Element(QName(self.namespaces['ssb'], 'SignalDictionary'), attrib={'version': '1.0'})
        # Add BaseElement and ATopLevelMetaData
        for entry in self.__dictionary_entry:
            dictionary_entry = ET.Element(QName(self.namespaces['ssb'], 'DictionaryEntry'), attrib={'name': entry.get('name')})
            dictionary_entry.append(entry["type_entry"].element())
            self.root.append(dictionary_entry)

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssb'], namespaces=self.namespaces)

    def add_dictionary_entry(self, name: str, ptype: str, value: dict, annotations=None):
        self.__dictionary_entry.append(DictionaryEntry(name=name,
                                                       type_entry=ParameterType(ptype, value, 'ssc'),
                                                       annotations=Annotations() if annotations is None else annotations))

    def add_annotation(self, annotation: Annotation):
        self.__annotations.add_annotation(annotation)

    def add_enumeration(self, enum: Enumeration):
        self.__enumerations.add_enumeration(enum)

    def add_unit(self):
        pass
