# pyssp_standard
[<img src="https://img.shields.io/badge/Status-In Development-orange.svg?logo=LOGO">](<LINK>)

Python package to interact with files specified by the SSP standard [<img src="https://img.shields.io/badge/SSP-Standard-blue.svg?logo=LOGO">](<https://ssp-standard.org/>)
. The library allows for 
the creation, reading and editing of SSV, SSM and SSB files. In addition, it allows for the reading of SSP, FMU and SSD
files. The intended use is for pre-processing work and inspection of a given file.

In addition to the SSP standard the SRMD standard is also supported.

[Index](https://fghaider.github.io/pyssp_standard/docs/index)

## Documentation
Here follows a number of examples of how to use the library.

### SSD

#### Example
Example code for creating an SSP wrapper around an FMU.
```python
connectors = []
with FMU(fmu_path) as fmu:
    connectors.extend(
        (scalar.name, "output", scalar.type_) for scalar in fmu.model_description.outputs
    )
    connectors.extend(
        (scalar.name, "input", scalar.type_) for scalar in fmu.model_description.inputs
    )
    units = fmu.model_description.units

with SSP(ssp_path, mode="w") as ssp:
    with ssp.system_structure as ssd:
        component = Component(None)
        component.component_type = "application/x-fmu-sharedlibrary"
        component.name = name
        component.source = str(Path("resources") / Path(fmu_path).name)
        component.implementation = "CoSimulation"

        ssd.system = System(None, "system")
        for con_name, con_kind, con_type in connectors:
            ssd.system.connectors.append(Connector(None, con_name, con_kind, con_type))
            component.connectors.append(Connector(None, con_name, con_kind, con_type))

            ssd.system.connections.append(
                Connection(
                    start_element=None,
                    start_connector=con_name,
                    end_element=name,
                    end_connector=con_name,
                )
            )

        ssd.system.elements.append(component)
        ssd.name = "root"
        ssd.version = "1.0"
        ssd.units = units

    ssp.add_resource(fmu_path)
```

### SSV 

#### Example
Here a ssv file is opened and checked if it is compliant with the SSP standard.

```python
with SSV(file_path) as file:
    file.check_compliance()
```


### SSM

#### Example
Here a ssm file is opened and checked if it is compliant with the SSP standard.

```python
with SSM(file_path) as file:
    file.check_compliance()
```


### FMU

In your SSP there are often FMU:s (functional mockup units) that hold the binaries for the models. pyssp unpacks these 
when loading an SSP or alternatively loading them directly, allowing the user to peak into its contents, specifically 
to see all declared ScalarVariables and lookup them on the basis of causality or variability.

#### Example

```python
with FMU(file_path) as file:
    parameters = file.get(causality='Parameter')
    print(Parameters)
```
with the print out formatted as:
```
___________________________________________________________________________________________
               Name: pipeC.tao_Tfrict
        Description: Time constant in LP-filtering of Text
        Variability: tunable
          Causality: parameter
 ```

### SRMD
Below follows an example where an SRMD file is created, coupled to some data and then added to an SSP file.
```python
test_file = Path('./test.srmd')
data_file = Path('./doc/embrace/test.csv')
def test_create_srmd(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification(classification_type='test')
        classification.add_classification_entry(ClassificationEntry('test', 'This is a test'))
        file.add_classification(classification)
        file.assign_data(data_file)
        
with SSP(test_file) as file:
    file.add_resource(test_file)
    file.add_resource(data_file)
```

In some cases it may be useful to perform additional parsing on Classifications. For example, to expose
a known set of keywords as attributes, or to perform additional parsing on entry values (such as parsing
dates). If an entry has an XML structure describing a more advanced value, this could also be parsed.
To enable these use cases there is a decorator associate a parser with a given Classification type. If
a classification of that type is encountered in an SRMD file, it will automatically be parsed with the
custom parser.

**Simple Example:**
A simple example of a custom classification is shown below.
```xml
<stc:Classification type="com.example.custom">
    <stc:ClassicationEntry keyword="test1">Value 1</stc:ClassificationEntry>
    <stc:ClassicationEntry keyword="test2">Value 2</stc:ClassificationEntry>
</stc:Classification>
```
To create a custom parser for the simple schema, we subclass Classification in the following way:
```python
@classification_parser("com.example.custom")
class CustomClassification(Classification):
    test1: str
    test2: str

    def __init__(self, element=None, test1="", test2="", **kwargs):
        if element is not None:
            super().__init__(element)

            for entry in self.classification_entries:
                if entry.keyword == "test1":
                    self.test1 = entry.text
                elif entry.keyword == "test2":
                    self.test2 = entry.text
        else:
            super().__init__("com.example.custom", **kwargs)
            self.test1 = test1
            self.test2 = test2

    def as_element(self):
        self.classification_entries = [
                ClassificationEntry("test1", text=self.test1),
                ClassificationEntry("test2", text=self.test2)
        ]

        return super().as_element()
```

**Advanced Example:**
The same functionality can also be used to parse classification schemas with XML structures as values.

```xml
<stc:Classification type="com.example.custom2">
    <stc:ClassificationEntry keyword="example">
        <Family>
            <Parent name="Alice" occupation="engineer"/>
            <Parent name="Bob" occupation="programmer"/>
            <Child name="Eve" age="15"/>
        </Family>
    </stc:ClassificationEntry>
</stc:Classification>
```

The following is sample code to parse the above schema.
```python
@dataclass
class Parent:
    name: str
    occupation: str

    def to_xml(self):
        element = et.Element("Parent")
        element.set("name", self.name)
        element.set("occupation", self.occupation)

        return element

    @classmethod
    def from_xml(cls, element):
        return cls(element.get("name"), element.get("occupation"))


@dataclass
class Child:
    name: str
    age: int

    def to_xml(self):
        element = et.Element("Child")
        element.set("name", self.name)
        element.set("age", str(self.age))

        return element

    @classmethod
    def from_xml(cls, element):
        return cls(element.get("name"), int(element.get("age")))


@dataclass
class Family:
    parents: list[Parent]
    children: list[Child]

    def to_xml(self):
        element = et.Element("Family")
        element.extend([parent.to_xml() for parent in self.parents])
        element.extend([child.to_xml() for child in self.children])

        return element

    @classmethod
    def from_xml(cls, element):
        parents = [Parent.from_xml(el) for el in element.findall("Parent")]
        children = [Child.from_xml(el) for el in element.findall("Child")]

        return Family(parents, children)


@classification_parser("com.example.custom2")
class CustomClassification2(Classification):
    example: Family

    def __init__(self, element=None, example="", **kwargs):
        if element is not None:
            super().__init__(element)

            for entry in self.classification_entries:
                if entry.keyword == "example":
                    self.example = Family.from_xml(entry.content[0])
        else:
            super().__init__("com.example.custom2", **kwargs)
            self.example = example

    def as_element(self):
        self.classification_entries = [
                ClassificationEntry("example", content=[self.example.to_xml()])
        ]

        return super().as_element()
```
