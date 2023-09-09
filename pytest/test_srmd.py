from pyssp_standard.srmd import SRMD, Classification, ClassificationEntry
import pytest
from pathlib import Path


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