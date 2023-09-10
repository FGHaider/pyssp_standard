from pyssp_standard.srmd import SRMD, Classification, ClassificationEntry
import pytest
from pathlib import Path
import hashlib


@pytest.fixture
def write_file():
    test_file = Path('./test.srmd')
    yield test_file
    test_file.unlink()


def test_create_srmd(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification(classification_type='test')
        classification.add_classification_entry(ClassificationEntry('test', 'This is a test'))
        file.add_classification(classification)
        #file.__check_compliance__()


def test_data_assign(write_file):
    test_file = Path('./doc/embrace/CONOPS.csv')
    with SRMD(write_file, 'w') as file:
        file.assign_data(test_file)
        checksum = file.checksum
    with open(test_file) as file:
        data = file.read()
        assert hashlib.sha3_256(data.encode()).hexdigest() == checksum
