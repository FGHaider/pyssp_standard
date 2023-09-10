import shutil
import tempfile
import zipfile
from pathlib import Path, PosixPath
from dataclasses import dataclass
from lxml import etree as et


@dataclass
class ScalarVariable:
    name: str
    description: str
    causality: str
    variability: str


class VariableList(list):

    def __repr__(self):
        print_out = """"""
        for item in self:
            print_out += f"""
        ___________________________________________________________________________________________
               Name: {item.name}
        Description: {item.description}
        Variability: {item.variability}
          Causality: {item.causality}
            """
        return print_out


class FMU:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir)

    def __repr__(self):
        return f"""
        Functional Mockup Unit:
             Model Name: {self.model_name}
            FMI Version: {self.fmi_version}
               Filepath: {self.file_path}
        """

    def __init__(self, file_path):
        """This class allows for peeking into a FMU file, it by no means covers the entirety of the FMI standard and should
             primarily be considered as a debugging tool for looking of model input, outputs and parameters.
            :param file_path: filepath to the target FMU.
            :type file_path: str or PosixPath
        """
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)

        self.temp_dir = tempfile.mkdtemp()
        self.file_path = file_path
        self.model_description_file = None
        self.guid = None

        self.__variables: VariableList[ScalarVariable] = VariableList()
        self.model_name = None
        self.fmi_version = None
        self.__read__()

    def __read__(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        self.model_description_file = list(Path(self.temp_dir).glob('modelDescription.xml'))[0]
        tree = et.parse(self.model_description_file)
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
            scalar_variable = ScalarVariable(name=name, description=description,
                                             variability=variability, causality=causality)
            self.__variables.append(scalar_variable)

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
