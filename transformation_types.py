from typing import TypedDict


class Transformation(TypedDict):
    pass


class LinearTransformation(Transformation):
    factor: float  # default 1.0
    offset: float  # default 0.0


class BooleanMappingTransformation(Transformation):
    source: bool
    target: bool


class IntegerMappingTransformation(Transformation):
    source: int
    target: int


class EnumerationMappingTransformation(Transformation):
    source: str
    target: str

