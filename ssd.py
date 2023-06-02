from transformation_types import Transformation
from utils import SSPStandard
import xml.etree.cElementTree as ET
from pathlib import Path, PosixPath
from typing import TypedDict, List


class SSD(SSPStandard):

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

        self.__tree = None
        self.__root = None

        self.__annotations = []

        if mode == 'r' or mode == 'a':
            self.__read__()
        elif mode == 'w':
            self.__write__()

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.__root = self.__tree.getroot()

    def __write__(self):
        pass

    def __save__(self):
        pass

    def __check_compliance__(self):
        pass
