
import pytest
from pyssp_standard.common_content_ssc import Annotations, Annotation, BaseElement, TopLevelMetaData


def test_annotation_creation():
    annotation = Annotation('Comment')
    annotation.add_text('This is a comment')
