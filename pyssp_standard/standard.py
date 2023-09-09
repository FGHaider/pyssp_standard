from pathlib import Path


class SSPStandard:
    namespaces = {'ssc': 'http://ssp-standard.org/SSP1/SystemStructureCommon',
                  'ssv': 'http://ssp-standard.org/SSP1/SystemStructureParameterValues',
                  'ssb': 'http://ssp-standard.org/SSP1/SystemStructureSignalDictionary',
                  'ssm': 'http://ssp-standard.org/SSP1/SystemStructureParameterMapping',
                  'ssd': 'http://ssp-standard.org/SSP1/SystemStructureDescription'}

    __resource_path = Path(__file__).parent / 'resources'
    schemas = {'ssc': __resource_path / 'SystemStructureCommon.xsd',
               'ssd': __resource_path / 'SystemStructureDescription.xsd',
               'ssd11': __resource_path / 'SystemStructureDescription11.xsd',
               'ssm': __resource_path / 'SystemStructureParameterMapping.xsd',
               'ssv': __resource_path / 'SystemStructureParameterValues.xsd',
               'ssb': __resource_path / 'SystemStructureSignalDictionary.xsd'}


class SRMDStandard:
    namespaces = {'stc': 'http://apps.pmsf.net/SSPTraceability/SSPTraceabilityCommon',
                  'ssc': 'http://ssp-standard.org/SSP1/SystemStructureCommon',
                  'srmd': 'http://apps.pmsf.net/STMD/SimulationResourceMetaData'}
    schema = Path(__file__).parent / 'resources' / 'SRMD.xsd'
