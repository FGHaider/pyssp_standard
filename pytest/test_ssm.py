import pytest
from pathlib import Path
from pyssp_standard.ssm import SSM


@pytest.fixture
def read_file():
    return Path("doc/embrace/resources/ECS_HW.ssm")


def test_read_correct_file(read_file):  # Asserts that reading a known correct file does not raise an exception

    with SSM(read_file) as file:
        print(file)
        file.__check_compliance__()


def test_create_basic_file():

    with SSM("./test.ssm", 'w') as f:
        f.add_mapping('dog', 'shepard')
        f.add_mapping('cat', 'odd')
        f.__check_compliance__()
