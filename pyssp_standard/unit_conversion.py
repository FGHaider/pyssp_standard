
import pint


def generate_base_unit(input_string):

    ureg = pint.UnitRegistry()
    parsed_quantity = ureg(input_string)

    conversion_table = {'meter': 'm',
                        'kilogram': 'kg',
                        'second': 's',
                        'ampere': 'A',
                        'kelvin': 'K',
                        'mole': 'mol',
                        'candela': 'Cd',
                        'radian': 'rad'
                        }
    unit_dict = {}
    units_to_parse = (str(parsed_quantity.to_base_units())).split()
    unit_dict['factor'] = float(units_to_parse[0])
    if len(units_to_parse) == 2 and units_to_parse[1] == 'kelvin':
        unit_dict = {'offset': float(units_to_parse[0]), conversion_table[units_to_parse[1]]: 1}
    elif len(units_to_parse) == 2:
        unit_dict[conversion_table[units_to_parse[1]]] = 1
    else:
        idx = 1
        previous_operator = None
        while idx < len(units_to_parse):
            if units_to_parse[idx] in ['*', '/']:
                previous_operator = units_to_parse[idx]
                change = 1
            else:
                unit = units_to_parse[idx]
                change = 2 if (idx + 1 < len(units_to_parse) - 1 and units_to_parse[idx + 1] in ['**', '*', '/']) else 1

                if '**' in units_to_parse[idx:idx + 3]:
                    exponent = int(units_to_parse[idx + 2])
                    change = 3
                else:
                    exponent = 1

                exponent_factor = -1 if previous_operator == '/' else 1
                unit_dict[conversion_table[unit]] = exponent_factor * exponent
                previous_operator = units_to_parse[idx + 1] if idx + 1 < len(units_to_parse) else None
            idx += change

    return unit_dict
