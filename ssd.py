from transformation_types import Transformation
from utils import SSPStandard
import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List


class System(SSPStandard):

    def __init__(self, system_element: ET.Element):

        self.name = None

        self.connectors = []
        self.parameter_bindings = []

        self.elements = []
        self.connections = []
        self.signal_dictionaries = []
        self.annotations = []


class SSD(SSPStandard):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mode == 'a':
            self.__save__()

    def __init__(self, file_path, mode='r'):
        self.__mode = mode
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.file_path = file_path

        self.__tree = None
        self.__root = None

        self.name = None
        self.version = None

        self.system = None
        self.__enumerations = []
        self.__units = []
        self.defaultExperiment = None
        self.__annotations = []

        if mode == 'r' or mode == 'a':
            self.__read__()
        else:
            raise Exception('Only read and append mode is supported for SSD files')

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.__root = self.__tree.getroot()

        self.name = self.__root.get('name')
        self.version = self.__root.get('version')

    def __save__(self):
        pass

    def __check_compliance__(self):
        pass
