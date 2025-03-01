import pytest
from pathlib import Path
from pyssp_standard.ssm import SSM
from pyssp_standard.transformation_types import Transformation
from lxml.etree import _Element


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace/resources/ECS_HW.ssm")


@pytest.fixture
def write_file():
    test_file = Path("./test.ssm")
    yield test_file
    test_file.unlink()


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception

    with SSM(read_file) as file:
        print(file)
        file.__check_compliance__()


def test_create_and_edit_basic_file(write_file):

    with SSM(write_file, 'w') as f:
        f.add_mapping('dog', 'shepard')
        f.add_mapping('cat', 'odd', transformation=Transformation('LinearTransformation', {'factor': 2, 'offset': 0}))
        f.__check_compliance__()

    with SSM(write_file, 'a') as f:
        f.edit_mapping(target='shepard', source='tax', suppress_unit_conversion=True)
        f.__check_compliance__()


def test_transformations_creation():
    linear_trans = Transformation('LinearTransformation', attributes={'factor': 1, 'offset': 0})
    assert type(linear_trans.element()) is _Element
    boolean_trans = Transformation('BooleanMappingTransformation', attributes={'source': 'cat', 'target': 'shelf'})
    assert type(boolean_trans.element()) is _Element
    enum_trans = Transformation('EnumerationMappingTransformation', attributes={'source': 'cat', 'target': 'shelf'})
    assert type(enum_trans.element()) is _Element
    int_trans = Transformation('IntegerMappingTransformation', attributes={'source': 'cat', 'target': 'shelf'})
    assert type(int_trans.element()) is _Element
