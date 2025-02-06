from pathlib import Path


class ModelicaStandard:
    namespaces = {
        # SSP
        "ssc": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        "ssv": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        "ssb": "http://ssp-standard.org/SSP1/SystemStructureSignalDictionary",
        "ssm": "http://ssp-standard.org/SSP1/SystemStructureParameterMapping",
        "ssd": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        # SRMD
        "stc": "http://ssp-standard.org/SSPTraceability1/SSPTraceabilityCommon",
        "srmd": "http://ssp-standard.org/SSPTraceability1/SimulationResourceMetaData",
        # FMI
        "fmi30": "",
        # XLink
        "xlink": "http://www.w3.org/1999/xlink"
    }

    __resource_path = Path(__file__).parent / "resources"
    schemas = {
        # SSP
        "ssc": __resource_path / "SystemStructureCommon.xsd",
        "ssd": __resource_path / "SystemStructureDescription.xsd",
        "ssd11": __resource_path / "SystemStructureDescription11.xsd",
        "ssm": __resource_path / "SystemStructureParameterMapping.xsd",
        "ssv": __resource_path / "SystemStructureParameterValues.xsd",
        "ssb": __resource_path / "SystemStructureSignalDictionary.xsd",
        # SSPTraceabillity
        "stc11": __resource_path / "STC11.xsd",
        "srmd11": __resource_path / "SRMD11.xsd",
        # FMI
        "fmi30": __resource_path / "fmi30" / "fmi3ModelDescription.xsd",
    }
