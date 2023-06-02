from ssp import SSP
from ssv import SSV
from ssm import SSM


def main():
    test_ssv = r"embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    test_ssp = r"embrace.ssp"
    test_ssm = r"embrace/resources/ECS_HW.ssm"
    with SSM(test_ssm) as ssm:
        pass


if __name__ == "__main__":
    main()
