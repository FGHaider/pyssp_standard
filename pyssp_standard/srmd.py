import os
import pathlib

import hashlib
from pyssp_standard.utils import ModelicaXMLFile, XMLFile, BaseElement
from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.common_content_ssc import BaseElement
from lxml import etree as et
from lxml.etree import QName


class ClassificationEntry(BaseElement, ModelicaStandard):
    """SSP Traceability ClassificationEntry

    This class represents a generic ClassificationEntry. As the standard
    is very flexible in what the "value" of a classification entry can
    be, the aim is not to fit every usecase, but rather to expose all
    data required for most common usecases. Therefore, the support for
    values other than text is only what is necessary to read and write
    in a standard-compliant manner.
    """
    keyword: str
    type_: str
    link: str | None
    linked_type: str | None
    content: list[et._Element]
    text: str

    def __init__(self, keyword_or_element: str | et._Element,
                 type_="text/plain",
                 link=None,
                 linked_type=None,
                 content: list[et._Element] | None = None,
                 text: str = "",
                 **kwargs):
        """ Construct a classification entry.

        This constructor should be called with either an lxml Element
        or keyword parameters for creating a new Classification Entry.
        Passing keyword parameters when constructing from an Element
        will result in values from kw parameters being overriden by the
        values in the XML element, or set to None if not present in the
        XML element.
        """
        super().__init__(**kwargs)

        self.content = []
        self.text = ""
        self.type_ = type_
        self.link = link
        self.linked_type = linked_type

        if isinstance(keyword_or_element, et._Element):
            self.content = []
            self.__read__(keyword_or_element)
        elif isinstance(keyword_or_element, str):
            self.keyword = keyword_or_element
            if content is not None:
                self.content = content
            self.text = text
        else:
            raise TypeError(f"Can't init ClassificationEntry with {type(keyword_or_element)}")

    def __read__(self, element):
        self.update({"id": element.get("id"), "description": element.get("description")})

        self.keyword = element.attrib["keyword"]
        self.type_ = element.get("type", "text/plain")
        self.link = element.get(QName(self.namespaces["xlink"], "href"))
        self.linked_type = element.get("linkedType")

        if element.text is not None:
            self.text = element.text

        for child in element:
            self.content.append(child)

    def __repr__(self):
        return f"ClassificationEntry(keyword={self.keyword}, text={self.text!r} content={self.content})"

    def as_element(self):
        entry = et.Element(QName(self.namespaces['stc'], 'ClassificationEntry'), attrib={'keyword': self.keyword})
        entry.text = self.text
        entry.extend(self.content)

        super().update_root(entry)

        if self.type_ != "text/plain":  # Only write if the value differs from the default
            entry.set("type", self.type_)

        if self.link is not None:  # optional
            entry.set(QName(self.namespaces["xlink"], "href"), self.link)

        if self.linked_type is not None:  # optional
            entry.set("linkedType", self.linked_type)

        return entry


class Classification(BaseElement, ModelicaStandard):
    """SSP Traceability Classification.

    This class represents a generic Classification. For easiser parsing
    of specific Classification types, this class can be subclassed, and
    registered with the @classification_parser decorator. A possible
    way to implement this is shown in the documentation for that
    decorator.
    """
    classification_type: str
    link: str
    linked_type: str
    classification_entries: list[ClassificationEntry]

    def __init__(self,
                 type_or_element: str | et._Element,
                 link: str | None = None,
                 linked_type: str | None = None,
                 entries: list[ClassificationEntry] | None = None,
                 **kwargs):
        """ Construct a classification.

        This constructor should be called with either an lxml Element
        or keyword parameters for creating a new Classification.
        Passing keyword parameters when constructing from an Element
        will result in values from kw parameters being overriden by the
        values in the XML element, or set to None if not present in the
        XML element.
        """
        super().__init__(**kwargs)

        self.link = link
        self.linked_type = linked_type
        self.classification_entries = []

        if isinstance(type_or_element, et._Element):
            self.__read__(type_or_element)
        elif isinstance(type_or_element, str):
            self.classification_type = type_or_element
            self.classification_entries = [] if entries is None else entries
        else:
            raise TypeError(f"Can't init Classification with {type(type_or_element)}")

    def add_classification_entry(self, classification_entry: ClassificationEntry):
        self.classification_entries.append(classification_entry)

    def __read__(self, element):
        # BaseElement doesn't work well with inheritance
        self.update({"id": element.get("id"), "description": element.get("description")})

        self.classification_type = element.attrib["type"]
        self.link = element.get(QName(self.namespaces["xlink"], "href"))
        self.linked_type = element.get("linkedType")

        for entry in element.getchildren():
            self.add_classification_entry(ClassificationEntry(entry))

    def as_element(self):
        classification = et.Element(QName(self.namespaces['stc'], 'Classification'),
                                    attrib={'type': self.classification_type})

        super().update_root(classification)

        if self.link is not None:
            classification.set(QName(self.namespaces["xlink"], "href"), self.link)

        if self.linked_type is not None:
            classification.set("linkedType", self.link)

        for entry in self.classification_entries:
            classification.append(entry.as_element())

        return classification


classification_parsers: dict[str, Classification] = {}


def classification_parser(type_: str):
    """Decorator for registering a classification parser for a given type.

    The parser class' constructor will be called with the XML element as
    its only argument. The class is expected to have a method as_element(self)
    that returns the XML element representation of the parsed classification.

    For example: to parse the following classification schema
    <stc:Classification type="com.example.custom">
        <stc:ClassicationEntry keyword="test1">Value 1</stc:ClassificationEntry>
        <stc:ClassicationEntry keyword="test2">Value 2</stc:ClassificationEntry>
    </stc:Classification>
    one might do something like the following code snippet.

    >>> @classification_parser("com.example.custom")
    >>> class CustomClassification(Classification):
    >>>     test1: str
    >>>     test2: str

    >>>     def __init__(self, element=None, test1="", test2="", **kwargs):
    >>>         if element is not None:
    >>>             super().__init__(element)

    >>>             for entry in self.classification_entries:
    >>>                 if entry.keyword == "test1":
    >>>                     self.test1 = entry.text
    >>>                 elif entry.keyword == "test2":
    >>>                     self.test2 = entry.text
    >>>         else:
    >>>             super().__init__("com.example.custom", **kwargs)
    >>>             self.test1 = test1
    >>>             self.test2 = test2

    >>>     def as_element(self):
    >>>         self.classification_entries = [
    >>>                 ClassificationEntry("test1", text=self.test1),
    >>>                 ClassificationEntry("test2", text=self.test2)
    >>>         ]

    >>>         return super().as_element()
    """
    def decorator(parser):
        register_classification_parser(type_, parser)

        return parser

    return decorator


def classification_parser_for(type_: str) -> type:
    return classification_parsers.get(type_, Classification)


def register_classification_parser(type_: str, parser: type):
    classification_parsers[type_] = parser


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
        tree = et.parse(str(self.file_path))
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
            type_ = classification.attrib['type']
            cls = classification_parser_for(type_)  # select an appropriate parser based on the registry
            self.add_classification(cls(classification))

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
