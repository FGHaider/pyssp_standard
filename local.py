from ssp import SSP
from ssv import SSV


def main():
    test_ssv = r"embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    test_ssp = r"embrace.ssp"
    with SSP(test_ssp) as ssp:
        pass


if __name__ == "__main__":
    main()
