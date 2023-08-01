from py_ssp.ssb import SSB


def test_create_ssb():
    with SSB('./test.ssb', 'w') as file:
        file.add_dictionary_entry('test_a', ptype='Integer', value={"value": "10"})
        file.__check_compliance__()
