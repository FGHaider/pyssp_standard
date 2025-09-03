from collections import defaultdict

from pyssp_standard.common_content_ssc import Enumerations, Annotations, Annotation, TypeChoice, TypeReal
from pyssp_standard.unit import Units
from pyssp_standard.utils import ModelicaXMLFile
from pyssp_standard.standard import ModelicaStandard
from lxml import etree as ET
from lxml.etree import QName


class Connection(ModelicaStandard):

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
        attrib = {
                'startElement': self.start_element,
                'startConnector': self.start_connector,
                'endElement': self.end_element,
                'endConnector': self.end_connector
        }
        attrib = {k: v for k, v in attrib.items() if v is not None}

        self.__root = ET.Element(QName(self.namespaces['ssd'], 'Connection'), **attrib)
        return self.__root

    def as_dict(self):
        return {'source': self.start_element, 'signal': self.start_connector,
                'target': self.end_element, 'receiver': self.end_connector}

    def __repr__(self) -> str:
        return f"""source {self.start_element} - {self.start_connector} -> target {self.end_element} - {self.end_connector}"""


class Connector(ModelicaStandard):

    def __init__(self, element=None, name="", kind="", type_=TypeReal(None)):
        self.name = name
        self.kind = kind
        self.type_ = type_

        if element is not None:
            self.__read__(element)

    def __read__(self, element: ET.Element):
        self.name = element.get('name')
        self.kind = element.get('kind')
        type_elem = TypeChoice.XPATH_SSP(element)
        self.type_ = TypeChoice.from_xml(type_elem[0]) if type_elem else None

    def as_element(self):
        elem = ET.Element(
                QName(self.namespaces["ssd"], "Connector"),
                name=self.name,
                kind=self.kind
        )
        elem.append(self.type_.to_xml(namespace="ssc"))

        return elem

    def as_dict(self):
        return {'name': self.name, 'kind': self.kind}


class Component(ModelicaStandard):
    def __init__(self, element=None):
        self.component_type = None
        self.name = None
        self.source = None
        self.implementation = None
        self.connectors = []
        self.parameter_bindings = None
        self.annotations = None

        if element is not None:
            self.__read__(element)

    def __read__(self, element):
        self.name = element.get('name')
        self.component_type = element.get('type')
        self.source = element.get('source')
        self.implementation = element.get('implementation')

        connectors = element.find('ssd:Connectors', namespaces=self.namespaces)
        if connectors is not None:
            for connector in connectors.findall('ssd:Connector', namespaces=self.namespaces):
                self.connectors.append(Connector(connector))

    def as_element(self):
        element = ET.Element(QName(self.namespaces["ssd"], "Component"), name=self.name)

        if self.component_type is not None:
            element.set("type", self.component_type)

        if self.source is not None:
            element.set("source", self.source)

        if self.implementation is not None:
            element.set("implementation", self.implementation)

        if self.connectors:
            connectors = ET.Element(QName(self.namespaces["ssd"], "Connectors"))
            for connector in self.connectors:
                connectors.append(connector.as_element())

            element.append(connectors)

        return element

    def as_dict(self):
        return {'name': self.name, 'connectors': [connector.as_dict() for connector in self.connectors]}


class Element(ModelicaStandard):

    def __init__(self, element):
        self.components = []
        self.__read__(element)

    def __read__(self, element):
        components = element.findall('ssd:Component', namespaces=self.namespaces)
        for component in components:
            self.components.append(Component(component))

    def as_dict(self):
        return [component.as_dict() for component in self.components]


class System(ModelicaStandard):
    name: str
    elements: "list[Component | System]"  # ugly, because of forward declarations. Fixed in py3.14+
    connections: list[Connection]

    connectors: list[Connector]
    parameter_bindings: list
    signal_dictionaries: list
    annotations: Annotations | None

    def __init__(
            self,
            system_element: ET.Element = None,
            name: str = "",
        ):
        self.name = name
        self.elements = []
        self.connections: list[Connection] = []

        self.connectors: list[Connector] = []
        self.parameter_bindings = []
        self.signal_dictionaries = []
        self.annotations = Annotations(namespace="ssd")

        if system_element is not None:
            self.__read__(system_element)

    def parse_element(self, elem):
        if elem.tag == QName(self.namespaces["ssd"], "Component"):
            return Component(elem)
        elif elem.tag == QName(self.namespaces["ssd"], "System"):
            return System(elem)
        else:
            # Unfortunately, no support for SignalDictionaries yet :(
            return elem

    def __read__(self, element):
        self.name = element.get('name', None)

        connectors = element.find('ssd:Connectors', namespaces=self.namespaces)
        if connectors is not None:
            for connector in connectors.findall('ssd:Connector', namespaces=self.namespaces):
                self.connectors.append(Connector(connector))

        elements = element.find('ssd:Elements', namespaces=self.namespaces)
        if elements is not None:
            self.elements = [self.parse_element(child) for child in elements]

        connections = element.find('ssd:Connections', namespaces=self.namespaces)
        if connections is not None:
            for connection in connections.findall('ssd:Connection', namespaces=self.namespaces):
                self.connections.append(Connection(connection))

        annotations = element.find("ssd:Annotations", namespaces=self.namespaces)
        if annotations is not None:
            for elem in annotations:
                self.annotations.add_annotation(Annotation(elem))

    def as_element(self):
        element = ET.Element(QName(self.namespaces["ssd"], "System"), name=self.name)

        if self.connectors:
            connectors = ET.Element(QName(self.namespaces["ssd"], "Connectors"))
            connectors.extend(connector.as_element() for connector in self.connectors)
            element.append(connectors)

        if self.elements:
            elements = ET.Element(QName(self.namespaces["ssd"], "Elements"))
            elements.extend(el.as_element()
                  if isinstance(el, (Component, System))
                  else el for el in self.elements)
            element.append(elements)

        if self.connections:
            connections = ET.Element(QName(self.namespaces["ssd"], "Connections"))
            connections.extend(connection.as_element() for connection in self.connections)
            element.append(connections)

        if not self.annotations.is_empty():
            element.append(self.annotations.element())

        return element


