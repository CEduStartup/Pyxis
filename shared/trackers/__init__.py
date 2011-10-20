# This constant describes available access methods. The key is an ID of access
# method (it's stored in DB).
ACCESS_METHODS = {
    1: {'pretty': u'HTTP', 'name': 'http'},
    2: {'pretty': u'SOAP', 'name': 'soap'},
}

# This constant describe available tracker datatype. The key is an ID of
# datatype (it's stored in DB).
DATA_TYPES = {
    1: {'pretty': u'XML', 'name': 'xml'},
    2: {'pretty': u'CSV', 'name': 'csv'},
    3: {'pretty': u'JSON', 'name': 'json'},
    4: {'pretty': u'HTML', 'name': 'html'},
}

# This constant describes available value types.
VALUE_TYPES = {
   1: {'pretty': u'Integer', 'name': 'int'},
   2: {'pretty': u'Float', 'name': 'float'},
}
