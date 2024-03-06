
import shutil
import tempfile
from pathlib import Path, PosixPath
from abc import ABC, abstractmethod
import zipfile
import xmlschema
import os
from lxml import etree as ET

from pyssp_standard.common_content_ssc import Annotations, Annotation, BaseElement, TopLevelMetaData
from pyssp_standard.standard import SSPStandard


def register_namespaces():
    ssp_standards = SSPStandard
    for name, url in ssp_standards.namespaces.items():
        ET.register_namespace(name, url)


class XMLFile(ABC):

    @abstractmethod
    def __read__(self):
        pass

    @abstractmethod
    def __write__(self):
        pass

    @property
    def BaseElement(self):
        return self.base_element

    @property
    def TopLevelMetaData(self):
        return self.top_level_metadata

    def __init__(self, file_path, mode='r'):
        self.__mode = mode
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.__file_path = file_path
        self.__tree = None
        self.root = None
        self.base_element: BaseElement = BaseElement()
        self.top_level_metadata: TopLevelMetaData = TopLevelMetaData()

        if mode == 'r' or mode == 'a':
            self.__read__()

    def check_compliance(self, schema, namespaces):
        if self.__mode in ['a', 'w']:  # Temporary file creation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = temp_dir + 'tmp.xml'
                self.__write__()
                xml_string = ET.tostring(self.root, pretty_print=True, encoding='utf-8', xml_declaration=True)
                with open(temp_file_path, 'wb') as file:
                    file.write(xml_string)
                xmlschema.validate(temp_file_path, schema, namespaces=namespaces)
        else:
            xmlschema.validate(self.file_path, schema, namespaces=namespaces)

    @property
    def file_path(self):
        return self.__file_path

    def __save__(self):
        xml_string = ET.tostring(self.root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        with open(self.__file_path, 'wb') as file:
            file.write(xml_string)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mode in ['w', 'a']:
            self.__write__()
            self.__save__()



class ZipFile:

    @staticmethod
    def get_files(dir : Path):
        return {os.path.relpath(p, dir):p for p in dir.rglob('*')}

    def __enter__(self):
        self.__temp_dir = Path(tempfile.mkdtemp(prefix="pyssp_"))
        self.__temp_content_dir = self.__temp_dir / self.file_path.stem

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.__temp_content_dir)

        self.__files = ZipFile.get_files(self.__temp_content_dir)

        self.__in_context = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.readonly and self.__changed:
            current_files = ZipFile.get_files(self.__temp_content_dir)

            added_files =   [f for f in self.__files if f not in current_files]
            removed_files = [f for f in current_files if f not in self.__files]

            for f in added_files:
                copy_to = self.__temp_content_dir / f
                copy_from = self.__files[f]
                # print(f"Copy from {copy_from} -> {copy_to}")
                shutil.copy(copy_from, copy_to)
            for f in removed_files:
                # print(f"Remove {current_files[f]}")
                current_files[f].unlink()

            zip_file_path = shutil.make_archive(self.__temp_content_dir, 'zip', self.__temp_content_dir)
            shutil.copy(zip_file_path, self.save_path)

        shutil.rmtree(self.__temp_dir)

        self.__in_context = False

    def __init__(self, file_path, save_path=None, readonly=False):
        """
        mode = ["r" | "w"]
        if savepath is not specified it will overwrite the opened file at exit
        this can be probibited by specifying mode as readonly
        """
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
    
        self.file_path = file_path
        self.save_path = save_path if save_path != None else file_path
        self.readonly = readonly

        self.__files : dict[str, Path]= {}
    
        self.__changed = False
        self.__in_context = False
        self.__temp_dir = ""
        self.__temp_content_dir = ""

    def check_context(self):
        if not self.__in_context:
            raise Exception("Function or variable not accessable unless opened using 'with'")

    @property
    def files(self):
        self.check_context()

        return self.__files

    def add_file(self, file : Path, rel_path = ""):
        """
        Add something to the resource folder of the ssp.
        :param resource: filepath of the object to add.
        """
        self.check_context()
        if self.readonly:
            raise Exception("Changes are not allowed in readonly archive")

        self.__changed = True

        rel_path = str(Path(rel_path) / os.path.basename(file))
        if rel_path not in self.__files:
            self.__files[rel_path] = file

    def remove_file(self, rel_path):
        """
        relative path should be within the file, no slash in the begining
        e.g. embrace/SystemStructure.ssd
        """
        self.check_context()
        if self.readonly:
            raise Exception("Changes are not allowed in readonly archive")

        self.__changed = True

        if rel_path in self.__files:
            del self.__files[rel_path]
        else:
            raise FileNotFoundError(f"Not found {rel_path}")


class SSPFile(XMLFile, SSPStandard):

    @abstractmethod
    def __read__(self):
        pass

    @abstractmethod
    def __write__(self):
        pass

    def __check_compliance__(self):
        super().check_compliance(self.schemas[self.identifier], self.namespaces)

    @property
    def identifier(self):
        return self.__identifier

    @property
    def annotations(self):
        return self.__annotations

    def add_annotation(self, annotation: Annotation):
        self.annotations.add_annotation(annotation)

    def __enter__(self):
        register_namespaces()
        return self

    def __init__(self, file_path, mode='r', identifier='unknown'):

        self.__identifier = identifier
        self.__annotations = Annotations()
        super().__init__(file_path, mode)


class SSPElement(ABC):

    @abstractmethod
    def to_element(self) -> ET.Element:
        pass

    @abstractmethod
    def from_element(self, element: ET.Element):
        pass


class EmptyElement(ET.ElementBase):

    def __init__(self, tag, attrib=None, **kwargs):
        super().__init__(tag, attrib, **kwargs)

    def __repr__(self):
        return ET.tostring(self, encoding='utf-8')
