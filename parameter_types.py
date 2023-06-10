from typing import TypedDict
import xml.etree.cElementTree as ET


class ParameterType:

    def __init__(self, parameter_type=None, attributes=None):

        if type(parameter_type) is ET.Element:
            self.parameter_type = parameter_type.tag.split('}')[-1]
            self.parameter = self.__create_parameter__(self.parameter_type, parameter_type.attrib)
        elif type(parameter_type) is str:
            self.parameter_type = parameter_type
            self.parameter = self.__create_parameter__(parameter_type, attributes)

    def element(self):
        return ET.Element(f'ssv:{self.parameter_type}', attrib=self.parameter)

    @staticmethod
    def __create_parameter__(ptype, attributes):
        value = attributes.get('value')
        name = attributes.get('name')
        unit = attributes.get('unit')
        mimetype = attributes.get('mem-type')

        parameter_types = {
            'Real': lambda: Real(value=value, unit=unit),
            'Integer': lambda: Integer(value=value),
            'Boolean': lambda: Boolean(value=value),
            'String': lambda: String(value=value),
            'Enumeration': lambda: Enumeration(value=value, name=name),
            'Binary': lambda: Binary(value=value, mimetype=mimetype)
        }

        return parameter_types.get(ptype, lambda: None)()


class ParameterValueType(TypedDict):
    pass


class Real(ParameterValueType):
    value: float
    unit: str


class Integer(ParameterValueType):
    value: int


class Boolean(ParameterValueType):
    value: bool


class String(ParameterValueType):
    value: str


class Enumeration(ParameterValueType):
    value: str
    name: str


class Binary(ParameterValueType):
    mimetype: str  # default 'application/octet-stream'
    value: str  # should be hexadecimal
