import xmlschema

from parameter_types import ParameterType
from ssm import Annotations
from utils import SSPStandard, SSPFile
import xml.etree.cElementTree as ET
from typing import TypedDict, List


class DictionaryEntry(TypedDict):
    name: str
    type_entry: ParameterType
    annotations: Annotations


class SSB(SSPStandard, SSPFile):

    def __init__(self, *args):
        self.version = None
        self.top_level_meta_data = None

        self.__annotations = []
        self.__dictionary_entry = List[DictionaryEntry]
        self.__enumerations = []
        self.__units = []

        super().__init__(*args)

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.__root = self.__tree.getroot()

        self.version = self.__root.get('version')
        dictionary_entries = self.__root.findall('ssb:DictionaryEntry', self.namespaces)
        for entry in dictionary_entries:
            name = entry.get('name')
            self.__dictionary_entry.append(DictionaryEntry(name=name, type_entry=ParameterType(),
                                                           annotations=Annotations()))

    def __write__(self):
        pass

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssb'])
