from .HTTP import DatasourceHTTP
from .Errors import UnknownDatasourceError

def get_data_source(source):
    """ Factory function, which returns concrete datasource object by source. """
    if any(map(str.startswith, ['http://', 'https://'])):
        return DatasourceHTTP(source)
    else:
        raise UnknownDatasourceError('Unknown datasource for source: %s' % (source,))