import shutil
import tempfile
import zipfile
import itertools
from pathlib import Path, PosixPath
from dataclasses import dataclass
from lxml import etree as et

from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.utils import ModelicaXMLFile, ZIPFile
from pyssp_standard.unit import Units
from pyssp_standard.common_content_ssc import (
    TypeChoice,
    Enumeration,
    TypeReal,
    TypeInteger,
    TypeBoolean,
    TypeString,
)


@dataclass
class ScalarVariable:
    name: str
    description: str
    causality: str
    variability: str
    type_: TypeChoice


class VariableList(list):

    def __repr__(self):
        print_out = \
f"""{'_'*100}
VariableList:
"""
        for item in self:
            print_out += \
f"""{'_'*20}
    Name:        {item.name}
    Description: {item.description}
    Variability: {item.variability}
    Causality:   {item.causality}
"""
        print_out += f"{'_' *100}\n"
        return print_out


class SimpleType:
    name: str
    description: str
    type_: Enumeration | TypeReal | TypeInteger | TypeBoolean | TypeString
    kind: str

    def __init__(self, name, type_, description=None, kind=None):
        self.name = name
        self.type_ = type_
        self.description = description
        self.kind = kind

    @classmethod
    def from_xml(cls, elem):
        name = elem.get("name")
        description = elem.get("description")
        type_kind = elem[0].tag
        if type_kind == "Real":
            type_ = TypeReal.from_xml(elem[0])
        elif type_kind == "Integer":
            type_ = TypeInteger.from_xml(elem[0])
        elif type_kind == "Boolean":
            type_ = TypeBoolean.from_xml(elem[0])
        elif type_kind == "String":
            type_ = TypeString.from_xml(elem[0])
        elif type_kind == "Enumeration":
            type_ = Enumeration.from_xml_fmi(name, description, elem[0])
        else:
            raise ValueError("Element is not a valid type choice element.")

        return cls(name, type_, description, type_kind)


class TypeDefinitions:
    types: list[Enumeration | TypeReal | TypeInteger | TypeBoolean | TypeString]

    def __init__(self, types):
        self.types = types

    def __len__(self):
        return len(self.types)

    def __getitem__(self, idx):
        return self.types[idx]

    def __setitem__(self, idx, val):
        self.types[idx] = val

    @classmethod
    def from_xml(cls, elem):
        children = elem.findall("SimpleType")

        return cls([SimpleType.from_xml(child) for child in children])


def _to_camel_case(snake_case):
    """Convert from snake_case to camelCase"""

    parts = snake_case.split("_")
    return "".join(itertools.chain(parts[:1], (part.capitalize() for part in parts[1:])))


class ModelDescription(ModelicaXMLFile):
    """FMI Model Description"""

    fmi_version: str
    model_name: str
    guid: str
    description: str | None
    author: str | None
    version: str | None
    copyright: str | None
    license: str | None
    generation_tool: str | None
    generation_date_and_time: str | None
    variable_naming_convention: str | None

    def __repr__(self):
        return \
f"""{'_'*100}
ModelDescription:
    Model Name:  {self.model_name}
    FMI Version: {self.fmi_version}
    Filepath:    {self.file_path}
{'_'*100}
"""

    def __init__(self, file_path, mode='r'):
        self.__variables: VariableList[ScalarVariable] = VariableList()
        self.type_defs = None
        self.units = None

        for name in self.__annotations__:
            setattr(self, name, None)

        super().__init__(file_path, mode, "fmi30")

    def __read__(self):
        tree = et.parse(str(self.file_path))
        root = tree.getroot()

        for name in self.__annotations__:
            xml_name = _to_camel_case(name)
            setattr(self, name, root.get(xml_name))

        model_variables = root.findall('ModelVariables')[0]
        scalar_variables = model_variables.findall('ScalarVariable')
        for scalar in scalar_variables:
            name = scalar.get('name')
            description = scalar.get('description')
            causality = scalar.get('causality')
            variability = scalar.get('variability')
            type_ = TypeChoice.from_xml(scalar.xpath(TypeChoice.XPATH_FMI)[0])
            scalar_variable = ScalarVariable(
                name=name,
                description=description,
                variability=variability,
                causality=causality,
                type_=type_,
            )
            self.__variables.append(scalar_variable)

        unit_defs = root.find("UnitDefinitions")
        if unit_defs is not None:
            self.units = Units(unit_defs)

        type_defs = root.find("TypeDefinitions")
        if type_defs is not None:
            self.type_defs = TypeDefinitions.from_xml(type_defs)

    def __write__(self):
        pass

    @property
    def parameters(self) -> VariableList:
        return VariableList([item for item in self.__variables if item.causality == 'parameter'])

    @property
    def outputs(self) -> VariableList:
        return VariableList([item for item in self.__variables if item.causality == 'output'])

    @property
    def inputs(self) -> VariableList:
        return VariableList([item for item in self.__variables if item.causality == 'input'])

    def exist(self, name: str):
        """ Returns true if a scalar variable exist with the given name """
        for entry in self.__variables:
            if entry.name == name:
                return True
        return False

    def get(self, causality: str = None, variability: str = None) -> VariableList:
        """
        Get a variable from the FMU, based on the attributes' causality, variability.
        :param causality: parameter, input etc.
        :param variability: fixed, tunable etc.
        :return: list of matching variables
        """
        return VariableList([item for item in self.__variables
                             if (causality is None or item.causality == causality) and
                             (variability is None or item.variability == variability)])

    def variables(self) -> VariableList:
        return self.__variables


class FMU(ZIPFile):
    """This class allows for peeking into a FMU file, it by no means covers the entirety of the FMI standard and should
            primarily be considered as a debugging tool for looking of model input, outputs and parameters.
    """

    def __enter__(self):
        super().__enter__()
        self.fmu_binaries_path = self.unpacked_path / 'binaries'
        self.fmu_documentation_path = self.unpacked_path / 'documentation'

        return self

    def __init__(self, source_path, target_path=None, mode="a", readonly=None):
        super().__init__(source_path, target_path, mode=mode, readonly=readonly)
        self.fmu_binaries_path: Path = None
        self.fmu_documentation_path: Path = None

    def __str__(self) -> str:
        nl = "\t\n - "
        return f"""
{'_'*100}
FMU:
    Path       {self.file_path}
    Temp_dir:  {self.unpacked_path}
    Resources:{nl}{ nl.join([str(i) for i in self.files_rel])}
"""

    @property
    def model_description(self):
        md = self.unpacked_path / "modelDescription.xml"
        return ModelDescription(md)

    @property
    def binaries(self):
        """ 
        Returns a list of available binaries in the fmu folder /binaries
        """
        return [f for f in self.get_files(self.fmu_binaries_path).keys()]

    @property
    def documentation(self):
        """ 
        Returns a list of available documentation in the fmu folder /documentation
        """
        return [f for f in self.get_files(self.fmu_documentation_path).keys()]
