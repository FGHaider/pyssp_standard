from lxml import etree as et
from lxml.etree import QName

from pyssp_standard.unit import Units
from pyssp_standard.standard import ModelicaStandard


def test_units_ssp_read():
    xml = """<ssd:Units xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon" xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription">
        <ssc:Unit name="V">
            <ssc:BaseUnit kg="1" m="2" s="-3" A="-1" />
        </ssc:Unit>
    </ssd:Units>
    """
    elem = et.fromstring(xml)

    units = Units(elem)
    assert len(units) == 1

    volts = units[0]
    assert volts.name == "V"

    base_volts = volts.base_unit
    assert base_volts.kg == 1
    assert base_volts.m == 2
    assert base_volts.s == -3
    assert base_volts.A == -1


def test_units_fmi_read():
    xml = """<UnitDefinitions>
        <Unit name="V">
            <BaseUnit kg="1" m="2" s="-3" A="-1" />
        </Unit>
    </UnitDefinitions>
    """
    elem = et.fromstring(xml)

    units = Units(elem)
    assert len(units) == 1

    volts = units[0]
    assert volts.name == "V"

    base_volts = volts.base_unit
    assert base_volts.kg == 1
    assert base_volts.m == 2
    assert base_volts.s == -3
    assert base_volts.A == -1


def test_units_fmi_to_ssp():
    xml = """<UnitDefinitions>
        <Unit name="V">
            <BaseUnit kg="1" m="2" s="-3" A="-1" />
        </Unit>
    </UnitDefinitions>
    """
    elem = et.fromstring(xml)
    units = Units(elem)
    ssd_elem = units.element(parent_type="ssd")

    assert ssd_elem.tag == QName(ModelicaStandard.namespaces["ssd"], "Units")
    assert len(ssd_elem) == 1

    unit_elem = ssd_elem[0]
    assert unit_elem.tag == QName(ModelicaStandard.namespaces["ssc"], "Unit")

    assert len(unit_elem) == 1
    base_elem = unit_elem[0]
    assert base_elem.tag == QName(ModelicaStandard.namespaces["ssc"], "BaseUnit")
