from pyssp_standard import SRMD, Classification, ClassificationEntry, classification_parser
import pytest
from pathlib import Path
import hashlib
from dataclasses import dataclass
import io

from lxml import etree as et


@pytest.fixture
def write_file():
    test_file = Path('./test.srmd')
    yield test_file
    if test_file.exists():
        test_file.unlink()


def test_read_srmd():
    print()
    test_file = Path('pytest/doc/test_schema_validation.srmd')
    with SRMD(test_file, 'r') as file:
        file.__check_compliance__()


def test_create_srmd(write_file):
    print()
    with SRMD(write_file, 'w') as file:
        classification = Classification('test')
        classification.add_classification_entry(ClassificationEntry('test', 'This is a test'))
        file.add_classification(classification)
        file.__check_compliance__()


def test_read_write_srmd_simple(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification("com.example.simple")
        classification.add_classification_entry(
                ClassificationEntry("key1", text="value1"))

        file.add_classification(classification)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.simple"
        assert len(classification.classification_entries) == 1
        entry = classification.classification_entries[0]

        assert entry.keyword == "key1"
        assert entry.text == "value1"
        assert len(entry.content) == 0


def test_read_write_srmd_multiple(write_file):
    data = {
           "com.example.mult1": {"key1": "value1", "key2": "value2"},
           "com.example.mult2": {"key3": "value3"}
            }

    with SRMD(write_file, 'w') as file:
        for classification_type, entries in data.items():
            classification = Classification(classification_type)
            for key, value in entries.items():
                classification.add_classification_entry(ClassificationEntry(key, text=value))

            file.add_classification(classification)

    actual = {}
    with SRMD(write_file) as file:
        for classification in file.classifications:
            entries = {}
            for entry in classification.classification_entries:
                entries[entry.keyword] = entry.text

            actual[classification.classification_type] = entries

    assert actual == data


def test_read_write_srmd_duplicate(write_file):
    data = {
           "com.example.duplicate": [("key1", "value1"), ("key2", "value2")],
            }

    with SRMD(write_file, 'w') as file:
        for classification_type, entries in data.items():
            classification = Classification(classification_type)
            for key, value in entries:
                classification.add_classification_entry(ClassificationEntry(key, text=value))

            file.add_classification(classification)

    actual = {}
    with SRMD(write_file) as file:
        for classification in file.classifications:
            entries = []
            for entry in classification.classification_entries:
                entries.append((entry.keyword, entry.text))

            actual[classification.classification_type] = entries

    assert actual == data


def test_read_write_srmd_xml(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification(
                "com.example.xml",
                link="test.txt",
                linked_type="text/plain"
        )
        elem = et.Element("a")
        elem.append(et.Element("b", example="attribute"))

        classification.add_classification_entry(
                ClassificationEntry("key1", type_="application/xml", content=[elem]))

        file.add_classification(classification)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.xml"
        assert len(classification.classification_entries) == 1
        entry = classification.classification_entries[0]

        assert entry.keyword == "key1"
        assert entry.text == ""
        assert entry.type_ == "application/xml"
        assert len(entry.content) == 1

        elem = entry.content[0]
        assert elem.tag == "a"
        assert len(elem) == 1

        child = elem[0]
        assert child.tag == "b"
        assert child.get("example") == "attribute"


def test_read_write_srmd_attrs(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification(
                "com.example.attrs",
                description="Test"
        )

        classification.add_classification_entry(
                ClassificationEntry("key1", description="Test2", text="Testing"))

        file.add_classification(classification)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.attrs"
        assert len(classification.classification_entries) == 1
        assert classification.description == "Test"
        entry = classification.classification_entries[0]

        assert entry.keyword == "key1"
        assert entry.text == "Testing"
        assert entry.description == "Test2"


@classification_parser("com.example.custom")
class CustomClassification(Classification):
    test1: str
    test2: str

    def __init__(self, element=None, test1="", test2="", **kwargs):
        if element is not None:
            super().__init__(element)

            for entry in self.classification_entries:
                if entry.keyword == "test1":
                    self.test1 = entry.text
                elif entry.keyword == "test2":
                    self.test2 = entry.text
        else:
            super().__init__("com.example.custom", **kwargs)
            self.test1 = test1
            self.test2 = test2

    def as_element(self):
        self.classification_entries = [
                ClassificationEntry("test1", text=self.test1),
                ClassificationEntry("test2", text=self.test2)
        ]

        return super().as_element()


def test_read_write_srmd_custom_parser(write_file):
    with SRMD(write_file, 'w') as file:
        classification = CustomClassification(
            test1="testing1",
            test2="testing2"
        )
        file.add_classification(classification)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.custom"
        assert isinstance(classification, CustomClassification)

        assert classification.test1 == "testing1"
        assert classification.test2 == "testing2"


@dataclass
class Parent:
    name: str
    occupation: str

    def to_xml(self):
        element = et.Element("Parent")
        element.set("name", self.name)
        element.set("occupation", self.occupation)

        return element

    @classmethod
    def from_xml(cls, element):
        return cls(element.get("name"), element.get("occupation"))


@dataclass
class Child:
    name: str
    age: int

    def to_xml(self):
        element = et.Element("Child")
        element.set("name", self.name)
        element.set("age", str(self.age))

        return element

    @classmethod
    def from_xml(cls, element):
        return cls(element.get("name"), int(element.get("age")))


@dataclass
class Family:
    parents: list[Parent]
    children: list[Child]

    def to_xml(self):
        element = et.Element("Family")
        element.extend([parent.to_xml() for parent in self.parents])
        element.extend([child.to_xml() for child in self.children])

        return element

    @classmethod
    def from_xml(cls, element):
        parents = [Parent.from_xml(el) for el in element.findall("Parent")]
        children = [Child.from_xml(el) for el in element.findall("Child")]

        return Family(parents, children)


@classification_parser("com.example.custom2")
class CustomClassification2(Classification):
    example: Family

    def __init__(self, element=None, example="", **kwargs):
        if element is not None:
            super().__init__(element)

            for entry in self.classification_entries:
                if entry.keyword == "example":
                    self.example = Family.from_xml(entry.content[0])
        else:
            super().__init__("com.example.custom2", **kwargs)
            self.example = example

    def as_element(self):
        self.classification_entries = [
                ClassificationEntry("example", content=[self.example.to_xml()])
        ]

        return super().as_element()


def test_read_srmd_custom_parser_xml(write_file):
    srmd_source = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<srmd:SimulationResourceMetaData version="1.0.0" name="Example"
        xmlns:srmd="http://ssp-standard.org/SSPTraceability1/SimulationResourceMetaData"
        xmlns:stc="http://ssp-standard.org/SSPTraceability1/SSPTraceabilityCommon">
    <stc:Classification type="com.example.custom2">
        <stc:ClassificationEntry keyword="example">
            <Family>
                <Parent name="Alice" occupation="engineer" />
                <Parent name="Bob" occupation="programmer" />
                <Child name="Eve" age="15" />
            </Family>
        </stc:ClassificationEntry>
    </stc:Classification>
</srmd:SimulationResourceMetaData>
    """
    with open(write_file, "w") as f:
        f.write(srmd_source)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.custom2"
        assert isinstance(classification, CustomClassification2)

        assert isinstance(classification.example, Family)
        family = classification.example

        assert len(family.parents) == 2
        assert len(family.children) == 1

        assert family.parents[0].name == "Alice"
        assert family.parents[0].occupation == "engineer"

        assert family.parents[1].name == "Bob"
        assert family.parents[1].occupation == "programmer"

        assert family.children[0].name == "Eve"
        assert family.children[0].age == 15


def test_read_write_srmd_custom_parser_xml(write_file):
    with SRMD(write_file, 'w') as file:
        classification = CustomClassification2(
            example=Family(
                [Parent("Alice", "engineer"), Parent("Bob", "programmer")],
                [Child("Eve", 15)]
            )
        )
        file.add_classification(classification)

    with SRMD(write_file) as file:
        assert len(file.classifications) == 1
        classification = file.classifications[0]
        assert classification.classification_type == "com.example.custom2"
        assert isinstance(classification, CustomClassification2)

        assert isinstance(classification.example, Family)
        family = classification.example

        assert len(family.parents) == 2
        assert len(family.children) == 1

        assert family.parents[0].name == "Alice"
        assert family.parents[0].occupation == "engineer"

        assert family.parents[1].name == "Bob"
        assert family.parents[1].occupation == "programmer"

        assert family.children[0].name == "Eve"
        assert family.children[0].age == 15


def test_data_assign(write_file):
    print()
    test_file = Path('pytest/doc/embrace/CONOPS.csv')
    with SRMD(write_file, 'w') as file:
        file.assign_data(test_file)
        checksum = file.checksum
    with open(test_file) as file:
        data = file.read()
        assert hashlib.sha3_256(data.encode()).hexdigest() == checksum
