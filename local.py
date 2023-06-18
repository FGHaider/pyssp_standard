from ssp import SSP
from ssv import SSV
from ssm import SSM
from fmu import FMU


def main():
    test_ssv = "embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    test_ssp = "embrace.ssp"
    test_ssm = "embrace/resources/ECS_HW.ssm"
    test_write_ssm = "./test.ssm"
    test_fmu = "embrace/resources/0001_ECS_HW.fmu"
    with SSM(test_write_ssm, 'w') as file:
        file.add_mapping('ica', 'coop')
        file.TopLevelMetaData.author = 'FH'
        file.BaseElement.id = '1'


if __name__ == "__main__":
    main()
