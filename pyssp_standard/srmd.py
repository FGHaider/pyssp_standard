import os
import pathlib

import hashlib
from pyssp_standard.utils import ModelicaXMLFile, XMLFile
from pyssp_standard.standard import ModelicaStandard
from lxml import etree as et
from lxml.etree import QName


class ClassificationEntry(ModelicaStandard):
    def __init__(self, keyword: str = None, content: str = None, *, element=None):
        self.keyword = keyword
        self.content = content
        if element is not None:
            self.__read__(element)

    def __read__(self, element):
        pass

    def as_element(self):
        entry = et.Element(QName(self.namespaces['stc'], 'ClassificationEntry'), attrib={'keyword': self.keyword})
        entry.text = self.content
        return entry


class Classification(ModelicaStandard):

    def __init__(self, classification_type: str = None, *, element=None):
        self.__classification_entries = []
        self.__classification_type = classification_type
        if element is not None:
            self.__read__(element)

    def add_classification_entry(self, classification_entry: ClassificationEntry):
        self.__classification_entries.append(classification_entry)

    def __read__(self, element):
        pass

    def as_element(self):
        classification = et.Element(QName(self.namespaces['stc'], 'Classification'),
                                    attrib={'type': self.__classification_type})
        for entry in self.__classification_entries:
            classification.append(entry.as_element())

        return classification


class SRMD(ModelicaXMLFile):

    def __init__(self, file_path, mode='r'):
        self.name = os.path.basename(file_path)
        self.classifications = []
        self.data = None
        self.checksum = None
        self.checksum_type = "SHA3-256"
        self.version = "1.0.0-beta2"

        super().__init__(file_path, mode, "srmd11")

    def assign_data(self, filepath, create_checksum=True):
        if type(filepath) is not pathlib.PosixPath:
            filepath = pathlib.Path(filepath)
        self.data = str(filepath)

        if create_checksum:
            with open(filepath) as file:
                data = file.read()
                self.checksum = hashlib.sha3_256(data.encode()).hexdigest()

    def __read__(self):
        tree = et.parse(self.file_path)
        self.root = tree.getroot()
        self.version = self.root.get('version')
        self.name = self.root.get('name')
        self.data = self.root.get('data')
        self.checksum = self.root.get('checksum')
        self.checksum_type = self.root.get('checksumType')

        self.top_level_metadata.update(self.root.attrib)
        self.base_element.update(self.root.attrib)

        classifications = self.root.findall('stc:Classification', self.namespaces)
        for classification in classifications:
            self.add_classification(Classification(element=classification))

    def __write__(self):
        attributes = {'version': self.version, 'name': self.name}
        if self.data is not None:
            attributes['data'] = self.data
        if self.checksum is not None:
            attributes['checksum'] = self.checksum
            attributes['checksumType'] = self.checksum_type

        self.root = et.Element(QName(self.namespaces['srmd'], 'SimulationResourceMetaData'), attrib=attributes)
        self.root = self.top_level_metadata.update_root(self.root)
        self.root = self.base_element.update_root(self.root)
        for classification in self.classifications:
            self.root.append(classification.as_element())

    def add_classification(self, classification: Classification):
        self.classifications.append(classification)
