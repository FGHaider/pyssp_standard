import tempfile
import pytest
from pathlib import Path
from pyssp_standard.ssd import SSD, Connection, System, DefaultExperiment, Component, Connector
import shutil


@pytest.fixture
def read_file():
    return Path("pytest/doc/embrace/SystemStructure.ssd")


@pytest.fixture
def modify_file():
    source_path = Path("pytest/doc/embrace/SystemStructure.ssd")
    test_file = Path("./test.ssd")
    shutil.copy(source_path, test_file)
    yield test_file
    test_file.unlink()


@pytest.fixture
def write_file():
    with tempfile.NamedTemporaryFile(delete_on_close=False) as f:
        f.close()
        yield f.name


def test_compliance_check(read_file):
    # Reference file is known to be good, no error should be raised.
    with SSD(read_file) as file:
        file.__check_compliance__()


def test_list_connectors(read_file):
    with SSD(read_file) as file:
        found = file.list_connectors(parent='Consumer')
    assert len(found) == 1


def test_modify(modify_file):
    with SSD(modify_file, 'a') as file:
        file.add_connection(Connection(start_element="house", start_connector="garage",
                                       end_element="work", end_connector="parking"))

        file.remove_connection(Connection(start_element="Atmos", start_connector="Tamb",
                                          end_element="Consumer", end_connector="Tamb"))
        file.__check_compliance__()


def test_create_ssd(write_file):
    with SSD(write_file, mode="w") as ssd:
        ssd.name = "Test SSD"
        ssd.version = "1.0"

        ssd.default_experiment = DefaultExperiment()
        ssd.default_experiment.start_time = 0.0
        ssd.default_experiment.stop_time = 1.0

        fmu = Component()
        fmu.name = "component"
        fmu.component_type = "application/x-fmu-sharedlibrary"
        fmu.source = "resources/example.fmu"
        fmu.implementation = "CoSimulation"

        fmu.connectors.append(Connector(None, "x", "output"))

        ssd.system = System(None, "system")
        ssd.system.elements.append(fmu)

        ssd.system.connectors.append(Connector(None, "x", "output"))
        ssd.add_connection(Connection(start_element="component", start_connector="x", end_connector="x"))

    with SSD(write_file, mode="r") as ssd:
        assert ssd.name == "Test SSD"
        assert ssd.version == "1.0"

        assert ssd.default_experiment.start_time == 0.0
        assert ssd.default_experiment.stop_time == 1.0

        assert len(ssd.system.elements) == 1
        fmu = ssd.system.elements[0]

        assert isinstance(fmu, Component)
        assert fmu.name == "component"
        assert fmu.component_type == "application/x-fmu-sharedlibrary"
        assert fmu.source == "resources/example.fmu"
        assert fmu.implementation == "CoSimulation"

        assert len(fmu.connectors) == 1
        fmu_conn = fmu.connectors[0]
        assert fmu_conn.name == "x"
        assert fmu_conn.kind == "output"

        assert len(ssd.system.connectors) == 1
        sys_conn = ssd.system.connectors[0]
        assert sys_conn.name == "x"
        assert sys_conn.kind == "output"

        assert len(ssd.connections()) == 1
        connection = ssd.connections()[0]

        assert connection.start_element == "component"
        assert connection.start_connector == "x"
        assert connection.end_element is None
        assert connection.end_connector == "x"
