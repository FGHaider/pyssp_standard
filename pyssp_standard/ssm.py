from pyssp_standard.transformation_types import Transformation
from pyssp_standard.common_content_ssc import Annotations, Annotation
from pyssp_standard.utils import SSPFile
from lxml import etree as et
from lxml.etree import QName
from typing import TypedDict


class MappingEntry(TypedDict):
    source: str
    target: str
    suppress_unit_conversion: bool
    annotations: Annotations
    transformation: Transformation


class MappingList(list):

    def __repr__(self):
        print_out = """"""
        for item in self:
            print_out += f"""
        ___________________________________________________________________________________________
        Source: {item['source']}
        Target: {item['target']}
            """
        return print_out


class SSM(SSPFile):

    def __init__(self, *args):
        self.__version: str
        self.__mappings: MappingList[MappingEntry] = MappingList()

        super().__init__(*args, identifier='ssm')

    def __repr__(self):
        return f"""
        Parameter Mapping:
            Filepath: {self.file_path}
            Mappings: {len(self.mappings)}
        """

    def __read__(self):
        self.__tree = et.parse(self.file_path)
        self.root = self.__tree.getroot()
        self.top_level_metadata.update(self.root.attrib)
        self.base_element.update(self.root.attrib)

        mappings = self.root.findall('ssm:MappingEntry', self.namespaces)
        for entry in mappings:
            transformation = entry.findall('ssc:Transformation', self.namespaces)
            trans = None
            if len(transformation) > 0:
                trans_type = transformation[0].tag.split('}')[-1]
                trans = Transformation(trans_type, transformation[0].attrib)
            annotations = entry.findall('ssc:Annotations', self.namespaces)
            if len(annotations) > 0:
                annotations_list = annotations[0].findall('ssc:Annotation', self.namespaces)
                anno_list = Annotations()
                for anno in annotations_list:
                    anno_item = Annotation(type_declaration=anno.get('type'))
                    anno_item.add_element(anno)
                    anno_list.add_annotation(anno_item)

            self.__mappings.append(MappingEntry(source=entry.attrib.get('source'), target=entry.attrib.get('target'),
                                                suppress_unit_conversion=False, annotations=Annotations(),
                                                transformation=trans if trans is not None else Transformation()))

    def __write__(self):

        self.root = et.Element(QName(self.namespaces['ssm'], 'ParameterMapping'), attrib={'version': '1.0'})
        self.root = self.top_level_metadata.update_root(self.root)
        self.root = self.base_element.update_root(self.root)

        for mapping in self.__mappings:
            mapping_entry = et.SubElement(self.root, QName(self.namespaces['ssm'], 'MappingEntry'),
                                          attrib={'target': mapping.get('target'),
                                                  'source': mapping.get('source')})
            if mapping['transformation'] is not Transformation():
                transformation_element = mapping['transformation'].element()
                if transformation_element is not None:
                    mapping_entry.append(transformation_element)
            if not mapping['annotations'].is_empty():
                annotation_element = mapping['annotations'].root
                if annotation_element is not None:
                    mapping_entry.append(annotation_element)

    @property
    def mappings(self):
        return self.__mappings

    def add_mapping(self, source, target, suppress_unit_conversion=False, transformation=None, annotations=None):
        self.__mappings.append(MappingEntry(source=source, target=target,
                                            suppress_unit_conversion=suppress_unit_conversion,
                                            transformation=Transformation() if transformation is None else transformation,
                                            annotations=Annotations() if annotations is None else annotations))

    def edit_mapping(self, edit_target=True, *, target=None, source=None,
                     transformation: Transformation = None, suppress_unit_conversion=None,
                     annotations: Annotations = None):
        found = False
        idx = 0
        for idx, entry in enumerate(self.__mappings):
            if edit_target and entry.get('target') == target:
                found = True
                break
            elif not edit_target and entry.get('source') == source:
                found = True
                break

        if found:
            mapping_found = self.__mappings[idx]
            if target is not None:
                mapping_found['target'] = target
            if source is not None:
                mapping_found['source'] = source
            if transformation is not None:
                mapping_found['transformation'] = transformation
            if suppress_unit_conversion is not None:
                mapping_found['suppress_unit_conversion'] = suppress_unit_conversion
            if annotations is not None:
                mapping_found['annotations'] = annotations

        else:
            raise Exception("The target or source was not found, there is nothing to edit")
