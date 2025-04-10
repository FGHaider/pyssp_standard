import pytest
from pyssp_standard.common_content_ssc import Annotations, Annotation, Enumerations, Enumeration, BaseElement, Item


def test_annotation_creation():
    annotation = Annotation('Comment')
    annotation.add_text('This is a comment')
    annotations = Annotations()
    annotations.add_annotation(annotation)
    assert annotations.is_empty() is False


def test_enumerations():
    items = [Item("test_a", 1), Item("test_b", 2)]

    enum = Enumeration(name="test_enum", items=items)
    enums = Enumerations([enum])

    elem = enums.as_element()

    enums2 = Enumerations(elem)
    enum2 = enums2.enumerations[0]
    print(enums2.enumerations)
    print(enum2.items, items)
    assert enum2.items == items
    assert enum2.name == "test_enum"


