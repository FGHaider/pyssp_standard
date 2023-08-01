from pathlib import Path

from pyssp_standard.common_content_ssc import Enumerations, Annotations, Annotation
from pyssp_standard.unit import Units
from pyssp_standard.utils import SSPStandard, SSPFile
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

    def as_dict(self):
        return {'source': self.start_element, 'signal': self.start_connector,
                'target': self.end_element, 'receiver': self.end_connector}


class Connector(SSPStandard):

    def __init__(self, element):
        self.name = ""
        self.kind = ""
        self.value_type = ""

        self.__read__(element)

    def __read__(self, element: ET.Element):
        self.name = element.get('name')
        self.kind = element.get('kind')

    def as_dict(self):
        return {'name': self.name, 'kind': self.kind}


class Component(SSPStandard):

    def __init__(self, element):
        self.component_type = None
        self.name = None
        self.source = None
        self.implementation = None
        self.connectors = []
        self.parameter_bindings = None
        self.annotations = None

        self.__read__(element)

    def __read__(self, element):
        self.name = element.get('name')
        connectors = element.findall('ssd:Connectors', namespaces=self.namespaces)
        for connector in connectors[0].findall('ssd:Connector', namespaces=self.namespaces):
            self.connectors.append(Connector(connector))

    def as_dict(self):
        return {'name': self.name, 'connectors': [connector.as_dict() for connector in self.connectors]}


class Element(SSPStandard):

    def __init__(self, element):
        self.components = []
        self.__read__(element)

    def __read__(self, element):
        components = element.findall('ssd:Component', namespaces=self.namespaces)
        for component in components:
            self.components.append(Component(component))

    def as_dict(self):
        return [component.as_dict() for component in self.components]


class System(SSPStandard):

    def __init__(self, system_element: ET.Element):

        self.name = None
        self.element = None
        self.__connections = []

        self.connectors = []
        self.parameter_bindings = []
        self.signal_dictionaries = []
        self.annotations = []

        self.__read__(system_element)

    def __read__(self, element):
        elements = element.findall('ssd:Elements', namespaces=self.namespaces)
        self.element = Element(elements[0])
        connections = element.findall('ssd:Connections', namespaces=self.namespaces)
        for connection in connections[0].findall('ssd:Connection', namespaces=self.namespaces):
            self.__connections.append(Connection(connection))

    @property
    def connections(self):
        return self.__connections


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

    def add_connection(self, connection):
        pass

    def remove_connection(self, name):
        pass

    def connections(self):
        return self.system.connections

    def list_connectors(self, *, kind=None, name=None, parent=None, state=None):
        """
        Returns a list of connectors, filtered by the following optional options
        :param kind: the kind of connector, e.g. input, output or parameter
        :param name: the name of the connector, utilizes 'in' for lookup
        :param parent: the name of the parent component, utilizes 'in' for lookup
        :param state: accepted states are 'closed', 'open' or leave as None.
            When using either of the states only connectors that are either used in
            the connections or is used in the listed connections.
        """

        matching_connectors = {}
        component_connectors = self.system.element.as_dict()
        connections = [connection.as_dict() for connection in self.system.connections]

        for component in component_connectors:
            if parent is not None and parent not in component['name']:
                continue

            for connector in component['connectors']:
                if kind is not None and kind != connector['kind']:
                    continue
                if name is not None and name not in connector['name']:
                    continue

                if state == 'open':
                    pass
                elif state == 'closed':
                    pass

                if component['name'] not in matching_connectors.keys():
                    matching_connectors[component['name']] = []
                matching_connectors[component['name']].append({'name': connector['name'], 'kind': connector['kind']})

        return matching_connectors

    def __write__(self):
        pass
