import pytest
from pathlib import Path
from pyssp.fmu import FMU


@pytest.fixture
def read_file():
    return Path("doc/embrace/resources/0001_ECS_HW.fmu")


def test_variable_unpacking(read_file):  # Asserts that reading a known correct file does not raise an exception
    with FMU(read_file) as file:
        inputs = file.inputs
        outputs = file.outputs
        parameters = file.parameters
    assert len(inputs) > 0
    assert len(outputs) > 0
    assert len(parameters) > 0


def test_get_variables(read_file):
    with FMU(read_file) as file:
        no_matches = file.get('none', 'none')
        matches_causality = file.get(causality='parameter')
        matches_variability = file.get(variability='tunable')
        matches = file.get('parameter', 'tunable')
    assert len(no_matches) == 0
    assert len(matches_variability) >= len(matches)
    assert len(matches_causality) >= len(matches)
