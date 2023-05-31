from typing import TypedDict


class ParameterType(TypedDict):
    pass


class Real(ParameterType):
    value: float
    unit: str


class Integer(ParameterType):
    value: int


class Boolean(ParameterType):
    value: bool


class String(ParameterType):
    value: str


class Enumeration(ParameterType):
    value: str
    name: str


class Binary(ParameterType):
    mimetype: str  # default 'application/octet-stream'
    value: str  # should be hexadecimal
