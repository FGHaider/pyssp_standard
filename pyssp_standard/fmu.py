import shutil
import tempfile
import zipfile
from pathlib import Path, PosixPath
from dataclasses import dataclass
from lxml import etree as et

from pyssp_standard.standard import ModelicaStandard
from pyssp_standard.utils import ModelicaXMLFile, ZIPFile
from pyssp_standard.unit import Units
from pyssp_standard.common_content_ssc import TypeChoice


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


class ModelDescription(ModelicaXMLFile):
    """
    
    """

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

        self.guid = None

        self.__variables: VariableList[ScalarVariable] = VariableList()
        self.model_name = None
        self.fmi_version = None
        self.units = None

        super().__init__(file_path, mode, "fmi30")

    def __read__(self):
        tree = et.parse(str(self.file_path))
        root = tree.getroot()

        self.guid = root.get('guid')
        self.model_name = root.get('modelName')
        self.fmi_version = root.get('fmiVersion')

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
