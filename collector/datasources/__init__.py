from datasources.HTTP import DatasourceHTTP
from datasources.Errors import UnknownDatasourceError

def get_datasource(settings_dict):
    """Factory function, which returns concrete datasource object by source.

    :Parameters:
        - `access_method`: `dict` with datasource settings. It must contains
          `access_method` key with string value i.e.: SOAP, HTTP, XMLRPC, etc.

    :Return:
        - datasource class instance suitable for the given `access_method`.
    """
    if settings_dict['access_method'] in ('HTTP', ):
        return DatasourceHTTP(settings_dict)
    # TODO: add another types.
    else:
        raise UnknownDatasourceError('Datasource not found for access method'\
                 '"%s"' % (settings_dict['access_method'],))

