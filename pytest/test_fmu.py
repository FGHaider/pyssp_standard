import shutil
import pytest
from pathlib import Path
from pyssp_standard.fmu import FMU, ModelDescription


@pytest.fixture
def fmu_file():
    return Path("doc/embrace/resources/0001_ECS_HW.fmu")

@pytest.fixture
def md_file():
    return Path("doc/embrace/fmu/modelDescription.xml")

def test_unpacking_packing(fmu_file):
    print()
    test_fmu_file = Path('./ecs.fmu')
    shutil.copy(fmu_file, test_fmu_file)

    with FMU(test_fmu_file) as fmu:

        md = fmu.model_description
        
        assert len(fmu.binaries) > 0
        assert len(fmu.documentation) > 0

    test_fmu_file.unlink()

def test_variable_unpacking(md_file):  # Asserts that reading a known correct file does not raise an exception
    with ModelDescription(md_file) as md:
        inputs = md.inputs
        outputs = md.outputs
        parameters = md.parameters
    assert len(inputs) > 0
    assert len(outputs) > 0
    assert len(parameters) > 0

def test_get_variables(md_file):
    with ModelDescription(md_file) as file:
        no_matches = file.get('none', 'none')
        matches_causality = file.get(causality='parameter')
        matches_variability = file.get(variability='tunable')
        matches = file.get('parameter', 'tunable')
    assert len(no_matches) == 0
    assert len(matches_variability) >= len(matches)
    assert len(matches_causality) >= len(matches)
