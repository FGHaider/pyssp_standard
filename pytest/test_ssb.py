from ssb import SSB


def test_create_ssb():
    with SSB('./test.ssb', 'r') as file:
        #file.add_dictionary_entry('test_a', 'Real', {'value': 10, 'unit': 'm'})
        file.__check_compliance__()
