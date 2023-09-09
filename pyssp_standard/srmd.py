from pyssp_standard.common_content_ssc import BaseElement, TopLevelMetaData
from pyssp_standard.utils import XMLFile
from pyssp_standard.standard import SRMDStandard
from lxml import etree as et
from lxml.etree import QName


def register_namespaces():
    srmd_standards = SRMDStandard
    for name, url in srmd_standards.namespaces.items():
        et.register_namespace(name, url)


class ClassificationEntry(SRMDStandard):
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


class Classification(SRMDStandard):

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


class SRMD(XMLFile, SRMDStandard):

    def __init__(self, file_path, mode='r', name='unnamed'):
        self.__base_element: BaseElement = BaseElement()
        self.__top_level_metadata: TopLevelMetaData = TopLevelMetaData()
        self.__name = name
        self.__classifications = []

        super().__init__(file_path, mode)

    def __check_compliance__(self):
        super().check_compliance(self.schema, self.namespaces)

    @property
    def BaseElement(self):
        return self.__base_element

    @property
    def TopLevelMetaData(self):
        return self.__top_level_metadata

    def __read__(self):
        self.__tree = et.parse(self.file_path)
        self.root = self.__tree.getroot()
        self.__top_level_metadata.update(self.root.attrib)
        self.__base_element.update(self.root.attrib)

        classifications = self.root.findall('stc:Classification', self.namespaces)
        for classification in classifications:
            self.add_classification(Classification(element=classification))

    def __enter__(self):
        register_namespaces()
        return self

    def __write__(self):
        self.root = et.Element(QName(self.namespaces['srmd'], 'SimulationResourceMetaData'),
                               attrib={'version': '1.0.0-beta2', 'name': self.__name})
        self.root = self.__top_level_metadata.update_root(self.root)
        self.root = self.__base_element.update_root(self.root)
        for classification in self.__classifications:
            self.root.append(classification.as_element())

    def add_classification(self, classification: Classification):
        self.__classifications.append(classification)
