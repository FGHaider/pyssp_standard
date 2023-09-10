from pyssp_standard.common_content_ssc import Enumerations, Annotations, Annotation
from pyssp_standard.unit import Units
from pyssp_standard.utils import SSPFile
from pyssp_standard.standard import SSPStandard
from lxml import etree as ET
from lxml.etree import QName


class Connection(SSPStandard):

    def __init__(self, element=None, *, start_element=None, start_connector=None, end_element=None, end_connector=None):
        self.__root = None

        self.base_element = None
        self.start_element = start_element  # Optional
        self.start_connector = start_connector
        self.end_element = end_element  # Optional
        self.end_connector = end_connector
        self.suppress_unit_conversion: bool = False

        self.transformation = None
        self.annotations = None
        # Connection geometry not connected

        if element is not None:
            self.__read__(element)

    def __read__(self, element):
        self.start_element = element.get('startElement')
        self.start_connector = element.get('startConnector')
        self.end_element = element.get('endElement')
        self.end_connector = element.get('endConnector')

    def __eq__(self, other):
        if self.start_element == other.start_element and self.start_connector == other.start_connector and \
                self.end_element == other.end_element and self.end_connector == other.end_connector:
            return True
        else:
            return False

    def as_element(self) -> ET.Element:
        self.__root = ET.Element(QName(self.namespaces['ssd'], 'Connection'),
                                 attrib={'startElement': self.start_element,
                                         'startConnector': self.start_connector,
                                         'endElement': self.end_element,
                                         'endConnector': self.end_connector})
        return self.__root

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


class SSD(SSPFile):

    def __init__(self, file_path, mode='r'):

        self.name = None
        self.version = None

        self.system = None
        self.default_experiment = None
        self.__enumerations: Enumerations = Enumerations()
        self.__units: Units = Units()

        self.connections_to_add = []
        self.connections_to_remove = []

        if mode not in ['r', 'a']:
            raise Exception('Only read mode and append mode are supported for SSD files')

        super().__init__(file_path=file_path, mode=mode, identifier='ssd')

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

    def add_connection(self, connection: Connection):
        if type(connection) is not Connection:
            raise "Only Connection object may be used."
        self.system.connections.append(connection)
        self.connections_to_add.append(connection)

    def remove_connection(self, connection: Connection):
        for idx, item in enumerate(self.connections()):
            if item == connection:
                self.system.connections.pop(idx)
                self.connections_to_remove.append(connection)
                break

    def connections(self):
        return self.system.connections

    def list_connections(self, *, source=None, target=None, source_parent=None, target_parent=None):
        connections = self.connections()
        matching_connections = []
        for connection in connections:

            if source is not None and source != connection.start_connector:
                continue
            if source is not None and target != connection.end_connector:
                continue
            if source is not None and source_parent != connection.start_element:
                continue
            if source is not None and target_parent != connection.end_element:
                continue
            matching_connections.append(connection)

        return matching_connections

    def list_connectors(self, *, kind=None, name=None, parent=None):
        """Returns a list of connectors, filtered by the following optional options
            :param kind: the kind of connector, e.g. input, output or parameter
            :param name: the name of the connector, utilizes 'in' for lookup
            :param parent: the name of the parent component, utilizes 'in' for lookup
        """

        matching_connectors = {}
        component_connectors = self.system.element.as_dict()

        for component in component_connectors:
            if parent is not None and parent not in component['name']:
                continue

            for connector in component['connectors']:
                if kind is not None and kind != connector['kind']:
                    continue
                if name is not None and name not in connector['name']:
                    continue

                if component['name'] not in matching_connectors.keys():
                    matching_connectors[component['name']] = []
                matching_connectors[component['name']].append({'name': connector['name'], 'kind': connector['kind']})

        return matching_connectors

    def __write__(self):
        self.__tree = ET.parse(self.file_path)
        self.root = self.__tree.getroot()
        system = self.root.findall('ssd:System', self.namespaces)
        if system is not None:
            connections_set = system[0].findall('ssd:Connections', self.namespaces)[0]
            for target in self.connections_to_remove:
                matching_elements = connections_set.findall('ssd:Connection', namespaces=self.namespaces)
                for element in matching_elements:
                    if Connection(element) == target:
                        element.getparent().remove(element)
            for add_connection in self.connections_to_add:
                connections_set.append(add_connection.as_element())