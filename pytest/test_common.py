
import pytest
from pyssp_standard.common_content_ssc import Annotations, Annotation


def test_annotation_creation():
    annotation = Annotation('Comment')
    annotation.add_text('This is a comment')
    annotations = Annotations()
    annotations.add_annotation(annotation)
    assert annotations.is_empty() is False
