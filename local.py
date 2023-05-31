from ssp import SSV

def main():
    test_ssv = r"embrace/resources/RAPID_Systems_2021-03-29_Test_1.ssv"
    with SSV(test_ssv) as ssv:
        pass


if __name__ == "__main__":
    main()
