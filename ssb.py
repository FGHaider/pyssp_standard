from parameter_types import ParameterType
from ssm import Annotations
from utils import SSPStandard
import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List


class DictionaryEntry(TypedDict):
    name: str
    type_entry: ParameterType
    annotations: Annotations


class SSB(SSPStandard):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mode in ['w', 'a']:
            self.__save__()

    def __init__(self, file_path, mode='r'):
        self.__mode = mode
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.file_path = file_path

        self.version = None
        self.top_level_meta_data = None

        self.__tree = None
        self.__root = None

        self.__annotations = []
        self.__dictionary_entry = List[DictionaryEntry]
        self.__enumerations = []
        self.__units = []

        if mode == 'r' or mode == 'a':
            self.__read__()
        elif mode == 'w':
            self.__write__()

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

    def __save__(self):
        tree = ET.ElementTree(self.__root)
        tree.write(self.file_path, encoding='utf-8', xml_declaration=True)

    def __check_compliance__(self):
        pass
