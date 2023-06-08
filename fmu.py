import shutil
import tempfile
import zipfile
from pathlib import Path, PosixPath
import xml.etree.cElementTree as ET
from typing import TypedDict


class ScalarVariable(TypedDict):
    name: str
    description: str
    causality: str
    variability: str
    type_declaration: dict


class VariableList(list):

    def __repr__(self):
        print_out = """"""
        for item in self:
            print_out += f"""
        ___________________________________________________________________________________________
               Name: {item['name']}
        Description: {item['description']}
        Variability: {item['variability']}
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

    def __init__(self, file_path, mode='r'):
        """
        This class allows for peeking into a FMU file, it by no means covers the entirety of the FMI standard and should
         primarily be considered as a debugging tool for looking of model input, outputs and parameters.
        :param file_path: file path to the target FMU
        :param mode: Mode to open file in, currently only read mode is available
        """
        if type(file_path) is not PosixPath:
            file_path = Path(file_path)
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = file_path
        self.model_description_file = None

        self.__parameters: VariableList[ScalarVariable] = VariableList()
        self.__inputs: VariableList[ScalarVariable] = VariableList()
        self.__outputs: VariableList[ScalarVariable] = VariableList()
        self.__other: VariableList[ScalarVariable] = VariableList()

        self.model_name = None
        self.fmi_version = None

        if mode != 'r':
            raise Exception('Only read mode is possible with FMUs.')

        self.__read__()

    def __read__(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        self.model_description_file = list(Path(self.temp_dir).glob('modelDescription.xml'))[0]
        tree = ET.parse(self.model_description_file)
        root = tree.getroot()

        self.model_name = root.get('modelName')
        self.fmi_version = root.get('fmiVersion')

        model_variables = root.findall('ModelVariables')[0]
        scalar_variables = model_variables.findall('ScalarVariable')
        for scalar in scalar_variables:
            name = scalar.get('name')
            description = scalar.get('description')
            causality = scalar.get('causality')
            variability = scalar.get('variability')
            #type_declaration = list(scalar.iter())
            scalar_variable = ScalarVariable(name=name, description=description, variability=variability,
                                             type_declaration={}, causality=causality)
            if causality == 'parameter':
                self.__parameters.append(scalar_variable)
            elif causality == 'input':
                self.__inputs.append(scalar_variable)
            elif causality == 'output':
                self.__outputs.append(scalar_variable)
            else:
                self.__other.append(scalar_variable)

    @property
    def parameters(self):
        return self.__parameters

    @property
    def outputs(self):
        return self.__outputs

    @property
    def inputs(self):
        return self.__inputs

    @property
    def other(self):
        return self.__other