class DefaultExperiment(ModelicaStandard):

    def __init__(self, element: ET.Element = None):
        self.start_tim: float = None
        self.stop_time: float = None
        self.annotations: Annotations = Annotations(namespace="ssd")

        if element is not None:
            self.__read__(element)

    def __read__(self, element):
        self.start_time = float(element.get('startTime'))
        self.stop_time = float(element.get('stopTime'))

        annotations = element.find('ssd:Annotations', self.namespaces)

        if annotations is not None:
            for annotation in annotations.findall('ssc:Annotation', self.namespaces):
                self.annotations.add_annotation(Annotation(annotation))

    def as_element(self):
        elem = ET.Element(
                QName(self.namespaces["ssd"], "DefaultExperiment"),
                startTime=str(self.start_time),
                stopTime=str(self.stop_time)
        )

        if not self.annotations.is_empty():
            elem.append(self.annotations.element())

        return elem


class SSD(ModelicaXMLFile):

    def __init__(self, file_path, mode='r'):

        self.name = None
        self.version = None

        self.system = None
        self.default_experiment = None
        self.__enumerations: Enumerations = Enumerations(namespace="ssd")
        self.units: Units = Units()

        super().__init__(file_path=file_path, mode=mode, identifier='ssd')

    def __read__(self):
        tree = ET.parse(str(self.file_path))
        self.root = tree.getroot()

        self.top_level_metadata.update(self.root.attrib)
        self.base_element.update(self.root.attrib)

        system = self.root.find('ssd:System', self.namespaces)
        if system is not None:
            self.system = System(system)

        default_experiment = self.root.findall('ssd:DefaultExperiment', self.namespaces)
        if len(default_experiment) > 0:
            self.default_experiment = DefaultExperiment(default_experiment[0])

        enumerations = self.root.find("ssd:Enumerations", self.namespaces)
        if enumerations is not None:
            self.__enumerations = Enumerations(enumerations, namespace="ssd")

        units = self.root.find("ssd:Units", self.namespaces)
        if units is not None:
            self.units = Units(units)

        self.name = self.root.get('name')
        self.version = self.root.get('version')

    def __write__(self):
        namespaces = ["ssd", "ssc"]
        nsmap = {k: self.namespaces[k] for k in namespaces}
        self.root = ET.Element(
                QName(self.namespaces["ssd"], "SystemStructureDescription"),
                version=self.version,
                name=self.name,
                nsmap=nsmap
        )

        self.root = self.top_level_metadata.update_root(self.root)
        self.root = self.base_element.update_root(self.root)

        if self.system is not None:
            self.root.append(self.system.as_element())

        if self.default_experiment is not None:
            self.root.append(self.default_experiment.as_element())

        if self.__enumerations is not None and self.__enumerations.enumerations:
            self.root.append(self.__enumerations.as_element())

        if self.units is not None and len(self.units) != 0:
            self.root.append(self.units.element(parent_type="ssd"))

    def add_connection(self, connection: Connection):
        if type(connection) is not Connection:
            raise "Only Connection object may be used."
        self.system.connections.append(connection)

    def remove_connection(self, connection: Connection):
        try:
            self.system.connections.remove(connection)
        except ValueError:
            pass  # Replicate previous behavior

    def connections(self):
        return self.system.connections

    def list_connections(self, *, start_connector=None, end_connector=None, start_element=None, end_element=None):
        connections = self.connections()
        matching_connections = []

        def check(value, comparision):
            return True if value is None else value == comparision

        for connection in connections:
            connection : Connection
            sc = [start_connector, connection.start_connector]
            ec = [end_connector, connection.end_connector]
            se = [start_element, connection.start_element]
            ee = [end_element, connection.end_element]

            if check(*sc) and check(*ec) and check(*se) and check(*ee):
                matching_connections.append(connection)

        return matching_connections

    def list_connectors(self, *, kind=None, name=None, parent=None):
        """Returns a list of connectors, filtered by the following optional options
            :param kind: the kind of connector, e.g. input, output or parameter
            :param name: the name of the connector, utilizes 'in' for lookup
            :param parent: the name of the parent component, utilizes 'in' for lookup
        """

        matching_connectors = defaultdict(list)

        for element in self.system.elements:
            if not isinstance(element, (System, Component)):
                continue

            if parent is not None and parent not in element.name:
                continue

            for connector in element.connectors:
                if kind is not None and kind != connector.kind:
                    continue
                if name is not None and name not in connector.name:
                    continue

                matching_connectors[element.name].append(
                        {"name": connector.name, "kind": connector.kind})

        return matching_connectors
