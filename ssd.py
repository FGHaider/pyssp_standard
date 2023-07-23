from common_content_ssc import Enumerations, Annotations, Annotation
from unit import Units
from utils import SSPStandard, SSPFile
from lxml import etree as ET
import xmlschema


class Connection(SSPStandard):

    def __init__(self, element):
        self.base_element = None
        self.start_element = None  # Optional
        self.start_connector = None
        self.end_element = None  # Optional
        self.end_connector = None
        self.suppress_unit_conversion: bool = False

        self.transformation = None
        self.annotations = None
        # Connection geometry not connected

        self.__read__(element)

    def __read__(self, element):
        self.start_element = element.get('startElement')
        self.start_connector = element.get('startConnector')
        self.end_element = element.get('endElement')
        self.end_connector = element.get('endConnector')


class Connector(SSPStandard):

    def __init__(self, element):
        self.name = ""
        self.kind = ""
        self.value_type = ""

        self.__read__(element)

    def __read__(self, element: ET.Element):
        self.name = element.get('name')
        self.kind = element.get('kind')


class Component(SSPStandard):

    def __init__(self, element):
        self.component_type = None
        self.source = None
        self.implementation = None
        self.connectors = []
        self.parameter_bindings = None

        self.annotations = None

        self.__read__(element)

    def __read__(self, element):
        connectors = element.findall('ssd:Connectors', namespaces=self.namespaces)
        for connector in connectors[0].findall('ssd:Connector', namespaces=self.namespaces):
            self.connectors.append(Connector(connector))


class Element(SSPStandard):

    def __init__(self, element):
        self.components = []

        self.__read__(element)

    def __read__(self, element):
        components = element.findall('ssd:Component', namespaces=self.namespaces)
        for component in components:
            self.components.append(Component(component))


class System(SSPStandard):

    def __init__(self, system_element: ET.Element):

        self.name = None
        self.elements = []
        self.connections = []

        self.connectors = []
        self.parameter_bindings = []
        self.signal_dictionaries = []
        self.annotations = []

        self.__read__(system_element)

    def __read__(self, element):
        elements = element.findall('ssd:Elements', namespaces=self.namespaces)
        self.elements = Element(elements[0])
        connections = element.findall('ssd:Connections', namespaces=self.namespaces)
        for connection in connections[0].findall('ssd:Connection', namespaces=self.namespaces):
            self.connections.append(Connection(connection))


class DefaultExperiment(SSPStandard):

    def __init__(self, element: ET.Element = None):
        self.start_time = None
        self.end_time = None
        self.annotations: Annotations = Annotations()

        if element is not None:
            self.__read__(element)

    def __read__(self, element):
        self.start_time = element.get('startTime')
        self.end_time = element.get('endTime')

        annotations = element.findall('ssd:Annotations', self.namespaces)
        if len(annotations) > 0:
            for annotation in annotations[0].findall('ssc:Annotation', self.namespaces):
                self.annotations.add_annotation(Annotation(annotation))


class SSD(SSPStandard, SSPFile):

    def __init__(self, file_path, mode='r'):

        self.name = None
        self.version = None
        self.base_element = None
        self.top_level_meta_data = None

        self.system = None
        self.default_experiment = None
        self.__enumerations: Enumerations = Enumerations()
        self.__annotations: Annotations = Annotations()
        self.__units: Units = Units()

        if mode not in ['r', 'a']:
            raise Exception('Only read mode and append mode are supported for SSD files')

        super().__init__(file_path=file_path, mode=mode)

    def __read__(self):
        self.__tree = ET.parse(self.file_path)
        self.root = self.__tree.getroot()

        system = self.root.findall('ssd:System', self.namespaces)[0]
        self.system = System(system)

        default_experiment = self.root.findall('ssd:DefaultExperiment', self.namespaces)
        if len(default_experiment) > 0:
            self.default_experiment = DefaultExperiment(default_experiment[0])

        self.name = self.root.get('name')
        self.version = self.root.get('version')

    def __check_compliance__(self):
        xmlschema.validate(self.file_path, self.schemas['ssd'], namespaces=self.namespaces)

    def __write__(self):
        pass
