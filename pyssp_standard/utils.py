
import shutil
import tempfile
from pathlib import Path, PosixPath
from abc import ABC, abstractmethod
import zipfile
import xmlschema
import os
from lxml import etree as ET

from pyssp_standard.common_content_ssc import Annotations, Annotation, BaseElement, TopLevelMetaData
from pyssp_standard.standard import ModelicaStandard


def register_namespaces():
    for name, url in ModelicaStandard.namespaces.items():
        ET.register_namespace(name, url)


class XMLFile(ABC):
    """
    Base for all xml files
    """

    @abstractmethod
    def __read__(self):
        """
        Fill class with information from xml file
        """
        pass

    @abstractmethod
    def __write__(self):
        """
        Write class data to xml objec
        """
        pass

    @property
    def BaseElement(self):
        return self.base_element

    @property
    def TopLevelMetaData(self):
        return self.top_level_metadata

    def __init__(self, file_path, mode='r'):
        """
        :param mode: [r]ead, [a]ppend or [w]rite
        """
        self.__mode = mode
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
    
        self.__file_path = file_path
        self.root = None
        self.base_element: BaseElement = BaseElement()
        self.top_level_metadata: TopLevelMetaData = TopLevelMetaData()

        if mode == 'r' or mode == 'a':
            self.__read__()

    def write_to_file(self, filepath):
        xml_string = ET.tostring(self.root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        with open(filepath, 'wb') as file:
            file.write(xml_string)

    def check_compliance(self, schema, namespaces):
        # check name for indications that xsd 1.1 should be used, 1.0 is the default
        if "11" in str(schema):
            schema = xmlschema.XMLSchema11(schema)
        else:
            schema = xmlschema.XMLSchema10(schema)

        if self.__mode in ['a', 'w']:  # Temporary file creation
            with tempfile.TemporaryDirectory(suffix="_pyssp") as temp_dir:
                temp_file_path = Path(temp_dir) / 'tmp.xml'
                self.__write__()
                self.write_to_file(temp_file_path)

                xmlschema.validate(temp_file_path, schema, namespaces=namespaces)
        else:
            xmlschema.validate(self.file_path, schema, namespaces=namespaces)

    @property
    def file_path(self):
        return self.__file_path

    def __save__(self):
        """
        Write xml object to file
        """
        self.write_to_file(self.__file_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mode in ['w', 'a']:
            self.__write__()
            self.__save__()


class ModelicaXMLFile(XMLFile, ModelicaStandard):
    """
    Base Class for all spp xml files
    """

    def __read__(self):
        pass

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


class ZIPFile:
    """
    All operations need to be in context and will be applied against temp dir
    
    """

    def __enter__(self):
        self.__temp_path = Path(tempfile.mkdtemp(prefix="pyssp_"))
        self.__unpacked_path = self.__temp_path / self.file_path.stem

        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.__unpacked_path)

        self.__in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.readonly and self.__changed:

            zip_file_path = shutil.make_archive(self.__unpacked_path, 'zip', self.__unpacked_path)
            shutil.copy(zip_file_path, self.save_path)

        shutil.rmtree(self.__temp_path)
        
        self.__in_context = False

    def __init__(self, source_path : Path, target_path: Path=None, readonly=False):
        """
        if target_path is not specified it will overwrite the opened file at exit
        this can be probibited by specifying readonly
        """
        if type(source_path) is not PosixPath:
            source_path = Path(source_path)
    
        self.file_path = source_path
        self.save_path = target_path if target_path != None else source_path
        self.readonly = readonly

        self.__changed = False
        self.__in_context = False
        self.__temp_path = ""
        self.__unpacked_path = ""

    def check_context(self):
        if not self.__in_context:
            raise Exception("Function or variable not accessable unless opened using 'with'")

    @staticmethod
    def get_files(dir : Path):
        return {os.path.relpath(p, dir):p for p in dir.rglob('*')}

    @property
    def unpacked_path(self):
        self.check_context()
        return self.__unpacked_path

    @property
    def __files(self):
        """
        get at dict with [rel_path:abs_path]
        """
        return self.get_files(self.__unpacked_path)

    @property
    def files_rel(self):
        """
        get a list of files relative to zip file
        """
        self.check_context()
        return self.__files.keys()
    
    @property
    def files_abs(self):
        """
        get a list of files, with absolute path within the temp dir
        """
        self.check_context()
        return self.__files.values()

    def get_file_temp_path(self, rel_path):
        """
        translate from rel_path to abs_path
        
        """
        self.check_context()
        return self.__files[rel_path]
        
    def add_file(self, file : Path, rel_path = ""):
        """
        Add something to the resource folder of the ssp.
        :param file: filepath of the object to add.
        :param rel_path: relative path inside archive, omitt '/' in the beginning 
        """
        self.check_context()
        if self.readonly:
            raise Exception("Changes are not allowed in readonly archive")

        self.__changed = True
        rel_path = os.path.join(rel_path, os.path.basename(file))
    
        if rel_path not in self.files_rel:
            shutil.copy(file, self.__unpacked_path / rel_path)

    def remove_file(self, rel_path):
        """
        relative path should be within the file, no slash in the begining
        e.g. SystemStructure.ssd
        """
        self.check_context()
        if self.readonly:
            raise Exception("Changes are not allowed in readonly archive")

        self.__changed = True
        file : Path = self.__unpacked_path / rel_path

        if file.exists():
            file.unlink()
        else:
            raise FileNotFoundError(f"Not found {file}")
        

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
