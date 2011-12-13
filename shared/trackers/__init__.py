HTTP_ACCESS_METHOD = 1
SOAP_ACCESS_METHOD = 2

# This constant describes available access methods. The key is an ID of access
# method (it's stored in DB).
ACCESS_METHODS = {
    HTTP_ACCESS_METHOD: {'pretty': u'HTTP', 'name': 'http'},
    SOAP_ACCESS_METHOD: {'pretty': u'SOAP', 'name': 'soap'},
}

# This constant describe available tracker datatype. The key is an ID of
# datatype (it's stored in DB).
XML_DATA_TYPE  = 1
CSV_DATA_TYPE  = 2
JSON_DATA_TYPE = 3
HTML_DATA_TYPE = 4

DATA_TYPES = {
    XML_DATA_TYPE:  {'pretty': u'XML', 'name': 'xml'},
    CSV_DATA_TYPE:  {'pretty': u'CSV', 'name': 'csv'},
    JSON_DATA_TYPE: {'pretty': u'JSON', 'name': 'json'},
    HTML_DATA_TYPE: {'pretty': u'HTML', 'name': 'html'},
}

INT_VALUE_TYPE   = 1
FLOAT_VALUE_TYPE = 2

def _cast_int(value):
    return int(value.replace(',', '').replace('.', ''))


def _cast_float(value):
    return int(float(value.replace(',', '.')))


# This constant describes available value types.
VALUE_TYPES = {
   INT_VALUE_TYPE:   {'pretty': u'Integer', 'name': 'int', 'cast': _cast_int },
   FLOAT_VALUE_TYPE: {'pretty': u'Float', 'name': 'float', 'cast': _cast_float},
}
